<?php
namespace App\Livewire\Products;

use App\Models\Product;
use Livewire\Component;
use Livewire\Attributes\On;

class ProductQuickView extends Component
{
    public bool $open = false;
    public ?int $pid = null;
    public ?string $psku = null;
    public array $data = [];
    public ?string $error = null;

    #[On('openProductView')]
    public function openProduct($productId = null, $sku = null): void
    {
        $this->pid = $productId ? (int) $productId : null;
        $this->psku = $sku ? trim((string) $sku) : null;
        $this->data = [];
        $this->error = null;
        $this->load();
        $this->open = true;
    }

    public function close(): void
    {
        $this->open = false;
        $this->pid = null;
        $this->psku = null;
        $this->data = [];
        $this->error = null;
    }

    protected function load(): void
    {
        $p = null;
        if ($this->pid) $p = Product::find($this->pid);
        if (!$p && $this->psku) $p = Product::where('sku', $this->psku)->first();

        if ($p) { $this->data = $this->normalize($p); return; }

        try {
            $client = app(\App\Infrastructure\WooCommerce\WooCommerceClient::class);
            if ($this->psku && method_exists($client, 'productBySku')) {
                $r = $client->productBySku($this->psku);
                if (is_array($r) && !empty($r['id'])) { $this->data = $this->fromWoo($r); return; }
            }
        } catch (\Throwable $e) {}

        $this->error = 'محصول در سیستم لوکال و سایت پیدا نشد';
    }

    protected function normalize(Product $p): array
    {
        $img = null;
        try { $img = \App\Support\ProductImage::resolve($p); } catch (\Throwable $e) {}
        $url = null;
        try { $url = \App\Support\ProductImage::permalink($p); } catch (\Throwable $e) {}
        return [
            'name' => $p->name ?? '—', 'sku' => $p->sku,
            'price' => $p->price, 'image' => $img, 'url' => $url,
            'updated' => optional($p->updated_at)->format('Y-m-d'),
        ];
    }

    protected function fromWoo(array $p): array
    {
        return [
            'name' => $p['name'] ?? '—', 'sku' => $p['sku'] ?? null,
            'price' => $p['price'] ?? null,
            'image' => $p['images'][0]['src'] ?? null,
            'url' => $p['permalink'] ?? null,
            'updated' => isset($p['date_modified']) ? date('Y-m-d', strtotime($p['date_modified'])) : null,
        ];
    }

    public function render() { return view('livewire.products.product-quick-view', ['p' => $this->data]); }
}
