from pathlib import Path
import textwrap

PROJECT = Path.home() / "projects" / "shopgun-v2.1"

if not PROJECT.exists():
    raise SystemExit(f"❌ پروژه پیدا نشد: {PROJECT}")

def write_file(relative_path, content):
    path = PROJECT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    existed = path.exists()
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    action = "🔁" if existed else "✅"
    print(f"{action} {relative_path}")

print("═" * 60)
print("🚀 مرحله ۲ (بخش ۳) — کامپوننت‌های باقی‌مانده")
print("═" * 60)
print()

# =========================================================
# ActivityLog
# =========================================================
print("📦 ActivityLog...")

write_file("app/Livewire/ActivityLog.php", r"""
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
""")

write_file("resources/views/livewire/activity-log.blade.php", r"""
<div class="p-6">
    <div class="flex flex-wrap items-center justify-between gap-4 mb-6">
        <h1 class="text-2xl font-bold">📜 لاگ فعالیت‌ها</h1>
        <div class="flex flex-wrap gap-2">
            <input type="text" wire:model.live.debounce.400ms="search" placeholder="🔍 جستجو..." class="input input-bordered input-sm w-52" />
            <select wire:model.live="logNameFilter" class="select select-bordered select-sm">
                <option value="">همه</option>
                @foreach($logNames as $name)
                    <option value="{{ $name }}">{{ $name }}</option>
                @endforeach
            </select>
        </div>
    </div>

    <div class="card bg-base-100 shadow">
        <div class="card-body p-0">
            <div class="overflow-x-auto">
                <table class="table table-zebra table-sm">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>تاریخ</th>
                            <th>کاربر</th>
                            <th>لاگ</th>
                            <th>رویداد</th>
                            <th>توضیح</th>
                        </tr>
                    </thead>
                    <tbody>
                        @forelse($activities as $a)
                            <tr>
                                <td class="text-xs">{{ $a->id }}</td>
                                <td class="text-xs whitespace-nowrap">{{ $a->created_at?->format('Y/m/d H:i:s') }}</td>
                                <td class="text-xs">{{ $a->causer?->name ?? 'سیستم' }}</td>
                                <td><span class="badge badge-outline badge-sm">{{ $a->log_name }}</span></td>
                                <td><span class="badge badge-primary badge-sm">{{ $a->event }}</span></td>
                                <td class="text-xs">{{ $a->description }}</td>
                            </tr>
                        @empty
                            <tr><td colspan="6" class="text-center py-8 text-base-content/50">لاگی نیست</td></tr>
                        @endforelse
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    <div class="mt-4">{{ $activities->links() }}</div>
</div>
""")

# =========================================================
# GlobalSearch
# =========================================================
print()
print("📦 GlobalSearch...")

write_file("app/Livewire/GlobalSearch.php", r"""
<?php

namespace App\Livewire;

use App\Models\Customer;
use App\Models\Order;
use Livewire\Component;

class GlobalSearch extends Component
{
    public string $query = '';
    public bool $open = false;

    public function updatedQuery(): void
    {
        $this->open = strlen(trim($this->query)) >= 2;
    }

    public function openSearch(): void { $this->open = true; }
    public function close(): void { $this->open = false; $this->query = ''; }

    public function render()
    {
        $orders = [];
        $customers = [];

        if (strlen(trim($this->query)) >= 2) {
            $q = trim($this->query);
            $orders = Order::query()
                ->where(function ($qq) use ($q) {
                    $qq->where('order_number', 'like', "%{$q}%")
                       ->orWhere('phone', 'like', "%{$q}%")
                       ->orWhereHas('customer', fn ($cq) => $cq->where('name', 'like', "%{$q}%"));
                })
                ->latest('id')->limit(5)->get();

            $customers = Customer::query()
                ->where(function ($qq) use ($q) {
                    $qq->where('phone', 'like', "%{$q}%")
                       ->orWhere('name', 'like', "%{$q}%");
                })
                ->latest('id')->limit(5)->get();
        }

        return view('livewire.global-search', compact('orders', 'customers'));
    }
}
""")

