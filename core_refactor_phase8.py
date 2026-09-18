#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShopGun V2 - Core Refactor Phase 8
====================================
- Dashboard بازطراحی کامل
- کانال فروش (WooCommerce, Basalam, Terb, Zibal, ...)
- نمودار فروش با فیلتر تاریخ
- سفارشات در انتظار تامین + workflow
- تاریخچه خرید مشتری در popup
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
# 1. MIGRATION — فیلدهای جدید orders
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
        Schema::table('orders', function (Blueprint $table) {
            if (!Schema::hasColumn('orders', 'payment_method')) {
                $table->string('payment_method', 60)->nullable()->index()->after('channel_id');
            }
            if (!Schema::hasColumn('orders', 'payment_title')) {
                $table->string('payment_title')->nullable()->after('payment_method');
            }
            if (!Schema::hasColumn('orders', 'sales_channel')) {
                $table->string('sales_channel', 40)->nullable()->index()->after('payment_title');
            }
            if (!Schema::hasColumn('orders', 'channel_metadata')) {
                $table->json('channel_metadata')->nullable()->after('sales_channel');
            }
            if (!Schema::hasColumn('orders', 'customer_note')) {
                $table->text('customer_note')->nullable()->after('notes');
            }
            if (!Schema::hasColumn('orders', 'supply_status')) {
                $table->string('supply_status', 40)->default('default')->index()->after('status');
            }
            if (!Schema::hasColumn('orders', 'woo_status')) {
                $table->string('woo_status', 40)->nullable()->index()->after('status');
            }
        });
    }

    public function down(): void
    {
        Schema::table('orders', function (Blueprint $table) {
            foreach ([
                'payment_method', 'payment_title', 'sales_channel',
                'channel_metadata', 'customer_note', 'supply_status', 'woo_status',
            ] as $col) {
                if (Schema::hasColumn('orders', $col)) $table->dropColumn($col);
            }
        });
    }
};
'''

write(f'database/migrations/{ts}_add_channel_fields_to_orders.php', MIGRATION)


# ═══════════════════════════════════════════════════════════════
# 2. UPDATE Order MODEL
# ═══════════════════════════════════════════════════════════════

om = ROOT / 'app' / 'Models' / 'Order.php'
if om.exists():
    txt = om.read_text(encoding='utf-8')

    # اضافه کردن fillable
    if "'payment_method'" not in txt:
        txt = txt.replace(
            "'invoice_needed', 'meta',",
            "'invoice_needed', 'meta',\n        'payment_method', 'payment_title', 'sales_channel',\n        'channel_metadata', 'customer_note', 'supply_status', 'woo_status',"
        )

    # casts
    if "'channel_metadata' => 'array'" not in txt:
        txt = txt.replace(
            "'shipping_events' => 'array',",
            "'shipping_events' => 'array',\n        'channel_metadata' => 'array',"
        )

    # accessor برای sales channel label
    if 'getSalesChannelLabelAttribute' not in txt:
        txt = txt.replace(
            "    public static function generateNumber(): string",
            '''    public function getSalesChannelLabelAttribute(): string
    {
        return match ($this->sales_channel) {
            'basalam' => '🛍️ باسلام',
            'terb' => '🏬 ترب',
            'zibal' => '💳 زیبال',
            'zarinpal' => '💳 زرین‌پال',
            'bank' => '🏦 کارت به کارت',
            'cod' => '💵 پرداخت در محل',
            'website' => '🌐 سایت',
            'instagram' => '📷 اینستاگرام',
            'telegram' => '✈️ تلگرام',
            'phone' => '📞 تلفنی',
            default => '🌐 ' . ($this->sales_channel ?? 'نامشخص'),
        };
    }

    public function getSalesChannelColorAttribute(): string
    {
        return match ($this->sales_channel) {
            'basalam' => '#00b894',
            'terb' => '#f59e0b',
            'zibal' => '#3b82f6',
            'zarinpal' => '#8b5cf6',
            'bank' => '#64748b',
            'cod' => '#10b981',
            'website' => '#6b0f1a',
            'instagram' => '#e91e63',
            'telegram' => '#29b6f6',
            'phone' => '#66bb6a',
            default => '#94a3b8',
        };
    }

    public function getSupplyStatusLabelAttribute(): string
    {
        return match ($this->supply_status) {
            'awaiting_supply' => '⏳ در انتظار تامین',
            'supplied' => '✅ تامین شد',
            'delivered_to_shipping' => '📦 تحویل واحد ارسال',
            default => '—',
        };
    }

    public static function generateNumber(): string''',
            1
        )

    om.write_text(txt, encoding='utf-8')
    print("[OK] Order Model - کانال فروش")


# ═══════════════════════════════════════════════════════════════
# 3. DASHBOARD METRICS SERVICE
# ═══════════════════════════════════════════════════════════════

write('app/Application/Reports/DashboardMetrics.php', r'''<?php

namespace App\Application\Reports;

use App\Models\Certificate;
use App\Models\Customer;
use App\Models\Order;
use App\Models\OrderItem;
use Carbon\Carbon;
use Illuminate\Support\Facades\DB;

/**
 * ★ DashboardMetrics — آمار کامل داشبورد
 * شامل: کانال فروش، روند، پرفروش‌ها، نسبت لغو، در انتظار تامین
 */
class DashboardMetrics
{
    public function __construct(
        public Carbon $from,
        public Carbon $to,
    ) {}

    // ═══════════════════════════════════════════════════════════
    // KPI
    // ═══════════════════════════════════════════════════════════
    public function kpi(): array
    {
        return [
            [
                'icon' => '📦', 'label' => 'کل سفارشات',
                'value' => Order::whereBetween('created_at', [$this->from, $this->to])->count(),
                'color' => '#3b82f6',
                'route' => route('orders.index'),
            ],
            [
                'icon' => '✅', 'label' => 'سفارشات موفق',
                'value' => Order::whereBetween('created_at', [$this->from, $this->to])
                    ->whereIn('status', ['final-check', 'courier'])->count(),
                'color' => '#10b981',
                'route' => route('orders.index', ['status' => 'final-check']),
            ],
            [
                'icon' => '⏳', 'label' => 'در انتظار تامین',
                'value' => Order::where('supply_status', 'awaiting_supply')->count(),
                'color' => '#f59e0b',
                'route' => route('orders.index', ['supply' => 'awaiting']),
            ],
            [
                'icon' => '👥', 'label' => 'مشتریان',
                'value' => Customer::count(),
                'color' => '#8b5cf6',
                'route' => route('customers.index'),
            ],
            [
                'icon' => '💎', 'label' => 'شناسنامه‌ها',
                'value' => Certificate::whereBetween('created_at', [$this->from, $this->to])->count(),
                'color' => '#c9a84c',
                'route' => route('certificates.index'),
            ],
            [
                'icon' => '💰', 'label' => 'درآمد (م تومان)',
                'value' => round(Order::whereBetween('created_at', [$this->from, $this->to])
                    ->whereIn('status', ['final-check', 'courier'])
                    ->sum('amount') / 1000000, 1),
                'color' => '#16a34a',
                'route' => route('reports.index'),
            ],
        ];
    }

