# -*- coding: utf-8 -*-
"""ShopGun V2 - v14: Fix preview (no regex escapes)"""
from pathlib import Path
import time

ROOT = Path(r'D:\prodo\shopgun-v2.2')

def write(rel, content):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        p.rename(str(p) + '.bak-' + str(int(time.time())))
    p.write_text(content, encoding='utf-8')
    print("[OK] " + rel)


# ═══════════════════════════════════════════════════════════════
# 1. SETTINGS/INDEX.PHP — بازنویسی کامل
# ═══════════════════════════════════════════════════════════════

NEW_PHP = r'''<?php

namespace App\Livewire\Settings;

use App\Models\AppSetting;
use App\Models\Certificate;
use App\Support\CertConfig;
use App\Services\CertRenderer;
use Illuminate\Support\Facades\Cache;
use Livewire\Component;

class Index extends Component
{
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
    public string $desc_image = '';
    public int $desc_image_w = 120;
    public int $desc_image_h = 80;

    // Templates
    public array $templates = [];
    public string $new_template_name = '';

    public function mount(): void
    {
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
        $this->desc_image = (string) AppSetting::get('desc_image', '');
        $this->desc_image_w = (int) AppSetting::get('desc_image_w', 120);
        $this->desc_image_h = (int) AppSetting::get('desc_image_h', 80);

        $this->loadTemplates();
    }

    public function setTab(string $tab): void
    {
        $this->tab = $tab;
    }

    /* ═══ General ═══ */
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
                ->timeout(15)->get($base . '/system_status');

            if ($r->successful()) {
                $this->commerce_test_result = ['ok' => true, 'message' => 'اتصال موفق'];
            } else {
                $this->commerce_test_result = ['ok' => false, 'message' => 'HTTP ' . $r->status()];
            }
        } catch (\Throwable $e) {
            $this->commerce_test_result = ['ok' => false, 'message' => $e->getMessage()];
        }
    }

    /* ═══ Certificate ═══ */
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
            'desc_image' => $this->desc_image,
            'desc_image_w' => $this->desc_image_w,
            'desc_image_h' => $this->desc_image_h,
        ], 'certificate');

        Cache::forget('app_settings_all');
        $this->dispatch('notify', type: 'success', message: 'تنظیمات ذخیره شد');
    }

    public function setCertPreset(float $w, float $h): void
    {
        $this->cert_width = $w;
        $this->cert_height = $h;
    }

    /* ═══ Logos ═══ */
    public function uploadLogo($file = null): void
    {
        try {
            // Livewire 3: از wire:model="logoUpload" استفاده می‌کنیم
            $f = $this->logoUpload ?? $file;
            if (!$f) {
                $this->dispatch('notify', type: 'error', message: 'فایل انتخاب نشد');
                return;
            }
            $path = is_object($f) ? $f->store('logos', 'public') : null;
            if ($path) {
                $this->logo_images[] = $path;
                AppSetting::put('logo_images', $this->logo_images, 'certificate');
                Cache::forget('app_settings_all');
                $this->logoUpload = null;
                $this->dispatch('notify', type: 'success', message: 'لوگو اضافه شد');
            }
        } catch (\Throwable $e) {
            $this->dispatch('notify', type: 'error', message: $e->getMessage());
        }
    }

    public $logoUpload = null;
    public $descUpload = null;

    public function removeLogo(int $idx): void
    {
        $arr = $this->logo_images;
        unset($arr[$idx]);
        $this->logo_images = array_values($arr);
        AppSetting::put('logo_images', $this->logo_images, 'certificate');
        Cache::forget('app_settings_all');
        $this->dispatch('notify', type: 'success', message: 'حذف شد');
    }

    public function uploadDesc($file = null): void
    {
        try {
            $f = $this->descUpload ?? $file;
            if (!$f) return;
            $path = is_object($f) ? $f->store('desc', 'public') : null;
            if ($path) {
                $this->desc_image = $path;
                AppSetting::put('desc_image', $path, 'certificate');
                Cache::forget('app_settings_all');
                $this->descUpload = null;
                $this->dispatch('notify', type: 'success', message: 'تصویر ذخیره شد');
            }
        } catch (\Throwable $e) {
            $this->dispatch('notify', type: 'error', message: $e->getMessage());
        }
    }

    public function saveLogos(): void
    {
        AppSetting::putMany([
            'logo_images' => $this->logo_images,
            'logo_size' => $this->logo_size,
            'desc_image' => $this->desc_image,
            'desc_image_w' => $this->desc_image_w,
            'desc_image_h' => $this->desc_image_h,
        ], 'certificate');
        Cache::forget('app_settings_all');
        $this->dispatch('notify', type: 'success', message: 'ذخیره شد');
    }

    /* ═══ Templates ═══ */
    public function loadTemplates(): void
    {
        $this->templates = (array) AppSetting::get('cert_templates', []);
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
        $this->dispatch('notify', type: 'success', message: "طرح «{$name}» ذخیره شد");
    }

    public function loadTemplate(string $id): void
    {
        $list = (array) AppSetting::get('cert_templates', []);
        $tpl = null;
        foreach ($list as $t) {
            if (($t['id'] ?? '') === $id) { $tpl = $t; break; }
        }
        if (!$tpl) {
            $this->dispatch('notify', type: 'error', message: 'طرح پیدا نشد');
            return;
        }

        foreach (($tpl['settings'] ?? []) as $k => $v) {
            if (property_exists($this, $k)) {
                $this->$k = $v;
            }
        }

        $this->dispatch('notify', type: 'success', message: "طرح «{$tpl['name']}» بارگذاری شد");
    }

    public function deleteTemplate(string $id): void
    {
        $list = (array) AppSetting::get('cert_templates', []);
        $list = array_values(array_filter($list, fn($t) => ($t['id'] ?? '') !== $id));
        AppSetting::put('cert_templates', $list, 'certificate');
        Cache::forget('app_settings_all');
        $this->loadTemplates();
        $this->dispatch('notify', type: 'success', message: 'حذف شد');
    }

    /* ═══ Preview ═══ */
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
            return '<div style="padding:16px;background:#fee2e2;color:#991b1b;border-radius:8px;font-size:12px;text-align:right;direction:rtl;max-width:400px;line-height:1.8">'
                 . '<b>⚠️ خطا در پیش‌نمایش:</b><br>'
                 . htmlspecialchars($e->getMessage())
                 . '<br><br><small style="opacity:.7">'
                 . htmlspecialchars(basename($e->getFile())) . ':' . $e->getLine()
                 . '</small>'
                 . '</div>';
        }
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
'''

write('app/Livewire/Settings/Index.php', NEW_PHP)

print()
print("=" * 60)
print("DONE")
print("=" * 60)
print()
print("Run:")
print("  php artisan view:clear")
print("  php artisan optimize:clear")
print("  php artisan serve")