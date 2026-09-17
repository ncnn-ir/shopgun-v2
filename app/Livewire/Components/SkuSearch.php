<?php

namespace App\Livewire\Components;

use App\Models\Integration;
use App\Services\WooCommerceService;
use Livewire\Component;

class SkuSearch extends Component
{
    public string $value = '';
    public array $suggestions = [];
    public bool $showDropdown = false;

    public function updatedValue(): void
    {
        $this->search();
    }

    public function search(): void
    {
        $q = trim($this->value);
        if (strlen($q) < 2) {
            $this->suggestions = [];
            $this->showDropdown = false;
            return;
        }

        $integration = Integration::where('key', 'woocommerce')->where('is_active', true)->first();
        if (! $integration || ! $integration->base_url) {
            $this->suggestions = [];
            $this->showDropdown = false;
            return;
        }

        try {
            $service = new WooCommerceService($integration);
            $products = $service->fetchProducts(1, 20, $q);

            $this->suggestions = collect($products)
                ->filter(fn ($p) => ! empty($p['sku']) || ! empty($p['name']))
                ->take(10)
                ->map(function ($p) {
                    return [
                        'id'    => $p['id'] ?? 0,
                        'sku'   => $p['sku'] ?? '',
                        'title' => $p['name'] ?? '',
                        'price' => (float) ($p['price'] ?? 0),
                        'image' => $p['images'][0]['src'] ?? '',
                        'stock' => $p['stock_quantity'] ?? null,
                    ];
                })
                ->all();

            $this->showDropdown = ! empty($this->suggestions);
        } catch (\Throwable $e) {
            $this->suggestions = [];
            $this->showDropdown = false;
        }
    }

    public function select(string $sku, string $title, float $price): void
    {
        $this->value = $sku;
        $this->showDropdown = false;
        $this->suggestions = [];

        $this->dispatch('sku-selected', [
            'sku'   => $sku,
            'title' => $title,
            'price' => $price,
        ]);
    }

    public function render()
    {
        return view('livewire.components.sku-search');
    }
}
