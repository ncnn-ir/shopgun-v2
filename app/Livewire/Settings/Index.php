<?php

namespace App\Livewire\Settings;

use App\Models\AppSetting;
use App\Models\Certificate;
use App\Support\CertConfig;
use App\Services\CertRenderer;
use Illuminate\Support\Facades\Cache;
use Livewire\Component;
use Livewire\WithFileUploads;

class Index extends Component
{
    use WithFileUploads;

    public string $tab = 'general';

    // General
    public string $shop_name = '';
    public string $shop_phone = '';
    public string $shop_address = '';
    public string $shop_postal = '';
    public string $shop_email = '';
    public string $currency = 'تومان';

    // Appearance
    public string $theme = 'light';
    public string $primary_color = '#1a5276';
    public string $accent_color = '#c9a84c';
    public string $density = 'normal';
    public string $font_family = 'Vazirmatn';

    // Commerce
    public string $commerce_url = '';
    public string $commerce_key = '';
    public string $commerce_secret = '';
    public array $commerce_test_result = [];

    // Certificate
    public float $cert_width = 6.5;
    public float $cert_height = 6.5;
    public int $cert_img_w = 120;
    public int $cert_img_h = 120;
    public int $cert_qr_size = 40;
    public int $cert_logo_w = 28;
    public int $cert_logo_h = 22;
    public int $cert_code_font = 11;
    public int $cert_title_font = 20;
    public int $cert_desc_font = 7;
    public bool $cert_hide_desc = false;

    public int $cert_col1 = 25;
    public int $cert_col2 = 25;
    public int $cert_col3 = 25;
    public int $cert_col4 = 25;

    // Label
    public int $label_width = 100;
    public int $label_height = 50;

    // Assets
    public string $bg_image = '';
    public array $logo_images = [];
    public int $logo_size = 60;
    public int $logo_offset_x = 50;
    public string $desc_image = '';
    public int $desc_image_w = 120;
    public int $desc_image_h = 80;

    // ★ سنگ و فلز — مقدار پیش‌فرض تا null نباشه
    public array $cert_stones = [];
    public array $cert_metals = [];
    public string $new_stone_name = '';
    public string $new_stone_en = '';
    public string $new_stone_origin = '';
    public string $new_stone_flag = 'ir';
    public string $new_stone_icon = '💎';
    public string $new_metal_name = '';
    public string $new_metal_en = '';
    public string $new_metal_carat = '925';
    public ?int $editing_stone_idx = null;
    public ?int $editing_metal_idx = null;

    // ★ Fetch از سایت
    public string $fetch_status = '';
    public bool $fetching = false;
    public int $fetch_limit = 200;

    // ★ JSON Import
    public string $json_input = '';
    public string $json_status = '';

    // ★ WooCommerce Attributes
    public array $woo_attributes = [];
    public int $woo_stone_attribute_id = 0;
    public string $woo_stone_attribute_name = '';
    public int $woo_metal_attribute_id = 0;
    public string $woo_metal_attribute_name = '';
    public array $woo_stone_terms = [];
    public array $woo_metal_terms = [];
    public string $woo_attr_status = '';
    public bool $woo_attr_loading = false;
    public $json_file = null;

    // Templates
    public array $templates = [];
    public string $new_template_name = '';

    public $logoUpload = null;
    public $descUpload = null;

    public function mount(): void
    {
        try {
            $this->shop_name = (string) AppSetting::get('shop_name', 'جواهری مشاهیر');
            $this->shop_phone = (string) AppSetting::get('shop_phone', '');
            $this->shop_address = (string) AppSetting::get('shop_address', '');
            $this->shop_postal = (string) AppSetting::get('shop_postal', '');
            $this->shop_email = (string) AppSetting::get('shop_email', '');
            $this->currency = (string) AppSetting::get('currency', 'تومان');

            $this->theme = (string) AppSetting::get('theme', 'light');
            $this->primary_color = (string) AppSetting::get('primary_color', '#1a5276');
            $this->accent_color = (string) AppSetting::get('accent_color', '#c9a84c');
            $this->density = (string) AppSetting::get('density', 'normal');
            $this->font_family = (string) AppSetting::get('font_family', 'Vazirmatn');

            $this->commerce_url = (string) AppSetting::get('commerce_url', '');
            $this->commerce_key = (string) AppSetting::get('commerce_key', '');
            $this->commerce_secret = (string) AppSetting::get('commerce_secret', '');

            $this->cert_width = (float) AppSetting::get('cert_width', 6.5);
            $this->cert_height = (float) AppSetting::get('cert_height', 6.5);
            $this->cert_img_w = (int) AppSetting::get('cert_img_w', 120);
            $this->cert_img_h = (int) AppSetting::get('cert_img_h', 120);
            $this->cert_qr_size = (int) AppSetting::get('cert_qr_size', 40);
            $this->cert_logo_w = (int) AppSetting::get('cert_logo_w', 28);
            $this->cert_logo_h = (int) AppSetting::get('cert_logo_h', 22);
            $this->cert_code_font = (int) AppSetting::get('cert_code_font', 11);
            $this->cert_title_font = (int) AppSetting::get('cert_title_font', 20);
            $this->cert_desc_font = (int) AppSetting::get('cert_desc_font', 7);
            $this->cert_hide_desc = (bool) AppSetting::get('cert_hide_desc', false);

            $this->cert_col1 = (int) AppSetting::get('cert_col1', 25);
            $this->cert_col2 = (int) AppSetting::get('cert_col2', 25);
            $this->cert_col3 = (int) AppSetting::get('cert_col3', 25);
            $this->cert_col4 = (int) AppSetting::get('cert_col4', 25);

            $this->label_width = (int) AppSetting::get('label_width', 100);
            $this->label_height = (int) AppSetting::get('label_height', 50);

            $this->bg_image = (string) AppSetting::get('bg_image', '');
            $this->logo_images = (array) AppSetting::get('logo_images', []);
            $this->logo_size = (int) AppSetting::get('logo_size', 60);
            $this->logo_offset_x = (int) AppSetting::get('logo_offset_x', 50);
            $this->desc_image = (string) AppSetting::get('desc_image', '');
            $this->desc_image_w = (int) AppSetting::get('desc_image_w', 120);
            $this->desc_image_h = (int) AppSetting::get('desc_image_h', 80);
        } catch (\Throwable $e) {}

        // ★ همیشه اینا رو لود کن
        $this->woo_stone_attribute_id = (int) AppSetting::get('woo_stone_attribute_id', 0);
        $this->woo_stone_attribute_name = (string) AppSetting::get('woo_stone_attribute_name', '');
        $this->woo_metal_attribute_id = (int) AppSetting::get('woo_metal_attribute_id', 0);
        $this->woo_metal_attribute_name = (string) AppSetting::get('woo_metal_attribute_name', '');

        $this->loadStonesMetals();
        $this->loadTemplates();
    }

