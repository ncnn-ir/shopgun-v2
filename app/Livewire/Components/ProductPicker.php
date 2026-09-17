<?php

namespace App\Livewire\Components;

use App\Models\Product;
use Livewire\Attributes\On;
use Livewire\Component;

class ProductPicker extends Component
{
    /** متن جستجو */
    public string $query = '';

    /** نتایج */
    public array $results = [];

    /** سبد */
    public array $cart = [];

    /** پیشوند رویدادها */
    public string $eventPrefix = 'products';

    /** نمایش compact */
    public bool $compact = false;

    /** جستجو در WooCommerce آنلاین */
    public bool $searchOnline = true;

    public function mount(array $cart = [], string $eventPrefix = 'products', bool $compact = false): void
    {
        $this->cart = $cart;
        $this->eventPrefix = $eventPrefix;
        $this->compact = $compact;
    }

    public function updatedQuery(): void
    {
        $q = trim($this->query);
        if (mb_strlen($q) < 2) {
            $this->results = [];
            return;
        }

        // ۱) اول جستجو در دیتابیس محلی
        $local = Product::query()
            ->active()
            ->search($q)
            ->orderByRaw("CASE WHEN sku = ? THEN 0 WHEN sku LIKE ? THEN 1 ELSE 2 END", [$q, $q . '%'])
            ->limit(20)
            ->get()
            ->map(fn($p) => $this->formatResult($p))
            ->toArray();

        $this->results = $local;

        // ۲) اگر کم بود و WooCommerce فعال است، آنلاین جستجو کن
        if (count($local) < 5 && $this->searchOnline) {
            $this->searchOnlineProducts($q);
        }
    }

    protected function searchOnlineProducts(string $q): void
    {
        try {
            $wc = app(\App\Services\WooCommerceService::class);
            $remote = $wc->getProducts(['search' => $q, 'per_page' => 10]);
            if (!is_array($remote)) return;

            $existingSkus = array_column($this->results, 'sku');
            foreach ($remote as $wcItem) {
                $sku = $wcItem['sku'] ?? null;
                if (!$sku || in_array($sku, $existingSkus, true)) continue;

                $product = Product::upsertFromWoo($wcItem);
                $this->results[] = $this->formatResult($product);
            }
        } catch (\Throwable $e) {
            // ignore
        }
    }

    protected function formatResult(Product $p): array
    {
        return [
            'id'            => $p->id,
            'sku'           => $p->sku,
            'name'          => $p->name,
            'price'         => (float) $p->price,
            'price_fmt'     => $p->price_formatted,
            'image'         => $p->image_src,
            'stock'         => $p->stock_quantity,
            'stock_status'  => $p->stock_status,
            'category'      => is_array($p->categories) ? ($p->categories[0]['name'] ?? null) : null,
        ];
    }

    public function addProduct(int $id): void
    {
        $p = Product::find($id);
        if (!$p) return;

        // اگر از قبل در سبد هست، فقط تعداد را ۱ اضافه کن
        foreach ($this->cart as $i => $item) {
            if (($item['product_id'] ?? null) === $p->id) {
                $this->cart[$i]['qty'] = ((int) ($item['qty'] ?? 1)) + 1;
                $this->recalcItem($i);
                $this->emitCart();
                return;
            }
        }

        $this->cart[] = [
            'product_id'   => $p->id,
            'sku'          => $p->sku,
            'title'        => $p->name,
            'price'        => (float) $p->price,
            'qty'          => 1,
            'image'        => $p->image_src,
            'certNeeded'   => false,
        ];

        $this->query = '';
        $this->results = [];
        $this->emitCart();
    }

    public function addBySku(string $sku): void
    {
        $sku = trim($sku);
        if ($sku === '') return;

        $p = Product::where('sku', $sku)->first();
        if (!$p) {
            // جستجو آنلاین
            try {
                $wc = app(\App\Services\WooCommerceService::class);
                $remote = $wc->getProducts(['sku' => $sku, 'per_page' => 1]);
                if (is_array($remote) && !empty($remote)) {
                    $p = Product::upsertFromWoo($remote[0]);
                }
            } catch (\Throwable $e) {}
        }

        if ($p) {
            $this->addProduct($p->id);
        }
    }

    public function updateQty(int $index, int $qty): void
    {
        if (!isset($this->cart[$index])) return;
        $qty = max(1, min(999, $qty));
        $this->cart[$index]['qty'] = $qty;
        $this->recalcItem($index);
        $this->emitCart();
    }

    public function updatePrice(int $index, $price): void
    {
        if (!isset($this->cart[$index])) return;
        $price = (float) preg_replace('/[^\d.]/', '', (string) $price);
        $this->cart[$index]['price'] = $price;
        $this->emitCart();
    }

    public function toggleCert(int $index): void
    {
        if (!isset($this->cart[$index])) return;
        $this->cart[$index]['certNeeded'] = !($this->cart[$index]['certNeeded'] ?? false);
        $this->emitCart();
    }

    public function removeItem(int $index): void
    {
        unset($this->cart[$index]);
        $this->cart = array_values($this->cart);
        $this->emitCart();
    }

    public function clearCart(): void
    {
        $this->cart = [];
        $this->emitCart();
    }

    protected function recalcItem(int $index): void
    {
        // فقط برای محاسبه‌ی نمایشی، خود مبلغ در parent محاسبه می‌شود
    }

    protected function emitCart(): void
    {
        $this->dispatch("{$this->eventPrefix}-updated", cart: $this->cart);
    }

    #[On('product-picker-set')]
    public function setCart(array $cart = []): void
    {
        $this->cart = $cart;
    }

    public function render()
    {
        $total = 0;
        foreach ($this->cart as $it) {
            $total += ((float) ($it['price'] ?? 0)) * ((int) ($it['qty'] ?? 1));
        }

        return view('livewire.components.product-picker', [
            'total' => $total,
        ]);
    }
}
