<?php

namespace App\Livewire\Settings;

use App\Models\Metal;
use Livewire\Component;
use Livewire\WithPagination;

class Metals extends Component
{
    use WithPagination;

    public string $search = '';

    public bool $showForm = false;
    public ?int $editingId = null;
    public string $name = '';
    public string $en = '';
    public string $carat = '';
    public string $icon = '⚙️';

    public function updatingSearch(): void { $this->resetPage(); }

    public function openForm(?int $id = null): void
    {
        $this->resetForm();
        $this->editingId = $id;
        $this->showForm = true;

        if ($id) {
            $m = Metal::find($id);
            if ($m) {
                $this->name  = $m->name;
                $this->en    = $m->en ?? '';
                $this->carat = $m->carat ?? '';
                $this->icon  = $m->icon ?? '⚙️';
            }
        }
    }

    public function closeForm(): void
    {
        $this->showForm = false;
        $this->resetForm();
    }

    public function resetForm(): void
    {
        $this->reset(['editingId', 'name', 'en', 'carat']);
        $this->icon = '⚙️';
    }

    public function save(): void
    {
        $this->validate([
            'name'  => 'required|string|max:255',
            'carat' => 'nullable|string|max:20',
        ]);

        $data = [
            'name'      => $this->name,
            'en'        => $this->en,
            'carat'     => $this->carat,
            'icon'      => $this->icon,
            'is_active' => true,
        ];

        if ($this->editingId) {
            Metal::find($this->editingId)?->update($data);
            session()->flash('success', 'فلز ویرایش شد');
        } else {
            Metal::create($data);
            session()->flash('success', 'فلز اضافه شد');
        }

        $this->closeForm();
    }

    public function delete(int $id): void
    {
        Metal::find($id)?->delete();
        session()->flash('success', 'فلز حذف شد');
    }

    public function toggleActive(int $id): void
    {
        $m = Metal::find($id);
        if ($m) $m->update(['is_active' => ! $m->is_active]);
    }

    public function render()
    {
        $metals = Metal::query()
            ->when($this->search, fn ($q) => $q->where('name', 'like', "%{$this->search}%"))
            ->orderBy('sort_order')
            ->paginate(20);

        return view('livewire.settings.metals', compact('metals'))
            ->layout('components.layouts.app');
    }
}
