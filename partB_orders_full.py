from pathlib import Path
import textwrap

PROJECT = Path.home() / "projects" / "shopgun-v2.1"
if not PROJECT.exists():
    raise SystemExit("❌ پروژه پیدا نشد")

def write_file(rel, content):
    path = PROJECT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    existed = path.exists()
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    print(f"{'🔁' if existed else '✅'} {rel}")

print("═" * 60)
print("🚀 Part B — سفارشات کامل + Tipax + Timeline + تم تیره")
print("═" * 60)
print()

# =========================================================
# ۱. Migration — Shipment fields on orders
# =========================================================

write_file("database/migrations/2026_09_16_020001_add_shipping_to_orders.php", r"""
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::table('orders', function (Blueprint $table) {
            if (! Schema::hasColumn('orders', 'tracking_code')) {
                $table->string('tracking_code')->nullable()->index()->after('postal_code');
                $table->string('carrier')->nullable()->after('tracking_code');
                $table->string('shipping_status')->nullable()->after('carrier');
                $table->json('shipping_events')->nullable()->after('shipping_status');
                $table->timestamp('shipped_at')->nullable()->after('shipping_events');
                $table->timestamp('delivered_at')->nullable()->after('shipped_at');
            }
        });
    }

    public function down(): void
    {
        Schema::table('orders', function (Blueprint $table) {
            $table->dropColumn(['tracking_code','carrier','shipping_status','shipping_events','shipped_at','delivered_at']);
        });
    }
};
""")

# =========================================================
# ۲. به‌روزرسانی Model Order
# =========================================================

write_file("app/Models/Order.php", r"""
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Spatie\Activitylog\Models\Activity;
use Spatie\Activitylog\Models\Concerns\LogsActivity;
use Spatie\Activitylog\Support\LogOptions;

class Order extends Model
{
    use LogsActivity;

    protected $fillable = [
        'order_number', 'customer_id', 'channel_id', 'status',
        'amount', 'insurance', 'address', 'postal_code', 'phone',
        'notes', 'invoice_needed', 'meta',
        'tracking_code', 'carrier', 'shipping_status', 'shipping_events',
        'shipped_at', 'delivered_at',
    ];

    protected $casts = [
        'amount'          => 'decimal:2',
        'insurance'       => 'decimal:2',
        'invoice_needed'  => 'boolean',
        'meta'            => 'array',
        'shipping_events' => 'array',
        'shipped_at'      => 'datetime',
        'delivered_at'    => 'datetime',
    ];

    public function getActivitylogOptions(): LogOptions
    {
        return LogOptions::defaults()
            ->logOnly(['status', 'amount', 'insurance', 'address'])
            ->logOnlyDirty()
            ->useLogName('order');
    }

    public function customer(): BelongsTo { return $this->belongsTo(Customer::class); }
    public function channel(): BelongsTo  { return $this->belongsTo(Channel::class); }
    public function items(): HasMany      { return $this->hasMany(OrderItem::class)->orderBy('sort_order'); }

    public function activities()
    {
        return Activity::query()
            ->where('subject_type', $this->getMorphClass())
            ->where('subject_id', $this->getKey())
            ->latest();
    }

    public function getStatusColorAttribute(): string
    {
        return match ($this->status) {
            'pending'     => 'warning',
            'final-check' => 'info',
            'courier'     => 'success',
            default       => 'ghost',
        };
    }

    public function getStatusLabelAttribute(): string
    {
        return match ($this->status) {
            'pending'     => '📝 ثبت سفارش',
            'final-check' => '🔍 چک نهایی',
            'courier'     => '🚚 تحویل مامور',
            default       => $this->status,
        };
    }

    public function getItemsTotalAttribute(): float
    {
        return (float) $this->items->sum(fn ($i) => $i->price * $i->quantity);
    }

    public function getProductsSummaryAttribute(): string
    {
        if ($this->items->isEmpty()) return '—';
        return $this->items->map(function ($i) {
            $t = $i->title;
            if ($i->sku) $t .= " [{$i->sku}]";
            if ($i->quantity > 1) $t .= " ×{$i->quantity}";
            return $t;
        })->join(' • ');
    }

    // بررسی اینکه آیا مرسوله داره
    public function getHasShipmentAttribute(): bool
    {
        return ! empty($this->tracking_code);
    }

    // رنگ بج وضعیت مرسوله
    public function getShippingColorAttribute(): string
    {
        $s = strtolower((string) $this->shipping_status);
        return match (true) {
            str_contains($s, 'deliver') || str_contains($s, 'تحویل') => 'success',
            str_contains($s, 'transit') || str_contains($s, 'مسیر') || str_contains($s, 'ارسال') => 'info',
            str_contains($s, 'return') || str_contains($s, 'مرجوع') => 'error',
            str_contains($s, 'fail') || str_contains($s, 'ناموفق') => 'error',
            default => 'warning',
        };
    }
}
""")

# =========================================================
# ۳. Tipax Import Service
# =========================================================

write_file("app/Services/TipaxImportService.php", r"""
<?php

namespace App\Services;

use App\Models\Order;
use Illuminate\Support\Carbon;
use Illuminate\Support\Facades\Log;

class TipaxImportService
{
    /**
     * ایمپورت ردیف‌های Tipax
     * $rows = [['tracking_code' => '...', 'order_number' => '...', 'phone' => '...', 'status' => '...', 'date' => '...'], ...]
     */
    public function import(array $rows): array
    {
        $stats = ['matched' => 0, 'updated' => 0, 'created' => 0, 'unmatched' => 0, 'errors' => 0];

        foreach ($rows as $row) {
            try {
                $order = $this->findOrder($row);

                if (! $order) {
                    $stats['unmatched']++;
                    continue;
                }

                $stats['matched']++;
                $isNew = empty($order->tracking_code);

                $events   = $order->shipping_events ?? [];
                $newEvent = [
                    'status'      => $row['status'] ?? '',
                    'description' => $row['description'] ?? ($row['status'] ?? ''),
                    'date'        => $row['date'] ?? now()->format('Y/m/d H:i'),
                    'ts'          => now()->timestamp,
                ];

                // جلوگیری از تکرار
                $exists = false;
                foreach ($events as $e) {
                    if (($e['status'] ?? '') === $newEvent['status']
                        && ($e['date'] ?? '') === $newEvent['date']) {
                        $exists = true;
                        break;
                    }
                }
                if (! $exists) {
                    $events[] = $newEvent;
                }

                $order->update([
                    'tracking_code'   => $row['tracking_code'] ?? $order->tracking_code,
                    'carrier'         => 'tipax',
                    'shipping_status' => $row['status'] ?? $order->shipping_status,
                    'shipping_events' => $events,
                    'shipped_at'      => $order->shipped_at ?? now(),
                    'delivered_at'    => $this->isDelivered($row['status'] ?? '')
                        ? ($order->delivered_at ?? now())
                        : $order->delivered_at,
                ]);

                // اگه تحویل شد، وضعیت سفارش هم به «تحویل مامور» تغییر کن
                if ($this->isDelivered($row['status'] ?? '') && $order->status !== 'courier') {
                    $order->update(['status' => 'courier']);
                }

                $isNew ? $stats['created']++ : $stats['updated']++;

            } catch (\Throwable $e) {
                Log::error('TipaxImport: ' . $e->getMessage());
                $stats['errors']++;
            }
        }

        return $stats;
    }

    protected function findOrder(array $row): ?Order
    {
        // اولویت ۱: شماره سفارش
        if (! empty($row['order_number'])) {
            $o = Order::where('order_number', trim($row['order_number']))->first();
            if ($o) return $o;
        }

        // اولویت ۲: شماره تلفن
        if (! empty($row['phone'])) {
            $digits = preg_replace('/\D/', '', $row['phone']);
            if (str_starts_with($digits, '98') && strlen($digits) > 10) {
                $digits = substr($digits, 2);
            }
            if (str_starts_with($digits, '0') && strlen($digits) > 10) {
                $digits = substr($digits, 1);
            }

            if (strlen($digits) >= 10) {
                $o = Order::where('phone', 'like', "%{$digits}%")->latest('id')->first();
                if ($o) return $o;
            }
        }

        // اولویت ۳: کد رهگیری موجود
        if (! empty($row['tracking_code'])) {
            $o = Order::where('tracking_code', $row['tracking_code'])->first();
            if ($o) return $o;
        }

        return null;
    }

    protected function isDelivered(string $status): bool
    {
        $s = mb_strtolower($status);
        return str_contains($s, 'تحویل') && ! str_contains($s, 'نشد')
            || str_contains($s, 'deliver');
    }
}
""")

