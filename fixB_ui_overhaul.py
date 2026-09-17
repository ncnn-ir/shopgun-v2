from pathlib import Path
import textwrap

PROJECT = Path.home() / "projects" / "shopgun-v2.1"

if not PROJECT.exists():
    raise SystemExit(f"❌ پروژه پیدا نشد")

def write_file(relative_path, content):
    path = PROJECT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    existed = path.exists()
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    action = "🔁" if existed else "✅"
    print(f"{action} {relative_path}")

print("═" * 60)
print("🎨 بازطراحی UI — جداول، کارت‌ها، شناسنامه")
print("═" * 60)
print()

# =========================================================
# ۱. CSS کامل — رنگ‌های جدید + جدول + کارت
# =========================================================

write_file("resources/css/app.css", r"""
@import url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css');
@import 'tailwindcss';

@plugin "daisyui" {
    themes: light --default;
}

@source '../../vendor/laravel/framework/src/Illuminate/Pagination/resources/views/*.blade.php';
@source '../../storage/framework/views/*.php';
@source '../**/*.blade.php';
@source '../**/*.js';

@theme {
    --font-sans: 'Vazirmatn', ui-sans-serif, system-ui, sans-serif;

    /* رنگ سازمانی جدید */
    --color-brand-50:  #f0f9ff;
    --color-brand-100: #e0f2fe;
    --color-brand-200: #bae6fd;
    --color-brand-300: #7dd3fc;
    --color-brand-400: #38bdf8;
    --color-brand-500: #0ea5e9;
    --color-brand-600: #0284c7;
    --color-brand-700: #0369a1;
    --color-brand-800: #075985;
    --color-brand-900: #0c4a6e;
}

/* =========================================================
   جدول حرفه‌ای
   ========================================================= */

.pro-table-wrap {
    width: 100%;
    overflow-x: auto;
    overflow-y: visible;
    -webkit-overflow-scrolling: touch;
    border-radius: 0.5rem;
    scrollbar-width: thin;
}

.pro-table-wrap::-webkit-scrollbar {
    height: 8px;
}

.pro-table-wrap::-webkit-scrollbar-track {
    background: transparent;
}

.pro-table-wrap::-webkit-scrollbar-thumb {
    background: rgba(100, 116, 139, 0.35);
    border-radius: 4px;
}

.pro-table-wrap::-webkit-scrollbar-thumb:hover {
    background: rgba(100, 116, 139, 0.55);
}

.pro-table {
    width: max-content;
    min-width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    font-size: 0.8125rem;
}

.pro-table thead th {
    position: sticky;
    top: 0;
    z-index: 10;
    background: #f8fafc;
    border-bottom: 2px solid #cbd5e1;
    padding: 0.5rem 0.75rem;
    font-weight: 700;
    font-size: 0.75rem;
    color: #334155;
    text-align: right;
    white-space: nowrap;
    user-select: none;
}

.pro-table thead th.sortable {
    cursor: pointer;
    transition: background 0.15s;
}

.pro-table thead th.sortable:hover {
    background: #e2e8f0;
}

.pro-table thead th .th-inner {
    display: flex;
    align-items: center;
    gap: 0.35rem;
    justify-content: flex-start;
}

.pro-table thead th .sort-icon {
    opacity: 0.3;
    font-size: 0.65rem;
    transition: opacity 0.15s;
}

.pro-table thead th.sortable:hover .sort-icon {
    opacity: 0.7;
}

.pro-table thead th.sort-active .sort-icon {
    opacity: 1;
    color: #0284c7;
}

.pro-table thead th .filter-btn {
    margin-right: auto;
    padding: 2px 5px;
    border-radius: 4px;
    background: transparent;
    border: none;
    cursor: pointer;
    font-size: 0.7rem;
    color: #64748b;
    transition: all 0.15s;
}

.pro-table thead th .filter-btn:hover,
.pro-table thead th .filter-btn.active {
    background: #0ea5e9;
    color: #fff;
}

.pro-table tbody td {
    padding: 0.55rem 0.75rem;
    border-bottom: 1px solid #e2e8f0;
    white-space: nowrap;
    vertical-align: middle;
    background: #fff;
    color: #1e293b;
}

.pro-table tbody tr:hover td {
    background: #f0f9ff;
}

.pro-table tbody tr.selected td {
    background: #e0f2fe;
}

.pro-table tbody td.cell-actions {
    position: sticky;
    left: 0;
    z-index: 5;
    background: #fff;
    border-left: 1px solid #e2e8f0;
}

.pro-table tbody tr:hover td.cell-actions {
    background: #f0f9ff;
}

.pro-table tbody td .badge-status {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    padding: 0.2rem 0.6rem;
    border-radius: 9999px;
    font-size: 0.7rem;
    font-weight: 700;
    color: #fff;
    white-space: nowrap;
}

.badge-status.pending     { background: linear-gradient(135deg, #f59e0b, #d97706); }
.badge-status.final-check { background: linear-gradient(135deg, #0ea5e9, #0284c7); }
.badge-status.courier     { background: linear-gradient(135deg, #10b981, #059669); }

/* =========================================================
   کارت آماری مینیمال
   ========================================================= */

.stat-strip {
    display: flex;
    gap: 0.75rem;
    overflow-x: auto;
    padding: 0.25rem 0.25rem 0.75rem;
    scrollbar-width: thin;
    scroll-snap-type: x mandatory;
}

.stat-strip::-webkit-scrollbar {
    height: 6px;
}

.stat-strip::-webkit-scrollbar-thumb {
    background: rgba(100, 116, 139, 0.25);
    border-radius: 3px;
}

.stat-card-mini {
    flex: 0 0 220px;
    scroll-snap-align: start;
    background: #fff;
    border: 1px solid #e2e8f0;
    border-radius: 0.75rem;
    padding: 0.85rem 1rem;
    box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    transition: all 0.15s;
}

.stat-card-mini:hover {
    box-shadow: 0 4px 12px rgba(15, 23, 42, 0.08);
    transform: translateY(-1px);
}

.stat-card-mini .stat-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.4rem;
}

.stat-card-mini .stat-icon {
    width: 32px;
    height: 32px;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 1rem;
}

.stat-card-mini .stat-label {
    font-size: 0.7rem;
    font-weight: 600;
    color: #64748b;
    letter-spacing: 0.02em;
}

.stat-card-mini .stat-value {
    font-size: 1.4rem;
    font-weight: 800;
    color: #0f172a;
    line-height: 1.2;
    font-variant-numeric: tabular-nums;
}

.stat-card-mini .stat-delta {
    display: inline-flex;
    align-items: center;
    gap: 0.25rem;
    margin-top: 0.4rem;
    padding: 0.15rem 0.5rem;
    border-radius: 9999px;
    font-size: 0.65rem;
    font-weight: 700;
}

.stat-card-mini .stat-delta.up   { background: #dcfce7; color: #15803d; }
.stat-card-mini .stat-delta.down { background: #fee2e2; color: #b91c1c; }
.stat-card-mini .stat-delta.flat { background: #f1f5f9; color: #475569; }

/* رنگ آیکون‌ها */
.ic-blue   { background: #dbeafe; color: #1d4ed8; }
.ic-green  { background: #dcfce7; color: #15803d; }
.ic-amber  { background: #fef3c7; color: #b45309; }
.ic-rose   { background: #ffe4e6; color: #be123c; }
.ic-indigo { background: #e0e7ff; color: #4338ca; }
.ic-sky    { background: #e0f2fe; color: #0369a1; }
.ic-violet { background: #ede9fe; color: #6d28d9; }

/* =========================================================
   موبایل
   ========================================================= */

@media (max-width: 768px) {
    .card-body { padding: 1rem !important; }
    .stat-card-mini { flex: 0 0 180px; padding: 0.7rem 0.85rem; }
    .stat-card-mini .stat-value { font-size: 1.2rem; }
    .pro-table { font-size: 0.75rem; }
    .pro-table thead th,
    .pro-table tbody td { padding: 0.45rem 0.6rem; }
}
""")

