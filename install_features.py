#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShopGun V2 - Feature Installer
نصب ویژگی‌های ناقص/شروع‌نشده پروژه ShopGun V2

اجرا:
    python3 install_features.py
    python3 install_features.py --feature users
    python3 install_features.py --dry-run
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime

# ═══════════════════════════════════════════════════════════════
# Configuration
# ═══════════════════════════════════════════════════════════════

PROJECT_ROOT = Path(os.getenv('SHOPGUN_ROOT', '.')).resolve()

if not (PROJECT_ROOT / 'artisan').exists():
    print(f"❌ artisan پیدا نشد در: {PROJECT_ROOT}")
    print("   مسیر پروژه را با SHOPGUN_ROOT ست کنید یا در ریشه پروژه اجرا کنید.")
    sys.exit(1)

DRY_RUN = False

# Colors
class C:
    OK    = '\033[92m'
    WARN  = '\033[93m'
    ERR   = '\033[91m'
    INFO  = '\033[96m'
    BOLD  = '\033[1m'
    END   = '\033[0m'

def log(msg, kind='info'):
    icon = {'info':'ℹ️', 'ok':'✅', 'warn':'⚠️', 'err':'❌'}[kind]
    color = {'info':C.INFO, 'ok':C.OK, 'warn':C.WARN, 'err':C.ERR}[kind]
    print(f"{color}{icon} {msg}{C.END}")

def write_file(rel_path, content):
    """نوشتن فایل با پشتیبانی dry-run"""
    full = PROJECT_ROOT / rel_path
    full.parent.mkdir(parents=True, exist_ok=True)

    if DRY_RUN:
        log(f"[DRY] would write: {rel_path} ({len(content)} bytes)", 'warn')
        return

    if full.exists():
        backup = full.with_suffix(full.suffix + f".bak-{datetime.now().strftime('%Y%m%d%H%M%S')}")
        full.rename(backup)
        log(f"backup: {backup.name}", 'warn')

    full.write_text(content, encoding='utf-8')
    log(f"created: {rel_path}", 'ok')


# ═══════════════════════════════════════════════════════════════
# FEATURE 1: USERS MANAGEMENT UI
# ═══════════════════════════════════════════════════════════════

USERS_INDEX_PHP = '''<?php

namespace App\\Livewire\\Users;

use App\\Models\\User;
use Illuminate\\Support\\Facades\\Hash;
use Livewire\\Component;
use Livewire\\WithPagination;
use Spatie\\Permission\\Models\\Role;

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

    protected $queryString = ['search', 'filterRole'];

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
            'name'  => 'required|string|max:120',
            'email' => 'required|email|unique:users,email' . ($this->editingId ? ','.$this->editingId : ''),
            'selectedRoles' => 'array',
        ];
        if (!$this->editingId) {
            $rules['password'] = 'required|string|min:6';
        } else {
            $rules['password'] = 'nullable|string|min:6';
        }
        $this->validate($rules, [
            'name.required'  => 'نام الزامی است',
            'email.required' => 'ایمیل الزامی است',
            'email.unique'   => 'این ایمیل قبلاً ثبت شده',
            'password.required' => 'رمز عبور الزامی است',
            'password.min'   => 'رمز عبور حداقل ۶ کاراکتر',
        ]);

        $data = [
            'name'  => $this->name,
            'email' => $this->email,
        ];
        if ($this->password) {
            $data['password'] = Hash::make($this->password);
        }

        if ($this->editingId) {
            $user = User::find($this->editingId);
            $user->update($data);
            $user->syncRoles($this->selectedRoles);
            $this->dispatch('notify', type: 'success', message: 'کاربر ویرایش شد');
        } else {
            $user = User::create($data);
            $user->syncRoles($this->selectedRoles);
            $this->dispatch('notify', type: 'success', message: 'کاربر ایجاد شد');
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

    public function toggleActive(int $id): void
    {
        $u = User::find($id);
        if (!$u) return;
        // فرض: ستون is_active در جدول users
        if (\\Illuminate\\Support\\Facades\\Schema::hasColumn('users', 'is_active')) {
            $u->update(['is_active' => !$u->is_active]);
        }
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
'''

