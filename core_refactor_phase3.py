#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShopGun V2 - Core Refactor Phase 3
====================================
- Certificate Snapshot (تاریخچه داده شناسنامه)
- Query Layer (یکدست‌سازی کوئری‌ها)
- Design Tokens (سیستم طراحی واحد)
- NotificationService
"""
from pathlib import Path
import time, subprocess

ROOT = Path('/data/data/com.termux/files/home/shopgun-v2.2')

def write(rel, content):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        p.rename(str(p) + '.bak-' + str(int(time.time())))
    p.write_text(content, encoding='utf-8')
    print("[OK] " + rel)

def run(cmd):
    print(f"$ {cmd}")
    return subprocess.run(cmd, shell=True, cwd=ROOT).returncode


# ═══════════════════════════════════════════════════════════════
# 1. MIGRATION — certificate_snapshots
# ═══════════════════════════════════════════════════════════════

ts = time.strftime('%Y_%m_%d_%H%M%S')
MIGRATION = '''<?php

use Illuminate\\Database\\Migrations\\Migration;
use Illuminate\\Database\\Schema\\Blueprint;
use Illuminate\\Support\\Facades\\Schema;

return new class extends Migration
{
    public function up(): void
    {
        // ★ certificate_snapshots — نگه‌داشتن تاریخچه تغییرات
        if (!Schema::hasTable('certificate_snapshots')) {
            Schema::create('certificate_snapshots', function (Blueprint $table) {
                $table->id();
                $table->foreignId('certificate_id')->constrained('certificates')->cascadeOnDelete();
                $table->string('event', 40); // issued | updated | reprinted | design_changed
                $table->string('sku', 100)->nullable()->index();
                $table->string('stone_name')->nullable();
                $table->string('stone_en')->nullable();
                $table->string('metal')->nullable();
                $table->string('metal_carat')->nullable();
                $table->decimal('length', 8, 2)->nullable();
                $table->decimal('width', 8, 2)->nullable();
                $table->decimal('weight', 10, 3)->nullable();
                $table->integer('brilliant')->nullable();
                $table->string('image_path')->nullable();
                $table->string('image_url')->nullable();
                $table->json('product_data')->nullable();
                $table->json('meta')->nullable();
                $table->foreignId('changed_by')->nullable();
                $table->timestamp('captured_at')->useCurrent();
                $table->timestamps();

                $table->index(['certificate_id', 'captured_at']);
            });
        }
    }

    public function down(): void
    {
        Schema::dropIfExists('certificate_snapshots');
    }
};
'''

write(f'database/migrations/{ts}_create_certificate_snapshots_table.php', MIGRATION)


# ═══════════════════════════════════════════════════════════════
# 2. MODEL CertificateSnapshot
# ═══════════════════════════════════════════════════════════════

write('app/Models/CertificateSnapshot.php', '''<?php

namespace App\\Models;

use Illuminate\\Database\\Eloquent\\Model;
use Illuminate\\Database\\Eloquent\\Relations\\BelongsTo;

class CertificateSnapshot extends Model
{
    protected $fillable = [
        'certificate_id', 'event', 'sku',
        'stone_name', 'stone_en', 'metal', 'metal_carat',
        'length', 'width', 'weight', 'brilliant',
        'image_path', 'image_url',
        'product_data', 'meta', 'changed_by', 'captured_at',
    ];

    protected $casts = [
        'product_data' => 'array',
        'meta' => 'array',
        'captured_at' => 'datetime',
        'length' => 'decimal:2',
        'width' => 'decimal:2',
        'weight' => 'decimal:3',
    ];

    public function certificate(): BelongsTo
    {
        return $this->belongsTo(Certificate::class);
    }

    public function getChangedByNameAttribute(): string
    {
        if (!$this->changed_by) return 'سیستم';
        return User::find($this->changed_by)?->name ?? 'سیستم';
    }
}
''')


# ═══════════════════════════════════════════════════════════════
# 3. CertificateSnapshotService
# ═══════════════════════════════════════════════════════════════

write('app/Application/Certificates/CertificateSnapshotService.php', r'''<?php

namespace App\Application\Certificates;

use App\Models\Certificate;
use App\Models\CertificateSnapshot;
use App\Models\ProductIdentity;
use Illuminate\Support\Facades\Log;

/**
 * ★ CertificateSnapshotService
 *
 * نگه‌داشتن snapshot از شناسنامه در لحظات کلیدی
 * - صدور
 * - ویرایش
 * - چاپ مجدد
 * - تغییر طرح
 *
 * ★ چرا؟ اگر قیمت/وزن محصول در WooCommerce عوض شود،
 *   شناسنامه صادرشده قدیمی نباید تغییر کند.
 */
class CertificateSnapshotService
{
    /**
     * ثبت snapshot جدید
     */
    public static function capture(Certificate $certificate, string $event = 'issued', ?array $productData = null): CertificateSnapshot
    {
        $sku = $certificate->sku;

        // اگه productData داده نشده ولی SKU داریم، از ProductIdentity بگیر
        if ($productData === null && $sku) {
            $identity = ProductIdentity::where('sku', $sku)->first();
            if ($identity) {
                $productData = $identity->last_known_woo_data;
            }
        }

        return CertificateSnapshot::create([
            'certificate_id' => $certificate->id,
            'event' => $event,
            'sku' => $sku,
            'stone_name' => $certificate->stone_name,
            'stone_en' => $certificate->stone_en,
            'metal' => $certificate->metal,
            'metal_carat' => $certificate->metal_carat,
            'length' => $certificate->length,
            'width' => $certificate->width,
            'weight' => $certificate->weight,
            'brilliant' => $certificate->brilliant,
            'image_path' => $certificate->image_path,
            'image_url' => $certificate->image_url,
            'product_data' => $productData,
            'meta' => [
                'ip' => request()?->ip(),
                'ua' => substr(request()?->userAgent() ?? '', 0, 200),
            ],
            'changed_by' => auth()->id(),
            'captured_at' => now(),
        ]);
    }

    /**
     * لیست snapshot های یک شناسنامه
     */
    public static function history(Certificate $certificate): \Illuminate\Database\Eloquent\Collection
    {
        return CertificateSnapshot::where('certificate_id', $certificate->id)
            ->latest('captured_at')
            ->get();
    }

    /**
     * تفاوت دو snapshot
     */
    public static function diff(CertificateSnapshot $old, CertificateSnapshot $new): array
    {
        $fields = ['stone_name', 'stone_en', 'metal', 'metal_carat', 'length', 'width', 'weight', 'brilliant'];
        $diff = [];

        foreach ($fields as $f) {
            if ((string) $old->$f !== (string) $new->$f) {
                $diff[] = [
                    'field' => $f,
                    'old' => $old->$f,
                    'new' => $new->$f,
                ];
            }
        }

        return $diff;
    }
}
''')


# ═══════════════════════════════════════════════════════════════
# 4. Certificate Observer — ثبت خودکار snapshot
# ═══════════════════════════════════════════════════════════════

write('app/Observers/CertificateObserver.php', '''<?php

namespace App\\Observers;

use App\\Application\\Certificates\\CertificateSnapshotService;
use App\\Models\\Certificate;
use App\\Models\\AppNotification;
use Illuminate\\Support\\Facades\\Route;

class CertificateObserver
{
    public function created(Certificate $certificate): void
    {
        try {
            CertificateSnapshotService::capture($certificate, 'issued');

            if (Route::has('certificates.show')) {
                AppNotification::broadcast(
                    type: 'certificate_created',
                    title: "شناسنامه جدید #{$certificate->code}",
                    message: ($certificate->stone_name ?? '') . ' — ' . ($certificate->metal ?? ''),
                    icon: '💎',
                    url: route('certificates.show', $certificate),
                    data: ['certificate_id' => $certificate->id],
                );
            }
        } catch (\\Throwable $e) {
            \\Log::warning('CertificateSnapshot created failed: ' . $e->getMessage());
        }
    }

    public function updated(Certificate $certificate): void
    {
        try {
            $changedFields = array_keys($certificate->getDirty());
            $important = ['stone_name', 'stone_en', 'metal', 'metal_carat', 'length', 'width', 'weight', 'brilliant', 'image_path'];

            $hasImportant = !empty(array_intersect($changedFields, $important));
            if (!$hasImportant) return;

            CertificateSnapshotService::capture($certificate, 'updated');
        } catch (\\Throwable $e) {
            \\Log::warning('CertificateSnapshot updated failed: ' . $e->getMessage());
        }
    }
}
''')


# ═══════════════════════════════════════════════════════════════
# 5. ثبت Observer در AppServiceProvider
# ═══════════════════════════════════════════════════════════════

app_provider = ROOT / 'app' / 'Providers' / 'AppServiceProvider.php'
if app_provider.exists():
    txt = app_provider.read_text(encoding='utf-8')

    if 'CertificateObserver' not in txt:
        txt = txt.replace(
            'use App\\Observers\\OrderObserver;',
            'use App\\Observers\\OrderObserver;\nuse App\\Observers\\CertificateObserver;\nuse App\\Models\\Certificate;'
        )
        txt = txt.replace(
            'Order::observe(OrderObserver::class);',
            'Order::observe(OrderObserver::class);\n        Certificate::observe(CertificateObserver::class);'
        )
        app_provider.write_text(txt, encoding='utf-8')
        print("[OK] AppServiceProvider - CertificateObserver")


# ═══════════════════════════════════════════════════════════════
# 6. QUERY LAYER — OrdersQuery, CustomersQuery, CertificatesQuery
# ═══════════════════════════════════════════════════════════════

write('app/Application/Queries/OrdersQuery.php', '''<?php

namespace App\\Application\\Queries;

use App\\Models\\Order;
use Illuminate\\Contracts\\Pagination\\LengthAwarePaginator;

/**
 * ★ OrdersQuery — کوئری یکدست برای سفارشات
 */
class OrdersQuery
{
    public function __construct(
        public string $search = '',
        public string $status = '',
        public ?int $channelId = null,
        public string $dateFrom = '',
        public string $dateTo = '',
        public string $sortField = 'id',
        public string $sortDir = 'desc',
        public int $perPage = 20,
    ) {}

    public function paginate(): LengthAwarePaginator
    {
        return Order::query()
            ->with(['items', 'channel', 'customer'])
            ->when($this->search, function ($q) {
                $q->where(function ($qq) {
                    $qq->where('order_number', 'like', "%{$this->search}%")
                       ->orWhere('customer_name', 'like', "%{$this->search}%")
                       ->orWhere('phone', 'like', "%{$this->search}%");
                });
            })
            ->when($this->status, fn($q) => $q->where('status', $this->status))
            ->when($this->channelId, fn($q) => $q->where('channel_id', $this->channelId))
            ->when($this->dateFrom, fn($q) => $q->whereDate('created_at', '>=', $this->dateFrom))
            ->when($this->dateTo, fn($q) => $q->whereDate('created_at', '<=', $this->dateTo))
            ->orderBy($this->sortField, $this->sortDir)
            ->paginate($this->perPage);
    }

    /**
     * شمارش بر اساس وضعیت
     */
    public function statusCounts(): array
    {
        return Order::query()
            ->selectRaw('status, COUNT(*) as cnt')
            ->groupBy('status')
            ->pluck('cnt', 'status')
            ->toArray();
    }

    /**
     * آمار خلاصه
     */
    public function summary(): array
    {
        $base = Order::query()
            ->when($this->dateFrom, fn($q) => $q->whereDate('created_at', '>=', $this->dateFrom))
            ->when($this->dateTo, fn($q) => $q->whereDate('created_at', '<=', $this->dateTo));

        return [
            'total' => (clone $base)->count(),
            'sum' => (float) (clone $base)->sum('amount'),
            'avg' => (float) (clone $base)->avg('amount'),
            'today' => Order::whereDate('created_at', today())->count(),
        ];
    }
}
''')

write('app/Application/Queries/CustomersQuery.php', '''<?php

namespace App\\Application\\Queries;

use App\\Models\\Customer;
use Illuminate\\Contracts\\Pagination\\LengthAwarePaginator;

class CustomersQuery
{
    public function __construct(
        public string $search = '',
        public string $filter = '',
        public string $sortField = 'id',
        public string $sortDir = 'desc',
        public int $perPage = 20,
    ) {}

    public function paginate(): LengthAwarePaginator
    {
        return Customer::query()
            ->withCount('orders')
            ->withSum('orders', 'amount')
            ->when($this->search, function ($q) {
                $q->where(function ($qq) {
                    $qq->where('name', 'like', "%{$this->search}%")
                       ->orWhere('phone', 'like', "%{$this->search}%");
                });
            })
            ->when($this->filter === 'has_orders', fn($q) => $q->has('orders'))
            ->when($this->filter === 'no_orders', fn($q) => $q->doesntHave('orders'))
            ->orderBy($this->sortField, $this->sortDir)
            ->paginate($this->perPage);
    }

    public function summary(): array
    {
        return [
            'total' => Customer::count(),
            'with_orders' => Customer::has('orders')->count(),
            'today' => Customer::whereDate('created_at', today())->count(),
        ];
    }
}
''')

write('app/Application/Queries/CertificatesQuery.php', '''<?php

namespace App\\Application\\Queries;

use App\\Models\\Certificate;
use Illuminate\\Contracts\\Pagination\\LengthAwarePaginator;

class CertificatesQuery
{
    public function __construct(
        public string $search = '',
        public string $filter = '',
        public int $perPage = 20,
    ) {}

    public function paginate(): LengthAwarePaginator
    {
        return Certificate::query()
            ->with(['customer'])
            ->when($this->search, function ($q) {
                $q->where(function ($qq) {
                    $qq->where('code', 'like', "%{$this->search}%")
                       ->orWhere('serial', 'like', "%{$this->search}%")
                       ->orWhere('sku', 'like', "%{$this->search}%")
                       ->orWhere('stone_name', 'like', "%{$this->search}%");
                });
            })
            ->when($this->filter === 'with_image', fn($q) => $q->whereNotNull('image_path'))
            ->when($this->filter === 'no_image', fn($q) => $q->whereNull('image_path'))
            ->latest('id')
            ->paginate($this->perPage);
    }
}
''')


# ═══════════════════════════════════════════════════════════════
# 7. NotificationService
# ═══════════════════════════════════════════════════════════════

write('app/Application/Notifications/NotificationService.php', r'''<?php

namespace App\Application\Notifications;

use App\Models\AppNotification;
use App\Models\User;

/**
 * ★ NotificationService
 * نقطه واحد برای ارسال اعلان
 */
class NotificationService
{
    public static function toUser(int $userId, string $type, string $title, string $message, string $icon = '🔔', ?string $url = null, array $data = []): AppNotification
    {
        return AppNotification::create([
            'user_id' => $userId,
            'type' => $type,
            'title' => $title,
            'message' => $message,
            'icon' => $icon,
            'url' => $url,
            'data' => $data,
        ]);
    }

    public static function toAll(string $type, string $title, string $message, string $icon = '🔔', ?string $url = null, array $data = []): int
    {
        $count = 0;
        foreach (User::all() as $user) {
            self::toUser($user->id, $type, $title, $message, $icon, $url, $data);
            $count++;
        }
        return $count;
    }

    public static function toRole(string $roleName, string $type, string $title, string $message, string $icon = '🔔', ?string $url = null, array $data = []): int
    {
        $count = 0;
        $users = User::role($roleName)->get();
        foreach ($users as $user) {
            self::toUser($user->id, $type, $title, $message, $icon, $url, $data);
            $count++;
        }
        return $count;
    }

    /**
     * اعلان سیستمی
     */
    public static function system(string $title, string $message, string $icon = '⚙️', array $data = []): int
    {
        return self::toAll('system', $title, $message, $icon, null, $data);
    }
}
''')


# ═══════════════════════════════════════════════════════════════
# 8. DESIGN SYSTEM CSS
# ═══════════════════════════════════════════════════════════════

write('public/css/shopgun-system.css', r'''/* ═══════════════════════════════════════════════════════════════
   ShopGun Design System v1.0
   ═══════════════════════════════════════════════════════════════
   یک فایل مرکزی برای همه design tokens و utility classes
   همه صفحات از این استفاده می‌کنند
   ═══════════════════════════════════════════════════════════════ */

:root {
    /* ═══ Colors ═══ */
    --sg-color-primary: #1a5276;
    --sg-color-primary-light: #2980b9;
    --sg-color-primary-dark: #0d3b5e;
    --sg-color-gold: #c9a84c;
    --sg-color-gold-light: #f0d68a;
    --sg-color-gold-dark: #8b6914;

    --sg-color-bg: #f5f0e8;
    --sg-color-bg-card: #ffffff;
    --sg-color-bg-soft: rgba(0,0,0,.03);

    --sg-color-text: #2c3e50;
    --sg-color-text-light: #7f8c8d;
    --sg-color-text-muted: #95a5a6;

    --sg-color-border: #d4c5a9;
    --sg-color-border-soft: rgba(0,0,0,.06);

    --sg-color-success: #27ae60;
    --sg-color-danger: #e74c3c;
    --sg-color-warn: #f39c12;
    --sg-color-info: #2980b9;

    /* ═══ Spacing ═══ */
    --sg-space-1: 4px;
    --sg-space-2: 8px;
    --sg-space-3: 12px;
    --sg-space-4: 16px;
    --sg-space-5: 20px;
    --sg-space-6: 24px;
    --sg-space-8: 32px;

    /* ═══ Radius ═══ */
    --sg-radius-sm: 6px;
    --sg-radius: 10px;
    --sg-radius-lg: 14px;
    --sg-radius-xl: 20px;
    --sg-radius-full: 9999px;

    /* ═══ Shadow ═══ */
    --sg-shadow-sm: 0 1px 3px rgba(0,0,0,.06);
    --sg-shadow: 0 4px 12px rgba(0,0,0,.08);
    --sg-shadow-lg: 0 8px 30px rgba(0,0,0,.12);
    --sg-shadow-xl: 0 20px 60px rgba(0,0,0,.4);

    /* ═══ Typography ═══ */
    --sg-font-body: 'Vazirmatn', Tahoma, sans-serif;
    --sg-font-mono: ui-monospace, 'Courier New', monospace;

    --sg-text-xs: 10.5px;
    --sg-text-sm: 11.5px;
    --sg-text-base: 12.5px;
    --sg-text-lg: 14px;
    --sg-text-xl: 16px;
    --sg-text-2xl: 20px;

    /* ═══ Transitions ═══ */
    --sg-transition-fast: 0.12s ease;
    --sg-transition: 0.18s cubic-bezier(0.4, 0, 0.2, 1);
    --sg-transition-slow: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ═══ Dark Theme ═══ */
[data-theme="dark"] {
    --sg-color-primary: #4da6d8;
    --sg-color-primary-light: #6bb8e3;
    --sg-color-primary-dark: #2c7db3;
    --sg-color-gold: #d4b85a;
    --sg-color-gold-light: #e8d090;
    --sg-color-gold-dark: #b89840;

    --sg-color-bg: #0a0f1a;
    --sg-color-bg-card: #151b27;
    --sg-color-bg-soft: rgba(255,255,255,.04);

    --sg-color-text: #e6edf5;
    --sg-color-text-light: #94a3b8;
    --sg-color-text-muted: #64748b;

    --sg-color-border: #2a3544;
    --sg-color-border-soft: rgba(255,255,255,.08);
}

/* ═══════════════════════════════════════════════════════════
   Base Reset (اختیاری — برای اطمینان از یکدستی)
   ═══════════════════════════════════════════════════════════ */
.sg-app {
    font-family: var(--sg-font-body);
    color: var(--sg-color-text);
    background: var(--sg-color-bg);
}

/* ═══════════════════════════════════════════════════════════
   Layout
   ═══════════════════════════════════════════════════════════ */

.sg-layout {
    display: flex;
    min-height: 100vh;
}

.sg-main {
    flex: 1;
    min-width: 0;
    padding: var(--sg-space-4);
}

/* ═══════════════════════════════════════════════════════════
   Card
   ═══════════════════════════════════════════════════════════ */

.sg-card {
    background: var(--sg-color-bg-card);
    border: 1px solid var(--sg-color-border-soft);
    border-radius: var(--sg-radius);
    padding: var(--sg-space-4);
    box-shadow: var(--sg-shadow-sm);
    transition: var(--sg-transition);
}

.sg-card:hover {
    box-shadow: var(--sg-shadow);
}

.sg-card-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: var(--sg-space-3);
    margin-bottom: var(--sg-space-3);
    padding-bottom: var(--sg-space-2);
    border-bottom: 1px solid var(--sg-color-border-soft);
}

.sg-card-header h3 {
    margin: 0;
    font-size: var(--sg-text-lg);
    font-weight: 700;
    color: var(--sg-color-primary);
}

/* ═══════════════════════════════════════════════════════════
   Buttons
   ═══════════════════════════════════════════════════════════ */

.sg-btn {
    display: inline-flex;
    align-items: center;
    justify-content: center;
    gap: var(--sg-space-1);
    padding: 8px 16px;
    border-radius: var(--sg-radius-sm);
    border: none;
    font-family: var(--sg-font-body);
    font-size: var(--sg-text-base);
    font-weight: 700;
    cursor: pointer;
    transition: var(--sg-transition-fast);
    text-decoration: none;
    white-space: nowrap;
}

.sg-btn:hover {
    transform: translateY(-1px);
    box-shadow: var(--sg-shadow-sm);
}

.sg-btn:active {
    transform: translateY(0);
}

.sg-btn:disabled {
    opacity: 0.5;
    cursor: not-allowed;
    transform: none;
}

.sg-btn-primary {
    background: linear-gradient(135deg, var(--sg-color-primary), var(--sg-color-primary-dark));
    color: #fff;
}

.sg-btn-gold {
    background: linear-gradient(135deg, var(--sg-color-gold), var(--sg-color-gold-dark));
    color: #fff;
}

.sg-btn-success {
    background: linear-gradient(135deg, #16a34a, #15803d);
    color: #fff;
}

.sg-btn-danger {
    background: linear-gradient(135deg, #dc2626, #991b1b);
    color: #fff;
}

.sg-btn-outline {
    background: transparent;
    color: var(--sg-color-text);
    border: 1.5px solid var(--sg-color-border);
}

.sg-btn-sm { padding: 5px 12px; font-size: var(--sg-text-sm); }
.sg-btn-xs { padding: 3px 8px; font-size: var(--sg-text-xs); }
.sg-btn-lg { padding: 12px 24px; font-size: var(--sg-text-lg); }

/* ═══════════════════════════════════════════════════════════
   Form Fields
   ═══════════════════════════════════════════════════════════ */

.sg-field {
    display: flex;
    flex-direction: column;
    gap: var(--sg-space-1);
    margin-bottom: var(--sg-space-3);
}

.sg-field > label {
    font-size: var(--sg-text-sm);
    font-weight: 700;
    color: var(--sg-color-primary);
}

.sg-field > input,
.sg-field > select,
.sg-field > textarea {
    width: 100%;
    padding: 8px 12px;
    border: 1.5px solid var(--sg-color-border);
    border-radius: var(--sg-radius-sm);
    background: var(--sg-color-bg-soft);
    color: var(--sg-color-text);
    font-family: var(--sg-font-body);
    font-size: var(--sg-text-base);
    transition: var(--sg-transition-fast);
    box-sizing: border-box;
}

.sg-field > input:focus,
.sg-field > select:focus,
.sg-field > textarea:focus {
    outline: none;
    border-color: var(--sg-color-gold);
    box-shadow: 0 0 0 3px rgba(201,168,76,.15);
}

.sg-field > input[dir="ltr"] {
    font-family: var(--sg-font-mono);
    text-align: left;
}

/* ═══════════════════════════════════════════════════════════
   Badges
   ═══════════════════════════════════════════════════════════ */

.sg-badge {
    display: inline-flex;
    align-items: center;
    gap: 3px;
    padding: 3px 10px;
    border-radius: var(--sg-radius-full);
    font-size: var(--sg-text-xs);
    font-weight: 700;
    white-space: nowrap;
}

.sg-badge-success { background: #d1fae5; color: #065f46; }
.sg-badge-warn    { background: #fef3c7; color: #92400e; }
.sg-badge-danger  { background: #fee2e2; color: #991b1b; }
.sg-badge-info    { background: #dbeafe; color: #1e40af; }
.sg-badge-ghost   { background: var(--sg-color-bg-soft); color: var(--sg-color-text-light); }

/* ═══════════════════════════════════════════════════════════
   Table
   ═══════════════════════════════════════════════════════════ */

.sg-table-wrap {
    overflow-x: auto;
    border-radius: var(--sg-radius);
    border: 1px solid var(--sg-color-border-soft);
    background: var(--sg-color-bg-card);
}

.sg-table {
    width: 100%;
    border-collapse: collapse;
    font-size: var(--sg-text-sm);
}

.sg-table thead th {
    background: var(--sg-color-bg-soft);
    padding: 8px 10px;
    text-align: right;
    font-weight: 700;
    font-size: var(--sg-text-sm);
    color: var(--sg-color-primary);
    border-bottom: 2px solid var(--sg-color-border-soft);
    white-space: nowrap;
}

.sg-table tbody td {
    padding: 6px 10px;
    border-bottom: 1px solid var(--sg-color-border-soft);
    color: var(--sg-color-text);
}

.sg-table tbody tr:hover td {
    background: rgba(201,168,76,.04);
}

/* ═══════════════════════════════════════════════════════════
   Modal
   ═══════════════════════════════════════════════════════════ */

.sg-modal-backdrop {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,.75);
    z-index: 90;
    display: flex;
    align-items: flex-start;
    justify-content: center;
    padding: var(--sg-space-2);
    overflow-y: auto;
    animation: sgFadeIn 0.2s ease;
}

.sg-modal-content {
    background: var(--sg-color-bg-card);
    width: 100%;
    max-width: 700px;
    margin: var(--sg-space-2) auto;
    border-radius: var(--sg-radius-lg);
    box-shadow: var(--sg-shadow-xl);
    overflow: hidden;
    animation: sgSlideUp 0.3s cubic-bezier(0.34, 1.4, 0.64, 1);
}

.sg-modal-header {
    padding: 14px 18px;
    background: linear-gradient(135deg, var(--sg-color-primary), var(--sg-color-primary-dark));
    color: #fff;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.sg-modal-body {
    padding: var(--sg-space-4);
    max-height: calc(100vh - 180px);
    overflow-y: auto;
}

.sg-modal-footer {
    padding: var(--sg-space-3) var(--sg-space-4);
    background: var(--sg-color-bg-soft);
    border-top: 1px solid var(--sg-color-border-soft);
    display: flex;
    justify-content: space-between;
    gap: var(--sg-space-2);
    flex-wrap: wrap;
}

@keyframes sgFadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes sgSlideUp {
    from { opacity: 0; transform: translateY(16px) scale(0.98); }
    to { opacity: 1; transform: translateY(0) scale(1); }
}

/* ═══════════════════════════════════════════════════════════
   Utilities
   ═══════════════════════════════════════════════════════════ */

.sg-flex { display: flex; }
.sg-flex-between { display: flex; justify-content: space-between; }
.sg-flex-center { display: flex; align-items: center; justify-content: center; }
.sg-gap-1 { gap: var(--sg-space-1); }
.sg-gap-2 { gap: var(--sg-space-2); }
.sg-gap-3 { gap: var(--sg-space-3); }
.sg-gap-4 { gap: var(--sg-space-4); }

.sg-mb-1 { margin-bottom: var(--sg-space-1); }
.sg-mb-2 { margin-bottom: var(--sg-space-2); }
.sg-mb-3 { margin-bottom: var(--sg-space-3); }
.sg-mb-4 { margin-bottom: var(--sg-space-4); }

.sg-p-2 { padding: var(--sg-space-2); }
.sg-p-3 { padding: var(--sg-space-3); }
.sg-p-4 { padding: var(--sg-space-4); }

.sg-text-xs { font-size: var(--sg-text-xs); }
.sg-text-sm { font-size: var(--sg-text-sm); }
.sg-text-base { font-size: var(--sg-text-base); }
.sg-text-lg { font-size: var(--sg-text-lg); }

.sg-text-primary { color: var(--sg-color-primary); }
.sg-text-gold { color: var(--sg-color-gold); }
.sg-text-muted { color: var(--sg-color-text-muted); }
.sg-text-success { color: var(--sg-color-success); }
.sg-text-danger { color: var(--sg-color-danger); }

.sg-font-bold { font-weight: 700; }
.sg-font-mono { font-family: var(--sg-font-mono); }
.sg-truncate {
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
    min-width: 0;
}

/* ═══════════════════════════════════════════════════════════
   Responsive
   ═══════════════════════════════════════════════════════════ */

@media (max-width: 768px) {
    .sg-main {
        padding: var(--sg-space-2);
    }

    .sg-modal-content {
        border-radius: var(--sg-radius);
    }

    .sg-table thead th,
    .sg-table tbody td {
        padding: 6px 8px;
        font-size: var(--sg-text-xs);
    }
}
''')


# ═══════════════════════════════════════════════════════════════
# 9. لود کردن CSS در Layout
# ═══════════════════════════════════════════════════════════════

layout = ROOT / 'resources' / 'views' / 'components' / 'layouts' / 'app.blade.php'
if layout.exists():
    txt = layout.read_text(encoding='utf-8')

    if 'shopgun-system.css' not in txt:
        # قبل از </head>
        txt = txt.replace(
            '</head>',
            '<link rel="stylesheet" href="{{ asset(\'css/shopgun-system.css\') }}?v=1">\n</head>'
        )
        layout.write_text(txt, encoding='utf-8')
        print("[OK] layout - shopgun-system.css")


# ═══════════════════════════════════════════════════════════════
# 10. اجرا
# ═══════════════════════════════════════════════════════════════

print()
print("🔧 Migration و پاک‌سازی...")
run('php artisan migrate --force')
run('php artisan optimize:clear')
run('php artisan route:clear')
run('php artisan view:clear')

print()
print("=" * 60)
print("DONE — Phase 3")
print("=" * 60)
print()
print("🎯 دستاوردهای فاز ۳:")
print("   ✅ Certificate Snapshot — تاریخچه تغییرات شناسنامه")
print("   ✅ CertificateObserver — ثبت خودکار snapshot")
print("   ✅ Query Layer: OrdersQuery, CustomersQuery, CertificatesQuery")
print("   ✅ NotificationService — نقطه واحد اعلان")
print("   ✅ Design System کامل در public/css/shopgun-system.css")
print()
print("📌 نکته:")
print("   Design System کلاس‌های sg-* جدید ارائه می‌دهد")
print("   صفحات قدیمی هنوز کار می‌کنند — می‌توانی یکی‌یکی مهاجرت کنی")
print()
print("🚀 php artisan serve")
