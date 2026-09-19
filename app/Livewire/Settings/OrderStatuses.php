<?php

namespace App\Livewire\Settings;

use App\Models\OrderStatus;
use Illuminate\Support\Facades\DB;
use Livewire\Component;

class OrderStatuses extends Component
{
    public array $statuses = [];

    public function mount(): void
    {
        $this->load();
    }

    protected function load(): void
    {
        $rows = OrderStatus::orderBy('sort_order')->get();
        if ($rows->isEmpty()) {
            foreach (OrderStatus::defaults() as $d) {
                OrderStatus::create([
                    'slug' => $d[0], 'title' => $d[1], 'color' => $d[2],
                    'is_active' => $d[3], 'should_import' => $d[4],
                    'should_count_sales' => $d[5], 'sort_order' => $d[6],
                ]);
            }
            $rows = OrderStatus::orderBy('sort_order')->get();
        }

        $this->statuses = $rows->map(fn($r) => [
            'id'                 => $r->id,
            'slug'               => $r->slug,
            'title'              => $r->title,
            'color'              => $r->color,
            'is_active'          => (bool) $r->is_active,
            'should_import'      => (bool) $r->should_import,
            'should_count_sales' => (bool) $r->should_count_sales,
            'sort_order'         => $r->sort_order,
        ])->toArray();
    }

    public function save(): void
    {
        DB::transaction(function () {
            foreach ($this->statuses as $s) {
                OrderStatus::where('id', $s['id'])->update([
                    'title'              => $s['title'],
                    'color'              => $s['color'],
                    'is_active'          => (bool) $s['is_active'],
                    'should_import'      => (bool) $s['should_import'],
                    'should_count_sales' => (bool) $s['should_count_sales'],
                    'sort_order'         => (int) $s['sort_order'],
                ]);
            }
        });
        session()->flash('message', '✓ وضعیت‌ها ذخیره شد.');
    }

    public function toggle(string $field, int $idx): void
    {
        if (isset($this->statuses[$idx][$field])) {
            $this->statuses[$idx][$field] = !$this->statuses[$idx][$field];
        }
    }

    public function render()
    {
        return view('livewire.settings.order-statuses')
            ->layout('components.layouts.app');
    }
}
