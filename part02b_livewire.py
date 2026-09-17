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
print("🚀 مرحله ۲ (بخش ۲) — Orders, Customers, Certificates")
print("═" * 60)
print()

# =========================================================
# Orders Index
# =========================================================
print("📦 Orders...")

write_file("app/Livewire/Orders/Index.php", r"""
<?php

namespace App\Livewire\Orders;

use App\Models\Channel;
use App\Models\Order;
use Livewire\Component;
use Livewire\WithPagination;

class Index extends Component
{
    use WithPagination;

    public string $search = '';
    public string $statusFilter = '';
    public string $channelFilter = '';
    public string $dateFrom = '';
    public string $dateTo = '';
    public string $insuranceFrom = '';
    public string $insuranceTo = '';
    public string $sortField = 'id';
    public string $sortDir = 'desc';
    public array $selected = [];
    public bool $advancedOpen = false;

    protected $queryString = [
        'search'        => ['except' => ''],
        'statusFilter'  => ['except' => ''],
        'channelFilter' => ['except' => ''],
    ];

    public function updatingSearch(): void { $this->resetPage(); }
    public function updatingStatusFilter(): void { $this->resetPage(); }
    public function updatingChannelFilter(): void { $this->resetPage(); }

    public function toggleAdvanced(): void { $this->advancedOpen = ! $this->advancedOpen; }

    public function sortBy(string $field): void
    {
        if ($this->sortField === $field) {
            $this->sortDir = $this->sortDir === 'asc' ? 'desc' : 'asc';
        } else {
            $this->sortField = $field;
            $this->sortDir   = 'asc';
        }
        $this->resetPage();
    }

    public function clearFilters(): void
    {
        $this->reset(['search', 'statusFilter', 'channelFilter', 'dateFrom', 'dateTo', 'insuranceFrom', 'insuranceTo']);
        $this->resetPage();
    }

    public function toggleSelect(int $id): void
    {
        if (in_array($id, $this->selected)) {
            $this->selected = array_values(array_diff($this->selected, [$id]));
        } else {
            $this->selected[] = $id;
        }
    }

    public function clearSelection(): void { $this->selected = []; }

    public function bulkChangeStatus(string $status): void
    {
        if (! in_array($status, ['pending', 'final-check', 'courier'])) return;
        if (empty($this->selected)) return;
        Order::whereIn('id', $this->selected)->update(['status' => $status]);
        session()->flash('success', count($this->selected) . ' سفارش به‌روز شد.');
        $this->selected = [];
    }

    public function bulkDelete(): void
    {
        if (empty($this->selected)) return;
        $count = count($this->selected);
        Order::whereIn('id', $this->selected)->delete();
        session()->flash('success', "{$count} سفارش حذف شد.");
        $this->selected = [];
    }

    public function bulkPrintLabels()
    {
        if (empty($this->selected)) return null;
        return redirect()->route('orders.bulk-print-labels', ['ids' => implode(',', $this->selected)]);
    }

    public function changeStatus(int $orderId, string $status): void
    {
        if (! in_array($status, ['pending', 'final-check', 'courier'])) return;
        $order = Order::find($orderId);
        if ($order) {
            $order->update(['status' => $status]);
            session()->flash('success', "وضعیت سفارش #{$order->order_number} به‌روز شد.");
        }
    }

    public function deleteOrder(int $orderId): void
    {
        Order::find($orderId)?->delete();
        session()->flash('success', 'سفارش حذف شد.');
    }

    protected function buildQuery()
    {
        return Order::query()
            ->with(['customer', 'channel'])
            ->when($this->search, function ($q) {
                $q->where(function ($qq) {
                    $qq->where('order_number', 'like', "%{$this->search}%")
                       ->orWhere('phone', 'like', "%{$this->search}%")
                       ->orWhere('postal_code', 'like', "%{$this->search}%")
                       ->orWhereHas('customer', fn ($cq) => $cq->where('name', 'like', "%{$this->search}%"));
                });
            })
            ->when($this->statusFilter, fn ($q) => $q->where('status', $this->statusFilter))
            ->when($this->channelFilter, fn ($q) => $q->where('channel_id', $this->channelFilter))
            ->when($this->dateFrom, fn ($q) => $q->whereDate('created_at', '>=', $this->dateFrom))
            ->when($this->dateTo, fn ($q) => $q->whereDate('created_at', '<=', $this->dateTo))
            ->when($this->insuranceFrom !== '', fn ($q) => $q->where('insurance', '>=', (float) $this->insuranceFrom))
            ->when($this->insuranceTo !== '', fn ($q) => $q->where('insurance', '<=', (float) $this->insuranceTo))
            ->orderBy($this->sortField, $this->sortDir);
    }

    public function render()
    {
        return view('livewire.orders.index', [
            'orders'   => $this->buildQuery()->paginate(20),
            'channels' => Channel::where('is_active', true)->orderBy('sort_order')->get(),
        ])->layout('components.layouts.app');
    }
}
""")