    // ═══════════════════════════════════════════════════════════
    // Sales by Channel
    // ═══════════════════════════════════════════════════════════
    public function salesByChannel(): array
    {
        $rows = Order::query()
            ->whereBetween('created_at', [$this->from, $this->to])
            ->select('sales_channel', DB::raw('COUNT(*) as cnt'), DB::raw('SUM(amount) as total'))
            ->groupBy('sales_channel')
            ->orderByDesc('total')
            ->get();

        $total = $rows->sum('total') ?: 1;

        return $rows->map(function ($r) use ($total) {
            $channel = $r->sales_channel ?? 'website';
            return [
                'channel' => $channel,
                'label' => $this->channelLabel($channel),
                'color' => $this->channelColor($channel),
                'count' => (int) $r->cnt,
                'total' => (float) $r->total,
                'percent' => round(($r->total / $total) * 100, 1),
            ];
        })->toArray();
    }

    // ═══════════════════════════════════════════════════════════
    // Recent Orders per channel (10 per channel)
    // ═══════════════════════════════════════════════════════════
    public function recentByChannel(int $limit = 10): array
    {
        $channels = ['website', 'basalam', 'terb', 'zibal', 'instagram', 'telegram', 'phone'];
        $result = [];

        foreach ($channels as $ch) {
            $orders = Order::query()
                ->where('sales_channel', $ch)
                ->with('items')
                ->latest('id')
                ->limit($limit)
                ->get();

            if ($orders->isEmpty()) continue;

            $result[] = [
                'channel' => $ch,
                'label' => $this->channelLabel($ch),
                'color' => $this->channelColor($ch),
                'count' => $orders->count(),
                'orders' => $orders->map(fn($o) => [
                    'id' => $o->id,
                    'num' => $o->order_number,
                    'customer' => $o->customer_name,
                    'amount' => (float) $o->amount,
                    'status' => $o->status,
                    'date' => \App\Support\PersianDate::format($o->created_at, 'Y/m/d H:i'),
                    'items_count' => $o->items->count(),
                ])->toArray(),
            ];
        }

        return $result;
    }

    // ═══════════════════════════════════════════════════════════
    // Sales Trend
    // ═══════════════════════════════════════════════════════════
    public function salesTrend(int $days = 30): array
    {
        $trend = [];
        $diff = $this->from->diffInDays($this->to);

        if ($diff <= 1) {
            // امروز — به تفکیک ساعت
            for ($h = 0; $h < 24; $h += 2) {
                $f = $this->from->copy()->addHours($h);
                $t = $f->copy()->addHours(2);
                $trend[] = [
                    'label' => $h . 'h',
                    'total' => (float) Order::whereBetween('created_at', [$f, $t])->sum('amount') / 1000000,
                    'count' => Order::whereBetween('created_at', [$f, $t])->count(),
                ];
            }
        } elseif ($diff <= 31) {
            // روزانه
            for ($i = $diff; $i >= 0; $i--) {
                $d = $this->to->copy()->subDays($i);
                $trend[] = [
                    'label' => \App\Support\PersianDate::format($d, 'm/d'),
                    'total' => (float) Order::whereDate('created_at', $d)->sum('amount') / 1000000,
                    'count' => Order::whereDate('created_at', $d)->count(),
                ];
            }
        } else {
            // ماهانه
            $start = $this->from->copy()->startOfMonth();
            while ($start <= $this->to) {
                $end = $start->copy()->endOfMonth();
                $trend[] = [
                    'label' => \App\Support\PersianDate::format($start, 'n'),
                    'total' => (float) Order::whereBetween('created_at', [$start, $end])->sum('amount') / 1000000,
                    'count' => Order::whereBetween('created_at', [$start, $end])->count(),
                ];
                $start->addMonth();
            }
        }

        return $trend;
    }

    // ═══════════════════════════════════════════════════════════
    // Top Products
    // ═══════════════════════════════════════════════════════════
    public function topProducts(int $limit = 10): array
    {
        return OrderItem::query()
            ->whereBetween('order_items.created_at', [$this->from, $this->to])
            ->whereHas('order')
            ->select(
                'title',
                DB::raw('COUNT(*) as cnt'),
                DB::raw('SUM(price * quantity) as total')
            )
            ->groupBy('title')
            ->orderByDesc('cnt')
            ->limit($limit)
            ->get()
            ->map(fn($r) => [
                'title' => $r->title,
                'count' => (int) $r->cnt,
                'total' => (float) $r->total,
            ])
            ->toArray();
    }

    // ═══════════════════════════════════════════════════════════
    // Top Customers
    // ═══════════════════════════════════════════════════════════
    public function topCustomers(int $limit = 10): array
    {
        return Customer::query()
            ->has('orders')
            ->withCount('orders')
            ->withSum('orders', 'amount')
            ->orderByDesc('orders_sum_amount')
            ->limit($limit)
            ->get()
            ->map(fn($c) => [
                'id' => $c->id,
                'name' => $c->name,
                'phone' => $c->phone,
                'orders_count' => (int) $c->orders_count,
                'total' => (float) $c->orders_sum_amount,
            ])
            ->toArray();
    }

    // ═══════════════════════════════════════════════════════════
    // Cancelled vs Successful
    // ═══════════════════════════════════════════════════════════
    public function cancelledRatio(): array
    {
        $base = Order::whereBetween('created_at', [$this->from, $this->to]);

        $success = (clone $base)->whereIn('status', ['final-check', 'courier'])->count();
        $cancelled = (clone $base)->whereIn('woo_status', ['cancelled', 'refunded', 'failed'])->count();
        $pending = (clone $base)->where('status', 'pending')->count();
        $total = $success + $cancelled + $pending;

        return [
            'success' => $success,
            'cancelled' => $cancelled,
            'pending' => $pending,
            'total' => $total,
            'success_pct' => $total > 0 ? round(($success / $total) * 100, 1) : 0,
            'cancelled_pct' => $total > 0 ? round(($cancelled / $total) * 100, 1) : 0,
            'pending_pct' => $total > 0 ? round(($pending / $total) * 100, 1) : 0,
        ];
    }

    // ═══════════════════════════════════════════════════════════
    // Pending Supply Orders (در انتظار تامین)
    // ═══════════════════════════════════════════════════════════
    public function pendingSupplyOrders(int $limit = 30): array
    {
        return Order::query()
            ->where('supply_status', 'awaiting_supply')
            ->with(['items', 'customer'])
            ->latest('id')
            ->limit($limit)
            ->get()
            ->map(fn($o) => [
                'id' => $o->id,
                'num' => $o->order_number,
                'customer' => $o->customer_name,
                'phone' => $o->phone,
                'amount' => (float) $o->amount,
                'date' => \App\Support\PersianDate::format($o->created_at, 'Y/m/d'),
                'items' => $o->items->map(fn($i) => [
                    'title' => $i->title,
                    'sku' => $i->sku,
                    'qty' => (int) $i->quantity,
                ])->toArray(),
            ])
            ->toArray();
    }