write_file("resources/views/livewire/global-search.blade.php", r"""
<div x-data="{ open: @entangle('open') }"
     @keydown.window.prevent.ctrl.k="open = true; $wire.openSearch(); $nextTick(() => $refs.searchInput?.focus())"
     @keydown.window.escape="open = false; $wire.close()">

    <div x-show="open" x-transition.opacity
         class="fixed inset-0 bg-black/60 backdrop-blur-sm z-[100]"
         @click="open = false; $wire.close()"></div>

    <div x-show="open" x-transition
         class="fixed inset-x-0 top-20 mx-auto max-w-2xl z-[101] px-4">
        <div class="card bg-base-100 shadow-2xl">
            <div class="card-body p-0">
                <div class="flex items-center gap-3 p-4 border-b border-base-300">
                    <span class="text-2xl">🔍</span>
                    <input x-ref="searchInput" type="text"
                           wire:model.live.debounce.300ms="query"
                           placeholder="جستجو..."
                           class="input input-ghost w-full text-lg" autofocus />
                    <kbd class="kbd kbd-sm">ESC</kbd>
                </div>

                <div class="max-h-96 overflow-y-auto p-2">
                    @if(strlen(trim($query)) < 2)
                        <div class="text-center py-8 text-base-content/50 text-sm">حداقل ۲ کاراکتر وارد کن</div>
                    @else
                        @if($orders->isNotEmpty())
                            <div class="text-xs text-base-content/60 px-3 pt-3 pb-1 font-bold">📦 سفارشات</div>
                            @foreach($orders as $order)
                                <a href="{{ route('orders.show', $order) }}" wire:navigate @click="open = false"
                                   class="flex items-center gap-3 p-3 rounded-lg hover:bg-base-200">
                                    <span class="text-xl">📦</span>
                                    <div class="flex-1">
                                        <div class="font-bold text-sm">#{{ $order->order_number }} — {{ $order->customer?->name ?? 'بدون نام' }}</div>
                                        <div class="text-xs text-base-content/60 font-mono" dir="ltr">{{ $order->phone }}</div>
                                    </div>
                                </a>
                            @endforeach
                        @endif

                        @if($customers->isNotEmpty())
                            <div class="text-xs text-base-content/60 px-3 pt-3 pb-1 font-bold">👥 مشتریان</div>
                            @foreach($customers as $customer)
                                <a href="{{ route('customers.show', $customer) }}" wire:navigate @click="open = false"
                                   class="flex items-center gap-3 p-3 rounded-lg hover:bg-base-200">
                                    <span class="text-xl">👤</span>
                                    <div class="flex-1">
                                        <div class="font-bold text-sm">{{ $customer->name ?? 'بدون نام' }}</div>
                                        <div class="text-xs text-base-content/60 font-mono" dir="ltr">{{ $customer->phone }}</div>
                                    </div>
                                </a>
                            @endforeach
                        @endif

                        @if($orders->isEmpty() && $customers->isEmpty())
                            <div class="text-center py-8 text-base-content/50 text-sm">نتیجه‌ای یافت نشد</div>
                        @endif
                    @endif
                </div>
            </div>
        </div>
    </div>
</div>
""")

# =========================================================
# NotificationCenter
# =========================================================
print()
print("📦 NotificationCenter...")

write_file("app/Livewire/NotificationCenter.php", r"""
<?php

namespace App\Livewire;

use App\Models\AppNotification;
use Illuminate\Support\Facades\Auth;
use Livewire\Component;

class NotificationCenter extends Component
{
    public int $unreadCount = 0;

    public function mount(): void { $this->refreshCount(); }

    public function refreshCount(): void
    {
        $this->unreadCount = AppNotification::where('user_id', Auth::id())->where('is_read', false)->count();
    }

    public function markAsRead(int $id): void
    {
        AppNotification::where('id', $id)->where('user_id', Auth::id())->update(['is_read' => true]);
        $this->refreshCount();
    }

    public function markAllAsRead(): void
    {
        AppNotification::where('user_id', Auth::id())->update(['is_read' => true]);
        $this->refreshCount();
    }

    public function delete(int $id): void
    {
        AppNotification::where('id', $id)->where('user_id', Auth::id())->delete();
        $this->refreshCount();
    }

    public function clearAll(): void
    {
        AppNotification::where('user_id', Auth::id())->delete();
        $this->refreshCount();
    }

    public function render()
    {
        $notifications = AppNotification::where('user_id', Auth::id())->latest()->limit(20)->get();
        return view('livewire.notification-center', compact('notifications'));
    }
}
""")

write_file("resources/views/livewire/notification-center.blade.php", r"""
<div wire:poll.15s="refreshCount" class="dropdown dropdown-end">
    <div tabindex="0" role="button" class="btn btn-ghost btn-sm">
        <div class="indicator">
            🔔
            @if($unreadCount > 0)
                <span class="badge badge-error badge-xs indicator-item">{{ $unreadCount > 99 ? '99+' : $unreadCount }}</span>
            @endif
        </div>
    </div>
    <div tabindex="0" class="dropdown-content z-[100] card card-compact w-80 bg-base-100 shadow-2xl border border-base-300">
        <div class="card-body p-0">
            <div class="flex items-center justify-between p-3 border-b border-base-300">
                <h3 class="font-bold text-sm">🔔 اعلان‌ها @if($unreadCount > 0)<span class="badge badge-error badge-sm">{{ $unreadCount }}</span>@endif</h3>
                @if($unreadCount > 0)
                    <button wire:click="markAllAsRead" class="btn btn-ghost btn-xs">✓ خواندن همه</button>
                @endif
            </div>
            <div class="max-h-96 overflow-y-auto">
                @forelse($notifications as $notif)
                    <div wire:key="notif-{{ $notif->id }}" class="p-3 border-b border-base-200 hover:bg-base-200 {{ !$notif->is_read ? 'bg-primary/5' : '' }}">
                        <div class="flex gap-3">
                            <div class="text-2xl">{{ $notif->icon }}</div>
                            <div class="flex-1">
                                <div class="flex justify-between items-start gap-2">
                                    <div class="font-bold text-sm">{{ $notif->title }}</div>
                                    <div class="text-[10px] text-base-content/50">{{ $notif->created_at->diffForHumans() }}</div>
                                </div>
                                <div class="text-xs text-base-content/70 mt-1">{{ $notif->message }}</div>
                                <div class="flex gap-2 mt-2">
                                    @if($notif->url)
                                        <a href="{{ $notif->url }}" wire:click="markAsRead({{ $notif->id }})" class="btn btn-primary btn-xs">مشاهده</a>
                                    @endif
                                    <button wire:click="delete({{ $notif->id }})" class="btn btn-ghost btn-xs text-error mr-auto">🗑️</button>
                                </div>
                            </div>
                        </div>
                    </div>
                @empty
                    <div class="text-center py-8 text-base-content/50 text-sm">اعلانی نیست</div>
                @endforelse
            </div>
            @if($notifications->isNotEmpty())
                <div class="p-3 border-t border-base-300">
                    <button wire:click="clearAll" class="btn btn-ghost btn-sm w-full">🗑️ پاک کردن همه</button>
                </div>
            @endif
        </div>
    </div>
</div>
""")