write_file("resources/views/livewire/orders/index.blade.php", r"""
<div class="p-6">
    @if (session('success'))
        <div class="alert alert-success mb-4"><span>{{ session('success') }}</span></div>
    @endif

    <div class="flex flex-wrap items-center justify-between gap-4 mb-4">
        <h1 class="text-2xl font-bold">📦 سفارشات</h1>
        <div class="flex flex-wrap gap-2 items-center">
            <input type="text" wire:model.live.debounce.400ms="search" placeholder="🔍 جستجو..." class="input input-bordered input-sm w-52" />
            <button wire:click="toggleAdvanced" class="btn btn-sm {{ $advancedOpen ? 'btn-primary' : 'btn-outline' }}">🎛️ فیلتر پیشرفته</button>
            <a href="{{ route('orders.import') }}" class="btn btn-secondary btn-sm">📥 وارد کردن</a>
            <a href="{{ route('orders.create') }}" class="btn btn-primary btn-sm">➕ سفارش جدید</a>
        </div>
    </div>

    @if($advancedOpen)
        <div class="card bg-base-100 shadow mb-4 border-2 border-primary/30">
            <div class="card-body py-4">
                <div class="flex justify-between items-center mb-3">
                    <h2 class="font-bold text-sm">🎛️ فیلترهای پیشرفته</h2>
                    <button wire:click="clearFilters" class="btn btn-ghost btn-xs">✕ پاک کردن</button>
                </div>
                <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">📊 وضعیت</span></label>
                        <select wire:model.live="statusFilter" class="select select-bordered select-sm">
                            <option value="">همه</option>
                            <option value="pending">📝 ثبت سفارش</option>
                            <option value="final-check">🔍 چک نهایی</option>
                            <option value="courier">🚚 تحویل مامور</option>
                        </select>
                    </div>
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">🌐 کانال</span></label>
                        <select wire:model.live="channelFilter" class="select select-bordered select-sm">
                            <option value="">همه</option>
                            @foreach($channels as $channel)
                                <option value="{{ $channel->id }}">{{ $channel->icon }} {{ $channel->name }}</option>
                            @endforeach
                        </select>
                    </div>
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">📅 از تاریخ</span></label>
                        <input type="date" wire:model.live="dateFrom" class="input input-bordered input-sm" dir="ltr" />
                    </div>
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">📅 تا تاریخ</span></label>
                        <input type="date" wire:model.live="dateTo" class="input input-bordered input-sm" dir="ltr" />
                    </div>
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">💰 بیمه از</span></label>
                        <input type="number" wire:model.live.debounce.500ms="insuranceFrom" class="input input-bordered input-sm" dir="ltr" />
                    </div>
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">💰 بیمه تا</span></label>
                        <input type="number" wire:model.live.debounce.500ms="insuranceTo" class="input input-bordered input-sm" dir="ltr" />
                    </div>
                </div>
            </div>
        </div>
    @endif

    @if(count($selected) > 0)
        <div class="alert alert-info mb-4 flex flex-wrap items-center gap-2">
            <span class="font-bold">✨ {{ count($selected) }} انتخاب شده</span>
            <div class="flex gap-1 ml-auto">
                <button wire:click="bulkChangeStatus('pending')" class="btn btn-secondary btn-sm">📝</button>
                <button wire:click="bulkChangeStatus('final-check')" class="btn btn-info btn-sm">🔍</button>
                <button wire:click="bulkChangeStatus('courier')" class="btn btn-success btn-sm">🚚</button>
                <button wire:click="bulkPrintLabels" class="btn btn-primary btn-sm">🏷️ چاپ</button>
                <button wire:click="clearSelection" class="btn btn-ghost btn-sm">✕</button>
                <button wire:click="bulkDelete" wire:confirm="{{ count($selected) }} سفارش حذف شود؟" class="btn btn-error btn-sm">🗑️</button>
            </div>
        </div>
    @endif

    <div class="card bg-base-100 shadow">
        <div class="card-body p-0">
            <div class="overflow-x-auto">
                <table class="table table-zebra">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th class="cursor-pointer" wire:click="sortBy('order_number')">شماره @if($sortField === 'order_number') {{ $sortDir === 'asc' ? '▲' : '▼' }} @endif</th>
                            <th>مشتری</th>
                            <th>تلفن</th>
                            <th>وضعیت</th>
                            <th>کانال</th>
                            <th class="cursor-pointer" wire:click="sortBy('insurance')">بیمه @if($sortField === 'insurance') {{ $sortDir === 'asc' ? '▲' : '▼' }} @endif</th>
                            <th class="cursor-pointer" wire:click="sortBy('created_at')">تاریخ @if($sortField === 'created_at') {{ $sortDir === 'asc' ? '▲' : '▼' }} @endif</th>
                            <th>عملیات</th>
                        </tr>
                    </thead>
                    <tbody>
                        @forelse($orders as $order)
                            <tr wire:key="order-{{ $order->id }}" class="{{ in_array($order->id, $selected) ? 'bg-primary/10' : '' }}">
                                <td><input type="checkbox" class="checkbox checkbox-sm" @checked(in_array($order->id, $selected)) wire:click="toggleSelect({{ $order->id }})" /></td>
                                <td class="font-mono font-bold"><a href="{{ route('orders.show', $order) }}" class="link link-primary">{{ $order->order_number }}</a></td>
                                <td>@if($order->customer)<a href="{{ route('customers.show', $order->customer) }}" class="link link-hover">{{ $order->customer->name }}</a>@else — @endif</td>
                                <td class="font-mono" dir="ltr">{{ $order->phone ?? '—' }}</td>
                                <td><span class="badge badge-{{ $order->status_color }}">{{ $order->status_label }}</span></td>
                                <td>@if($order->channel)<span class="badge badge-outline badge-sm">{{ $order->channel->icon }} {{ $order->channel->name }}</span>@else — @endif</td>
                                <td>{{ number_format((float) $order->insurance) }}</td>
                                <td class="text-xs">{{ $order->created_at?->format('Y/m/d H:i') }}</td>
                                <td>
                                    <div class="flex gap-1">
                                        <a href="{{ route('orders.show', $order) }}" class="btn btn-ghost btn-xs">👁️</a>
                                        <a href="{{ route('orders.edit', $order) }}" class="btn btn-ghost btn-xs">✏️</a>
                                        <a href="{{ route('orders.print-label', $order) }}" class="btn btn-ghost btn-xs">🏷️</a>
                                        <button wire:click="deleteOrder({{ $order->id }})" wire:confirm="حذف شود؟" class="btn btn-ghost btn-xs text-error">🗑️</button>
                                    </div>
                                </td>
                            </tr>
                        @empty
                            <tr><td colspan="9" class="text-center py-8 text-base-content/50">سفارشی نیست</td></tr>
                        @endforelse
                    </tbody>
                </table>
            </div>
        </div>
    </div>
    <div class="mt-4">{{ $orders->links() }}</div>
</div>
""")

