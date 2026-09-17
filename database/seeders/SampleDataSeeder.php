<?php

namespace Database\Seeders;

use App\Models\Channel;
use App\Models\Customer;
use App\Models\Order;
use Illuminate\Database\Seeder;

class SampleDataSeeder extends Seeder
{
    public function run(): void
    {
        $channels = Channel::all();

        if ($channels->isEmpty()) {
            $this->call(ChannelSeeder::class);
            $channels = Channel::all();
        }

        $customers = [
            ['name' => 'علی رضایی',    'phone' => '09151234567', 'postal_code' => '9317613441', 'address' => 'نیشابور - خیابان امام - پلاک ۱۲'],
            ['name' => 'مریم احمدی',   'phone' => '09121234567', 'postal_code' => '9317613442', 'address' => 'مشهد - بلوار وکیل‌آباد - پلاک ۴۵'],
            ['name' => 'حسن موسوی',    'phone' => '09131234567', 'postal_code' => '9317613443', 'address' => 'تهران - خیابان ولیعصر - پلاک ۷۸'],
            ['name' => 'فاطمه کریمی',  'phone' => '09141234567', 'postal_code' => '9317613444', 'address' => 'اصفهان - چهارباغ - پلاک ۹۰'],
            ['name' => 'رضا نوری',     'phone' => '09151234568', 'postal_code' => '9317613445', 'address' => 'شیراز - بلوار زند - پلاک ۲۳'],
        ];

        $customerModels = [];
        foreach ($customers as $data) {
            $customerModels[] = Customer::updateOrCreate(['phone' => $data['phone']], $data);
        }

        $statuses = ['pending', 'final-check', 'courier'];

        for ($i = 1; $i <= 30; $i++) {
            $customer = $customerModels[array_rand($customerModels)];
            $channel  = $channels->random();

            Order::create([
                'order_number' => (string) (317400 + $i),
                'customer_id'  => $customer->id,
                'channel_id'   => $channel->id,
                'status'       => $statuses[array_rand($statuses)],
                'amount'       => rand(500000, 20000000),
                'insurance'    => rand(500, 5000),
                'phone'        => $customer->phone,
                'address'      => $customer->address,
                'postal_code'  => $customer->postal_code,
            ]);
        }

        $this->command->info('✅ ۵ مشتری و ۳۰ سفارش نمونه ساخته شد.');
    }
}
