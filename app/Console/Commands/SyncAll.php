<?php

namespace App\Console\Commands;

use App\Application\Sync\SyncEngine;
use App\Models\AppSetting;
use Illuminate\Console\Command;

class SyncAll extends Command
{
    protected $signature = 'shopgun:sync-all
        {--type=full : products | catalog | media | full}
        {--mode=full : full | incremental}
        {--media : شامل media هم باشد}';

    protected $description = 'سینک کامل از ووکامرس';

    public function handle(): int
    {
        @set_time_limit(900);

        $type = $this->option('type');
        $mode = $this->option('mode');

        $this->info("🔄 شروع سینک: {$type} ({$mode})");

        try {
            $engine = new SyncEngine();
            $run = $engine->createRun($type, $mode, [
                'media' => $this->option('media'),
            ]);

            $this->info("📋 Run #{$run->id}");

            $bar = $this->output->createProgressBar();
            $bar->start();

            match ($type) {
                'products' => $engine->syncProducts($run),
                'catalog' => $engine->syncCatalog($run),
                'media' => $engine->syncMedia($run),
                'full' => $engine->syncFull($run),
                default => throw new \InvalidArgumentException("نوع نامعتبر: {$type}"),
            };

            $bar->finish();
            $this->newLine(2);

            $run->refresh();

            $this->table(['مورد', 'تعداد'], [
                ['کل', $run->total_items],
                ['جدید', $run->created_items],
                ['بروزرسانی', $run->updated_items],
                ['رد شده', $run->skipped_items],
                ['خطا', $run->failed_items],
            ]);

            if ($run->last_error) {
                $this->warn('خطا: ' . $run->last_error);
            }

            AppSetting::put('woo_last_sync_' . $type, now()->toIso8601String(), 'commerce');
            \Illuminate\Support\Facades\Cache::forget('app_settings_all');

            $this->newLine();
            $this->info('✅ تمام شد');
            return 0;

        } catch (\Throwable $e) {
            $this->error('❌ ' . $e->getMessage());
            return 1;
        }
    }
}
