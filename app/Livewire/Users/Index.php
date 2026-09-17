<?php

namespace App\Livewire\Users;

use App\Models\User;
use Illuminate\Support\Facades\Hash;
use Livewire\Component;
use Livewire\WithPagination;
use Spatie\Permission\Models\Role;

class Index extends Component
{
    use WithPagination;

    public string $search = '';
    public string $filterRole = '';

    public bool $showForm = false;
    public ?int $editingId = null;

    public string $name = '';
    public string $email = '';
    public string $password = '';
    public array $selectedRoles = [];

    public function updatingSearch(): void  { $this->resetPage(); }
    public function updatingFilterRole(): void { $this->resetPage(); }

    public function openForm(?int $id = null): void
    {
        $this->resetForm();
        $this->editingId = $id;
        $this->showForm = true;

        if ($id) {
            $u = User::with('roles')->find($id);
            if ($u) {
                $this->name  = $u->name;
                $this->email = $u->email;
                $this->selectedRoles = $u->roles->pluck('name')->toArray();
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
        $this->reset(['editingId', 'name', 'email', 'password', 'selectedRoles']);
    }

    public function save(): void
    {
        $rules = [
            'name'          => 'required|string|max:120',
            'email'         => 'required|email|unique:users,email' . ($this->editingId ? ',' . $this->editingId : ''),
            'selectedRoles' => 'array',
        ];
        $rules['password'] = $this->editingId
            ? 'nullable|string|min:6'
            : 'required|string|min:6';

        $this->validate($rules, [
            'name.required'     => 'نام الزامی است',
            'email.required'    => 'ایمیل الزامی است',
            'email.unique'      => 'این ایمیل قبلاً ثبت شده',
            'password.required' => 'رمز عبور الزامی است',
            'password.min'      => 'رمز حداقل ۶ کاراکتر',
        ]);

        $data = ['name' => $this->name, 'email' => $this->email];
        if ($this->password) {
            $data['password'] = Hash::make($this->password);
        }

        if ($this->editingId) {
            $user = User::find($this->editingId);
            $user->update($data);
            $user->syncRoles($this->selectedRoles);
            $this->dispatch('notify', type: 'success', message: 'کاربر ویرایش شد ✅');
        } else {
            $user = User::create($data);
            $user->syncRoles($this->selectedRoles);
            $this->dispatch('notify', type: 'success', message: 'کاربر ایجاد شد ✅');
        }

        $this->closeForm();
    }

    public function delete(int $id): void
    {
        if ($id === auth()->id()) {
            $this->dispatch('notify', type: 'error', message: 'نمی‌توانید خودتان را حذف کنید');
            return;
        }
        User::find($id)?->delete();
        $this->dispatch('notify', type: 'success', message: 'کاربر حذف شد');
    }

    public function render()
    {
        $users = User::query()
            ->with('roles')
            ->when($this->search, function ($q) {
                $q->where(function ($qq) {
                    $qq->where('name', 'like', "%{$this->search}%")
                       ->orWhere('email', 'like', "%{$this->search}%");
                });
            })
            ->when($this->filterRole, function ($q) {
                $q->whereHas('roles', fn($rq) => $rq->where('name', $this->filterRole));
            })
            ->latest('id')
            ->paginate(20);

        $roles = Role::orderBy('name')->get();

        return view('livewire.users.index', compact('users', 'roles'))
            ->layout('components.layouts.app');
    }
}