# =========================================================
# ۴. Tipax Import Livewire Component
# =========================================================

write_file("app/Livewire/Orders/ImportTipax.php", r"""
<?php

namespace App\Livewire\Orders;

use App\Services\TipaxImportService;
use Livewire\Component;
use Livewire\WithFileUploads;

class ImportTipax extends Component
{
    use WithFileUploads;

    public $file = null;
    public array $headers = [];
    public array $rows = [];
    public array $mapping = [];
    public ?array $result = null;

    public array $fields = [
        ''              => '— نادیده بگیر —',
        'tracking_code' => '📮 کد رهگیری',
        'order_number'  => '🔢 شماره سفارش',
        'phone'         => '📱 تلفن گیرنده',
        'receiver'      => '👤 نام گیرنده',
        'status'        => '🚦 وضعیت',
        'date'          => '📅 تاریخ',
        'description'   => '📝 توضیح',
        'city'          => '🏙️ شهر',
        'weight'        => '⚖️ وزن',
    ];

    public function updatedFile(): void
    {
        $this->validate(['file' => 'required|file|max:10240']);
        $this->result = null;

        $handle = fopen($this->file->getRealPath(), 'r');
        $bom = fread($handle, 3);
        if ($bom !== "\xEF\xBB\xBF") rewind($handle);

        $this->headers = fgetcsv($handle) ?: [];
        $this->headers = array_map(fn ($h) => trim((string) $h), $this->headers);

        $rows = [];
        while (($r = fgetcsv($handle)) !== false) {
            if (count(array_filter($r)) === 0) continue;
            $rows[] = $r;
        }
        fclose($handle);

        $this->rows = array_slice($rows, 0, 1000);

        $this->mapping = [];
        foreach ($this->headers as $i => $h) {
            $this->mapping[$i] = $this->autoDetect($h);
        }
    }

    protected function autoDetect(string $h): string
    {
        $s = mb_strtolower(trim($h));
        if (preg_match('/رهگیری|tracking|بارکد/u', $s))      return 'tracking_code';
        if (preg_match('/شماره.*سفارش|order.?num/u', $s))    return 'order_number';
        if (preg_match('/تلفن|موبایل|phone|mobile/u', $s))   return 'phone';
        if (preg_match('/گیرنده|receiver|نام/u', $s))        return 'receiver';
        if (preg_match('/وضعیت|status/u', $s))               return 'status';
        if (preg_match('/تاریخ|date|زمان/u', $s))            return 'date';
        if (preg_match('/توضیح|description|ملاحظ/u', $s))    return 'description';
        if (preg_match('/شهر|city/u', $s))                   return 'city';
        if (preg_match('/وزن|weight/u', $s))                 return 'weight';
        return '';
    }

    public function import(): void
    {
        $data = [];
        foreach ($this->rows as $row) {
            $item = [];
            foreach ($this->mapping as $idx => $field) {
                if ($field && isset($row[$idx])) {
                    $item[$field] = trim((string) $row[$idx]);
                }
            }
            if (! empty($item)) $data[] = $item;
        }

        if (empty($data)) {
            session()->flash('error', 'داده‌ای برای ایمپورت نیست');
            return;
        }

        $service = new TipaxImportService();
        $this->result = $service->import($data);

        session()->flash('success', 'ایمپورت انجام شد');
    }

    public function reset_(): void
    {
        $this->reset(['file', 'headers', 'rows', 'mapping', 'result']);
    }

    public function render()
    {
        return view('livewire.orders.import-tipax')
            ->layout('components.layouts.app');
    }
}
""")

write_file("resources/views/livewire/orders/import-tipax.blade.php", r"""
<div class="p-4 md:p-6 max-w-5xl mx-auto">

    <div class="flex items-center gap-3 mb-6">
        <a href="{{ route('orders.index') }}" class="btn btn-ghost btn-sm">→</a>
        <h1 class="text-xl md:text-2xl font-bold">📮 ایمپورت مرسولات تیپاکس</h1>
    </div>

    @if (session('error'))
        <div class="alert alert-error mb-4 text-sm"><span>{{ session('error') }}</span></div>
    @endif

    @if($result)
        <div class="alert alert-success mb-4">
            <div class="text-sm space-y-1">
                <div>✅ تطبیق: <strong>{{ $result['matched'] }}</strong></div>
                <div>🔁 بروزرسانی: <strong>{{ $result['updated'] }}</strong></div>
                <div>✨ جدید: <strong>{{ $result['created'] }}</strong></div>
                <div>⚠️ بدون تطبیق: <strong>{{ $result['unmatched'] }}</strong></div>
                @if($result['errors'])
                    <div>❌ خطا: <strong>{{ $result['errors'] }}</strong></div>
                @endif
            </div>
        </div>
        <div class="flex gap-2 mb-4">
            <a href="{{ route('orders.index') }}" class="btn btn-primary btn-sm">مشاهده سفارشات</a>
            <button wire:click="reset_" class="btn btn-ghost btn-sm">ایمپورت جدید</button>
        </div>
    @endif

    @if(! $result)
        <div class="card bg-base-100 shadow">
            <div class="card-body gap-4">

                <div class="form-control">
                    <label class="label py-1">
                        <span class="label-text font-bold text-sm">📁 فایل CSV / TSV تیپاکس</span>
                    </label>
                    <input type="file" wire:model="file" accept=".csv,.tsv,.txt"
                           class="file-input file-input-bordered file-input-sm w-full" />
                </div>

                <div wire:loading wire:target="file" class="text-xs text-info">⏳ در حال بارگذاری...</div>

                @if(! empty($headers))
                    <div class="divider my-1">نگاشت ستون‌ها</div>

                    <div class="overflow-x-auto">
                        <table class="table table-sm table-zebra">
                            <thead>
                                <tr>
                                    <th>ستون فایل</th>
                                    <th>نمونه</th>
                                    <th>فیلد مقصد</th>
                                </tr>
                            </thead>
                            <tbody>
                                @foreach($headers as $i => $h)
                                    <tr>
                                        <td class="font-bold text-xs">{{ $h }}</td>
                                        <td class="text-xs text-base-content/60">{{ $rows[0][$i] ?? '—' }}</td>
                                        <td>
                                            <select wire:model="mapping.{{ $i }}" class="select select-bordered select-xs w-full">
                                                @foreach($fields as $k => $l)
                                                    <option value="{{ $k }}">{{ $l }}</option>
                                                @endforeach
                                            </select>
                                        </td>
                                    </tr>
                                @endforeach
                            </tbody>
                        </table>
                    </div>

                    <div class="alert alert-info text-xs py-2">
                        💡 {{ count($rows) }} ردیف آماده ایمپورت — تطبیق با <strong>شماره سفارش</strong> یا <strong>تلفن</strong> انجام می‌شود
                    </div>

                    <div class="card-actions justify-end">
                        <button wire:click="import" wire:loading.attr="disabled" class="btn btn-primary btn-sm">
                            <span wire:loading.remove wire:target="import">✅ ایمپورت</span>
                            <span wire:loading wire:target="import">⏳...</span>
                        </button>
                    </div>
                @endif
            </div>
        </div>
    @endif
</div>
""")

