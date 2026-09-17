<?php
namespace App\Livewire\Customers;

use App\Models\Customer;
use Livewire\Component;
use Livewire\WithPagination;

class Index extends Component
{
    use WithPagination;
    public string $search = '';
    public string $filter = '';

    public function updatingSearch() { $this->resetPage(); }
    public function updatingFilter() { $this->resetPage(); }

    public function delete(int $id) {
        Customer::find($id)?->delete();
        $this->dispatch('notify', type: 'success', message: 'حذف شد');
    }

    public function render() {
        $customers = Customer::query()
            ->withCount('orders')
            ->when($this->search, function($q) {
                $q->where(function($qq) {
                    $qq->where('name', 'like', "%{$this->search}%")
                       ->orWhere('phone', 'like', "%{$this->search}%");
                });
            })
            ->when($this->filter === 'has_orders', fn($q) => $q->has('orders'))
            ->when($this->filter === 'no_orders', fn($q) => $q->doesntHave('orders'))
            ->latest('id')->paginate(20);

        return view('livewire.customers.index', compact('customers'))
            ->layout('components.layouts.app');
    }
}