USERS_VIEW = '''<div class="p-4 md:p-6 space-y-4">

    <div class="flex flex-wrap items-center justify-between gap-3">
        <h1 class="text-xl md:text-2xl font-bold">👤 مدیریت کاربران</h1>
        <button wire:click="openForm()" class="btn btn-primary btn-sm">➕ کاربر جدید</button>
    </div>

    <div class="bg-base-100 rounded-lg shadow border p-3 flex flex-wrap gap-2">
        <input type="text" wire:model.live.debounce.400ms="search"
               placeholder="🔍 جستجوی نام یا ایمیل..."
               class="input input-bordered input-sm w-full md:w-72" />
        <select wire:model.live="filterRole" class="select select-bordered select-sm">
            <option value="">— همه نقش‌ها —</option>
            @foreach($roles as $r)
                <option value="{{ $r->name }}">{{ $r->name }}</option>
            @endforeach
        </select>
    </div>

    <div class="bg-base-100 rounded-lg shadow border overflow-hidden">
        <div class="pro-table-wrap">
            <table class="pro-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>نام</th>
                        <th>ایمیل</th>
                        <th>نقش‌ها</th>
                        <th>وضعیت</th>
                        <th>عملیات</th>
                    </tr>
                </thead>
                <tbody>
                    @forelse($users as $u)
                        <tr wire:key="user-{{ $u->id }}">
                            <td class="font-mono text-xs">{{ $u->id }}</td>
                            <td class="font-bold">{{ $u->name }}</td>
                            <td class="font-mono text-xs" dir="ltr">{{ $u->email }}</td>
                            <td>
                                @forelse($u->roles as $r)
                                    <span class="badge badge-primary badge-sm">{{ $r->name }}</span>
                                @empty
                                    <span class="badge badge-ghost badge-sm">بدون نقش</span>
                                @endforelse
                            </td>
                            <td>
                                @if(\\Illuminate\\Support\\Facades\\Schema::hasColumn('users', 'is_active'))
                                    <button wire:click="toggleActive({{ $u->id }})"
                                            class="badge badge-{{ $u->is_active ? 'success' : 'ghost' }} badge-sm cursor-pointer">
                                        {{ $u->is_active ? '✓ فعال' : 'غیرفعال' }}
                                    </button>
                                @else
                                    <span class="badge badge-success badge-sm">✓</span>
                                @endif
                            </td>
                            <td>
                                <div class="flex gap-1">
                                    <button wire:click="openForm({{ $u->id }})" class="btn btn-ghost btn-xs">✏️</button>
                                    <button wire:click="delete({{ $u->id }})" wire:confirm="حذف شود؟"
                                            class="btn btn-ghost btn-xs text-error">🗑️</button>
                                </div>
                            </td>
                        </tr>
                    @empty
                        <tr><td colspan="6" class="text-center py-8 text-base-content/50">کاربری نیست</td></tr>
                    @endforelse
                </tbody>
            </table>
        </div>
    </div>

    <div>{{ $users->links() }}</div>

    @if($showForm)
    <div class="fixed inset-0 z-[90] flex items-start justify-center p-4 overflow-y-auto">
        <div class="fixed inset-0 bg-black/60 backdrop-blur-md" wire:click="closeForm"></div>

        <div class="relative bg-base-100 rounded-2xl shadow-2xl w-full max-w-md my-8 md:my-16 border border-base-300">
            <div class="flex items-center justify-between p-4 border-b border-base-300 bg-gradient-to-l from-primary/10 to-transparent rounded-t-2xl">
                <h2 class="font-bold text-base">{{ $editingId ? '✏️ ویرایش کاربر' : '➕ کاربر جدید' }}</h2>
                <button wire:click="closeForm" class="btn btn-ghost btn-sm btn-circle">✕</button>
            </div>

            <div class="p-5 space-y-3">
                <div class="form-control">
                    <label class="label py-1"><span class="label-text text-xs font-bold">نام *</span></label>
                    <input type="text" wire:model="name" class="input input-bordered input-sm w-full" />
                    @error('name') <span class="text-error text-xs">{{ $message }}</span> @enderror
                </div>
                <div class="form-control">
                    <label class="label py-1"><span class="label-text text-xs font-bold">ایمیل *</span></label>
                    <input type="email" wire:model="email" dir="ltr" class="input input-bordered input-sm w-full" />
                    @error('email') <span class="text-error text-xs">{{ $message }}</span> @enderror
                </div>
                <div class="form-control">
                    <label class="label py-1">
                        <span class="label-text text-xs font-bold">
                            رمز عبور {{ $editingId ? '(خالی=بدون تغییر)' : '*' }}
                        </span>
                    </label>
                    <input type="password" wire:model="password" dir="ltr" class="input input-bordered input-sm w-full" />
                    @error('password') <span class="text-error text-xs">{{ $message }}</span> @enderror
                </div>
                <div class="form-control">
                    <label class="label py-1"><span class="label-text text-xs font-bold">نقش‌ها</span></label>
                    <div class="flex flex-wrap gap-2">
                        @foreach($roles as $r)
                            <label class="flex items-center gap-1 cursor-pointer">
                                <input type="checkbox" wire:model="selectedRoles" value="{{ $r->name }}"
                                       class="checkbox checkbox-xs checkbox-primary">
                                <span class="text-xs">{{ $r->name }}</span>
                            </label>
                        @endforeach
                    </div>
                </div>
            </div>

            <div class="p-4 border-t border-base-300 flex justify-end gap-2 rounded-b-2xl bg-base-200/50">
                <button wire:click="closeForm" class="btn btn-ghost btn-sm">انصراف</button>
                <button wire:click="save" wire:loading.attr="disabled" class="btn btn-primary btn-sm">
                    <span wire:loading.remove wire:target="save">✅ ذخیره</span>
                    <span wire:loading wire:target="save">⏳...</span>
                </button>
            </div>
        </div>
    </div>
    @endif
</div>
'''


