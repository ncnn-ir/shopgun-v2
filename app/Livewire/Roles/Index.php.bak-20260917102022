<?php

namespace App\Livewire\Roles;

use Livewire\Component;
use Spatie\Permission\Models\Permission;
use Spatie\Permission\Models\Role;
use Spatie\Permission\PermissionRegistrar;

class Index extends Component
{
    public array $permissions = [];
    public array $matrix = [];
    public array $roles = [];

    public function mount(): void
    {
        $this->load();
    }

    public function load(): void
    {
        $allPermissions = Permission::orderBy('name')->get();
        $allRoles = Role::with('permissions')->orderBy('name')->get();

        $this->permissions = $allPermissions->pluck('name')->toArray();
        $this->roles = $allRoles->pluck('name')->toArray();

        $this->matrix = [];
        foreach ($allRoles as $role) {
            $granted = $role->permissions->pluck('name')->toArray();
            foreach ($this->permissions as $perm) {
                $this->matrix[$role->name][$perm] = in_array($perm, $granted, true);
            }
        }
    }

    public function toggle(string $roleName, string $permissionName): void
    {
        $role = Role::findByName($roleName);
        if ($role->hasPermissionTo($permissionName)) {
            $role->revokePermissionTo($permissionName);
        } else {
            $role->givePermissionTo($permissionName);
        }
        app(PermissionRegistrar::class)->forgetCachedPermissions();
        $this->matrix[$roleName][$permissionName] = !$this->matrix[$roleName][$permissionName];
        $this->dispatch('notify', type: 'success', message: 'بروزرسانی شد');
    }

    public function saveAll(): void
    {
        foreach ($this->matrix as $roleName => $perms) {
            $role = Role::findByName($roleName);
            $granted = array_keys(array_filter($perms));
            $role->syncPermissions($granted);
        }
        app(PermissionRegistrar::class)->forgetCachedPermissions();
        $this->dispatch('notify', type: 'success', message: 'همه نقش‌ها ذخیره شد ✅');
    }

    public function render()
    {
        return view('livewire.roles.index')
            ->layout('components.layouts.app');
    }
}
