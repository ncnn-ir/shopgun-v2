<?php

namespace App\Livewire\Orders;

use App\Models\Channel;
use App\Models\Customer;
use App\Models\Order;
use App\Models\Product;
use App\Models\AppSetting;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use Livewire\Attributes\On;
use Livewire\Component;

class FormModal extends Component
{
    public bool $show = false;
    public ?int $orderId = null;
    public string $mode = 'create';

    public string $customerName = '';
    public string $phone = '';
    public string $postalCode = '';
    public string $address = '';
    public ?int $customerId = null;

    public array $items = [];
    public array $phoneSuggestions = [];
    public array $skuSuggestions = [];
    public int $activeSkuIndex = -1;

    public string $insurance = '0';
    public string $discount = '0';
    public string $shipping = '0';
    public string $status = 'pending';
    public ?int $channelId = null;
    public string $notes = '';

    public function updated($property, $value): void
    {
        if ($property === 'phone') {
            $this->handlePhoneSearch();
            return;
        }

        if (preg_match('/^items\.(\d+)\.sku$/', $property, $m)) {
            $this->handleSkuSearch((int) $m[1], (string) $value);
            return;
        }

        if (preg_match('/^items\.\d+\.(price|quantity)$/', $property)) {
            $this->autoInsurance();
        }
    }

    #[On('open-order-form')]
    public function open(?int $orderId = null): void
    {
        $this->resetForm();
        $this->orderId = $orderId;
        $this->mode = $orderId ? 'edit' : 'create';

        if ($orderId) {
            $o = Order::with('items')->find($orderId);
            if ($o) {
                $this->customerId = $o->customer_id;
                $this->customerName = $o->customer_name ?? '';
                $this->phone = $o->phone ?? '';
                $this->postalCode = $o->postal_code ?? '';
                $this->address = $o->address ?? '';
                $this->insurance = (string)($o->insurance ?? 0);
                $this->discount = (string)($o->discount ?? 0);
                $this->shipping = (string)($o->shipping ?? 0);
                $this->status = $o->status ?? 'pending';
                $this->channelId = $o->channel_id;
                $this->notes = $o->notes ?? '';
                $this->items = $o->items->map(fn($i) => [
                    'title' => $i->title,
                    'sku' => $i->sku ?? '',
                    'price' => (float)$i->price,
                    'quantity' => (int)$i->quantity,
                    'certificate_needed' => (bool)$i->certificate_needed,
                ])->toArray();
            }
        }

        if (empty($this->items)) $this->addItem();
        $this->show = true;
    }

    public function close(): void
    {
        $this->show = false;
        $this->resetForm();
    }

    public function resetForm(): void
    {
        $this->orderId = null;
        $this->customerId = null;
        $this->customerName = '';
        $this->phone = '';
        $this->postalCode = '';
        $this->address = '';
        $this->items = [];
        $this->insurance = '0';
        $this->discount = '0';
        $this->shipping = '0';
        $this->status = 'pending';
        $this->channelId = null;
        $this->notes = '';
        $this->activeSkuIndex = -1;
        $this->skuSuggestions = [];
        $this->phoneSuggestions = [];
    }

    public function addItem(): void
    {
        $this->items[] = [
            'title' => '', 'sku' => '', 'price' => 0,
            'quantity' => 1, 'certificate_needed' => false,
        ];
    }

    public function removeItem(int $idx): void
    {
        unset($this->items[$idx]);
        $this->items = array_values($this->items);
        if (empty($this->items)) $this->addItem();
        $this->autoInsurance();
    }

    public function autoInsurance(): void
    {
        $total = 0;
        foreach ($this->items as $i) {
            $total += (float)($i['price'] ?? 0) * (int)($i['quantity'] ?? 1);
        }
        if ($total > 0) {
            $this->insurance = (string) round($total / 100000);
        }
    }

