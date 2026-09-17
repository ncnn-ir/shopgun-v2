#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""تنظیمات کامل — همه ۱۰ تب با Legacy Style"""
import shutil
from pathlib import Path
from datetime import datetime

PROJECT = Path("/data/data/com.termux/files/home/shopgun-v2.2")
if not PROJECT.exists():
    PROJECT = Path(input("مسیر پروژه: ").strip())

def write(rel, content):
    full = PROJECT / rel
    full.parent.mkdir(parents=True, exist_ok=True)
    with open(full, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print(f"  ✓ {rel}")

def backup(rel):
    src = PROJECT / rel
    if not src.exists(): return
    bd = PROJECT / "storage/backups"; bd.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(src, bd / f"{src.stem}_{ts}.bak")

# ═══════════════════════════════════════════════════════════════
# SETTINGS INDEX — Livewire کامل با ۱۰ تب
# ═══════════════════════════════════════════════════════════════
SETTINGS_INDEX = r'''<?php
namespace App\Livewire\Settings;

use App\Models\ApiLog;
use App\Models\AppSetting;
use App\Models\Channel;
use App\Models\Metal;
use App\Models\Stone;
use App\Services\ApiLogger;
use Livewire\Attributes\On;
use Livewire\Component;
use Livewire\WithFileUploads;

class Index extends Component
{
    use WithFileUploads;

    public string $tab = 'general';

    /* ═══ General ═══ */
    public string $shop_name = 'جواهری مشاهیر';
    public string $shop_phone = '09151531301';
    public string $shop_address = '';
    public string $shop_postal = '';
    public string $shop_email = '';
    public string $currency = 'تومان';

    /* ═══ Appearance ═══ */
    public string $theme = 'light';
    public string $primary_color = '#1a5276';
    public string $accent_color = '#c9a84c';
    public string $density = 'normal';
    public string $font_family = 'Vazirmatn';

    /* ═══ Commerce ═══ */
    public string $commerce_url = '';
    public string $commerce_key = '';
    public string $commerce_secret = '';
    public array $wc_status_filter = [];
    public bool $commerce_update_existing = true;
    public array $commerce_test_result = [];
    public array $commerce_sync_result = [];
    public bool $testing = false;
    public bool $syncing = false;

    /* ═══ Certificate ═══ */
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

    /* ═══ Label ═══ */
    public int $label_width = 100;
    public int $label_height = 50;
    public array $label_fonts = [
        'customer' => 16, 'insurance' => 12, 'address' => 14,
        'contactLbl' => 11, 'contactVal' => 16, 'meta' => 11, 'footer' => 10,
    ];

    /* ═══ Assets ═══ */
    public string $bg_image = '';
    public array $logo_images = [];
    public string $desc_image = '';
    public string $header_logo = '';

    /* ═══ Logs ═══ */
    public string $log_filter = '';
    public string $log_search = '';
    public array $logs = [];

    /* ═══ Stones/Metals ═══ */
    public array $stones_list = [];
    public array $metals_list = [];
    public string $new_stone_name = '';
    public string $new_stone_en = '';
    public string $new_stone_origin = '';
    public string $new_stone_icon = '💎';
    public string $new_stone_flag = 'ir';
    public string $new_metal_name = '';
    public string $new_metal_en = '';
    public string $new_metal_carat = '';

    /* ═══ Monitor ═══ */
    public string $monitor_filter = '';
    public array $monitor_stats = [];
    public array $monitor_logs = [];

    public function mount(): void
    {
        $this->loadSettings();
    }

    public function loadSettings(): void
    {
        // General
        $this->shop_name = (string) AppSetting::get('shop_name', 'جواهری مشاهیر');
        $this->shop_phone = (string) AppSetting::get('shop_phone', '09151531301');
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

        // Commerce
        $this->commerce_url = (string) AppSetting::get('commerce_url', '');
        $this->commerce_key = (string) AppSetting::get('commerce_key', '');
        $this->commerce_secret = (string) AppSetting::get('commerce_secret', '');
        $this->wc_status_filter = (array) AppSetting::get('wc_status_filter', ['processing','completed','on-hold']);
        $this->commerce_update_existing = (bool) AppSetting::get('commerce_update_existing', true);

        // Certificate
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

        // Label
        $this->label_width = (int) AppSetting::get('label_width', 100);
        $this->label_height = (int) AppSetting::get('label_height', 50);
        $lf = AppSetting::get('label_fonts', null);
        if (is_array($lf)) $this->label_fonts = array_merge($this->label_fonts, $lf);

        // Assets
        $this->bg_image = (string) AppSetting::get('bg_image', '');
        $this->logo_images = (array) AppSetting::get('logo_images', []);
        $this->desc_image = (string) AppSetting::get('desc_image', '');
        $this->header_logo = (string) AppSetting::get('header_logo', '');

        // Stones/Metals
        $this->loadStonesMetals();

        if ($this->tab === 'monitor') $this->refreshMonitor();
        if ($this->tab === 'logs') $this->loadLogs();
    }

    public function setTab(string $tab): void
    {
        $this->tab = $tab;
        if ($tab === 'monitor') $this->refreshMonitor();
        if ($tab === 'logs') $this->loadLogs();
        if ($tab === 'stones') $this->loadStonesMetals();
    }

    /* ═══════════════════════════════════════════════════════════
       ذخیره تب‌ها
       ═══════════════════════════════════════════════════════════ */

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
        $this->dispatch('notify', type: 'success', message: 'تنظیمات عمومی ذخیره شد ✅');
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
        $this->dispatch('notify', type: 'success', message: 'ظاهر ذخیره شد ✅');
        $this->dispatch('apply-theme', [
            'theme' => $this->theme,
            'density' => $this->density,
            'primary_color' => $this->primary_color,
        ]);
    }

    public function saveCommerce(): void
    {
        AppSetting::putMany([
            'commerce_url' => $this->commerce_url,
            'commerce_key' => $this->commerce_key,
            'commerce_secret' => $this->commerce_secret,
            'wc_status_filter' => $this->wc_status_filter,
            'commerce_update_existing' => $this->commerce_update_existing,
        ], 'commerce');
        $this->dispatch('notify', type: 'success', message: 'تنظیمات کامرس ذخیره شد ✅');
    }

    public function testCommerce(): void
    {
        $this->testing = true;
        $this->commerce_test_result = [];

        $url = trim($this->commerce_url);
        $key = trim($this->commerce_key);
        $secret = trim($this->commerce_secret);

        if (!$url || !$key || !$secret) {
            $this->commerce_test_result = ['ok' => false, 'message' => 'هر سه فیلد الزامی است'];
            $this->testing = false;
            return;
        }

        $base = rtrim($url, '/');
        if (!str_contains($base, '/wp-json')) {
            $base .= '/wp-json/wc/v3';
        }

        try {
            $response = \Illuminate\Support\Facades\Http::withBasicAuth($key, $secret)
                ->timeout(30)
                ->get($base . '/system_status');

            if ($response->successful()) {
                $data = $response->json();
                $this->commerce_test_result = [
                    'ok' => true,
                    'message' => 'اتصال موفق ✅',
                    'wp_version' => $data['environment']['wp_version'] ?? '?',
                    'currency' => $data['settings']['currency'] ?? '?',
                ];
                ApiLogger::log('woocommerce', 'تست اتصال موفق');
            } else {
                $this->commerce_test_result = [
                    'ok' => false,
                    'message' => 'HTTP ' . $response->status(),
                ];
            }
        } catch (\Throwable $e) {
            $this->commerce_test_result = ['ok' => false, 'message' => $e->getMessage()];
            ApiLogger::log('woocommerce', 'تست اتصال ناموفق', $e->getMessage());
        }

        $this->testing = false;
        $this->saveCommerce();
    }

    public function syncProducts(): void
    {
        $this->syncing = true;
        $this->commerce_sync_result = ['running' => true, 'message' => 'در حال سینک...'];

        try {
            $service = app(\App\Services\ProductSyncService::class);
            $report = $service::syncFromWoo(true);
            $this->commerce_sync_result = array_merge($report, ['success' => true]);
            $this->dispatch('notify', type: 'success', message: "سینک: {$report['total']} محصول");
        } catch (\Throwable $e) {
            $this->commerce_sync_result = ['success' => false, 'message' => $e->getMessage()];
            $this->dispatch('notify', type: 'error', message: 'خطا: ' . $e->getMessage());
        }

        $this->syncing = false;
    }

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
            'cert_hide_desc' => $this->cert_hide_desc,
        ], 'certificate');
        $this->dispatch('notify', type: 'success', message: 'تنظیمات شناسنامه ذخیره شد ✅');
    }

    public function saveLabel(): void
    {
        AppSetting::putMany([
            'label_width' => $this->label_width,
            'label_height' => $this->label_height,
            'label_fonts' => $this->label_fonts,
        ], 'label');
        $this->dispatch('notify', type: 'success', message: 'تنظیمات برچسب ذخیره شد ✅');
    }

    public function setCertPreset(float $w, float $h): void
    {
        $this->cert_width = $w;
        $this->cert_height = $h;
    }

    /* ═══════════════════════════════════════════════════════════
       Assets
       ═══════════════════════════════════════════════════════════ */

    public function uploadBg(): void
    {
        $this->validate(['bg_image' => 'image|max:5120']);
        $path = $this->bg_image->store('settings', 'public');
        $this->bg_image = asset('storage/' . $path);
        AppSetting::put('bg_image', $this->bg_image, 'assets');
        $this->dispatch('notify', type: 'success', message: 'پس‌زمینه ذخیره شد');
    }

    public function removeBg(): void
    {
        $this->bg_image = '';
        AppSetting::put('bg_image', '', 'assets');
    }

    /* ═══════════════════════════════════════════════════════════
       Stones / Metals
       ═══════════════════════════════════════════════════════════ */

    public function loadStonesMetals(): void
    {
        $this->stones_list = Stone::orderBy('id')->get()->toArray();
        $this->metals_list = Metal::orderBy('id')->get()->toArray();
    }

    public function addStone(): void
    {
        $this->validate([
            'new_stone_name' => 'required|string|max:100',
            'new_stone_en' => 'required|string|max:100',
        ]);

        Stone::create([
            'name' => $this->new_stone_name,
            'name_en' => $this->new_stone_en,
            'origin' => $this->new_stone_origin,
            'flag' => $this->new_stone_flag,
            'icon' => $this->new_stone_icon,
        ]);

        $this->reset(['new_stone_name', 'new_stone_en', 'new_stone_origin']);
        $this->loadStonesMetals();
        $this->dispatch('notify', type: 'success', message: 'سنگ اضافه شد ✅');
    }

    public function removeStone(int $id): void
    {
        Stone::find($id)?->delete();
        $this->loadStonesMetals();
        $this->dispatch('notify', type: 'success', message: 'حذف شد');
    }

    public function addMetal(): void
    {
        $this->validate([
            'new_metal_name' => 'required|string|max:100',
            'new_metal_carat' => 'required|string|max:20',
        ]);

        Metal::create([
            'name' => $this->new_metal_name,
            'name_en' => $this->new_metal_en ?: $this->new_metal_name,
            'carat' => $this->new_metal_carat,
        ]);

        $this->reset(['new_metal_name', 'new_metal_en', 'new_metal_carat']);
        $this->loadStonesMetals();
        $this->dispatch('notify', type: 'success', message: 'فلز اضافه شد ✅');
    }

    public function removeMetal(int $id): void
    {
        Metal::find($id)?->delete();
        $this->loadStonesMetals();
        $this->dispatch('notify', type: 'success', message: 'حذف شد');
    }

    /* ═══════════════════════════════════════════════════════════
       Logs
       ═══════════════════════════════════════════════════════════ */

    public function loadLogs(): void
    {
        $query = \Spatie\Activitylog\Models\Activity::query()
            ->latest();

        if ($this->log_search) {
            $query->where('description', 'like', "%{$this->log_search}%");
        }

        $this->logs = $query->limit(100)->get()->map(fn($l) => [
            'id' => $l->id,
            'description' => $l->description,
            'event' => $l->event,
            'subject_type' => class_basename($l->subject_type ?? ''),
            'subject_id' => $l->subject_id,
            'causer' => $l->causer?->name ?? 'سیستم',
            'created_at' => $l->created_at?->format('Y-m-d H:i:s'),
        ])->toArray();
    }

    public function clearLogs(): void
    {
        \Spatie\Activitylog\Models\Activity::truncate();
        $this->loadLogs();
        $this->dispatch('notify', type: 'success', message: 'لاگ‌ها پاک شد');
    }

    /* ═══════════════════════════════════════════════════════════
       Monitor API
       ═══════════════════════════════════════════════════════════ */

    public function refreshMonitor(): void
    {
        if (!class_exists(ApiLog::class)) return;

        try {
            $query = ApiLog::query();
            if ($this->monitor_filter) {
                $query->where('url', 'like', "%{$this->monitor_filter}%");
            }

            $this->monitor_stats = [
                'total' => ApiLog::count(),
                'today' => ApiLog::whereDate('created_at', today())->count(),
                'errors' => ApiLog::whereNotNull('error')->count(),
            ];

            $this->monitor_logs = $query->latest('id')->limit(50)->get()->map(fn($l) => [
                'id' => $l->id,
                'service' => $l->service,
                'method' => $l->method,
                'url' => substr($l->url ?? '', 0, 100),
                'status_code' => $l->status_code,
                'duration_ms' => $l->duration_ms,
                'error' => $l->error,
                'created_at' => $l->created_at?->format('H:i:s'),
            ])->toArray();
        } catch (\Throwable $e) {
            $this->monitor_stats = [];
            $this->monitor_logs = [];
        }
    }

    public function clearMonitor(): void
    {
        ApiLog::truncate();
        $this->refreshMonitor();
        $this->dispatch('notify', type: 'success', message: 'لاگ API پاک شد');
    }

    /* ═══════════════════════════════════════════════════════════
       Backup
       ═══════════════════════════════════════════════════════════ */

    public function createBackup(): void
    {
        try {
            \Illuminate\Support\Facades\Artisan::call('backup:run');
            $this->dispatch('notify', type: 'success', message: 'پشتیبان ساخته شد ✅');
        } catch (\Throwable $e) {
            $this->dispatch('notify', type: 'error', message: 'خطا: ' . $e->getMessage());
        }
    }

    public function downloadBackup(): void
    {
        $this->dispatch('notify', type: 'info', message: 'در حال آماده‌سازی...');
    }

    public function exportJson(): void
    {
        $data = [
            'stones' => Stone::all()->toArray(),
            'metals' => Metal::all()->toArray(),
            'orders' => \App\Models\Order::with('items')->get()->toArray(),
            'customers' => \App\Models\Customer::all()->toArray(),
            'certificates' => \App\Models\Certificate::all()->toArray(),
            'settings' => AppSetting::all()->toArray(),
        ];

        $json = json_encode($data, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT);
        $path = storage_path('app/backup-' . date('Ymd-His') . '.json');
        file_put_contents($path, $json);

        $this->dispatch('notify', type: 'success', message: 'خروجی: ' . basename($path));
    }

    public function render()
    {
        return view('livewire.settings.index', [
            'stats' => $this->getSystemStats(),
        ])->layout('components.layouts.app');
    }

    protected function getSystemStats(): array
    {
        return [
            'php' => PHP_VERSION,
            'laravel' => app()->version(),
            'orders' => \App\Models\Order::count(),
            'customers' => \App\Models\Customer::count(),
            'products' => \App\Models\Product::count(),
            'certificates' => \App\Models\Certificate::count(),
            'storage' => '—',
        ];
    }
}
'''

# ═══════════════════════════════════════════════════════════════
# SETTINGS VIEW — 10 Tabs
# ═══════════════════════════════════════════════════════════════
SETTINGS_BLADE = r'''<div style="padding:0 18px 18px">
    <h1 style="font-size:20px;font-weight:700;margin-bottom:14px">⚙️ تنظیمات</h1>

    {{-- Tabs --}}
    <div class="sg-tabs-bar" style="padding:0;margin-bottom:14px;overflow-x:auto;flex-wrap:nowrap">
        @foreach([
            'general' => ['⚙️', 'عمومی'],
            'appearance' => ['🎨', 'ظاهر'],
            'commerce' => ['🔌', 'کامرس'],
            'certificate' => ['💎', 'شناسنامه'],
            'label' => ['🏷️', 'برچسب'],
            'assets' => ['🖼️', 'تصاویر'],
            'backup' => ['💾', 'پشتیبان'],
            'logs' => ['📜', 'لاگ'],
            'stones' => ['💠', 'سنگ/فلز'],
            'monitor' => ['📊', 'رصد API'],
        ] as $key => $meta)
            <button wire:click="setTab('{{ $key }}')"
                    class="sg-tab-btn {{ $tab === $key ? 'active' : '' }}"
                    style="white-space:nowrap">
                <span>{{ $meta[0] }}</span><span>{{ $meta[1] }}</span>
            </button>
        @endforeach
    </div>

    {{-- ═══════ General ═══════ --}}
    @if($tab === 'general')
        <div class="sg-settings-card" style="max-width:800px">
            <h3>اطلاعات فروشگاه</h3>
            <div class="form-row cols-2">
                <div class="form-group"><label>🏪 نام فروشگاه</label><input type="text" wire:model="shop_name" class="form-control"></div>
                <div class="form-group"><label>📱 تلفن</label><input type="text" wire:model="shop_phone" class="form-control" dir="ltr"></div>
            </div>
            <div class="form-group"><label>📍 آدرس</label><textarea wire:model="shop_address" class="form-control" rows="2"></textarea></div>
            <div class="form-row cols-3">
                <div class="form-group"><label>📮 کدپستی</label><input type="text" wire:model="shop_postal" class="form-control" dir="ltr"></div>
                <div class="form-group"><label>📧 ایمیل</label><input type="email" wire:model="shop_email" class="form-control" dir="ltr"></div>
                <div class="form-group"><label>💵 واحد پول</label><input type="text" wire:model="currency" class="form-control"></div>
            </div>
            <div style="display:flex;justify-content:flex-end;padding-top:10px;border-top:1px solid var(--border)">
                <button wire:click="saveGeneral" class="btn btn-success">💾 ذخیره</button>
            </div>
        </div>
    @endif

    {{-- ═══════ Appearance ═══════ --}}
    @if($tab === 'appearance')
        <div class="sg-settings-card" style="max-width:800px">
            <h3>ظاهر برنامه</h3>
            <div class="form-row cols-2">
                <div class="form-group"><label>🌓 تم</label>
                    <div style="display:flex;gap:6px">
                        @foreach(['light'=>'☀️ روشن','dark'=>'🌙 تیره'] as $k => $v)
                            <label style="flex:1;cursor:pointer">
                                <input type="radio" wire:model="theme" value="{{ $k }}" style="display:none">
                                <div style="padding:10px;border:2px solid {{ $theme === $k ? 'var(--gold)' : 'var(--border)' }};border-radius:10px;text-align:center;font-size:12px;font-weight:700;background:{{ $theme === $k ? 'rgba(201,168,76,.15)' : 'transparent' }}">{{ $v }}</div>
                            </label>
                        @endforeach
                    </div>
                </div>
                <div class="form-group"><label>📐 تراکم</label>
                    <div style="display:flex;gap:6px">
                        @foreach(['compact'=>'فشرده','normal'=>'معمولی','comfortable'=>'راحت'] as $k => $v)
                            <label style="flex:1;cursor:pointer">
                                <input type="radio" wire:model="density" value="{{ $k }}" style="display:none">
                                <div style="padding:10px;border:2px solid {{ $density === $k ? 'var(--gold)' : 'var(--border)' }};border-radius:10px;text-align:center;font-size:12px;font-weight:700;background:{{ $density === $k ? 'rgba(201,168,76,.15)' : 'transparent' }}">{{ $v }}</div>
                            </label>
                        @endforeach
                    </div>
                </div>
            </div>
            <div class="form-row cols-2">
                <div class="form-group"><label>🎨 رنگ اصلی</label>
                    <input type="color" wire:model="primary_color" style="width:100%;height:42px;border:2px solid var(--border);border-radius:10px;cursor:pointer">
                </div>
                <div class="form-group"><label>✨ رنگ تاکیدی</label>
                    <input type="color" wire:model="accent_color" style="width:100%;height:42px;border:2px solid var(--border);border-radius:10px;cursor:pointer">
                </div>
            </div>
            <div style="display:flex;justify-content:flex-end;padding-top:10px;border-top:1px solid var(--border)">
                <button wire:click="saveAppearance" class="btn btn-success">💾 ذخیره</button>
            </div>
        </div>
    @endif

    {{-- ═══════ Commerce ═══════ --}}
    @if($tab === 'commerce')
        <div class="sg-settings-card" style="max-width:800px">
            <h3>🔌 اتصال به WooCommerce</h3>
            <div style="padding:10px;background:rgba(41,128,185,.08);border-radius:10px;font-size:11.5px;margin-bottom:12px">
                💡 وردپرس → WooCommerce → Settings → Advanced → REST API → Add key
            </div>
            <div class="form-group"><label>🌐 آدرس سایت</label>
                <input type="text" wire:model="commerce_url" class="form-control" dir="ltr" placeholder="https://yoursite.com">
            </div>
            <div class="form-row cols-2">
                <div class="form-group"><label>🔑 Consumer Key</label><input type="text" wire:model="commerce_key" class="form-control" dir="ltr"></div>
                <div class="form-group"><label>🔐 Consumer Secret</label><input type="password" wire:model="commerce_secret" class="form-control" dir="ltr"></div>
            </div>

            @if(!empty($commerce_test_result))
                <div style="padding:12px;border-radius:10px;margin-bottom:12px;background:{{ $commerce_test_result['ok'] ? 'rgba(39,174,96,.1)' : 'rgba(231,76,60,.1)' }};color:{{ $commerce_test_result['ok'] ? 'var(--success)' : 'var(--danger)' }};font-weight:700;font-size:13px">
                    {{ $commerce_test_result['ok'] ? '✅' : '❌' }} {{ $commerce_test_result['message'] }}
                </div>
            @endif

            @if(!empty($commerce_sync_result))
                <div style="padding:12px;border-radius:10px;margin-bottom:12px;background:rgba(41,128,185,.1);font-weight:700;font-size:13px">
                    {{ $commerce_sync_result['message'] ?? '' }}
                </div>
            @endif

            <div style="display:flex;gap:6px;flex-wrap:wrap;padding-top:10px;border-top:1px solid var(--border)">
                <button wire:click="saveCommerce" class="btn btn-primary">💾 ذخیره</button>
                <button wire:click="testCommerce" wire:loading.attr="disabled" class="btn btn-secondary">
                    <span wire:loading.remove wire:target="testCommerce">🔌 تست اتصال</span>
                    <span wire:loading wire:target="testCommerce">⏳...</span>
                </button>
                <button wire:click="syncProducts" wire:loading.attr="disabled" class="btn btn-success">
                    <span wire:loading.remove wire:target="syncProducts">📥 سینک محصولات</span>
                    <span wire:loading wire:target="syncProducts">⏳...</span>
                </button>
            </div>
        </div>
    @endif

    {{-- ═══════ Certificate ═══════ --}}
    @if($tab === 'certificate')
        <div class="sg-settings-card" style="max-width:800px">
            <h3>📏 اندازه شناسنامه</h3>
            <div class="form-row cols-2">
                <div class="form-group"><label>📐 عرض (cm)</label><input type="number" step="0.1" wire:model="cert_width" class="form-control" dir="ltr"></div>
                <div class="form-group"><label>📐 ارتفاع (cm)</label><input type="number" step="0.1" wire:model="cert_height" class="form-control" dir="ltr"></div>
            </div>
            <div style="display:flex;gap:6px;margin-bottom:14px">
                <button wire:click="setCertPreset(6.5,6.5)" class="btn btn-outline btn-sm">۶.۵×۶.۵</button>
                <button wire:click="setCertPreset(7,7)" class="btn btn-outline btn-sm">۷×۷</button>
                <button wire:click="setCertPreset(8,6)" class="btn btn-outline btn-sm">۸×۶</button>
            </div>

            <h3>📸 ابعاد تصویر</h3>
            <div class="form-row cols-2">
                <div class="form-group"><label>عرض (px)</label><input type="number" wire:model="cert_img_w" class="form-control" dir="ltr"></div>
                <div class="form-group"><label>ارتفاع (px)</label><input type="number" wire:model="cert_img_h" class="form-control" dir="ltr"></div>
            </div>

            <h3>📱 QR و لوگو</h3>
            <div class="form-row cols-3">
                <div class="form-group"><label>سایز QR</label><input type="number" wire:model="cert_qr_size" class="form-control" dir="ltr"></div>
                <div class="form-group"><label>عرض لوگو</label><input type="number" wire:model="cert_logo_w" class="form-control" dir="ltr"></div>
                <div class="form-group"><label>ارتفاع لوگو</label><input type="number" wire:model="cert_logo_h" class="form-control" dir="ltr"></div>
            </div>

            <h3>🔤 فونت‌ها</h3>
            <div class="form-row cols-3">
                <div class="form-group"><label>فونت کد</label><input type="number" wire:model="cert_code_font" class="form-control" dir="ltr"></div>
                <div class="form-group"><label>فونت عنوان</label><input type="number" wire:model="cert_title_font" class="form-control" dir="ltr"></div>
                <div class="form-group"><label>فونت توضیحات</label><input type="number" wire:model="cert_desc_font" class="form-control" dir="ltr"></div>
            </div>

            <label style="display:flex;align-items:center;gap:8px;padding:10px;background:var(--bg);border-radius:8px;cursor:pointer;margin-bottom:14px">
                <input type="checkbox" wire:model="cert_hide_desc" style="width:18px;height:18px;accent-color:var(--gold)">
                <span style="font-size:12.5px">🚫 حذف توضیحات کنار تصویر</span>
            </label>

            <div style="display:flex;justify-content:flex-end;padding-top:10px;border-top:1px solid var(--border)">
                <button wire:click="saveCertificate" class="btn btn-success">💾 ذخیره</button>
            </div>
        </div>
    @endif

    {{-- ═══════ Label ═══════ --}}
    @if($tab === 'label')
        <div class="sg-settings-card" style="max-width:800px">
            <h3>📐 اندازه برچسب</h3>
            <div class="form-row cols-2">
                <div class="form-group"><label>📐 عرض (mm)</label><input type="number" wire:model="label_width" class="form-control" dir="ltr"></div>
                <div class="form-group"><label>📐 ارتفاع (mm)</label><input type="number" wire:model="label_height" class="form-control" dir="ltr"></div>
            </div>

            <h3>🔤 فونت‌ها</h3>
            @foreach([
                'customer' => '👤 نام مشتری',
                'insurance' => '💰 بیمه',
                'address' => '📍 آدرس',
                'contactLbl' => '🏷️ برچسب تماس',
                'contactVal' => '📱 مقدار تماس',
                'meta' => '🔖 متا',
                'footer' => '🌐 فوتر',
            ] as $k => $label)
                <div style="display:grid;grid-template-columns:1fr 80px;gap:8px;align-items:center;margin-bottom:8px">
                    <label style="font-size:12.5px;font-weight:600">{{ $label }}</label>
                    <input type="number" wire:model="label_fonts.{{ $k }}" class="form-control" dir="ltr" style="text-align:center">
                </div>
            @endforeach

            <div style="display:flex;justify-content:flex-end;padding-top:10px;border-top:1px solid var(--border)">
                <button wire:click="saveLabel" class="btn btn-success">💾 ذخیره</button>
            </div>
        </div>
    @endif

    {{-- ═══════ Assets ═══════ --}}
    @if($tab === 'assets')
        <div class="sg-settings-card" style="max-width:800px">
            <h3>🖼️ پس‌زمینه شناسنامه</h3>
            @if($bg_image)
                <div style="margin-bottom:12px">
                    <img src="{{ $bg_image }}" style="max-width:200px;border-radius:10px;border:2px solid var(--gold)">
                    <button wire:click="removeBg" class="btn btn-danger btn-sm" style="margin-right:8px">حذف</button>
                </div>
            @endif
            <input type="file" wire:model="bg_image" accept="image/*" class="form-control">

            <h3 style="margin-top:20px">🏷️ لوگوها</h3>
            @if(!empty($logo_images))
                <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px">
                    @foreach($logo_images as $logo)
                        <img src="{{ $logo }}" style="width:60px;height:50px;object-fit:contain;border:2px solid var(--gold);border-radius:8px;background:#fff">
                    @endforeach
                </div>
            @endif
            <input type="file" accept="image/*" class="form-control" multiple>

            <h3 style="margin-top:20px">📝 تصویر توضیحات</h3>
            @if($desc_image)
                <div style="margin-bottom:12px">
                    <img src="{{ $desc_image }}" style="max-width:200px;border-radius:10px">
                </div>
            @endif
            <input type="file" accept="image/*" class="form-control">
        </div>
    @endif

    {{-- ═══════ Backup ═══════ --}}
    @if($tab === 'backup')
        <div class="sg-settings-card" style="max-width:800px">
            <h3>💾 پشتیبان‌گیری</h3>
            <p style="font-size:12px;color:var(--text-light);margin-bottom:14px">
                از داده‌ها و تنظیمات پشتیبان بگیرید یا بازگردانی کنید.
            </p>
            <div style="display:flex;gap:6px;flex-wrap:wrap">
                <button wire:click="createBackup" class="btn btn-primary">➕ پشتیبان جدید</button>
                <button wire:click="exportJson" class="btn btn-secondary">📥 خروجی JSON</button>
            </div>

            <h3 style="margin-top:20px">📊 اطلاعات سیستم</h3>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
                @foreach([
                    ['🖥️', 'PHP', $stats['php']],
                    ['⚡', 'Laravel', $stats['laravel']],
                    ['📦', 'سفارشات', \App\Support\PersianNumber::toFa($stats['orders'])],
                    ['👥', 'مشتریان', \App\Support\PersianNumber::toFa($stats['customers'])],
                    ['💎', 'شناسنامه‌ها', \App\Support\PersianNumber::toFa($stats['certificates'])],
                    ['🛍️', 'محصولات', \App\Support\PersianNumber::toFa($stats['products'])],
                ] as $item)
                    <div style="padding:10px;background:var(--bg);border-radius:8px;display:flex;justify-content:space-between;font-size:12px">
                        <span>{{ $item[0] }} {{ $item[1] }}</span>
                        <strong style="font-family:monospace">{{ $item[2] }}</strong>
                    </div>
                @endforeach
            </div>
        </div>
    @endif

    {{-- ═══════ Logs ═══════ --}}
    @if($tab === 'logs')
        <div class="sg-settings-card" style="max-width:900px">
            <h3>📜 لاگ تغییرات</h3>
            <div style="display:flex;gap:8px;margin-bottom:14px">
                <input type="text" wire:model.live.debounce.400ms="log_search" placeholder="🔍 جستجو..." class="form-control" style="flex:1">
                <button wire:click="clearLogs" wire:confirm="پاک شوند؟" class="btn btn-danger btn-sm">🗑️ پاک</button>
            </div>
            <div style="max-height:500px;overflow-y:auto">
                @forelse($logs as $log)
                    <div style="padding:10px 12px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;font-size:11.5px">
                        <div>
                            <strong>{{ $log['description'] }}</strong>
                            <span style="opacity:.6"> · {{ $log['event'] }} · {{ $log['subject_type'] }}#{{ $log['subject_id'] }}</span>
                            <div style="opacity:.5;font-size:10px">{{ $log['causer'] }}</div>
                        </div>
                        <div style="font-family:monospace;font-size:10px;opacity:.6">{{ $log['created_at'] }}</div>
                    </div>
                @empty
                    <p style="text-align:center;padding:20px;opacity:.5">لاگی نیست</p>
                @endforelse
            </div>
        </div>
    @endif

    {{-- ═══════ Stones/Metals ═══════ --}}
    @if($tab === 'stones')
        <div class="sg-settings-card" style="max-width:900px">
            <h3>💎 سنگ‌های قیمتی ({{ \App\Support\PersianNumber::toFa(count($stones_list)) }})</h3>
            <div class="sg-stones-grid">
                @foreach($stones_list as $s)
                    <div class="sg-stone-card">
                        <button wire:click="removeStone({{ $s['id'] }})" wire:confirm="حذف شود؟"
                                style="position:absolute;top:-6px;left:-6px;width:20px;height:20px;border-radius:50%;background:var(--danger);color:#fff;border:none;cursor:pointer;font-size:11px">✕</button>
                        <div class="s-icon">{{ $s['icon'] ?? '💎' }}</div>
                        <div class="s-name">{{ $s['name'] }}</div>
                        <div class="s-origin">{{ $s['origin'] ?? '' }}</div>
                    </div>
                @endforeach
            </div>

            <h3 style="margin-top:20px">➕ افزودن سنگ</h3>
            <div class="form-row cols-3">
                <div class="form-group"><label>نام فارسی</label><input type="text" wire:model="new_stone_name" class="form-control"></div>
                <div class="form-group"><label>نام انگلیسی</label><input type="text" wire:model="new_stone_en" class="form-control" dir="ltr"></div>
                <div class="form-group"><label>آیکون</label><input type="text" wire:model="new_stone_icon" class="form-control"></div>
            </div>
            <div class="form-row cols-2">
                <div class="form-group"><label>اصالت</label><input type="text" wire:model="new_stone_origin" class="form-control"></div>
                <div class="form-group"><label>کشور (ISO)</label><input type="text" wire:model="new_stone_flag" class="form-control" dir="ltr" maxlength="2"></div>
            </div>
            <button wire:click="addStone" class="btn btn-primary">➕ افزودن سنگ</button>

            <h3 style="margin-top:30px">⚙️ فلزات ({{ \App\Support\PersianNumber::toFa(count($metals_list)) }})</h3>
            @foreach($metals_list as $m)
                <div style="padding:8px 12px;background:var(--bg);border-radius:8px;margin-bottom:6px;display:flex;justify-content:space-between;align-items:center">
                    <span>⚙️ <strong>{{ $m['name'] }}</strong> — عیار {{ $m['carat'] ?? '-' }}</span>
                    <button wire:click="removeMetal({{ $m['id'] }})" wire:confirm="حذف شود؟" class="btn btn-danger btn-sm">حذف</button>
                </div>
            @endforeach

            <h3 style="margin-top:20px">➕ افزودن فلز</h3>
            <div class="form-row cols-3">
                <div class="form-group"><label>نام فارسی</label><input type="text" wire:model="new_metal_name" class="form-control"></div>
                <div class="form-group"><label>نام انگلیسی</label><input type="text" wire:model="new_metal_en" class="form-control" dir="ltr"></div>
                <div class="form-group"><label>عیار</label><input type="text" wire:model="new_metal_carat" class="form-control" dir="ltr"></div>
            </div>
            <button wire:click="addMetal" class="btn btn-primary">➕ افزودن فلز</button>
        </div>
    @endif

    {{-- ═══════ Monitor ═══════ --}}
    @if($tab === 'monitor')
        <div class="sg-settings-card" style="max-width:900px">
            <h3>📊 رصد API</h3>
            <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:14px">
                <div style="padding:12px;background:rgba(41,128,185,.1);border-radius:10px;text-align:center">
                    <div style="font-size:20px;font-weight:800;color:var(--primary)">{{ \App\Support\PersianNumber::toFa($monitor_stats['total'] ?? 0) }}</div>
                    <div style="font-size:11px;opacity:.7">کل درخواست</div>
                </div>
                <div style="padding:12px;background:rgba(39,174,96,.1);border-radius:10px;text-align:center">
                    <div style="font-size:20px;font-weight:800;color:var(--success)">{{ \App\Support\PersianNumber::toFa($monitor_stats['today'] ?? 0) }}</div>
                    <div style="font-size:11px;opacity:.7">امروز</div>
                </div>
                <div style="padding:12px;background:rgba(231,76,60,.1);border-radius:10px;text-align:center">
                    <div style="font-size:20px;font-weight:800;color:var(--danger)">{{ \App\Support\PersianNumber::toFa($monitor_stats['errors'] ?? 0) }}</div>
                    <div style="font-size:11px;opacity:.7">خطاها</div>
                </div>
            </div>

            <div style="display:flex;gap:8px;margin-bottom:14px">
                <input type="text" wire:model.live.debounce.400ms="monitor_filter" placeholder="🔍 فیلتر URL..." class="form-control" style="flex:1">
                <button wire:click="refreshMonitor" class="btn btn-outline btn-sm">🔄</button>
                <button wire:click="clearMonitor" wire:confirm="پاک شوند؟" class="btn btn-danger btn-sm">🗑️</button>
            </div>

            <div style="max-height:500px;overflow-y:auto">
                @forelse($monitor_logs as $log)
                    <div style="padding:8px 10px;border-bottom:1px solid var(--border);font-size:11px">
                        <div style="display:flex;gap:8px;align-items:center;margin-bottom:4px">
                            <span style="padding:2px 6px;border-radius:6px;background:{{ ($log['status_code'] ?? 0) >= 200 && ($log['status_code'] ?? 0) < 300 ? 'var(--success)' : 'var(--danger)' }};color:#fff;font-weight:700;font-size:10px;font-family:monospace">{{ $log['status_code'] ?? '—' }}</span>
                            <span style="font-family:monospace;font-weight:700">{{ $log['method'] }}</span>
                            <span style="opacity:.6">{{ $log['service'] }}</span>
                            @if($log['duration_ms']) <span style="opacity:.5">⏱️{{ $log['duration_ms'] }}ms</span> @endif
                            <span style="margin-right:auto;font-family:monospace;opacity:.5">{{ $log['created_at'] }}</span>
                        </div>
                        <div style="font-family:monospace;font-size:10px;opacity:.7;overflow:hidden;text-overflow:ellipsis" dir="ltr">{{ $log['url'] }}</div>
                        @if($log['error']) <div style="color:var(--danger);font-size:10px">❌ {{ $log['error'] }}</div> @endif
                    </div>
                @empty
                    <p style="text-align:center;padding:20px;opacity:.5">لاگی نیست</p>
                @endforelse
            </div>
        </div>
    @endif
</div>
'''

# ═══════════════════════════════════════════════════════════════
# Patch layout — اضافه کردن apply-theme listener
# ═══════════════════════════════════════════════════════════════
def patch_layout():
    layout = PROJECT / "resources/views/components/layouts/app.blade.php"
    if not layout.exists(): return

    with open(layout, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'apply-theme' in content: return

    inject = '''
    Livewire.on('apply-theme', function(data) {
        var p = Array.isArray(data) ? data[0] : data;
        if (p.theme) {
            document.documentElement.setAttribute('data-theme', p.theme);
            localStorage.setItem('theme', p.theme);
        }
        if (p.primary_color) {
            document.documentElement.style.setProperty('--primary', p.primary_color);
        }
    });
'''
    if 'Livewire.on(' not in content:
        content = content.replace(
            "document.addEventListener('livewire:init', function() {",
            "document.addEventListener('livewire:init', function() {" + inject,
            1
        )
        with open(layout, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        print("  ✓ Layout: apply-theme اضافه شد")

# ═══════════════════════════════════════════════════════════════
# اجرا
# ═══════════════════════════════════════════════════════════════
def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  قسمت ۲: تنظیمات کامل — ۱۰ تب                                 ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    backup("app/Livewire/Settings/Index.php")
    backup("resources/views/livewire/settings/index.blade.php")
    backup("resources/views/components/layouts/app.blade.php")

    print("📄 نوشتن فایل‌ها...")
    write("app/Livewire/Settings/Index.php", SETTINGS_INDEX)
    write("resources/views/livewire/settings/index.blade.php", SETTINGS_BLADE)

    print("\n🔧 Patch Layout...")
    patch_layout()

    print("\n" + "═" * 64)
    print("✅ قسمت ۲ تمام!")
    print("═" * 64)
    print(f"""
📋 اجرا کن:

  cd {PROJECT}
  php artisan optimize:clear
  php artisan view:clear

  # سرور رو ببند و دوباره باز کن
  php artisan serve

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 ۱۰ تب تنظیمات:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ⚙️ عمومی       نام، تلفن، آدرس، کدپستی، ایمیل، پول
  🎨 ظاهر         تم، رنگ اصلی، رنگ تاکیدی، تراکم
  🔌 کامرس        URL + Key + Secret + تست + سینک
  💎 شناسنامه     ابعاد، تصویر، QR، لوگو، فونت‌ها
  🏷️ برچسب        ابعاد + ۷ فونت قابل تنظیم
  🖼️ تصاویر        پس‌زمینه + لوگوها + توضیحات
  💾 پشتیبان       پشتیبان + خروجی JSON + آمار سیستم
  📜 لاگ          لاگ تغییرات با جستجو
  💠 سنگ/فلز      مدیریت کامل با گرید
  📊 رصد API      آمار + لاگ درخواست‌ها

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 بعد از تست:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  • صفحه /settings رو باز کن
  • تب‌ها رو یکی‌یکی تست کن
  • ذخیره‌سازی هر تب رو چک کن

بعد بگو "ادامه" تا قسمت ۳ (Certificates Create + Designer + Print) رو بفرستم.
""")

if __name__ == "__main__":
    main()
