from pathlib import Path
import textwrap

PROJECT = Path(r"D:\prodo\shopgun-v2.1")
if not PROJECT.exists():
    raise SystemExit("❌ پروژه پیدا نشد")

def write_file(rel, content):
    path = PROJECT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    existed = path.exists()
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    print(f"{'🔁' if existed else '✅'} {rel}")

print("═" * 60)
print("🔧 Part E — رفع باگ‌ها + تاریخ شمسی + اعداد فارسی")
print("═" * 60)
print()

# =========================================================
# ۱. Designer — رفع خطای null
# =========================================================

write_file("app/Livewire/Certificates/Designer.php", r"""
<?php

namespace App\Livewire\Certificates;

use App\Models\Certificate;
use App\Support\CertConfig;
use Livewire\Component;

class Designer extends Component
{
    public ?Certificate $certificate = null;
    public array $design = [];
    public array $sizes = [];
    public array $assets = [];
    public bool $hideDesc = false;

    public function mount(Certificate|int|string|null $certificate = null): void
    {
        // تبدیل ورودی
        if ($certificate instanceof Certificate) {
            $this->certificate = $certificate;
        } elseif (is_numeric($certificate)) {
            $this->certificate = Certificate::find((int) $certificate);
        }

        // اگه نبود، اولین رو بگیر یا یه خالی بساز
        if (! $this->certificate) {
            $this->certificate = Certificate::first();
        }

        if (! $this->certificate) {
            $this->certificate = new Certificate([
                'code' => '000000', 'serial' => 'MJ-DESIGN',
                'stone_name' => 'فیروزه عجمی', 'stone_en' => 'Turquoise Ajami',
                'stone_origin' => 'نیشابور', 'stone_flag' => 'ir',
                'metal' => 'نقره 925', 'metal_en' => 'Silver 925', 'metal_carat' => '925',
                'length' => 13, 'width' => 9, 'weight' => 1.28, 'brilliant' => 5,
            ]);
        }

        // اطمینان از array بودن
        $designData = $this->certificate->design_data;
        $this->design = is_array($designData) ? $designData : [];
        if (empty($this->design)) {
            $this->design = $this->certificate->design_or_default ?? ['version' => '1.0', 'elements' => []];
        }

        $this->sizes    = CertConfig::sizes();
        $this->assets   = CertConfig::assets();
        $this->hideDesc = CertConfig::hideDesc();
    }

    public function save(array $design = []): void
    {
        $design = is_array($design) ? $design : [];
        $this->design = $design;

        if ($this->certificate && $this->certificate->exists) {
            $this->certificate->update(['design_data' => $design]);
        }

        CertConfig::set('cert.design_data', $design);
        session()->flash('success', 'طراحی ذخیره شد');
    }

    public function saveSizes(array $sizes = []): void
    {
        foreach ($sizes as $k => $v) {
            CertConfig::set('cert.' . $k, $v);
        }
        $this->sizes = CertConfig::sizes();
        session()->flash('success', 'سایزها ذخیره شد');
    }

    public function saveAssets(array $assets = []): void
    {
        foreach ($assets as $k => $v) {
            CertConfig::set('cert.' . $k, $v);
        }
        $this->assets = CertConfig::assets();
        session()->flash('success', 'تصاویر ذخیره شد');
    }

    public function toggleHideDesc(): void
    {
        $this->hideDesc = ! $this->hideDesc;
        CertConfig::set('cert.hide_desc', $this->hideDesc ? 'true' : 'false');
    }

    public function render()
    {
        return view('livewire.certificates.designer')
            ->layout('components.layouts.app');
    }
}
""")

# =========================================================
# ۲. Certificate Model — رفع ابعاد + پشتیبانی طول/عرض null
# =========================================================