# =========================================================
# ۲. فرم کامل ایجاد شناسنامه (مطابق فایل اصلی)
# =========================================================

write_file("app/Livewire/Certificates/Create.php", r"""
<?php

namespace App\Livewire\Certificates;

use App\Models\Certificate;
use App\Models\Customer;
use App\Models\Order;
use Livewire\Component;
use Livewire\WithFileUploads;

class Create extends Component
{
    use WithFileUploads;

    public int $step = 1;

    // سنگ و فلز
    public string $stoneName   = '';
    public string $stoneEn     = '';
    public string $stoneOrigin = 'نیشابور';
    public string $stoneFlag   = 'ir';
    public string $stoneIcon   = '💠';
    public string $metal       = 'نقره 925';
    public string $metalEn     = 'Silver 925';
    public string $metalCarat  = '925';

    // مشخصات
    public string $length    = '';
    public string $width     = '';
    public string $weight    = '';
    public string $brilliant = '0';

    // ارتباط
    public ?int $customerId = null;
    public ?int $orderId    = null;

    // تصویر
    public $image = null;

    // سنگ‌های پیش‌فرض
    public array $stoneOptions = [
        ['name' => 'فیروزه عجمی',   'en' => 'Turquoise Ajami',   'origin' => 'نیشابور',   'flag' => 'ir', 'icon' => '💠'],
        ['name' => 'فیروزه شجری',   'en' => 'Turquoise Shajari', 'origin' => 'نیشابور',   'flag' => 'ir', 'icon' => '💠'],
        ['name' => 'عقیق یمانی',    'en' => 'Yemeni Agate',      'origin' => 'یمن',        'flag' => 'ye', 'icon' => '🔴'],
        ['name' => 'عقیق سلیمانی',  'en' => 'Solomoni Agate',    'origin' => 'یمن',        'flag' => 'ye', 'icon' => '❤️'],
        ['name' => 'عقیق شجر',      'en' => 'Dendritic Agate',   'origin' => 'یمن',        'flag' => 'ye', 'icon' => '🌿'],
        ['name' => 'در نجف',        'en' => 'Najaf Pearl',       'origin' => 'عراق',       'flag' => 'iq', 'icon' => '⚪'],
        ['name' => 'الماس',         'en' => 'Diamond',           'origin' => 'آفریقا',     'flag' => 'za', 'icon' => '💎'],
        ['name' => 'یاقوت سرخ',     'en' => 'Ruby',              'origin' => 'میانمار',    'flag' => 'mm', 'icon' => '❤️'],
        ['name' => 'یاقوت کبود',    'en' => 'Blue Sapphire',     'origin' => 'سری‌لانکا',  'flag' => 'lk', 'icon' => '🔵'],
        ['name' => 'زمرد',          'en' => 'Emerald',           'origin' => 'کلمبیا',     'flag' => 'co', 'icon' => '🟢'],
        ['name' => 'توپاز',         'en' => 'Topaz',             'origin' => 'برزیل',      'flag' => 'br', 'icon' => '💛'],
        ['name' => 'آمیتیست',       'en' => 'Amethyst',          'origin' => 'برزیل',      'flag' => 'br', 'icon' => '🟣'],
    ];

    public array $metalOptions = [
        ['name' => 'نقره 925',      'en' => 'Silver 925',      'carat' => '925'],
        ['name' => 'نقره 999',      'en' => 'Fine Silver',     'carat' => '999'],
        ['name' => 'طلا 18K',       'en' => 'Gold 18K',        'carat' => '750'],
        ['name' => 'طلا 21K',       'en' => 'Gold 21K',        'carat' => '875'],
        ['name' => 'طلا 22K',       'en' => 'Gold 22K',        'carat' => '916'],
        ['name' => 'طلا 24K',       'en' => 'Gold 24K',        'carat' => '999'],
        ['name' => 'پلاتین 950',    'en' => 'Platinum 950',    'carat' => '950'],
        ['name' => 'استیل',         'en' => 'Stainless Steel', 'carat' => '-'],
    ];

    public function selectStone(int $index): void
    {
        $s = $this->stoneOptions[$index] ?? null;
        if (! $s) return;

        $this->stoneName   = $s['name'];
        $this->stoneEn     = $s['en'];
        $this->stoneOrigin = $s['origin'];
        $this->stoneFlag   = $s['flag'];
        $this->stoneIcon   = $s['icon'];
    }

    public function selectMetal(int $index): void
    {
        $m = $this->metalOptions[$index] ?? null;
        if (! $m) return;

        $this->metal      = $m['name'];
        $this->metalEn    = $m['en'];
        $this->metalCarat = $m['carat'];
    }

    public function nextStep(): void
    {
        if ($this->step === 1) {
            $this->validate([
                'stoneName' => 'required|string',
                'metal'     => 'required|string',
            ], [
                'stoneName.required' => 'سنگ را انتخاب کن',
                'metal.required'     => 'فلز را انتخاب کن',
            ]);
        }

        if ($this->step === 2) {
            $this->validate([
                'length' => 'required|numeric|min:0',
                'width'  => 'required|numeric|min:0',
                'weight' => 'required|numeric|min:0',
            ], [
                'length.required' => 'طول الزامی است',
                'width.required'  => 'عرض الزامی است',
                'weight.required' => 'وزن الزامی است',
            ]);
        }

        $this->step = min(3, $this->step + 1);
    }

    public function prevStep(): void
    {
        $this->step = max(1, $this->step - 1);
    }

    public function save()
    {
        $this->validate([
            'stoneName' => 'required|string|max:255',
            'metal'     => 'required|string|max:255',
            'length'    => 'nullable|numeric|min:0',
            'width'     => 'nullable|numeric|min:0',
            'weight'    => 'nullable|numeric|min:0',
            'image'     => 'nullable|image|max:5120',
        ]);

        $code   = Certificate::generateCode();
        $serial = Certificate::generateSerial($code, $this->stoneEn ?: $this->stoneName);

        $imagePath = null;
        if ($this->image) {
            $imagePath = $this->image->store('certificates', 'public');
        }

        $cert = Certificate::create([
            'code'         => $code,
            'serial'       => $serial,
            'stone_name'   => $this->stoneName,
            'stone_en'     => $this->stoneEn,
            'stone_origin' => $this->stoneOrigin,
            'stone_flag'   => $this->stoneFlag,
            'metal'        => $this->metal,
            'metal_en'     => $this->metalEn,
            'metal_carat'  => $this->metalCarat,
            'length'       => (float) ($this->length ?: 0),
            'width'        => (float) ($this->width ?: 0),
            'weight'       => (float) ($this->weight ?: 0),
            'brilliant'    => (int) ($this->brilliant ?: 0),
            'image_path'   => $imagePath,
            'customer_id'  => $this->customerId,
            'order_id'     => $this->orderId,
            'issued_at'    => now(),
        ]);

        session()->flash('success', "شناسنامه #{$code} صادر شد.");

        return redirect()->route('certificates.show', $cert);
    }

    public function render()
    {
        return view('livewire.certificates.create', [
            'customers' => Customer::orderBy('name')->limit(200)->get(),
            'orders'    => Order::latest('id')->limit(100)->get(),
        ])->layout('components.layouts.app');
    }
}
""")