    /* ═══════════════════════════════════════════════════════════
       جستجوی مشتری — لوکال + WooCommerce
       ═══════════════════════════════════════════════════════════ */
    protected function handlePhoneSearch(): void
    {
        $raw = trim($this->phone);
        $digits = preg_replace('/\D/', '', $raw);

        Log::info("PHONE SEARCH: raw={$raw} digits={$digits}");

        if (strlen($raw) < 1) {
            $this->phoneSuggestions = [];
            return;
        }

        // ═══ ۱. لوکال ═══
        $local = [];
        if (strlen($digits) >= 1) {
            $variants = array_unique(array_filter([
                $digits,
                ltrim($digits, '0'),
                '0' . ltrim($digits, '0'),
            ]));

            $local = Customer::where(function ($qq) use ($variants, $raw) {
                    foreach ($variants as $v) {
                        $qq->orWhere('phone', 'like', "%{$v}%");
                    }
                    if (strlen($raw) >= 2) {
                        $qq->orWhere('name', 'like', "%{$raw}%");
                    }
                })
                ->orderByDesc('id')
                ->limit(10)
                ->get()
                ->map(fn($c) => [
                    'id' => (int) $c->id,
                    'name' => $c->name ?: 'بدون نام',
                    'phone' => (string) $c->phone,
                    'address' => (string) ($c->address ?? ''),
                    'postal_code' => (string) ($c->postal_code ?? ''),
                    'orders_count' => Order::where('customer_id', $c->id)->count(),
                    'source' => 'local',
                ])
                ->all();
        }

        Log::info("PHONE SEARCH: local found " . count($local));

        // ═══ ۲. WooCommerce (اگر ۳ رقم یا بیشتر) ═══
        $remote = [];
        if (strlen($digits) >= 3) {
            $remote = $this->searchWooCustomers($digits);
        }

        Log::info("PHONE SEARCH: woo found " . count($remote));

        $merged = $local;
        $existingPhones = array_column($local, 'phone');
        foreach ($remote as $r) {
            if (!in_array($r['phone'], $existingPhones, true)) {
                $merged[] = $r;
                $existingPhones[] = $r['phone'];
            }
        }

        $this->phoneSuggestions = array_slice($merged, 0, 12);
    }

    protected function searchWooCustomers(string $q): array
    {
        try {
            $url = trim((string) AppSetting::get('commerce_url', ''));
            $key = trim((string) AppSetting::get('commerce_key', ''));
            $secret = trim((string) AppSetting::get('commerce_secret', ''));

            if (!$url || !$key || !$secret) {
                Log::warning('WOO CUSTOMERS: تنظیمات کامرس خالی');
                return [];
            }

            $base = rtrim($url, '/');
            if (!str_contains($base, '/wp-json')) {
                $base .= '/wp-json/wc/v3';
            }

            $variants = array_unique(array_filter([
                $q,
                ltrim($q, '0'),
                '0' . ltrim($q, '0'),
            ]));

            $search = implode(' ', $variants);

            Log::info("WOO CUSTOMERS: GET orders?search={$search}");

            $r = Http::withBasicAuth($key, $secret)
                ->timeout(10)
                ->connectTimeout(5)
                ->get("{$base}/orders", [
                    'search' => $search,
                    'per_page' => 30,
                    'orderby' => 'date',
                    'order' => 'desc',
                ]);

            Log::info("WOO CUSTOMERS: HTTP " . $r->status());

            if (!$r->successful()) {
                return [];
            }

            $orders = $r->json() ?? [];
            Log::info("WOO CUSTOMERS: got " . count($orders) . " orders");

            $map = [];
            foreach ($orders as $o) {
                $billing = $o['billing'] ?? [];
                $phone = preg_replace('/\D/', '', $billing['phone'] ?? '');
                if ($phone === '') continue;

                if (isset($map[$phone])) {
                    $map[$phone]['orders_count']++;
                    continue;
                }

                $name = trim(($billing['first_name'] ?? '') . ' ' . ($billing['last_name'] ?? ''));
                if ($name === '') $name = 'مشتری سایت';

                $address = trim(implode(' ', array_filter([
                    $billing['address_1'] ?? '',
                    $billing['address_2'] ?? '',
                    $billing['city'] ?? '',
                    $billing['state'] ?? '',
                ])));

                $map[$phone] = [
                    'id' => -1 * (int)($o['id'] ?? 0),
                    'name' => $name,
                    'phone' => $phone,
                    'address' => $address,
                    'postal_code' => $billing['postcode'] ?? '',
                    'orders_count' => 1,
                    'source' => 'woo',
                    'email' => $billing['email'] ?? '',
                ];
            }

            return array_values($map);

        } catch (\Throwable $e) {
            Log::error("WOO CUSTOMERS ERROR: " . $e->getMessage());
            return [];
        }
    }

    public function selectPhoneSuggestion(int $index): void
    {
        $s = $this->phoneSuggestions[$index] ?? null;
        if (!$s) return;

        if (($s['source'] ?? '') === 'local' && !empty($s['id']) && $s['id'] > 0) {
            $this->customerId = (int) $s['id'];
        } else {
            $this->customerId = null;
        }

        $this->customerName = (string) ($s['name'] ?? '');
        $this->phone = (string) ($s['phone'] ?? '');
        $this->address = (string) ($s['address'] ?? '');
        $this->postalCode = (string) ($s['postal_code'] ?? '');
        $this->phoneSuggestions = [];
    }