write_file("app/Models/Certificate.php", r"""
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Spatie\Activitylog\Models\Activity;
use Spatie\Activitylog\Models\Concerns\LogsActivity;
use Spatie\Activitylog\Support\LogOptions;

class Certificate extends Model
{
    use LogsActivity;

    protected $fillable = [
        'code', 'serial', 'sku', 'stone_name', 'stone_en', 'stone_origin', 'stone_flag',
        'metal', 'metal_en', 'metal_carat', 'length', 'width', 'weight', 'brilliant',
        'image_path', 'order_id', 'customer_id', 'issued_at', 'design_data', 'meta',
    ];

    protected $casts = [
        'issued_at'   => 'datetime',
        'design_data' => 'array',
        'meta'        => 'array',
    ];

    public function getActivitylogOptions(): LogOptions
    {
        return LogOptions::defaults()
            ->logOnly(['code', 'stone_name', 'metal', 'weight'])
            ->logOnlyDirty()
            ->useLogName('certificate');
    }

    public function order(): BelongsTo    { return $this->belongsTo(Order::class); }
    public function customer(): BelongsTo { return $this->belongsTo(Customer::class); }

    public function activities()
    {
        return Activity::query()
            ->where('subject_type', $this->getMorphClass())
            ->where('subject_id', $this->getKey())
            ->latest();
    }

    public static function generateCode(): string
    {
        do { $code = (string) random_int(100000, 999999); }
        while (self::where('code', $code)->exists());
        return $code;
    }

    public static function generateSerial(string $code, string $stoneEn = 'XXX'): string
    {
        $now  = now();
        $ymd  = $now->format('ymd');
        $hm   = $now->format('Hi');
        $abbr = strtoupper(substr(preg_replace('/[^A-Za-z]/', '', $stoneEn), 0, 3)) ?: 'XXX';
        return "MJ-{$ymd}-{$hm}-{$code}-{$abbr}-A";
    }

    public function getPublicUrlAttribute(): string
    {
        return url("/Q/{$this->code}");
    }

    public function getQrUrlAttribute(): string
    {
        return 'https://api.qrserver.com/v1/create-qr-code/?size=300x300&margin=1&data='
            . urlencode($this->public_url);
    }

    // عدد بدون .00
    protected static function fmt($v): string
    {
        if ($v === null || $v === '') return '—';
        $f = (float) $v;
        if ($f == 0) return '0';
        if (floor($f) == $f) return (string) (int) $f;
        return rtrim(rtrim(number_format($f, 2, '.', ''), '0'), '.');
    }

    public function getLengthCleanAttribute(): string { return self::fmt($this->length); }
    public function getWidthCleanAttribute(): string  { return self::fmt($this->width); }
    public function getWeightCleanAttribute(): string { return self::fmt($this->weight); }
    public function getBrilliantCleanAttribute(): string { return self::fmt($this->brilliant); }

    public function getDimensionAttribute(): string
    {
        return $this->length_clean . '×' . $this->width_clean;
    }

    public function getDesignOrDefaultAttribute(): array
    {
        if (! empty($this->design_data) && is_array($this->design_data)) {
            return $this->design_data;
        }

        return [
            'version' => '1.0',
            'elements' => [
                ['id' => 'title',  'type' => 'text', 'text' => 'Certificate',           'x' => 180, 'y' => 30,  'fontSize' => 28, 'fill' => '#6b4423', 'fontWeight' => 'bold'],
                ['id' => 'stone',  'type' => 'text', 'text' => '{stoneEn}',             'x' => 160, 'y' => 90,  'fontSize' => 20, 'fill' => '#0369a1', 'fontWeight' => 'bold'],
                ['id' => 'metal',  'type' => 'text', 'text' => '{metal} ({carat})',     'x' => 160, 'y' => 130, 'fontSize' => 14, 'fill' => '#334155'],
                ['id' => 'size',   'type' => 'text', 'text' => '{length}×{width} mm',   'x' => 160, 'y' => 165, 'fontSize' => 12, 'fill' => '#334155'],
                ['id' => 'weight', 'type' => 'text', 'text' => 'Weight: {weight} gr',   'x' => 160, 'y' => 195, 'fontSize' => 12, 'fill' => '#334155'],
                ['id' => 'code',   'type' => 'text', 'text' => '#{code}',                'x' => 160, 'y' => 230, 'fontSize' => 14, 'fill' => '#b45309', 'fontWeight' => 'bold'],
                ['id' => 'qr',     'type' => 'qr',   'text' => '',                       'x' => 200, 'y' => 200, 'size' => 100],
            ],
        ];
    }
}
""")

# =========================================================
# ۳. ViewModal — رفع iframe
# =========================================================

