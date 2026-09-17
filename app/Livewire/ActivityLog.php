<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\WithPagination;
use Spatie\Activitylog\Models\Activity;

class ActivityLog extends Component
{
    use WithPagination;

    public string $search = '';
    public string $logNameFilter = '';

    public function updatingSearch(): void { $this->resetPage(); }

    public function render()
    {
        $activities = Activity::query()
            ->with(['causer', 'subject'])
            ->when($this->search, fn ($q) => $q->where('description', 'like', "%{$this->search}%"))
            ->when($this->logNameFilter, fn ($q) => $q->where('log_name', $this->logNameFilter))
            ->latest()
            ->paginate(50);

        $logNames = Activity::distinct()->pluck('log_name')->filter()->values();

        return view('livewire.activity-log', compact('activities', 'logNames'))
            ->layout('components.layouts.app');
    }
}
