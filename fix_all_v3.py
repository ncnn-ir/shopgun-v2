#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Fix Reports (HAVING) + Product Sync (timeout) + Fallback Import
"""
import shutil
from pathlib import Path
from datetime import datetime

PROJECT = Path(r"D:\prodo\shopgun-v2.1")
if not PROJECT.exists():
    PROJECT = Path(input("مسیر پروژه: ").strip().strip('"'))
    if not PROJECT.exists():
        print("❌"); exit(1)

def write(rel, content):
    full = PROJECT / rel
    full.parent.mkdir(parents=True, exist_ok=True)
    with open(full, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print(f"  ✓ {rel}")

def backup(rel):
    src = PROJECT / rel
    if not src.exists(): return
    bd = PROJECT / "storage/backups"; bd.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(src, bd / f"{src.stem}_{ts}.bak")

# ═══════════════════════════════════════════════════════════════
# ۱) Reports/Index.php — بدون HAVING
# ═══════════════════════════════════════════════════════════════

REPORTS_PHP = r'''<?php

namespace App\Livewire\Reports;

use App\Models\Certificate;
use App\Models\Customer;
use App\Models\Order;
use App\Models\Product;
use Livewire\Component;

class Index extends Component
{
    public string $range = 'today';

    public function setRange(string $range): void
    {
        $this->range = $range;
    }

    public function getStartDateProperty()
    {
        return match($this->range) {
            'today' => now()->startOfDay(),
            'week'  => now()->subDays(7)->startOfDay(),
            'month' => now()->subDays(30)->startOfDay(),
            'year'  => now()->startOfYear(),
            default => now()->startOfDay(),
        };
    }

    public function render()
    {
        $start = $this->start_date;

        $orders = Order::where('created_at', '>=', $start);
        $total = (clone $orders)->count();
        $amount = (float) (clone $orders)->sum('amount');
        $avgAmount = $total > 0 ? $amount / $total : 0;

        $byStatus = [
            'pending'     => (clone $orders)->where('status', 'pending')->count(),
            'final-check' => (clone $orders)->where('status', 'final-check')->count(),
            'courier'     => (clone $orders)->where('status', 'courier')->count(),
        ];

        // روند روزانه
        $daily = [];
        for ($i = 6; $i >= 0; $i--) {
            $d = now()->subDays($i);
            $daily[] = [
                'date'   => \App\Support\PersianDate::format($d, 'm/d'),
                'count'  => Order::whereDate('created_at', $d)->count(),
                'amount' => (float) Order::whereDate('created_at', $d)->sum('amount'),
            ];
        }

        // ★ فیکس: به جای HAVING از has() استفاده کن (سازگار با SQLite)
        $topCustomers = Customer::has('orders')
            ->withCount('orders')
            ->orderByDesc('orders_count')
            ->limit(5)
            ->get();

        $stats = [
            'customers'    => Customer::count(),
            'orders_total' => Order::count(),
            'products'     => Product::count(),
            'certificates' => Certificate::count(),
        ];

        return view('livewire.reports.index', [
            'total'        => $total,
            'amount'       => $amount,
            'avgAmount'    => $avgAmount,
            'byStatus'     => $byStatus,
            'daily'        => $daily,
            'topCustomers' => $topCustomers,
            'stats'        => $stats,
        ])->layout('components.layouts.app');
    }
}
'''

# ═══════════════════════════════════════════════════════════════
# ۲) SyncProducts Command — با timeout بیشتر + retry + پیام واضح
# ═══════════════════════════════════════════════════════════════

SYNC_COMMAND = r'''<?php

namespace App\Console\Commands;

use App\Models\AppSetting;
use App\Models\Product;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Http;

class SyncProducts extends Command
{
    protected $signature = 'shopgun:sync-products
                            {--timeout=120 : timeout در ثانیه}
                            {--per-page=50 : تعداد در هر صفحه}';

    protected $description = 'سینک محصولات از WooCommerce';

    public function handle(): int
    {
        $url    = AppSetting::get('commerce_url', '');
        $key    = AppSetting::get('commerce_key', '');
        $secret = AppSetting::get('commerce_secret', '');

        if (!$url || !$key || !$secret) {
            $this->error('❌ اطلاعات کامرس تنظیم نشده.');
            $this->line('   برو به /settings → تب کامرس و اطلاعات رو وارد کن.');
            return 1;
        }

        $base = rtrim($url, '/');
        if (!str_contains($base, '/wp-json')) {
            $base .= '/wp-json/wc/v3';
        }

        $timeout = (int) $this->option('timeout');
        $perPage = (int) $this->option('per-page');

        $this->info("🔌 اتصال به: {$base}");
        $this->line("⏱️  Timeout: {$timeout}s · Per-page: {$perPage}");
        $this->newLine();

        // ─── تست اتصال اول ───
        $this->line('⏳ تست اتصال...');
        try {
            $test = Http::withBasicAuth($key, $secret)
                ->timeout(30)
                ->get("{$base}/system_status");

            if (!$test->successful()) {
                $this->error("❌ تست اتصال ناموفق — HTTP {$test->status()}");
                $this->line('   پاسخ: ' . mb_substr($test->body(), 0, 200));
                return 1;
            }
            $this->info('✅ اتصال موفق');
        } catch (\Throwable $e) {
            $this->error('❌ اتصال برقرار نشد');
            $this->line('   خطا: ' . $e->getMessage());
            $this->newLine();
            $this->warn('💡 راه‌حل‌ها:');
            $this->line('   ۱. آدرس سایت رو چک کن (مثلاً mashahir.jewelry باز می‌شه؟)');
            $this->line('   ۲. کلیدها رو دوباره چک کن');
            $this->line('   ۳. اگه سایت کند است، از دکمه‌ی Import دستی استفاده کن');
            return 1;
        }

        $this->newLine();
        $page = 1;
        $created = 0;
        $updated = 0;
        $errors = 0;
        $total = 0;

        $bar = $this->output->createProgressBar();
        $bar->start();

        while ($page <= 100) {
            try {
                $response = Http::withBasicAuth($key, $secret)
                    ->timeout($timeout)
                    ->connectTimeout(15)
                    ->retry(2, 3000)
                    ->get("{$base}/products", [
                        'per_page' => $perPage,
                        'page'     => $page,
                        'status'   => 'publish',
                    ]);

                if (!$response->successful()) {
                    $this->newLine();
                    $this->error("HTTP {$response->status()} در صفحه {$page}");
                    break;
                }

                $products = $response->json();
                if (!is_array($products) || empty($products)) break;

                foreach ($products as $wc) {
                    try {
                        $sku = $wc['sku'] ?? null;
                        if (!$sku) $sku = 'WC-' . $wc['id'];

                        $exists = Product::where('sku', $sku)->exists();

                        Product::updateOrCreate(['sku' => $sku], [
                            'sku'            => $sku,
                            'wc_id'          => $wc['id'] ?? null,
                            'name'           => $wc['name'] ?? '',
                            'price'          => (float) ($wc['price'] ?? 0),
                            'regular_price'  => (float) ($wc['regular_price'] ?? 0),
                            'stock_quantity' => $wc['stock_quantity'] ?? null,
                            'stock_status'   => $wc['stock_status'] ?? 'instock',
                            'image_url'      => $wc['images'][0]['src'] ?? null,
                            'weight'         => !empty($wc['weight']) ? (float) $wc['weight'] : null,
                            'categories'     => array_map(fn($c) => ['id' => $c['id'] ?? null, 'name' => $c['name'] ?? ''], $wc['categories'] ?? []),
                            'attributes'     => array_map(fn($a) => ['name' => $a['name'] ?? '', 'options' => $a['options'] ?? []], $wc['attributes'] ?? []),
                            'wc_data'        => $wc,
                            'is_active'      => true,
                            'synced_at'      => now(),
                        ]);

                        if ($exists) $updated++;
                        else         $created++;
                        $total++;
                        $bar->advance();
                    } catch (\Throwable $e) {
                        $errors++;
                    }
                }

                if (count($products) < $perPage) break;
                $page++;
            } catch (\Throwable $e) {
                $this->newLine();
                $this->error('خطا در صفحه ' . $page . ': ' . $e->getMessage());
                $this->newLine();
                $this->warn('⏱️  اتصال کند است. راه‌حل:');
                $this->line('   php artisan shopgun:sync-products --timeout=300 --per-page=20');
                break;
            }
        }

        $bar->finish();
        $this->newLine(2);

        $this->table(
            ['مورد', 'تعداد'],
            [
                ['کل',       $total],
                ['جدید',     $created],
                ['بروز شده', $updated],
                ['خطا',      $errors],
            ]
        );

        if ($total === 0) {
            $this->warn('⚠️ هیچ محصولی دریافت نشد.');
            $this->line('   ممکنه سایت کند باشه یا timeout کم باشه:');
            $this->line('   php artisan shopgun:sync-products --timeout=300');
        }

        return 0;
    }
}
'''

# ═══════════════════════════════════════════════════════════════
# ۳) Import Products from JSON (برای مواقعی که API کند است)
# ═══════════════════════════════════════════════════════════════

IMPORT_JSON_COMMAND = r'''<?php

namespace App\Console\Commands;

use App\Models\Product;
use Illuminate\Console\Command;

class ImportProductsJson extends Command
{
    protected $signature = 'shopgun:import-products-json {file : مسیر فایل JSON}';
    protected $description = 'ایمپورت محصولات از فایل JSON (برای وقتی که WooCommerce کند است)';

    public function handle(): int
    {
        $file = $this->argument('file');
        if (!file_exists($file)) {
            $this->error("فایل پیدا نشد: {$file}");
            return 1;
        }

        $json = json_decode(file_get_contents($file), true);
        if (!is_array($json)) {
            $this->error('JSON نامعتبر');
            return 1;
        }

        // پشتیبانی از چند فرمت
        $products = $json['products'] ?? $json;

        $this->info('📦 ' . count($products) . ' محصول برای ایمپورت');
        $bar = $this->output->createProgressBar(count($products));
        $bar->start();

        $created = 0; $updated = 0; $errors = 0;

        foreach ($products as $p) {
            try {
                $sku = $p['sku'] ?? null;
                if (!$sku) { $errors++; $bar->advance(); continue; }

                $exists = Product::where('sku', $sku)->exists();

                Product::updateOrCreate(['sku' => $sku], [
                    'sku'            => $sku,
                    'wc_id'          => $p['id'] ?? $p['wc_id'] ?? null,
                    'name'           => $p['name'] ?? $p['title'] ?? '',
                    'price'          => (float) ($p['price'] ?? 0),
                    'regular_price'  => (float) ($p['regular_price'] ?? 0),
                    'stock_quantity' => $p['stock_quantity'] ?? $p['stock'] ?? null,
                    'stock_status'   => $p['stock_status'] ?? 'instock',
                    'image_url'      => $p['image_url'] ?? $p['image'] ?? null,
                    'weight'         => !empty($p['weight']) ? (float) $p['weight'] : null,
                    'categories'     => $p['categories'] ?? [],
                    'attributes'     => $p['attributes'] ?? [],
                    'is_active'      => true,
                    'synced_at'      => now(),
                ]);

                if ($exists) $updated++;
                else         $created++;
            } catch (\Throwable $e) {
                $errors++;
            }
            $bar->advance();
        }

        $bar->finish();
        $this->newLine(2);
        $this->table(['مورد', 'تعداد'], [
            ['جدید', $created],
            ['بروز', $updated],
            ['خطا', $errors],
        ]);

        return 0;
    }
}
'''

# ═══════════════════════════════════════════════════════════════
# ۴) Command برای تست سریع (بدون WooCommerce)
# ═══════════════════════════════════════════════════════════════

SEED_TEST_COMMAND = r'''<?php

namespace App\Console\Commands;

use App\Models\Product;
use Illuminate\Console\Command;

class SeedTestProducts extends Command
{
    protected $signature = 'shopgun:seed-test-products {--count=20}';
    protected $description = 'ساخت محصولات تست برای اطمینان از کارکرد جستجو';

    public function handle(): int
    {
        $count = (int) $this->option('count');

        $names = [
            'انگشتر نقره فیروزه', 'گردنبند طلا ۱۸ عیار', 'دستبند نقره عقیق',
            'گوشواره طلا', 'آویز نقره', 'زنجیر طلا', 'انگشتر طلا یاقوت',
            'سرویس نقره', 'پلاک طلا', 'نیم‌ست طلا', 'مدال نقره',
            'انگشتر عقیق', 'گردنبند زمرد', 'دستبند طلا', 'آویز فیروزه',
            'چوکر نقره', 'بازوبند نقره', 'زنجیر نقره', 'انگشتر الماس', 'پلاک نقره',
        ];

        $metals = ['نقره', 'طلا', 'پلاتین'];
        $stones = ['فیروزه', 'عقیق', 'زمرد', 'یاقوت', 'الماس', 'بدون سنگ'];

        for ($i = 0; $i < $count; $i++) {
            $name = $names[array_rand($names)] . ' مدل ' . ($i + 1);
            $sku  = 'TEST-' . str_pad($i + 1, 4, '0', STR_PAD_LEFT);

            Product::updateOrCreate(['sku' => $sku], [
                'sku'          => $sku,
                'name'         => $name,
                'price'        => rand(100, 5000) * 1000,
                'stock_quantity' => rand(0, 20),
                'stock_status' => 'instock',
                'is_active'    => true,
                'synced_at'    => now(),
                'categories'   => [['name' => 'دست‌ساز']],
                'attributes'   => [
                    ['name' => 'فلز',    'options' => [$metals[array_rand($metals)]]],
                    ['name' => 'سنگ',    'options' => [$stones[array_rand($stones)]]],
                    ['name' => 'وزن',    'options' => [rand(1, 15) . ' گرم']],
                ],
            ]);
        }

        $this->info("✅ {$count} محصول تست ساخته شد.");
        $this->line('حالا در فرم سفارش، SKU مثل TEST-0001 رو تایپ کن.');

        return 0;
    }
}
'''

# ═══════════════════════════════════════════════════════════════
# اجرا
# ═══════════════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  Fix Reports + Sync + Test Data                               ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    for rel in [
        "app/Livewire/Reports/Index.php",
        "app/Console/Commands/SyncProducts.php",
    ]:
        backup(rel)

    print("📄 نوشتن فایل‌ها...")
    write("app/Livewire/Reports/Index.php", REPORTS_PHP)
    write("app/Console/Commands/SyncProducts.php", SYNC_COMMAND)
    write("app/Console/Commands/ImportProductsJson.php", IMPORT_JSON_COMMAND)
    write("app/Console/Commands/SeedTestProducts.php", SEED_TEST_COMMAND)

    print("\n" + "═" * 64)
    print("✅ آماده!")
    print("═" * 64)
    print(f"""