# ═══════════════════════════════════════════════════════════════
# FEATURE 2: ROLES & PERMISSIONS UI
# ═══════════════════════════════════════════════════════════════

ROLES_INDEX_PHP = '''<?php

namespace App\\Livewire\\Roles;

use Livewire\\Component;
use Spatie\\Permission\\Models\\Permission;
use Spatie\\Permission\\Models\\Role;

class Index extends Component
{
    public array $permissions = [];
    public array $matrix = [];       // [roleName][permissionName] = bool
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
        app()[\\Spatie\\Permission\\PermissionRegistrar::class]->forgetCachedPermissions();
        $this->matrix[$roleName][$permissionName] = !$this->matrix[$roleName][$permissionName];
        $this->dispatch('notify', type: 'success', message: 'بروزرسانی شد');
    }

    public function save(): void
    {
        foreach ($this->matrix as $roleName => $perms) {
            $role = Role::findByName($roleName);
            $granted = array_keys(array_filter($perms));
            $role->syncPermissions($granted);
        }
        app()[\\Spatie\\Permission\\PermissionRegistrar::class]->forgetCachedPermissions();
        $this->dispatch('notify', type: 'success', message: 'همه نقش‌ها ذخیره شد');
    }

    public function render()
    {
        return view('livewire.roles.index')
            ->layout('components.layouts.app');
    }
}
'''

ROLES_VIEW = '''<div class="p-4 md:p-6 space-y-4">

    <div class="flex flex-wrap items-center justify-between gap-3">
        <h1 class="text-xl md:text-2xl font-bold">🔐 نقش‌ها و مجوزها</h1>
        <button wire:click="save" class="btn btn-primary btn-sm">💾 ذخیره همه</button>
    </div>

    <div class="bg-base-100 rounded-lg shadow border overflow-hidden">
        <div class="pro-table-wrap">
            <table class="pro-table">
                <thead>
                    <tr>
                        <th style="min-width:180px">مجوز / نقش</th>
                        @foreach($roles as $role)
                            <th class="text-center">{{ $role }}</th>
                        @endforeach
                    </tr>
                </thead>
                <tbody>
                    @foreach($permissions as $perm)
                        <tr wire:key="perm-{{ $perm }}">
                            <td class="font-mono text-xs">{{ $perm }}</td>
                            @foreach($roles as $role)
                                <td class="text-center">
                                    <input type="checkbox"
                                           wire:click="toggle('{{ $role }}', '{{ $perm }}')"
                                           {{ ($matrix[$role][$perm] ?? false) ? 'checked' : '' }}
                                           class="checkbox checkbox-xs checkbox-primary">
                                </td>
                            @endforeach
                        </tr>
                    @endforeach
                </tbody>
            </table>
        </div>
    </div>

    <p class="text-xs text-base-content/60">
        💡 هر تغییر بلافاصله اعمال می‌شود. دکمه ذخیره برای پشتیبان‌گیری است.
    </p>
</div>
'''


# ═══════════════════════════════════════════════════════════════
# FEATURE 3: CHANNELS CRUD
# ═══════════════════════════════════════════════════════════════

