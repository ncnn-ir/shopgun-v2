<?php

namespace App\Console\Commands;

use App\Models\Certificate;
use App\Models\CertSetting;
use Illuminate\Console\Command;

class ApplyGlobalDesign extends Command
{
    protected $signature = 'cert:apply-global {--reset-design : حذف design_data اختصاصی}';
    protected $description = 'اعمال طرح پیش‌فرض روی همه شناسنامه‌ها';

    public function handle(): int
    {
        $global = CertSetting::get('global_design', null);

        if (!$global) {
            $this->error('طرح پیش‌فرض وجود ندارد. اول در ویرایشگر ذخیره کن.');
            return 1;
        }

        $count = Certificate::count();

        if ($this->option('reset-design')) {
            $affected = Certificate::whereNotNull('design_data')->update(['design_data' => null]);
            $this->info("{$affected} شناسنامه از طرح اختصاصی پاک شد.");
        }

        $this->info("✅ طرح پیش‌فرض روی {$count} شناسنامه اعمال شد.");
        return 0;
    }
}