# =========================================================
# Customers
# =========================================================
print()
print("📦 Customers...")

write_file("app/Livewire/Customers/Index.php", r"""
<?php

namespace App\Livewire\Customers;

use App\Models\Customer;
use Livewire\Component;
use Livewire\WithPagination;

class Index extends Component
{
    use WithPagination;
    public string $search = '';

    public function updatingSearch(): void { $this->resetPage(); }

    public function render()
    {
        $customers = Customer::query()
            ->withCount('orders')
            ->when($this->search, function ($q) {
                $q->where(function ($qq) {
                    $qq->where('name', 'like', "%{$this->search}%")
                       ->orWhere('phone', 'like', "%{$this->search}%");
                });
            })
            ->latest('id')->paginate(20);

        return view('livewire.customers.index', compact('customers'))
            ->layout('components.layouts.app');
    }
}
""")

write_file("resources/views/livewire/customers/index.blade.php", r"""
<div class="p-6">
    <div class="flex flex-wrap items-center justify-between gap-4 mb-6">
        <h1 class="text-2xl font-bold">👥 مشتریان</h1>
        <div class="flex flex-wrap gap-2">
            <input type="text" wire:model.live.debounce.400ms="search" placeholder="🔍 جستجو..." class="input input-bordered input-sm w-64" />
            <a href="{{ route('customers.create') }}" class="btn btn-primary btn-sm">➕ مشتری جدید</a>
        </div>
    </div>

    <div class="card bg-base-100 shadow">
        <div class="card-body p-0">
            <div class="overflow-x-auto">
                <table class="table table-zebra">
                    <thead>
                        <tr><th>#</th><th>نام</th><th>تلفن</th><th>کدپستی</th><th>سفارش</th><th>آدرس</th><th>عملیات</th></tr>
                    </thead>
                    <tbody>
                        @forelse($customers as $c)
                            <tr>
                                <td>{{ $c->id }}</td>
                                <td class="font-bold"><a href="{{ route('customers.show', $c) }}" class="link link-primary">{{ $c->name ?? '—' }}</a></td>
                                <td class="font-mono" dir="ltr">{{ $c->phone }}</td>
                                <td class="font-mono" dir="ltr">{{ $c->postal_code ?? '—' }}</td>
                                <td><span class="badge badge-primary">{{ $c->orders_count }}</span></td>
                                <td class="text-xs max-w-xs truncate">{{ $c->address ?? '—' }}</td>
                                <td>
                                    <div class="flex gap-1">
                                        <a href="{{ route('customers.show', $c) }}" class="btn btn-ghost btn-xs">👁️</a>
                                        <a href="{{ route('customers.edit', $c) }}" class="btn btn-ghost btn-xs">✏️</a>
                                    </div>
                                </td>
                            </tr>
                        @empty
                            <tr><td colspan="7" class="text-center py-8 text-base-content/50">مشتری‌ای نیست</td></tr>
                        @endforelse
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    <div class="mt-4">{{ $customers->links() }}</div>
</div>
""")

write_file("app/Livewire/Customers/Create.php", r"""
<?php

namespace App\Livewire\Customers;

use App\Models\Customer;
use Livewire\Component;

class Create extends Component
{
    public string $name = '';
    public string $phone = '';
    public string $postalCode = '';
    public string $address = '';
    public string $notes = '';

    protected function normalizePhone(string $phone): string
    {
        $digits = preg_replace('/\D/', '', $phone);
        if (str_starts_with($digits, '0098')) $digits = substr($digits, 4);
        elseif (str_starts_with($digits, '98') && strlen($digits) > 10) $digits = substr($digits, 2);
        if (str_starts_with($digits, '0') && strlen($digits) > 10) $digits = substr($digits, 1);
        return $digits;
    }

    public function save()
    {
        $this->validate([
            'phone' => 'required|min:10|unique:customers,phone',
            'name'  => 'nullable|string|max:255',
        ], ['phone.unique' => 'این شماره قبلاً ثبت شده.']);

        Customer::create([
            'name'        => $this->name ?: 'بدون نام',
            'phone'       => $this->normalizePhone($this->phone),
            'postal_code' => $this->postalCode,
            'address'     => $this->address,
            'notes'       => $this->notes,
        ]);

        session()->flash('success', 'مشتری ثبت شد.');
        return redirect()->route('customers.index');
    }

    public function render()
    {
        return view('livewire.customers.create')->layout('components.layouts.app');
    }
}
""")

write_file("resources/views/livewire/customers/create.blade.php", r"""
<div class="p-6 max-w-3xl mx-auto">
    <div class="flex items-center gap-3 mb-6">
        <a href="{{ route('customers.index') }}" class="btn btn-ghost btn-sm">→</a>
        <h1 class="text-2xl font-bold">➕ مشتری جدید</h1>
    </div>

    <div class="card bg-base-100 shadow">
        <div class="card-body space-y-4">
            <div class="form-control">
                <label class="label"><span class="label-text font-bold">📱 تلفن *</span></label>
                <input type="text" wire:model="phone" dir="ltr" class="input input-bordered font-mono" />
                @error('phone') <label class="label"><span class="label-text-alt text-error">{{ $message }}</span></label> @enderror
            </div>
            <div class="form-control">
                <label class="label"><span class="label-text font-bold">👤 نام</span></label>
                <input type="text" wire:model="name" class="input input-bordered" />
            </div>
            <div class="form-control">
                <label class="label"><span class="label-text font-bold">📮 کدپستی</span></label>
                <input type="text" wire:model="postalCode" dir="ltr" class="input input-bordered font-mono" />
            </div>
            <div class="form-control">
                <label class="label"><span class="label-text font-bold">📍 آدرس</span></label>
                <textarea wire:model="address" class="textarea textarea-bordered" rows="3"></textarea>
            </div>
            <div class="form-control">
                <label class="label"><span class="label-text font-bold">📝 یادداشت</span></label>
                <textarea wire:model="notes" class="textarea textarea-bordered" rows="2"></textarea>
            </div>
            <div class="card-actions justify-end mt-6">
                <a href="{{ route('customers.index') }}" class="btn btn-ghost">انصراف</a>
                <button wire:click="save" class="btn btn-primary">✅ ذخیره</button>
            </div>
        </div>
    </div>
</div>
""")

