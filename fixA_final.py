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
print("🔧 رفع مشکلات مرحله A")
print("═" * 60)
print()

# =========================================================
# ۱. روت‌های کامل با همه missing
# =========================================================

write_file("routes/web.php", r"""
<?php

use Illuminate\Support\Facades\Route;
use Illuminate\Support\Facades\Auth;
use App\Livewire\Auth\Login;
use App\Livewire\Dashboard;
use App\Livewire\ActivityLog;
use App\Livewire\Orders\Index as OrdersIndex;
use App\Livewire\Orders\Create as OrdersCreate;
use App\Livewire\Orders\Show as OrdersShow;
use App\Livewire\Orders\Edit as OrdersEdit;
use App\Livewire\Orders\PrintLabel as OrdersPrintLabel;
use App\Livewire\Orders\BulkPrintLabels as OrdersBulkPrintLabels;
use App\Livewire\Orders\CourierList as OrdersCourierList;
use App\Livewire\Customers\Index as CustomersIndex;
use App\Livewire\Customers\Create as CustomersCreate;
use App\Livewire\Customers\Show as CustomersShow;
use App\Livewire\Customers\Edit as CustomersEdit;
use App\Livewire\Certificates\Index as CertificatesIndex;
use App\Livewire\Reports\Index as ReportsIndex;
use App\Livewire\Settings\Index as SettingsIndex;

Route::get('/', fn () => redirect('/dashboard'));

Route::middleware('guest')->group(function () {
    Route::get('/login', Login::class)->name('login');
});

Route::middleware('auth')->group(function () {

    Route::post('/logout', function () {
        Auth::logout();
        request()->session()->invalidate();
        request()->session()->regenerateToken();
        return redirect('/login');
    })->name('logout');

    Route::get('/dashboard', Dashboard::class)->name('dashboard');
    Route::get('/activity-log', ActivityLog::class)->name('activity-log');

    Route::prefix('orders')->name('orders.')->group(function () {
        Route::get('/', OrdersIndex::class)->name('index');
        Route::get('/create', OrdersCreate::class)->name('create');
        Route::get('/import', fn () => view('pages.coming-soon', ['title' => 'وارد کردن سفارشات']))->name('import');
        Route::get('/courier-list', OrdersCourierList::class)->name('courier-list');
        Route::get('/bulk-print-labels', OrdersBulkPrintLabels::class)->name('bulk-print-labels');
        Route::get('/{order}/print-label', OrdersPrintLabel::class)->name('print-label');
        Route::get('/{order}/edit', OrdersEdit::class)->name('edit');
        Route::get('/{order}', OrdersShow::class)->name('show');
    });

    Route::prefix('customers')->name('customers.')->group(function () {
        Route::get('/', CustomersIndex::class)->name('index');
        Route::get('/create', CustomersCreate::class)->name('create');
        Route::get('/{customer}/edit', CustomersEdit::class)->name('edit');
        Route::get('/{customer}', CustomersShow::class)->name('show');
    });

    Route::prefix('certificates')->name('certificates.')->group(function () {
        Route::get('/', CertificatesIndex::class)->name('index');
    });

    Route::get('/reports', ReportsIndex::class)->name('reports.index');
    Route::get('/settings', SettingsIndex::class)->name('settings.index');
});
""")

write_file("resources/views/pages/coming-soon.blade.php", r"""
@extends('components.layouts.app')

@section('content')
<div class="p-6 text-center">
    <div class="text-6xl mb-4">🚧</div>
    <h1 class="text-2xl font-bold mb-2">{{ $title ?? 'این صفحه' }}</h1>
    <p class="text-base-content/60">به زودی فعال می‌شود</p>
    <a href="{{ url()->previous() }}" class="btn btn-primary btn-sm mt-6">→ بازگشت</a>
</div>
@endsection
""")

# =========================================================
# ۲. PhoneSearch کاملاً همگام با پدر
# =========================================================

