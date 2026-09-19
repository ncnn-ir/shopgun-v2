<?php

namespace App\Livewire\Orders;

use App\Infrastructure\WooCommerce\WooCommerceClient;
use App\Models\OrderItem;
use App\Models\Product;
use App\Models\ProductIdentity;
use Illuminate\Support\Facades\DB;
use Livewire\Attributes\On;
use Livewire\Component;
use Livewire\WithPagination;

/**
 * ★ SupplyList — لیست محصولات فروش رفته (تأمین)
 */
class SupplyList extends Component
{
    use WithPagination;

    public string $search = '';
    public string $sortBy = 'sold_count';
    public string $sortDir = 'desc';

    public bool $showProductPopup = false;
    public ?array $productPopup = null;

    public function updatingSearch(): void { $this->resetPage(); }

    #[On('supply-show-product')]
    public function showProduct($sku = null): void
    {
        $sku = trim($sku);
        if ($sku === '') return;

        $data = [
            'sku' => $sku,
            'title' => '—',
            'price' => 0,
            'weight' => null,
            'dimensions' => null,
            'stock' => null,
            'stock_status' => 'unknown',
            'image' => null,
            'woo_id' => null,
            'edit_url' => null,
            'view_url' => null,
        ];

        // 1. از ProductIdentity
        $identity = ProductIdentity::where('sku', $sku)->first();
        if ($identity) {
            $data['woo_id'] = $identity->woo_product_id;
            $data['title'] = $identity->canonical_name ?? $data['title'];
            $data['price'] = (float) ($identity->last_known_price ?? 0);
            $data['weight'] = $identity->last_known_weight;
            $data['edit_url'] = $identity->woo_edit_url;

            $woo = $identity->last_known_woo_data;
            if (is_array($woo)) {
                $data['image'] = $woo['images'][0]['src'] ?? null;
                $data['dimensions'] = $woo['dimensions'] ?? null;
                $data['stock'] = $woo['stock_quantity'] ?? null;
                $data['stock_status'] = $woo['stock_status'] ?? 'unknown';
                $data['view_url'] = $data['woo_id'] ? rtrim((string) \App\Models\AppSetting::get('commerce_url', ''), '/') . '/?p=' . $data['woo_id'] : null;
            }
        }

        // 2. اگه نبود، از Product محلی
        if ($data['title'] === '—') {
            $local = Product::where('sku', $sku)->first();
            if ($local) {
                $data['title'] = $local->name;
                $data['price'] = (float) $local->price;
                $data['weight'] = $local->weight;
                $data['image'] = $local->image_src;
                $data['stock'] = $local->stock_quantity;
                $data['stock_status'] = $local->stock_status;
                $data['woo_id'] = $local->wc_id;
                $data['dimensions'] = [
                    'length' => $local->length,
                    'width' => $local->width,
                    'height' => $local->height,
                ];
            }
        }

        // 3. اگه هنوز نبود، از Woo بگیر
        if ($data['title'] === '—' && $sku) {
            try {
                $client = (new WooCommerceClient())->module('supply');
                $r = $client->productBySku($sku);
                if ($r['ok'] && !empty($r['body'])) {
                    $p = $r['body'][0];
                    $data['title'] = $p['name'] ?? '—';
                    $data['price'] = (float) ($p['price'] ?? 0);
                    $data['weight'] = $p['weight'] ?? null;
                    $data['image'] = $p['images'][0]['src'] ?? null;
                    $data['stock'] = $p['stock_quantity'] ?? null;
                    $data['stock_status'] = $p['stock_status'] ?? 'unknown';
                    $data['woo_id'] = $p['id'] ?? null;
                    $data['dimensions'] = $p['dimensions'] ?? null;

                    // کش در ProductIdentity
                    try {
                        (new \App\Application\Products\ProductResolver())->touchFromWoo($p);
                    } catch (\Throwable $e) {}
                }
            } catch (\Throwable $e) {}
        }

        // 4. قیمت اخیر از سفارشات (اگه هیچ قیمتی نیامد)
        if (empty($data['price']) || $data['price'] <= 0) {
            $lastItem = OrderItem::where('sku', $sku)->latest('id')->first();
            if ($lastItem) {
                $data['price'] = (float) $lastItem->price;
                if ($data['title'] === '—') $data['title'] = $lastItem->title;
            }
        }

        $this->productPopup = $data;
        $this->showProductPopup = true;
    }

    public function closeProductPopup(): void
    {
        $this->showProductPopup = false;
        $this->productPopup = null;
    }

    public function render()
    {
        // گروه‌بندی order_items بر اساس SKU
        $query = OrderItem::query()
            ->select(
                'sku',
                DB::raw('MAX(title) as title'),
                DB::raw('SUM(quantity) as sold_count'),
                DB::raw('SUM(price * quantity) as total_revenue'),
                DB::raw('MAX(price) as last_price'),
                DB::raw('MAX(created_at) as last_sold_at'),
                DB::raw('COUNT(DISTINCT order_id) as orders_count')
            )
            ->whereNotNull('sku')
            ->where('sku', '!=', '')
            ->groupBy('sku')
            ->when($this->search, function ($q) {
                $q->where(function ($qq) {
                    $qq->where('sku', 'like', "%{$this->search}%")
                       ->orWhere('title', 'like', "%{$this->search}%");
                });
            })
            ->orderBy($this->sortBy, $this->sortDir);

        $items = $query->paginate(20);

        // شماره کل
        $totalSkus = OrderItem::whereNotNull('sku')->where('sku', '!=', '')
            ->distinct('sku')->count('sku');

        return view('livewire.orders.supply-list', [
            'items' => $items,
            'totalSkus' => $totalSkus,
        ])->layout('components.layouts.app');
    }
}
