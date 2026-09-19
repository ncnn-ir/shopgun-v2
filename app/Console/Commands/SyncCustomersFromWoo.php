<?php

namespace App\Console\Commands;

use App\Models\AppSetting;
use App\Models\Customer;
use App\Models\Order;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Http;

class SyncCustomersFromWoo extends Command
{
    protected $signature = 'shopgun:sync-customers {--limit=100} {--page=1}';
    protected $description = 'سینک مشتریان از WooCommerce';

    public function handle(): int
    {
        @set_time_limit(300);

        $auth = $this->wooAuth();
        if (!$auth) {
            $this->error('تنظیمات کامرس کامل نیست');
            return 1;
        }

        $limit = (int) $this->option('limit');
        $page = (int) $this->option('page');

        try {
            $r = Http::withBasicAuth($auth['key'], $auth['secret'])
                ->timeout(60)->connectTimeout(20)
                ->get($auth['base'] . '/customers', [
                    'per_page' => min(100, $limit),
                    'page' => $page,
                    'orderby' => 'registered_date',
                    'order' => 'desc',
                ]);

            if (!$r->successful()) {
                $this->error("HTTP {$r->status()}");
                return 1;
            }

            $customers = $r->json() ?? [];
            $this->info(count($customers) . " مشتری");

            $created = 0; $updated = 0;

            foreach ($customers as $wc) {
                $billing = $wc['billing'] ?? [];
                $phone = $this->normalizePhone($billing['phone'] ?? '');
                if ($phone === '') continue;

                $name = trim(($billing['first_name'] ?? '') . ' ' . ($billing['last_name'] ?? ''));
                if ($name === '') $name = $wc['username'] ?? 'مشتری سایت';

                $address = trim(implode(' ', array_filter([
                    $billing['address_1'] ?? '',
                    $billing['address_2'] ?? '',
                    $billing['city'] ?? '',
                    $billing['state'] ?? '',
                ])));

                $existing = Customer::where('phone', $phone)->first();

                $data = [
                    'name' => $name,
                    'phone' => $phone,
                    'email' => $billing['email'] ?? null,
                    'address' => $address ?: null,
                    'postal_code' => $billing['postcode'] ?? null,
                ];

                if ($existing) {
                    $existing->update(array_filter($data, fn($v) => $v !== null));
                    $updated++;
                } else {
                    Customer::create($data);
                    $created++;
                }
            }

            $this->newLine();
            $this->table(['مورد', 'تعداد'], [
                ['جدید', $created],
                ['بروزرسانی', $updated],
            ]);

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

    protected function normalizePhone(string $phone): string
    {
        $d = preg_replace('/\D/', '', $phone);
        if (str_starts_with($d, '0098')) $d = substr($d, 4);
        elseif (str_starts_with($d, '98') && strlen($d) > 10) $d = substr($d, 2);
        if (str_starts_with($d, '0') && strlen($d) > 10) $d = substr($d, 1);
        return $d;
    }
}
