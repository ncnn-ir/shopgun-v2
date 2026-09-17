<?php
namespace App\Livewire\Certificates;

use App\Models\Certificate;
use Livewire\Component;
use Livewire\WithPagination;

class Index extends Component
{
    use WithPagination;
    public string $search = '';

    public function updatingSearch() { $this->resetPage(); }

    public function delete(int $id) {
        Certificate::find($id)?->delete();
        $this->dispatch('notify', type: 'success', message: 'حذف شد');
    }

    public function render() {
        $certificates = Certificate::query()
            ->when($this->search, function($q) {
                $q->where('code', 'like', "%{$this->search}%")
                  ->orWhere('sku', 'like', "%{$this->search}%")
                  ->orWhere('stone_name', 'like', "%{$this->search}%");
            })
            ->latest('id')->paginate(20);

        return view('livewire.certificates.index', compact('certificates'))
            ->layout('components.layouts.app');
    }
}