write_file("app/Livewire/Orders/Show.php", r"""
<?php

namespace App\Livewire\Orders;

use App\Models\Order;
use Livewire\Component;

class Show extends Component
{
    public Order $order;

    public function mount(Order $order): void
    {
        $this->order = $order->load(['customer', 'channel']);
    }

    public function changeStatus(string $status): void
    {
        if (! in_array($status, ['pending', 'final-check', 'courier'])) return;
        $this->order->update(['status' => $status]);
        $this->order->refresh();
        session()->flash('success', 'وضعیت به‌روز شد.');
    }

    public function delete()
    {
        $number = $this->order->order_number;
        $this->order->delete();
        session()->flash('success', "سفارش #{$number} حذف شد.");
        return redirect()->route('orders.index');
    }

    public function render()
    {
        $activities = $this->order->activities()->with('causer')->limit(20)->get();
        return view('livewire.orders.show', compact('activities'))
            ->layout('components.layouts.app');
    }
}
""")

write_file("resources/views/livewire/orders/show.blade.php", r"""
<div class="p-6 max-w-4xl mx-auto">
    <div class="flex flex-wrap items-center justify-between gap-3 mb-6">
        <div class="flex items-center gap-3">
            <a href="{{ route('orders.index') }}" class="btn btn-ghost btn-sm">→</a>
            <h1 class="text-2xl font-bold">سفارش #{{ $order->order_number }}</h1>
        </div>
        <div class="flex gap-2">
            <a href="{{ route('orders.edit', $order) }}" class="btn btn-warning btn-sm">✏️ ویرایش</a>
            <button wire:click="delete" wire:confirm="حذف شود؟" class="btn btn-error btn-sm">🗑️</button>
        </div>
    </div>

    @if (session('success'))
        <div class="alert alert-success mb-4"><span>{{ session('success') }}</span></div>
    @endif

    <div class="card bg-base-100 shadow mb-4">
        <div class="card-body">
            <h2 class="card-title text-base mb-2">📊 وضعیت</h2>
            <div class="flex flex-wrap gap-2">
                @foreach(['pending' => '📝 ثبت سفارش', 'final-check' => '🔍 چک نهایی', 'courier' => '🚚 تحویل مامور'] as $key => $label)
                    <button wire:click="changeStatus('{{ $key }}')" class="btn btn-sm {{ $order->status === $key ? 'btn-primary' : 'btn-outline' }}">{{ $label }}</button>
                @endforeach
            </div>
        </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
        <div class="card bg-base-100 shadow">
            <div class="card-body">
                <h2 class="card-title text-base mb-2">👤 مشتری</h2>
                <div class="text-sm space-y-1">
                    <div class="flex justify-between"><span class="text-base-content/60">نام:</span><span class="font-bold">{{ $order->customer?->name ?? '—' }}</span></div>
                    <div class="flex justify-between"><span class="text-base-content/60">تلفن:</span><span class="font-mono" dir="ltr">{{ $order->phone ?? '—' }}</span></div>
                    <div class="flex justify-between"><span class="text-base-content/60">کدپستی:</span><span class="font-mono" dir="ltr">{{ $order->postal_code ?? '—' }}</span></div>
                </div>
            </div>
        </div>
        <div class="card bg-base-100 shadow">
            <div class="card-body">
                <h2 class="card-title text-base mb-2">📦 اطلاعات</h2>
                <div class="text-sm space-y-1">
                    <div class="flex justify-between"><span class="text-base-content/60">کانال:</span><span>@if($order->channel)<span class="badge badge-outline">{{ $order->channel->icon }} {{ $order->channel->name }}</span>@else — @endif</span></div>
                    <div class="flex justify-between"><span class="text-base-content/60">بیمه:</span><span>{{ number_format((float) $order->insurance) }}</span></div>
                    <div class="flex justify-between"><span class="text-base-content/60">مبلغ:</span><span>{{ number_format((float) $order->amount) }}</span></div>
                </div>
            </div>
        </div>
    </div>

    <div class="card bg-base-100 shadow mb-4">
        <div class="card-body">
            <h2 class="card-title text-base mb-2">📍 آدرس</h2>
            <p class="text-sm leading-7">{{ $order->address ?? '—' }}</p>
        </div>
    </div>

    <div class="card bg-base-100 shadow">
        <div class="card-body">
            <h2 class="card-title text-base mb-4">📜 تاریخچه</h2>
            @if($activities->isEmpty())
                <p class="text-sm text-base-content/50">هنوز تغییری ثبت نشده.</p>
            @else
                <div class="space-y-3">
                    @foreach($activities as $a)
                        <div class="flex gap-3 text-sm border-r-2 border-primary/30 pr-3">
                            <div class="text-xs text-base-content/50 whitespace-nowrap">{{ $a->created_at?->format('Y/m/d H:i') }}</div>
                            <div class="flex-1">
                                <div class="font-bold">{{ $a->description }}</div>
                                @if($a->causer)<div class="text-xs text-base-content/60 mt-1">توسط {{ $a->causer->name ?? 'کاربر' }}</div>@endif
                            </div>
                        </div>
                    @endforeach
                </div>
            @endif
        </div>
    </div>
</div>
""")

