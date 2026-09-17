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
print("🚀 مرحله A — سفارشات پیشرفته")
print("═" * 60)
print()

# =========================================================
# ۱. Model: OrderItem
# =========================================================

write_file("app/Models/OrderItem.php", r"""
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class OrderItem extends Model
{
    protected $fillable = [
        'order_id',
        'title',
        'sku',
        'price',
        'quantity',
        'cert_needed',
        'sort_order',
    ];

    protected $casts = [
        'price'       => 'decimal:2',
        'quantity'    => 'integer',
        'cert_needed' => 'boolean',
        'sort_order'  => 'integer',
    ];

    public function order(): BelongsTo
    {
        return $this->belongsTo(Order::class);
    }
}
""")

# =========================================================
# ۲. Migration: OrderItems
# =========================================================

write_file("database/migrations/2026_09_16_010001_create_order_items_table.php", r"""
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('order_items', function (Blueprint $table) {
            $table->id();
            $table->foreignId('order_id')->constrained('orders')->cascadeOnDelete();
            $table->string('title');
            $table->string('sku')->nullable()->index();
            $table->decimal('price', 15, 2)->default(0);
            $table->integer('quantity')->default(1);
            $table->boolean('cert_needed')->default(true);
            $table->integer('sort_order')->default(0);
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('order_items');
    }
};
""")

# =========================================================
# ۳. به‌روزرسانی Model Order
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
    ];

    protected $casts = [
        'amount'         => 'decimal:2',
        'insurance'      => 'decimal:2',
        'invoice_needed' => 'boolean',
        'meta'           => 'array',
    ];

    public function getActivitylogOptions(): LogOptions
    {
        return LogOptions::defaults()
            ->logOnly(['status', 'amount', 'insurance', 'address'])
            ->logOnlyDirty()
            ->useLogName('order');
    }

    public function customer(): BelongsTo
    {
        return $this->belongsTo(Customer::class);
    }

    public function channel(): BelongsTo
    {
        return $this->belongsTo(Channel::class);
    }

    public function items(): HasMany
    {
        return $this->hasMany(OrderItem::class)->orderBy('sort_order');
    }

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

    // مجموع محصولات
    public function getItemsTotalAttribute(): float
    {
        return (float) $this->items->sum(function ($i) {
            return $i->price * $i->quantity;
        });
    }

    // خلاصه‌ی محصولات به صورت متن
    public function getProductsSummaryAttribute(): string
    {
        if ($this->items->isEmpty()) {
            return '—';
        }

        return $this->items->map(function ($i) {
            $txt = $i->title;
            if ($i->sku) $txt .= " [{$i->sku}]";
            if ($i->quantity > 1) $txt .= " ×{$i->quantity}";
            return $txt;
        })->join(' • ');
    }
}
""")

# =========================================================
# ۴. Migration: Add invoice_needed to orders
# =========================================================

write_file("database/migrations/2026_09_16_010002_add_invoice_needed_to_orders.php", r"""
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::table('orders', function (Blueprint $table) {
            if (! Schema::hasColumn('orders', 'invoice_needed')) {
                $table->boolean('invoice_needed')->default(false)->after('insurance');
            }
        });
    }

    public function down(): void
    {
        Schema::table('orders', function (Blueprint $table) {
            $table->dropColumn('invoice_needed');
        });
    }
};
""")

# =========================================================
# ۵. Helper: Persian Date
# =========================================================

write_file("app/Support/PersianDate.php", r"""
<?php

namespace App\Support;