    public function setTab(string $tab): void
    {
        $this->tab = $tab;
        if ($tab === 'stones') $this->woo_stone_attribute_id = (int) AppSetting::get('woo_stone_attribute_id', 0);
        $this->woo_stone_attribute_name = (string) AppSetting::get('woo_stone_attribute_name', '');
        $this->woo_metal_attribute_id = (int) AppSetting::get('woo_metal_attribute_id', 0);
        $this->woo_metal_attribute_name = (string) AppSetting::get('woo_metal_attribute_name', '');

        $this->loadStonesMetals();
    }

    /* ═══════════════════════════════════════════════════════════ */
    /* General                                                       */
    /* ═══════════════════════════════════════════════════════════ */
    public function saveGeneral(): void
    {
        AppSetting::putMany([
            'shop_name' => $this->shop_name,
            'shop_phone' => $this->shop_phone,
            'shop_address' => $this->shop_address,
            'shop_postal' => $this->shop_postal,
            'shop_email' => $this->shop_email,
            'currency' => $this->currency,
        ], 'general');
        Cache::forget('app_settings_all');
        $this->dispatch('notify', type: 'success', message: 'ذخیره شد');
    }

    public function saveAppearance(): void
    {
        AppSetting::putMany([
            'theme' => $this->theme,
            'primary_color' => $this->primary_color,
            'accent_color' => $this->accent_color,
            'density' => $this->density,
            'font_family' => $this->font_family,
        ], 'appearance');
        Cache::forget('app_settings_all');
        $this->dispatch('notify', type: 'success', message: 'ذخیره شد');
    }

    public function saveCommerce(): void
    {
        AppSetting::putMany([
            'commerce_url' => $this->commerce_url,
            'commerce_key' => $this->commerce_key,
            'commerce_secret' => $this->commerce_secret,
        ], 'commerce');
        Cache::forget('app_settings_all');
        $this->dispatch('notify', type: 'success', message: 'ذخیره شد');
    }

    public function testCommerce(): void
    {
        $url = trim($this->commerce_url);
        $key = trim($this->commerce_key);
        $secret = trim($this->commerce_secret);

        if (!$url || !$key || !$secret) {
            $this->commerce_test_result = ['ok' => false, 'message' => 'هر سه فیلد الزامی است'];
            return;
        }

        $base = rtrim($url, '/');
        if (!str_contains($base, '/wp-json')) $base .= '/wp-json/wc/v3';

        try {
            $r = \Illuminate\Support\Facades\Http::withBasicAuth($key, $secret)
                ->timeout(20)->connectTimeout(10)->get($base . '/system_status');

            if ($r->successful()) {
                $this->commerce_test_result = ['ok' => true, 'message' => 'اتصال موفق ✅'];
            } else {
                $this->commerce_test_result = ['ok' => false, 'message' => 'HTTP ' . $r->status()];
            }
        } catch (\Throwable $e) {
            $this->commerce_test_result = ['ok' => false, 'message' => $e->getMessage()];
        }
    }

    /* ═══════════════════════════════════════════════════════════ */
    /* Certificate                                                   */
    /* ═══════════════════════════════════════════════════════════ */
    public function saveCertificate(): void
    {
        AppSetting::putMany([
            'cert_width' => $this->cert_width,
            'cert_height' => $this->cert_height,
            'cert_img_w' => $this->cert_img_w,
            'cert_img_h' => $this->cert_img_h,
            'cert_qr_size' => $this->cert_qr_size,
            'cert_logo_w' => $this->cert_logo_w,
            'cert_logo_h' => $this->cert_logo_h,
            'cert_code_font' => $this->cert_code_font,
            'cert_title_font' => $this->cert_title_font,
            'cert_desc_font' => $this->cert_desc_font,
            'cert_col1' => $this->cert_col1,
            'cert_col2' => $this->cert_col2,
            'cert_col3' => $this->cert_col3,
            'cert_col4' => $this->cert_col4,
            'cert_hide_desc' => $this->cert_hide_desc ? '1' : '0',
            'logo_images' => $this->logo_images,
            'logo_size' => $this->logo_size,
            'logo_offset_x' => $this->logo_offset_x,
            'desc_image' => $this->desc_image,
            'desc_image_w' => $this->desc_image_w,
            'desc_image_h' => $this->desc_image_h,
        ], 'certificate');

        Cache::forget('app_settings_all');
        $this->dispatch('notify', type: 'success', message: 'تنظیمات ذخیره شد ✅');
    }

    public function setCertPreset(float $w, float $h): void
    {
        $this->cert_width = $w;
        $this->cert_height = $h;
    }