write_file("resources/views/livewire/certificates/create.blade.php", r"""
<div class="p-4 md:p-6 max-w-3xl mx-auto">
    <div class="flex items-center gap-3 mb-6">
        <a href="{{ route('certificates.index') }}" class="btn btn-ghost btn-sm">→</a>
        <h1 class="text-xl md:text-2xl font-bold">💎 شناسنامه جدید</h1>
    </div>

    {{-- Step indicator --}}
    <ul class="steps steps-horizontal w-full mb-6 text-xs">
        <li class="step {{ $step >= 1 ? 'step-primary' : '' }}">سنگ/فلز</li>
        <li class="step {{ $step >= 2 ? 'step-primary' : '' }}">مشخصات</li>
        <li class="step {{ $step >= 3 ? 'step-primary' : '' }}">تصویر</li>
    </ul>

    <div class="card bg-base-100 shadow">
        <div class="card-body gap-5">

            {{-- ========== STEP 1 ========== --}}
            @if($step === 1)
                <div>
                    <h3 class="font-bold text-sm mb-3 text-base-content/70">💎 انتخاب سنگ</h3>
                    <div class="grid grid-cols-3 md:grid-cols-4 gap-2">
                        @foreach($stoneOptions as $i => $s)
                            <button type="button"
                                    wire:click="selectStone({{ $i }})"
                                    class="border-2 rounded-lg p-2 text-center transition
                                        {{ $stoneName === $s['name'] ? 'border-primary bg-primary/10' : 'border-base-300 hover:border-primary/50' }}">
                                <div class="text-2xl mb-1">{{ $s['icon'] }}</div>
                                <div class="text-[11px] font-bold leading-tight">{{ $s['name'] }}</div>
                            </button>
                        @endforeach
                    </div>
                </div>

                <div class="divider my-1"></div>

                <div>
                    <h3 class="font-bold text-sm mb-3 text-base-content/70">⚙️ انتخاب فلز</h3>
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-2">
                        @foreach($metalOptions as $i => $m)
                            <button type="button"
                                    wire:click="selectMetal({{ $i }})"
                                    class="border-2 rounded-lg p-2 text-center text-xs font-bold transition
                                        {{ $metal === $m['name'] ? 'border-primary bg-primary/10' : 'border-base-300 hover:border-primary/50' }}">
                                {{ $m['name'] }}
                            </button>
                        @endforeach
                    </div>
                </div>
            @endif

            {{-- ========== STEP 2 ========== --}}
            @if($step === 2)
                <div class="alert alert-info py-2 text-xs">
                    <span>💎 <strong>{{ $stoneName }}</strong> — ⚙️ <strong>{{ $metal }}</strong></span>
                </div>

                <div class="grid grid-cols-2 md:grid-cols-5 gap-3">
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">طول (mm)</span></label>
                        <input type="number" wire:model="length" step="0.01" dir="ltr"
                               class="input input-bordered input-sm w-full text-center" />
                        @error('length') <span class="text-error text-[10px]">{{ $message }}</span> @enderror
                    </div>
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">عرض (mm)</span></label>
                        <input type="number" wire:model="width" step="0.01" dir="ltr"
                               class="input input-bordered input-sm w-full text-center" />
                        @error('width') <span class="text-error text-[10px]">{{ $message }}</span> @enderror
                    </div>
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">وزن (gr)</span></label>
                        <input type="number" wire:model="weight" step="0.001" dir="ltr"
                               class="input input-bordered input-sm w-full text-center" />
                        @error('weight') <span class="text-error text-[10px]">{{ $message }}</span> @enderror
                    </div>
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">عیار</span></label>
                        <input type="text" value="{{ $metalCarat }}" readonly
                               class="input input-bordered input-sm w-full text-center bg-base-200" />
                    </div>
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">برلیان</span></label>
                        <input type="number" wire:model="brilliant" dir="ltr"
                               class="input input-bordered input-sm w-full text-center" />
                    </div>
                </div>
            @endif

            {{-- ========== STEP 3 ========== --}}
            @if($step === 3)
                <div class="alert alert-info py-2 text-xs">
                    <span>💎 {{ $stoneName }} — ⚙️ {{ $metal }} — 📐 {{ $length }}×{{ $width }} — ⚖️ {{ $weight }}g</span>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">👤 مشتری (اختیاری)</span></label>
                        <select wire:model="customerId" class="select select-bordered select-sm w-full">
                            <option value="">— بدون مشتری —</option>
                            @foreach($customers as $c)
                                <option value="{{ $c->id }}">{{ $c->name }} — {{ $c->phone }}</option>
                            @endforeach
                        </select>
                    </div>
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">📦 سفارش (اختیاری)</span></label>
                        <select wire:model="orderId" class="select select-bordered select-sm w-full">
                            <option value="">— بدون سفارش —</option>
                            @foreach($orders as $o)
                                <option value="{{ $o->id }}">#{{ $o->order_number }} — {{ $o->customer?->name }}</option>
                            @endforeach
                        </select>
                    </div>
                </div>

                <div class="form-control">
                    <label class="label py-1"><span class="label-text text-xs font-bold">📸 تصویر محصول</span></label>
                    <input type="file" wire:model="image" accept="image/*"
                           class="file-input file-input-bordered file-input-sm w-full" />
                    @if($image)
                        <div class="mt-2">
                            <img src="{{ $image->temporaryUrl() }}" class="w-24 h-24 object-contain border rounded" />
                        </div>
                    @endif
                    @error('image') <span class="text-error text-[10px]">{{ $message }}</span> @enderror
                </div>
            @endif

            {{-- دکمه‌ها --}}
            <div class="flex justify-between gap-2 mt-4 pt-3 border-t">
                <div>
                    @if($step > 1)
                        <button wire:click="prevStep" class="btn btn-ghost btn-sm">→ قبلی</button>
                    @endif
                </div>
                <div class="flex gap-2">
                    <a href="{{ route('certificates.index') }}" class="btn btn-ghost btn-sm">انصراف</a>
                    @if($step < 3)
                        <button wire:click="nextStep" class="btn btn-primary btn-sm">بعدی ←</button>
                    @else
                        <button wire:click="save" wire:loading.attr="disabled" class="btn btn-success btn-sm">
                            <span wire:loading.remove wire:target="save">✅ صدور شناسنامه</span>
                            <span wire:loading wire:target="save">⏳...</span>
                        </button>
                    @endif
                </div>
            </div>
        </div>
    </div>
</div>
""")