    /* ═══════════════════════════════════════════════════════════
       جستجوی SKU — دقیق (sku=) + سراسری (search=)
       ═══════════════════════════════════════════════════════════ */
    protected function handleSkuSearch(int $idx, string $q): void
    {
        $q = trim($q);

        if (strlen($q) < 1) {
            $this->skuSuggestions = [];
            $this->activeSkuIndex = -1;
            return;
        }

        $this->activeSkuIndex = $idx;

        // ═══ ۱. اول SKU دقیق (لوکال) ═══
        $exactLocal = Product::where('sku', $q)->first();

        // ═══ ۲. اول SKU دقیق (سایت) ═══
        $exactWoo = $this->searchWooByExactSku($q);

        $results = [];

        if ($exactLocal) {
            $results[] = [
                'id' => (int) $exactLocal->id,
                'sku' => (string) $exactLocal->sku,
                'name' => (string) $exactLocal->name,
                'price' => (float) $exactLocal->price,
                'image' => $exactLocal->image_src ?? null,
                'source' => 'local',
                'exact' => true,
            ];
        }

        if ($exactWoo) {
            $results[] = [
                'id' => (int) $exactWoo['id'],
                'sku' => (string) $exactWoo['sku'],
                'name' => (string) $exactWoo['name'],
                'price' => (float) $exactWoo['price'],
                'image' => $exactWoo['image'] ?? null,
                'source' => 'woo',
                'exact' => true,
            ];
        }

        // ═══ ۳. اگر SKU دقیق هیچی نداد، جستجوی معمولی ═══
        if (empty($results)) {
            $localResults = Product::where(function ($qq) use ($q) {
                    $qq->where('sku', 'like', "%{$q}%")
                       ->orWhere('name', 'like', "%{$q}%");
                })
                ->limit(10)
                ->get()
                ->map(fn($p) => [
                    'id' => (int) $p->id,
                    'sku' => (string) $p->sku,
                    'name' => (string) $p->name,
                    'price' => (float) $p->price,
                    'image' => $p->image_src ?? null,
                    'source' => 'local',
                    'exact' => false,
                ])
                ->all();

            $results = array_merge($results, $localResults);

            $remote = $this->searchWooProducts($q);
            $existing = array_column($results, 'sku');
            foreach ($remote as $r) {
                if (!in_array($r['sku'], $existing, true)) {
                    $r['exact'] = false;
                    $results[] = $r;
                }
            }
        }

        $this->skuSuggestions = array_slice($results, 0, 15);
    }

    /**
     * جستجوی دقیق SKU در WooCommerce — از endpoint ?sku=
     */
    protected function searchWooByExactSku(string $sku): ?array
    {
        try {
            $url = trim((string) AppSetting::get('commerce_url', ''));
            $key = trim((string) AppSetting::get('commerce_key', ''));
            $secret = trim((string) AppSetting::get('commerce_secret', ''));
            if (!$url || !$key || !$secret) return null;

            $base = rtrim($url, '/');
            if (!str_contains($base, '/wp-json')) $base .= '/wp-json/wc/v3';

            Log::info("WOO EXACT SKU: GET {$base}/products?sku={$sku}");

            $r = Http::withBasicAuth($key, $secret)
                ->timeout(8)
                ->connectTimeout(5)
                ->get("{$base}/products", [
                    'sku' => $sku,
                    'per_page' => 1,
                ]);

            if (!$r->successful()) {
                Log::info("WOO EXACT SKU: HTTP " . $r->status());
                return null;
            }

            $json = $r->json();
            if (empty($json) || !is_array($json)) {
                Log::info("WOO EXACT SKU: not found");
                return null;
            }

            $p = $json[0];
            Log::info("WOO EXACT SKU: found id={$p['id']} sku={$p['sku']}");

            return [
                'id' => (int) ($p['id'] ?? 0),
                'sku' => (string) ($p['sku'] ?? ''),
                'name' => (string) ($p['name'] ?? ''),
                'price' => (float) ($p['price'] ?? 0),
                'image' => $p['images'][0]['src'] ?? null,
                'source' => 'woo',
            ];

        } catch (\Throwable $e) {
            Log::error("WOO EXACT SKU ERROR: " . $e->getMessage());
            return null;
        }
    }