    /* ═══════════════════════════════════════════════════════════ */
    /* Logos/Desc                                                    */
    /* ═══════════════════════════════════════════════════════════ */
    public function updatedLogoUpload(): void
    {
        if (!$this->logoUpload) return;
        try {
            $path = $this->logoUpload->store('logos', 'public');
            if ($path) {
                $arr = $this->logo_images;
                $arr[] = $path;
                $this->logo_images = array_values($arr);
                AppSetting::put('logo_images', $this->logo_images, 'certificate');
                Cache::forget('app_settings_all');
                $this->logoUpload = null;
                $this->dispatch('notify', type: 'success', message: 'لوگو اضافه شد');
            }
        } catch (\Throwable $e) {
            $this->dispatch('notify', type: 'error', message: $e->getMessage());
        }
    }

    public function removeLogo(int $idx): void
    {
        $arr = $this->logo_images;
        unset($arr[$idx]);
        $this->logo_images = array_values($arr);
        AppSetting::put('logo_images', $this->logo_images, 'certificate');
        Cache::forget('app_settings_all');
    }

    public function updatedDescUpload(): void
    {
        if (!$this->descUpload) return;
        try {
            $path = $this->descUpload->store('desc', 'public');
            if ($path) {
                $this->desc_image = $path;
                AppSetting::put('desc_image', $path, 'certificate');
                Cache::forget('app_settings_all');
                $this->descUpload = null;
                $this->dispatch('notify', type: 'success', message: 'تصویر ذخیره شد');
            }
        } catch (\Throwable $e) {}
    }

    public function saveLogos(): void
    {
        AppSetting::putMany([
            'logo_images' => $this->logo_images,
            'logo_size' => $this->logo_size,
            'logo_offset_x' => $this->logo_offset_x,
            'desc_image' => $this->desc_image,
            'desc_image_w' => $this->desc_image_w,
            'desc_image_h' => $this->desc_image_h,
        ], 'certificate');
        Cache::forget('app_settings_all');
        $this->dispatch('notify', type: 'success', message: 'ذخیره شد');
    }

    /* ═══════════════════════════════════════════════════════════ */
    /* Stones / Metals — ★ این بخش اصلی فیکس                        */
    /* ═══════════════════════════════════════════════════════════ */

    protected function defaultStones(): array
    {
        return [
            ['name' => 'فیروزه عجمی',   'en' => 'Turquoise Ajami',   'origin' => 'نیشابور',   'flag' => 'ir', 'icon' => '💠'],
            ['name' => 'فیروزه شجری',   'en' => 'Turquoise Shajari', 'origin' => 'نیشابور',   'flag' => 'ir', 'icon' => '💠'],
            ['name' => 'فیروزه',        'en' => 'Turquoise',         'origin' => 'نیشابور',   'flag' => 'ir', 'icon' => '💠'],
            ['name' => 'عقیق یمانی',    'en' => 'Yemeni Agate',      'origin' => 'یمن',        'flag' => 'ye', 'icon' => '🔴'],
            ['name' => 'عقیق سلیمانی',  'en' => 'Solomoni Agate',    'origin' => 'یمن',        'flag' => 'ye', 'icon' => '❤️'],
            ['name' => 'عقیق شجر',      'en' => 'Dendritic Agate',   'origin' => 'یمن',        'flag' => 'ye', 'icon' => '🌿'],
            ['name' => 'عقیق',          'en' => 'Agate',             'origin' => 'یمن',        'flag' => 'ye', 'icon' => '🔴'],
            ['name' => 'در نجف',        'en' => 'Najaf Pearl',       'origin' => 'عراق',       'flag' => 'iq', 'icon' => '⚪'],
            ['name' => 'الماس',         'en' => 'Diamond',           'origin' => 'آفریقا',     'flag' => 'za', 'icon' => '💎'],
            ['name' => 'یاقوت سرخ',     'en' => 'Ruby',              'origin' => 'میانمار',    'flag' => 'mm', 'icon' => '❤️'],
            ['name' => 'یاقوت کبود',    'en' => 'Blue Sapphire',     'origin' => 'سری‌لانکا',  'flag' => 'lk', 'icon' => '🔵'],
            ['name' => 'یاقوت',         'en' => 'Sapphire',          'origin' => 'سری‌لانکا',  'flag' => 'lk', 'icon' => '💙'],
            ['name' => 'زمرد',          'en' => 'Emerald',           'origin' => 'کلمبیا',     'flag' => 'co', 'icon' => '🟢'],
            ['name' => 'توپاز',         'en' => 'Topaz',             'origin' => 'برزیل',      'flag' => 'br', 'icon' => '💛'],
            ['name' => 'آمیتیست',       'en' => 'Amethyst',          'origin' => 'برزیل',      'flag' => 'br', 'icon' => '🟣'],
            ['name' => 'اوپال',         'en' => 'Opal',              'origin' => 'استرالیا',   'flag' => 'au', 'icon' => '🌈'],
            ['name' => 'مرجان',         'en' => 'Coral',             'origin' => 'مدیترانه',   'flag' => 'it', 'icon' => '🟠'],
            ['name' => 'لاجورد',        'en' => 'Lapis Lazuli',      'origin' => 'افغانستان',  'flag' => 'af', 'icon' => '💙'],
            ['name' => 'چشم ببر',       'en' => 'Tiger Eye',         'origin' => 'آفریقا',     'flag' => 'za', 'icon' => '🐯'],
            ['name' => 'آکوامارین',     'en' => 'Aquamarine',        'origin' => 'برزیل',      'flag' => 'br', 'icon' => '💧'],
            ['name' => 'سیترین',       'en' => 'Citrine',           'origin' => 'برزیل',      'flag' => 'br', 'icon' => '🍋'],
            ['name' => 'پریدوت',       'en' => 'Peridot',           'origin' => 'مصر',        'flag' => 'eg', 'icon' => '🟩'],
            ['name' => 'مروارید',       'en' => 'Pearl',             'origin' => 'خلیج فارس',  'flag' => 'ir', 'icon' => '⚪'],
            ['name' => 'حدید',          'en' => 'Hematite',          'origin' => 'ایران',      'flag' => 'ir', 'icon' => '⚫'],
            ['name' => 'یشم',           'en' => 'Jade',              'origin' => 'چین',        'flag' => 'cn', 'icon' => '🟢'],
            ['name' => 'رز کوارتز',     'en' => 'Rose Quartz',       'origin' => 'برزیل',      'flag' => 'br', 'icon' => '🌸'],
        ];
    }