# =========================================================
# ۳. کامپوننت Dashboard با کارت‌های مینیمال
# =========================================================

write_file("app/Livewire/Dashboard.php", r"""
<?php

namespace App\Livewire;

use App\Models\Customer;
use App\Models\Order;
use Livewire\Component;

class Dashboard extends Component
{
    public function render()
    {
        $todayStart     = now()->startOfDay();
        $yesterdayStart = now()->subDay()->startOfDay();
        $yesterdayEnd   = now()->subDay()->endOfDay();

        // امروز
        $ordersToday = Order::where('created_at', '>=', $todayStart)->count();
        $amountToday = (float) Order::where('created_at', '>=', $todayStart)->sum('amount');
        $customersToday = Customer::where('created_at', '>=', $todayStart)->count();

        // دیروز
        $ordersYesterday = Order::whereBetween('created_at', [$yesterdayStart, $yesterdayEnd])->count();
        $amountYesterday = (float) Order::whereBetween('created_at', [$yesterdayStart, $yesterdayEnd])->sum('amount');
        $customersYesterday = Customer::whereBetween('created_at', [$yesterdayStart, $yesterdayEnd])->count();

        // کل
        $ordersTotal    = Order::count();
        $customersTotal = Customer::count();

        // وضعیت‌ها
        $pending    = Order::where('status', 'pending')->count();
        $finalCheck = Order::where('status', 'final-check')->count();
        $courier    = Order::where('status', 'courier')->count();

        // درصد تغییرات
        $calcGrowth = function ($today, $yesterday) {
            if ($yesterday == 0) {
                return $today > 0 ? ['dir' => 'up', 'pct' => 100] : ['dir' => 'flat', 'pct' => 0];
            }
            $pct = round((($today - $yesterday) / $yesterday) * 100, 1);
            return [
                'dir' => $pct > 0 ? 'up' : ($pct < 0 ? 'down' : 'flat'),
                'pct' => abs($pct),
            ];
        };

        $stats = [
            'orders' => [
                'label'    => 'سفارش امروز',
                'value'    => $ordersToday,
                'yesterday'=> $ordersYesterday,
                'growth'   => $calcGrowth($ordersToday, $ordersYesterday),
                'icon'     => '📦',
                'ic'       => 'ic-blue',
            ],
            'amount' => [
                'label'    => 'فروش امروز',
                'value'    => $amountToday,
                'yesterday'=> $amountYesterday,
                'growth'   => $calcGrowth($amountToday, $amountYesterday),
                'icon'     => '💰',
                'ic'       => 'ic-green',
                'money'    => true,
            ],
            'customers' => [
                'label'    => 'مشتری امروز',
                'value'    => $customersToday,
                'yesterday'=> $customersYesterday,
                'growth'   => $calcGrowth($customersToday, $customersYesterday),
                'icon'     => '👥',
                'ic'       => 'ic-indigo',
            ],
            'pending' => [
                'label'    => 'در انتظار',
                'value'    => $pending,
                'yesterday'=> null,
                'growth'   => null,
                'icon'     => '📝',
                'ic'       => 'ic-amber',
            ],
            'check' => [
                'label'    => 'چک نهایی',
                'value'    => $finalCheck,
                'yesterday'=> null,
                'growth'   => null,
                'icon'     => '🔍',
                'ic'       => 'ic-sky',
            ],
            'courier' => [
                'label'    => 'تحویل مامور',
                'value'    => $courier,
                'yesterday'=> null,
                'growth'   => null,
                'icon'     => '🚚',
                'ic'       => 'ic-violet',
            ],
            'total' => [
                'label'    => 'کل سفارشات',
                'value'    => $ordersTotal,
                'yesterday'=> null,
                'growth'   => null,
                'icon'     => '📊',
                'ic'       => 'ic-rose',
            ],
        ];

        $recentOrders = Order::with(['customer', 'channel', 'items'])
            ->latest('id')
            ->limit(8)
            ->get();

        return view('livewire.dashboard', compact('stats', 'recentOrders'))
            ->layout('components.layouts.app');
    }
}
""")