write_file("app/Livewire/Customers/Show.php", r"""
<?php

namespace App\Livewire\Customers;

use App\Models\Customer;
use Livewire\Component;

class Show extends Component
{
    public Customer $customer;

    public function mount(Customer $customer): void { $this->customer = $customer; }

    public function delete()
    {
        $name = $this->customer->name ?? $this->customer->phone;
        $this->customer->delete();
        session()->flash('success', "مشتری «{$name}» حذف شد.");
        return redirect()->route('customers.index');
    }

    public function render()
    {
        $orders = $this->customer->orders()->with('channel')->latest('id')->limit(50)->get();
        $totalAmount = $this->customer->orders()->sum('amount');
        $activities = $this->customer->activities()->with('causer')->limit(20)->get();

        return view('livewire.customers.show', compact('orders', 'totalAmount', 'activities'))
            ->layout('components.layouts.app');
    }
}
""")

write_file("resources/views/livewire/customers/show.blade.php", r"""
<div class="p-6 max-w-4xl mx-auto">
    <div class="flex flex-wrap items-center justify-between gap-3 mb-6">
        <div class="flex items-center gap-3">
            <a href="{{ route('customers.index') }}" class="btn btn-ghost btn-sm">→</a>
            <h1 class="text-2xl font-bold">👤 {{ $customer->name ?? $customer->phone }}</h1>
        </div>
        <div class="flex gap-2">
            <a href="{{ route('customers.edit', $customer) }}" class="btn btn-warning btn-sm">✏️ ویرایش</a>
            <button wire:click="delete" wire:confirm="حذف شود؟" class="btn btn-error btn-sm">🗑️</button>
        </div>
    </div>

    @if (session('success'))
        <div class="alert alert-success mb-4"><span>{{ session('success') }}</span></div>
    @endif

    <div class="grid grid-cols-2 md:grid-cols-4 gap-4 mb-4">
        <div class="card bg-primary text-primary-content shadow">
            <div class="card-body p-4">
                <div class="text-xs opacity-80">تعداد سفارش</div>
                <div class="text-2xl font-bold">{{ number_format($orders->count()) }}</div>
            </div>
        </div>
        <div class="card bg-success text-success-content shadow">
            <div class="card-body p-4">
                <div class="text-xs opacity-80">مجموع خرید</div>
                <div class="text-xl font-bold">{{ number_format((float) $totalAmount) }}</div>
            </div>
        </div>
        <div class="card bg-base-100 shadow">
            <div class="card-body p-4">
                <div class="text-xs text-base-content/60">اولین سفارش</div>
                <div class="text-sm font-bold">{{ $orders->last()?->created_at?->format('Y/m/d') ?? '—' }}</div>
            </div>
        </div>
        <div class="card bg-base-100 shadow">
            <div class="card-body p-4">
                <div class="text-xs text-base-content/60">آخرین سفارش</div>
                <div class="text-sm font-bold">{{ $orders->first()?->created_at?->format('Y/m/d') ?? '—' }}</div>
            </div>
        </div>
    </div>

    <div class="card bg-base-100 shadow mb-4">
        <div class="card-body">
            <h2 class="card-title text-base mb-2">📋 اطلاعات تماس</h2>
            <div class="grid grid-cols-2 gap-3 text-sm">
                <div class="flex justify-between"><span class="text-base-content/60">تلفن:</span><span class="font-mono" dir="ltr">{{ $customer->phone }}</span></div>
                <div class="flex justify-between"><span class="text-base-content/60">کدپستی:</span><span class="font-mono" dir="ltr">{{ $customer->postal_code ?? '—' }}</span></div>
            </div>
            <div class="mt-3 text-sm leading-7"><strong>آدرس:</strong> {{ $customer->address ?? '—' }}</div>
        </div>
    </div>

    <div class="card bg-base-100 shadow mb-4">
        <div class="card-body">
            <div class="flex justify-between items-center mb-4">
                <h2 class="card-title text-base">📦 سفارشات</h2>
                <a href="{{ route('orders.create') }}" class="btn btn-primary btn-sm">➕ سفارش جدید</a>
            </div>
            @if($orders->isEmpty())
                <p class="text-sm text-base-content/50">هنوز سفارشی نیست.</p>
            @else
                <div class="overflow-x-auto">
                    <table class="table table-zebra table-sm">
                        <thead><tr><th>#</th><th>وضعیت</th><th>کانال</th><th>بیمه</th><th>تاریخ</th><th></th></tr></thead>
                        <tbody>
                            @foreach($orders as $o)
                                <tr>
                                    <td class="font-mono font-bold">{{ $o->order_number }}</td>
                                    <td><span class="badge badge-{{ $o->status_color }} badge-sm">{{ $o->status_label }}</span></td>
                                    <td class="text-xs">{{ $o->channel?->icon }} {{ $o->channel?->name ?? '—' }}</td>
                                    <td>{{ number_format((float) $o->insurance) }}</td>
                                    <td class="text-xs">{{ $o->created_at?->format('Y/m/d') }}</td>
                                    <td><a href="{{ route('orders.show', $o) }}" class="btn btn-ghost btn-xs">👁️</a></td>
                                </tr>
                            @endforeach
                        </tbody>
                    </table>
                </div>
            @endif
        </div>
    </div>

    <div class="card bg-base-100 shadow">
        <div class="card-body">
            <h2 class="card-title text-base mb-4">📜 تاریخچه</h2>
            @if($activities->isEmpty())
                <p class="text-sm text-base-content/50">تغییری ثبت نشده.</p>
            @else
                <div class="space-y-3">
                    @foreach($activities as $a)
                        <div class="flex gap-3 text-sm border-r-2 border-primary/30 pr-3">
                            <div class="text-xs text-base-content/50 whitespace-nowrap">{{ $a->created_at?->format('Y/m/d H:i') }}</div>
                            <div class="flex-1 font-bold">{{ $a->description }}</div>
                        </div>
                    @endforeach
                </div>
            @endif
        </div>
    </div>
</div>
""")

