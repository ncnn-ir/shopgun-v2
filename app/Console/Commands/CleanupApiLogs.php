<?php

namespace App\Console\Commands;

use App\Models\ApiLog;
use Illuminate\Console\Command;

class CleanupApiLogs extends Command
{
    protected $signature = 'shopgun:cleanup-api-logs {--days=7}';
    protected $description = 'حذف لاگ‌های API قدیمی';

    public function handle(): int
    {
        $days = (int) $this->option('days');
        $count = ApiLog::where('created_at', '<', now()->subDays($days))->delete();
        $this->info("{$count} لاگ قدیمی‌تر از {$days} روز حذف شد.");
        return 0;
    }
}