# =========================================================
# ۵. Timeline Component (پاپ‌آپ)
# =========================================================

write_file("app/Livewire/Components/ShipmentTimeline.php", r"""
<?php

namespace App\Livewire\Components;

use App\Models\Order;
use Livewire\Component;

class ShipmentTimeline extends Component
{
    public ?int $orderId = null;
    public bool $show = false;

    protected $listeners = ['show-timeline' => 'showTimeline'];

    public function showTimeline(int $orderId): void
    {
        $this->orderId = $orderId;
        $this->show = true;
    }

    public function close(): void
    {
        $this->show = false;
        $this->orderId = null;
    }

    public function render()
    {
        $order = $this->orderId ? Order::with(['customer', 'items'])->find($this->orderId) : null;
        $events = $order ? ($order->shipping_events ?? []) : [];
        usort($events, fn ($a, $b) => ($b['ts'] ?? 0) <=> ($a['ts'] ?? 0));
        $events = array_reverse($events);

        return view('livewire.components.shipment-timeline', [
            'order'  => $order,
            'events' => $events,
        ]);
    }
}
""")

write_file("resources/views/livewire/components/shipment-timeline.blade.php", r"""
@if($show && $order)
<div class="fixed inset-0 z-[100] flex items-start justify-center p-4 overflow-y-auto"
     x-data="{ show: true }"
     x-init="$nextTick(() => show = true)">

    {{-- Backdrop --}}
    <div class="fixed inset-0 bg-black/70 backdrop-blur-md transition-opacity duration-300"
         x-show="show"
         x-transition:enter="ease-out duration-300"
         x-transition:enter-start="opacity-0"
         x-transition:enter-end="opacity-100"
         wire:click="close"></div>

    {{-- Modal --}}
    <div class="relative bg-base-100 rounded-2xl shadow-2xl w-full max-w-3xl my-8 md:my-16
                border border-primary/20 transition-all duration-300"
         x-show="show"
         x-transition:enter="ease-out duration-300"
         x-transition:enter-start="opacity-0 translate-y-8 scale-95"
         x-transition:enter-end="opacity-100 translate-y-0 scale-100">

        {{-- Header --}}
        <div class="flex items-center justify-between p-4 border-b border-base-300 bg-gradient-to-l from-primary/10 to-transparent rounded-t-2xl">
            <div class="flex items-center gap-3">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-teal-600 flex items-center justify-center text-white text-lg shadow-lg">
                    📮
                </div>
                <div>
                    <div class="font-bold text-sm">مرسوله تیپاکس</div>
                    <div class="text-xs text-base-content/60">سفارش #{{ $order->order_number }}</div>
                </div>
            </div>
            <button wire:click="close" class="btn btn-ghost btn-sm btn-circle">✕</button>
        </div>

        {{-- Body --}}
        <div class="p-5 space-y-5">

            {{-- Tracking + Recipient --}}
            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div class="bg-gradient-to-br from-cyan-500 to-teal-600 text-white rounded-xl p-4 shadow-lg">
                    <div class="text-[10px] opacity-80 mb-1">📮 کد رهگیری</div>
                    <div class="font-mono font-bold text-lg tracking-wider" dir="ltr">
                        {{ $order->tracking_code ?: '—' }}
                    </div>
                    @if($order->shipping_status)
                        <div class="inline-block mt-2 px-2 py-0.5 bg-white/20 rounded-full text-[10px] font-bold">
                            {{ $order->shipping_status }}
                        </div>
                    @endif
                </div>

                <div class="bg-base-200 rounded-xl p-4">
                    <div class="text-[10px] text-base-content/60 mb-1">👤 گیرنده</div>
                    <div class="font-bold text-sm">{{ $order->customer?->name ?? '—' }}</div>
                    <div class="text-xs text-base-content/60 font-mono mt-1" dir="ltr">{{ $order->phone }}</div>
                    <div class="text-xs text-base-content/60 mt-1 truncate">{{ $order->address }}</div>
                </div>
            </div>

            {{-- Timeline افقی --}}
            <div>
                <h3 class="font-bold text-sm mb-4 flex items-center gap-2">
                    <span class="w-2 h-2 rounded-full bg-cyan-500 animate-pulse"></span>
                    مراحل ارسال
                </h3>

                @if(empty($events))
                    <div class="text-center py-8 text-base-content/40 text-sm">
                        هنوز رویدادی ثبت نشده
                    </div>
                @else
                    {{-- Timeline افقی با اسکرول --}}
                    <div class="overflow-x-auto pb-4 -mx-5 px-5">
                        <div class="flex items-start gap-0 min-w-max">
                            @foreach(array_reverse($events) as $i => $e)
                                @php
                                    $isLast = $i === count($events) - 1;
                                    $s = mb_strtolower($e['status'] ?? '');
                                    $color = str_contains($s, 'تحویل') && ! str_contains($s, 'نشد')
                                        ? 'from-emerald-500 to-green-600'
                                        : (str_contains($s, 'مسیر') || str_contains($s, 'ارسال')
                                            ? 'from-cyan-500 to-blue-600'
                                            : 'from-amber-500 to-orange-500');
                                @endphp

                                <div class="flex items-start">
                                    {{-- Node --}}
                                    <div class="flex flex-col items-center w-40" wire:key="event-{{ $i }}">
                                        <div class="relative">
                                            <div class="w-12 h-12 rounded-full bg-gradient-to-br {{ $color }} 
                                                        flex items-center justify-center text-white text-xl shadow-lg
                                                        {{ $isLast ? 'ring-4 ring-cyan-500/30 animate-pulse' : '' }}">
                                                {{ $isLast ? '🚚' : ($i === 0 ? '📦' : '📍') }}
                                            </div>
                                            @if(! $isLast)
                                                <div class="absolute top-1/2 -right-14 w-14 h-0.5 bg-gradient-to-l from-cyan-500 to-transparent"></div>
                                            @endif
                                        </div>
                                        <div class="mt-3 text-center w-36">
                                            <div class="text-xs font-bold text-base-content/80 leading-tight">
                                                {{ \Illuminate\Support\Str::limit($e['status'] ?? '—', 30) }}
                                            </div>
                                            <div class="text-[10px] text-base-content/50 mt-1 font-mono" dir="ltr">
                                                {{ $e['date'] ?? '' }}
                                            </div>
                                            @if(! empty($e['description']) && $e['description'] !== ($e['status'] ?? ''))
                                                <div class="text-[10px] text-base-content/40 mt-1 leading-tight">
                                                    {{ \Illuminate\Support\Str::limit($e['description'], 60) }}
                                                </div>
                                            @endif
                                        </div>
                                    </div>
                                </div>
                            @endforeach
                        </div>
                    </div>
                @endif
            </div>

            {{-- لینک پیگیری --}}
            @if($order->tracking_code)
                <a href="https://tipaxco.com/tracking?code={{ $order->tracking_code }}"
                   target="_blank"
                   class="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-l from-cyan-500 to-teal-600 text-white text-xs font-bold hover:opacity-90 transition">
                    🔗 پیگیری در سایت تیپاکس
                </a>
            @endif
        </div>
    </div>
</div>
@endif
""")

# =========================================================
# ۶. کامپوننت‌های Modal استاندارد (قابل استفاده مجدد)
# =========================================================