write_file("app/Livewire/Customers/Edit.php", r"""
<?php

namespace App\Livewire\Customers;

use App\Models\Customer;
use Livewire\Component;

class Edit extends Component
{
    public Customer $customer;
    public string $name = '';
    public string $phone = '';
    public string $postalCode = '';
    public string $address = '';
    public string $notes = '';

    public function mount(Customer $customer): void
    {
        $this->customer   = $customer;
        $this->name       = $customer->name ?? '';
        $this->phone      = $customer->phone ?? '';
        $this->postalCode = $customer->postal_code ?? '';
        $this->address    = $customer->address ?? '';
        $this->notes      = $customer->notes ?? '';
    }

    public function save()
    {
        $this->validate([
            'phone' => 'required|min:10|unique:customers,phone,' . $this->customer->id,
            'name'  => 'nullable|string|max:255',
        ], ['phone.unique' => 'این شماره قبلاً ثبت شده.']);

        $this->customer->update([
            'name'        => $this->name ?: 'بدون نام',
            'phone'       => $this->phone,
            'postal_code' => $this->postalCode,
            'address'     => $this->address,
            'notes'       => $this->notes,
        ]);

        session()->flash('success', 'ویرایش شد.');
        return redirect()->route('customers.show', $this->customer);
    }

    public function render()
    {
        return view('livewire.customers.edit')->layout('components.layouts.app');
    }
}
""")

write_file("resources/views/livewire/customers/edit.blade.php", r"""
<div class="p-6 max-w-3xl mx-auto">
    <div class="flex items-center gap-3 mb-6">
        <a href="{{ route('customers.show', $customer) }}" class="btn btn-ghost btn-sm">→</a>
        <h1 class="text-2xl font-bold">✏️ ویرایش مشتری</h1>
    </div>

    <div class="card bg-base-100 shadow">
        <div class="card-body space-y-4">
            <div class="form-control">
                <label class="label"><span class="label-text font-bold">📱 تلفن *</span></label>
                <input type="text" wire:model="phone" dir="ltr" class="input input-bordered font-mono" />
                @error('phone') <label class="label"><span class="label-text-alt text-error">{{ $message }}</span></label> @enderror
            </div>
            <div class="form-control">
                <label class="label"><span class="label-text font-bold">👤 نام</span></label>
                <input type="text" wire:model="name" class="input input-bordered" />
            </div>
            <div class="form-control">
                <label class="label"><span class="label-text font-bold">📮 کدپستی</span></label>
                <input type="text" wire:model="postalCode" dir="ltr" class="input input-bordered font-mono" />
            </div>
            <div class="form-control">
                <label class="label"><span class="label-text font-bold">📍 آدرس</span></label>
                <textarea wire:model="address" class="textarea textarea-bordered" rows="3"></textarea>
            </div>
            <div class="form-control">
                <label class="label"><span class="label-text font-bold">📝 یادداشت</span></label>
                <textarea wire:model="notes" class="textarea textarea-bordered" rows="2"></textarea>
            </div>
            <div class="card-actions justify-end mt-6">
                <a href="{{ route('customers.show', $customer) }}" class="btn btn-ghost">انصراف</a>
                <button wire:click="save" class="btn btn-primary">✅ ذخیره</button>
            </div>
        </div>
    </div>
</div>
""")

# =========================================================
# Certificates Index (ساده)
# =========================================================
print()
print("📦 Certificates...")

write_file("app/Livewire/Certificates/Index.php", r"""
<?php

namespace App\Livewire\Certificates;

use App\Models\Certificate;
use Livewire\Component;
use Livewire\WithPagination;

class Index extends Component
{
    use WithPagination;
    public string $search = '';

    public function updatingSearch(): void { $this->resetPage(); }

    public function delete(int $id): void
    {
        Certificate::find($id)?->delete();
        session()->flash('success', 'شناسنامه حذف شد.');
    }

    public function render()
    {
        $certificates = Certificate::query()
            ->with(['customer', 'order'])
            ->when($this->search, function ($q) {
                $q->where(function ($qq) {
                    $qq->where('code', 'like', "%{$this->search}%")
                       ->orWhere('serial', 'like', "%{$this->search}%")
                       ->orWhere('sku', 'like', "%{$this->search}%")
                       ->orWhere('stone_name', 'like', "%{$this->search}%");
                });
            })
            ->latest('id')->paginate(20);

        return view('livewire.certificates.index', compact('certificates'))
            ->layout('components.layouts.app');
    }
}
""")

