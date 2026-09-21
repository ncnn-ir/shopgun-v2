<?php

namespace App\Livewire\Settings;

use App\Models\AppSetting;
use App\Models\Certificate;
use App\Support\CertConfig;
use App\Services\CertRenderer;
use Illuminate\Support\Facades\Cache;
use Livewire\Component;
use Livewire\WithFileUploads;

/**
 * ★ Settings Hub v6
 * ناوبری دو سطحی:
 *   Level 1: 4 گروه (System, Commerce, Certificates, Catalog)
 *   Level 2: زیر-تب‌های هر گروه
 */
class Index extends Component
{
    // ─── تنظیمات ظاهری (auto-added) ───
    public $ui_style = 'material';

    use WithFileUploads;

    // ★ ناوبری
    public string $group = 'system';
    public string $tab = 'general';

    // ═══════════════════════════════════════════════════════════
    // GROUPS and TABS
    // ═══════════════════════════════════════════════════════════
    public const GROUPS = [
        'system' => [
            'label' => 'سیستم',
            'icon' => '⚙️',
            'desc' => 'تنظیمات عمومی و ظاهر',
            'tabs' => [
                'general' => ['⚙️', 'عمومی'],
                'appearance' => ['🎨', 'ظاهر'],
                'notifications' => ['🔔', 'اعلان‌ها'],
                'maintenance' => ['🔧', 'نگهداری'],
            ],
        ],
        'commerce' => [
            'label' => 'فروشگاه',
            'icon' => '🔌',
            'desc' => 'ووکامرس، سینک، مانیتور',
            'tabs' => [
                'woo' => ['🔌', 'اتصال ووکامرس'],
                'sync' => ['🔄', 'سینک و ایمپورت'],
                'api-monitor' => ['📊', 'رصد API'],
            ],
        ],
        'certificates' => [
            'label' => 'شناسنامه',
            'icon' => '💎',
            'desc' => 'قالب، اندازه، سنگ/فلز',
            'tabs' => [
                'cert-templates' => ['🎨', 'قالب‌ها'],
                'cert-sizes' => ['📏', 'اندازه و ظاهر'],
                'catalog' => ['💠', 'سنگ و فلز'],
                'labels' => ['🏷️', 'برچسب پستی'],
                'assets' => ['🖼️', 'تصاویر و لوگو'],
            ],
        ],
        'health' => [
            'label' => 'سلامت',
            'icon' => '🩺',
            'desc' => 'بهداشت سیستم',
            'tabs' => [
                'health' => ['🩺', 'سلامت سیستم'],
                'logs' => ['📜', 'لاگ‌ها'],
                'backup' => ['💾', 'پشتیبان'],
            ],
        ],
    ];

    // ═══════════════════════════════════════════════════════════
    // Properties (همه‌ی فیلدها)
    // ═══════════════════════════════════════════════════════════

    // System: General
    public string $shop_name = '';
    public string $shop_phone = '';
    public string $shop_address = '';
    public string $shop_postal = '';
    public string $shop_email = '';
    public string $currency = 'تومان';

    // System: Appearance
    public string $theme = 'light';
    public string $primary_color = '#1a5276';
    public string $accent_color = '#c9a84c';
    public string $density = 'normal';
    public string $font_family = 'Vazirmatn';

    // System: Notifications
    public bool $notif_order_created = true;
    public bool $notif_order_status = true;
    public bool $notif_certificate_issued = true;
    public bool $notif_api_error = true;

    // Commerce: Woo
    public string $commerce_url = '';
    public string $commerce_key = '';
    public string $commerce_secret = '';
    public array $wc_status_filter = ['processing', 'completed', 'on-hold'];
    public array $commerce_test_result = [];
    public bool $testing = false;

    // Commerce: Sync
    public string $woo_last_orders_sync = '';
    public string $woo_last_cust_sync = '';
    public string $woo_catalog_last_sync = '';
    public string $woo_sync_status = '';
    public bool $woo_syncing = false;
    public int $sync_limit = 100;

    // Commerce: API Monitor
    public array $api_stats = [];
    public array $api_logs_list = [];