write_file("app/Livewire/Components/PhoneSearch.php", r"""
<?php

namespace App\Livewire\Components;

use App\Models\Customer;
use App\Models\Order;
use Livewire\Attributes\Modelable;
use Livewire\Component;

class PhoneSearch extends Component
{
    #[Modelable]
    public string $value = '';

    public string $placeholder = '09151234567';
    public array $suggestions = [];
    public bool $showDropdown = false;

    public function updatedValue(): void
    {
        // ارسال فوری مقدار به پدر
        $this->dispatch('phone-typed', value: $this->value);
        $this->search();
    }

    public function search(): void
    {
        $raw    = (string) $this->value;
        $digits = preg_replace('/\D/', '', $raw);
        $norm   = $this->normalize($digits);

        if (strlen($norm) < 3) {
            $this->suggestions  = [];
            $this->showDropdown = false;
            return;
        }

        $map = [];

        // جستجو در سفارشات
        Order::query()
            ->with('customer')
            ->where(function ($q) use ($digits, $norm) {
                $q->where('phone', 'like', "%{$digits}%")
                  ->orWhere('phone', 'like', "%{$norm}%");
            })
            ->latest('id')
            ->limit(30)
            ->get()
            ->each(function ($o) use (&$map) {
                $p = $this->normalize((string) ($o->phone ?? ''));
                if (! $p) return;

                if (! isset($map[$p])) {
                    $map[$p] = [
                        'phone'   => $o->phone,
                        'norm'    => $p,
                        'name'    => $o->customer?->name ?? '',
                        'address' => $o->address ?? '',
                        'postal'  => $o->postal_code ?? '',
                        'count'   => 0,
                        'ts'      => 0,
                    ];
                }
                $map[$p]['count']++;
                $ts = $o->created_at?->getTimestamp() ?? 0;
                if ($ts > $map[$p]['ts']) {
                    $map[$p]['name']    = $o->customer?->name ?? $map[$p]['name'];
                    $map[$p]['address'] = $o->address ?? $map[$p]['address'];
                    $map[$p]['postal']  = $o->postal_code ?? $map[$p]['postal'];
                    $map[$p]['ts']      = $ts;
                }
            });

        // جستجو در مشتریان
        Customer::query()
            ->where(function ($q) use ($digits, $norm) {
                $q->where('phone', 'like', "%{$digits}%")
                  ->orWhere('phone', 'like', "%{$norm}%");
            })
            ->limit(30)
            ->get()
            ->each(function ($c) use (&$map) {
                $p = $this->normalize((string) ($c->phone ?? ''));
                if (! $p) return;

                if (! isset($map[$p])) {
                    $map[$p] = [
                        'phone'   => $c->phone,
                        'norm'    => $p,
                        'name'    => $c->name ?? '',
                        'address' => $c->address ?? '',
                        'postal'  => $c->postal_code ?? '',
                        'count'   => 0,
                        'ts'      => 0,
                    ];
                } else {
                    if (! $map[$p]['name'] && $c->name)         $map[$p]['name']    = $c->name;
                    if (! $map[$p]['address'] && $c->address)   $map[$p]['address'] = $c->address;
                    if (! $map[$p]['postal'] && $c->postal_code) $map[$p]['postal']  = $c->postal_code;
                }
            });

        $list = array_values($map);
        usort($list, function ($a, $b) use ($norm) {
            $aExact = ($a['norm'] === $norm) ? 1 : 0;
            $bExact = ($b['norm'] === $norm) ? 1 : 0;
            if ($aExact !== $bExact) return $bExact - $aExact;
            return ($b['count'] ?? 0) - ($a['count'] ?? 0);
        });

        $this->suggestions  = array_slice($list, 0, 10);
        $this->showDropdown = ! empty($this->suggestions);
    }

    public function select(string $phone, string $name, string $address, string $postal): void
    {
        $this->value = $phone;
        $this->showDropdown = false;
        $this->suggestions  = [];

        $this->dispatch('phone-selected', [
            'phone'   => $phone,
            'name'    => $name,
            'address' => $address,
            'postal'  => $postal,
        ]);
    }

    protected function normalize(string $phone): string
    {
        $digits = preg_replace('/\D/', '', $phone);
        if (str_starts_with($digits, '0098')) {
            $digits = substr($digits, 4);
        } elseif (str_starts_with($digits, '98') && strlen($digits) > 10) {
            $digits = substr($digits, 2);
        }
        if (str_starts_with($digits, '0') && strlen($digits) > 10) {
            $digits = substr($digits, 1);
        }
        return $digits;
    }

    public function render()
    {
        return view('livewire.components.phone-search');
    }
}
""")

