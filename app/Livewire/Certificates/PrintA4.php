<?php

namespace App\Livewire\Certificates;

use App\Models\Certificate;
use Livewire\Component;

class PrintA4 extends Component
{
    public array $certificates = [];

    public function mount(): void
    {
        $ids = request()->query('ids', '');
        $idArray = array_filter(explode(',', $ids));

        if (empty($idArray)) {
            $this->certificates = [];
            return;
        }

        $this->certificates = Certificate::whereIn('id', $idArray)
            ->orderBy('id')
            ->get()
            ->all();
    }

    public function render()
    {
        return view('livewire.certificates.print-a4')
            ->layout('components.layouts.app');
    }
}
