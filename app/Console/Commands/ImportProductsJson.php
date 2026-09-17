<?php

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