class PersianDate
{
    public static function toJalali(\DateTimeInterface $date): array
    {
        $gy = (int) $date->format('Y');
        $gm = (int) $date->format('n');
        $gd = (int) $date->format('j');

        $g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
        $jy = ($gy <= 1600) ? 0 : 979;
        $gy -= ($gy <= 1600) ? 621 : 1600;
        $gy2 = ($gm > 2) ? ($gy + 1) : $gy;
        $days = (365 * $gy) + ((int) (($gy2 + 3) / 4)) - ((int) (($gy2 + 99) / 100))
              + ((int) (($gy2 + 399) / 400)) - 80 + $gd + $g_d_m[$gm - 1];

        $jy += 33 * ((int) ($days / 12053));
        $days %= 12053;
        $jy += 4 * ((int) ($days / 1461));
        $days %= 1461;

        if ($days > 365) {
            $jy += (int) (($days - 1) / 365);
            $days = ($days - 1) % 365;
        }

        $jm = ($days < 186) ? 1 + (int) ($days / 31) : 7 + (int) (($days - 186) / 30);
        $jd = 1 + (($days < 186) ? ($days % 31) : (($days - 186) % 30));

        return ['year' => $jy, 'month' => $jm, 'day' => $jd];
    }

    public static function format(\DateTimeInterface $date, string $format = 'Y/m/d H:i'): string
    {
        $j = self::toJalali($date);
        $out = str_replace(
            ['Y', 'm', 'd', 'H', 'i'],
            [
                $j['year'],
                str_pad((string) $j['month'], 2, '0', STR_PAD_LEFT),
                str_pad((string) $j['day'], 2, '0', STR_PAD_LEFT),
                $date->format('H'),
                $date->format('i'),
            ],
            $format
        );
        return $out;
    }

    public static function now(string $format = 'Y/m/d H:i'): string
    {
        return self::format(now(), $format);
    }

    public static function toPersianDigits(string $str): string
    {
        return str_replace(
            ['0','1','2','3','4','5','6','7','8','9'],
            ['۰','۱','۲','۳','۴','۵','۶','۷','۸','۹'],
            $str
        );
    }
}
""")

# =========================================================
# ۶. Livewire: PhoneSearch (کامپوننت جستجوی تلفن)
# =========================================================

write_file("app/Livewire/Components/PhoneSearch.php", r"""
<?php

namespace App\Livewire\Components;

use App\Models\Customer;
use App\Models\Order;
use Livewire\Component;

class PhoneSearch extends Component
{
    public string $value = '';
    public string $placeholder = '09151234567';
    public array $suggestions = [];
    public bool $showDropdown = false;

    public function updatedValue(): void
    {
        $this->search();
    }