write_file("resources/views/livewire/dashboard.blade.php", r"""
<div class="p-4 md:p-6 space-y-5">

    {{-- هدر --}}
    <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
            <h1 class="text-xl md:text-2xl font-bold">🏠 داشبورد</h1>
            <div class="text-xs text-base-content/60 mt-1">{{ now()->format('Y/m/d H:i') }}</div>
        </div>
        <a href="{{ route('orders.create') }}" class="btn btn-primary btn-sm">➕ سفارش جدید</a>
    </div>

    {{-- کارت‌های آماری --}}
    <div class="stat-strip">
        @foreach($stats as $key => $s)
            <div class="stat-card-mini">
                <div class="stat-head">
                    <div class="stat-icon {{ $s['ic'] }}">{{ $s['icon'] }}</div>
                    @if($s['growth'] && $s['growth']['dir'] !== 'flat')
                        <span class="stat-delta {{ $s['growth']['dir'] }}">
                            {{ $s['growth']['dir'] === 'up' ? '▲' : '▼' }}
                            {{ $s['growth']['pct'] }}%
                        </span>
                    @endif
                </div>

                <div class="stat-label">{{ $s['label'] }}</div>

                <div class="stat-value">
                    @if(isset($s['money']))
                        {{ number_format($s['value']) }}
                    @else
                        {{ number_format($s['value']) }}
                    @endif
                </div>

                @if($s['yesterday'] !== null)
                    <div class="text-[10px] text-base-content/50 mt-1">
                        دیروز: {{ number_format($s['yesterday']) }}
                    </div>
                @endif
            </div>
        @endforeach
    </div>

    {{-- آخرین سفارشات --}}
    <div class="card bg-base-100 shadow">
        <div class="card-body p-0">
            <div class="flex justify-between items-center p-4 border-b">
                <h2 class="font-bold">📋 آخرین سفارشات</h2>
                <a href="{{ route('orders.index') }}" class="btn btn-ghost btn-xs">همه →</a>
            </div>

            @if($recentOrders->isEmpty())
                <div class="p-8 text-center text-base-content/50 text-sm">هنوز سفارشی نیست.</div>
            @else
                <div class="pro-table-wrap">
                    <table class="pro-table">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>مشتری</th>
                                <th>محصولات</th>
                                <th>وضعیت</th>
                                <th>تاریخ</th>
                            </tr>
                        </thead>
                        <tbody>
                            @foreach($recentOrders as $o)
                                <tr>
                                    <td>
                                        <a href="{{ route('orders.show', $o) }}" class="link link-primary font-mono font-bold">
                                            {{ $o->order_number }}
                                        </a>
                                    </td>
                                    <td>{{ $o->customer?->name ?? '—' }}</td>
                                    <td class="text-xs text-base-content/70">{{ \Illuminate\Support\Str::limit($o->products_summary, 50) }}</td>
                                    <td>
                                        <span class="badge-status {{ $o->status }}">{{ $o->status_label }}</span>
                                    </td>
                                    <td class="text-xs">{{ $o->created_at?->format('m/d H:i') }}</td>
                                </tr>
                            @endforeach
                        </tbody>
                    </table>
                </div>
            @endif
        </div>
    </div>
</div>
""")