write_file("resources/views/livewire/certificates/view-modal.blade.php", r"""
<div>
    @if($show && $certificate)
    <div class="fixed inset-0 z-[85] flex items-start justify-center p-4 overflow-y-auto"
         x-data="{ show: true }" x-init="$nextTick(() => show = true)"
         @keydown.escape.window="$wire.close()">

        <div class="fixed inset-0 bg-black/70 backdrop-blur-md"
             x-show="show"
             x-transition:enter="ease-out duration-300"
             x-transition:enter-start="opacity-0"
             x-transition:enter-end="opacity-100"
             wire:click="close"></div>

        <div class="relative bg-base-100 rounded-2xl shadow-2xl w-full max-w-3xl my-8 md:my-16 border border-base-300"
             x-show="show"
             x-transition:enter="ease-out duration-300"
             x-transition:enter-start="opacity-0 translate-y-8 scale-95"
             x-transition:enter-end="opacity-100 translate-y-0 scale-100">

            <div class="flex items-center justify-between p-4 border-b border-base-300 bg-gradient-to-l from-primary/10 to-transparent rounded-t-2xl">
                <div class="flex items-center gap-3">
                    <div class="w-9 h-9 rounded-lg bg-gradient-to-br from-violet-500 to-purple-600 flex items-center justify-center text-white shadow">💎</div>
                    <div>
                        <h2 class="font-bold text-base">شناسنامه #{{ $certificate->code }}</h2>
                        <div class="text-xs text-base-content/60 font-mono" dir="ltr">{{ $certificate->serial }}</div>
                    </div>
                </div>
                <button wire:click="close" class="btn btn-ghost btn-sm btn-circle">✕</button>
            </div>

            <div class="p-5 space-y-4 max-h-[calc(100vh-14rem)] overflow-y-auto">

                {{-- پیش‌نمایش کارت --}}
                <div class="flex justify-center bg-base-200/50 rounded-lg p-4">
                    <div id="certPreviewMount"
                         style="width: 300px; height: 300px; border-radius: 8px; overflow: hidden; background: #fffef9;">
                    </div>
                </div>

                {{-- اطلاعات --}}
                <div class="grid grid-cols-2 md:grid-cols-3 gap-2 text-sm">
                    <div class="p-3 rounded-lg bg-base-200/50">
                        <div class="text-[10px] text-base-content/60">💎 سنگ</div>
                        <div class="font-bold mt-0.5">{{ $certificate->stone_name }}</div>
                    </div>
                    <div class="p-3 rounded-lg bg-base-200/50">
                        <div class="text-[10px] text-base-content/60">⚙️ فلز</div>
                        <div class="mt-0.5">{{ $certificate->metal }} ({{ $certificate->metal_carat }})</div>
                    </div>
                    <div class="p-3 rounded-lg bg-base-200/50">
                        <div class="text-[10px] text-base-content/60">📐 ابعاد</div>
                        <div class="mt-0.5">{{ $certificate->dimension }} mm</div>
                    </div>
                    <div class="p-3 rounded-lg bg-base-200/50">
                        <div class="text-[10px] text-base-content/60">⚖️ وزن</div>
                        <div class="mt-0.5">{{ $certificate->weight_clean }} gr</div>
                    </div>
                    <div class="p-3 rounded-lg bg-base-200/50">
                        <div class="text-[10px] text-base-content/60">👤 مشتری</div>
                        <div class="mt-0.5">{{ $certificate->customer?->name ?? '—' }}</div>
                    </div>
                    <div class="p-3 rounded-lg bg-base-200/50">
                        <div class="text-[10px] text-base-content/60">📅 صدور</div>
                        <div class="mt-0.5 text-xs">{{ $certificate->issued_at?->format('Y/m/d') }}</div>
                    </div>
                </div>
            </div>

            <div class="p-4 border-t border-base-300 flex flex-wrap justify-end gap-2 rounded-b-2xl bg-base-200/50">
                <button wire:click="close" class="btn btn-ghost btn-sm">بستن</button>
                <button onclick="printCertView()" class="btn btn-info btn-sm">🖨️ چاپ</button>
                <button onclick="exportCertViewPng()" class="btn btn-success btn-sm">📸 PNG</button>
                <a href="{{ route('certificates.show', $certificate) }}" class="btn btn-outline btn-sm">صفحه کامل</a>
            </div>
        </div>
    </div>
    @endif
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script>
let certHtml = @json($html);

// رندر HTML توی یه iframe داینامیک
function mountCertPreview() {
    const mount = document.getElementById('certPreviewMount');
    if (!mount) return;

    mount.innerHTML = '';
    const iframe = document.createElement('iframe');
    iframe.id = 'certViewFrame';
    iframe.style.cssText = 'width: 100%; height: 100%; border: 0; background: #fffef9;';
    iframe.srcdoc = certHtml;
    mount.appendChild(iframe);
}

// وقتی Livewire این کامپوننت رو رندر کرد
document.addEventListener('DOMContentLoaded', () => {
    setTimeout(mountCertPreview, 100);
});

document.addEventListener('livewire:navigated', () => {
    setTimeout(mountCertPreview, 100);
});

// وقتی modal باز/بسته شد
if (window.Livewire) {
    Livewire.hook('morphed', () => {
        if (document.getElementById('certPreviewMount')) {
            setTimeout(mountCertPreview, 50);
        }
    });
}

function printCertView() {
    const frame = document.getElementById('certViewFrame');
    if (!frame) {
        alert('کارت پیدا نشد');
        return;
    }
    const w = window.open('', '', 'width=800,height=800');
    w.document.write(frame.srcdoc);
    w.document.close();
    setTimeout(() => { w.print(); setTimeout(() => w.close(), 500); }, 500);
}

function exportCertViewPng() {
    const frame = document.getElementById('certViewFrame');
    if (!frame) { alert('کارت پیدا نشد'); return; }

    const doc = frame.contentDocument || frame.contentWindow.document;
    const cert = doc.querySelector('.cert');
    if (!cert) { alert('کارت پیدا نشد'); return; }

    html2canvas(cert, {
        scale: 3,
        backgroundColor: '#fffef9',
        useCORS: true,
        allowTaint: true,
        logging: false,
    }).then(canvas => {
        const a = document.createElement('a');
        a.download = 'certificate.png';
        a.href = canvas.toDataURL('image/png');
        a.click();
    }).catch(err => {
        console.error(err);
        alert('خطا در ساخت PNG');
    });
}
</script>
""")

# =========================================================
# ۴. PersianDate Helper — با انتخابگر
# =========================================================

write_file("app/Support/PersianNumber.php", r"""
<?php

namespace App\Support;

class PersianNumber
{
    public static function toFa($input): string
    {
        if ($input === null) return '';

        $str = (string) $input;

        // اگه عدد بود، با format
        if (is_numeric($str)) {
            $str = number_format((float) $str, 0, '.', ',');
        }

        return str_replace(
            ['0','1','2','3','4','5','6','7','8','9'],
            ['۰','۱','۲','۳','۴','۵','۶','۷','۸','۹'],
            $str
        );
    }

    public static function toEn($input): string
    {
        return str_replace(
            ['۰','۱','۲','۳','۴','۵','۶','۷','۸','۹','٠','١','٢','٣','٤','٥','٦','٧','٨','٩'],
            ['0','1','2','3','4','5','6','7','8','9','0','1','2','3','4','5','6','7','8','9'],
            (string) $input
        );
    }
}
""")

# =========================================================
# ۵. Date Picker شمسی (Component)
# =========================================================