    protected function defaultMetals(): array
    {
        return [
            ['name' => 'نقره 925',      'en' => 'Silver 925',      'carat' => '925'],
            ['name' => 'نقره 999',      'en' => 'Fine Silver',     'carat' => '999'],
            ['name' => 'طلا 18K',       'en' => 'Gold 18K',        'carat' => '750'],
            ['name' => 'طلا 21K',       'en' => 'Gold 21K',        'carat' => '875'],
            ['name' => 'طلا 22K',       'en' => 'Gold 22K',        'carat' => '916'],
            ['name' => 'طلا 24K',       'en' => 'Gold 24K',        'carat' => '999'],
            ['name' => 'پلاتین 950',    'en' => 'Platinum 950',    'carat' => '950'],
            ['name' => 'استیل',         'en' => 'Stainless Steel', 'carat' => '-'],
            ['name' => 'رودیم',         'en' => 'Rhodium',         'carat' => '-'],
            ['name' => 'پالادیوم',      'en' => 'Palladium',       'carat' => '-'],
            ['name' => 'برنج',          'en' => 'Brass',           'carat' => '-'],
        ];
    }

    public function loadStonesMetals(): void
    {
        try {
            $s = AppSetting::get('cert_stones', null);
            $this->cert_stones = (is_array($s) && count($s) > 0) ? $s : $this->defaultStones();

            $m = AppSetting::get('cert_metals', null);
            $this->cert_metals = (is_array($m) && count($m) > 0) ? $m : $this->defaultMetals();
        } catch (\Throwable $e) {
            $this->cert_stones = $this->defaultStones();
            $this->cert_metals = $this->defaultMetals();
        }
    }

    public function addStone(): void
    {
        $name = trim($this->new_stone_name);
        if ($name === '') {
            $this->dispatch('notify', type: 'error', message: 'نام سنگ الزامی است');
            return;
        }

        $stone = [
            'name'   => $name,
            'en'     => trim($this->new_stone_en) ?: $name,
            'origin' => trim($this->new_stone_origin) ?: '—',
            'flag'   => $this->new_stone_flag ?: 'ir',
            'icon'   => $this->new_stone_icon ?: '💎',
        ];

        if ($this->editing_stone_idx !== null && isset($this->cert_stones[$this->editing_stone_idx])) {
            $this->cert_stones[$this->editing_stone_idx] = $stone;
            $msg = "سنگ «{$name}» ویرایش شد";
        } else {
            $this->cert_stones[] = $stone;
            $msg = "سنگ «{$name}» اضافه شد";
        }

        AppSetting::put('cert_stones', $this->cert_stones, 'certificate');
        Cache::forget('app_settings_all');

        $this->new_stone_name = '';
        $this->new_stone_en = '';
        $this->new_stone_origin = '';
        $this->new_stone_flag = 'ir';
        $this->new_stone_icon = '💎';
        $this->editing_stone_idx = null;

        $this->woo_stone_attribute_id = (int) AppSetting::get('woo_stone_attribute_id', 0);
        $this->woo_stone_attribute_name = (string) AppSetting::get('woo_stone_attribute_name', '');
        $this->woo_metal_attribute_id = (int) AppSetting::get('woo_metal_attribute_id', 0);
        $this->woo_metal_attribute_name = (string) AppSetting::get('woo_metal_attribute_name', '');

        $this->loadStonesMetals();
        $this->dispatch('notify', type: 'success', message: $msg);
    }

    public function editStone(int $idx): void
    {
        if (!isset($this->cert_stones[$idx])) return;
        $s = $this->cert_stones[$idx];
        $this->editing_stone_idx = $idx;
        $this->new_stone_name = $s['name'] ?? '';
        $this->new_stone_en = $s['en'] ?? '';
        $this->new_stone_origin = $s['origin'] ?? '';
        $this->new_stone_flag = $s['flag'] ?? 'ir';
        $this->new_stone_icon = $s['icon'] ?? '💎';
    }

    public function removeStone(int $idx): void
    {
        if (!isset($this->cert_stones[$idx])) return;
        array_splice($this->cert_stones, $idx, 1);
        AppSetting::put('cert_stones', $this->cert_stones, 'certificate');
        Cache::forget('app_settings_all');
        $this->woo_stone_attribute_id = (int) AppSetting::get('woo_stone_attribute_id', 0);
        $this->woo_stone_attribute_name = (string) AppSetting::get('woo_stone_attribute_name', '');
        $this->woo_metal_attribute_id = (int) AppSetting::get('woo_metal_attribute_id', 0);
        $this->woo_metal_attribute_name = (string) AppSetting::get('woo_metal_attribute_name', '');

        $this->loadStonesMetals();
        $this->dispatch('notify', type: 'success', message: 'حذف شد');
    }

    public function cancelStoneEdit(): void
    {
        $this->editing_stone_idx = null;
        $this->new_stone_name = '';
        $this->new_stone_en = '';
        $this->new_stone_origin = '';
        $this->new_stone_flag = 'ir';
        $this->new_stone_icon = '💎';
    }

