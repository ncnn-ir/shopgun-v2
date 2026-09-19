<?php

namespace App\Console\Commands;

use App\Models\AppSetting;
use App\Models\Customer;
use App\Models\Order;
use App\Models\OrderItem;
use App\Application\Orders\ChannelDetector;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Http;

class ImportOrdersFromWoo extends Command
{
    protected $signature = 'shopgun:import-orders
        {--status=processing,completed,on-hold,pending}
        {--limit=100}
        {--page=1}';

    protected $description = 'ایمپورت سفارشات از WooCommerce (فقط خواندن)';

    public function handle(): int
    {
        @set_time_limit(300);

        $auth = $this->wooAuth();
        if (!$auth) {
            $this->error('تنظیمات کامرس کامل نیست');
            return 1;
        }

        $status = $this->option('status');
        $limit  = (int) $this->option('limit');
        $page   = (int) $this->option('page');

        $this->info("Base: {$auth['base']}");
        $this->info("Status: {$status}");

        try {
            $r = Http::withBasicAuth($auth['key'], $auth['secret'])
                ->timeout(60)->connectTimeout(20)
                ->get($auth['base'] . '/orders', [
                    'per_page' => min(100, $limit),
                    'page' => $page,
                    'status' => $status,
                    'orderby' => 'date',
                    'order' => 'desc',
                ]);

            if (!$r->successful()) {
                $this->error("HTTP {$r->status()}");
                return 1;
            }

            $orders = $r->json() ?? [];
            $this->info(count($orders) . " سفارش");

            $created = 0; $updated = 0; $skipped = 0;

            foreach ($orders as $wc) {
                try {
                    $result = $this->importOne($wc);
                    if ($result === 'created') $created++;
                    elseif ($result === 'updated') $updated++;
                    else $skipped++;
                } catch (\Throwable $e) {
                    $this->warn("خطا: " . $e->getMessage());
                }
            }

            $this->newLine();
            $this->table(['مورد', 'تعداد'], [
                ['جدید', $created],
                ['بروزرسانی', $updated],
                ['رد شده', $skipped],
            ]);

            AppSetting::put('woo_last_orders_sync', now()->toIso8601String(), 'commerce');
            return 0;

        } catch (\Throwable $e) {
            $this->error($e->getMessage());
            return 1;
        }
    }

    protected function wooAuth(): ?array
    {
        $url = trim((string) AppSetting::get('commerce_url', ''));
        $key = trim((string) AppSetting::get('commerce_key', ''));
        $secret = trim((string) AppSetting::get('commerce_secret', ''));

        if (!$url || !$key || !$secret) return null;

        $base = rtrim($url, '/');
        if (!str_contains($base, '/wp-json')) $base .= '/wp-json/wc/v3';

        return ['base' => $base, 'key' => $key, 'secret' => $secret];
    }

    protected function importOne(array $wc): string
    {
        $wcId = $wc['id'] ?? null;
        if (!$wcId) return 'skip';

        $billing = $wc['billing'] ?? [];
        $shipping = $wc['shipping'] ?? [];

        $phone = $this->normalizePhone($billing['phone'] ?? $shipping['phone'] ?? '');
        $name = trim(($billing['first_name'] ?? '') . ' ' . ($billing['last_name'] ?? ''));
        if ($name === '') $name = trim(($shipping['first_name'] ?? '') . ' ' . ($shipping['last_name'] ?? ''));
        if ($name === '') $name = 'مشتری سایت';

        $address = trim(implode(' ', array_filter([
            $shipping['address_1'] ?? $billing['address_1'] ?? '',
            $shipping['address_2'] ?? $billing['address_2'] ?? '',
            $shipping['city'] ?? $billing['city'] ?? '',
            $shipping['state'] ?? $billing['state'] ?? '',
        ])));
        $postal = $shipping['postcode'] ?? $billing['postcode'] ?? null;

        // مشتری
        $customer = null;
        if ($phone) {
            $customer = Customer::where('phone', $phone)->first();
            if (!$customer) {
                $customer = Customer::create([
                    'name' => $name,
                    'phone' => $phone,
                    'address' => $address ?: null,
                    'postal_code' => $postal ?: null,
                ]);
            } else {
                $customer->update([
                    'name' => $customer->name ?: $name,
                    'address' => $customer->address ?: $address,
                    'postal_code' => $customer->postal_code ?: $postal,
                ]);
            }
        }

        // چک تکراری
        $existing = Order::where('order_number', (string) $wcId)->first();
        $status = $this->mapStatus($wc['status'] ?? 'pending');

        // کانال
        $channelId = null;
        try {
            $via = strtolower($wc['created_via'] ?? '');
            $chanKey = match (true) {
                str_contains($via, 'checkout') => 'website',
                str_contains($via, 'instagram') => 'instagram',
                str_contains($via, 'basalam') => 'basalam',
                str_contains($via, 'telegram') => 'telegram',
                str_contains($via, 'phone') => 'phone',
                str_contains($wc['payment_method_title'] ?? '', 'باسلام') => 'basalam',
                default => 'website',
            };
            $channelId = \App\Models\Channel::where('key', $chanKey)->first()?->id;
        } catch (\Throwable $e) {}

        // ★ تشخیص کانال فروش
        $channelInfo = ChannelDetector::detect($wc);
        $channelMeta = ChannelDetector::extractMeta($wc);

        $customerNote = (string) ($wc['customer_note'] ?? '');

        $data = [
            'order_number' => (string) $wcId,
            'sales_channel' => $channelInfo['channel'],
            'payment_method' => $wc['payment_method'] ?? null,
            'payment_title' => $wc['payment_method_title'] ?? null,
            'channel_metadata' => array_merge($channelInfo['meta'] ?? [], $channelMeta),
            'customer_note' => $customerNote ?: null,
            'woo_status' => $wc['status'] ?? null,
            'customer_id' => $customer?->id,
            'customer_name' => $name,
            'phone' => $phone ?: null,
            'address' => $address ?: null,
            'postal_code' => $postal,
            'status' => $status,
            'amount' => (float) ($wc['total'] ?? 0),
            'insurance' => 0,
            'channel_id' => $channelId,
            'notes' => 'سایت #' . $wcId,
        ];

        if ($existing) {
            $existing->update($data);
            $existing->items()->delete();
            $order = $existing;
            $result = 'updated';
        } else {
            $order = Order::create($data);
            $result = 'created';
        }

        // اقلام
        foreach ($wc['line_items'] ?? [] as $idx => $item) {
            OrderItem::create([
                'order_id' => $order->id,
                'title' => $item['name'] ?? 'محصول',
                'sku' => $item['sku'] ?? null,
                'price' => (float) ($item['price'] ?? 0),
                'quantity' => (int) ($item['quantity'] ?? 1),
                'cert_needed' => false,
                'sort_order' => $idx,
            ]);
        }

        return $result;
    }

    protected function mapStatus(string $wcStatus): string
    {
        return match ($wcStatus) {
            'pending', 'on-hold' => 'pending',
            'processing' => 'final-check',
            'completed' => 'courier',
            default => 'pending',
        };
    }

    protected function normalizePhone(string $phone): string
    {
        $d = preg_replace('/\D/', '', $phone);
        if (str_starts_with($d, '0098')) $d = substr($d, 4);
        elseif (str_starts_with($d, '98') && strlen($d) > 10) $d = substr($d, 2);
        if (str_starts_with($d, '0') && strlen($d) > 10) $d = substr($d, 1);
        return $d;
    }
}
