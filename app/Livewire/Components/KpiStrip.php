<?php

namespace App\Livewire\Components;

use Livewire\Component;

/**
 * ★ KpiStrip — نوار کارت‌های آماری مینیمال
 * هر کارت: عدد امروز + رشد/کاهش + تعداد دیروز
 */
class KpiStrip extends Component
{
    public array $items = [];

    public function mount(array $items = []): void
    {
        $this->items = $items;
    }

    public function render()
    {
        return view('livewire.components.kpi-strip');
    }
}