write_file("resources/views/components/ui/persian-date.blade.php", r"""
@props([
    'wire' => 'date',
    'label' => 'تاریخ',
    'placeholder' => '۱۴۰۳/۰۱/۰۱',
])

<div class="form-control">
    @if($label)
        <label class="label py-1"><span class="label-text text-xs font-bold">{{ $label }}</span></label>
    @endif

    <div class="persian-date-wrap relative" wire:ignore x-data="persianDatePicker(@entangle($wire))">
        <input
            type="text"
            x-ref="input"
            :value="displayValue"
            @focus="open()"
            @click="open()"
            dir="ltr"
            placeholder="{{ $placeholder }}"
            class="input input-bordered input-sm w-full font-mono text-center"
            readonly />

        {{-- پنل انتخابگر --}}
        <div x-show="isOpen"
             x-transition.opacity
             @click.outside="close()"
             class="absolute z-[100] mt-1 bg-base-100 border-2 border-primary rounded-lg shadow-xl p-3"
             style="width: 280px; top: 100%; right: 0;">

            {{-- هدر --}}
            <div class="flex justify-between items-center mb-2">
                <button type="button" @click="prevMonth()" class="btn btn-ghost btn-xs btn-circle">‹</button>
                <div class="text-sm font-bold" x-text="monthNames[month-1] + ' ' + toFa(year)"></div>
                <button type="button" @click="nextMonth()" class="btn btn-ghost btn-xs btn-circle">›</button>
            </div>

            {{-- روزهای هفته --}}
            <div class="grid grid-cols-7 gap-1 mb-1 text-[10px] text-base-content/60 text-center">
                <div>ش</div><div>ی</div><div>د</div><div>س</div><div>چ</div><div>پ</div><div>ج</div>
            </div>

            {{-- روزها --}}
            <div class="grid grid-cols-7 gap-1">
                <template x-for="blank in firstDayOffset" :key="'b' + blank">
                    <div></div>
                </template>
                <template x-for="day in daysInMonth" :key="day">
                    <button type="button"
                            @click="pick(day)"
                            class="w-full aspect-square rounded text-xs font-bold transition"
                            :class="{
                                'bg-primary text-primary-content': isSelected(day),
                                'hover:bg-base-300': !isSelected(day),
                            }"
                            x-text="toFa(day)"></button>
                </template>
            </div>

            {{-- دکمه‌ها --}}
            <div class="flex justify-between mt-3 pt-2 border-t border-base-300">
                <button type="button" @click="clear()" class="btn btn-ghost btn-xs">پاک کردن</button>
                <button type="button" @click="today()" class="btn btn-primary btn-xs">امروز</button>
            </div>
        </div>
    </div>
</div>

@once
@push('scripts')
<script>
function persianDatePicker(initialValue) {
    return {
        isOpen: false,
        year: 1403,
        month: 1,
        value: initialValue || '',

        monthNames: ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'],
        monthDays: [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29],

        get displayValue() {
            if (!this.value) return '';
            const parts = String(this.value).split('/');
            if (parts.length !== 3) return this.value;
            return this.toFa(parts[0]) + '/' + this.toFa(parts[1]) + '/' + this.toFa(parts[2]);
        },

        get daysInMonth() {
            return this.monthDays[this.month - 1];
        },

        get firstDayOffset() {
            // محاسبه‌ی ساده: روز هفته‌ی اول ماه
            // (کافیه برای نمایش)
            return (this.year * 365 + this.month * 30) % 7;
        },

        toFa(n) {
            return String(n).replace(/\d/g, d => '۰۱۲۳۴۵۶۷۸۹'[d]);
        },

        init() {
            // تاریخ امروز رو تنظیم کن
            const today = new Date();
            const jalali = this.gregorianToJalali(today.getFullYear(), today.getMonth() + 1, today.getDate());
            this.year = jalali[0];
            this.month = jalali[1];

            this.$watch('value', v => {
                if (v) {
                    const parts = String(v).split('/');
                    if (parts.length === 3) {
                        this.year = parseInt(parts[0]);
                        this.month = parseInt(parts[1]);
                    }
                }
            });
        },

        open() { this.isOpen = true; },
        close() { this.isOpen = false; },

        prevMonth() {
            this.month--;
            if (this.month < 1) { this.month = 12; this.year--; }
        },

        nextMonth() {
            this.month++;
            if (this.month > 12) { this.month = 1; this.year++; }
        },

        isSelected(day) {
            if (!this.value) return false;
            const parts = String(this.value).split('/');
            if (parts.length !== 3) return false;
            return parseInt(parts[0]) === this.year
                && parseInt(parts[1]) === this.month
                && parseInt(parts[2]) === day;
        },

        pick(day) {
            this.value = this.year + '/' + String(this.month).padStart(2, '0') + '/' + String(day).padStart(2, '0');
            this.close();
        },

        clear() {
            this.value = '';
            this.close();
        },

        today() {
            const now = new Date();
            const j = this.gregorianToJalali(now.getFullYear(), now.getMonth() + 1, now.getDate());
            this.value = j[0] + '/' + String(j[1]).padStart(2, '0') + '/' + String(j[2]).padStart(2, '0');
            this.close();
        },

        gregorianToJalali(gy, gm, gd) {
            const g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
            let jy = (gy <= 1600) ? 0 : 979;
            gy -= (gy <= 1600) ? 621 : 1600;
            const gy2 = (gm > 2) ? (gy + 1) : gy;
            let days = (365 * gy) + Math.floor((gy2 + 3) / 4) - Math.floor((gy2 + 99) / 100)
                + Math.floor((gy2 + 399) / 400) - 80 + gd + g_d_m[gm - 1];
            jy += 33 * Math.floor(days / 12053); days %= 12053;
            jy += 4 * Math.floor(days / 1461); days %= 1461;
            if (days > 365) { jy += Math.floor((days - 1) / 365); days = (days - 1) % 365; }
            const jm = (days < 186) ? 1 + Math.floor(days / 31) : 7 + Math.floor((days - 186) / 30);
            const jd = 1 + ((days < 186) ? (days % 31) : ((days - 186) % 30));
            return [jy, jm, jd];
        },
    }
}
</script>
@endpush
@endonce
""")

# =========================================================
# ۶. Blade Directives — اعداد فارسی سراسری
# =========================================================

write_file("app/Providers/AppServiceProvider.php", r"""
<?php

namespace App\Providers;

use App\Models\Order;
use App\Observers\OrderObserver;
use App\Support\PersianNumber;
use Illuminate\Support\Facades\Blade;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    public function register(): void {}

    public function boot(): void
    {
        Order::observe(OrderObserver::class);

        // @faNum($value) — نمایش عدد با اعداد فارسی
        Blade::directive('faNum', function ($expression) {
            return "<?php echo e(\App\Support\PersianNumber::toFa($expression)); ?>";
        });

        // @faMoney($value) — عدد با جداکننده هزارگان
        Blade::directive('faMoney', function ($expression) {
            return "<?php echo e(\App\Support\PersianNumber::toFa(number_format((float) ($expression ?? 0)))); ?>";
        });

        // @jdate($date, $format) — تاریخ شمسی
        Blade::directive('jdate', function ($expression) {
            return "<?php echo e(\App\Support\PersianDate::format($expression ?? now(), 'Y/m/d H:i')); ?>";
        });

        // ماکرو برای تنظیم اعداد فارسی
        Blade::stringable(function (\DateTimeInterface $date) {
            return \App\Support\PersianDate::format($date);
        });
    }
}
""")