write_file("resources/views/components/ui/modal.blade.php", r"""
@props([
    'id' => 'modal',
    'title' => 'عنوان',
    'icon' => '📋',
    'maxWidth' => '2xl',
])

@php
    $maxWidthClass = match($maxWidth) {
        'sm'  => 'max-w-md',
        'md'  => 'max-w-xl',
        'lg'  => 'max-w-2xl',
        'xl'  => 'max-w-3xl',
        '2xl' => 'max-w-4xl',
        '3xl' => 'max-w-5xl',
        default => 'max-w-2xl',
    };
@endphp

<div id="{{ $id }}" class="fixed inset-0 z-[90] hidden items-start justify-center p-4 overflow-y-auto">
    {{-- Backdrop --}}
    <div class="modal-backdrop fixed inset-0 bg-black/60 backdrop-blur-md transition-opacity duration-300 opacity-0"
         onclick="closeModal('{{ $id }}')"></div>

    {{-- Panel --}}
    <div class="modal-panel relative bg-base-100 rounded-2xl shadow-2xl w-full {{ $maxWidthClass }} my-8 md:my-16
                border border-base-300 transform transition-all duration-300 opacity-0 scale-95 translate-y-4">

        {{-- Header --}}
        <div class="flex items-center justify-between p-4 border-b border-base-300 bg-gradient-to-l from-primary/10 to-transparent rounded-t-2xl sticky top-0 z-10">
            <div class="flex items-center gap-3">
                <div class="w-9 h-9 rounded-lg bg-gradient-to-br from-cyan-500 to-teal-600 flex items-center justify-center text-white text-base shadow">
                    {{ $icon }}
                </div>
                <h2 class="font-bold text-base">{{ $title }}</h2>
            </div>
            <button type="button" onclick="closeModal('{{ $id }}')" class="btn btn-ghost btn-sm btn-circle">✕</button>
        </div>

        {{-- Body --}}
        <div class="p-5 max-h-[calc(100vh-16rem)] overflow-y-auto">
            {{ $slot }}
        </div>

        {{-- Footer --}}
        @if(isset($footer))
            <div class="p-4 border-t border-base-300 flex justify-end gap-2 rounded-b-2xl bg-base-200/50">
                {{ $footer }}
            </div>
        @endif
    </div>
</div>

@once
@push('scripts')
<script>
    function openModal(id) {
        const m = document.getElementById(id);
        if (!m) return;
        m.classList.remove('hidden');
        m.classList.add('flex');
        document.body.style.overflow = 'hidden';
        requestAnimationFrame(() => {
            m.querySelector('.modal-backdrop').classList.remove('opacity-0');
            m.querySelector('.modal-panel').classList.remove('opacity-0', 'scale-95', 'translate-y-4');
        });
    }

    function closeModal(id) {
        const m = document.getElementById(id);
        if (!m) return;
        m.querySelector('.modal-backdrop').classList.add('opacity-0');
        m.querySelector('.modal-panel').classList.add('opacity-0', 'scale-95', 'translate-y-4');
        setTimeout(() => {
            m.classList.add('hidden');
            m.classList.remove('flex');
            document.body.style.overflow = '';
        }, 250);
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal-panel').forEach(p => {
                const m = p.closest('[id]');
                if (m && ! m.classList.contains('hidden')) closeModal(m.id);
            });
        }
    });
</script>
@endpush
@endonce
""")

# =========================================================
# ۷. CSS — تم تیره فیروزه‌ای
# =========================================================

write_file("resources/css/app.css", r"""
@import url('https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css');
@import 'tailwindcss';

@plugin "daisyui" {
    themes: light --default, dark --prefersdark;
}

@source '../../vendor/laravel/framework/src/Illuminate/Pagination/resources/views/*.blade.php';
@source '../../storage/framework/views/*.php';
@source '../**/*.blade.php';
@source '../**/*.js';

@theme {
    --font-sans: 'Vazirmatn', ui-sans-serif, system-ui, sans-serif;
}

/* =========================================================
   تم تیره فیروزه‌ای — deep dark teal
   ========================================================= */

[data-theme="dark"] {
    color-scheme: dark;

    --color-base-100: #0a1414;
    --color-base-200: #0f1e1e;
    --color-base-300: #142828;
    --color-base-content: #d4f0ed;

    --color-primary: #14b8a6;
    --color-primary-content: #041414;

    --color-secondary: #0891b2;
    --color-secondary-content: #ecfeff;

    --color-accent: #22d3ee;
    --color-accent-content: #041414;

    --color-neutral: #1a2e2e;
    --color-neutral-content: #a7d5d0;

    --color-info: #06b6d4;
    --color-success: #10b981;
    --color-warning: #f59e0b;
    --color-error: #ef4444;
}

[data-theme="dark"] body {
    background:
        radial-gradient(circle at top right, rgba(20, 184, 166, 0.08), transparent 40%),
        radial-gradient(circle at bottom left, rgba(8, 145, 178, 0.06), transparent 40%),
        #0a1414;
    min-height: 100vh;
}

/* =========================================================
   جدول حرفه‌ای
   ========================================================= */

.pro-table-wrap {
    width: 100%;
    overflow-x: auto;
    -webkit-overflow-scrolling: touch;
    border-radius: 0.5rem;
    scrollbar-width: thin;
}
.pro-table-wrap::-webkit-scrollbar { height: 8px; }
.pro-table-wrap::-webkit-scrollbar-thumb {
    background: rgba(100, 116, 139, 0.35);
    border-radius: 4px;
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
    padding: 0.55rem 0.75rem;
    font-weight: 700;
    font-size: 0.72rem;
    color: #334155;
    text-align: right;
    white-space: nowrap;
    user-select: none;
}

[data-theme="dark"] .pro-table thead th {
    background: #0f1e1e;
    color: #7dd3d0;
    border-bottom-color: #14b8a6;
}

.pro-table thead th.sortable { cursor: pointer; transition: background 0.15s; }
.pro-table thead th.sortable:hover { background: #e2e8f0; }
[data-theme="dark"] .pro-table thead th.sortable:hover { background: #142828; }

.pro-table thead th .th-inner {
    display: flex;
    align-items: center;
    gap: 0.35rem;
    justify-content: flex-start;
}

.pro-table thead th .sort-icon { opacity: 0.3; font-size: 0.65rem; transition: opacity 0.15s; }
.pro-table thead th.sortable:hover .sort-icon { opacity: 0.7; }
.pro-table thead th.sort-active .sort-icon { opacity: 1; color: #14b8a6; }

.pro-table tbody td {
    padding: 0.55rem 0.75rem;
    border-bottom: 1px solid #e2e8f0;
    white-space: nowrap;
    vertical-align: middle;
    background: #fff;
    color: #1e293b;
}

[data-theme="dark"] .pro-table tbody td {
    background: #0a1414;
    color: #d4f0ed;
    border-bottom-color: #142828;
}

.pro-table tbody tr:hover td { background: #f0f9ff; }
[data-theme="dark"] .pro-table tbody tr:hover td { background: #0f1e1e; }

.pro-table tbody tr.selected td { background: #cffafe; }
[data-theme="dark"] .pro-table tbody tr.selected td { background: #142828; }

.pro-table tbody td.cell-actions {
    position: sticky;
    left: 0;
    z-index: 5;
    background: inherit;
    border-left: 1px solid #e2e8f0;
}

[data-theme="dark"] .pro-table tbody td.cell-actions { border-left-color: #142828; }

/* Badge وضعیت */
.badge-status {
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
.badge-status.final-check { background: linear-gradient(135deg, #06b6d4, #0891b2); }
.badge-status.courier     { background: linear-gradient(135deg, #10b981, #059669); }

/* =========================================================
   کارت‌های آماری مینیمال
   ========================================================= */

.stat-strip {
    display: flex;
    gap: 0.75rem;
    overflow-x: auto;
    padding: 0.25rem 0.25rem 0.75rem;
    scroll-snap-type: x mandatory;
    scrollbar-width: thin;
}
.stat-strip::-webkit-scrollbar { height: 6px; }
.stat-strip::-webkit-scrollbar-thumb { background: rgba(100, 116, 139, 0.25); border-radius: 3px; }

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

[data-theme="dark"] .stat-card-mini {
    background: linear-gradient(135deg, #0f1e1e, #0a1414);
    border-color: #142828;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.stat-card-mini:hover {
    box-shadow: 0 4px 12px rgba(20, 184, 166, 0.15);
    transform: translateY(-2px);
}

.stat-card-mini .stat-head {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 0.4rem;
}

.stat-card-mini .stat-icon {
    width: 32px; height: 32px;
    border-radius: 8px;
    display: flex; align-items: center; justify-content: center;
    font-size: 1rem;
}

.stat-card-mini .stat-label {
    font-size: 0.7rem; font-weight: 600;
    color: #64748b; letter-spacing: 0.02em;
}

[data-theme="dark"] .stat-card-mini .stat-label { color: #7dd3d0; }

.stat-card-mini .stat-value {
    font-size: 1.4rem; font-weight: 800;
    color: #0f172a; line-height: 1.2;
    font-variant-numeric: tabular-nums;
}

[data-theme="dark"] .stat-card-mini .stat-value { color: #d4f0ed; }

.stat-card-mini .stat-delta {
    display: inline-flex; align-items: center; gap: 0.25rem;
    margin-top: 0.4rem; padding: 0.15rem 0.5rem;
    border-radius: 9999px; font-size: 0.65rem; font-weight: 700;
}
.stat-card-mini .stat-delta.up   { background: #dcfce7; color: #15803d; }
.stat-card-mini .stat-delta.down { background: #fee2e2; color: #b91c1c; }
.stat-card-mini .stat-delta.flat { background: #f1f5f9; color: #475569; }

[data-theme="dark"] .stat-card-mini .stat-delta.up   { background: rgba(16,185,129,.2); color: #6ee7b7; }
[data-theme="dark"] .stat-card-mini .stat-delta.down { background: rgba(239,68,68,.2); color: #fca5a5; }

.ic-blue   { background: #dbeafe; color: #1d4ed8; }
.ic-green  { background: #dcfce7; color: #15803d; }
.ic-amber  { background: #fef3c7; color: #b45309; }
.ic-rose   { background: #ffe4e6; color: #be123c; }
.ic-indigo { background: #e0e7ff; color: #4338ca; }
.ic-sky    { background: #e0f2fe; color: #0369a1; }
.ic-violet { background: #ede9fe; color: #6d28d9; }

[data-theme="dark"] .ic-blue   { background: rgba(59,130,246,.2); color: #93c5fd; }
[data-theme="dark"] .ic-green  { background: rgba(16,185,129,.2); color: #6ee7b7; }
[data-theme="dark"] .ic-amber  { background: rgba(245,158,11,.2); color: #fcd34d; }
[data-theme="dark"] .ic-rose   { background: rgba(244,63,94,.2); color: #fda4af; }
[data-theme="dark"] .ic-indigo { background: rgba(99,102,241,.2); color: #a5b4fc; }
[data-theme="dark"] .ic-sky    { background: rgba(6,182,212,.2); color: #67e8f9; }
[data-theme="dark"] .ic-violet { background: rgba(139,92,246,.2); color: #c4b5fd; }

/* =========================================================
   موبایل
   ========================================================= */

@media (max-width: 768px) {
    .card-body { padding: 1rem !important; }
    .stat-card-mini { flex: 0 0 180px; padding: 0.7rem 0.85rem; }
    .stat-card-mini .stat-value { font-size: 1.2rem; }
    .pro-table { font-size: 0.75rem; }
    .pro-table thead th, .pro-table tbody td { padding: 0.45rem 0.6rem; }
}

/* Animations */
@keyframes pulse-ring {
    0% { box-shadow: 0 0 0 0 rgba(20, 184, 166, 0.5); }
    70% { box-shadow: 0 0 0 12px rgba(20, 184, 166, 0); }
    100% { box-shadow: 0 0 0 0 rgba(20, 184, 166, 0); }
}

/* Modal scroll lock */
body:has(.modal-panel:not(.hidden)) { overflow: hidden; }
""")

