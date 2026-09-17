<?php

namespace App\Console\Commands;

use App\Models\AppSetting;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Http;

class TestWooSearch extends Command
{
    protected $signature = 'test:woo-search {q?}';
    protected $description = 'تست جستجوی محصول در WooCommerce';

    public function handle(): int
    {
        $q = $this->argument('q') ?: 'طلا';

        $url = AppSetting::get('commerce_url');
        $key = AppSetting::get('commerce_key');
        $secret = AppSetting::get('commerce_secret');

        $base = rtrim($url, '/');
        if (!str_contains($base, '/wp-json')) $base .= '/wp-json/wc/v3';

        $this->info("جستجو برای: {$q}");

        $r = Http::withBasicAuth($key, $secret)
            ->timeout(15)
            ->get("{$base}/products", ['search' => $q, 'per_page' => 10]);

        $this->info("HTTP: " . $r->status());

        $json = $r->json();
        $this->info("یافت شد: " . count($json));

        foreach (array_slice($json, 0, 5) as $p) {
            $this->line("- [{$p['id']}] SKU: {$p['sku']} | {$p['name']} | {$p['price']}");
        }

        return 0;
    }
}