<?php

namespace App\Console\Commands;

use App\Models\Customer;
use Illuminate\Console\Command;

class MigrateLegacyCustomerData extends Command
{
    protected $signature = 'shopgun:migrate-legacy-customer-data
                            {--force : بدون تأییدیه اجرا شود}';

    protected $description = 'مهاجرت داده‌های قدیمی مشتریان به جدول‌های جدید (customer_phones, customer_addresses)';

    public function handle(): int
    {
        $total = Customer::count();
        if ($total === 0) {
            $this->info('هیچ مشتری‌ای وجود ندارد.');
            return 0;
        }

        if (!$this->option('force') && !$this->confirm("{$total} مشتری پردازش می‌شود. ادامه؟")) {
            return 0;
        }

        $bar = $this->output->createProgressBar($total);
        $bar->start();

        $phoneAdded = 0;
        $addrAdded  = 0;
        $skipped    = 0;

        Customer::with(['phones', 'addresses'])->chunk(200, function ($customers) use (&$phoneAdded, &$addrAdded, &$skipped, $bar) {
            foreach ($customers as $c) {
                // تلفن
                if ($c->phones->isEmpty() && !empty($c->phone)) {
                    $cp = $c->addPhone($c->phone, 'اصلی', true);
                    if ($cp) $phoneAdded++;
                } else {
                    $skipped++;
                }

                // آدرس
                if ($c->addresses->isEmpty()) {
                    $addr = $c->address ?? null;
                    $postal = $c->postal_code ?? $c->postal ?? null;
                    if ($addr || $postal) {
                        $c->addAddress([
                            'address'     => $addr,
                            'postal_code' => $postal,
                        ], true);
                        $addrAdded++;
                    }
                }

                $bar->advance();
            }
        });

        $bar->finish();
        $this->newLine(2);

        $this->table(
            ['مورد', 'تعداد'],
            [
                ['تلفن اضافه شده',    $phoneAdded],
                ['آدرس اضافه شده',    $addrAdded],
                ['بدون تغییر',         $skipped],
                ['کل مشتریان',        $total],
            ]
        );

        return 0;
    }
}