# =========================================================
# ۸. Layout — افزودن @stack('scripts')
# =========================================================

write_file("resources/views/components/layouts/app.blade.php", r"""
<!DOCTYPE html>
<html lang="fa" dir="rtl" data-theme="light" id="appHtml">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>ShopGun — شاپگان</title>
    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">
    <script>
        // تم از localStorage
        (function() {
            const t = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', t);
        })();
    </script>
    @vite(['resources/css/app.css', 'resources/js/app.js'])
    @livewireStyles
</head>
<body class="min-h-screen bg-base-200 font-sans text-base-content">

    @auth
        <livewire:global-search />
        <livewire:components.shipment-timeline />
    @endauth

    <div class="drawer lg:drawer-open">
        <input id="main-drawer" type="checkbox" class="drawer-toggle" />

        <div class="drawer-content flex flex-col min-h-screen">
            <header class="navbar bg-base-100 border-b border-base-300 sticky top-0 z-30 shadow-sm">
                <div class="flex-none lg:hidden">
                    <label for="main-drawer" class="btn btn-square btn-ghost">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                        </svg>
                    </label>
                </div>

                <div class="flex-1 px-3 flex items-center gap-3">
                    <span class="text-lg font-extrabold text-primary">ShopGun</span>
                    <span class="text-xs text-base-content/60">v2.1</span>
                    <button onclick="window.dispatchEvent(new KeyboardEvent('keydown', {key: 'k', ctrlKey: true}))"
                            class="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-base-200 hover:bg-base-300 text-xs text-base-content/60 border border-base-300">
                        <span>🔍 جستجو</span>
                        <kbd class="kbd kbd-xs">Ctrl+K</kbd>
                    </button>
                </div>

                <div class="flex-none gap-2 items-center flex">
                    <button onclick="toggleTheme()" class="btn btn-ghost btn-sm btn-circle" title="تغییر تم">
                        <span id="themeIcon">🌙</span>
                    </button>

                    @auth
                        <livewire:notification-center />
                    @endauth

                    <div class="dropdown dropdown-end">
                        <div tabindex="0" role="button" class="btn btn-ghost btn-sm gap-2">
                            <div class="avatar placeholder">
                                <div class="bg-primary text-primary-content rounded-full w-8">
                                    <span class="text-xs font-bold">{{ mb_substr(Auth::user()->name ?? '؟', 0, 1) }}</span>
                                </div>
                            </div>
                            <span class="hidden sm:inline text-xs">{{ Auth::user()->name ?? 'کاربر' }}</span>
                        </div>
                        <ul tabindex="0" class="dropdown-content menu bg-base-100 rounded-box z-[1] w-56 p-2 shadow">
                            <li><a href="{{ route('settings.index') }}">⚙️ تنظیمات</a></li>
                            <li><a href="{{ route('activity-log') }}">📜 لاگ فعالیت‌ها</a></li>
                            <li>
                                <form method="POST" action="{{ route('logout') }}">
                                    @csrf
                                    <button type="submit" class="w-full text-right">🚪 خروج</button>
                                </form>
                            </li>
                        </ul>
                    </div>
                </div>
            </header>

            <main class="flex-1">{{ $slot }}</main>

            <footer class="footer footer-center p-4 bg-base-100 border-t border-base-300 text-xs text-base-content/60">
                <aside><p>ShopGun V2.1 — گروه هنری اقاقیا — نیشابور</p></aside>
            </footer>
        </div>

        <div class="drawer-side z-40">
            <label for="main-drawer" class="drawer-overlay"></label>
            <aside class="w-64 min-h-full bg-base-100 border-l border-base-300 flex flex-col">
                <div class="p-5 border-b border-base-300">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-teal-600 text-white flex items-center justify-center font-extrabold shadow-lg">S</div>
                        <div>
                            <div class="font-extrabold text-base">شاپگان</div>
                            <div class="text-[10px] text-base-content/50">ShopGun v2.1</div>
                        </div>
                    </div>
                </div>

                <ul class="menu menu-md gap-1 p-3 flex-1">
                    <li><a href="{{ route('dashboard') }}" class="{{ request()->routeIs('dashboard') ? 'active' : '' }}"><span class="text-lg">🏠</span><span>داشبورد</span></a></li>
                    <li><a href="{{ route('orders.index') }}" class="{{ request()->routeIs('orders.*') ? 'active' : '' }}"><span class="text-lg">📦</span><span>سفارشات</span></a></li>
                    <li><a href="{{ route('customers.index') }}" class="{{ request()->routeIs('customers.*') ? 'active' : '' }}"><span class="text-lg">👥</span><span>مشتریان</span></a></li>
                    <li><a href="{{ route('certificates.index') }}" class="{{ request()->routeIs('certificates.*') ? 'active' : '' }}"><span class="text-lg">💎</span><span>شناسنامه‌ها</span></a></li>
                    <li><a href="{{ route('reports.index') }}" class="{{ request()->routeIs('reports.*') ? 'active' : '' }}"><span class="text-lg">📊</span><span>گزارش‌ها</span></a></li>
                    <li><a href="{{ route('activity-log') }}" class="{{ request()->routeIs('activity-log') ? 'active' : '' }}"><span class="text-lg">📜</span><span>لاگ</span></a></li>
                    <li><a href="{{ route('settings.index') }}" class="{{ request()->routeIs('settings.*') ? 'active' : '' }}"><span class="text-lg">⚙️</span><span>تنظیمات</span></a></li>
                </ul>
            </aside>
        </div>
    </div>

    <script>
        function toggleTheme() {
            const html = document.documentElement;
            const cur = html.getAttribute('data-theme') || 'light';
            const next = cur === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', next);
            localStorage.setItem('theme', next);
            document.getElementById('themeIcon').textContent = next === 'dark' ? '☀️' : '🌙';
        }
        document.addEventListener('DOMContentLoaded', () => {
            const cur = document.documentElement.getAttribute('data-theme');
            const icon = document.getElementById('themeIcon');
            if (icon) icon.textContent = cur === 'dark' ? '☀️' : '🌙';
        });
    </script>

    @livewireScripts
    @stack('scripts')
</body>
</html>
""")