CHANNELS_PHP = '''<?php

namespace App\\Livewire\\Settings;

use App\\Models\\Channel;
use Livewire\\Component;

class Channels extends Component
{
    public bool $showForm = false;
    public ?int $editingId = null;

    public string $key = '';
    public string $name = '';
    public string $icon = '🌐';
    public string $color = '#1a5276';
    public bool $is_active = true;
    public int $sort_order = 0;

    public function openForm(?int $id = null): void
    {
        $this->resetForm();
        $this->editingId = $id;
        $this->showForm = true;

        if ($id) {
            $c = Channel::find($id);
            if ($c) {
                $this->key        = $c->key;
                $this->name       = $c->name;
                $this->icon       = $c->icon ?? '🌐';
                $this->color      = $c->color ?? '#1a5276';
                $this->is_active  = (bool) $c->is_active;
                $this->sort_order = (int) $c->sort_order;
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
        $this->reset(['editingId', 'key', 'name', 'icon', 'color', 'is_active', 'sort_order']);
        $this->icon = '🌐';
        $this->color = '#1a5276';
        $this->is_active = true;
    }

    public function save(): void
    {
        $this->validate([
            'key'  => 'required|string|max:50|unique:channels,key' . ($this->editingId ? ','.$this->editingId : ''),
            'name' => 'required|string|max:100',
            'icon' => 'nullable|string|max:10',
            'color'=> 'nullable|string|max:20',
        ], [
            'key.required'  => 'کلید الزامی است',
            'key.unique'    => 'این کلید قبلاً استفاده شده',
            'name.required' => 'نام الزامی است',
        ]);

        $data = [
            'key'        => $this->key,
            'name'       => $this->name,
            'icon'       => $this->icon,
            'color'      => $this->color,
            'is_active'  => $this->is_active,
            'sort_order' => $this->sort_order,
        ];

        if ($this->editingId) {
            Channel::find($this->editingId)?->update($data);
            $this->dispatch('notify', type: 'success', message: 'کانال ویرایش شد');
        } else {
            Channel::create($data);
            $this->dispatch('notify', type: 'success', message: 'کانال اضافه شد');
        }
        $this->closeForm();
    }

    public function delete(int $id): void
    {
        Channel::find($id)?->delete();
        $this->dispatch('notify', type: 'success', message: 'کانال حذف شد');
    }

    public function toggleActive(int $id): void
    {
        $c = Channel::find($id);
        if ($c) $c->update(['is_active' => !$c->is_active]);
    }

    public function render()
    {
        return view('livewire.settings.channels', [
            'channels' => Channel::orderBy('sort_order')->orderBy('id')->get(),
        ])->layout('components.layouts.app');
    }
}
'''

CHANNELS_VIEW = '''<div class="p-4 md:p-6 space-y-4">

    <div class="flex flex-wrap items-center justify-between gap-3">
        <h1 class="text-xl md:text-2xl font-bold">🌐 مدیریت کانال‌ها</h1>
        <button wire:click="openForm()" class="btn btn-primary btn-sm">➕ کانال جدید</button>
    </div>

    <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3">
        @forelse($channels as $c)
            <div wire:key="ch-{{ $c->id }}"
                 class="card bg-base-100 shadow border {{ !$c->is_active ? 'opacity-50' : '' }}">
                <div class="card-body p-4">
                    <div class="flex items-center justify-between mb-2">
                        <div class="flex items-center gap-2">
                            <span class="text-2xl">{{ $c->icon }}</span>
                            <div>
                                <div class="font-bold text-sm">{{ $c->name }}</div>
                                <div class="text-[10px] font-mono text-base-content/50" dir="ltr">{{ $c->key }}</div>
                            </div>
                        </div>
                        <div class="w-4 h-4 rounded-full" style="background:{{ $c->color }}"></div>
                    </div>

                    <div class="flex gap-2">
                        <button wire:click="toggleActive({{ $c->id }})"
                                class="btn btn-xs {{ $c->is_active ? 'btn-success' : 'btn-ghost' }}">
                            {{ $c->is_active ? '✓ فعال' : '— غیرفعال' }}
                        </button>
                        <button wire:click="openForm({{ $c->id }})" class="btn btn-ghost btn-xs">✏️</button>
                        <button wire:click="delete({{ $c->id }})" wire:confirm="حذف شود؟"
                                class="btn btn-ghost btn-xs text-error">🗑️</button>
                    </div>
                </div>
            </div>
        @empty
            <div class="col-span-full text-center py-12 text-base-content/50">
                <div class="text-4xl mb-2">🌐</div>
                کانالی نیست
            </div>
        @endforelse
    </div>

    @if($showForm)
    <div class="fixed inset-0 z-[90] flex items-start justify-center p-4 overflow-y-auto">
        <div class="fixed inset-0 bg-black/60 backdrop-blur-md" wire:click="closeForm"></div>

        <div class="relative bg-base-100 rounded-2xl shadow-2xl w-full max-w-md my-8 border border-base-300">
            <div class="flex items-center justify-between p-4 border-b border-base-300 bg-gradient-to-l from-primary/10 to-transparent rounded-t-2xl">
                <h2 class="font-bold text-base">{{ $editingId ? '✏️ ویرایش کانال' : '➕ کانال جدید' }}</h2>
                <button wire:click="closeForm" class="btn btn-ghost btn-sm btn-circle">✕</button>
            </div>

            <div class="p-5 space-y-3">
                <div class="grid grid-cols-2 gap-3">
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">کلید *</span></label>
                        <input type="text" wire:model="key" dir="ltr" class="input input-bordered input-sm w-full font-mono" />
                        @error('key') <span class="text-error text-xs">{{ $message }}</span> @enderror
                    </div>
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">نام *</span></label>
                        <input type="text" wire:model="name" class="input input-bordered input-sm w-full" />
                        @error('name') <span class="text-error text-xs">{{ $message }}</span> @enderror
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-3">
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">آیکون</span></label>
                        <input type="text" wire:model="icon" class="input input-bordered input-sm w-full text-center text-2xl" />
                    </div>
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">رنگ</span></label>
                        <input type="color" wire:model="color" class="input input-bordered input-sm w-full h-10" />
                    </div>
                </div>

                <div class="form-control">
                    <label class="label py-1"><span class="label-text text-xs font-bold">ترتیب</span></label>
                    <input type="number" wire:model="sort_order" dir="ltr" class="input input-bordered input-sm w-full" />
                </div>

                <label class="flex items-center gap-2 cursor-pointer">
                    <input type="checkbox" wire:model="is_active" class="checkbox checkbox-primary checkbox-sm" />
                    <span class="text-sm font-bold">فعال باشد</span>
                </label>
            </div>

            <div class="p-4 border-t border-base-300 flex justify-end gap-2 rounded-b-2xl bg-base-200/50">
                <button wire:click="closeForm" class="btn btn-ghost btn-sm">انصراف</button>
                <button wire:click="save" class="btn btn-primary btn-sm">✅ ذخیره</button>
            </div>
        </div>
    </div>
    @endif
</div>
'''