    protected function searchWooProducts(string $q): array
    {
        try {
            $url = trim((string) AppSetting::get('commerce_url', ''));
            $key = trim((string) AppSetting::get('commerce_key', ''));
            $secret = trim((string) AppSetting::get('commerce_secret', ''));
            if (!$url || !$key || !$secret) return [];

            $base = rtrim($url, '/');
            if (!str_contains($base, '/wp-json')) $base .= '/wp-json/wc/v3';

            $r = Http::withBasicAuth($key, $secret)
                ->timeout(10)
                ->connectTimeout(5)
                ->get("{$base}/products", [
                    'search' => $q,
                    'per_page' => 15,
                ]);

            if (!$r->successful()) return [];

            return collect($r->json())->map(fn($p) => [
                'id' => (int)($p['id'] ?? 0),
                'sku' => (string)($p['sku'] ?? ''),
                'name' => (string)($p['name'] ?? ''),
                'price' => (float)($p['price'] ?? 0),
                'image' => $p['images'][0]['src'] ?? null,
                'source' => 'woo',
            ])->all();

        } catch (\Throwable $e) {
            Log::error("WOO PRODUCTS ERROR: " . $e->getMessage());
            return [];
        }
    }

    public function selectSkuProduct(int $productId): void
    {
        if ($this->activeSkuIndex < 0) return;

        foreach ($this->skuSuggestions as $s) {
            if ((int)$s['id'] === $productId) {
                $this->items[$this->activeSkuIndex]['sku'] = $s['sku'];
                $this->items[$this->activeSkuIndex]['title'] = $s['name'];
                $this->items[$this->activeSkuIndex]['price'] = (float)$s['price'];
                break;
            }
        }

        $this->skuSuggestions = [];
        $this->activeSkuIndex = -1;
        $this->autoInsurance();
    }

    public function getSubtotalProperty(): float
    {
        $t = 0;
        foreach ($this->items as $i) {
            $t += (float)($i['price'] ?? 0) * (int)($i['quantity'] ?? 1);
        }
        return $t;
    }

    public function getTotalProperty(): float
    {
        return max(0, $this->subtotal + (float)$this->insurance + (float)$this->shipping - (float)$this->discount);
    }

    public function save(): void
    {
        $this->validate([
            'phone' => 'required|string|max:20',
            'customerName' => 'required|string|max:120',
            'items' => 'required|array|min:1',
            'items.*.title' => 'required|string|max:255',
        ]);

        $normalized = preg_replace('/\D/', '', $this->phone);
        $normalizedNoZero = ltrim($normalized, '0');

        $customer = $this->customerId ? Customer::find($this->customerId) : null;
        if (!$customer) {
            $customer = Customer::where('phone', $normalized)
                ->orWhere('phone', $normalizedNoZero)
                ->orWhere('phone', '0' . $normalizedNoZero)
                ->first();
        }
        if (!$customer) {
            $customer = Customer::create([
                'name' => $this->customerName,
                'phone' => $normalized ?: $normalizedNoZero,
                'address' => $this->address,
                'postal_code' => $this->postalCode,
            ]);
        } else {
            $customer->update([
                'name' => $this->customerName,
                'address' => $this->address,
                'postal_code' => $this->postalCode,
            ]);
        }

        $data = [
            'customer_id' => $customer->id,
            'customer_name' => $this->customerName,
            'phone' => $this->phone,
            'address' => $this->address,
            'postal_code' => $this->postalCode,
            'status' => $this->status,
            'channel_id' => $this->channelId,
            'insurance' => (float)$this->insurance,
            'discount' => (float)$this->discount,
            'shipping' => (float)$this->shipping,
            'amount' => $this->total,
            'notes' => $this->notes,
        ];

        if ($this->orderId) {
            $order = Order::find($this->orderId);
            $order->update($data);
            $order->items()->delete();
        } else {
            $data['order_number'] = Order::generateNumber();
            $order = Order::create($data);
        }

        foreach ($this->items as $it) {
            $order->items()->create([
                'product_id' => null,
                'sku' => $it['sku'] ?? null,
                'title' => $it['title'],
                'price' => (float)$it['price'],
                'quantity' => (int)$it['quantity'],
                'cert_needed' => !empty($it['certificate_needed']),
            ]);
        }

        $this->dispatch('order-saved', orderId: $order->id);
        $this->dispatch('notify', type: 'success', message: $this->orderId ? 'ویرایش شد' : 'ثبت شد');
        $this->close();
    }

    public function render()
    {
        return view('livewire.orders.form-modal', [
            'channels' => Channel::all(),
        ]);
    }
}