    public function search(): void
    {
        $raw = $this->value;
        $digits = preg_replace('/\D/', '', $raw);
        $norm   = $this->normalize($digits);

        if (strlen($norm) < 3) {
            $this->suggestions = [];
            $this->showDropdown = false;
            return;
        }

        $map = [];

        Order::with('customer')
            ->whereNotNull('phone')
            ->when($norm, function ($q) use ($norm, $digits) {
                $q->where(function ($qq) use ($norm, $digits) {
                    $qq->where('phone', 'like', "%{$digits}%")
                       ->orWhere('phone', 'like', "%{$norm}%");
                });
            })
            ->latest('id')
            ->limit(20)
            ->get()
            ->each(function ($o) use (&$map) {
                $p = $this->normalize($o->phone ?? '');
                if (!$p) return;
                if (! isset($map[$p])) {
                    $map[$p] = [
                        'phone'   => $o->phone,
                        'norm'    => $p,
                        'name'    => $o->customer?->name ?? '—',
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

        Customer::query()
            ->when($norm, fn ($q) => $q->where('phone', 'like', "%{$norm}%"))
            ->limit(20)
            ->get()
            ->each(function ($c) use (&$map) {
                $p = $this->normalize($c->phone ?? '');
                if (!$p) return;
                if (! isset($map[$p])) {
                    $map[$p] = [
                        'phone'   => $c->phone,
                        'norm'    => $p,
                        'name'    => $c->name ?? '—',
                        'address' => $c->address ?? '',
                        'postal'  => $c->postal_code ?? '',
                        'count'   => 0,
                        'ts'      => 0,
                    ];
                } else {
                    if (! $map[$p]['name'] && $c->name)    $map[$p]['name']    = $c->name;
                    if (! $map[$p]['address'] && $c->address) $map[$p]['address'] = $c->address;
                    if (! $map[$p]['postal'] && $c->postal_code) $map[$p]['postal'] = $c->postal_code;
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

    public function select(string $phone): void
    {
        $norm = $this->normalize($phone);

        $order = Order::with('customer')
            ->where('phone', 'like', "%{$norm}%")
            ->latest('id')
            ->first();

        $customer = Customer::where('phone', 'like', "%{$norm}%")->first();

        $data = [
            'phone'   => $order?->phone ?? $customer?->phone ?? $phone,
            'name'    => $order?->customer?->name ?? $customer?->name ?? '',
            'address' => $order?->address ?? $customer?->address ?? '',
            'postal'  => $order?->postal_code ?? $customer?->postal_code ?? '',
        ];

        $this->value = $data['phone'];
        $this->showDropdown = false;
        $this->suggestions = [];

        $this->dispatch('phone-selected', $data);
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
<div class="relative" x-data="{ open: @entangle('showDropdown') }" @click.outside="open = false">
    <input
        type="text"
        wire:model.live.debounce.400ms="value"
        dir="ltr"
        placeholder="{{ $placeholder }}"
        class="input input-bordered font-mono w-full"
        autocomplete="off" />

    @if($showDropdown && count($suggestions) > 0)
        <div class="absolute top-full right-0 left-0 mt-1 bg-base-100 border-2 border-primary rounded-lg shadow-xl z-50 max-h-72 overflow-y-auto">
            @foreach($suggestions as $s)
                <button
                    type="button"
                    wire:click="select('{{ $s['phone'] }}')"
                    class="w-full text-right p-3 hover:bg-base-200 border-b border-base-200 last:border-0
                           {{ strlen($s['norm']) && $s['norm'] === preg_replace('/\D/', '', $value) ? 'bg-success/10' : '' }}">
                    <div class="flex justify-between items-center gap-2">
                        <div class="flex-1 min-w-0">
                            <div class="font-bold text-sm text-primary">{{ $s['name'] ?: '—' }}</div>
                            <div class="font-mono text-xs text-base-content/60" dir="ltr">{{ $s['phone'] }}</div>
                        </div>
                        <div class="badge badge-warning badge-sm whitespace-nowrap">
                            {{ $s['count'] }} 📦
                        </div>
                    </div>
                </button>
            @endforeach
        </div>
    @endif
</div>
""")

# =========================================================
# ۷. Livewire: SkuSearch (کامپوننت جستجوی SKU)
# =========================================================

write_file("app/Livewire/Components/SkuSearch.php", r"""
<?php

namespace App\Livewire\Components;

use App\Models\Integration;
use App\Services\WooCommerceService;
use Livewire\Component;

class SkuSearch extends Component
{
    public string $value = '';
    public array $suggestions = [];
    public bool $showDropdown = false;

    public function updatedValue(): void
    {
        $this->search();
    }

    public function search(): void
    {
        $q = trim($this->value);
        if (strlen($q) < 2) {
            $this->suggestions = [];
            $this->showDropdown = false;
            return;
        }

        $integration = Integration::where('key', 'woocommerce')->where('is_active', true)->first();
        if (! $integration || ! $integration->base_url) {
            $this->suggestions = [];
            $this->showDropdown = false;
            return;
        }

        try {
            $service = new WooCommerceService($integration);
            $products = $service->fetchProducts(1, 20, $q);

            $this->suggestions = collect($products)
                ->filter(fn ($p) => ! empty($p['sku']) || ! empty($p['name']))
                ->take(10)
                ->map(function ($p) {
                    return [
                        'id'    => $p['id'] ?? 0,
                        'sku'   => $p['sku'] ?? '',
                        'title' => $p['name'] ?? '',
                        'price' => (float) ($p['price'] ?? 0),
                        'image' => $p['images'][0]['src'] ?? '',
                        'stock' => $p['stock_quantity'] ?? null,
                    ];
                })
                ->all();

            $this->showDropdown = ! empty($this->suggestions);
        } catch (\Throwable $e) {
            $this->suggestions = [];
            $this->showDropdown = false;
        }
    }

    public function select(string $sku, string $title, float $price): void
    {
        $this->value = $sku;
        $this->showDropdown = false;
        $this->suggestions = [];

        $this->dispatch('sku-selected', [
            'sku'   => $sku,
            'title' => $title,
            'price' => $price,
        ]);
    }

    public function render()
    {
        return view('livewire.components.sku-search');
    }
}
""")

write_file("resources/views/livewire/components/sku-search.blade.php", r"""
<div class="relative" x-data="{ open: @entangle('showDropdown') }" @click.outside="open = false">
    <input
        type="text"
        wire:model.live.debounce.500ms="value"
        dir="ltr"
        placeholder="SKU یا نام محصول..."
        class="input input-bordered font-mono w-full"
        autocomplete="off" />

    @if($showDropdown && count($suggestions) > 0)
        <div class="absolute top-full right-0 left-0 mt-1 bg-base-100 border-2 border-primary rounded-lg shadow-xl z-50 max-h-80 overflow-y-auto">
            @foreach($suggestions as $s)
                <button
                    type="button"
                    wire:click="select('{{ $s['sku'] }}', @js($s['title']), {{ $s['price'] }})"
                    class="w-full text-right p-3 hover:bg-base-200 border-b border-base-200 last:border-0">
                    <div class="flex items-center gap-3">
                        @if($s['image'])
                            <img src="{{ $s['image'] }}" class="w-10 h-10 rounded object-cover flex-shrink-0" />
                        @else
                            <div class="w-10 h-10 rounded bg-base-200 flex items-center justify-center flex-shrink-0">💎</div>
                        @endif
                        <div class="flex-1 min-w-0">
                            <div class="font-bold text-sm text-primary truncate">{{ $s['title'] }}</div>
                            <div class="font-mono text-xs text-base-content/60" dir="ltr">{{ $s['sku'] }}</div>
                        </div>
                        <div class="text-left flex-shrink-0">
                            <div class="font-bold text-xs text-warning">{{ number_format($s['price']) }}</div>
                            @if($s['stock'] !== null)
                                <div class="text-[10px] text-success">موجودی: {{ $s['stock'] }}</div>
                            @endif
                        </div>
                    </div>
                </button>
            @endforeach
        </div>
    @endif
</div>
""")

# =========================================================
# ۸. به‌روزرسانی WooCommerceService (اضافه کردن search)
# =========================================================

woo_file = PROJECT / "app/Services/WooCommerceService.php"
if woo_file.exists():
    content = woo_file.read_text(encoding="utf-8")

    # جایگزینی متد fetchProducts
    old_method = """    // دریافت محصولات
    public function fetchProducts(int $page = 1, int $perPage = 100): array
    {
        try {
            $response = Http::timeout(30)
                ->withoutVerifying()
                ->get($this->buildUrl('products', [
                    'page'     => $page,
                    'per_page' => $perPage,
                ]));

            if ($response->successful()) {
                return $response->json() ?: [];
            }

            return [];
        } catch (\\Throwable $e) {
            Log::error('WC fetch products failed: ' . $e->getMessage());
            return [];
        }
    }"""

    new_method = """    // دریافت محصولات
    public function fetchProducts(int $page = 1, int $perPage = 100, ?string $search = null): array
    {
        try {
            $params = [
                'page'     => $page,
                'per_page' => $perPage,
            ];

            if ($search) {
                $params['search'] = $search;
            }

            $response = Http::timeout(30)
                ->withoutVerifying()
                ->get($this->buildUrl('products', $params));

            if ($response->successful()) {
                return $response->json() ?: [];
            }

            return [];
        } catch (\\Throwable $e) {
            Log::error('WC fetch products failed: ' . $e->getMessage());
            return [];
        }
    }"""

    if old_method in content:
        content = content.replace(old_method, new_method)
        woo_file.write_text(content, encoding="utf-8")
        print("🔁 app/Services/WooCommerceService.php (به‌روزرسانی fetchProducts)")
    else:
        print("⚠️ متد fetchProducts پیدا نشد — دستی چک کن")

# =========================================================
# ۹. کامپوننت Create سفارش (نسخه پیشرفته با محصولات)
# =========================================================

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
    public bool $invoiceNeeded = false;
    public string $notes = '';

    /** @var array<int, array{title:string,sku:string,price:string,qty:int,cert:bool}> */
    public array $items = [];

    public bool $customerFound = false;
    public ?int $existingCustomerId = null;

    protected $listeners = [
        'phone-selected' => 'onPhoneSelected',
        'sku-selected'   => 'onSkuSelected',
    ];

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
    }

    public function onPhoneSelected(array $data): void
    {
        $this->phone        = $data['phone'] ?? '';
        $this->customerName = $data['name'] ?? '';
        $this->address      = $data['address'] ?? '';
        $this->postalCode   = $data['postal'] ?? '';

        $this->updatedPhone();
    }

    public function onSkuSelected(array $data): void
    {
        // آخرین ردیف خالی رو پر کن
        foreach (array_reverse(array_keys($this->items)) as $idx) {
            if (empty($this->items[$idx]['sku'])) {
                $this->items[$idx]['sku']   = $data['sku'] ?? '';
                $this->items[$idx]['title'] = $data['title'] ?? '';
                $this->items[$idx]['price'] = (string) ($data['price'] ?? 0);
                $this->recalcInsurance();
                return;
            }
        }

        // اگه ردیف خالی نبود، ردیف جدید اضافه کن
        $this->items[] = [
            'title' => $data['title'] ?? '',
            'sku'   => $data['sku'] ?? '',
            'price' => (string) ($data['price'] ?? 0),
            'qty'   => 1,
            'cert'  => true,
        ];
        $this->recalcInsurance();
    }

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
            'items'        => 'array',
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
<div class="p-6 max-w-4xl mx-auto">
    <div class="flex items-center gap-3 mb-6">
        <a href="{{ route('orders.index') }}" class="btn btn-ghost btn-sm">→</a>
        <h1 class="text-2xl font-bold">➕ سفارش جدید</h1>
    </div>

    <div class="card bg-base-100 shadow">
        <div class="card-body space-y-5">

            {{-- تلفن با جستجوی خودکار --}}
            <div class="form-control">
                <label class="label"><span class="label-text font-bold">📱 تلفن مشتری *</span></label>
                <livewire:components.phone-search wire:key="phone-search" />
                @if($customerFound)
                    <label class="label"><span class="label-text-alt text-success font-bold">✅ مشتری موجود (ID: {{ $existingCustomerId }})</span></label>
                @elseif(strlen(preg_replace('/\D/', '', $phone)) >= 10)
                    <label class="label"><span class="label-text-alt text-info font-bold">🆕 مشتری جدید</span></label>
                @endif
                @error('phone') <label class="label"><span class="label-text-alt text-error">{{ $message }}</span></label> @enderror
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="form-control">
                    <label class="label"><span class="label-text font-bold">👤 نام</span></label>
                    <input type="text" wire:model="customerName" class="input input-bordered" />
                </div>
                <div class="form-control">
                    <label class="label"><span class="label-text font-bold">📮 کدپستی</span></label>
                    <input type="text" wire:model="postalCode" dir="ltr" class="input input-bordered font-mono" />
                </div>
                <div class="form-control">
                    <label class="label"><span class="label-text font-bold">💰 بیمه</span></label>
                    <input type="text" wire:model="insurance" dir="ltr" class="input input-bordered font-mono" />
                </div>
            </div>

            <div class="form-control">
                <label class="label"><span class="label-text font-bold">📍 آدرس</span></label>
                <textarea wire:model="address" class="textarea textarea-bordered" rows="2"></textarea>
            </div>

            {{-- وضعیت و کانال --}}
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div class="form-control">
                    <label class="label"><span class="label-text font-bold">📊 وضعیت</span></label>
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
                    <label class="label"><span class="label-text font-bold">🌐 کانال</span></label>
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

            {{-- فاکتور --}}
            <label class="label cursor-pointer justify-start gap-3">
                <input type="checkbox" wire:model="invoiceNeeded" class="checkbox checkbox-primary" />
                <span class="label-text font-bold">📄 نیاز به فاکتور</span>
            </label>

            {{-- محصولات --}}
            <div class="divider">🛍️ محصولات</div>

            <div class="space-y-3">
                @foreach($items as $idx => $it)
                    <div class="grid grid-cols-12 gap-2 items-end border border-base-300 rounded-lg p-3 bg-base-200" wire:key="item-{{ $idx }}">
                        <div class="col-span-12 md:col-span-4">
                            <label class="label py-1"><span class="label-text text-xs font-bold">SKU / جستجو</span></label>
                            <input type="text" wire:model="items.{{ $idx }}.sku"
                                   dir="ltr" class="input input-bordered input-sm font-mono w-full" />
                        </div>
                        <div class="col-span-12 md:col-span-4">
                            <label class="label py-1"><span class="label-text text-xs font-bold">عنوان</span></label>
                            <input type="text" wire:model="items.{{ $idx }}.title"
                                   class="input input-bordered input-sm w-full" />
                        </div>
                        <div class="col-span-6 md:col-span-2">
                            <label class="label py-1"><span class="label-text text-xs font-bold">قیمت</span></label>
                            <input type="number" wire:model.live.debounce.500ms="items.{{ $idx }}.price"
                                   dir="ltr" class="input input-bordered input-sm font-mono w-full" />
                        </div>
                        <div class="col-span-3 md:col-span-1">
                            <label class="label py-1"><span class="label-text text-xs font-bold">تعداد</span></label>
                            <input type="number" wire:model.live="items.{{ $idx }}.qty" min="1"
                                   dir="ltr" class="input input-bordered input-sm w-full" />
                        </div>
                        <div class="col-span-3 md:col-span-1 flex flex-col items-center">
                            <label class="label py-1"><span class="label-text text-xs font-bold">شناسنامه</span></label>
                            <div class="flex gap-1">
                                <input type="checkbox" wire:model="items.{{ $idx }}.cert" class="checkbox checkbox-sm" />
                                <button type="button" wire:click="removeItem({{ $idx }})"
                                        class="btn btn-error btn-xs">✕</button>
                            </div>
                        </div>
                    </div>
                @endforeach
            </div>

            <button type="button" wire:click="addItem" class="btn btn-outline btn-sm">➕ افزودن محصول</button>

            {{-- یادداشت --}}
            <div class="form-control">
                <label class="label"><span class="label-text font-bold">📝 یادداشت</span></label>
                <textarea wire:model="notes" class="textarea textarea-bordered" rows="2"></textarea>
            </div>

            <div class="card-actions justify-end mt-4">
                <a href="{{ route('orders.index') }}" class="btn btn-ghost">انصراف</a>
                <button wire:click="save" class="btn btn-primary">✅ ثبت سفارش</button>
            </div>
        </div>
    </div>
</div>
""")

# =========================================================
# ۱۰. به‌روزرسانی Show سفارش (نمایش محصولات از items)
# =========================================================

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
        $this->order = $order->load(['customer', 'channel', 'items']);
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
            @if($order->invoice_needed)
                <span class="badge badge-warning">📄 فاکتور</span>
            @endif
        </div>
        <div class="flex gap-2">
            <a href="{{ route('orders.print-label', $order) }}" target="_blank" class="btn btn-info btn-sm">🏷️ برچسب</a>
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
                    <div class="flex justify-between"><span class="text-base-content/60">مبلغ کل:</span><span>{{ number_format((float) $order->amount) }}</span></div>
                </div>
            </div>
        </div>
    </div>

    @if($order->items->isNotEmpty())
        <div class="card bg-base-100 shadow mb-4">
            <div class="card-body">
                <h2 class="card-title text-base mb-3">🛍️ محصولات</h2>
                <div class="overflow-x-auto">
                    <table class="table table-zebra table-sm">
                        <thead>
                            <tr>
                                <th>#</th>
                                <th>عنوان</th>
                                <th>SKU</th>
                                <th>قیمت</th>
                                <th>تعداد</th>
                                <th>شناسنامه</th>
                            </tr>
                        </thead>
                        <tbody>
                            @foreach($order->items as $i => $item)
                                <tr>
                                    <td>{{ $i + 1 }}</td>
                                    <td class="font-bold">{{ $item->title }}</td>
                                    <td class="font-mono text-xs" dir="ltr">{{ $item->sku ?? '—' }}</td>
                                    <td>{{ number_format((float) $item->price) }}</td>
                                    <td>{{ $item->quantity }}</td>
                                    <td>{!! $item->cert_needed ? '<span class="badge badge-success badge-sm">✓</span>' : '<span class="badge badge-ghost badge-sm">—</span>' !!}</td>
                                </tr>
                            @endforeach
                        </tbody>
                    </table>
                </div>
                <div class="text-left mt-2 font-bold">
                    جمع کل: {{ number_format($order->items_total) }}
                </div>
            </div>
        </div>
    @endif

    <div class="card bg-base-100 shadow mb-4">
        <div class="card-body">
            <h2 class="card-title text-base mb-2">📍 آدرس</h2>
            <p class="text-sm leading-7">{{ $order->address ?? '—' }}</p>
        </div>
    </div>

    @if($order->notes)
        <div class="card bg-base-100 shadow mb-4">
            <div class="card-body">
                <h2 class="card-title text-base mb-2">📝 یادداشت</h2>
                <p class="text-sm leading-7">{{ $order->notes }}</p>
            </div>
        </div>
    @endif

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

# =========================================================
# ۱۱. به‌روزرسانی جدول سفارشات (نمایش خلاصه محصولات)
# =========================================================

orders_index = PROJECT / "app/Livewire/Orders/Index.php"
if orders_index.exists():
    content = orders_index.read_text(encoding="utf-8")
    content = content.replace(
        "->with(['customer', 'channel'])",
        "->with(['customer', 'channel', 'items'])"
    )
    orders_index.write_text(content, encoding="utf-8")
    print("🔁 app/Livewire/Orders/Index.php (eager load items)")

orders_view = PROJECT / "resources/views/livewire/orders/index.blade.php"
if orders_view.exists():
    content = orders_view.read_text(encoding="utf-8")
    # جایگزینی $sum با products_summary
    old = "<td style=\"max-width:200px;font-size:11px;overflow:hidden;text-overflow:ellipsis\" title=\"{{ $sum }}\">{{ $sum }}</td>"
    if old in content:
        content = content.replace(old, "")
    orders_view.write_text(content, encoding="utf-8")
    print("🔁 resources/views/livewire/orders/index.blade.php")

print()
print("═" * 60)
print("✅ مرحله A کامل شد")
print("═" * 60)
print()
print("📌 دستورات بعدی:")
print()
print("   cd ~/projects/shopgun-v2.1")
print("   php artisan optimize:clear")
print("   php artisan migrate")
print("   php artisan serve --host=0.0.0.0 --port=8000")
print()
print("🌐 تست کن:")
print("   http://127.0.0.1:8000/orders/create")
print()