    // ═══════════════════════════════════════════════════════════
    // Helpers
    // ═══════════════════════════════════════════════════════════
    public static function channelLabel(string $ch): string
    {
        return match ($ch) {
            'basalam' => '🛍️ باسلام',
            'terb' => '🏬 ترب',
            'zibal' => '💳 زیبال',
            'zarinpal' => '💳 زرین‌پال',
            'bank' => '🏦 کارت‌به‌کارت',
            'cod' => '💵 در محل',
            'website' => '🌐 سایت',
            'instagram' => '📷 اینستاگرام',
            'telegram' => '✈️ تلگرام',
            'phone' => '📞 تلفنی',
            'direct' => '🤝 حضوری',
            default => '🌐 ' . $ch,
        };
    }

    public static function channelColor(string $ch): string
    {
        return match ($ch) {
            'basalam' => '#00b894',
            'terb' => '#f59e0b',
            'zibal' => '#3b82f6',
            'zarinpal' => '#8b5cf6',
            'bank' => '#64748b',
            'cod' => '#10b981',
            'website' => '#6b0f1a',
            'instagram' => '#e91e63',
            'telegram' => '#29b6f6',
            'phone' => '#66bb6a',
            'direct' => '#ffb74d',
            default => '#94a3b8',
        };
    }
}
''')


# ═══════════════════════════════════════════════════════════════
# 4. CHANNEL DETECTOR — تشخیص خودکار کانال
# ═══════════════════════════════════════════════════════════════

write('app/Application/Orders/ChannelDetector.php', r'''<?php

namespace App\Application\Orders;

/**
 * ★ ChannelDetector — تشخیص خودکار کانال فروش از داده ووکامرس
 */
class ChannelDetector
{
    /**
     * تشخیص از payment_method + created_via + customer_note
     */
    public static function detect(array $wcOrder): array
    {
        $paymentMethod = strtolower((string) ($wcOrder['payment_method'] ?? ''));
        $paymentTitle = strtolower((string) ($wcOrder['payment_method_title'] ?? ''));
        $createdVia = strtolower((string) ($wcOrder['created_via'] ?? ''));
        $customerNote = strtolower((string) ($wcOrder['customer_note'] ?? ''));
        $metaData = $wcOrder['meta_data'] ?? [];

        // ۱. باسلام
        if (str_contains($paymentMethod, 'basalam')
            || str_contains($paymentTitle, 'basalam')
            || str_contains($paymentTitle, 'باسلام')
            || str_contains($customerNote, 'باسلام')) {
            return ['channel' => 'basalam', 'meta' => ['detected_from' => 'basalam_in_payment']];
        }

        // ۲. ترب
        if (str_contains($paymentMethod, 'terb')
            || str_contains($paymentTitle, 'ترب')
            || str_contains($paymentTitle, 'torob')
            || str_contains($customerNote, 'ترب')
            || str_contains($customerNote, 'torob')) {
            return ['channel' => 'terb', 'meta' => ['detected_from' => 'terb']];
        }

        // ۳. زیبال
        if (str_contains($paymentMethod, 'zibal') || str_contains($paymentTitle, 'زیبال')) {
            return ['channel' => 'zibal', 'meta' => ['detected_from' => 'zibal']];
        }

        // ۴. زرین‌پال
        if (str_contains($paymentMethod, 'zarinpal') || str_contains($paymentTitle, 'زرین')) {
            return ['channel' => 'zarinpal', 'meta' => ['detected_from' => 'zarinpal']];
        }

        // ۵. کارت‌به‌کارت / bacs
        if ($paymentMethod === 'bacs' || str_contains($paymentTitle, 'کارت')
            || str_contains($paymentTitle, 'واریز') || str_contains($paymentTitle, 'انتقال')) {
            return ['channel' => 'bank', 'meta' => ['detected_from' => 'bank_transfer']];
        }

        // ۶. پرداخت در محل
        if ($paymentMethod === 'cod' || str_contains($paymentTitle, 'در محل')) {
            return ['channel' => 'cod', 'meta' => ['detected_from' => 'cod']];
        }

        // ۷. اینستاگرام
        if (str_contains($createdVia, 'instagram') || str_contains($customerNote, 'اینستاگرام')) {
            return ['channel' => 'instagram', 'meta' => ['detected_from' => 'instagram']];
        }

        // ۸. تلگرام
        if (str_contains($createdVia, 'telegram') || str_contains($customerNote, 'تلگرام')) {
            return ['channel' => 'telegram', 'meta' => ['detected_from' => 'telegram']];
        }

        // ۹. بررسی meta_data برای کانال
        foreach ($metaData as $meta) {
            $key = strtolower((string) ($meta['key'] ?? ''));
            $val = strtolower((string) ($meta['value'] ?? ''));

            if (str_contains($key, 'basalam') || str_contains($val, 'basalam')) {
                return ['channel' => 'basalam', 'meta' => ['detected_from' => 'meta_' . $key]];
            }
            if (str_contains($key, 'terb') || str_contains($key, 'torob')) {
                return ['channel' => 'terb', 'meta' => ['detected_from' => 'meta_' . $key]];
            }
        }

        // ۱۰. از created_via checkout → website
        if (str_contains($createdVia, 'checkout') || str_contains($createdVia, 'api')) {
            return ['channel' => 'website', 'meta' => ['detected_from' => 'checkout']];
        }

        // پیش‌فرض
        return ['channel' => 'website', 'meta' => ['detected_from' => 'default']];
    }