write_file("resources/views/livewire/components/phone-search.blade.php", r"""
<div class="relative">
    <input
        type="text"
        wire:model.live.debounce.400ms="value"
        dir="ltr"
        inputmode="tel"
        placeholder="{{ $placeholder }}"
        class="input input-bordered font-mono w-full text-base"
        autocomplete="off" />

    @if($showDropdown && count($suggestions) > 0)
        <div class="absolute top-full right-0 left-0 mt-1 bg-base-100 border-2 border-primary rounded-lg shadow-xl z-[60] max-h-80 overflow-y-auto">
            @foreach($suggestions as $s)
                <button
                    type="button"
                    wire:click="select(@js($s['phone']), @js($s['name']), @js($s['address']), @js($s['postal']))"
                    class="w-full text-right p-3 hover:bg-base-200 border-b border-base-200 last:border-0 transition">
                    <div class="flex justify-between items-center gap-2">
                        <div class="flex-1 min-w-0">
                            <div class="font-bold text-sm text-primary truncate">
                                {{ $s['name'] ?: '—' }}
                            </div>
                            <div class="font-mono text-xs text-base-content/60 mt-0.5" dir="ltr">
                                {{ $s['phone'] }}
                            </div>
                        </div>
                        <div class="badge badge-warning badge-sm whitespace-nowrap">
                            {{ $s['count'] }} سفارش
                        </div>
                    </div>
                </button>
            @endforeach
        </div>
    @endif
</div>
""")

# =========================================================
# ۳. Create سفارش — با listener درست و Sync کامل
# =========================================================