    // Certificates: Sizes
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

    // Certificates: Assets
    public string $bg_image = '';
    public array $logo_images = [];
    public int $logo_size = 60;
    public int $logo_offset_x = 50;
    public string $desc_image = '';
    public int $desc_image_w = 120;
    public int $desc_image_h = 80;
    public $logoUpload = null;
    public $descUpload = null;
    public $bgUpload = null;

    // Certificates: Catalog (Stones/Metals)
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

    // Labels
    public int $label_width = 100;
    public int $label_height = 50;

    // Logs
    public string $log_search = '';

    // Catalog (from phase 2)
    public array $woo_categories = [];
    public array $woo_attributes = [];
    public array $wp_users = [];

    // ═══════════════════════════════════════════════════════════
    public function mount(): void
    {
        $this->loadAll();
    }

    protected function loadAll(): void
    {
        try {
            // General
            $this->shop_name = (string) AppSetting::get('shop_name', 'جواهری مشاهیر');
            $this->shop_phone = (string) AppSetting::get('shop_phone', '');
            $this->shop_address = (string) AppSetting::get('shop_address', '');
            $this->shop_postal = (string) AppSetting::get('shop_postal', '');
            $this->shop_email = (string) AppSetting::get('shop_email', '');
            $this->currency = (string) AppSetting::get('currency', 'تومان');

            // Appearance
            $this->theme = (string) AppSetting::get('theme', 'light');
            $this->primary_color = (string) AppSetting::get('primary_color', '#1a5276');
            $this->accent_color = (string) AppSetting::get('accent_color', '#c9a84c');
            $this->density = (string) AppSetting::get('density', 'normal');
            $this->font_family = (string) AppSetting::get('font_family', 'Vazirmatn');

            // Notifications
            $this->notif_order_created = (bool) AppSetting::get('notif_order_created', true);
            $this->notif_order_status = (bool) AppSetting::get('notif_order_status', true);
            $this->notif_certificate_issued = (bool) AppSetting::get('notif_certificate_issued', true);
            $this->notif_api_error = (bool) AppSetting::get('notif_api_error', true);

            // Commerce
            $this->commerce_url = (string) AppSetting::get('commerce_url', '');
            $this->commerce_key = (string) AppSetting::get('commerce_key', '');
            $this->commerce_secret = (string) AppSetting::get('commerce_secret', '');
            $this->wc_status_filter = (array) AppSetting::get('wc_status_filter', ['processing', 'completed', 'on-hold']);
            $this->woo_last_orders_sync = (string) AppSetting::get('woo_last_orders_sync', '');
            $this->woo_last_cust_sync = (string) AppSetting::get('woo_last_cust_sync', '');
            $this->woo_catalog_last_sync = (string) AppSetting::get('woo_catalog_last_sync', '');

            // Certificate sizes
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

            // Assets
            $this->bg_image = (string) AppSetting::get('bg_image', '');
            $this->logo_images = (array) AppSetting::get('logo_images', []);
            $this->logo_size = (int) AppSetting::get('logo_size', 60);
            $this->logo_offset_x = (int) AppSetting::get('logo_offset_x', 50);
            $this->desc_image = (string) AppSetting::get('desc_image', '');
            $this->desc_image_w = (int) AppSetting::get('desc_image_w', 120);
            $this->desc_image_h = (int) AppSetting::get('desc_image_h', 80);

            // Label
            $this->label_width = (int) AppSetting::get('label_width', 100);
            $this->label_height = (int) AppSetting::get('label_height', 50);

        } catch (\Throwable $e) {}

        $this->loadStonesMetals();
    }

    // ═══════════════════════════════════════════════════════════
    // Navigation
    // ═══════════════════════════════════════════════════════════
    public function setGroup(string $group): void
    {
        if (!isset(self::GROUPS[$group])) return;
        $this->group = $group;
        // به اولین تب گروه برو
        $this->tab = array_key_first(self::GROUPS[$group]['tabs']);
    }

    public function setTab(string $tab): void
    {
        $this->tab = $tab;

        if ($tab === 'catalog') $this->loadStonesMetals();
        if ($tab === 'api-monitor') $this->loadApiMonitor();
    }

