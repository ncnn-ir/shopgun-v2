<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * مهاجرت داده‌های قدیمی Customer به جداول جدید
     */
    public function up(): void
    {
        if (!Schema::hasTable('customers')) return;
        if (!Schema::hasTable('customer_phones')) return;

        $now = now();

        // مشتریانی که حداقل یک phone دارند ولی هنوز در customer_phones نیستند
        $customers = DB::table('customers')
            ->whereNotNull('phone')
            ->where('phone', '!=', '')
            ->get();

        $insertPhones = [];
        $insertAddresses = [];

        foreach ($customers as $c) {
            // بررسی اینکه آیا از قبل رکورد تلفن دارد
            $exists = DB::table('customer_phones')
                ->where('customer_id', $c->id)
                ->exists();
            if ($exists) continue;

            $normalized = $this->normalizePhone($c->phone);
            if (!$normalized) continue;

            $insertPhones[] = [
                'customer_id' => $c->id,
                'phone'       => $normalized,
                'label'       => 'اصلی',
                'is_primary'  => true,
                'created_at'  => $now,
                'updated_at'  => $now,
            ];

            // آدرس قدیمی
            $addr = $c->address ?? null;
            $postal = $c->postal_code ?? $c->postal ?? null;

            if ($addr || $postal) {
                $addrExists = DB::table('customer_addresses')
                    ->where('customer_id', $c->id)
                    ->exists();
                if (!$addrExists) {
                    $insertAddresses[] = [
                        'customer_id'  => $c->id,
                        'label'        => 'اصلی',
                        'province'     => null,
                        'city'         => null,
                        'address'      => $addr,
                        'postal_code'  => $postal,
                        'is_primary'   => true,
                        'created_at'   => $now,
                        'updated_at'   => $now,
                    ];
                }
            }
        }

        foreach (array_chunk($insertPhones, 500) as $chunk) {
            DB::table('customer_phones')->insert($chunk);
        }
        foreach (array_chunk($insertAddresses, 500) as $chunk) {
            DB::table('customer_addresses')->insert($chunk);
        }
    }

    protected function normalizePhone(?string $phone): string
    {
        $s = preg_replace('/\D/', '', (string) $phone);
        if (str_starts_with($s, '0098')) $s = substr($s, 4);
        elseif (str_starts_with($s, '98') && strlen($s) > 10) $s = substr($s, 2);
        if (str_starts_with($s, '0') && strlen($s) > 10) $s = substr($s, 1);
        return $s;
    }

    public function down(): void
    {
        DB::table('customer_phones')->truncate();
        DB::table('customer_addresses')->truncate();
    }
};