write_file("app/Livewire/Orders/Create.php", r"""
<?php

namespace App\Livewire\Orders;

use App\Models\Channel;
use App\Models\Customer;
use App\Models\Order;
use Livewire\Attributes\On;
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
    public bool $invoiceNeeded = false;
    public string $notes = '';

    /** @var array<int, array{title:string,sku:string,price:string,qty:int,cert:bool}> */
    public array $items = [];

    public bool $customerFound = false;
    public ?int $existingCustomerId = null;

    public function mount(): void
    {
        $this->addItem();
    }

    public function addItem(): void
    {
        $this->items[] = [
            'title' => '',
            'sku'   => '',
            'price' => '',
            'qty'   => 1,
            'cert'  => true,
        ];
    }

    public function removeItem(int $index): void
    {
        if (isset($this->items[$index])) {
            unset($this->items[$index]);
            $this->items = array_values($this->items);
        }
        $this->recalcInsurance();
    }

    /** وقتی کاربر تلفن رو تایپ کرد، فقط شماره رو همگام کن */
    #[On('phone-typed')]
    public function onPhoneTyped(string $value): void
    {
        $this->phone = $value;
        $this->checkCustomer();
    }

    /** وقتی کاربر از لیست پیشنهادها انتخاب کرد، همه‌چیز رو پر کن */
    #[On('phone-selected')]
    public function onPhoneSelected(string $phone, string $name = '', string $address = '', string $postal = ''): void
    {
        $this->phone        = $phone;
        $this->customerName = $name;
        $this->address      = $address;
        $this->postalCode   = $postal;
        $this->checkCustomer();
    }

    /** انتخاب محصول از SkuSearch */
    #[On('sku-selected')]
    public function onSkuSelected(string $sku, string $title = '', float $price = 0): void
    {
        // دنبال ردیف خالی بگرد
        foreach (array_reverse(array_keys($this->items)) as $idx) {
            if (empty($this->items[$idx]['sku'])) {
                $this->items[$idx]['sku']   = $sku;
                $this->items[$idx]['title'] = $title;
                $this->items[$idx]['price'] = (string) $price;
                $this->recalcInsurance();
                return;
            }
        }

        $this->items[] = [
            'title' => $title,
            'sku'   => $sku,
            'price' => (string) $price,
            'qty'   => 1,
            'cert'  => true,
        ];
        $this->recalcInsurance();
    }

    public function checkCustomer(): void
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
            if (! $this->customerName) $this->customerName = $customer->name ?? '';
            if (! $this->postalCode)   $this->postalCode   = $customer->postal_code ?? '';
            if (! $this->address)      $this->address      = $customer->address ?? '';
        } else {
            $this->customerFound = false;
            $this->existingCustomerId = null;
        }
    }

    public function updatedItems(): void
    {
        $this->recalcInsurance();
    }

    public function recalcInsurance(): void
    {
        $total = 0;
        foreach ($this->items as $it) {
            $total += ((float) ($it['price'] ?? 0)) * ((int) ($it['qty'] ?? 1));
        }
        $this->insurance = (string) round($total / 100000);
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
        ], [
            'phone.required' => 'شماره تلفن الزامی است.',
            'phone.min'      => 'شماره تلفن حداقل ۱۰ رقم.',
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

        $amount = 0;
        foreach ($this->items as $it) {
            $amount += ((float) ($it['price'] ?? 0)) * ((int) ($it['qty'] ?? 1));
        }

        $order = Order::create([
            'order_number'   => (string) $newNumber,
            'customer_id'    => $customer->id,
            'channel_id'     => $this->channelId,
            'status'         => $this->status,
            'amount'         => $amount,
            'insurance'      => (float) ($this->insurance ?: 0),
            'phone'          => $normalized,
            'address'        => $this->address,
            'postal_code'    => $this->postalCode,
            'notes'          => $this->notes,
            'invoice_needed' => $this->invoiceNeeded,
        ]);

        foreach ($this->items as $i => $it) {
            if (empty($it['title']) && empty($it['sku'])) continue;
            $order->items()->create([
                'title'       => $it['title'] ?: 'محصول',
                'sku'         => $it['sku'] ?? '',
                'price'       => (float) ($it['price'] ?? 0),
                'quantity'    => (int) ($it['qty'] ?? 1),
                'cert_needed' => (bool) ($it['cert'] ?? true),
                'sort_order'  => $i,
            ]);
        }

        session()->flash('success', "سفارش #{$newNumber} با موفقیت ثبت شد.");

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

# =========================================================
# ۴. ویو Create — فرم بازنویسی شده
# =========================================================

write_file("resources/views/livewire/orders/create.blade.php", r"""
<div class="p-4 md:p-6 max-w-4xl mx-auto">
    <div class="flex items-center gap-3 mb-6">
        <a href="{{ route('orders.index') }}" class="btn btn-ghost btn-sm">→</a>
        <h1 class="text-xl md:text-2xl font-bold">➕ سفارش جدید</h1>
    </div>

    <div class="card bg-base-100 shadow">
        <div class="card-body gap-5">

            {{-- تلفن --}}
            <div class="form-control">
                <label class="label pb-1">
                    <span class="label-text font-bold">📱 تلفن مشتری <span class="text-error">*</span></span>
                </label>
                <livewire:components.phone-search wire:model="phone" wire:key="phone-search-create" />
                @if($customerFound)
                    <label class="label pt-1">
                        <span class="label-text-alt text-success font-bold">
                            ✅ مشتری موجود — ID: {{ $existingCustomerId }}
                        </span>
                    </label>
                @elseif(strlen(preg_replace('/\D/', '', $phone)) >= 10)
                    <label class="label pt-1">
                        <span class="label-text-alt text-info font-bold">🆕 مشتری جدید ساخته می‌شود</span>
                    </label>
                @endif
                @error('phone')
                    <label class="label pt-1"><span class="label-text-alt text-error">{{ $message }}</span></label>
                @enderror
            </div>

            {{-- نام و کدپستی --}}
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="form-control">
                    <label class="label pb-1"><span class="label-text font-bold">👤 نام مشتری</span></label>
                    <input type="text" wire:model="customerName" class="input input-bordered w-full" />
                </div>
                <div class="form-control">
                    <label class="label pb-1"><span class="label-text font-bold">📮 کدپستی</span></label>
                    <input type="text" wire:model="postalCode" dir="ltr" class="input input-bordered font-mono w-full" />
                </div>
            </div>

            {{-- آدرس --}}
            <div class="form-control">
                <label class="label pb-1"><span class="label-text font-bold">📍 آدرس</span></label>
                <textarea wire:model="address" class="textarea textarea-bordered w-full" rows="2"></textarea>
            </div>

            {{-- وضعیت و کانال --}}
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="form-control">
                    <label class="label pb-1"><span class="label-text font-bold">📊 وضعیت</span></label>
                    <div class="flex flex-wrap gap-2">
                        @foreach(['pending' => '📝 ثبت', 'final-check' => '🔍 چک', 'courier' => '🚚 تحویل'] as $k => $v)
                            <button type="button" wire:click="$set('status', '{{ $k }}')"
                                    class="btn btn-sm {{ $status === $k ? 'btn-primary' : 'btn-outline' }}">
                                {{ $v }}
                            </button>
                        @endforeach
                    </div>
                </div>

                <div class="form-control">
                    <label class="label pb-1"><span class="label-text font-bold">🌐 کانال</span></label>
                    <div class="flex flex-wrap gap-2">
                        @foreach($channels as $c)
                            <button type="button" wire:click="$set('channelId', {{ $c->id }})"
                                    class="btn btn-sm {{ $channelId === $c->id ? 'btn-primary' : 'btn-outline' }}">
                                {{ $c->icon }} {{ $c->name }}
                            </button>
                        @endforeach
                    </div>
                </div>
            </div>

            {{-- بیمه و فاکتور --}}
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4 items-end">
                <div class="form-control">
                    <label class="label pb-1"><span class="label-text font-bold">💰 بیمه</span></label>
                    <input type="text" wire:model="insurance" dir="ltr" class="input input-bordered font-mono w-full" />
                </div>
                <label class="label cursor-pointer justify-start gap-3 pb-3">
                    <input type="checkbox" wire:model="invoiceNeeded" class="checkbox checkbox-primary" />
                    <span class="label-text font-bold">📄 نیاز به فاکتور</span>
                </label>
            </div>

            {{-- محصولات --}}
            <div class="divider my-1">
                <span class="text-sm font-bold">🛍️ محصولات</span>
            </div>

            <div class="space-y-3">
                @foreach($items as $idx => $it)
                    <div class="border-2 border-base-300 rounded-xl p-3 bg-base-200/50"
                         wire:key="item-{{ $idx }}">

                        {{-- ردیف اول: SKU + عنوان --}}
                        <div class="grid grid-cols-1 md:grid-cols-2 gap-3 mb-3">
                            <div class="form-control">
                                <label class="label py-1">
                                    <span class="label-text text-xs font-bold">SKU</span>
                                </label>
                                <input type="text" wire:model="items.{{ $idx }}.sku"
                                       dir="ltr" class="input input-bordered input-sm font-mono w-full" />
                            </div>
                            <div class="form-control">
                                <label class="label py-1">
                                    <span class="label-text text-xs font-bold">عنوان</span>
                                </label>
                                <input type="text" wire:model="items.{{ $idx }}.title"
                                       class="input input-bordered input-sm w-full" />
                            </div>
                        </div>

                        {{-- ردیف دوم: قیمت + تعداد + شناسنامه + حذف --}}
                        <div class="grid grid-cols-12 gap-2 items-end">
                            <div class="col-span-6 md:col-span-4">
                                <label class="label py-1">
                                    <span class="label-text text-xs font-bold">قیمت (تومان)</span>
                                </label>
                                <input type="number" wire:model.live.debounce.500ms="items.{{ $idx }}.price"
                                       dir="ltr" class="input input-bordered input-sm font-mono w-full" />
                            </div>
                            <div class="col-span-3 md:col-span-2">
                                <label class="label py-1">
                                    <span class="label-text text-xs font-bold">تعداد</span>
                                </label>
                                <input type="number" wire:model.live="items.{{ $idx }}.qty" min="1"
                                       dir="ltr" class="input input-bordered input-sm w-full text-center" />
                            </div>
                            <div class="col-span-3 md:col-span-3 flex flex-col items-center">
                                <label class="label py-1">
                                    <span class="label-text text-xs font-bold">شناسنامه</span>
                                </label>
                                <input type="checkbox" wire:model="items.{{ $idx }}.cert"
                                       class="checkbox checkbox-sm checkbox-primary" />
                            </div>
                            <div class="col-span-12 md:col-span-3 flex justify-end">
                                <button type="button" wire:click="removeItem({{ $idx }})"
                                        wire:confirm="این ردیف حذف شود؟"
                                        class="btn btn-error btn-sm w-full md:w-auto">
                                    🗑️ حذف
                                </button>
                            </div>
                        </div>
                    </div>
                @endforeach
            </div>

            <button type="button" wire:click="addItem"
                    class="btn btn-outline btn-sm w-full md:w-auto">
                ➕ افزودن محصول
            </button>

            {{-- یادداشت --}}
            <div class="form-control">
                <label class="label pb-1"><span class="label-text font-bold">📝 یادداشت</span></label>
                <textarea wire:model="notes" class="textarea textarea-bordered w-full" rows="2"></textarea>
            </div>

            {{-- دکمه‌ها --}}
            <div class="flex flex-col-reverse md:flex-row justify-end gap-2 mt-2">
                <a href="{{ route('orders.index') }}" class="btn btn-ghost w-full md:w-auto">انصراف</a>
                <button wire:click="save" wire:loading.attr="disabled" class="btn btn-primary w-full md:w-auto">
                    <span wire:loading.remove wire:target="save">✅ ثبت سفارش</span>
                    <span wire:loading wire:target="save">⏳ در حال ذخیره...</span>
                </button>
            </div>
        </div>
    </div>
</div>
""")

# =========================================================
# ۵. CSS برای جداول responsive و موبایل
# =========================================================

write_file("resources/css/app.css", r"""
@import url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css');

@import 'tailwindcss';

@plugin "daisyui" {
    themes: light --default, dark --prefersdark;
}

@source '../../vendor/laravel/framework/src/Illuminate/Pagination/resources/views/*.blade.php';
@source '../../storage/framework/views/*.php';
@source '../../vendor/robsontenorio/mary/src/View/Components/**/*.php';
@source '../**/*.blade.php';
@source '../**/*.js';

@theme {
    --font-sans: 'Vazirmatn', ui-sans-serif, system-ui, sans-serif;
}

/* =========================================================
   جدول‌های ریسپانسیو
   ========================================================= */

.table-wrap {
    width: 100%;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
}

.table-wrap table {
    min-width: 800px;
    width: 100%;
}

.table-wrap td,
.table-wrap th {
    white-space: nowrap;
    vertical-align: middle;
}

/* ستون‌هایی که باید متن آزاد داشته باشن */
.table-wrap td.col-address {
    white-space: normal;
    min-width: 200px;
    max-width: 300px;
    word-break: break-word;
}

.table-wrap td.col-products {
    white-space: normal;
    min-width: 250px;
    max-width: 350px;
    word-break: break-word;
}

/* موبایل: جدول تبدیل به کارت */
@media (max-width: 768px) {
    .table-wrap table.mobile-cards {
        min-width: auto;
    }

    .table-wrap table.mobile-cards thead {
        display: none;
    }

    .table-wrap table.mobile-cards tbody,
    .table-wrap table.mobile-cards tr,
    .table-wrap table.mobile-cards td {
        display: block;
        width: 100%;
    }

    .table-wrap table.mobile-cards tr {
        border: 1px solid oklch(var(--b3));
        border-radius: 0.75rem;
        margin-bottom: 0.75rem;
        padding: 0.75rem;
        background: oklch(var(--b1));
    }

    .table-wrap table.mobile-cards td {
        padding: 0.4rem 0.25rem;
        border: none;
        white-space: normal;
        display: flex;
        justify-content: space-between;
        align-items: center;
        gap: 1rem;
        font-size: 0.85rem;
    }

    .table-wrap table.mobile-cards td::before {
        content: attr(data-label);
        font-weight: 700;
        color: oklch(var(--bc) / 0.6);
        flex-shrink: 0;
        font-size: 0.75rem;
    }

    .table-wrap table.mobile-cards td:empty {
        display: none;
    }

    /* دکمه‌های عملیات */
    .table-wrap table.mobile-cards td.td-actions {
        padding-top: 0.75rem;
        border-top: 1px solid oklch(var(--b3));
        margin-top: 0.5rem;
    }
}

/* اسکرول افقی بهتر */
.table-wrap::-webkit-scrollbar {
    height: 6px;
}

.table-wrap::-webkit-scrollbar-thumb {
    background: oklch(var(--bc) / 0.2);
    border-radius: 3px;
}

/* اندازه‌های ریسپانسیو */
@media (max-width: 640px) {
    .card-body {
        padding: 1rem !important;
    }

    .stat-card-value {
        font-size: 1.5rem !important;
    }
}
""")

print()
print("═" * 60)
print("✅ همه اصلاحات انجام شد")
print("═" * 60)
print()
print("📌 اجرا کن:")
print("   php artisan optimize:clear")
print("   npm run build")
print("   php artisan serve --host=0.0.0.0 --port=8000")
print()
