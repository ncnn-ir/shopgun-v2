<?php

namespace App\Livewire\Orders;

use App\Models\Order;
use App\Models\Channel;
use Livewire\Component;
use Livewire\WithPagination;

class Index extends Component
{
    use WithPagination;

    public string $search = '';
    public string $filterStatus = '';
    public ?int $filterChannel = null;
    public string $dateFrom = '';
    public string $dateTo = '';
    public array $selected = [];
    public bool $selectAll = false;
    public string $sortField = 'id';
    public string $sortDirection = 'desc';

    protected $queryString = ['search', 'filterStatus'];

    public function updatingSearch(): void { $this->resetPage(); }
    public function updatingFilterStatus(): void { $this->resetPage(); }
    public function updatingDateFrom(): void { $this->resetPage(); }
    public function updatingDateTo(): void { $this->resetPage(); }

    public function sortBy(string $field): void
    {
        if ($this->sortField === $field) {
            $this->sortDirection = $this->sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            $this->sortField = $field;
            $this->sortDirection = 'asc';
        }
    }

    public function clearFilters(): void
    {
        $this->reset(['search', 'filterStatus', 'filterChannel', 'dateFrom', 'dateTo']);
        $this->resetPage();
    }

    public function toggleSelect(int $id): void
    {
        if (in_array($id, $this->selected, true)) {
            $this->selected = array_values(array_diff($this->selected, [$id]));
        } else {
            $this->selected[] = $id;
        }
    }

    public function clearSelection(): void
    {
        $this->selected = [];
        $this->selectAll = false;
    }

    public function bulkStatus(string $status): void
    {
        if (!in_array($status, ['pending', 'final-check', 'courier'], true)) return;
        Order::whereIn('id', $this->selected)->update(['status' => $status]);
        $this->dispatch('notify', type: 'success', message: count($this->selected) . ' سفارش تغییر کرد');
        $this->clearSelection();
    }

    public function bulkDelete(): void
    {
        if (empty($this->selected)) return;
        Order::whereIn('id', $this->selected)->delete();
        $this->dispatch('notify', type: 'success', message: 'حذف شد');
        $this->clearSelection();
    }

    public function delete(int $id): void
    {
        Order::find($id)?->delete();
        $this->dispatch('notify', type: 'success', message: 'حذف شد');
    }

    public function cycleStatus(int $id): void
    {
        $o = Order::find($id);
        if (!$o) return;
        $list = ['pending', 'final-check', 'courier'];
        $cur = array_search($o->status, $list, true);
        $o->update(['status' => $list[($cur === false ? 0 : ($cur + 1)) % 3]]);
    }

    public function render()
    {
        $orders = Order::query()
            ->with(['items', 'channel'])
            ->when($this->search, fn($q) => $q->where(function ($qq) {
                $qq->where('order_number', 'like', "%{$this->search}%")
                   ->orWhere('customer_name', 'like', "%{$this->search}%")
                   ->orWhere('phone', 'like', "%{$this->search}%");
            }))
            ->when($this->filterStatus, fn($q) => $q->where('status', $this->filterStatus))
            ->when($this->dateFrom, fn($q) => $q->whereDate('created_at', '>=', $this->dateFrom))
            ->when($this->dateTo, fn($q) => $q->whereDate('created_at', '<=', $this->dateTo))
            ->orderBy($this->sortField, $this->sortDirection)
            ->paginate(20);

        return view('livewire.orders.index', [
            'orders' => $orders,
            'channels' => Channel::all(),
        ])->layout('components.layouts.app');
    }
}
