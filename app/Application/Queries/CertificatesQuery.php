<?php

namespace App\Application\Queries;

use App\Models\Certificate;
use Illuminate\Contracts\Pagination\LengthAwarePaginator;

class CertificatesQuery
{
    public function __construct(
        public string $search = '',
        public string $filter = '',
        public int $perPage = 20,
    ) {}

    public function paginate(): LengthAwarePaginator
    {
        return Certificate::query()
            ->with(['customer'])
            ->when($this->search, function ($q) {
                $q->where(function ($qq) {
                    $qq->where('code', 'like', "%{$this->search}%")
                       ->orWhere('serial', 'like', "%{$this->search}%")
                       ->orWhere('sku', 'like', "%{$this->search}%")
                       ->orWhere('stone_name', 'like', "%{$this->search}%");
                });
            })
            ->when($this->filter === 'with_image', fn($q) => $q->whereNotNull('image_path'))
            ->when($this->filter === 'no_image', fn($q) => $q->whereNull('image_path'))
            ->latest('id')
            ->paginate($this->perPage);
    }
}
