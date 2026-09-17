<?php

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
