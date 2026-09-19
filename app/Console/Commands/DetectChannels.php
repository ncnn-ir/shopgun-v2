<?php

namespace App\Console\Commands;

use App\Application\Orders\ChannelDetector;
use App\Models\Order;
use Illuminate\Console\Command;

class DetectChannels extends Command
{
    protected $signature = 'shopgun:detect-channels {--force : همه سفارشات را دوباره بررسی کن}';
    protected $description = 'تشخیص خودکار کانال فروش برای سفارشات';

    public function handle(ChannelDetector $detector): int
    {
        $this->info('🔍 در حال تشخیص کانال فروش...');
        $stats = $detector->backfill((bool) $this->option('force'));

        if (empty($stats)) {
            $this->warn('هیچ سفارشی تغییر نکرد.');
        } else {
            $this->table(['کانال', 'تعداد'], collect($stats)->map(fn($c, $k) => [$k, $c])->values()->toArray());
        }

        $total = Order::count();
        $withChannel = Order::whereNotNull('sales_channel')->where('sales_channel', '!=', '')->count();
        $this->info("✅ {$withChannel} از {$total} سفارش کانال دارند.");

        return self::SUCCESS;
    }
}