# =========================================================
# ۹. Order Form به صورت Modal
# =========================================================

write_file("app/Livewire/Orders/FormModal.php", r"""
<?php

namespace App\Livewire\Orders;

use App\Models\Channel;
use App\Models\Customer;
use App\Models\Order;
use Livewire\Attributes\On;
use Livewire\Component;

class FormModal extends Component
{
    public bool $show = false;
    public ?int $orderId = null;

    public string $phone = '';
    public string $customerName = '';
    public string $postalCode = '';
    public string $address = '';
    public string $insurance = '0';
    public string $status = 'pending';
    public ?int $channelId = null;
    public bool $invoiceNeeded = false;
    public string $notes = '';
    public array $items = [];

    public bool $customerFound = false;

    protected $listeners = [
        'phone-selected' => 'onPhoneSelected',
        'sku-selected'   => 'onSkuSelected',
        'open-order-form' => 'open',
    ];

    public function open(?int $orderId = null): void
    {
        $this->resetForm();
        $this->orderId = $orderId;

        if ($orderId) {
            $order = Order::with('items')->find($orderId);
            if ($order) {
                $this->phone        = $order->phone ?? '';
                $this->customerName = $order->customer?->name ?? '';
                $this->postalCode   = $order->postal_code ?? '';
                $this->address      = $order->address ?? '';
                $this->insurance    = (string) ($order->insurance ?? '0');
                $this->status       = $order->status ?? 'pending';
                $this->channelId    = $order->channel_id;
                $this->invoiceNeeded = (bool) $order->invoice_needed;
                $this->notes        = $order->notes ?? '';

                $this->items = $order->items->map(fn ($i) => [
                    'title' => $i->title,
                    'sku'   => $i->sku ?? '',
                    'price' => (string) $i->price,
                    'qty'   => $i->quantity,
                    'cert'  => (bool) $i->cert_needed,
                ])->all();
            }
        }

        if (empty($this->items)) $this->addItem();

        $this->show = true;
    }

    public function close(): void
    {
        $this->show = false;
        $this->resetForm();
    }

    protected function resetForm(): void
    {
        $this->orderId       = null;
        $this->phone         = '';
        $this->customerName  = '';
        $this->postalCode    = '';
        $this->address       = '';
        $this->insurance     = '0';
        $this->status        = 'pending';
        $this->channelId     = null;
        $this->invoiceNeeded = false;
        $this->notes         = '';
        $this->items         = [];
        $this->customerFound = false;
    }

    public function addItem(): void
    {
        $this->items[] = ['title' => '', 'sku' => '', 'price' => '', 'qty' => 1, 'cert' => true];
    }

    public function removeItem(int $i): void
    {
        unset($this->items[$i]);
        $this->items = array_values($this->items);
        $this->recalc();
    }

    #[On('phone-typed')]
    public function onPhoneTyped(string $value): void
    {
        $this->phone = $value;
    }

    #[On('phone-selected')]
    public function onPhoneSelected(string $phone, string $name = '', string $address = '', string $postal = ''): void
    {
        $this->phone        = $phone;
        $this->customerName = $name;
        $this->address      = $address;
        $this->postalCode   = $postal;
    }

    #[On('sku-selected')]
    public function onSkuSelected(string $sku, string $title = '', float $price = 0): void
    {
        foreach (array_reverse(array_keys($this->items)) as $i) {
            if (empty($this->items[$i]['sku'])) {
                $this->items[$i]['sku']   = $sku;
                $this->items[$i]['title'] = $title;
                $this->items[$i]['price'] = (string) $price;
                $this->recalc();
                return;
            }
        }
        $this->items[] = ['title' => $title, 'sku' => $sku, 'price' => (string) $price, 'qty' => 1, 'cert' => true];
        $this->recalc();
    }

    public function updatedItems(): void { $this->recalc(); }

    public function recalc(): void
    {
        $total = 0;
        foreach ($this->items as $it) {
            $total += ((float) ($it['price'] ?? 0)) * ((int) ($it['qty'] ?? 1));
        }
        $this->insurance = (string) round($total / 100000);
    }

    protected function normalizePhone(string $p): string
    {
        $d = preg_replace('/\D/', '', $p);
        if (str_starts_with($d, '0098')) $d = substr($d, 4);
        elseif (str_starts_with($d, '98') && strlen($d) > 10) $d = substr($d, 2);
        if (str_starts_with($d, '0') && strlen($d) > 10) $d = substr($d, 1);
        return $d;
    }

    public function save()
    {
        $this->validate([
            'phone' => 'required|min:10',
            'items' => 'array',
        ], ['phone.required' => 'شماره تلفن الزامی است']);

        $normalized = $this->normalizePhone($this->phone);

        $customer = Customer::firstOrCreate(
            ['phone' => $normalized],
            ['name' => $this->customerName ?: 'بدون نام']
        );

        $customer->update([
            'name'        => $this->customerName ?: $customer->name,
            'postal_code' => $this->postalCode ?: $customer->postal_code,
            'address'     => $this->address ?: $customer->address,
        ]);

        $amount = 0;
        foreach ($this->items as $it) {
            $amount += ((float) ($it['price'] ?? 0)) * ((int) ($it['qty'] ?? 1));
        }

        $data = [
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
        ];

        if ($this->orderId) {
            $order = Order::findOrFail($this->orderId);
            $order->update($data);
            $order->items()->delete();
            $msg = "سفارش #{$order->order_number} ویرایش شد";
        } else {
            $last = (int) Order::max('order_number');
            $data['order_number'] = (string) max($last + 1, 317401);
            $order = Order::create($data);
            $msg = "سفارش #{$order->order_number} ثبت شد";
        }

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

        session()->flash('success', $msg);
        $this->close();
        $this->dispatch('order-saved');
    }

    public function render()
    {
        return view('livewire.orders.form-modal', [
            'channels' => Channel::where('is_active', true)->orderBy('sort_order')->get(),
        ]);
    }
}
""")

