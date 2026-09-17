# -*- coding: utf-8 -*-
from pathlib import Path
import time, re

ROOT = Path(r'D:\prodo\shopgun-v2.2')

p = ROOT / 'app' / 'Livewire' / 'Settings' / 'Index.php'
if p.exists():
    txt = p.read_text(encoding='utf-8')

    # ★ جایگزینی کل متد fetchStonesFromWoo
    old = re.search(
        r'    public function fetchStonesFromWoo\(\): void\s*\{.*?\n    \}',
        txt,
        flags=re.DOTALL
    )

    if old:
        new_method = '''    public function fetchStonesFromWoo(): void
    {
        // ★ افزایش زمان اجرا
        @set_time_limit(120);
        @ini_set('max_execution_time', '120');

        $this->fetching = true;
        $this->fetch_status = '⏳ در حال دریافت...';

        try {
            $url    = trim((string) AppSetting::get('commerce_url', ''));
            $key    = trim((string) AppSetting::get('commerce_key', ''));
            $secret = trim((string) AppSetting::get('commerce_secret', ''));

            if (!$url || !$key || !$secret) {
                $this->fetch_status = '❌ تنظیمات کامرس پر نشده';
                $this->fetching = false;
                return;
            }

            $base = rtrim($url, '/');
            if (!str_contains($base, '/wp-json')) $base .= '/wp-json/wc/v3';

            // ★ فقط ۱ صفحه — per_page 100 (کمتر، سریع‌تر)
            $this->fetch_status = '⏳ دریافت ۱۰۰ محصول از سایت...';

            $r = \\Illuminate\\Support\\Facades\\Http::withBasicAuth($key, $secret)
                ->timeout(45)
                ->connectTimeout(15)
                ->get("{$base}/products", [
                    'per_page' => 100,
                    'page' => 1,
                    'status' => 'publish',
                ]);

            if (!$r->successful()) {
                $this->fetch_status = '❌ خطای HTTP ' . $r->status();
                $this->fetching = false;
                return;
            }

            $products = $r->json() ?? [];
            if (empty($products)) {
                $this->fetch_status = '❌ محصولی دریافت نشد';
                $this->fetching = false;
                return;
            }

            // ★ استخراج سریع سنگ‌ها از نام فقط (نه از attributes پیچیده)
            $stoneKeywords = [
                'فیروزه عجمی'   => ['origin' => 'نیشابور',   'flag' => 'ir', 'icon' => '💠'],
                'فیروزه شجری'   => ['origin' => 'نیشابور',   'flag' => 'ir', 'icon' => '💠'],
                'فیروزه'        => ['origin' => 'نیشابور',   'flag' => 'ir', 'icon' => '💠'],
                'عقیق یمانی'    => ['origin' => 'یمن',        'flag' => 'ye', 'icon' => '🔴'],
                'عقیق سلیمانی'  => ['origin' => 'یمن',        'flag' => 'ye', 'icon' => '❤️'],
                'عقیق شجر'      => ['origin' => 'یمن',        'flag' => 'ye', 'icon' => '🌿'],
                'عقیق'          => ['origin' => 'یمن',        'flag' => 'ye', 'icon' => '🔴'],
                'در نجف'        => ['origin' => 'عراق',       'flag' => 'iq', 'icon' => '⚪'],
                'الماس'         => ['origin' => 'آفریقا',     'flag' => 'za', 'icon' => '💎'],
                'یاقوت سرخ'     => ['origin' => 'میانمار',    'flag' => 'mm', 'icon' => '❤️'],
                'یاقوت کبود'    => ['origin' => 'سری‌لانکا',  'flag' => 'lk', 'icon' => '🔵'],
                'یاقوت'         => ['origin' => 'سری‌لانکا',  'flag' => 'lk', 'icon' => '💙'],
                'زمرد'          => ['origin' => 'کلمبیا',     'flag' => 'co', 'icon' => '🟢'],
                'توپاز'         => ['origin' => 'برزیل',      'flag' => 'br', 'icon' => '💛'],
                'آمیتیست'       => ['origin' => 'برزیل',      'flag' => 'br', 'icon' => '🟣'],
                'اوپال'         => ['origin' => 'استرالیا',   'flag' => 'au', 'icon' => '🌈'],
                'مرجان'         => ['origin' => 'مدیترانه',   'flag' => 'it', 'icon' => '🟠'],
                'لاجورد'        => ['origin' => 'افغانستان',  'flag' => 'af', 'icon' => '💙'],
                'چشم ببر'       => ['origin' => 'آفریقا',     'flag' => 'za', 'icon' => '🐯'],
                'آکوامارین'     => ['origin' => 'برزیل',      'flag' => 'br', 'icon' => '💧'],
                'سیترین'       => ['origin' => 'برزیل',      'flag' => 'br', 'icon' => '🍋'],
                'پریدوت'       => ['origin' => 'مصر',        'flag' => 'eg', 'icon' => '🟩'],
                'مروارید'       => ['origin' => 'خلیج فارس',  'flag' => 'ir', 'icon' => '⚪'],
                'حدید'          => ['origin' => 'ایران',      'flag' => 'ir', 'icon' => '⚫'],
                'یشم'           => ['origin' => 'چین',        'flag' => 'cn', 'icon' => '🟢'],
                'رز کوارتز'     => ['origin' => 'برزیل',      'flag' => 'br', 'icon' => '🌸'],
            ];

            $found = [];
            foreach ($products as $p) {
                $name = $p['name'] ?? '';
                foreach ($stoneKeywords as $key2 => $meta) {
                    if (mb_strpos($name, $key2) !== false && !isset($found[$key2])) {
                        $found[$key2] = [
                            'name' => $key2,
                            'en' => $this->guessEnName($key2),
                            'origin' => $meta['origin'],
                            'flag' => $meta['flag'],
                            'icon' => $meta['icon'],
                        ];
                    }
                }
            }

            if (empty($found)) {
                $this->fetch_status = "❌ از " . count($products) . " محصول، سنگ جدیدی پیدا نشد";
                $this->fetching = false;
                return;
            }

            // ادغام با لیست موجود
            $existingNames = array_column($this->cert_stones, 'name');
            $added = 0;
            foreach ($found as $s) {
                if (!in_array($s['name'], $existingNames, true)) {
                    $this->cert_stones[] = $s;
                    $added++;
                }
            }

            AppSetting::put('cert_stones', $this->cert_stones, 'certificate');
            Cache::forget('app_settings_all');

            $this->fetch_status = "✅ {$added} سنگ جدید از " . count($products) . " محصول اضافه شد";

        } catch (\\Throwable $e) {
            $this->fetch_status = '❌ ' . $e->getMessage();
        }

        $this->fetching = false;
    }'''
        txt = txt[:old.start()] + new_method + txt[old.end():]
        p.write_text(txt, encoding='utf-8')
        print("[OK] fetchStonesFromWoo - بهینه شد")
    else:
        print("[WARN] متد پیدا نشد")

print()
print("Run:")
print("  php artisan view:clear")
print("  php artisan optimize:clear")
print("  php artisan serve")