# ═══════════════════════════════════════════════════════════════
# FEATURE 4: SHIPMENTS MODULE
# ═══════════════════════════════════════════════════════════════

SHIPMENTS_MIGRATION = '''<?php

use Illuminate\\Database\\Migrations\\Migration;
use Illuminate\\Database\\Schema\\Blueprint;
use Illuminate\\Support\\Facades\\Schema;

return new class extends Migration
{
    public function up(): void
    {
        if (Schema::hasTable('shipments')) return;

        Schema::create('shipments', function (Blueprint $table) {
            $table->id();
            $table->foreignId('order_id')->constrained('orders')->cascadeOnDelete();
            $table->string('tracking_code')->nullable()->index();
            $table->string('carrier', 50)->default('tipax');
            $table->string('status', 50)->default('pending')->index();
            $table->string('receiver_name')->nullable();
            $table->string('receiver_phone', 20)->nullable();
            $table->text('address')->nullable();
            $table->string('postal_code', 20)->nullable();
            $table->decimal('weight', 10, 3)->nullable();
            $table->decimal('cost', 15, 2)->nullable();
            $table->json('events')->nullable();
            $table->timestamp('shipped_at')->nullable();
            $table->timestamp('delivered_at')->nullable();
            $table->timestamps();

            $table->index(['carrier', 'status']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('shipments');
    }
};
'''

SHIPMENT_MODEL = '''<?php

namespace App\\Models;

use Illuminate\\Database\\Eloquent\\Model;
use Illuminate\\Database\\Eloquent\\Relations\\BelongsTo;

class Shipment extends Model
{
    protected $fillable = [
        'order_id', 'tracking_code', 'carrier', 'status',
        'receiver_name', 'receiver_phone', 'address', 'postal_code',
        'weight', 'cost', 'events', 'shipped_at', 'delivered_at',
    ];

    protected $casts = [
        'events'       => 'array',
        'weight'       => 'decimal:3',
        'cost'         => 'decimal:2',
        'shipped_at'   => 'datetime',
        'delivered_at' => 'datetime',
    ];

    public function order(): BelongsTo
    {
        return $this->belongsTo(Order::class);
    }

    public function getStatusLabelAttribute(): string
    {
        return match ($this->status) {
            'pending'    => '📦 ثبت شده',
            'in_transit' => '🚚 در مسیر',
            'delivered'  => '✅ تحویل شد',
            'returned'   => '↩️ مرجوع',
            'failed'     => '❌ ناموفق',
            default      => $this->status,
        };
    }
}
'''