    // ═══════════════════════════════════════════════════════════
    // System Saves
    // ═══════════════════════════════════════════════════════════
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
        $this->dispatch('notify', type: 'success', message: 'ذخیره شد ✅');
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
        $this->dispatch('notify', type: 'success', message: 'ذخیره شد ✅');
        $this->dispatch('apply-appearance', [
            'theme' => $this->theme,
            'density' => $this->density,
            'primary_color' => $this->primary_color,
            'accent_color' => $this->accent_color,
            'font_family' => $this->font_family,
        ]);
    }

    public function saveNotifications(): void
    {
        AppSetting::putMany([
            'notif_order_created' => $this->notif_order_created ? '1' : '0',
            'notif_order_status' => $this->notif_order_status ? '1' : '0',
            'notif_certificate_issued' => $this->notif_certificate_issued ? '1' : '0',
            'notif_api_error' => $this->notif_api_error ? '1' : '0',
        ], 'notifications');
        Cache::forget('app_settings_all');
        $this->dispatch('notify', type: 'success', message: 'ذخیره شد ✅');
    }

    // ═══════════════════════════════════════════════════════════
    // Commerce Saves
    // ═══════════════════════════════════════════════════════════
    public function saveCommerce(): void
    {
        AppSetting::putMany([
            'commerce_url' => $this->commerce_url,
            'commerce_key' => $this->commerce_key,
            'commerce_secret' => $this->commerce_secret,
            'wc_status_filter' => $this->wc_status_filter,
        ], 'commerce');
        Cache::forget('app_settings_all');
        $this->dispatch('notify', type: 'success', message: 'ذخیره شد ✅');
    }

    public function testCommerce(): void
    {
        $this->testing = true;
        $this->commerce_test_result = [];

        try {
            $client = new \App\Infrastructure\WooCommerce\WooCommerceClient([
                'base' => rtrim(trim($this->commerce_url), '/') . (str_contains(trim($this->commerce_url), '/wp-json') ? '' : '/wp-json/wc/v3'),
                'wp_base' => preg_replace('#/wc/v3$#', '', rtrim(trim($this->commerce_url), '/') . (str_contains(trim($this->commerce_url), '/wp-json') ? '' : '/wp-json/wc/v3')),
                'key' => trim($this->commerce_key),
                'secret' => trim($this->commerce_secret),
            ]);
            $r = $client->testConnection();

            if ($r['ok']) {
                $this->commerce_test_result = ['ok' => true, 'message' => '✅ اتصال موفق'];
            } else {
                $this->commerce_test_result = ['ok' => false, 'message' => '❌ ' . ($r['error'] ?? 'خطا')];
            }
        } catch (\Throwable $e) {
            $this->commerce_test_result = ['ok' => false, 'message' => '❌ ' . $e->getMessage()];
        }

        $this->testing = false;
        $this->saveCommerce();
    }

    public function saveWcStatusFilter(): void
    {
        AppSetting::put('wc_status_filter', $this->wc_status_filter, 'commerce');
        Cache::forget('app_settings_all');
        $this->dispatch('notify', type: 'success', message: 'ذخیره شد ✅');
    }

    public function syncOrdersFromWoo(): void
    {
        $this->woo_syncing = true;
        $this->woo_sync_status = '⏳ در حال دریافت سفارشات...';
        @set_time_limit(300);

        try {
            $statuses = implode(',', $this->wc_status_filter ?: ['processing', 'completed']);
            \Illuminate\Support\Facades\Artisan::call('shopgun:import-orders', [
                '--status' => $statuses,
                '--limit' => $this->sync_limit,
            ]);
            $this->woo_sync_status = '✅ سفارشات دریافت شد';
            $this->woo_last_orders_sync = now()->toIso8601String();
            AppSetting::put('woo_last_orders_sync', $this->woo_last_orders_sync, 'commerce');
            Cache::forget('app_settings_all');
        } catch (\Throwable $e) {
            $this->woo_sync_status = '❌ ' . $e->getMessage();
        }

        $this->woo_syncing = false;
    }

    public function syncCustomersFromWoo(): void
    {
        $this->woo_syncing = true;
        $this->woo_sync_status = '⏳ در حال دریافت مشتریان...';
        @set_time_limit(300);

        try {
            \Illuminate\Support\Facades\Artisan::call('shopgun:sync-customers', ['--limit' => $this->sync_limit]);
            $this->woo_sync_status = '✅ مشتریان دریافت شد';
            $this->woo_last_cust_sync = now()->toIso8601String();
            AppSetting::put('woo_last_cust_sync', $this->woo_last_cust_sync, 'commerce');
            Cache::forget('app_settings_all');
        } catch (\Throwable $e) {
            $this->woo_sync_status = '❌ ' . $e->getMessage();
        }

        $this->woo_syncing = false;
    }

    public function syncWooCatalog(): void
    {
        $this->woo_syncing = true;
        $this->woo_sync_status = '⏳ در حال سینک کاتالوگ...';
        @set_time_limit(600);

        try {
            \Illuminate\Support\Facades\Artisan::call('shopgun:sync-catalog');
            $this->woo_sync_status = '✅ کاتالوگ سینک شد';
            $this->woo_catalog_last_sync = now()->toIso8601String();
            AppSetting::put('woo_catalog_last_sync', $this->woo_catalog_last_sync, 'commerce');
            Cache::forget('app_settings_all');
        } catch (\Throwable $e) {
            $this->woo_sync_status = '❌ ' . $e->getMessage();
        }

        $this->woo_syncing = false;
    }

    public function syncProductsFromWoo(): void
    {
        $this->woo_syncing = true;
        $this->woo_sync_status = '⏳ در حال سینک محصولات...';
        @set_time_limit(600);

        try {
            \Illuminate\Support\Facades\Artisan::call('shopgun:sync-products', [
                '--timeout' => 120,
                '--per-page' => 50,
            ]);
            $this->woo_sync_status = '✅ محصولات سینک شد';
        } catch (\Throwable $e) {
            $this->woo_sync_status = '❌ ' . $e->getMessage();
        }

        $this->woo_syncing = false;
    }

    // ═══════════════════════════════════════════════════════════
    // Certificates Saves
    // ═══════════════════════════════════════════════════════════
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
            'cert_hide_desc' => $this->cert_hide_desc ? '1' : '0',
            'cert_col1' => $this->cert_col1,
            'cert_col2' => $this->cert_col2,
            'cert_col3' => $this->cert_col3,
            'cert_col4' => $this->cert_col4,
        ], 'certificate');
        Cache::forget('app_settings_all');
        $this->dispatch('notify', type: 'success', message: 'ذخیره شد ✅');
    }

    public function saveLabel(): void
    {
        AppSetting::putMany([
            'label_width' => $this->label_width,
            'label_height' => $this->label_height,
        ], 'certificate');
        Cache::forget('app_settings_all');
        $this->dispatch('notify', type: 'success', message: 'ذخیره شد ✅');
    }

    public function setCertPreset(float $w, float $h): void
    {
        $this->cert_width = $w;
        $this->cert_height = $h;
    }

    // ═══════════════════════════════════════════════════════════
    // Stones/Metals
    // ═══════════════════════════════════════════════════════════
    protected function defaultStones(): array
    {
        return [
            ['name' => 'فیروزه عجمی', 'en' => 'Turquoise Ajami', 'origin' => 'نیشابور', 'flag' => 'ir', 'icon' => '💠'],
            ['name' => 'فیروزه شجری', 'en' => 'Turquoise Shajari', 'origin' => 'نیشابور', 'flag' => 'ir', 'icon' => '💠'],
            ['name' => 'عقیق یمانی', 'en' => 'Yemeni Agate', 'origin' => 'یمن', 'flag' => 'ye', 'icon' => '🔴'],
            ['name' => 'عقیق سلیمانی', 'en' => 'Solomoni Agate', 'origin' => 'یمن', 'flag' => 'ye', 'icon' => '❤️'],
            ['name' => 'در نجف', 'en' => 'Najaf Pearl', 'origin' => 'عراق', 'flag' => 'iq', 'icon' => '⚪'],
            ['name' => 'الماس', 'en' => 'Diamond', 'origin' => 'آفریقا', 'flag' => 'za', 'icon' => '💎'],
            ['name' => 'یاقوت سرخ', 'en' => 'Ruby', 'origin' => 'میانمار', 'flag' => 'mm', 'icon' => '❤️'],
            ['name' => 'یاقوت کبود', 'en' => 'Blue Sapphire', 'origin' => 'سری‌لانکا', 'flag' => 'lk', 'icon' => '🔵'],
            ['name' => 'زمرد', 'en' => 'Emerald', 'origin' => 'کلمبیا', 'flag' => 'co', 'icon' => '🟢'],
            ['name' => 'توپاز', 'en' => 'Topaz', 'origin' => 'برزیل', 'flag' => 'br', 'icon' => '💛'],
            ['name' => 'آمیتیست', 'en' => 'Amethyst', 'origin' => 'برزیل', 'flag' => 'br', 'icon' => '🟣'],
            ['name' => 'اوپال', 'en' => 'Opal', 'origin' => 'استرالیا', 'flag' => 'au', 'icon' => '🌈'],
            ['name' => 'مرجان', 'en' => 'Coral', 'origin' => 'مدیترانه', 'flag' => 'it', 'icon' => '🟠'],
            ['name' => 'لاجورد', 'en' => 'Lapis Lazuli', 'origin' => 'افغانستان', 'flag' => 'af', 'icon' => '💙'],
        ];
    }

    protected function defaultMetals(): array
    {
        return [
            ['name' => 'نقره 925', 'en' => 'Silver 925', 'carat' => '925'],
            ['name' => 'نقره 999', 'en' => 'Fine Silver', 'carat' => '999'],
            ['name' => 'طلا 18K', 'en' => 'Gold 18K', 'carat' => '750'],
            ['name' => 'طلا 21K', 'en' => 'Gold 21K', 'carat' => '875'],
            ['name' => 'طلا 22K', 'en' => 'Gold 22K', 'carat' => '916'],
            ['name' => 'پلاتین 950', 'en' => 'Platinum 950', 'carat' => '950'],
            ['name' => 'استیل', 'en' => 'Stainless Steel', 'carat' => '-'],
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
        if ($name === '') { $this->dispatch('notify', type: 'error', message: 'نام الزامی است'); return; }

        $stone = [
            'name' => $name,
            'en' => trim($this->new_stone_en) ?: $name,
            'origin' => trim($this->new_stone_origin) ?: '—',
            'flag' => $this->new_stone_flag ?: 'ir',
            'icon' => $this->new_stone_icon ?: '💎',
        ];

        if ($this->editing_stone_idx !== null && isset($this->cert_stones[$this->editing_stone_idx])) {
            $this->cert_stones[$this->editing_stone_idx] = $stone;
            $msg = "ویرایش شد";
        } else {
            $this->cert_stones[] = $stone;
            $msg = "اضافه شد";
        }

        AppSetting::put('cert_stones', $this->cert_stones, 'certificate');
        Cache::forget('app_settings_all');

        $this->new_stone_name = '';
        $this->new_stone_en = '';
        $this->new_stone_origin = '';
        $this->new_stone_flag = 'ir';
        $this->new_stone_icon = '💎';
        $this->editing_stone_idx = null;
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
        $this->loadStonesMetals();
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
        if ($name === '') { $this->dispatch('notify', type: 'error', message: 'نام الزامی است'); return; }

        $metal = [
            'name' => $name,
            'en' => trim($this->new_metal_en) ?: $name,
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
        $this->loadStonesMetals();
    }

    // ═══════════════════════════════════════════════════════════
    // Uploads
    // ═══════════════════════════════════════════════════════════
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
                $this->dispatch('notify', type: 'success', message: 'ذخیره شد');
            }
        } catch (\Throwable $e) {}
    }

    public function updatedBgUpload(): void
    {
        if (!$this->bgUpload) return;
        try {
            $path = $this->bgUpload->store('bg', 'public');
            if ($path) {
                $this->bg_image = asset('storage/' . $path);
                AppSetting::put('bg_image', $this->bg_image, 'certificate');
                Cache::forget('app_settings_all');
                $this->bgUpload = null;
                $this->dispatch('notify', type: 'success', message: 'پس‌زمینه ذخیره شد');
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

    // ═══════════════════════════════════════════════════════════
    // API Monitor
    // ═══════════════════════════════════════════════════════════
    public function loadApiMonitor(): void
    {
        try {
            $this->api_stats = [
                'total' => \App\Models\ApiLog::count(),
                'today' => \App\Models\ApiLog::whereDate('created_at', today())->count(),
                'errors' => \App\Models\ApiLog::whereNotNull('error')->count(),
                'errors_today' => \App\Models\ApiLog::whereNotNull('error')->whereDate('created_at', today())->count(),
                'avg_ms' => (int) \App\Models\ApiLog::avg('duration_ms'),
            ];

            $this->api_logs_list = \App\Models\ApiLog::latest('id')->limit(30)->get()->map(fn($l) => [
                'id' => $l->id,
                'service' => $l->service,
                'method' => $l->method,
                'url' => mb_substr($l->url ?? '', 0, 80),
                'status_code' => $l->status_code,
                'duration_ms' => $l->duration_ms,
                'error' => $l->error ? mb_substr($l->error, 0, 60) : null,
                'time' => $l->created_at?->format('H:i:s'),
            ])->toArray();
        } catch (\Throwable $e) {}
    }

    public function clearApiLogs(): void
    {
        try {
            \App\Models\ApiLog::truncate();
            $this->loadApiMonitor();
            $this->dispatch('notify', type: 'success', message: 'پاک شد');
        } catch (\Throwable $e) {}
    }

    // ═══════════════════════════════════════════════════════════
    // Preview
    // ═══════════════════════════════════════════════════════════
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
                    'length' => 15, 'width' => 12, 'weight' => 5.5, 'brilliant' => 0,
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
                'imgW' => $this->cert_img_w, 'imgH' => $this->cert_img_h,
                'qrSize' => $this->cert_qr_size,
                'logoW' => $this->cert_logo_w, 'logoH' => $this->cert_logo_h,
                'codeFont' => $this->cert_code_font,
                'titleFont' => $this->cert_title_font,
                'descFont' => $this->cert_desc_font,
            ];

            CertConfig::$overrideCols = [$this->cert_col1, $this->cert_col2, $this->cert_col3, $this->cert_col4];
            CertConfig::$overrideHideDesc = $this->cert_hide_desc;

            return CertRenderer::renderCard($cert);
        } catch (\Throwable $e) {
            return '<div style="padding:16px;background:#fee2e2;color:#991b1b;border-radius:8px;font-size:12px;text-align:right;direction:rtl;line-height:1.8">'
                 . '<b>⚠️ خطا:</b><br>' . htmlspecialchars($e->getMessage())
                 . '<br><small>' . htmlspecialchars(basename($e->getFile())) . ':' . $e->getLine() . '</small></div>';
        }
    }

    
        public function updated($property)
    {
        if (! in_array($property, ['primary_color', 'accent_color', 'font_family', 'theme', 'ui_style'])) {
            return;
        }

        $settings = [
            'primary_color' => $this->primary_color,
            'accent_color'  => $this->accent_color,
            'font_family'   => $this->font_family,
            'theme'         => $this->theme,
            'ui_style'      => $this->ui_style,
        ];

        foreach ($settings as $key => $value) {
            \App\Models\AppSetting::updateOrCreate(
                ['key' => $key],
                ['value' => $value]
            );
        }

        \Illuminate\Support\Facades\Cache::forget('app_settings_all');

        // ★ Named args → JS در e.detail یک object می‌گیرد (نه آرایه)
        $this->dispatch('theme-changed',
            theme:   $this->theme,
            style:   $this->ui_style,
            primary: $this->primary_color,
            accent:  $this->accent_color,
            font:    $this->font_family,
        );
    }

    public function render()
    {
        return view('livewire.settings.index', [
            'groups' => self::GROUPS,
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