write_file("app/Livewire/Orders/Create.php", r"""
<?php

namespace App\Livewire\Orders;

use App\Models\Channel;
use App\Models\Customer;
use App\Models\Order;
use Livewire\Component;

class Create extends Component
{
    public string $phone = '';
    public string $customerName = '';
    public string $postalCode = '';
    public string $address = '';
    public string $insurance = '0';
    public string $status = 'pending';
    public ?int $channelId = null;
    public bool $customerFound = false;
    public ?int $existingCustomerId = null;

    public function updatedPhone(): void
    {
        $normalized = $this->normalizePhone($this->phone);
        if (strlen($normalized) < 10) {
            $this->customerFound = false;
            $this->existingCustomerId = null;
            return;
        }
        $customer = Customer::where('phone', $normalized)->first();
        if ($customer) {
            $this->customerFound = true;
            $this->existingCustomerId = $customer->id;
            $this->customerName = $customer->name ?? '';
            $this->postalCode   = $customer->postal_code ?? '';
            $this->address      = $customer->address ?? '';
        } else {
            $this->customerFound = false;
            $this->existingCustomerId = null;
        }
    }

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
            'phone'        => 'required|min:10',
            'customerName' => 'nullable|string|max:255',
            'postalCode'   => 'nullable|string|max:20',
            'address'      => 'nullable|string',
            'insurance'    => 'nullable|numeric',
            'status'       => 'required|in:pending,final-check,courier',
            'channelId'    => 'nullable|exists:channels,id',
        ]);

        $normalized = $this->normalizePhone($this->phone);

        $customer = Customer::where('phone', $normalized)->first();
        if ($customer) {
            $customer->update([
                'name'        => $this->customerName ?: $customer->name,
                'postal_code' => $this->postalCode ?: $customer->postal_code,
                'address'     => $this->address ?: $customer->address,
            ]);
        } else {
            $customer = Customer::create([
                'name'        => $this->customerName ?: 'بدون نام',
                'phone'       => $normalized,
                'postal_code' => $this->postalCode,
                'address'     => $this->address,
            ]);
        }

        $lastNumber = (int) Order::max('order_number');
        $newNumber  = max($lastNumber + 1, 317401);

        Order::create([
            'order_number' => (string) $newNumber,
            'customer_id'  => $customer->id,
            'channel_id'   => $this->channelId,
            'status'       => $this->status,
            'amount'       => 0,
            'insurance'    => (float) ($this->insurance ?: 0),
            'phone'        => $normalized,
            'address'      => $this->address,
            'postal_code'  => $this->postalCode,
        ]);

        session()->flash('success', "سفارش #{$newNumber} ثبت شد.");
        return redirect()->route('orders.index');
    }

    public function render()
    {
        return view('livewire.orders.create', [
            'channels' => Channel::where('is_active', true)->orderBy('sort_order')->get(),
        ])->layout('components.layouts.app');
    }
}
""")

