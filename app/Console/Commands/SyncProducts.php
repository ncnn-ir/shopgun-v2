<?php

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