write_file("resources/views/livewire/certificates/index.blade.php", r"""
<div class="p-6">
    @if (session('success'))
        <div class="alert alert-success mb-4"><span>{{ session('success') }}</span></div>
    @endif

    <div class="flex flex-wrap items-center justify-between gap-4 mb-6">
        <h1 class="text-2xl font-bold">💎 شناسنامه‌ها</h1>
        <input type="text" wire:model.live.debounce.400ms="search" placeholder="🔍 کد، SKU، سنگ..." class="input input-bordered input-sm w-64" />
    </div>

    <div class="card bg-base-100 shadow">
        <div class="card-body p-0">
            <div class="overflow-x-auto">
                <table class="table table-zebra">
                    <thead>
                        <tr><th>کد</th><th>SKU</th><th>سنگ</th><th>فلز</th><th>ابعاد</th><th>وزن</th><th>مشتری</th><th>تاریخ</th><th>عملیات</th></tr>
                    </thead>
                    <tbody>
                        @forelse($certificates as $c)
                            <tr>
                                <td class="font-mono font-bold">{{ $c->code }}</td>
                                <td class="font-mono text-xs" dir="ltr">{{ $c->sku ?? '—' }}</td>
                                <td><span class="badge badge-outline badge-sm">{{ $c->stone_name }}</span></td>
                                <td class="text-xs">{{ $c->metal_en ?? $c->metal }}</td>
                                <td class="text-xs">{{ $c->length }}×{{ $c->width }}</td>
                                <td class="text-xs">{{ $c->weight }}</td>
                                <td class="text-xs">{{ $c->customer?->name ?? '—' }}</td>
                                <td class="text-xs">{{ $c->issued_at?->format('Y/m/d') }}</td>
                                <td>
                                    <button wire:click="delete({{ $c->id }})" wire:confirm="حذف شود؟" class="btn btn-ghost btn-xs text-error">🗑️</button>
                                </td>
                            </tr>
                        @empty
                            <tr><td colspan="9" class="text-center py-8 text-base-content/50">شناسنامه‌ای نیست</td></tr>
                        @endforelse
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    <div class="mt-4">{{ $certificates->links() }}</div>
</div>
""")

# =========================================================
# Reports Index (ساده)
# =========================================================
print()
print("📦 Reports...")

write_file("app/Livewire/Reports/Index.php", r"""
<?php

namespace App\Livewire\Reports;

use App\Models\Channel;
use App\Models\Customer;
use App\Models\Order;
use Livewire\Component;

class Index extends Component
{
    public string $range = '7days';

    public function render()
    {
        $start = match ($this->range) {
            'today'  => now()->startOfDay(),
            '7days'  => now()->subDays(7)->startOfDay(),
            '30days' => now()->subDays(30)->startOfDay(),
            'year'   => now()->startOfYear(),
            default  => now()->subDays(7)->startOfDay(),
        };

        $orders = Order::where('created_at', '>=', $start)->get();
        $totalCount  = $orders->count();
        $totalAmount = (float) $orders->sum('amount');
        $avgAmount   = $totalCount > 0 ? $totalAmount / $totalCount : 0;

        $days = match ($this->range) {
            'today' => 1, '7days' => 7, '30days' => 30, 'year' => 12, default => 7,
        };

        $dailyLabels = []; $dailyCounts = []; $dailyAmounts = [];

        if ($this->range === 'year') {
            for ($i = 11; $i >= 0; $i--) {
                $ms = now()->subMonths($i)->startOfMonth();
                $me = now()->subMonths($i)->endOfMonth();
                $dailyLabels[]  = $ms->format('Y/m');
                $dailyCounts[]  = Order::whereBetween('created_at', [$ms, $me])->count();
                $dailyAmounts[] = (float) Order::whereBetween('created_at', [$ms, $me])->sum('amount');
            }
        } else {
            for ($i = $days - 1; $i >= 0; $i--) {
                $date = now()->subDays($i);
                $ds = $date->copy()->startOfDay();
                $de = $date->copy()->endOfDay();
                $dailyLabels[]  = $date->format('m/d');
                $dailyCounts[]  = Order::whereBetween('created_at', [$ds, $de])->count();
                $dailyAmounts[] = (float) Order::whereBetween('created_at', [$ds, $de])->sum('amount');
            }
        }

        $byStatus = [
            Order::where('status', 'pending')->where('created_at', '>=', $start)->count(),
            Order::where('status', 'final-check')->where('created_at', '>=', $start)->count(),
            Order::where('status', 'courier')->where('created_at', '>=', $start)->count(),
        ];

        $channels = Channel::withCount(['orders' => fn ($q) => $q->where('created_at', '>=', $start)])
            ->orderByDesc('orders_count')->get();

        $channelLabels = $channels->pluck('name')->toArray();
        $channelCounts = $channels->pluck('orders_count')->toArray();
        $channelColors = $channels->pluck('color')->toArray();

        $topCustomers = Customer::has('orders')->withCount('orders')->orderByDesc('orders_count')->limit(5)->get();

        return view('livewire.reports.index', compact(
            'totalCount', 'totalAmount', 'avgAmount',
            'dailyLabels', 'dailyCounts', 'dailyAmounts',
            'byStatus', 'channelLabels', 'channelCounts', 'channelColors', 'topCustomers'
        ))->layout('components.layouts.app');
    }
}
""")