📋 حالا این دستورات رو بزن:

  cd {PROJECT}
  php artisan optimize:clear

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔧 ۱) اول محصولات تستی بساز (تا بفهمیم search کار می‌کنه یا نه):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  php artisan shopgun:seed-test-products --count=30

  حالا تو مرورگر → سفارش جدید → تو کادر SKU تایپ کن: TEST

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔧 ۲) برای سینک واقعی از WooCommerce:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  # با timeout بیشتر:
  php artisan shopgun:sync-products --timeout=300 --per-page=20

  # اگه باز timeout داد، یعنی سایت کند است. صبر کن یا از روش زیر استفاده کن.

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🔧 ۳) اگه WooCommerce timeout داد، از دیتابیس سایت خروجی JSON بگیر:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  # فایل products.json رو بذار تو پروژه و بزن:
  php artisan shopgun:import-products-json storage/products.json

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 چه چیزی حل شد:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✅ Reports — خطای HAVING با has() حل شد (SQLite سازگار)
  ✅ Sync — timeout قابل تنظیم + retry + پیام واضح
  ✅ Import JSON — جایگزین وقتی API کند است
  ✅ Seed تست — ۳۰ محصول تستی برای بررسی search

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
💡 چرا mashahir.jewelry timeout می‌ده:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  - سایت یا سرور کند است
  - یا firewall روی api هست
  - یا تعداد محصولات زیاده
  
  پس اول با seed تست، search رو verify کن، بعد sync واقعی رو با timeout 300 بزن.
""")

if __name__ == "__main__":
    main()