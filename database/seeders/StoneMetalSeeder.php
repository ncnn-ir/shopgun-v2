<?php

namespace Database\Seeders;

use App\Models\CertSetting;
use App\Models\Metal;
use App\Models\Stone;
use Illuminate\Database\Seeder;
class StoneMetalSeeder extends Seeder
{
    public function run(): void
    {
        $stones = [
            ['name'=>'فیروزه عجمی',   'en'=>'Turquoise Ajami',   'origin'=>'نیشابور',  'flag'=>'ir', 'balloon'=>'عجمی',      'icon'=>'💠'],
            ['name'=>'فیروزه شجری',   'en'=>'Turquoise Shajari', 'origin'=>'نیشابور',  'flag'=>'ir', 'balloon'=>'شجری',      'icon'=>'💠'],
            ['name'=>'عقیق یمانی',    'en'=>'Yemeni Agate',      'origin'=>'یمن',      'flag'=>'ye', 'balloon'=>'یمانی',     'icon'=>'🔴'],
            ['name'=>'عقیق سلیمانی',  'en'=>'Solomoni Agate',    'origin'=>'یمن',      'flag'=>'ye', 'balloon'=>'سلیمانی',   'icon'=>'❤️'],
            ['name'=>'عقیق شجر',      'en'=>'Dendritic Agate',   'origin'=>'یمن',      'flag'=>'ye', 'balloon'=>'شجری',      'icon'=>'🌿'],
            ['name'=>'در نجف',        'en'=>'Najaf Pearl',       'origin'=>'عراق',     'flag'=>'iq', 'balloon'=>'در نجف',    'icon'=>'⚪'],
            ['name'=>'الماس',         'en'=>'Diamond',           'origin'=>'آفریقا',   'flag'=>'za', 'balloon'=>'الماس',     'icon'=>'💎'],
            ['name'=>'یاقوت سرخ',     'en'=>'Ruby',              'origin'=>'میانمار',  'flag'=>'mm', 'balloon'=>'یاقوت',     'icon'=>'❤️'],
            ['name'=>'یاقوت کبود',    'en'=>'Blue Sapphire',     'origin'=>'سری‌لانکا','flag'=>'lk', 'balloon'=>'کبود',      'icon'=>'🔵'],
            ['name'=>'زمرد',          'en'=>'Emerald',           'origin'=>'کلمبیا',   'flag'=>'co', 'balloon'=>'زمرد',      'icon'=>'🟢'],
            ['name'=>'توپاز',         'en'=>'Topaz',             'origin'=>'برزیل',    'flag'=>'br', 'balloon'=>'توپاز',     'icon'=>'💛'],
            ['name'=>'آمیتیست',       'en'=>'Amethyst',          'origin'=>'برزیل',    'flag'=>'br', 'balloon'=>'بنفش',      'icon'=>'🟣'],
            ['name'=>'چشم ببر',       'en'=>'Tiger Eye',         'origin'=>'آفریقا',   'flag'=>'za', 'balloon'=>'چشم ببر',   'icon'=>'🐯'],
            ['name'=>'لاجورد',        'en'=>'Lapis Lazuli',      'origin'=>'افغانستان','flag'=>'af', 'balloon'=>'لاجورد',    'icon'=>'💙'],
            ['name'=>'حدید',          'en'=>'Hematite',          'origin'=>'ایران',    'flag'=>'ir', 'balloon'=>'حدید',      'icon'=>'⚫'],
            ['name'=>'مرجان',         'en'=>'Coral',             'origin'=>'مدیترانه', 'flag'=>'it', 'balloon'=>'مرجان',     'icon'=>'🟠'],
        ];

        foreach ($stones as $i => $s) {
            Stone::updateOrCreate(
                ['en' => $s['en']],
                array_merge($s, ['is_active' => true, 'sort_order' => $i])
            );
        }

        $metals = [
            ['name'=>'نقره 925',   'en'=>'Silver 925',      'carat'=>'925', 'icon'=>'🥈'],
            ['name'=>'نقره 999',   'en'=>'Fine Silver',     'carat'=>'999', 'icon'=>'⚪'],
            ['name'=>'طلا 18K',    'en'=>'Gold 18K',        'carat'=>'750', 'icon'=>'✨'],
            ['name'=>'طلا 21K',    'en'=>'Gold 21K',        'carat'=>'875', 'icon'=>'🌟'],
            ['name'=>'طلا 22K',    'en'=>'Gold 22K',        'carat'=>'916', 'icon'=>'⭐'],
            ['name'=>'طلا 24K',    'en'=>'Gold 24K',        'carat'=>'999', 'icon'=>'🌟'],
            ['name'=>'پلاتین 950', 'en'=>'Platinum 950',    'carat'=>'950', 'icon'=>'⚙️'],
            ['name'=>'استیل',      'en'=>'Stainless Steel', 'carat'=>'-',   'icon'=>'🔩'],
        ];

        foreach ($metals as $i => $m) {
            Metal::updateOrCreate(
                ['name' => $m['name']],
                array_merge($m, ['is_active' => true, 'sort_order' => $i])
            );
        }

        // تنظیمات پیش‌فرض شناسنامه
        $defaults = [
            'cert.width'      => '6.5',
            'cert.height'     => '6.5',
            'cert.img_w'      => '120',
            'cert.img_h'      => '120',
            'cert.qr_size'    => '40',
            'cert.logo_w'     => '28',
            'cert.logo_h'     => '22',
            'cert.code_font'  => '11',
            'cert.title_font' => '20',
            'cert.desc_font'  => '7',
            'cert.table_label_font' => '8',
            'cert.table_value_font' => '8',
            'cert.hide_desc'  => 'false',
            'cert.bg_image'   => '',
            'cert.desc_image' => '',
            'cert.logo_image' => '',
            'cert.design_data' => '{}',
        ];

        foreach ($defaults as $k => $v) {
            CertSetting::updateOrCreate(
                ['key' => $k],
                ['value' => $v, 'group' => 'certificate']
            );
        }

        $this->command->info('✅ ' . count($stones) . ' سنگ و ' . count($metals) . ' فلز اضافه شد');
    }
}
