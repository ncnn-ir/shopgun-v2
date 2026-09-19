<?php

namespace App\Livewire;

use App\Application\Reports\DashboardMetrics;
use Carbon\Carbon;
use Livewire\Component;

class Dashboard extends Component
{
    public string $range = 'today';
    public array $accessCards = [];

    public bool $showProductPopup = false;
    public ?array $productDetail = null;

    public function mount(): void
    {
        $this->loadAccessCards();
    }

    protected function loadAccessCards(): void
    {
        $this->accessCards = [
            ['route' => route('orders.index'), 'icon' => '📦', 'label' => 'سفارشات', 'color' => '#3b82f6'],
            ['route' => route('orders.create'), 'icon' => '➕', 'label' => 'سفارش جدید', 'color' => '#10b981'],
            ['route' => route('customers.index'), 'icon' => '👥', 'label' => 'مشتریان', 'color' => '#8b5cf6'],
            ['route' => route('certificates.create'), 'icon' => '💎', 'label' => 'صدور شناسنامه', 'color' => '#c9a84c'],
            ['route' => route('products.bulk'), 'icon' => '⚡', 'label' => 'ثبت گروهی', 'color' => '#7c3aed'],
            ['route' => route('reports.index'), 'icon' => '📊', 'label' => 'گزارش‌ها', 'color' => '#06b6d4'],
            ['route' => route('settings.index'), 'icon' => '⚙️', 'label' => 'تنظیمات', 'color' => '#64748b'],
            ['route' => route('settings.health'), 'icon' => '🩺', 'label' => 'سلامت', 'color' => '#ef4444'],
        ];
    }

    public function setRange(string $range): void
    {
        $this->range = $range;
    }

    public function showProduct(string $title, string $sku = ''): void
    {
        $this->productDetail = [
            'title' => $title,
            'sku' => $sku,
            'image' => null,
        ];

        // تلاش برای گرفتن تصویر از Product
        if ($sku) {
            $p = \App\Models\Product::where('sku', $sku)->first();
            if ($p && $p->image_src) {
                $this->productDetail['image'] = $p->image_src;
            }
        }

        $this->showProductPopup = true;
    }

    public function closeProduct(): void
    {
        $this->showProductPopup = false;
        $this->productDetail = null;
    }

    public function markSupplied(int $orderId): void
    {
        $order = \App\Models\Order::find($orderId);
        if (!$order) return;

        $order->update(['supply_status' => 'delivered_to_shipping']);
        $this->dispatch('notify', type: 'success', message: 'تحویل واحد ارسال شد ✅');
    }

    protected function getPeriods(): array
    {
        $now = now();
        return match ($this->range) {
            'today' => [$now->copy()->startOfDay(), $now->copy()->endOfDay(), 'امروز'],
            'yesterday' => [$now->copy()->subDay()->startOfDay(), $now->copy()->subDay()->endOfDay(), 'دیروز'],
            'week' => [$now->copy()->subDays(6)->startOfDay(), $now->copy()->endOfDay(), '۷ روز اخیر'],
            'month' => [$now->copy()->subDays(29)->startOfDay(), $now->copy()->endOfDay(), '۳۰ روز اخیر'],
            'year' => [$now->copy()->startOfYear(), $now->copy()->endOfDay(), 'سال جاری'],
            default => [$now->copy()->startOfDay(), $now->copy()->endOfDay(), 'امروز'],
        };
    }

    public function render()
    {
        [$from, $to, $label] = $this->getPeriods();
        $metrics = new DashboardMetrics($from, $to);

        return view('livewire.dashboard', [
            'label' => $label,
            'kpi' => $metrics->kpi(),
            'salesByChannel' => $metrics->salesByChannel(),
            'recentByChannel' => $metrics->recentByChannel(10),
            'salesTrend' => $metrics->salesTrend(),
            'topProducts' => $metrics->topProducts(10),
            'topCustomers' => $metrics->topCustomers(10),
            'cancelRatio' => $metrics->cancelledRatio(),
            'pendingSupply' => $metrics->pendingSupplyOrders(20),
        ])->layout('components.layouts.app');
    }
}
