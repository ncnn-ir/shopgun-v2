<?php

namespace App\Application\Reports;

use Carbon\Carbon;

/**
 * ★ ReportEngine — نقطه واحد دسترسی به همه metrics
 */
class ReportEngine
{
    public Carbon $from;
    public Carbon $to;
    public string $rangeLabel;

    public function __construct(public string $range = 'week')
    {
        [$from, $to, $label] = match ($range) {
            'today' => [now()->startOfDay(), now()->endOfDay(), 'امروز'],
            'week' => [now()->subDays(6)->startOfDay(), now()->endOfDay(), '۷ روز اخیر'],
            'month' => [now()->subDays(29)->startOfDay(), now()->endOfDay(), '۳۰ روز اخیر'],
            'year' => [now()->startOfYear(), now()->endOfDay(), 'سال جاری'],
            default => [now()->subDays(6)->startOfDay(), now()->endOfDay(), '۷ روز اخیر'],
        };

        $this->from = $from;
        $this->to = $to;
        $this->rangeLabel = $label;
    }

    public function sales(): SalesMetrics
    {
        return new SalesMetrics($this->from, $this->to);
    }

    public function customers(): CustomerMetrics
    {
        return new CustomerMetrics($this->from, $this->to);
    }

    public function products(): ProductMetrics
    {
        return new ProductMetrics($this->from, $this->to);
    }

    /**
     * همه KPI های صفحه گزارش
     */
    public function dashboardKpi(): array
    {
        $sales = $this->sales();
        $customers = $this->customers();
        $products = $this->products();

        return [
            [
                'icon' => '📦',
                'color' => 'rgba(41,128,185,.15)',
                'num' => $sales->ordersCount(),
                'lbl' => 'سفارشات',
                'raw' => true,
            ],
            [
                'icon' => '💰',
                'color' => 'rgba(39,174,96,.15)',
                'num' => $sales->totalRevenue() / 1000000,
                'lbl' => 'فروش (م)',
                'dec' => 1,
            ],
            [
                'icon' => '👥',
                'color' => 'rgba(155,89,182,.15)',
                'num' => $customers->newCustomersCount(),
                'lbl' => 'مشتریان جدید',
                'raw' => true,
            ],
            [
                'icon' => '💎',
                'color' => 'rgba(201,168,76,.2)',
                'num' => $products->certificatesCount(),
                'lbl' => 'شناسنامه',
                'raw' => true,
            ],
            [
                'icon' => '📊',
                'color' => 'rgba(230,126,34,.15)',
                'num' => $sales->avgOrderValue() / 1000,
                'lbl' => 'میانگین (ه)',
                'dec' => 0,
            ],
            [
                'icon' => '⏳',
                'color' => 'rgba(243,156,18,.15)',
                'num' => $sales->pendingOrdersCount(),
                'lbl' => 'در انتظار',
                'raw' => true,
            ],
        ];
    }
}