SHIPMENTS_INDEX_PHP = '''<?php

namespace App\\Livewire\\Shipments;

use App\\Models\\Shipment;
use Livewire\\Component;
use Livewire\\WithPagination;

class Index extends Component
{
    use WithPagination;

    public string $search = '';
    public string $filterStatus = '';

    public function updatingSearch(): void { $this->resetPage(); }
    public function updatingFilterStatus(): void { $this->resetPage(); }

    public function render()
    {
        $shipments = Shipment::query()
            ->with('order')
            ->when($this->search, function ($q) {
                $q->where('tracking_code', 'like', "%{$this->search}%")
                  ->orWhereHas('order', fn($oq) => $oq->where('order_number', 'like', "%{$this->search}%"))
                  ->orWhere('receiver_phone', 'like', "%{$this->search}%");
            })
            ->when($this->filterStatus, fn($q) => $q->where('status', $this->filterStatus))
            ->latest('id')
            ->paginate(20);

        return view('livewire.shipments.index', compact('shipments'))
            ->layout('components.layouts.app');
    }
}
'''

SHIPMENTS_VIEW = '''<div class="p-4 md:p-6 space-y-4">

    <h1 class="text-xl md:text-2xl font-bold">📮 مرسولات</h1>

    <div class="bg-base-100 rounded-lg shadow border p-3 flex flex-wrap gap-2">
        <input type="text" wire:model.live.debounce.400ms="search"
               placeholder="🔍 کد رهگیری / شماره سفارش / تلفن..."
               class="input input-bordered input-sm w-full md:w-80" />
        <select wire:model.live="filterStatus" class="select select-bordered select-sm">
            <option value="">— همه وضعیت‌ها —</option>
            <option value="pending">📦 ثبت شده</option>
            <option value="in_transit">🚚 در مسیر</option>
            <option value="delivered">✅ تحویل شد</option>
            <option value="returned">↩️ مرجوع</option>
            <option value="failed">❌ ناموفق</option>
        </select>
    </div>

    <div class="bg-base-100 rounded-lg shadow border overflow-hidden">
        <div class="pro-table-wrap">
            <table class="pro-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>سفارش</th>
                        <th>کد رهگیری</th>
                        <th>گیرنده</th>
                        <th>تلفن</th>
                        <th>حامل</th>
                        <th>وضعیت</th>
                        <th>تاریخ</th>
                    </tr>
                </thead>
                <tbody>
                    @forelse($shipments as $s)
                        <tr wire:key="ship-{{ $s->id }}">
                            <td class="font-mono text-xs">{{ $s->id }}</td>
                            <td>
                                @if($s->order)
                                    <a href="{{ route('orders.show', $s->order) }}"
                                       class="link link-primary font-bold">#{{ $s->order->order_number }}</a>
                                @else — @endif
                            </td>
                            <td class="font-mono text-xs" dir="ltr">{{ $s->tracking_code ?? '—' }}</td>
                            <td>{{ $s->receiver_name ?? $s->order?->customer?->name ?? '—' }}</td>
                            <td class="font-mono text-xs" dir="ltr">{{ $s->receiver_phone ?? '—' }}</td>
                            <td><span class="badge badge-ghost badge-sm">{{ $s->carrier }}</span></td>
                            <td><span class="badge badge-info badge-sm">{{ $s->status_label }}</span></td>
                            <td class="text-xs font-mono">
                                {{ $s->created_at ? \\App\\Support\\PersianDate::format($s->created_at, 'Y/m/d') : '—' }}
                            </td>
                        </tr>
                    @empty
                        <tr><td colspan="8" class="text-center py-8 text-base-content/50">مرسوله‌ای نیست</td></tr>
                    @endforelse
                </tbody>
            </table>
        </div>
    </div>

    <div>{{ $shipments->links() }}</div>
</div>
'''


# ═══════════════════════════════════════════════════════════════
# FEATURE 5: ABOUT PAGE
# ═══════════════════════════════════════════════════════════════

ABOUT_PHP = '''<?php

namespace App\\Livewire;

use Livewire\\Component;

class About extends Component
{
    public function render()
    {
        $stats = [
            'orders'       => \\App\\Models\\Order::count(),
            'customers'    => \\App\\Models\\Customer::count(),
            'products'     => \\App\\Models\\Product::count(),
            'certificates' => \\App\\Models\\Certificate::count(),
        ];

        return view('livewire.about', compact('stats'))
            ->layout('components.layouts.app');
    }
}
'''