write_file("resources/views/livewire/orders/form-modal.blade.php", r"""
@if($show)
<div class="fixed inset-0 z-[80] flex items-start justify-center p-4 overflow-y-auto"
     x-data="{ show: true }"
     x-init="$nextTick(() => show = true)">

    <div class="fixed inset-0 bg-black/60 backdrop-blur-md transition-opacity duration-300"
         x-show="show"
         x-transition:enter="ease-out duration-300"
         x-transition:enter-start="opacity-0"
         x-transition:enter-end="opacity-100"
         wire:click="close"></div>

    <div class="relative bg-base-100 rounded-2xl shadow-2xl w-full max-w-3xl my-8 md:my-16
                border border-base-300 transition-all duration-300"
         x-show="show"
         x-transition:enter="ease-out duration-300"
         x-transition:enter-start="opacity-0 translate-y-8 scale-95"
         x-transition:enter-end="opacity-100 translate-y-0 scale-100">

        <div class="flex items-center justify-between p-4 border-b border-base-300 bg-gradient-to-l from-primary/10 to-transparent rounded-t-2xl sticky top-0 z-10 bg-base-100/95 backdrop-blur">
            <div class="flex items-center gap-3">
                <div class="w-9 h-9 rounded-lg bg-gradient-to-br from-cyan-500 to-teal-600 flex items-center justify-center text-white shadow">
                    {{ $orderId ? '✏️' : '📦' }}
                </div>
                <h2 class="font-bold text-base">{{ $orderId ? 'ویرایش سفارش' : 'سفارش جدید' }}</h2>
            </div>
            <button wire:click="close" class="btn btn-ghost btn-sm btn-circle">✕</button>
        </div>

        <div class="p-5 space-y-4 max-h-[calc(100vh-14rem)] overflow-y-auto">

            {{-- تلفن --}}
            <div>
                <label class="label pb-1"><span class="label-text font-bold text-sm">📱 تلفن <span class="text-error">*</span></span></label>
                <livewire:components.phone-search wire:model="phone" :key="'phone-'.$orderId" />
                @error('phone') <span class="text-error text-xs">{{ $message }}</span> @enderror
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                    <label class="label pb-1"><span class="label-text text-xs font-bold">👤 نام</span></label>
                    <input type="text" wire:model="customerName" class="input input-bordered input-sm w-full" />
                </div>
                <div>
                    <label class="label pb-1"><span class="label-text text-xs font-bold">📮 کدپستی</span></label>
                    <input type="text" wire:model="postalCode" dir="ltr" class="input input-bordered input-sm w-full font-mono" />
                </div>
            </div>

            <div>
                <label class="label pb-1"><span class="label-text text-xs font-bold">📍 آدرس</span></label>
                <textarea wire:model="address" class="textarea textarea-bordered textarea-sm w-full" rows="2"></textarea>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                <div>
                    <label class="label pb-1"><span class="label-text text-xs font-bold">📊 وضعیت</span></label>
                    <div class="flex flex-wrap gap-1">
                        @foreach(['pending' => '📝 ثبت', 'final-check' => '🔍 چک', 'courier' => '🚚 تحویل'] as $k => $v)
                            <button type="button" wire:click="$set('status', '{{ $k }}')"
                                    class="btn btn-xs {{ $status === $k ? 'btn-primary' : 'btn-outline' }}">{{ $v }}</button>
                        @endforeach
                    </div>
                </div>
                <div>
                    <label class="label pb-1"><span class="label-text text-xs font-bold">🌐 کانال</span></label>
                    <div class="flex flex-wrap gap-1">
                        @foreach($channels as $c)
                            <button type="button" wire:click="$set('channelId', {{ $c->id }})"
                                    class="btn btn-xs {{ $channelId === $c->id ? 'btn-primary' : 'btn-outline' }}">
                                {{ $c->icon }}
                            </button>
                        @endforeach
                    </div>
                </div>
            </div>

            <div class="grid grid-cols-2 gap-3">
                <div>
                    <label class="label pb-1"><span class="label-text text-xs font-bold">💰 بیمه</span></label>
                    <input type="text" wire:model="insurance" dir="ltr" class="input input-bordered input-sm w-full font-mono" />
                </div>
                <label class="label cursor-pointer justify-start gap-2 pt-5">
                    <input type="checkbox" wire:model="invoiceNeeded" class="checkbox checkbox-sm checkbox-primary" />
                    <span class="label-text text-xs font-bold">📄 فاکتور</span>
                </label>
            </div>

            <div class="divider my-1 text-xs">🛍️ محصولات</div>

            <div class="space-y-2">
                @foreach($items as $idx => $it)
                    <div class="border border-base-300 rounded-lg p-2 bg-base-200/30" wire:key="item-{{ $idx }}">
                        <div class="grid grid-cols-12 gap-2 items-end">
                            <div class="col-span-6 md:col-span-3">
                                <input type="text" wire:model="items.{{ $idx }}.sku" dir="ltr"
                                       placeholder="SKU" class="input input-bordered input-xs w-full font-mono" />
                            </div>
                            <div class="col-span-6 md:col-span-4">
                                <input type="text" wire:model="items.{{ $idx }}.title"
                                       placeholder="عنوان" class="input input-bordered input-xs w-full" />
                            </div>
                            <div class="col-span-6 md:col-span-2">
                                <input type="number" wire:model.live.debounce.500ms="items.{{ $idx }}.price"
                                       dir="ltr" placeholder="قیمت" class="input input-bordered input-xs w-full font-mono" />
                            </div>
                            <div class="col-span-3 md:col-span-1">
                                <input type="number" wire:model.live="items.{{ $idx }}.qty" min="1"
                                       class="input input-bordered input-xs w-full text-center" />
                            </div>
                            <div class="col-span-2 md:col-span-1 flex flex-col items-center">
                                <input type="checkbox" wire:model="items.{{ $idx }}.cert" class="checkbox checkbox-xs" title="شناسنامه" />
                            </div>
                            <div class="col-span-1">
                                <button type="button" wire:click="removeItem({{ $idx }})"
                                        class="btn btn-error btn-xs btn-circle">✕</button>
                            </div>
                        </div>
                    </div>
                @endforeach
            </div>

            <button type="button" wire:click="addItem" class="btn btn-outline btn-xs">➕ افزودن محصول</button>

            <div>
                <label class="label pb-1"><span class="label-text text-xs font-bold">📝 یادداشت</span></label>
                <textarea wire:model="notes" class="textarea textarea-bordered textarea-sm w-full" rows="2"></textarea>
            </div>
        </div>

        <div class="p-4 border-t border-base-300 flex justify-end gap-2 rounded-b-2xl bg-base-200/50">
            <button wire:click="close" class="btn btn-ghost btn-sm">انصراف</button>
            <button wire:click="save" wire:loading.attr="disabled" class="btn btn-primary btn-sm">
                <span wire:loading.remove wire:target="save">✅ ذخیره</span>
                <span wire:loading wire:target="save">⏳...</span>
            </button>
        </div>
    </div>
</div>
@endif
""")

