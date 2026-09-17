<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    public function run(): void
    {
        $this->call([
            RoleAndUserSeeder::class,
            ChannelSeeder::class,
            StoneMetalSeeder::class,
            SampleDataSeeder::class,
        ]);
    }
}
