<?php

namespace Database\Seeders;

use App\Models\Channel;
use Illuminate\Database\Seeder;

class ChannelSeeder extends Seeder
{
    public function run(): void
    {
        $channels = [
            ['key' => 'website',   'name' => 'سایت',       'icon' => '🌐', 'color' => '#1a5276'],
            ['key' => 'instagram', 'name' => 'اینستاگرام', 'icon' => '📷', 'color' => '#e91e63'],
            ['key' => 'telegram',  'name' => 'تلگرام',     'icon' => '✈️', 'color' => '#29b6f6'],
            ['key' => 'phone',     'name' => 'تلفنی',      'icon' => '📞', 'color' => '#66bb6a'],
            ['key' => 'direct',    'name' => 'حضوری',      'icon' => '🤝', 'color' => '#ffb74d'],
            ['key' => 'basalam',   'name' => 'باسلام',     'icon' => '🛍️', 'color' => '#00b894'],
        ];

        foreach ($channels as $i => $c) {
            Channel::updateOrCreate(
                ['key' => $c['key']],
                array_merge($c, ['sort_order' => $i, 'is_active' => true])
            );
        }
    }
}