write_file("resources/views/livewire/orders/create.blade.php", r"""
<div class="p-6 max-w-3xl mx-auto">
    <div class="flex items-center gap-3 mb-6">
        <a href="{{ route('orders.index') }}" class="btn btn-ghost btn-sm">→</a>
        <h1 class="text-2xl font-bold">➕ سفارش جدید</h1>
    </div>

    <div class="card bg-base-100 shadow">
        <div class="card-body space-y-4">
            <div class="form-control">
                <label class="label"><span class="label-text font-bold">📱 تلفن *</span></label>
                <input type="text" wire:model.live.debounce.500ms="phone" dir="ltr" class="input input-bordered font-mono" placeholder="09151234567" />
                @if($customerFound)
                    <label class="label"><span class="label-text-alt text-success font-bold">✅ مشتری موجود — ID: {{ $existingCustomerId }}</span></label>
                @elseif(strlen(preg_replace('/\D/', '', $phone)) >= 10)
                    <label class="label"><span class="label-text-alt text-info font-bold">🆕 مشتری جدید</span></label>
                @endif
                @error('phone') <label class="label"><span class="label-text-alt text-error">{{ $message }}</span></label> @enderror
            </div>

            <div class="form-control">
                <label class="label"><span class="label-text font-bold">👤 نام</span></label>
                <input type="text" wire:model="customerName" class="input input-bordered" />
            </div>

            <div class="form-control">
                <label class="label"><span class="label-text font-bold">📮 کدپستی</span></label>
                <input type="text" wire:model="postalCode" dir="ltr" class="input input-bordered font-mono" />
            </div>

            <div class="form-control">
                <label class="label"><span class="label-text font-bold">📍 آدرس</span></label>
                <textarea wire:model="address" class="textarea textarea-bordered" rows="3"></textarea>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="form-control">
                    <label class="label"><span class="label-text font-bold">💰 بیمه</span></label>
                    <input type="number" wire:model="insurance" dir="ltr" class="input input-bordered" />
                </div>
                <div class="form-control">
                    <label class="label"><span class="label-text font-bold">📊 وضعیت</span></label>
                    <select wire:model="status" class="select select-bordered">
                        <option value="pending">📝 ثبت سفارش</option>
                        <option value="final-check">🔍 چک نهایی</option>
                        <option value="courier">🚚 تحویل مامور</option>
                    </select>
                </div>
                <div class="form-control">
                    <label class="label"><span class="label-text font-bold">🌐 کانال</span></label>
                    <select wire:model="channelId" class="select select-bordered">
                        <option value="">— انتخاب —</option>
                        @foreach($channels as $channel)
                            <option value="{{ $channel->id }}">{{ $channel->icon }} {{ $channel->name }}</option>
                        @endforeach
                    </select>
                </div>
            </div>

            <div class="card-actions justify-end mt-6">
                <a href="{{ route('orders.index') }}" class="btn btn-ghost">انصراف</a>
                <button wire:click="save" class="btn btn-primary">✅ ثبت</button>
            </div>
        </div>
    </div>
</div>
""")

write_file("app/Livewire/Orders/Edit.php", r"""
<?php

namespace App\Livewire\Orders;

use App\Models\Channel;
use App\Models\Order;
use Livewire\Component;

class Edit extends Component
{
    public Order $order;
    public string $phone = '';
    public string $customerName = '';
    public string $postalCode = '';
    public string $address = '';
    public string $insurance = '0';
    public string $status = 'pending';
    public ?int $channelId = null;
    public string $notes = '';

    public function mount(Order $order): void
    {
        $this->order        = $order;
        $this->phone        = $order->phone ?? '';
        $this->customerName = $order->customer?->name ?? '';
        $this->postalCode   = $order->postal_code ?? '';
        $this->address      = $order->address ?? '';
        $this->insurance    = (string) ($order->insurance ?? 0);
        $this->status       = $order->status ?? 'pending';
        $this->channelId    = $order->channel_id;
        $this->notes        = $order->notes ?? '';
    }

    public function save()
    {
        $this->validate([
            'phone'        => 'required|min:10',
            'customerName' => 'nullable|string|max:255',
            'postalCode'   => 'nullable|string|max:20',
            'address'      => 'nullable|string',
            'insurance'    => 'nullable|numeric',
            'status'       => 'required|in:pending,final-check,courier',
            'channelId'    => 'nullable|exists:channels,id',
        ]);

        if ($this->order->customer) {
            $this->order->customer->update([
                'name'        => $this->customerName ?: $this->order->customer->name,
                'postal_code' => $this->postalCode,
                'address'     => $this->address,
            ]);
        }

        $this->order->update([
            'phone'       => $this->phone,
            'postal_code' => $this->postalCode,
            'address'     => $this->address,
            'insurance'   => (float) ($this->insurance ?: 0),
            'status'      => $this->status,
            'channel_id'  => $this->channelId,
            'notes'       => $this->notes,
        ]);

        session()->flash('success', 'ویرایش شد.');
        return redirect()->route('orders.show', $this->order);
    }

    public function render()
    {
        return view('livewire.orders.edit', [
            'channels' => Channel::where('is_active', true)->orderBy('sort_order')->get(),
        ])->layout('components.layouts.app');
    }
}
""")