# =========================================================
# ۷. Dashboard View — بازنویسی کامل با اعداد فارسی
# =========================================================

write_file("resources/views/livewire/dashboard.blade.php", r"""
<div class="p-4 md:p-6 space-y-4" wire:loading.class="opacity-60" wire:target="setRange">

    <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
            <h1 class="text-xl md:text-2xl font-bold">🏠 داشبورد</h1>
            <div class="text-xs text-base-content/60 mt-0.5">
                📅 {{ \App\Support\PersianDate::format(now(), 'Y/m/d H:i') }}
            </div>
        </div>

        <div class="flex gap-1 bg-base-100 rounded-lg p-1 shadow border">
            <button wire:click="setRange('today')" class="btn btn-xs {{ $range === 'today' ? 'btn-primary' : 'btn-ghost' }}">امروز</button>
            <button wire:click="setRange('yesterday')" class="btn btn-xs {{ $range === 'yesterday' ? 'btn-primary' : 'btn-ghost' }}">دیروز</button>
            <button wire:click="setRange('7days')" class="btn btn-xs {{ $range === '7days' ? 'btn-primary' : 'btn-ghost' }}">۷ روز</button>
            <button wire:click="setRange('30days')" class="btn btn-xs {{ $range === '30days' ? 'btn-primary' : 'btn-ghost' }}">۳۰ روز</button>
            <button wire:click="setRange('month')" class="btn btn-xs {{ $range === 'month' ? 'btn-primary' : 'btn-ghost' }}">این ماه</button>
        </div>
    </div>

    {{-- KPIها --}}
    <div class="kpi-strip">
        @foreach($kpis as $kpi)
            <div class="kpi-card" wire:key="kpi-{{ $kpi['key'] }}">
                <div class="kpi-head">
                    <div class="kpi-icon {{ $kpi['iconClass'] }}">{{ $kpi['icon'] }}</div>
                    <div class="kpi-title">{{ $kpi['title'] }}</div>
                </div>

                <div class="kpi-value">
                    {{ \App\Support\PersianNumber::toFa($kpi['value']) }}
                    <span class="kpi-unit">{{ $kpi['unit'] }}</span>
                </div>

                <div class="kpi-compare">
                    <span class="kpi-prev">{{ $kpi['comparison_label'] }}: {{ \App\Support\PersianNumber::toFa($kpi['previous']) }}</span>
                    @php $g = $kpi['growth']; @endphp
                    <span class="kpi-delta {{ $g['dir'] }}">
                        @if($g['dir'] === 'up')   ↑
                        @elseif($g['dir'] === 'down') ↓
                        @else → @endif
                        {{ \App\Support\PersianNumber::toFa($g['text']) }}
                    </span>
                </div>

                @if(! empty($kpi['meta']))
                    <div class="kpi-meta">
                        @foreach($kpi['meta'] as $label => $val)
                            <span><strong>{{ $label }}</strong> {{ \App\Support\PersianNumber::toFa($val) }}</span>
                        @endforeach
                    </div>
                @endif
            </div>
        @endforeach
    </div>

    {{-- ۴ جدول کوچک --}}
    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3">

        {{-- سفارشات اخیر --}}
        <div class="panel-compact">
            <div class="panel-head">
                <span>📦 سفارشات اخیر</span>
                <a href="{{ route('orders.index') }}" class="text-xs link">همه</a>
            </div>
            <table class="mini-table">
                <tbody>
                    @forelse($recentOrders as $o)
                        <tr>
                            <td class="mono text-[10px]">
                                <button onclick="Livewire.dispatch('open-order-view', { orderId: {{ $o->id }} })" class="link link-primary">
                                    #{{ \App\Support\PersianNumber::toFa($o->order_number) }}
                                </button>
                            </td>
                            <td class="text-[11px] truncate">{{ $o->customer?->name ?? '—' }}</td>
                            <td class="text-[10px] text-base-content/60">{{ \App\Support\PersianNumber::toFa(number_format((float) $o->amount)) }}</td>
                            <td><span class="badge-status {{ $o->status }} text-[9px]">{{ $o->status_label }}</span></td>
                        </tr>
                    @empty
                        <tr><td colspan="4" class="text-center py-3 text-xs text-base-content/50">نداده</td></tr>
                    @endforelse
                </tbody>
            </table>
        </div>

        {{-- پرفروش‌ها --}}
        <div class="panel-compact">
            <div class="panel-head"><span>⭐ پرفروش‌ها</span></div>
            <table class="mini-table">
                <tbody>
                    @forelse($topProducts as $p)
                        <tr>
                            <td class="text-[11px] truncate">{{ \Illuminate\Support\Str::limit($p->title, 20) }}</td>
                            <td class="text-[10px] text-center">{{ \App\Support\PersianNumber::toFa($p->c) }}</td>
                            <td class="text-[10px] text-base-content/60 text-left" dir="ltr">{{ \App\Support\PersianNumber::toFa(number_format((float) $p->total)) }}</td>
                        </tr>
                    @empty
                        <tr><td colspan="3" class="text-center py-3 text-xs text-base-content/50">نداده</td></tr>
                    @endforelse
                </tbody>
            </table>
        </div>

        {{-- کانال‌ها --}}
        <div class="panel-compact">
            <div class="panel-head"><span>🌐 کانال‌ها</span></div>
            <table class="mini-table">
                <tbody>
                    @forelse($channels as $c)
                        <tr>
                            <td class="text-[11px]">{{ $c->icon }} {{ $c->name }}</td>
                            <td class="text-[10px] text-center">{{ \App\Support\PersianNumber::toFa($c->orders_count) }}</td>
                            <td class="w-16">
                                @php $maxC = max(1, $channels->max('orders_count')); @endphp
                                <div class="bar-track"><div class="bar-fill" style="width: {{ round($c->orders_count / $maxC * 100) }}%"></div></div>
                            </td>
                        </tr>
                    @empty
                        <tr><td colspan="3" class="text-center py-3 text-xs text-base-content/50">نداده</td></tr>
                    @endforelse
                </tbody>
            </table>
        </div>

        {{-- وضعیت ارسال --}}
        <div class="panel-compact">
            <div class="panel-head"><span>🚚 وضعیت ارسال</span></div>
            <table class="mini-table">
                <tbody>
                    <tr>
                        <td class="text-[11px]">📝 ثبت سفارش</td>
                        <td class="text-[11px] text-center font-bold">{{ \App\Support\PersianNumber::toFa($statusCounts['pending']) }}</td>
                    </tr>
                    <tr>
                        <td class="text-[11px]">🔍 چک نهایی</td>
                        <td class="text-[11px] text-center font-bold">{{ \App\Support\PersianNumber::toFa($statusCounts['final-check']) }}</td>
                    </tr>
                    <tr>
                        <td class="text-[11px]">🚚 تحویل مامور</td>
                        <td class="text-[11px] text-center font-bold">{{ \App\Support\PersianNumber::toFa($statusCounts['courier']) }}</td>
                    </tr>
                    <tr class="border-t border-base-300">
                        <td class="text-[11px] font-bold">جمع</td>
                        <td class="text-[11px] text-center font-bold text-primary">{{ \App\Support\PersianNumber::toFa(array_sum($statusCounts)) }}</td>
                    </tr>
                </tbody>
            </table>
        </div>
    </div>
</div>
""")