    public function addMetal(): void
    {
        $name = trim($this->new_metal_name);
        if ($name === '') {
            $this->dispatch('notify', type: 'error', message: 'نام فلز الزامی است');
            return;
        }

        $metal = [
            'name'  => $name,
            'en'    => trim($this->new_metal_en) ?: $name,
            'carat' => trim($this->new_metal_carat) ?: '925',
        ];

        if ($this->editing_metal_idx !== null && isset($this->cert_metals[$this->editing_metal_idx])) {
            $this->cert_metals[$this->editing_metal_idx] = $metal;
        } else {
            $this->cert_metals[] = $metal;
        }

        AppSetting::put('cert_metals', $this->cert_metals, 'certificate');
        Cache::forget('app_settings_all');

        $this->new_metal_name = '';
        $this->new_metal_en = '';
        $this->new_metal_carat = '925';
        $this->editing_metal_idx = null;

        $this->woo_stone_attribute_id = (int) AppSetting::get('woo_stone_attribute_id', 0);
        $this->woo_stone_attribute_name = (string) AppSetting::get('woo_stone_attribute_name', '');
        $this->woo_metal_attribute_id = (int) AppSetting::get('woo_metal_attribute_id', 0);
        $this->woo_metal_attribute_name = (string) AppSetting::get('woo_metal_attribute_name', '');

        $this->loadStonesMetals();
        $this->dispatch('notify', type: 'success', message: 'ذخیره شد');
    }

    public function editMetal(int $idx): void
    {
        if (!isset($this->cert_metals[$idx])) return;
        $m = $this->cert_metals[$idx];
        $this->editing_metal_idx = $idx;
        $this->new_metal_name = $m['name'] ?? '';
        $this->new_metal_en = $m['en'] ?? '';
        $this->new_metal_carat = $m['carat'] ?? '925';
    }

    public function removeMetal(int $idx): void
    {
        if (!isset($this->cert_metals[$idx])) return;
        array_splice($this->cert_metals, $idx, 1);
        AppSetting::put('cert_metals', $this->cert_metals, 'certificate');
        Cache::forget('app_settings_all');
        $this->woo_stone_attribute_id = (int) AppSetting::get('woo_stone_attribute_id', 0);
        $this->woo_stone_attribute_name = (string) AppSetting::get('woo_stone_attribute_name', '');
        $this->woo_metal_attribute_id = (int) AppSetting::get('woo_metal_attribute_id', 0);
        $this->woo_metal_attribute_name = (string) AppSetting::get('woo_metal_attribute_name', '');

        $this->loadStonesMetals();
        $this->dispatch('notify', type: 'success', message: 'حذف شد');
    }

    /* ═══════════════════════════════════════════════════════════ */
    /* Templates                                                     */
    /* ═══════════════════════════════════════════════════════════ */
    public function loadTemplates(): void
    {
        try {
            $this->templates = (array) AppSetting::get('cert_templates', []);
        } catch (\Throwable $e) {
            $this->templates = [];
        }
    }

    public function saveTemplate(): void
    {
        $name = trim($this->new_template_name);
        if ($name === '') {
            $this->dispatch('notify', type: 'error', message: 'نام طرح الزامی است');
            return;
        }

        $tpl = [
            'id' => uniqid('tpl_'),
            'name' => $name,
            'created_at' => now()->toIso8601String(),
            'settings' => [
                'cert_width' => $this->cert_width,
                'cert_height' => $this->cert_height,
                'cert_img_w' => $this->cert_img_w,
                'cert_img_h' => $this->cert_img_h,
                'cert_qr_size' => $this->cert_qr_size,
                'cert_logo_w' => $this->cert_logo_w,
                'cert_logo_h' => $this->cert_logo_h,
                'cert_code_font' => $this->cert_code_font,
                'cert_title_font' => $this->cert_title_font,
                'cert_desc_font' => $this->cert_desc_font,
                'cert_col1' => $this->cert_col1,
                'cert_col2' => $this->cert_col2,
                'cert_col3' => $this->cert_col3,
                'cert_col4' => $this->cert_col4,
                'cert_hide_desc' => $this->cert_hide_desc,
            ],
        ];

        $list = (array) AppSetting::get('cert_templates', []);
        array_unshift($list, $tpl);
        AppSetting::put('cert_templates', $list, 'certificate');
        Cache::forget('app_settings_all');

        $this->new_template_name = '';
        $this->loadTemplates();
        $this->dispatch('notify', type: 'success', message: "طرح ذخیره شد");
    }

    public function loadTemplate(string $id): void
    {
        $list = (array) AppSetting::get('cert_templates', []);
        $tpl = null;
        foreach ($list as $t) {
            if (($t['id'] ?? '') === $id) { $tpl = $t; break; }
        }
        if (!$tpl) return;

        foreach (($tpl['settings'] ?? []) as $k => $v) {
            if (property_exists($this, $k)) {
                $this->$k = $v;
            }
        }
        $this->dispatch('notify', type: 'success', message: "طرح بارگذاری شد");
    }

    public function deleteTemplate(string $id): void
    {
        $list = (array) AppSetting::get('cert_templates', []);
        $list = array_values(array_filter($list, fn($t) => ($t['id'] ?? '') !== $id));
        AppSetting::put('cert_templates', $list, 'certificate');
        Cache::forget('app_settings_all');
        $this->loadTemplates();
    }