write_file("resources/views/livewire/orders/edit.blade.php", r"""
<div class="p-6 max-w-3xl mx-auto">
    <div class="flex items-center gap-3 mb-6">
        <a href="{{ route('orders.show', $order) }}" class="btn btn-ghost btn-sm">→</a>
        <h1 class="text-2xl font-bold">✏️ ویرایش سفارش #{{ $order->order_number }}</h1>
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
                <input type="text" wire:model="customerName" class="input input-bordered" />
            </div>

            <div class="form-control">
                <label class="label"><span class="label-text font-bold">📮 کدپستی</span></label>
                <input type="text" wire:model="postalCode" dir="ltr" class="input input-bordered font-mono" />
            </div>

            <div class="form-control">
                <label class="label"><span class="label-text font-bold">📍 آدرس</span></label>
                <textarea wire:model="address" class="textarea textarea-bordered" rows="3"></textarea>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="form-control">
                    <label class="label"><span class="label-text font-bold">💰 بیمه</span></label>
                    <input type="number" wire:model="insurance" dir="ltr" class="input input-bordered" />
                </div>
                <div class="form-control">
                    <label class="label"><span class="label-text font-bold">📊 وضعیت</span></label>
                    <select wire:model="status" class="select select-bordered">
                        <option value="pending">📝 ثبت سفارش</option>
                        <option value="final-check">🔍 چک نهایی</option>
                        <option value="courier">🚚 تحویل مامور</option>
                    </select>
                </div>
                <div class="form-control">
                    <label class="label"><span class="label-text font-bold">🌐 کانال</span></label>
                    <select wire:model="channelId" class="select select-bordered">
                        <option value="">— انتخاب —</option>
                        @foreach($channels as $channel)
                            <option value="{{ $channel->id }}">{{ $channel->icon }} {{ $channel->name }}</option>
                        @endforeach
                    </select>
                </div>
            </div>

            <div class="form-control">
                <label class="label"><span class="label-text font-bold">📝 یادداشت</span></label>
                <textarea wire:model="notes" class="textarea textarea-bordered" rows="2"></textarea>
            </div>

            <div class="card-actions justify-end mt-6">
                <a href="{{ route('orders.show', $order) }}" class="btn btn-ghost">انصراف</a>
                <button wire:click="save" class="btn btn-primary">✅ ذخیره</button>
            </div>
        </div>
    </div>
</div>
""")

write_file("app/Livewire/Orders/PrintLabel.php", r"""
<?php

namespace App\Livewire\Orders;

use App\Models\Order;
use Livewire\Component;

class PrintLabel extends Component
{
    public Order $order;
    public function mount(Order $order): void { $this->order = $order->load('customer'); }
    public function render()
    {
        return view('livewire.orders.print-label')->layout('components.layouts.app');
    }
}
""")