# =========================================================
# ۸. Reports View — بازنویسی کامل با اعداد فارسی + خروجی
# =========================================================

write_file("resources/views/livewire/reports/index.blade.php", r"""
<div class="p-4 md:p-6 space-y-4">

    <div class="flex flex-wrap items-center justify-between gap-3">
        <h1 class="text-xl md:text-2xl font-bold">📊 گزارش‌ها</h1>
        <div class="flex flex-wrap gap-2">
            <div class="flex gap-1 bg-base-100 rounded-lg p-1 shadow border">
                <button wire:click="setRange('today')" class="btn btn-xs {{ $range === 'today' ? 'btn-primary' : 'btn-ghost' }}">امروز</button>
                <button wire:click="setRange('7days')" class="btn btn-xs {{ $range === '7days' ? 'btn-primary' : 'btn-ghost' }}">۷ روز</button>
                <button wire:click="setRange('30days')" class="btn btn-xs {{ $range === '30days' ? 'btn-primary' : 'btn-ghost' }}">۳۰ روز</button>
                <button wire:click="setRange('year')" class="btn btn-xs {{ $range === 'year' ? 'btn-primary' : 'btn-ghost' }}">امسال</button>
            </div>
            <button onclick="window.print()" class="btn btn-info btn-sm">🖨️ چاپ</button>
            <button onclick="exportReportPng()" class="btn btn-success btn-sm">📸 خروجی تصویر</button>
        </div>
    </div>

    <div class="relative" id="reportArea" wire:loading.class="report-loading" wire:target="setRange">
        <div wire:loading.flex wire:target="setRange"
             class="absolute inset-0 z-30 backdrop-blur-md bg-base-100/40 items-center justify-center rounded-lg">
            <div class="flex flex-col items-center gap-3">
                <span class="loading loading-spinner loading-lg text-primary"></span>
                <span class="text-sm font-bold text-primary">⏳ در حال بارگذاری...</span>
            </div>
        </div>

        {{-- KPI cards --}}
        <div class="kpi-strip mb-4">
            <div class="kpi-card">
                <div class="kpi-head"><div class="kpi-icon ic-sky">📦</div><div class="kpi-title">سفارشات</div></div>
                <div class="kpi-value">{{ \App\Support\PersianNumber::toFa(number_format($totalCount)) }}</div>
            </div>
            <div class="kpi-card">
                <div class="kpi-head"><div class="kpi-icon ic-green">💰</div><div class="kpi-title">مجموع فروش</div></div>
                <div class="kpi-value">{{ \App\Support\PersianNumber::toFa(number_format($totalAmount)) }}<span class="kpi-unit">تومان</span></div>
            </div>
            <div class="kpi-card">
                <div class="kpi-head"><div class="kpi-icon ic-amber">📊</div><div class="kpi-title">میانگین هر سفارش</div></div>
                <div class="kpi-value">{{ \App\Support\PersianNumber::toFa(number_format($avgAmount)) }}</div>
            </div>
        </div>

        {{-- نمودار روند --}}
        <div class="card bg-base-100 shadow border mb-4">
            <div class="card-body">
                <h2 class="font-bold text-base mb-4">📈 روند سفارشات</h2>
                <div style="height: 300px;"><canvas id="dailyChart"></canvas></div>
            </div>
        </div>

        <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
            <div class="card bg-base-100 shadow border">
                <div class="card-body">
                    <h2 class="font-bold text-base mb-4">📊 تفکیک وضعیت</h2>
                    <div style="height: 250px;"><canvas id="statusChart"></canvas></div>
                </div>
            </div>
            <div class="card bg-base-100 shadow border">
                <div class="card-body">
                    <h2 class="font-bold text-base mb-4">🌐 توزیع کانال‌ها</h2>
                    <div style="height: 250px;"><canvas id="channelChart"></canvas></div>
                </div>
            </div>
        </div>

        <div class="card bg-base-100 shadow border">
            <div class="card-body">
                <h2 class="font-bold text-base mb-3">🏆 مشتریان برتر</h2>
                <table class="mini-table">
                    <tbody>
                        @forelse($topCustomers as $i => $c)
                            <tr>
                                <td class="w-6 text-center font-bold text-xs">{{ \App\Support\PersianNumber::toFa($i + 1) }}</td>
                                <td class="text-xs">
                                    <button onclick="Livewire.dispatch('show-customer-profile', { phone: '{{ $c->phone }}' })"
                                            class="link link-primary font-bold">{{ $c->name ?? 'بدون نام' }}</button>
                                </td>
                                <td class="font-mono text-[10px] text-base-content/60" dir="ltr">{{ \App\Support\PersianNumber::toFa($c->phone) }}</td>
                                <td class="text-xs text-left"><span class="badge badge-primary badge-sm">{{ \App\Support\PersianNumber::toFa($c->orders_count) }}</span></td>
                            </tr>
                        @empty
                            <tr><td class="text-center py-4 text-xs text-base-content/50">داده‌ای نیست</td></tr>
                        @endforelse
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script>
let dailyChart, statusChart, channelChart;

function initCharts() {
    if (dailyChart)   { dailyChart.destroy();   dailyChart = null; }
    if (statusChart)  { statusChart.destroy();  statusChart = null; }
    if (channelChart) { channelChart.destroy(); channelChart = null; }

    Chart.defaults.font.family = 'Vazirmatn, Tahoma, sans-serif';
    Chart.defaults.font.size = 11;
    Chart.defaults.animation.duration = 400;

    const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
    const gridColor = isDark ? 'rgba(125, 211, 208, 0.1)' : 'rgba(148, 163, 184, 0.2)';
    const textColor = isDark ? '#7dd3d0' : '#475569';
    const toFa = n => String(n).replace(/\d/g, d => '۰۱۲۳۴۵۶۷۸۹'[d]);

    const dc = document.getElementById('dailyChart');
    if (dc) {
        dailyChart = new Chart(dc, {
            type: 'line',
            data: {
                labels: @json($dailyLabels),
                datasets: [
                    { label: 'تعداد', data: @json($dailyCounts),  borderColor: '#14b8a6', backgroundColor: 'rgba(20,184,166,.1)', tension: .3, fill: true, yAxisID: 'y' },
                    { label: 'مبلغ',  data: @json($dailyAmounts), borderColor: '#0ea5e9', backgroundColor: 'rgba(14,165,233,.1)', tension: .3, fill: true, yAxisID: 'y1', hidden: true }
                ]
            },
            options: { responsive: true, maintainAspectRatio: false,
                plugins: { legend: { labels: { color: textColor } },
                    tooltip: { callbacks: { label: (ctx) => ctx.dataset.label + ': ' + toFa(ctx.parsed.y) } }
                },
                scales: {
                    y:  { position: 'right', ticks: { color: textColor, callback: v => toFa(v) }, grid: { color: gridColor } },
                    y1: { position: 'left',  grid: { drawOnChartArea: false }, ticks: { color: textColor, callback: v => toFa(v) } },
                    x:  { ticks: { color: textColor, callback: v => toFa(v) }, grid: { color: gridColor } }
                }
            }
        });
    }

    const sc = document.getElementById('statusChart');
    if (sc) {
        statusChart = new Chart(sc, {
            type: 'doughnut',
            data: {
                labels: ['📝 ثبت سفارش', '🔍 چک نهایی', '🚚 تحویل مامور'],
                datasets: [{ data: @json($byStatus), backgroundColor: ['#f59e0b', '#0ea5e9', '#10b981'], borderWidth: 2, borderColor: isDark ? '#0a1414' : '#fff' }]
            },
            options: { responsive: true, maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom', labels: { color: textColor } },
                    tooltip: { callbacks: { label: (ctx) => ctx.label + ': ' + toFa(ctx.parsed) } }
                }
            }
        });
    }

    const cc = document.getElementById('channelChart');
    if (cc) {
        channelChart = new Chart(cc, {
            type: 'bar',
            data: {
                labels: @json($channelLabels),
                datasets: [{ label: 'تعداد', data: @json($channelCounts), backgroundColor: @json($channelColors), borderWidth: 1 }]
            },
            options: { responsive: true, maintainAspectRatio: false, indexAxis: 'y',
                plugins: { legend: { display: false },
                    tooltip: { callbacks: { label: (ctx) => toFa(ctx.parsed.x) } }
                },
                scales: {
                    x: { ticks: { color: textColor, callback: v => toFa(v) }, grid: { color: gridColor } },
                    y: { ticks: { color: textColor }, grid: { color: gridColor } }
                }
            }
        });
    }
}

document.addEventListener('DOMContentLoaded', initCharts);
document.addEventListener('livewire:init', () => {
    Livewire.hook('morphed', () => setTimeout(initCharts, 80));
});

function exportReportPng() {
    const area = document.getElementById('reportArea');
    if (!area) return;
    html2canvas(area, {
        scale: 2,
        backgroundColor: getComputedStyle(document.body).backgroundColor,
        useCORS: true,
        allowTaint: true,
        logging: false,
    }).then(canvas => {
        const a = document.createElement('a');
        a.download = 'report-' + Date.now() + '.png';
        a.href = canvas.toDataURL('image/png');
        a.click();
    }).catch(err => {
        console.error(err);
        alert('خطا در ساخت تصویر');
    });
}
</script>
""")