    /* ═══════════════════════════════════════════════════════════ */
    /* Preview                                                       */
    /* ═══════════════════════════════════════════════════════════ */
    public function getPreviewCardProperty(): string
    {
        try {
            CertConfig::$overrideSizes = null;
            CertConfig::$overrideCols = null;
            CertConfig::$overrideHideDesc = null;

            $cert = Certificate::latest('id')->first();
            if (!$cert) {
                $cert = new Certificate([
                    'code' => '123456',
                    'serial' => 'MJ-000000-0000-123456-TUR-A',
                    'stone_name' => 'فیروزه عجمی',
                    'stone_en' => 'Turquoise Ajami',
                    'stone_origin' => 'نیشابور',
                    'stone_flag' => 'ir',
                    'metal' => 'نقره 925',
                    'metal_en' => 'Silver 925',
                    'metal_carat' => '925',
                    'length' => 15,
                    'width' => 12,
                    'weight' => 5.5,
                    'brilliant' => 0,
                    'issued_at' => now(),
                ]);
            }

            CertConfig::$overrideSizes = [
                'width' => $this->cert_width,
                'height' => $this->cert_height,
                'img_w' => $this->cert_img_w,
                'img_h' => $this->cert_img_h,
                'qr_size' => $this->cert_qr_size,
                'logo_w' => $this->cert_logo_w,
                'logo_h' => $this->cert_logo_h,
                'code_font' => $this->cert_code_font,
                'title_font' => $this->cert_title_font,
                'desc_font' => $this->cert_desc_font,
                'imgW' => $this->cert_img_w,
                'imgH' => $this->cert_img_h,
                'qrSize' => $this->cert_qr_size,
                'logoW' => $this->cert_logo_w,
                'logoH' => $this->cert_logo_h,
                'codeFont' => $this->cert_code_font,
                'titleFont' => $this->cert_title_font,
                'descFont' => $this->cert_desc_font,
            ];

            CertConfig::$overrideCols = [
                $this->cert_col1,
                $this->cert_col2,
                $this->cert_col3,
                $this->cert_col4,
            ];

            CertConfig::$overrideHideDesc = $this->cert_hide_desc;

            return CertRenderer::renderCard($cert);
        } catch (\Throwable $e) {
            return '<div style="padding:16px;background:#fee2e2;color:#991b1b;border-radius:8px;font-size:12px;direction:rtl">'
                 . '<b>خطا:</b><br>' . htmlspecialchars($e->getMessage())
                 . '<br><small>' . htmlspecialchars(basename($e->getFile())) . ':' . $e->getLine() . '</small>'
                 . '</div>';
        }
    }


    /* ═══════════════════════════════════════════════════════════
       ★ FETCH STONES FROM WOOCOMMERCE
       ═══════════════════════════════════════════════════════════ */
    public function fetchStonesFromWoo(): void
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

