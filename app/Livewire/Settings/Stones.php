<?php

namespace App\Livewire\Settings;

use App\Models\Stone;
use Livewire\Component;
use Livewire\WithFileUploads;
use Livewire\WithPagination;

class Stones extends Component
{
    use WithPagination, WithFileUploads;

    public string $search = '';

    // فرم افزودن/ویرایش
    public bool $showForm = false;
    public ?int $editingId = null;

    public string $name = '';
    public string $en = '';
    public string $origin = '';
    public string $originEn = '';
    public string $flag = 'ir';
    public string $balloon = '';
    public string $icon = '💎';
    public $png = null;

    public array $countries = [
        'ir'=>'🇮🇷 ایران','af'=>'🇦🇫 افغانستان','iq'=>'🇮🇶 عراق','tr'=>'🇹🇷 ترکیه',
        'ye'=>'🇾🇪 یمن','sa'=>'🇸🇦 عربستان','ae'=>'🇦🇪 امارات','pk'=>'🇵🇰 پاکستان',
        'in'=>'🇮🇳 هند','cn'=>'🇨🇳 چین','us'=>'🇺🇸 آمریکا','gb'=>'🇬🇧 انگلیس',
        'de'=>'🇩🇪 آلمان','fr'=>'🇫🇷 فرانسه','it'=>'🇮🇹 ایتالیا','ru'=>'🇷🇺 روسیه',
        'jp'=>'🇯🇵 ژاپن','kr'=>'🇰🇷 کره','th'=>'🇹🇭 تایلند','my'=>'🇲🇾 مالزی',
        'au'=>'🇦🇺 استرالیا','ca'=>'🇨🇦 کانادا','br'=>'🇧🇷 برزیل','za'=>'🇿🇦 آفریقای جنوبی',
        'mm'=>'🇲🇲 میانمار','lk'=>'🇱🇰 سری‌لانکا','co'=>'🇨🇴 کلمبیا','zm'=>'🇿🇲 زامبیا',
        'eg'=>'🇪🇬 مصر','ke'=>'🇰🇪 کنیا','mg'=>'🇲🇬 ماداگاسکار','kh'=>'🇰🇭 کامبوج',
    ];

    public function updatingSearch(): void { $this->resetPage(); }

    public function openForm(?int $id = null): void
    {
        $this->resetForm();
        $this->editingId = $id;
        $this->showForm = true;

        if ($id) {
            $s = Stone::find($id);
            if ($s) {
                $this->name     = $s->name;
                $this->en       = $s->en ?? '';
                $this->origin   = $s->origin ?? '';
                $this->originEn = $s->origin_en ?? '';
                $this->flag     = $s->flag ?? 'ir';
                $this->balloon  = $s->balloon ?? '';
                $this->icon     = $s->icon ?? '💎';
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
        $this->reset(['editingId', 'name', 'en', 'origin', 'originEn', 'flag', 'balloon', 'icon', 'png']);
        $this->icon = '💎';
        $this->flag = 'ir';
    }

    public function save(): void
    {
        $this->validate([
            'name' => 'required|string|max:255',
            'en'   => 'nullable|string|max:255',
            'png'  => 'nullable|image|max:2048',
        ]);

        $data = [
            'name'      => $this->name,
            'en'        => $this->en,
            'origin'    => $this->origin,
            'origin_en' => $this->originEn ?: $this->origin,
            'flag'      => $this->flag,
            'balloon'   => $this->balloon ?: $this->name,
            'icon'      => $this->icon,
            'is_active' => true,
        ];

        if ($this->png) {
            $data['png_path'] = $this->png->store('stones', 'public');
        }

        if ($this->editingId) {
            Stone::find($this->editingId)?->update($data);
            session()->flash('success', 'سنگ ویرایش شد');
        } else {
            Stone::create($data);
            session()->flash('success', 'سنگ اضافه شد');
        }

        $this->closeForm();
    }

    public function delete(int $id): void
    {
        Stone::find($id)?->delete();
        session()->flash('success', 'سنگ حذف شد');
    }

    public function toggleActive(int $id): void
    {
        $s = Stone::find($id);
        if ($s) {
            $s->update(['is_active' => ! $s->is_active]);
        }
    }

    public function render()
    {
        $stones = Stone::query()
            ->when($this->search, function ($q) {
                $q->where('name', 'like', "%{$this->search}%")
                  ->orWhere('en', 'like', "%{$this->search}%");
            })
            ->orderBy('sort_order')
            ->orderBy('name')
            ->paginate(24);

        return view('livewire.settings.stones', compact('stones'))
            ->layout('components.layouts.app');
    }
}