# =========================================================
# ۱۰. Orders Index — بازنویسی کامل با دکمه‌های new
# =========================================================

write_file("resources/views/livewire/orders/index.blade.php", r"""
<div class="p-4 md:p-6 space-y-4">

    @if (session('success'))
        <div class="alert alert-success text-sm py-2"><span>{{ session('success') }}</span></div>
    @endif

    <div class="flex flex-wrap items-center justify-between gap-3">
        <h1 class="text-xl md:text-2xl font-bold">📦 سفارشات</h1>
        <div class="flex flex-wrap gap-2">
            <a href="{{ route('orders.import-tipax') }}" class="btn btn-outline btn-sm">📮 تیپاکس</a>
            <button wire:click="$dispatch('open-order-form')" class="btn btn-primary btn-sm">➕ سفارش جدید</button>
        </div>
    </div>

    {{-- جستجو و فیلتر --}}
    <div class="bg-base-100 rounded-lg shadow border p-3">
        <div class="grid grid-cols-1 md:grid-cols-4 gap-2">
            <input type="text" wire:model.live.debounce.400ms="search"
                   placeholder="🔍 جستجو..." class="input input-bordered input-sm w-full" />

            <select wire:model.live="statusFilter" class="select select-bordered select-sm w-full">
                <option value="">📊 همه وضعیت‌ها</option>
                <option value="pending">📝 ثبت سفارش</option>
                <option value="final-check">🔍 چک نهایی</option>
                <option value="courier">🚚 تحویل مامور</option>
            </select>

            <select wire:model.live="channelFilter" class="select select-bordered select-sm w-full">
                <option value="">🌐 همه کانال‌ها</option>
                @foreach($channels as $c)
                    <option value="{{ $c->id }}">{{ $c->icon }} {{ $c->name }}</option>
                @endforeach
            </select>

            @if($search || $statusFilter || $channelFilter)
                <button wire:click="clearFilters" class="btn btn-ghost btn-sm">✕ پاک کردن</button>
            @else
                <div></div>
            @endif
        </div>
    </div>

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
                            <input type="checkbox" class="checkbox checkbox-xs" wire:click="selectAllVisible" />
                        </th>
                        <th class="sortable {{ $sortField === 'order_number' ? 'sort-active' : '' }}" wire:click="sortBy('order_number')">
                            <div class="th-inner">
                                <span class="sort-icon">{{ $sortField === 'order_number' ? ($sortDir === 'asc' ? '▲' : '▼') : '⇅' }}</span>
                                <span>شماره</span>
                            </div>
                        </th>
                        <th>مشتری</th>
                        <th>تلفن</th>
                        <th>محصولات</th>
                        <th class="sortable {{ $sortField === 'status' ? 'sort-active' : '' }}" wire:click="sortBy('status')">
                            <div class="th-inner">
                                <span class="sort-icon">{{ $sortField === 'status' ? ($sortDir === 'asc' ? '▲' : '▼') : '⇅' }}</span>
                                <span>وضعیت</span>
                            </div>
                        </th>
                        <th>کانال</th>
                        <th class="sortable {{ $sortField === 'insurance' ? 'sort-active' : '' }}" wire:click="sortBy('insurance')">
                            <div class="th-inner">
                                <span class="sort-icon">{{ $sortField === 'insurance' ? ($sortDir === 'asc' ? '▲' : '▼') : '⇅' }}</span>
                                <span>بیمه</span>
                            </div>
                        </th>
                        <th>مرسوله</th>
                        <th class="sortable {{ $sortField === 'created_at' ? 'sort-active' : '' }}" wire:click="sortBy('created_at')">
                            <div class="th-inner">
                                <span class="sort-icon">{{ $sortField === 'created_at' ? ($sortDir === 'asc' ? '▲' : '▼') : '⇅' }}</span>
                                <span>تاریخ</span>
                            </div>
                        </th>
                        <th>عملیات</th>
                    </tr>
                </thead>
                <tbody>
                    @forelse($orders as $order)
                        <tr wire:key="order-{{ $order->id }}" class="{{ in_array($order->id, $selected) ? 'selected' : '' }}">
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
                                @else — @endif
                            </td>
                            <td class="font-mono text-xs" dir="ltr">{{ $order->phone ?? '—' }}</td>
                            <td class="text-xs">{{ \Illuminate\Support\Str::limit($order->products_summary, 40) }}</td>
                            <td><span class="badge-status {{ $order->status }}">{{ $order->status_label }}</span></td>
                            <td class="text-xs">
                                @if($order->channel)
                                    {{ $order->channel->icon }} {{ $order->channel->name }}
                                @else — @endif
                            </td>
                            <td>{{ number_format((float) $order->insurance) }}</td>
                            <td>
                                @if($order->has_shipment)
                                    <button wire:click="$dispatch('show-timeline', { orderId: {{ $order->id }} })"
                                            class="badge badge-{{ $order->shipping_color }} badge-sm gap-1 cursor-pointer hover:scale-105 transition">
                                        📮 مشاهده
                                    </button>
                                @else
                                    <span class="text-xs text-base-content/40">—</span>
                                @endif
                            </td>
                            <td class="text-xs">{{ $order->created_at?->format('Y/m/d H:i') }}</td>
                            <td class="cell-actions">
                                <div class="flex gap-1">
                                    <a href="{{ route('orders.show', $order) }}" class="btn btn-ghost btn-xs" title="مشاهده">👁️</a>
                                    <button wire:click="$dispatch('open-order-form', { orderId: {{ $order->id }} })"
                                            class="btn btn-ghost btn-xs" title="ویرایش">✏️</button>
                                    <a href="{{ route('orders.print-label', $order) }}" target="_blank" class="btn btn-ghost btn-xs" title="برچسب">🏷️</a>
                                    <button wire:click="deleteOrder({{ $order->id }})" wire:confirm="حذف شود؟"
                                            class="btn btn-ghost btn-xs text-error" title="حذف">🗑️</button>
                                </div>
                            </td>
                        </tr>
                    @empty
                        <tr>
                            <td colspan="11" class="text-center py-12 text-base-content/50">
                                <div class="text-4xl mb-2">📦</div>
                                سفارشی نیست
                            </td>
                        </tr>
                    @endforelse
                </tbody>
            </table>
        </div>
    </div>

    <div>{{ $orders->links() }}</div>

    {{-- Modal فرم --}}
    <livewire:orders.form-modal />
</div>
""")

# =========================================================
# ۱۱. Routes جدید
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
use App\Livewire\Orders\ImportTipax;
use App\Livewire\Customers\Index as CustomersIndex;
use App\Livewire\Customers\Create as CustomersCreate;
use App\Livewire\Customers\Show as CustomersShow;
use App\Livewire\Customers\Edit as CustomersEdit;
use App\Livewire\Certificates\Index as CertificatesIndex;
use App\Livewire\Certificates\Create as CertificatesCreate;
use App\Livewire\Certificates\Show as CertificatesShow;
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
        Route::get('/import-tipax', ImportTipax::class)->name('import-tipax');
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
        Route::get('/create', CertificatesCreate::class)->name('create');
        Route::get('/{certificate}', CertificatesShow::class)->name('show');
    });

    Route::get('/reports', ReportsIndex::class)->name('reports.index');
    Route::get('/settings', SettingsIndex::class)->name('settings.index');
});
""")

print()
print("═" * 60)
print("✅ Part B کامل شد")
print("═" * 60)
print()
print("📌 اجرا کن:")
print("   php artisan optimize:clear")
print("   php artisan migrate")
print("   npm run build")
print("   php artisan serve --host=0.0.0.0 --port=8000")
print()