ABOUT_VIEW = '''<div class="p-4 md:p-6 max-w-3xl mx-auto">

    <div class="text-center mb-6">
        <div class="text-6xl mb-3">💎</div>
        <h1 class="text-3xl font-extrabold text-primary">ShopGun V2</h1>
        <p class="text-sm text-base-content/60 mt-1">جواهری مشاهیر — مدیریت سفارشات و شناسنامه</p>
        <p class="text-xs text-base-content/40 mt-1">گروه هنری اقاقیا</p>
    </div>

    <div class="card bg-base-100 shadow border border-base-300 mb-4">
        <div class="card-body">
            <h2 class="font-bold text-base mb-3">📊 آمار سیستم</h2>
            <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
                <div class="text-center p-3 bg-base-200/50 rounded-lg">
                    <div class="text-2xl font-bold text-primary">{{ \\App\\Support\\PersianNumber::toFa($stats['orders']) }}</div>
                    <div class="text-xs text-base-content/60">سفارش</div>
                </div>
                <div class="text-center p-3 bg-base-200/50 rounded-lg">
                    <div class="text-2xl font-bold text-primary">{{ \\App\\Support\\PersianNumber::toFa($stats['customers']) }}</div>
                    <div class="text-xs text-base-content/60">مشتری</div>
                </div>
                <div class="text-center p-3 bg-base-200/50 rounded-lg">
                    <div class="text-2xl font-bold text-primary">{{ \\App\\Support\\PersianNumber::toFa($stats['products']) }}</div>
                    <div class="text-xs text-base-content/60">محصول</div>
                </div>
                <div class="text-center p-3 bg-base-200/50 rounded-lg">
                    <div class="text-2xl font-bold text-primary">{{ \\App\\Support\\PersianNumber::toFa($stats['certificates']) }}</div>
                    <div class="text-xs text-base-content/60">شناسنامه</div>
                </div>
            </div>
        </div>
    </div>

    <div class="card bg-base-100 shadow border border-base-300 mb-4">
        <div class="card-body">
            <h2 class="font-bold text-base mb-3">⚙️ اطلاعات فنی</h2>
            <div class="space-y-2 text-sm">
                <div class="flex justify-between p-2 bg-base-200/50 rounded">
                    <span class="text-base-content/60">Laravel</span>
                    <span class="font-mono font-bold">{{ app()->version() }}</span>
                </div>
                <div class="flex justify-between p-2 bg-base-200/50 rounded">
                    <span class="text-base-content/60">PHP</span>
                    <span class="font-mono font-bold">{{ PHP_VERSION }}</span>
                </div>
                <div class="flex justify-between p-2 bg-base-200/50 rounded">
                    <span class="text-base-content/60">محیط</span>
                    <span class="font-mono">{{ app()->environment() }}</span>
                </div>
                <div class="flex justify-between p-2 bg-base-200/50 rounded">
                    <span class="text-base-content/60">دیتابیس</span>
                    <span class="font-mono">{{ config('database.default') }}</span>
                </div>
            </div>
        </div>
    </div>

    <div class="card bg-base-100 shadow border border-base-300">
        <div class="card-body">
            <h2 class="font-bold text-base mb-3">🔗 لینک‌های مفید</h2>
            <div class="flex flex-wrap gap-2">
                <a href="https://laravel.com/docs" target="_blank" class="btn btn-outline btn-sm">📖 Laravel Docs</a>
                <a href="https://livewire.laravel.com/docs" target="_blank" class="btn btn-outline btn-sm">⚡ Livewire Docs</a>
                <a href="https://daisyui.com" target="_blank" class="btn btn-outline btn-sm">🌸 DaisyUI</a>
            </div>
        </div>
    </div>

    <div class="text-center mt-6 text-xs text-base-content/40">
        ساخته‌شده توسط گروه هنری اقاقیا
    </div>
</div>
'''


# ═══════════════════════════════════════════════════════════════
# ROUTE INJECTION
# ═══════════════════════════════════════════════════════════════

def inject_routes():
    """اضافه کردن routes جدید در routes/web.php"""
    path = PROJECT_ROOT / 'routes' / 'web.php'
    if not path.exists():
        log("routes/web.php پیدا نشد", 'err')
        return

    content = path.read_text(encoding='utf-8')
    original = content

    # Users + Roles + Channels + Shipments + About
    new_routes = '''
    // ═══ New Features (auto-injected) ═══
    Route::get('/users', App\\Livewire\\Users\\Index::class)->name('users.index');
    Route::get('/roles', App\\Livewire\\Roles\\Index::class)->name('roles.index');
    Route::get('/shipments', App\\Livewire\\Shipments\\Index::class)->name('shipments.index');
    Route::get('/about', App\\Livewire\\About::class)->name('about');
    Route::get('/settings/channels', App\\Livewire\\Settings\\Channels::class)->name('settings.channels');
    // ═══ End New Features ═══
'''

    marker = "    Route::prefix('settings')->name('settings.')->group(function () {"
    if 'New Features (auto-injected)' in content:
        log("routes قبلاً inject شده‌اند", 'warn')
        return
    if marker not in content:
        log("marker پیدا نشد — routes دستی اضافه کنید", 'warn')
        return

    content = content.replace(marker, new_routes + '\n' + marker)

    if DRY_RUN:
        log("[DRY] would update routes/web.php", 'warn')
        return

    path.write_text(content, encoding='utf-8')
    log("routes/web.php بروزرسانی شد", 'ok')