write_file("resources/views/livewire/orders/print-label.blade.php", r"""
<div>
    <iframe style="position:fixed;inset:0;width:100%;height:100%;border:0;z-index:9999;"
        srcdoc="
        <!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><title>برچسب</title>
        <style>
            @page{size:100mm 65mm;margin:0}
            *{box-sizing:border-box;margin:0;padding:0;font-family:Tahoma,sans-serif}
            body{padding:3mm;background:#fff}
            .no-print{padding:10px;text-align:center;background:#f0f0f0;margin-bottom:8px}
            .no-print button{padding:8px 16px;background:#1a5276;color:#fff;border:none;border-radius:6px;cursor:pointer;margin:0 4px;font-family:inherit}
            .label{width:94mm;height:59mm;border:2px solid #000;padding:3mm;display:flex;flex-direction:column;background:#fff}
            .label-header{display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid #000;padding-bottom:2mm;margin-bottom:2mm}
            .customer-name{font-size:18px;font-weight:bold}
            .insurance-tag{background:#000;color:#fff;padding:2px 10px;border-radius:20px;font-size:13px;font-weight:bold}
            .addr-box{border:2px solid #000;border-radius:6px;padding:2mm;font-size:14px;line-height:1.5;font-weight:600;flex:1;overflow:hidden;margin-bottom:2mm}
            .contact-row{display:flex;gap:3mm;margin-bottom:2mm}
            .contact-tag{flex:1;display:flex;align-items:center;gap:4px}
            .contact-tag .lbl{background:#000;color:#fff;padding:2px 8px;border-radius:5px;font-size:11px;font-weight:bold}
            .contact-tag .val{flex:1;border:2px solid #000;border-radius:5px;padding:2px 8px;font-size:15px;font-weight:bold;font-family:monospace;text-align:center}
            .meta-row{display:flex;gap:5px;justify-content:space-between;font-size:11px}
            .meta-row span{background:#000;color:#fff;padding:2px 10px;border-radius:10px;font-weight:bold}
            @media print{.no-print{display:none!important}}
        </style></head><body>
        <div class='no-print'><button onclick='window.print()'>🖨️ چاپ</button><button onclick='history.back()' style='background:#eee;color:#333'>✕ بستن</button></div>
        <div class='label'>
            <div class='label-header'>
                <div class='customer-name'>{{ $order->customer?->name ?? 'مشتری' }}</div>
                @if($order->insurance > 0)<div class='insurance-tag'>بیمه: {{ number_format((float) $order->insurance) }}</div>@endif
            </div>
            <div class='addr-box'>{{ $order->address ?? '—' }}</div>
            <div class='contact-row'>
                <div class='contact-tag'><span class='lbl'>تلفن</span><span class='val'>{{ $order->phone ?? '—' }}</span></div>
                <div class='contact-tag'><span class='lbl'>کدپستی</span><span class='val'>{{ $order->postal_code ?? '—' }}</span></div>
            </div>
            <div class='meta-row'><span>#{{ $order->order_number }}</span><span>{{ $order->created_at?->format('Y/m/d') }}</span></div>
        </div></body></html>
        ">
    </iframe>
</div>
""")

write_file("app/Livewire/Orders/BulkPrintLabels.php", r"""
<?php

namespace App\Livewire\Orders;

use App\Models\Order;
use Livewire\Component;

class BulkPrintLabels extends Component
{
    public array $orders = [];

    public function mount(): void
    {
        $ids = request()->query('ids', '');
        $idArray = array_filter(explode(',', $ids));
        $this->orders = empty($idArray) ? [] : Order::with('customer')->whereIn('id', $idArray)->orderBy('id')->get()->all();
    }

    public function render()
    {
        return view('livewire.orders.bulk-print-labels')->layout('components.layouts.app');
    }
}
""")

write_file("resources/views/livewire/orders/bulk-print-labels.blade.php", r"""
<div>
    <iframe style="position:fixed;inset:0;width:100%;height:100%;border:0;z-index:9999;"
        srcdoc="
        <!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><title>چاپ برچسب‌ها</title>
        <style>
            @page{size:A4;margin:5mm}
            *{box-sizing:border-box;margin:0;padding:0;font-family:Tahoma,sans-serif}
            body{background:#f0f0f0;padding:10px}
            .no-print{padding:12px;text-align:center;background:#fff;margin-bottom:12px;border-radius:8px}
            .no-print button{padding:8px 16px;background:#1a5276;color:#fff;border:none;border-radius:6px;cursor:pointer;margin:0 4px;font-family:inherit}
            .labels-container{display:grid;grid-template-columns:repeat(2,100mm);gap:5mm;justify-content:center}
            .label{width:100mm;height:65mm;background:#fff;border:2px solid #000;padding:3mm;display:flex;flex-direction:column;page-break-inside:avoid;overflow:hidden}
            .label-header{display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid #000;padding-bottom:2mm;margin-bottom:2mm}
            .customer-name{font-size:18px;font-weight:bold;flex:1;overflow:hidden}
            .insurance-tag{background:#000;color:#fff;padding:2px 10px;border-radius:20px;font-size:13px;font-weight:bold}
            .addr-box{border:2px solid #000;border-radius:6px;padding:2mm;font-size:14px;line-height:1.5;font-weight:600;flex:1;overflow:hidden;margin-bottom:2mm}
            .contact-row{display:flex;gap:3mm;margin-bottom:2mm}
            .contact-tag{flex:1;display:flex;align-items:center;gap:4px}
            .contact-tag .lbl{background:#000;color:#fff;padding:2px 8px;border-radius:5px;font-size:11px;font-weight:bold}
            .contact-tag .val{flex:1;border:2px solid #000;border-radius:5px;padding:2px 8px;font-size:15px;font-weight:bold;font-family:monospace;text-align:center}
            .meta-row{display:flex;gap:5px;justify-content:space-between;font-size:11px}
            .meta-row span{background:#000;color:#fff;padding:2px 10px;border-radius:10px;font-weight:bold}
            @media print{body{background:#fff;padding:0}.no-print{display:none!important}}
        </style></head><body>
        <div class='no-print'><button onclick='window.print()'>🖨️ چاپ {{ count($orders) }} برچسب</button><button onclick='history.back()' style='background:#eee;color:#333'>✕ بستن</button></div>
        @if(empty($orders))<div style='text-align:center;padding:40px;color:#999'>سفارشی انتخاب نشده</div>
        @else
        <div class='labels-container'>
            @foreach($orders as $order)
            <div class='label'>
                <div class='label-header'>
                    <div class='customer-name'>{{ $order->customer?->name ?? 'مشتری' }}</div>
                    @if($order->insurance > 0)<div class='insurance-tag'>بیمه: {{ number_format((float) $order->insurance) }}</div>@endif
                </div>
                <div class='addr-box'>{{ $order->address ?? '—' }}</div>
                <div class='contact-row'>
                    <div class='contact-tag'><span class='lbl'>تلفن</span><span class='val'>{{ $order->phone ?? '—' }}</span></div>
                    <div class='contact-tag'><span class='lbl'>کدپستی</span><span class='val'>{{ $order->postal_code ?? '—' }}</span></div>
                </div>
                <div class='meta-row'><span>#{{ $order->order_number }}</span><span>{{ $order->created_at?->format('Y/m/d') }}</span></div>
            </div>
            @endforeach
        </div>
        @endif
        </body></html>
        ">
    </iframe>
</div>
""")