# =========================================================
# ۴. جدول سفارشات — بازنویسی کامل
# =========================================================

write_file("resources/views/livewire/orders/index.blade.php", r"""
<div class="p-4 md:p-6 space-y-4">

    @if (session('success'))
        <div class="alert alert-success text-sm py-2"><span>{{ session('success') }}</span></div>
    @endif

    <div class="flex flex-wrap items-center justify-between gap-3">
        <h1 class="text-xl md:text-2xl font-bold">📦 سفارشات</h1>
        <div class="flex flex-wrap gap-2">
            <a href="{{ route('orders.create') }}" class="btn btn-primary btn-sm">➕ سفارش جدید</a>
        </div>
    </div>

    {{-- فیلترهای فعال --}}
    @if($search || $statusFilter || $channelFilter || $dateFrom || $dateTo)
        <div class="flex flex-wrap gap-2 items-center p-3 bg-base-100 rounded-lg border">
            <span class="text-xs font-bold text-base-content/60">فیلترها:</span>
            @if($search)
                <span class="badge badge-primary badge-sm gap-1">
                    🔍 {{ $search }}
                    <button wire:click="$set('search', '')" class="text-xs">✕</button>
                </span>
            @endif
            @if($statusFilter)
                <span class="badge badge-primary badge-sm gap-1">
                    {{ $statusFilter }}
                    <button wire:click="$set('statusFilter', '')" class="text-xs">✕</button>
                </span>
            @endif
            @if($channelFilter)
                <span class="badge badge-primary badge-sm gap-1">
                    کانال
                    <button wire:click="$set('channelFilter', '')" class="text-xs">✕</button>
                </span>
            @endif
            @if($dateFrom || $dateTo)
                <span class="badge badge-primary badge-sm gap-1">
                    {{ $dateFrom ?: '...' }} → {{ $dateTo ?: '...' }}
                    <button wire:click="$set('dateFrom', ''); $set('dateTo', '')" class="text-xs">✕</button>
                </span>
            @endif
            <button wire:click="clearFilters" class="btn btn-ghost btn-xs mr-auto">✕ پاک کردن همه</button>
        </div>
    @endif

    {{-- نوار انتخاب --}}
    @if(count($selected) > 0)
        <div class="alert alert-info py-2 flex flex-wrap items-center gap-2 text-sm">
            <span class="font-bold">✨ {{ count($selected) }} انتخاب شده</span>
            <div class="flex flex-wrap gap-1 ml-auto">
                <button wire:click="bulkChangeStatus('pending')" class="btn btn-warning btn-xs">📝</button>
                <button wire:click="bulkChangeStatus('final-check')" class="btn btn-info btn-xs">🔍</button>
                <button wire:click="bulkChangeStatus('courier')" class="btn btn-success btn-xs">🚚</button>
                <button wire:click="bulkPrintLabels" class="btn btn-primary btn-xs">🏷️ چاپ</button>
                <button wire:click="clearSelection" class="btn btn-ghost btn-xs">✕</button>
                <button wire:click="bulkDelete" wire:confirm="حذف شود؟" class="btn btn-error btn-xs">🗑️</button>
            </div>
        </div>
    @endif

    {{-- جدول --}}
    <div class="bg-base-100 rounded-lg shadow border overflow-hidden">
        <div class="pro-table-wrap">
            <table class="pro-table">
                <thead>
                    <tr>
                        <th style="width:36px;">
                            <input type="checkbox" class="checkbox checkbox-xs"
                                   wire:click="selectAllVisible" />
                        </th>

                        {{-- شماره --}}
                        <th class="sortable {{ $sortField === 'order_number' ? 'sort-active' : '' }}"
                            wire:click="sortBy('order_number')">
                            <div class="th-inner">
                                <span class="sort-icon">
                                    {{ $sortField === 'order_number' ? ($sortDir === 'asc' ? '▲' : '▼') : '⇅' }}
                                </span>
                                <span>شماره</span>
                                <button class="filter-btn" wire:click.stop="$set('statusFilter', $statusFilter ? '' : 'pending')"
                                        title="فیلتر">⚙</button>
                            </div>
                        </th>

                        {{-- مشتری --}}
                        <th class="sortable {{ $sortField === 'customer' ? 'sort-active' : '' }}"
                            wire:click="sortBy('id')">
                            <div class="th-inner">
                                <span class="sort-icon">⇅</span>
                                <span>مشتری</span>
                            </div>
                        </th>

                        {{-- تلفن --}}
                        <th class="sortable">
                            <div class="th-inner">
                                <span>تلفن</span>
                            </div>
                        </th>

                        {{-- محصولات --}}
                        <th>
                            <div class="th-inner">
                                <span>محصولات</span>
                            </div>
                        </th>

                        {{-- وضعیت --}}
                        <th class="sortable {{ $sortField === 'status' ? 'sort-active' : '' }}"
                            wire:click="sortBy('status')">
                            <div class="th-inner">
                                <span class="sort-icon">
                                    {{ $sortField === 'status' ? ($sortDir === 'asc' ? '▲' : '▼') : '⇅' }}
                                </span>
                                <span>وضعیت</span>
                                <button class="filter-btn {{ $statusFilter ? 'active' : '' }}"
                                        wire:click.stop>⚙</button>
                            </div>
                        </th>

                        {{-- کانال --}}
                        <th class="sortable">
                            <div class="th-inner">
                                <span>کانال</span>
                                <button class="filter-btn {{ $channelFilter ? 'active' : '' }}"
                                        wire:click.stop>⚙</button>
                            </div>
                        </th>

                        {{-- بیمه --}}
                        <th class="sortable {{ $sortField === 'insurance' ? 'sort-active' : '' }}"
                            wire:click="sortBy('insurance')">
                            <div class="th-inner">
                                <span class="sort-icon">
                                    {{ $sortField === 'insurance' ? ($sortDir === 'asc' ? '▲' : '▼') : '⇅' }}
                                </span>
                                <span>بیمه</span>
                            </div>
                        </th>

                        {{-- تاریخ --}}
                        <th class="sortable {{ $sortField === 'created_at' ? 'sort-active' : '' }}"
                            wire:click="sortBy('created_at')">
                            <div class="th-inner">
                                <span class="sort-icon">
                                    {{ $sortField === 'created_at' ? ($sortDir === 'asc' ? '▲' : '▼') : '⇅' }}
                                </span>
                                <span>تاریخ</span>
                            </div>
                        </th>

                        {{-- عملیات --}}
                        <th>عملیات</th>
                    </tr>
                </thead>
                <tbody>
                    @forelse($orders as $order)
                        <tr wire:key="order-{{ $order->id }}"
                            class="{{ in_array($order->id, $selected) ? 'selected' : '' }}">
                            <td>
                                <input type="checkbox" class="checkbox checkbox-xs"
                                       @checked(in_array($order->id, $selected))
                                       wire:click="toggleSelect({{ $order->id }})" />
                            </td>

                            <td>
                                <a href="{{ route('orders.show', $order) }}" class="link link-primary font-mono font-bold">
                                    {{ $order->order_number }}
                                </a>
                            </td>

                            <td>
                                @if($order->customer)
                                    <a href="{{ route('customers.show', $order->customer) }}" class="link link-hover">
                                        {{ $order->customer->name }}
                                    </a>
                                @else
                                    —
                                @endif
                            </td>

                            <td class="font-mono text-xs" dir="ltr">{{ $order->phone ?? '—' }}</td>

                            <td class="text-xs">{{ \Illuminate\Support\Str::limit($order->products_summary, 40) }}</td>

                            <td>
                                <span class="badge-status {{ $order->status }}">{{ $order->status_label }}</span>
                            </td>

                            <td>
                                @if($order->channel)
                                    <span class="text-xs">
                                        {{ $order->channel->icon }} {{ $order->channel->name }}
                                    </span>
                                @else
                                    —
                                @endif
                            </td>

                            <td>{{ number_format((float) $order->insurance) }}</td>

                            <td class="text-xs">{{ $order->created_at?->format('Y/m/d H:i') }}</td>

                            <td class="cell-actions">
                                <div class="flex gap-1">
                                    <a href="{{ route('orders.show', $order) }}" class="btn btn-ghost btn-xs" title="مشاهده">👁️</a>
                                    <a href="{{ route('orders.edit', $order) }}" class="btn btn-ghost btn-xs" title="ویرایش">✏️</a>
                                    <a href="{{ route('orders.print-label', $order) }}" target="_blank" class="btn btn-ghost btn-xs" title="برچسب">🏷️</a>
                                    <button wire:click="deleteOrder({{ $order->id }})" wire:confirm="حذف شود؟"
                                            class="btn btn-ghost btn-xs text-error" title="حذف">🗑️</button>
                                </div>
                            </td>
                        </tr>
                    @empty
                        <tr>
                            <td colspan="10" class="text-center py-8 text-base-content/50">سفارشی نیست</td>
                        </tr>
                    @endforelse
                </tbody>
            </table>
        </div>
    </div>

    <div>{{ $orders->links() }}</div>
</div>
""")