    /**
     * استخراج اطلاعات متفرقه از سفارش (فقط موارد مفید)
     */
    public static function extractMeta(array $wcOrder): array
    {
        $meta = [];
        $metaData = $wcOrder['meta_data'] ?? [];

        foreach ($metaData as $m) {
            $key = (string) ($m['key'] ?? '');
            $val = $m['value'] ?? null;

            // فقط کلیدهای مفید
            if (in_array($key, [
                'billing_phone', 'shipping_phone',
                '_billing_national_code', 'کد ملی',
                '_shipping_city', '_shipping_state',
                'basalam_order_id', 'torob_order_id',
                '_payment_verification_status',
                '_transaction_id',
            ], true) || str_contains($key, 'basalam') || str_contains($key, 'torob')) {
                $meta[$key] = is_string($val) ? mb_substr($val, 0, 200) : $val;
            }
        }

        return $meta;
    }
}
''')


# ═══════════════════════════════════════════════════════════════
# 5. UPDATE ImportOrdersFromWoo — استخراج کانال
# ═══════════════════════════════════════════════════════════════

import_path = ROOT / 'app' / 'Console' / 'Commands' / 'ImportOrdersFromWoo.php'
if import_path.exists():
    txt = import_path.read_text(encoding='utf-8')

    # اضافه کردن use
    if 'ChannelDetector' not in txt:
        txt = txt.replace(
            'use App\\Models\\OrderItem;',
            'use App\\Models\\OrderItem;\nuse App\\Application\\Orders\\ChannelDetector;'
        )

    # اضافه کردن داده کانال
    if 'sales_channel' not in txt:
        # در متد importOne، قبل از $data = [
        txt = txt.replace(
            "        $data = [\n            'order_number' => (string) $wcId,",
            '''        // ★ تشخیص کانال فروش
        $channelInfo = ChannelDetector::detect($wc);
        $channelMeta = ChannelDetector::extractMeta($wc);

        $customerNote = (string) ($wc['customer_note'] ?? '');

        $data = [
            'order_number' => (string) $wcId,
            'sales_channel' => $channelInfo['channel'],
            'payment_method' => $wc['payment_method'] ?? null,
            'payment_title' => $wc['payment_method_title'] ?? null,
            'channel_metadata' => array_merge($channelInfo['meta'] ?? [], $channelMeta),
            'customer_note' => $customerNote ?: null,
            'woo_status' => $wc['status'] ?? null,'''
        )

    import_path.write_text(txt, encoding='utf-8')
    print("[OK] ImportOrdersFromWoo - کانال فروش")


# ═══════════════════════════════════════════════════════════════
# 6. DASHBOARD COMPONENT — بازنویسی کامل
# ═══════════════════════════════════════════════════════════════

write('app/Livewire/Dashboard.php', r'''<?php

namespace App\Livewire;

use App\Application\Reports\DashboardMetrics;
use Carbon\Carbon;
use Livewire\Component;

class Dashboard extends Component
{
    public string $range = 'today';
    public array $accessCards = [];

    public bool $showProductPopup = false;
    public ?array $productDetail = null;

    public function mount(): void
    {
        $this->loadAccessCards();
    }

    protected function loadAccessCards(): void
    {
        $this->accessCards = [
            ['route' => route('orders.index'), 'icon' => '📦', 'label' => 'سفارشات', 'color' => '#3b82f6'],
            ['route' => route('orders.create'), 'icon' => '➕', 'label' => 'سفارش جدید', 'color' => '#10b981'],
            ['route' => route('customers.index'), 'icon' => '👥', 'label' => 'مشتریان', 'color' => '#8b5cf6'],
            ['route' => route('certificates.create'), 'icon' => '💎', 'label' => 'صدور شناسنامه', 'color' => '#c9a84c'],
            ['route' => route('products.bulk'), 'icon' => '⚡', 'label' => 'ثبت گروهی', 'color' => '#7c3aed'],
            ['route' => route('reports.index'), 'icon' => '📊', 'label' => 'گزارش‌ها', 'color' => '#06b6d4'],
            ['route' => route('settings.index'), 'icon' => '⚙️', 'label' => 'تنظیمات', 'color' => '#64748b'],
            ['route' => route('settings.health'), 'icon' => '🩺', 'label' => 'سلامت', 'color' => '#ef4444'],
        ];
    }

    public function setRange(string $range): void
    {
        $this->range = $range;
    }

    public function showProduct(string $title, string $sku = ''): void
    {
        $this->productDetail = [
            'title' => $title,
            'sku' => $sku,
            'image' => null,
        ];

        // تلاش برای گرفتن تصویر از Product
        if ($sku) {
            $p = \App\Models\Product::where('sku', $sku)->first();
            if ($p && $p->image_src) {
                $this->productDetail['image'] = $p->image_src;
            }
        }

        $this->showProductPopup = true;
    }

    public function closeProduct(): void
    {
        $this->showProductPopup = false;
        $this->productDetail = null;
    }

    public function markSupplied(int $orderId): void
    {
        $order = \App\Models\Order::find($orderId);
        if (!$order) return;

        $order->update(['supply_status' => 'delivered_to_shipping']);
        $this->dispatch('notify', type: 'success', message: 'تحویل واحد ارسال شد ✅');
    }

    protected function getPeriods(): array
    {
        $now = now();
        return match ($this->range) {
            'today' => [$now->copy()->startOfDay(), $now->copy()->endOfDay(), 'امروز'],
            'yesterday' => [$now->copy()->subDay()->startOfDay(), $now->copy()->subDay()->endOfDay(), 'دیروز'],
            'week' => [$now->copy()->subDays(6)->startOfDay(), $now->copy()->endOfDay(), '۷ روز اخیر'],
            'month' => [$now->copy()->subDays(29)->startOfDay(), $now->copy()->endOfDay(), '۳۰ روز اخیر'],
            'year' => [$now->copy()->startOfYear(), $now->copy()->endOfDay(), 'سال جاری'],
            default => [$now->copy()->startOfDay(), $now->copy()->endOfDay(), 'امروز'],
        };
    }

    public function render()
    {
        [$from, $to, $label] = $this->getPeriods();
        $metrics = new DashboardMetrics($from, $to);

        return view('livewire.dashboard', [
            'label' => $label,
            'kpi' => $metrics->kpi(),
            'salesByChannel' => $metrics->salesByChannel(),
            'recentByChannel' => $metrics->recentByChannel(10),
            'salesTrend' => $metrics->salesTrend(),
            'topProducts' => $metrics->topProducts(10),
            'topCustomers' => $metrics->topCustomers(10),
            'cancelRatio' => $metrics->cancelledRatio(),
            'pendingSupply' => $metrics->pendingSupplyOrders(20),
        ])->layout('components.layouts.app');
    }
}
''')


# ═══════════════════════════════════════════════════════════════
# 7. DASHBOARD VIEW — بازنویسی کامل
# ═══════════════════════════════════════════════════════════════

DASHBOARD_VIEW = r'''<div style="padding:10px;direction:rtl">

    {{-- ═══ Header + Range Filter ═══ --}}
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:12px">
        <h1 style="margin:0;font-size:19px;font-weight:700">🏠 داشبورد</h1>
        <div style="display:flex;gap:4px;flex-wrap:wrap">
            @foreach(['today'=>'امروز','yesterday'=>'دیروز','week'=>'۷ روز','month'=>'۳۰ روز','year'=>'سال'] as $k => $lbl)
                <button wire:click="setRange('{{ $k }}')"
                        style="padding:6px 12px;border-radius:8px;font-weight:700;cursor:pointer;font-size:11.5px;border:1.5px solid {{ $range === $k ? '#1a5276' : '#e2e8f0' }};background:{{ $range === $k ? 'linear-gradient(135deg,#1a5276,#0d3b5e)' : '#fff' }};color:{{ $range === $k ? '#fff' : '#64748b' }}">
                    {{ $lbl }}
                </button>
            @endforeach
        </div>
    </div>

    {{-- ═══ KPI Cards (Horizontal Scroll) ═══ --}}
    <div style="display:flex;gap:8px;overflow-x:auto;padding-bottom:10px;margin-bottom:12px;scrollbar-width:none">
        @foreach($kpi as $k)
            <a href="{{ $k['route'] }}" wire:navigate
               style="flex:0 0 auto;min-width:130px;padding:10px;border-radius:12px;text-decoration:none;
                   background:#fff;border:1.5px solid #e2e8f0;
                   box-shadow:0 1px 3px rgba(0,0,0,.04);
                   transition:all .15s"
               onmouseover="this.style.transform='translateY(-2px)';this.style.boxShadow='0 6px 18px rgba(0,0,0,.08)'"
               onmouseout="this.style.transform='none';this.style.boxShadow='0 1px 3px rgba(0,0,0,.04)'">
                <div style="display:flex;align-items:center;gap:6px;margin-bottom:6px">
                    <div style="width:30px;height:30px;border-radius:8px;background:{{ $k['color'] }}20;color:{{ $k['color'] }};display:flex;align-items:center;justify-content:center;font-size:15px">
                        {{ $k['icon'] }}
                    </div>
                </div>
                <div style="font-size:18px;font-weight:800;color:{{ $k['color'] }};line-height:1;font-variant-numeric:tabular-nums">
                    {{ \App\Support\PersianNumber::toFa(number_format($k['value'], is_int($k['value']) ? 0 : 1)) }}
                </div>
                <div style="font-size:10px;color:#64748b;font-weight:700;margin-top:3px">{{ $k['label'] }}</div>
            </a>
        @endforeach
    </div>

    {{-- ═══ Access Cards (Quick Links) ═══ --}}
    <div style="margin-bottom:12px">
        <h3 style="font-size:13px;font-weight:700;color:#1a5276;margin:0 0 8px">🚀 دسترسی سریع</h3>
        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:8px">
            @foreach($accessCards as $card)
                <a href="{{ $card['route'] }}" wire:navigate
                   style="padding:10px 8px;border-radius:10px;background:#fff;border:1.5px solid #e2e8f0;text-decoration:none;text-align:center;transition:all .15s"
                   onmouseover="this.style.borderColor='{{ $card['color'] }}';this.style.background='{{ $card['color'] }}10'"
                   onmouseout="this.style.borderColor='#e2e8f0';this.style.background='#fff'">
                    <div style="font-size:20px;margin-bottom:4px">{{ $card['icon'] }}</div>
                    <div style="font-size:10.5px;font-weight:700;color:{{ $card['color'] }}">{{ $card['label'] }}</div>
                </a>
            @endforeach
        </div>
    </div>

    {{-- ═══ 2-column Layout ═══ --}}
    <div style="display:grid;grid-template-columns:1fr;gap:12px">
        @media (min-width: 1024px) {
            & { grid-template-columns: 2fr 1fr; }
        }
    </div>

    <div style="display:grid;grid-template-columns:1fr;gap:12px" id="dash-main">

        {{-- ═══ Sales Trend Chart ═══ --}}
        <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:14px">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
                <h3 style="margin:0;font-size:13.5px;font-weight:700;color:#1a5276">📈 نمودار فروش — {{ $label }}</h3>
                <span style="font-size:10.5px;color:#94a3b8">میلیون تومان</span>
            </div>

            @php
                $maxVal = max(collect($salesTrend)->max('total') ?: 1, 0.1);
            @endphp

            @if(empty($salesTrend))
                <div style="text-align:center;padding:30px;color:#94a3b8;font-size:12px">داده‌ای نیست</div>
            @else
                <div style="display:flex;align-items:flex-end;gap:3px;height:150px;padding:10px 0;overflow-x:auto">
                    @foreach($salesTrend as $d)
                        @php
                            $pct = $maxVal > 0 ? ($d['total'] / $maxVal) * 100 : 0;
                            $h = max(2, $pct);
                        @endphp
                        <div style="flex:0 0 auto;min-width:22px;display:flex;flex-direction:column;align-items:center;gap:3px">
                            <div style="font-size:9px;color:#1a5276;font-weight:700;font-family:monospace">
                                {{ $d['total'] > 0 ? number_format($d['total'], 1) : '' }}
                            </div>
                            <div style="width:100%;height:{{ $h }}%;min-height:4px;
                                        background:linear-gradient(180deg,#14b8a6,#0891b2);
                                        border-radius:4px 4px 0 0;transition:height .3s"
                                 title="{{ $d['count'] }} سفارش · {{ number_format($d['total'], 1) }}M">
                            </div>
                            <div style="font-size:8.5px;color:#94a3b8;font-family:monospace;white-space:nowrap">{{ $d['label'] }}</div>
                        </div>
                    @endforeach
                </div>
            @endif
        </div>

        {{-- ═══ Channel Breakdown ═══ --}}
        <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:14px">
            <h3 style="margin:0 0 12px;font-size:13.5px;font-weight:700;color:#1a5276">🎯 فروش بر اساس کانال</h3>

            @if(empty($salesByChannel))
                <div style="text-align:center;padding:20px;color:#94a3b8;font-size:12px">داده‌ای نیست</div>
            @else
                @php $total = collect($salesByChannel)->sum('total') ?: 1; @endphp
                <div style="display:flex;flex-direction:column;gap:8px">
                    @foreach($salesByChannel as $ch)
                        <div>
                            <div style="display:flex;justify-content:space-between;font-size:11.5px;margin-bottom:3px">
                                <span style="font-weight:700;color:#1e293b">
                                    {{ $ch['label'] }}
                                    <span style="color:#94a3b8;font-size:10px">({{ \App\Support\PersianNumber::toFa($ch['count']) }})</span>
                                </span>
                                <span style="color:{{ $ch['color'] }};font-weight:700;font-family:monospace">
                                    {{ number_format($ch['total'] / 1000000, 1) }}M
                                    <span style="color:#94a3b8;font-size:10px">({{ \App\Support\PersianNumber::toFa($ch['percent']) }}%)</span>
                                </span>
                            </div>
                            <div style="height:6px;background:#f1f5f9;border-radius:3px;overflow:hidden">
                                <div style="height:100%;width:{{ $ch['percent'] }}%;background:{{ $ch['color'] }};border-radius:3px;transition:width .3s"></div>
                            </div>
                        </div>
                    @endforeach
                </div>
            @endif
        </div>
    </div>

    {{-- ═══ Cancel Ratio ═══ --}}
    <div style="display:grid;grid-template-columns:1fr;gap:12px;margin-top:12px">
        <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:14px">
            <h3 style="margin:0 0 12px;font-size:13.5px;font-weight:700;color:#1a5276">📊 نسبت سفارشات — {{ $label }}</h3>

            @php
                $total = $cancelRatio['total'] ?: 1;
                $pctSuccess = $cancelRatio['success_pct'];
                $pctCancelled = $cancelRatio['cancelled_pct'];
                $pctPending = $cancelRatio['pending_pct'];
            @endphp

            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:12px">
                <div style="padding:10px;background:#d1fae5;border-radius:8px;text-align:center">
                    <div style="font-size:22px;font-weight:800;color:#065f46">{{ \App\Support\PersianNumber::toFa($cancelRatio['success']) }}</div>
                    <div style="font-size:10.5px;color:#065f46;font-weight:700">✅ موفق ({{ \App\Support\PersianNumber::toFa($pctSuccess) }}%)</div>
                </div>
                <div style="padding:10px;background:#fee2e2;border-radius:8px;text-align:center">
                    <div style="font-size:22px;font-weight:800;color:#991b1b">{{ \App\Support\PersianNumber::toFa($cancelRatio['cancelled']) }}</div>
                    <div style="font-size:10.5px;color:#991b1b;font-weight:700">❌ لغو ({{ \App\Support\PersianNumber::toFa($pctCancelled) }}%)</div>
                </div>
                <div style="padding:10px;background:#fef3c7;border-radius:8px;text-align:center">
                    <div style="font-size:22px;font-weight:800;color:#92400e">{{ \App\Support\PersianNumber::toFa($cancelRatio['pending']) }}</div>
                    <div style="font-size:10.5px;color:#92400e;font-weight:700">⏳ در انتظار ({{ \App\Support\PersianNumber::toFa($pctPending) }}%)</div>
                </div>
            </div>

            {{-- Horizontal Bar --}}
            <div style="display:flex;height:16px;border-radius:8px;overflow:hidden;background:#f1f5f9">
                <div style="width:{{ $pctSuccess }}%;background:#10b981;height:100%"></div>
                <div style="width:{{ $pctCancelled }}%;background:#ef4444;height:100%"></div>
                <div style="width:{{ $pctPending }}%;background:#f59e0b;height:100%"></div>
            </div>
        </div>
    </div>

    {{-- ═══ 2-Column: Top Products + Top Customers ═══ --}}
    <div style="display:grid;grid-template-columns:1fr;gap:12px;margin-top:12px" id="top-grid">

        {{-- Top Products --}}
        <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:14px">
            <h3 style="margin:0 0 10px;font-size:13.5px;font-weight:700;color:#1a5276">🏆 پرفروش‌ترین محصولات</h3>

            @if(empty($topProducts))
                <div style="text-align:center;padding:20px;color:#94a3b8;font-size:12px">داده‌ای نیست</div>
            @else
                <div style="display:flex;flex-direction:column;gap:4px">
                    @foreach($topProducts as $i => $p)
                        <div wire:click="showProduct(@js($p['title']), '')"
                             style="display:flex;align-items:center;gap:8px;padding:6px 8px;background:#f8fafc;border-radius:6px;cursor:pointer;font-size:11.5px"
                             onmouseover="this.style.background='#eff6ff'" onmouseout="this.style.background='#f8fafc'">
                            <span style="width:20px;height:20px;border-radius:50%;background:{{ $i < 3 ? '#c9a84c' : '#cbd5e1' }};color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:10px;flex-shrink:0">
                                {{ \App\Support\PersianNumber::toFa($i + 1) }}
                            </span>
                            <span style="flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-weight:700">{{ $p['title'] }}</span>
                            <span style="background:#dbeafe;color:#1e40af;padding:1px 7px;border-radius:8px;font-size:10px;font-weight:700;flex-shrink:0">
                                ×{{ \App\Support\PersianNumber::toFa($p['count']) }}
                            </span>
                            <span style="color:#16a34a;font-family:monospace;font-size:10.5px;font-weight:700;flex-shrink:0">
                                {{ number_format($p['total'] / 1000000, 1) }}M
                            </span>
                        </div>
                    @endforeach
                </div>
            @endif
        </div>

        {{-- Top Customers --}}
        <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:14px">
            <h3 style="margin:0 0 10px;font-size:13.5px;font-weight:700;color:#1a5276">⭐ بهترین مشتریان</h3>

            @if(empty($topCustomers))
                <div style="text-align:center;padding:20px;color:#94a3b8;font-size:12px">داده‌ای نیست</div>
            @else
                <div style="display:flex;flex-direction:column;gap:4px">
                    @foreach($topCustomers as $c)
                        <div onclick="Livewire.dispatch('open-customer-profile', {customerId: {{ $c['id'] }}})"
                             style="display:flex;align-items:center;gap:8px;padding:6px 8px;background:#f8fafc;border-radius:6px;cursor:pointer;font-size:11.5px"
                             onmouseover="this.style.background='#f0fdf4'" onmouseout="this.style.background='#f8fafc'">
                            <div style="width:24px;height:24px;border-radius:50%;background:linear-gradient(135deg,#14b8a6,#0891b2);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:11px;flex-shrink:0">
                                {{ mb_substr($c['name'] ?? '?', 0, 1) }}
                            </div>
                            <div style="flex:1;min-width:0">
                                <div style="font-weight:700;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ $c['name'] ?: 'بدون نام' }}</div>
                                <div style="font-family:monospace;font-size:9.5px;color:#94a3b8" dir="ltr">{{ $c['phone'] }}</div>
                            </div>
                            <span style="background:#d1fae5;color:#065f46;padding:1px 7px;border-radius:8px;font-size:10px;font-weight:700;flex-shrink:0">
                                {{ \App\Support\PersianNumber::toFa($c['orders_count']) }}
                            </span>
                            <span style="color:#16a34a;font-family:monospace;font-size:10.5px;font-weight:700;flex-shrink:0">
                                {{ number_format($c['total'] / 1000000, 1) }}M
                            </span>
                        </div>
                    @endforeach
                </div>
            @endif
        </div>
    </div>

    {{-- ═══ Pending Supply Orders ═══ --}}
    @if(!empty($pendingSupply))
        <div style="background:#fff;border:2px solid #f59e0b;border-radius:12px;padding:14px;margin-top:12px">
            <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px">
                <h3 style="margin:0;font-size:13.5px;font-weight:700;color:#92400e">
                    ⏳ در انتظار تامین ({{ \App\Support\PersianNumber::toFa(count($pendingSupply)) }})
                </h3>
                <a href="{{ route('orders.index') }}" wire:navigate style="font-size:11px;color:#1e40af;font-weight:700;text-decoration:none">مشاهده همه →</a>
            </div>

            <div style="display:flex;flex-direction:column;gap:8px;max-height:400px;overflow-y:auto">
                @foreach($pendingSupply as $o)
                    <div style="padding:10px;background:#fffbeb;border:1px solid #fef3c7;border-radius:10px">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;flex-wrap:wrap;gap:6px">
                            <div style="display:flex;align-items:center;gap:8px">
                                <span onclick="Livewire.dispatch('open-order-view', {orderId: {{ $o['id'] }}})"
                                      style="font-family:monospace;font-weight:700;font-size:12.5px;cursor:pointer;color:#1e40af;text-decoration:underline dotted">
                                    #{{ $o['num'] }}
                                </span>
                                <span style="font-size:11px;color:#78350f">{{ $o['customer'] }}</span>
                                <span style="font-size:10px;color:#94a3b8" dir="ltr">{{ $o['phone'] }}</span>
                            </div>
                            <div style="display:flex;gap:6px;align-items:center">
                                <span style="font-family:monospace;font-size:11px;color:#16a34a;font-weight:700">{{ number_format($o['amount']) }}</span>
                                <button wire:click="markSupplied({{ $o['id'] }})"
                                        wire:confirm="تایید شد؟ وضعیت به «تحویل واحد ارسال» تغییر می‌کند"
                                        style="padding:4px 12px;background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;border:none;border-radius:6px;font-weight:700;cursor:pointer;font-size:10.5px">
                                    ✓ تحویل واحد ارسال
                                </button>
                            </div>
                        </div>

                        {{-- محصولات --}}
                        <div style="display:flex;flex-direction:column;gap:3px">
                            @foreach($o['items'] as $it)
                                <div wire:click="showProduct(@js($it['title']), @js($it['sku'] ?? ''))"
                                     style="display:flex;align-items:center;gap:6px;padding:4px 8px;background:#fff;border-radius:6px;font-size:11px;cursor:pointer"
                                     onmouseover="this.style.background='#fffbeb'" onmouseout="this.style.background='#fff'">
                                    <span style="width:22px;height:22px;background:#f1f5f9;border-radius:4px;display:flex;align-items:center;justify-content:center;font-size:12px;flex-shrink:0">💎</span>
                                    <span style="flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-weight:700">{{ $it['title'] }}</span>
                                    @if(!empty($it['sku']))
                                        <span style="font-family:monospace;font-size:9.5px;color:#94a3b8" dir="ltr">{{ $it['sku'] }}</span>
                                    @endif
                                    <span style="background:#fef3c7;color:#92400e;padding:1px 6px;border-radius:6px;font-size:9.5px;font-weight:700;flex-shrink:0">×{{ \App\Support\PersianNumber::toFa($it['qty']) }}</span>
                                </div>
                            @endforeach
                        </div>
                    </div>
                @endforeach
            </div>
        </div>
    @endif

    {{-- ═══ Recent Orders by Channel (Minimal Tables) ═══ --}}
    @if(!empty($recentByChannel))
        <div style="margin-top:12px">
            <h3 style="font-size:13.5px;font-weight:700;color:#1a5276;margin:0 0 8px">🕐 آخرین تراکنش‌ها به تفکیک کانال</h3>

            <div style="display:grid;grid-template-columns:1fr;gap:10px">
                @foreach($recentByChannel as $ch)
                    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;overflow:hidden">
                        <div style="padding:8px 12px;background:linear-gradient(135deg,{{ $ch['color'] }}20,{{ $ch['color'] }}10);border-bottom:1px solid {{ $ch['color'] }}30;display:flex;justify-content:space-between;align-items:center">
                            <div style="display:flex;align-items:center;gap:8px">
                                <span style="width:10px;height:10px;border-radius:50%;background:{{ $ch['color'] }}"></span>
                                <span style="font-weight:700;color:#1e293b;font-size:12.5px">{{ $ch['label'] }}</span>
                                <span style="background:{{ $ch['color'] }}20;color:{{ $ch['color'] }};padding:1px 8px;border-radius:8px;font-size:10px;font-weight:700">
                                    {{ \App\Support\PersianNumber::toFa($ch['count']) }}
                                </span>
                            </div>
                        </div>
                        <div style="overflow-x:auto">
                            <table style="width:100%;border-collapse:collapse;font-size:11px">
                                <thead style="background:#fafafa">
                                    <tr>
                                        <th style="padding:5px 8px;text-align:right;color:#64748b;font-size:10px">#</th>
                                        <th style="padding:5px 8px;text-align:right;color:#64748b;font-size:10px">مشتری</th>
                                        <th style="padding:5px 8px;text-align:right;color:#64748b;font-size:10px">مبلغ</th>
                                        <th style="padding:5px 8px;text-align:right;color:#64748b;font-size:10px">وضعیت</th>
                                        <th style="padding:5px 8px;text-align:right;color:#64748b;font-size:10px">تاریخ</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    @foreach($ch['orders'] as $o)
                                        <tr onclick="Livewire.dispatch('open-order-view', {orderId: {{ $o['id'] }}})"
                                            style="border-bottom:1px solid #f1f5f9;cursor:pointer;transition:background .1s"
                                            onmouseover="this.style.background='#f8fafc'" onmouseout="this.style.background='transparent'">
                                            <td style="padding:5px 8px;font-family:monospace;font-weight:700;color:#1e40af">#{{ $o['num'] }}</td>
                                            <td style="padding:5px 8px;font-weight:700">{{ $o['customer'] }}</td>
                                            <td style="padding:5px 8px;font-family:monospace;color:#16a34a">{{ number_format($o['amount']) }}</td>
                                            <td style="padding:5px 8px">
                                                @php
                                                    $stMap = ['pending'=>['📝','ثبت','#f59e0b'],'final-check'=>['🔍','چک','#3b82f6'],'courier'=>['🚚','مامور','#10b981']];
                                                    $st = $stMap[$o['status']] ?? ['📝','ثبت','#f59e0b'];
                                                @endphp
                                                <span style="background:{{ $st[2] }}20;color:{{ $st[2] }};padding:1px 6px;border-radius:6px;font-size:9.5px;font-weight:700">
                                                    {{ $st[0] }} {{ $st[1] }}
                                                </span>
                                            </td>
                                            <td style="padding:5px 8px;font-family:monospace;font-size:10px;color:#94a3b8">{{ $o['date'] }}</td>
                                        </tr>
                                    @endforeach
                                </tbody>
                            </table>
                        </div>
                    </div>
                @endforeach
            </div>
        </div>
    @endif

    {{-- ═══ Product Popup ═══ --}}
    @if($showProductPopup && $productDetail)
        <div style="position:fixed;inset:0;background:rgba(0,0,0,.85);z-index:95;display:flex;align-items:center;justify-content:center;padding:14px"
             wire:click="closeProduct" @keydown.escape.window="$wire.closeProduct()">
            <div style="background:#fff;border-radius:14px;max-width:340px;width:100%;overflow:hidden" wire:click.stop>
                <div style="aspect-ratio:1;background:#f8fafc;display:flex;align-items:center;justify-content:center;overflow:hidden">
                    @if($productDetail['image'])
                        <img src="{{ $productDetail['image'] }}" style="width:100%;height:100%;object-fit:cover">
                    @else
                        <span style="font-size:60px;color:#cbd5e1">💎</span>
                    @endif
                </div>
                <div style="padding:12px">
                    <div style="font-weight:700;font-size:14px;margin-bottom:6px;color:#1e293b">{{ $productDetail['title'] }}</div>
                    @if($productDetail['sku'])
                        <div style="font-family:monospace;font-size:11px;color:#94a3b8;margin-bottom:8px" dir="ltr">SKU: {{ $productDetail['sku'] }}</div>
                    @endif
                    <button wire:click="closeProduct" style="width:100%;padding:8px;background:#f1f5f9;color:#475569;border:1.5px solid #cbd5e1;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">بستن</button>
                </div>
            </div>
        </div>
    @endif
</div>

{{-- ═══ Responsive Grid ═══ --}}
<style>
@media (min-width: 1024px) {
    #dash-main { grid-template-columns: 2fr 1fr !important; }
    #top-grid { grid-template-columns: 1fr 1fr !important; }
}
</style>
'''

write('resources/views/livewire/dashboard.blade.php', DASHBOARD_VIEW)


# ═══════════════════════════════════════════════════════════════
# 8. UPDATE Order ViewModal — customer history + channel info
# ═══════════════════════════════════════════════════════════════

vm = ROOT / 'resources' / 'views' / 'livewire' / 'orders' / 'view-modal.blade.php'
if vm.exists():
    txt = vm.read_text(encoding='utf-8')

    # اضافه کردن اطلاعات کانال + یادداشت مشتری
    marker = '{{-- ═══ اطلاعات فشرده در یک خط ═══ --}}'
    CHANNEL_INFO = '''            {{-- ═══ کانال فروش + پرداخت ═══ --}}
            @if($order->sales_channel || $order->payment_title)
                <div style="padding:8px 10px;background:#eff6ff;border-radius:8px;margin-bottom:8px;font-size:11px">
                    <div style="display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap">
                        @if($order->sales_channel)
                            <span style="padding:2px 8px;border-radius:6px;background:{{ $order->sales_channel_color }}20;color:{{ $order->sales_channel_color }};font-weight:700">
                                {{ $order->sales_channel_label }}
                            </span>
                        @endif
                        @if($order->payment_title)
                            <span style="font-size:10.5px;color:#1e40af">
                                💳 {{ $order->payment_title }}
                            </span>
                        @endif
                    </div>
                    @if($order->customer_note)
                        <div style="margin-top:6px;padding:6px 8px;background:#fff;border-radius:6px;font-size:10.5px;color:#475569;line-height:1.6">
                            📝 <b>یادداشت مشتری:</b> {{ $order->customer_note }}
                        </div>
                    @endif
                    @if(!empty($order->channel_metadata))
                        <details style="margin-top:6px">
                            <summary style="cursor:pointer;font-size:10.5px;color:#64748b">📋 اطلاعات اضافی</summary>
                            <div style="margin-top:4px;font-size:10px;font-family:monospace;direction:ltr;background:#fff;padding:6px;border-radius:6px;max-height:120px;overflow-y:auto">
                                @foreach($order->channel_metadata as $k => $v)
                                    <div>{{ $k }}: {{ is_array($v) ? json_encode($v, JSON_UNESCAPED_UNICODE) : $v }}</div>
                                @endforeach
                            </div>
                        </details>
                    @endif
                </div>
            @endif

            {{-- ═══ تاریخچه مشتری ═══ --}}
            @if($order->customer_id)
                @php
                    $custOrders = \\App\\Models\\Order::where('customer_id', $order->customer_id)->get();
                    $successCount = $custOrders->whereIn('status', ['final-check','courier'])->count();
                    $cancelCount = $custOrders->whereIn('woo_status', ['cancelled','refunded','failed'])->count();
                    $totalSpent = $custOrders->whereIn('status', ['final-check','courier'])->sum('amount');
                @endphp
                <div style="padding:8px 10px;background:#f0fdf4;border-radius:8px;margin-bottom:8px;font-size:10.5px">
                    <div style="font-weight:700;color:#065f46;margin-bottom:6px">📊 سابقه خرید این مشتری</div>
                    <div style="display:grid;grid-template-columns:repeat(4,1fr);gap:6px">
                        <div style="text-align:center">
                            <div style="font-size:14px;font-weight:800;color:#16a34a">{{ \\App\\Support\\PersianNumber::toFa($successCount) }}</div>
                            <div style="font-size:9.5px;color:#065f46">موفق</div>
                        </div>
                        <div style="text-align:center">
                            <div style="font-size:14px;font-weight:800;color:#dc2626">{{ \\App\\Support\\PersianNumber::toFa($cancelCount) }}</div>
                            <div style="font-size:9.5px;color:#991b1b">لغو</div>
                        </div>
                        <div style="text-align:center">
                            <div style="font-size:14px;font-weight:800;color:#16a34a">{{ \\App\\Support\\PersianNumber::toFa($custOrders->count()) }}</div>
                            <div style="font-size:9.5px;color:#065f46">کل</div>
                        </div>
                        <div style="text-align:center">
                            <div style="font-size:12px;font-weight:800;color:#16a34a;font-family:monospace">{{ number_format($totalSpent / 1000000, 1) }}M</div>
                            <div style="font-size:9.5px;color:#065f46">مجموع</div>
                        </div>
                    </div>
                </div>
            @endif

'''

    if marker in txt and 'سابقه خرید این مشتری' not in txt:
        txt = txt.replace(marker, CHANNEL_INFO + marker, 1)
        vm.write_text(txt, encoding='utf-8')
        print("[OK] order view-modal - کانال + تاریخچه مشتری")


# ═══════════════════════════════════════════════════════════════
# 9. Order Observer — auto awaiting_supply
# ═══════════════════════════════════════════════════════════════

obs = ROOT / 'app' / 'Observers' / 'OrderObserver.php'
if obs.exists():
    txt = obs.read_text(encoding='utf-8')
    if 'awaiting_supply' not in txt:
        txt = txt.replace(
            "        if (! Route::has('orders.show')) {\n            return;\n        }\n\n        AppNotification::broadcast(\n            type: 'order_created',",
            """        // ★ سفارشات pending → awaiting_supply به صورت خودکار
        if ($order->status === 'pending' && $order->supply_status === 'default') {
            try {
                $order->updateQuietly(['supply_status' => 'awaiting_supply']);
            } catch (\\Throwable $e) {}
        }

        if (! Route::has('orders.show')) {
            return;
        }

        AppNotification::broadcast(
            type: 'order_created',""",
            1
        )
        obs.write_text(txt, encoding='utf-8')
        print("[OK] OrderObserver - awaiting_supply")


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
print("DONE — Phase 8")
print("=" * 60)
print()
print("🎯 دستاوردهای فاز ۸:")
print("   ✅ Dashboard بازطراحی کامل")
print("   ✅ ۶ KPI Card + ۸ Access Card")
print("   ✅ کانال فروش خودکار (ChannelDetector)")
print("   ✅ نمودار فروش با فیلتر تاریخ")
print("   ✅ فروش به تفکیک کانال")
print("   ✅ نسبت سفارشات لغو/موفق")
print("   ✅ پرفروش‌ترین محصولات + بهترین مشتریان")
print("   ✅ سفارشات در انتظار تامین با workflow")
print("   ✅ تاریخچه خرید مشتری در popup سفارش")
print("   ✅ اطلاعات اضافی کانال در popup")
print()
print("📌 برای سینک مجدد سفارشات:")
print("   php artisan shopgun:import-orders")
print()
print("🚀 php artisan serve")