write_file("app/Livewire/Orders/CourierList.php", r"""
<?php

namespace App\Livewire\Orders;

use App\Models\Order;
use Livewire\Component;

class CourierList extends Component
{
    public function render()
    {
        $orders = Order::with('customer')->where('status', 'courier')->orderBy('created_at')->get();
        return view('livewire.orders.courier-list', compact('orders'))->layout('components.layouts.app');
    }
}
""")

write_file("resources/views/livewire/orders/courier-list.blade.php", r"""
<div>
    <iframe style="position:fixed;inset:0;width:100%;height:100%;border:0;z-index:9999;"
        srcdoc="
        <!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><title>لیست مامور</title>
        <style>
            @page{size:A4;margin:8mm}
            *{box-sizing:border-box;margin:0;padding:0;font-family:Tahoma,sans-serif}
            body{padding:12px}
            .no-print{padding:12px;text-align:center;margin-bottom:12px}
            .no-print button{padding:8px 16px;background:#1a5276;color:#fff;border:none;border-radius:6px;cursor:pointer;margin:0 4px;font-family:inherit}
            h1{text-align:center;color:#1a5276;font-size:16px;margin-bottom:6px}
            .subtitle{text-align:center;color:#666;font-size:11px;margin-bottom:10px;border-bottom:2px solid #1a5276;padding-bottom:8px}
            table{width:100%;border-collapse:collapse}
            thead th{background:#1a5276;color:#fff;padding:7px 5px;font-size:10.5px;border:1px solid #0d3b5e}
            tbody td{padding:6px 5px;border:1px solid #999;font-size:10.5px;text-align:right}
            tbody tr:nth-child(even){background:#f9f9f9}
            .center{text-align:center!important}.mono{font-family:monospace;direction:ltr}
            .sign{margin-top:40px;display:flex;justify-content:space-around;font-size:11px}
            .sign div{border-top:1px solid #333;padding-top:4px;min-width:150px;text-align:center}
            @media print{.no-print{display:none!important}}
        </style></head><body>
        <div class='no-print'><button onclick='window.print()'>🖨️ چاپ</button><button onclick='history.back()' style='background:#eee;color:#333'>✕ بستن</button></div>
        <h1>📦 لیست سفارشات تحویل به مامور</h1>
        <div class='subtitle'>ShopGun — {{ now()->format('Y/m/d H:i') }} — تعداد: {{ count($orders) }}</div>
        @if(empty($orders))<p style='text-align:center;padding:40px;color:#999'>سفارشی نیست</p>
        @else
        <table><thead><tr><th>ردیف</th><th>شماره</th><th>نام</th><th>تلفن</th><th>کدپستی</th><th>آدرس</th><th>بیمه</th></tr></thead>
        <tbody>
        @foreach($orders as $i => $o)
        <tr><td class='center'>{{ $i+1 }}</td><td class='center mono'>{{ $o->order_number }}</td><td>{{ $o->customer?->name }}</td><td class='center mono'>{{ $o->phone }}</td><td class='center mono'>{{ $o->postal_code }}</td><td style='font-size:10px'>{{ \Illuminate\Support\Str::limit($o->address, 80) }}</td><td class='center'>{{ number_format((float) $o->insurance) }}</td></tr>
        @endforeach
        </tbody></table>
        <div class='sign'><div>امضاء تحویل‌دهنده</div><div>امضاء مامور</div></div>
        @endif
        </body></html>
        ">
    </iframe>
</div>
""")

print()
print("═" * 60)
print("✅ مرحله ۲ (بخش ۲) — Orders کامل شد")
print("═" * 60)
print()