write_file("resources/views/livewire/reports/index.blade.php", r"""
<div class="p-6 space-y-6">
    <div class="flex flex-wrap items-center justify-between gap-3">
        <h1 class="text-2xl font-bold">📊 گزارش‌ها</h1>
        <div class="flex gap-1 bg-base-100 rounded-lg p-1 shadow">
            <button wire:click="$set('range', 'today')" class="btn btn-sm {{ $range === 'today' ? 'btn-primary' : 'btn-ghost' }}">امروز</button>
            <button wire:click="$set('range', '7days')" class="btn btn-sm {{ $range === '7days' ? 'btn-primary' : 'btn-ghost' }}">۷ روز</button>
            <button wire:click="$set('range', '30days')" class="btn btn-sm {{ $range === '30days' ? 'btn-primary' : 'btn-ghost' }}">۳۰ روز</button>
            <button wire:click="$set('range', 'year')" class="btn btn-sm {{ $range === 'year' ? 'btn-primary' : 'btn-ghost' }}">امسال</button>
        </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div class="card bg-primary text-primary-content shadow"><div class="card-body p-5">
            <div class="text-xs opacity-80">📦 تعداد سفارشات</div>
            <div class="text-3xl font-extrabold mt-2">{{ number_format($totalCount) }}</div>
        </div></div>
        <div class="card bg-success text-success-content shadow"><div class="card-body p-5">
            <div class="text-xs opacity-80">💰 مجموع فروش</div>
            <div class="text-2xl font-extrabold mt-2" dir="ltr">{{ number_format($totalAmount) }}</div>
        </div></div>
        <div class="card bg-info text-info-content shadow"><div class="card-body p-5">
            <div class="text-xs opacity-80">📊 میانگین</div>
            <div class="text-2xl font-extrabold mt-2" dir="ltr">{{ number_format($avgAmount) }}</div>
        </div></div>
    </div>

    <div class="card bg-base-100 shadow">
        <div class="card-body">
            <h2 class="card-title text-base mb-4">📈 روند سفارشات</h2>
            <div style="height: 300px;"><canvas id="dailyChart"></canvas></div>
        </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="card bg-base-100 shadow"><div class="card-body">
            <h2 class="card-title text-base mb-4">📊 تفکیک وضعیت</h2>
            <div style="height: 250px;"><canvas id="statusChart"></canvas></div>
        </div></div>
        <div class="card bg-base-100 shadow"><div class="card-body">
            <h2 class="card-title text-base mb-4">🌐 توزیع کانال‌ها</h2>
            <div style="height: 250px;"><canvas id="channelChart"></canvas></div>
        </div></div>
    </div>

    <div class="card bg-base-100 shadow">
        <div class="card-body">
            <h2 class="card-title text-base mb-4">🏆 مشتریان برتر</h2>
            @forelse($topCustomers as $i => $c)
                <div class="flex items-center gap-3 py-3 border-b border-base-200 last:border-0">
                    <div class="w-10 h-10 rounded-full bg-primary text-primary-content flex items-center justify-center font-bold">{{ $i + 1 }}</div>
                    <div class="flex-1">
                        <a href="{{ route('customers.show', $c) }}" class="link link-hover font-bold">{{ $c->name ?? 'بدون نام' }}</a>
                        <div class="text-xs text-base-content/60 font-mono" dir="ltr">{{ $c->phone }}</div>
                    </div>
                    <div class="badge badge-primary badge-lg">{{ $c->orders_count }} سفارش</div>
                </div>
            @empty
                <p class="text-sm text-base-content/50">داده‌ای نیست.</p>
            @endforelse
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script>
document.addEventListener('livewire:init', () => {
    let dailyChart, statusChart, channelChart;
    function initCharts() {
        if (dailyChart) dailyChart.destroy();
        if (statusChart) statusChart.destroy();
        if (channelChart) channelChart.destroy();
        Chart.defaults.font.family = 'Vazirmatn, Tahoma, sans-serif';
        Chart.defaults.font.size = 12;

        const dc = document.getElementById('dailyChart');
        if (dc) dailyChart = new Chart(dc, {
            type: 'line',
            data: {
                labels: @json($dailyLabels),
                datasets: [
                    { label: 'تعداد', data: @json($dailyCounts), borderColor: '#1a5276', backgroundColor: 'rgba(26,82,118,.1)', tension: .3, fill: true, yAxisID: 'y' },
                    { label: 'مبلغ', data: @json($dailyAmounts), borderColor: '#27ae60', backgroundColor: 'rgba(39,174,96,.1)', tension: .3, fill: true, yAxisID: 'y1', hidden: true }
                ]
            },
            options: { responsive: true, maintainAspectRatio: false,
                scales: { y: { position: 'right' }, y1: { position: 'left', grid: { drawOnChartArea: false } } }
            }
        });

        const sc = document.getElementById('statusChart');
        if (sc) statusChart = new Chart(sc, {
            type: 'doughnut',
            data: {
                labels: ['📝 ثبت سفارش', '🔍 چک نهایی', '🚚 تحویل مامور'],
                datasets: [{ data: @json($byStatus), backgroundColor: ['#ffb74d', '#42a5f5', '#4caf50'], borderWidth: 2, borderColor: '#fff' }]
            },
            options: { responsive: true, maintainAspectRatio: false }
        });

        const cc = document.getElementById('channelChart');
        if (cc) channelChart = new Chart(cc, {
            type: 'bar',
            data: {
                labels: @json($channelLabels),
                datasets: [{ label: 'تعداد', data: @json($channelCounts), backgroundColor: @json($channelColors), borderWidth: 1 }]
            },
            options: { responsive: true, maintainAspectRatio: false, indexAxis: 'y',
                plugins: { legend: { display: false } }
            }
        });
    }
    initCharts();
    Livewire.hook('morph.updated', () => setTimeout(initCharts, 100));
});
</script>
""")

# =========================================================
# Settings Index (ساده)
# =========================================================
print()
print("📦 Settings...")

