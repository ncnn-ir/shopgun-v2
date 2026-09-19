<?php

namespace App\Application\Reports;

use App\Models\Product;
use App\Models\Certificate;

class ProductMetrics
{
    public function __construct(
        public \Carbon\Carbon $from,
        public \Carbon\Carbon $to,
    ) {}

    public function totalProducts(): int
    {
        return Product::count();
    }

    public function activeProducts(): int
    {
        return Product::where('is_active', true)->count();
    }

    public function certificatesCount(): int
    {
        return Certificate::whereBetween('created_at', [$this->from, $this->to])->count();
    }

    public function topIssuedStones(int $limit = 5): array
    {
        return Certificate::query()
            ->whereBetween('created_at', [$this->from, $this->to])
            ->select('stone_name', \Illuminate\Support\Facades\DB::raw('COUNT(*) as cnt'))
            ->groupBy('stone_name')
            ->orderByDesc('cnt')
            ->limit($limit)
            ->get()
            ->toArray();
    }
}