# =========================================================
# ۵. تنظیمات ادمین — لینک به import
# =========================================================

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

    protected $queryString = [
        'search'        => ['except' => ''],
        'statusFilter'  => ['except' => ''],
        'channelFilter' => ['except' => ''],
    ];

    public function updatingSearch(): void { $this->resetPage(); }
    public function updatingStatusFilter(): void { $this->resetPage(); }
    public function updatingChannelFilter(): void { $this->resetPage(); }

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

    public function selectAllVisible(): void
    {
        $ids = $this->buildQuery()->pluck('id')->all();
        $this->selected = array_values(array_unique(array_merge($this->selected, $ids)));
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

    public function deleteOrder(int $orderId): void
    {
        Order::find($orderId)?->delete();
        session()->flash('success', 'سفارش حذف شد.');
    }

    protected function buildQuery()
    {
        return Order::query()
            ->with(['customer', 'channel', 'items'])
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

# =========================================================
# ۶. Customers Index با جدول جدید
# =========================================================

write_file("resources/views/livewire/customers/index.blade.php", r"""
<div class="p-4 md:p-6 space-y-4">

    <div class="flex flex-wrap items-center justify-between gap-3">
        <h1 class="text-xl md:text-2xl font-bold">👥 مشتریان</h1>
        <a href="{{ route('customers.create') }}" class="btn btn-primary btn-sm">➕ مشتری جدید</a>
    </div>

    <div class="bg-base-100 rounded-lg shadow border overflow-hidden">
        <div class="pro-table-wrap">
            <table class="pro-table">
                <thead>
                    <tr>
                        <th style="width:50px;">#</th>
                        <th>نام</th>
                        <th>تلفن</th>
                        <th>کدپستی</th>
                        <th>سفارش</th>
                        <th>مجموع</th>
                        <th>آدرس</th>
                        <th>عملیات</th>
                    </tr>
                </thead>
                <tbody>
                    @forelse($customers as $c)
                        <tr>
                            <td>{{ $c->id }}</td>
                            <td class="font-bold">
                                <a href="{{ route('customers.show', $c) }}" class="link link-primary">
                                    {{ $c->name ?? '—' }}
                                </a>
                            </td>
                            <td class="font-mono text-xs" dir="ltr">{{ $c->phone }}</td>
                            <td class="font-mono text-xs" dir="ltr">{{ $c->postal_code ?? '—' }}</td>
                            <td><span class="badge badge-primary badge-sm">{{ $c->orders_count }}</span></td>
                            <td class="text-xs">{{ number_format($c->orders_sum_amount ?? 0) }}</td>
                            <td class="text-xs">{{ \Illuminate\Support\Str::limit($c->address, 40) }}</td>
                            <td>
                                <div class="flex gap-1">
                                    <a href="{{ route('customers.show', $c) }}" class="btn btn-ghost btn-xs">👁️</a>
                                    <a href="{{ route('customers.edit', $c) }}" class="btn btn-ghost btn-xs">✏️</a>
                                </div>
                            </td>
                        </tr>
                    @empty
                        <tr><td colspan="8" class="text-center py-8 text-base-content/50">مشتری‌ای نیست</td></tr>
                    @endforelse
                </tbody>
            </table>
        </div>
    </div>

    <div>{{ $customers->links() }}</div>
</div>
""")

# =========================================================
# ۷. Customers Index — محاسبه‌ی مجموع خرید
# =========================================================

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
            ->withSum('orders as orders_sum_amount', 'amount')
            ->when($this->search, function ($q) {
                $q->where(function ($qq) {
                    $qq->where('name', 'like', "%{$this->search}%")
                       ->orWhere('phone', 'like', "%{$this->search}%");
                });
            })
            ->latest('id')
            ->paginate(20);

        return view('livewire.customers.index', compact('customers'))
            ->layout('components.layouts.app');
    }
}
""")

print()
print("═" * 60)
print("✅ بازطراحی کامل شد")
print("═" * 60)
print()
print("📌 اجرا کن:")
print()
print("   php artisan optimize:clear")
print("   npm run build")
print("   php artisan serve --host=0.0.0.0 --port=8000")
print()