write_file("app/Livewire/Settings/Index.php", r"""
<?php

namespace App\Livewire\Settings;

use App\Models\User;
use Illuminate\Support\Facades\Auth;
use Livewire\Component;

class Index extends Component
{
    public string $name = '';
    public string $email = '';
    public string $newPassword = '';
    public string $newPasswordConfirm = '';

    public function mount(): void
    {
        $user = Auth::user();
        $this->name  = $user->name;
        $this->email = $user->email;
    }

    public function updateProfile(): void
    {
        $this->validate([
            'name'  => 'required|string|max:255',
            'email' => 'required|email|unique:users,email,' . Auth::id(),
        ]);

        Auth::user()->update(['name' => $this->name, 'email' => $this->email]);
        session()->flash('profile_success', 'پروفایل به‌روز شد.');
    }

    public function updatePassword(): void
    {
        $this->validate([
            'newPassword'        => 'required|min:8',
            'newPasswordConfirm' => 'required|same:newPassword',
        ], [
            'newPassword.min'         => 'رمز جدید حداقل ۸ کاراکتر.',
            'newPasswordConfirm.same' => 'تکرار مطابقت ندارد.',
        ]);

        Auth::user()->update(['password' => bcrypt($this->newPassword)]);
        $this->reset(['newPassword', 'newPasswordConfirm']);
        session()->flash('password_success', 'رمز تغییر کرد.');
    }

    public function render()
    {
        return view('livewire.settings.index', ['users' => User::with('roles')->get()])
            ->layout('components.layouts.app');
    }
}
""")

write_file("resources/views/livewire/settings/index.blade.php", r"""
<div class="p-6 space-y-6 max-w-4xl mx-auto">
    <h1 class="text-2xl font-bold">⚙️ تنظیمات</h1>

    <div class="card bg-base-100 shadow">
        <div class="card-body">
            <h2 class="card-title text-base mb-4">👤 پروفایل</h2>
            @if (session('profile_success'))
                <div class="alert alert-success mb-3"><span>{{ session('profile_success') }}</span></div>
            @endif
            <div class="space-y-4">
                <div class="form-control">
                    <label class="label"><span class="label-text font-bold">نام</span></label>
                    <input type="text" wire:model="name" class="input input-bordered" />
                </div>
                <div class="form-control">
                    <label class="label"><span class="label-text font-bold">ایمیل</span></label>
                    <input type="email" wire:model="email" dir="ltr" class="input input-bordered" />
                </div>
                <div class="card-actions justify-end">
                    <button wire:click="updateProfile" class="btn btn-primary btn-sm">💾 ذخیره</button>
                </div>
            </div>
        </div>
    </div>

    <div class="card bg-base-100 shadow">
        <div class="card-body">
            <h2 class="card-title text-base mb-4">🔐 تغییر رمز</h2>
            @if (session('password_success'))
                <div class="alert alert-success mb-3"><span>{{ session('password_success') }}</span></div>
            @endif
            <div class="space-y-4">
                <div class="form-control">
                    <label class="label"><span class="label-text font-bold">رمز جدید</span></label>
                    <input type="password" wire:model="newPassword" dir="ltr" class="input input-bordered" />
                    @error('newPassword') <label class="label"><span class="label-text-alt text-error">{{ $message }}</span></label> @enderror
                </div>
                <div class="form-control">
                    <label class="label"><span class="label-text font-bold">تکرار رمز</span></label>
                    <input type="password" wire:model="newPasswordConfirm" dir="ltr" class="input input-bordered" />
                </div>
                <div class="card-actions justify-end">
                    <button wire:click="updatePassword" class="btn btn-warning btn-sm">🔐 تغییر</button>
                </div>
            </div>
        </div>
    </div>

    <div class="card bg-base-100 shadow">
        <div class="card-body">
            <h2 class="card-title text-base mb-4">👥 کاربران</h2>
            <div class="overflow-x-auto">
                <table class="table table-zebra table-sm">
                    <thead><tr><th>#</th><th>نام</th><th>ایمیل</th><th>نقش</th></tr></thead>
                    <tbody>
                        @foreach($users as $u)
                            <tr>
                                <td>{{ $u->id }}</td>
                                <td class="font-bold">{{ $u->name }}</td>
                                <td class="font-mono text-xs" dir="ltr">{{ $u->email }}</td>
                                <td>@foreach($u->roles as $r)<span class="badge badge-primary badge-sm">{{ $r->name }}</span>@endforeach</td>
                            </tr>
                        @endforeach
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    <div class="card bg-base-100 shadow">
        <div class="card-body">
            <h2 class="card-title text-base mb-4">ℹ️ درباره سیستم</h2>
            <div class="text-sm space-y-2 leading-7">
                <div><strong>نام:</strong> شاپگان نسخه ۲ (ShopGun V2)</div>
                <div><strong>سازنده:</strong> گروه هنری اقاقیا</div>
                <div><strong>معماری:</strong> امیر حاجی قاسمی</div>
                <div><strong>محل توسعه:</strong> نیشابور</div>
                <div><strong>Laravel:</strong> {{ app()->version() }}</div>
                <div><strong>PHP:</strong> {{ PHP_VERSION }}</div>
            </div>
        </div>
    </div>
</div>
""")

print()
print("═" * 60)
print("✅ مرحله ۲ (بخش ۳) — همه کامپوننت‌ها کامل شد")
print("═" * 60)
print()
print("📌 حالا این دستورات رو بزن:")
print("   php artisan optimize:clear")
print("   php artisan route:list")
print("   php artisan serve --host=0.0.0.0 --port=8000")
print()