            $r = \Illuminate\Support\Facades\Http::withBasicAuth($key, $secret)
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

        } catch (\Throwable $e) {
            $this->fetch_status = '❌ ' . $e->getMessage();
        }

        $this->fetching = false;
    }

    protected function guessEnName(string $fa): string
    {
        $map = [
            'فیروزه' => 'Turquoise', 'عقیق' => 'Agate', 'الماس' => 'Diamond',
            'یاقوت' => 'Sapphire', 'زمرد' => 'Emerald', 'توپاز' => 'Topaz',
            'آمیتیست' => 'Amethyst', 'اوپال' => 'Opal', 'مرجان' => 'Coral',
            'لاجورد' => 'Lapis Lazuli', 'چشم ببر' => 'Tiger Eye',
            'مروارید' => 'Pearl', 'حدید' => 'Hematite', 'یشم' => 'Jade',
            'آکوامارین' => 'Aquamarine', 'سیترین' => 'Citrine',
            'پریدوت' => 'Peridot', 'رز کوارتز' => 'Rose Quartz',
        ];
        foreach ($map as $k => $v) {
            if (mb_strpos($fa, $k) !== false) return $v;
        }
        return $fa;
    }

    protected function guessCarat(string $metal): string
    {
        if (preg_match('/(18|21|22|24)/', $metal, $m)) {
            return match ($m[1]) {
                '18' => '750', '21' => '875', '22' => '916', '24' => '999',
                default => '925',
            };
        }
        if (mb_strpos($metal, 'نقره') !== false || mb_strpos($metal, 'silver') !== false) {
            return '925';
        }
        if (mb_strpos($metal, 'پلاتین') !== false) return '950';
        return '-';
    }

    /* ═══════════════════════════════════════════════════════════
       ★ JSON IMPORT
       ═══════════════════════════════════════════════════════════ */
    public function importStonesJson(): void
    {
        $this->json_status = '⏳ در حال پردازش...';

        $json = trim($this->json_input);
        if ($json === '') {
            $this->json_status = '❌ JSON خالی است';
            return;
        }

        try {
            $data = json_decode($json, true);
            if (!is_array($data)) {
                $this->json_status = '❌ JSON نامعتبر';
                return;
            }

            // پشتیبانی از چند فرمت: {stones: [...]} یا [...]
            $stones = $data['stones'] ?? $data;

            if (!is_array($stones)) {
                $this->json_status = '❌ ساختار نامعتبر — باید آرایه باشد';
                return;
            }

            $existing = array_column($this->cert_stones, 'name');
            $added = 0;
            $updated = 0;

            foreach ($stones as $s) {
                if (!is_array($s)) continue;
                $name = trim((string) ($s['name'] ?? ''));
                if ($name === '') continue;

                $stone = [
                    'name' => $name,
                    'en' => (string) ($s['en'] ?? $s['name_en'] ?? $name),
                    'origin' => (string) ($s['origin'] ?? '—'),
                    'flag' => (string) ($s['flag'] ?? 'ir'),
                    'icon' => (string) ($s['icon'] ?? '💎'),
                ];

                $idx = array_search($name, $existing, true);
                if ($idx !== false) {
                    $this->cert_stones[$idx] = $stone;
                    $updated++;
                } else {
                    $this->cert_stones[] = $stone;
                    $existing[] = $name;
                    $added++;
                }
            }

            AppSetting::put('cert_stones', $this->cert_stones, 'certificate');
            Cache::forget('app_settings_all');

            $this->json_status = "✅ {$added} سنگ اضافه + {$updated} سنگ بروزرسانی شد";
            $this->json_input = '';
            $this->woo_stone_attribute_id = (int) AppSetting::get('woo_stone_attribute_id', 0);
        $this->woo_stone_attribute_name = (string) AppSetting::get('woo_stone_attribute_name', '');
        $this->woo_metal_attribute_id = (int) AppSetting::get('woo_metal_attribute_id', 0);
        $this->woo_metal_attribute_name = (string) AppSetting::get('woo_metal_attribute_name', '');

        $this->loadStonesMetals();

        } catch (\Throwable $e) {
            $this->json_status = '❌ ' . $e->getMessage();
        }
    }

    public function clearAllStones(): void
    {
        AppSetting::put('cert_stones', [], 'certificate');
        Cache::forget('app_settings_all');
        $this->cert_stones = [];
        $this->dispatch('notify', type: 'success', message: 'همه سنگ‌ها پاک شدند');
    }

    public function resetStonesToDefault(): void
    {
        $this->cert_stones = $this->defaultStones();
        AppSetting::put('cert_stones', $this->cert_stones, 'certificate');
        Cache::forget('app_settings_all');
        $this->dispatch('notify', type: 'success', message: 'بازگشت به پیش‌فرض');
    }


    /* ═══════════════════════════════════════════════════════════
       ★ WOOCOMMERCE ATTRIBUTES
       ═══════════════════════════════════════════════════════════ */

    protected function wooAuth(): ?array
    {
        $url    = trim((string) AppSetting::get('commerce_url', ''));
        $key    = trim((string) AppSetting::get('commerce_key', ''));
        $secret = trim((string) AppSetting::get('commerce_secret', ''));

        if (!$url || !$key || !$secret) return null;

        $base = rtrim($url, '/');
        if (!str_contains($base, '/wp-json')) $base .= '/wp-json/wc/v3';

        return ['base' => $base, 'key' => $key, 'secret' => $secret];
    }

    /**
     * دریافت لیست ویژگی‌های سراسری ووکامرس
     */
    public function fetchWooAttributes(): void
    {
        @set_time_limit(60);
        $this->woo_attr_loading = true;
        $this->woo_attr_status = '⏳ دریافت ویژگی‌ها...';

        try {
            $auth = $this->wooAuth();
            if (!$auth) {
                $this->woo_attr_status = '❌ اطلاعات کامرس پر نشده';
                $this->woo_attr_loading = false;
                return;
            }

            $r = \Illuminate\Support\Facades\Http::withBasicAuth($auth['key'], $auth['secret'])
                ->timeout(20)
                ->connectTimeout(10)
                ->get("{$auth['base']}/products/attributes");

            if (!$r->successful()) {
                $this->woo_attr_status = '❌ خطای HTTP ' . $r->status();
                $this->woo_attr_loading = false;
                return;
            }

            $raw = $r->json() ?? [];

            $this->woo_attributes = array_map(function ($a) {
                return [
                    'id' => (int) ($a['id'] ?? 0),
                    'name' => (string) ($a['name'] ?? ''),
                    'slug' => (string) ($a['slug'] ?? ''),
                    'type' => (string) ($a['type'] ?? 'select'),
                    'order_by' => (string) ($a['order_by'] ?? 'menu_order'),
                    'has_archives' => (bool) ($a['has_archives'] ?? false),
                ];
            }, $raw);

            $this->woo_attr_status = "✅ " . count($this->woo_attributes) . " ویژگی پیدا شد";

        } catch (\Throwable $e) {
            $this->woo_attr_status = '❌ ' . $e->getMessage();
        }

        $this->woo_attr_loading = false;
    }

    /**
     * دریافت اصطلاحات (terms) یک ویژگی
     */
    protected function fetchTermsFor(int $attrId): array
    {
        try {
            $auth = $this->wooAuth();
            if (!$auth) return [];

            $r = \Illuminate\Support\Facades\Http::withBasicAuth($auth['key'], $auth['secret'])
                ->timeout(30)
                ->connectTimeout(10)
                ->get("{$auth['base']}/products/attributes/{$attrId}/terms", [
                    'per_page' => 100,
                ]);

            if (!$r->successful()) return [];

            $raw = $r->json() ?? [];
            return array_map(function ($t) {
                return [
                    'id' => (int) ($t['id'] ?? 0),
                    'name' => (string) ($t['name'] ?? ''),
                    'slug' => (string) ($t['slug'] ?? ''),
                    'count' => (int) ($t['count'] ?? 0),
                ];
            }, $raw);

        } catch (\Throwable $e) {
            return [];
        }
    }

    /**
     * انتخاب ویژگی برای سنگ
     */
    public function pickStoneAttribute(int $attrId): void
    {
        $this->woo_stone_attribute_id = $attrId;

        // پیدا کردن نام
        $this->woo_stone_attribute_name = '';
        foreach ($this->woo_attributes as $a) {
            if ($a['id'] === $attrId) {
                $this->woo_stone_attribute_name = $a['name'];
                break;
            }
        }

        // دریافت terms
        $this->woo_stone_terms = $this->fetchTermsFor($attrId);

        AppSetting::put('woo_stone_attribute_id', $attrId, 'commerce');
        AppSetting::put('woo_stone_attribute_name', $this->woo_stone_attribute_name, 'commerce');
        Cache::forget('app_settings_all');

        $this->woo_attr_status = "✅ ویژگی سنگ: «{$this->woo_stone_attribute_name}» با " . count($this->woo_stone_terms) . " اصطلاح";
    }

    /**
     * انتخاب ویژگی برای فلز
     */
    public function pickMetalAttribute(int $attrId): void
    {
        $this->woo_metal_attribute_id = $attrId;

        $this->woo_metal_attribute_name = '';
        foreach ($this->woo_attributes as $a) {
            if ($a['id'] === $attrId) {
                $this->woo_metal_attribute_name = $a['name'];
                break;
            }
        }

        $this->woo_metal_terms = $this->fetchTermsFor($attrId);

        AppSetting::put('woo_metal_attribute_id', $attrId, 'commerce');
        AppSetting::put('woo_metal_attribute_name', $this->woo_metal_attribute_name, 'commerce');
        Cache::forget('app_settings_all');

        $this->woo_attr_status = "✅ ویژگی فلز: «{$this->woo_metal_attribute_name}» با " . count($this->woo_metal_terms) . " اصطلاح";
    }

    /**
     * اعمال اصطلاحات انتخاب‌شده به عنوان لیست سنگ‌ها
     */
    public function applyWooTermsAsStones(): void
    {
        if (empty($this->woo_stone_terms)) {
            $this->woo_attr_status = '❌ اول یک ویژگی سنگ انتخاب کن';
            return;
        }

        $existingNames = array_column($this->cert_stones, 'name');
        $added = 0;

        foreach ($this->woo_stone_terms as $t) {
            $name = trim($t['name']);
            if ($name === '') continue;
            if (in_array($name, $existingNames, true)) continue;

            // تلاش برای تشخیص origin/flag/icon
            $meta = $this->guessStoneMeta($name);

            $this->cert_stones[] = [
                'name' => $name,
                'en' => $this->guessEnName($name),
                'origin' => $meta['origin'],
                'flag' => $meta['flag'],
                'icon' => $meta['icon'],
            ];
            $existingNames[] = $name;
            $added++;
        }

        AppSetting::put('cert_stones', $this->cert_stones, 'certificate');
        Cache::forget('app_settings_all');

        $this->woo_attr_status = "✅ {$added} سنگ از ویژگی‌های ووکامرس اضافه شد";
        $this->loadStonesMetals();
    }

    /**
     * اعمال اصطلاحات فلز
     */
    public function applyWooTermsAsMetals(): void
    {
        if (empty($this->woo_metal_terms)) {
            $this->woo_attr_status = '❌ اول یک ویژگی فلز انتخاب کن';
            return;
        }

        $existing = array_column($this->cert_metals, 'name');
        $added = 0;

        foreach ($this->woo_metal_terms as $t) {
            $name = trim($t['name']);
            if ($name === '') continue;
            if (in_array($name, $existing, true)) continue;

            $this->cert_metals[] = [
                'name' => $name,
                'en' => $name,
                'carat' => $this->guessCarat($name),
            ];
            $existing[] = $name;
            $added++;
        }

        AppSetting::put('cert_metals', $this->cert_metals, 'certificate');
        Cache::forget('app_settings_all');

        $this->woo_attr_status = "✅ {$added} فلز اضافه شد";
        $this->loadStonesMetals();
    }

    /**
     * حدس origin/flag/icon سنگ بر اساس نام
     */
    protected function guessStoneMeta(string $name): array
    {
        $map = [
            'فیروزه' => ['origin' => 'نیشابور', 'flag' => 'ir', 'icon' => '💠'],
            'عقیق' => ['origin' => 'یمن', 'flag' => 'ye', 'icon' => '🔴'],
            'در نجف' => ['origin' => 'عراق', 'flag' => 'iq', 'icon' => '⚪'],
            'الماس' => ['origin' => 'آفریقا', 'flag' => 'za', 'icon' => '💎'],
            'یاقوت سرخ' => ['origin' => 'میانمار', 'flag' => 'mm', 'icon' => '❤️'],
            'یاقوت کبود' => ['origin' => 'سری‌لانکا', 'flag' => 'lk', 'icon' => '🔵'],
            'یاقوت' => ['origin' => 'سری‌لانکا', 'flag' => 'lk', 'icon' => '💙'],
            'زمرد' => ['origin' => 'کلمبیا', 'flag' => 'co', 'icon' => '🟢'],
            'توپاز' => ['origin' => 'برزیل', 'flag' => 'br', 'icon' => '💛'],
            'آمیتیست' => ['origin' => 'برزیل', 'flag' => 'br', 'icon' => '🟣'],
            'اوپال' => ['origin' => 'استرالیا', 'flag' => 'au', 'icon' => '🌈'],
            'مرجان' => ['origin' => 'مدیترانه', 'flag' => 'it', 'icon' => '🟠'],
            'لاجورد' => ['origin' => 'افغانستان', 'flag' => 'af', 'icon' => '💙'],
            'چشم ببر' => ['origin' => 'آفریقا', 'flag' => 'za', 'icon' => '🐯'],
            'آکوامارین' => ['origin' => 'برزیل', 'flag' => 'br', 'icon' => '💧'],
            'سیترین' => ['origin' => 'برزیل', 'flag' => 'br', 'icon' => '🍋'],
            'پریدوت' => ['origin' => 'مصر', 'flag' => 'eg', 'icon' => '🟩'],
            'مروارید' => ['origin' => 'خلیج فارس', 'flag' => 'ir', 'icon' => '⚪'],
            'حدید' => ['origin' => 'ایران', 'flag' => 'ir', 'icon' => '⚫'],
            'یشم' => ['origin' => 'چین', 'flag' => 'cn', 'icon' => '🟢'],
            'رز کوارتز' => ['origin' => 'برزیل', 'flag' => 'br', 'icon' => '🌸'],
        ];

        foreach ($map as $k => $v) {
            if (mb_strpos($name, $k) !== false) return $v;
        }

        return ['origin' => '—', 'flag' => 'ir', 'icon' => '💎'];
    }

    public function render()
    {
        return view('livewire.settings.index', [
            'stats' => [
                'php' => PHP_VERSION,
                'laravel' => app()->version(),
                'orders' => \App\Models\Order::count(),
                'customers' => \App\Models\Customer::count(),
                'products' => \App\Models\Product::count(),
                'certificates' => \App\Models\Certificate::count(),
            ],
        ])->layout('components.layouts.app');
    }
}