# ═══════════════════════════════════════════════════════════════
# FEATURE REGISTRY
# ═══════════════════════════════════════════════════════════════

FEATURES = {
    'users': {
        'name': 'Users Management UI',
        'files': {
            'app/Livewire/Users/Index.php':                USERS_INDEX_PHP,
            'resources/views/livewire/users/index.blade.php': USERS_VIEW,
        },
    },
    'roles': {
        'name': 'Roles & Permissions UI',
        'files': {
            'app/Livewire/Roles/Index.php':                ROLES_INDEX_PHP,
            'resources/views/livewire/roles/index.blade.php': ROLES_VIEW,
        },
    },
    'channels': {
        'name': 'Channels CRUD',
        'files': {
            'app/Livewire/Settings/Channels.php':                  CHANNELS_PHP,
            'resources/views/livewire/settings/channels.blade.php': CHANNELS_VIEW,
        },
    },
    'shipments': {
        'name': 'Shipments Module',
        'files': {
            'database/migrations/' + datetime.now().strftime('%Y_%m_%d_%H%M%S') + '_create_shipments_table.php': SHIPMENTS_MIGRATION,
            'app/Models/Shipment.php':                      SHIPMENT_MODEL,
            'app/Livewire/Shipments/Index.php':             SHIPMENTS_INDEX_PHP,
            'resources/views/livewire/shipments/index.blade.php': SHIPMENTS_VIEW,
        },
    },
    'about': {
        'name': 'About Page',
        'files': {
            'app/Livewire/About.php':              ABOUT_PHP,
            'resources/views/livewire/about.blade.php': ABOUT_VIEW,
        },
    },
}


# ═══════════════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════════════

def install(feature_key):
    if feature_key not in FEATURES:
        log(f"Feature ناشناخته: {feature_key}", 'err')
        return False

    f = FEATURES[feature_key]
    print(f"\n{C.BOLD}═══ {f['name']} ═══{C.END}")

    for rel_path, content in f['files'].items():
        write_file(rel_path, content)

    return True


def main():
    global DRY_RUN

    parser = argparse.ArgumentParser(description='ShopGun V2 Feature Installer')
    parser.add_argument('--feature', '-f', choices=list(FEATURES.keys()) + ['all', 'routes'],
                        default='all', help='کدام ویژگی نصب شود')
    parser.add_argument('--dry-run', action='store_true', help='فقط نمایش، بدون نوشتن')
    parser.add_argument('--root', help='مسیر ریشه پروژه')
    args = parser.parse_args()

    global PROJECT_ROOT
    if args.root:
        PROJECT_ROOT = Path(args.root).resolve()

    DRY_RUN = args.dry_run

    print(f"{C.BOLD}╔══════════════════════════════════════════╗")
    print(f"║  ShopGun V2 - Feature Installer          ║")
    print(f"╚══════════════════════════════════════════╝{C.END}")
    print(f"📁 Project: {PROJECT_ROOT}")
    if DRY_RUN:
        print(f"{C.WARN}🧪 DRY RUN MODE — هیچ فایلی نوشته نمی‌شود{C.END}")
    print()

    if args.feature == 'all':
        for key in FEATURES:
            install(key)
        print()
        print(f"{C.BOLD}═══ Routes ═══{C.END}")
        inject_routes()
    elif args.feature == 'routes':
        inject_routes()
    else:
        install(args.feature)

    print()
    print(f"{C.OK}╔══════════════════════════════════════════╗")
    print(f"║  ✅ تمام شد                              ║")
    print(f"╚══════════════════════════════════════════╝{C.END}")

    print(f"\n{C.INFO}🚀 مراحل بعدی:{C.END}")
    print("   php artisan migrate --force")
    print("   php artisan optimize:clear")
    print("   php artisan serve")
    print()
    print(f"{C.INFO}📍 صفحات جدید:{C.END}")
    print("   /users            → مدیریت کاربران")
    print("   /roles            → نقش‌ها و مجوزها")
    print("   /shipments        → مرسولات")
    print("   /settings/channels → مدیریت کانال‌ها")
    print("   /about            → درباره")


if __name__ == '__main__':
    main()
