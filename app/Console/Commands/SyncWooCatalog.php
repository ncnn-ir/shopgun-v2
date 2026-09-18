<?php

namespace App\Console\Commands;

use App\Application\Woo\WooCatalogService;
use App\Models\AppSetting;
use Illuminate\Console\Command;

class SyncWooCatalog extends Command
{
    protected $signature = 'shopgun:sync-catalog';
    protected $description = 'سینک دسته‌ها، ویژگی‌ها، اصطلاحات و کاربران ووکامرس';

    public function handle(): int
    {
        @set_time_limit(600);

        $this->info('🔄 شروع سینک کاتالوگ...');

        try {
            $service = new WooCatalogService();
            $report = $service->syncAll();

            $this->newLine();
            $this->table(['مورد', 'تعداد'], [
                ['دسته‌ها', $report['categories']],
                ['ویژگی‌ها', $report['attributes']],
                ['اصطلاحات', $report['terms']],
                ['کاربران', $report['users']],
            ]);

            if (!empty($report['errors'])) {
                $this->newLine();
                $this->warn('خطاها:');
                foreach ($report['errors'] as $err) {
                    $this->line('  • ' . $err);
                }
            }

            AppSetting::put('woo_catalog_last_sync', now()->toIso8601String(), 'commerce');
            \Illuminate\Support\Facades\Cache::forget('app_settings_all');

            $this->newLine();
            $this->info('✅ سینک کامل شد');
            return 0;

        } catch (\Throwable $e) {
            $this->error('❌ ' . $e->getMessage());
            return 1;
        }
    }
}