# =========================================================
# ۹. Stones Index — پیش‌نمایش با PNG
# =========================================================

write_file("resources/views/livewire/settings/stones.blade.php", r"""
<div class="p-4 md:p-6 space-y-4">

    @if (session('success'))
        <div class="alert alert-success text-sm py-2"><span>{{ session('success') }}</span></div>
    @endif

    <div class="flex flex-wrap items-center justify-between gap-3">
        <h1 class="text-xl md:text-2xl font-bold">💎 مدیریت سنگ‌ها</h1>
        <button wire:click="openForm()" class="btn btn-primary btn-sm">➕ سنگ جدید</button>
    </div>

    <div class="bg-base-100 rounded-lg shadow border p-3">
        <input type="text" wire:model.live.debounce.400ms="search"
               placeholder="🔍 جستجوی سنگ..." class="input input-bordered input-sm w-full md:w-80" />
    </div>

    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
        @forelse($stones as $stone)
            <div wire:key="stone-{{ $stone->id }}"
                 class="card bg-base-100 shadow border {{ ! $stone->is_active ? 'opacity-50' : '' }} hover:shadow-lg transition">
                <div class="card-body p-3 items-center text-center relative">

                    <button wire:click="delete({{ $stone->id }})" wire:confirm="حذف شود؟"
                            class="absolute top-1 left-1 btn btn-error btn-xs btn-circle opacity-70 hover:opacity-100 z-10">✕</button>

                    <button wire:click="toggleActive({{ $stone->id }})"
                            class="absolute top-1 right-1 btn btn-xs btn-circle z-10 {{ $stone->is_active ? 'btn-success' : 'btn-ghost' }}">
                        {{ $stone->is_active ? '✓' : '—' }}
                    </button>

                    {{-- تصویر یا آیکون --}}
                    <div class="w-16 h-16 rounded-xl bg-base-200 flex items-center justify-center overflow-hidden">
                        @if($stone->png_path)
                            <img src="{{ asset('storage/' . $stone->png_path) }}"
                                 class="w-full h-full object-contain" alt="{{ $stone->name }}"
                                 onerror="this.replaceWith(document.createTextNode('{{ $stone->icon ?? '💎' }}'))" />
                        @else
                            <span class="text-3xl">{{ $stone->icon ?? '💎' }}</span>
                        @endif
                    </div>

                    <div class="font-bold text-xs mt-2 leading-tight">{{ $stone->name }}</div>
                    @if($stone->en)
                        <div class="text-[10px] text-base-content/50" dir="ltr">{{ $stone->en }}</div>
                    @endif
                    @if($stone->origin)
                        <div class="text-[10px] text-base-content/60 mt-1">{{ $stone->flag }} {{ $stone->origin }}</div>
                    @endif

                    <button wire:click="openForm({{ $stone->id }})" class="btn btn-ghost btn-xs mt-1 w-full">✏️ ویرایش</button>
                </div>
            </div>
        @empty
            <div class="col-span-full text-center py-12 text-base-content/50">
                <div class="text-4xl mb-2">💎</div>
                سنگی نیست
            </div>
        @endforelse
    </div>

    <div>{{ $stones->links() }}</div>

    @if($showForm)
    <div class="fixed inset-0 z-[90] flex items-start justify-center p-4 overflow-y-auto">
        <div class="fixed inset-0 bg-black/60 backdrop-blur-md" wire:click="closeForm"></div>

        <div class="relative bg-base-100 rounded-2xl shadow-2xl w-full max-w-lg my-8 md:my-16 border border-base-300">
            <div class="flex items-center justify-between p-4 border-b border-base-300 bg-gradient-to-l from-primary/10 to-transparent rounded-t-2xl">
                <div class="flex items-center gap-3">
                    <div class="w-9 h-9 rounded-lg bg-gradient-to-br from-cyan-500 to-teal-600 flex items-center justify-center text-white shadow">
                        {{ $editingId ? '✏️' : '💎' }}
                    </div>
                    <h2 class="font-bold text-base">{{ $editingId ? 'ویرایش سنگ' : 'سنگ جدید' }}</h2>
                </div>
                <button wire:click="closeForm" class="btn btn-ghost btn-sm btn-circle">✕</button>
            </div>

            <div class="p-5 space-y-3 max-h-[calc(100vh-14rem)] overflow-y-auto">
                <div class="grid grid-cols-2 gap-3">
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">نام فارسی *</span></label>
                        <input type="text" wire:model="name" class="input input-bordered input-sm w-full" />
                        @error('name') <span class="text-error text-xs">{{ $message }}</span> @enderror
                    </div>
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">نام انگلیسی</span></label>
                        <input type="text" wire:model="en" dir="ltr" class="input input-bordered input-sm w-full" />
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-3">
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">اصالت</span></label>
                        <input type="text" wire:model="origin" class="input input-bordered input-sm w-full" />
                    </div>
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">کشور</span></label>
                        <select wire:model="flag" class="select select-bordered select-sm w-full">
                            @foreach($countries as $k => $v)
                                <option value="{{ $k }}">{{ $v }}</option>
                            @endforeach
                        </select>
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-3">
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">برچسب</span></label>
                        <input type="text" wire:model="balloon" class="input input-bordered input-sm w-full" />
                    </div>
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">آیکون</span></label>
                        <input type="text" wire:model="icon" class="input input-bordered input-sm w-full text-center text-2xl" />
                    </div>
                </div>

                <div class="form-control">
                    <label class="label py-1"><span class="label-text text-xs font-bold">تصویر PNG (اختیاری)</span></label>
                    <input type="file" wire:model="png" accept="image/png,image/*"
                           class="file-input file-input-bordered file-input-sm w-full" />
                    @if($png)
                        <div class="mt-2"><img src="{{ $png->temporaryUrl() }}" class="w-20 h-20 object-contain border rounded" /></div>
                    @endif
                    @error('png') <span class="text-error text-xs">{{ $message }}</span> @enderror
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
""")

print()
print("═" * 60)
print("✅ Part E کامل شد — رفع باگ + تاریخ + اعداد فارسی")
print("═" * 60)
print()
print("📌 اجرا کن:")
print("   php artisan optimize:clear")
print("   npm run build")
print("   php artisan serve")
print()