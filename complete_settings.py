#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║  ShopGun V2 — تنظیمات کامل                                   ║
║  همه تب‌ها + رصد API + ظاهر + درباره                          ║
╚══════════════════════════════════════════════════════════════╝
"""
import shutil
from pathlib import Path
from datetime import datetime

PROJECT = Path(r"D:\prodo\shopgun-v2.1")
if not PROJECT.exists():
    PROJECT = Path(input("مسیر پروژه: ").strip().strip('"'))
    if not PROJECT.exists():
        print("❌ مسیر پیدا نشد"); exit(1)

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
# ۱) Migration — جدول تنظیمات + لاگ API
# ═══════════════════════════════════════════════════════════════

MIG_SETTINGS = r'''<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        if (!Schema::hasTable('app_settings')) {
            Schema::create('app_settings', function (Blueprint $table) {
                $table->id();
                $table->string('key', 100)->unique();
                $table->text('value')->nullable();
                $table->string('group', 50)->default('general');
                $table->string('type', 30)->default('string'); // string|int|bool|json
                $table->timestamps();
                $table->index('group');
            });
        }

        if (!Schema::hasTable('api_logs')) {
            Schema::create('api_logs', function (Blueprint $table) {
                $table->id();
                $table->string('service', 50)->index();      // woocommerce | server | ...
                $table->string('method', 10);                 // GET|POST|...
                $table->text('url');
                $table->integer('status_code')->nullable();
                $table->integer('duration_ms')->nullable();
                $table->text('request_body')->nullable();
                $table->longText('response_body')->nullable();
                $table->text('error')->nullable();
                $table->integer('items_count')->nullable();
                $table->foreignId('user_id')->nullable();
                $table->timestamp('created_at')->useCurrent();
                $table->index(['service', 'created_at']);
            });
        }
    }

    public function down(): void
    {
        Schema::dropIfExists('api_logs');
        Schema::dropIfExists('app_settings');
    }
};
'''

# ═══════════════════════════════════════════════════════════════
# ۲) Models
# ═══════════════════════════════════════════════════════════════

MODEL_APP_SETTING = r'''<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\Cache;

class AppSetting extends Model
{
    protected $fillable = ['key', 'value', 'group', 'type'];

    /**
     * خواندن مقدار
     */
    public static function get(string $key, $default = null)
    {
        $all = Cache::remember('app_settings_all', 60, function () {
            return static::all()->mapWithKeys(fn($s) => [$s->key => $s->value])->toArray();
        });

        if (!array_key_exists($key, $all)) return $default;

        return static::castValue($all[$key], static::where('key', $key)->value('type'));
    }

    /**
     * نوشتن مقدار
     */
    public static function put(string $key, $value, string $group = 'general', string $type = 'string'): void
    {
        if (is_array($value) || is_object($value)) {
            $value = json_encode($value, JSON_UNESCAPED_UNICODE);
            $type = 'json';
        } elseif (is_bool($value)) {
            $value = $value ? '1' : '0';
            $type = 'bool';
        }

        static::updateOrCreate(
            ['key' => $key],
            ['value' => (string) $value, 'group' => $group, 'type' => $type]
        );

        Cache::forget('app_settings_all');
    }

    /**
     * چند مقدار با هم
     */
    public static function putMany(array $data, string $group = 'general'): void
    {
        foreach ($data as $key => $value) {
            $type = 'string';
            if (is_bool($value)) $type = 'bool';
            elseif (is_int($value)) $type = 'int';
            elseif (is_array($value)) $type = 'json';
            static::put($key, $value, $group, $type);
        }
    }

    protected static function castValue($value, $type)
    {
        return match ($type) {
            'int'  => (int) $value,
            'bool' => $value === '1' || $value === 'true',
            'json' => json_decode($value, true),
            default => $value,
        };
    }
}
'''

MODEL_API_LOG = r'''<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class ApiLog extends Model
{
    public $timestamps = false;
    protected $fillable = [
        'service', 'method', 'url', 'status_code', 'duration_ms',
        'request_body', 'response_body', 'error', 'items_count',
        'user_id', 'created_at',
    ];

    protected $casts = [
        'created_at' => 'datetime',
        'status_code' => 'integer',
        'duration_ms' => 'integer',
        'items_count' => 'integer',
    ];

    public static function record(array $data): self
    {
        $data['created_at'] = now();
        $data['user_id'] = $data['user_id'] ?? (auth()->id() ?? null);

        // پاکسازی لاگ‌های قدیمی
        if (random_int(1, 20) === 1) {
            static::where('created_at', '<', now()->subDays(7))->delete();
        }

        return static::create($data);
    }

    public static function cleanup(int $days = 7): int
    {
        return static::where('created_at', '<', now()->subDays($days))->delete();
    }
}
'''

# ═══════════════════════════════════════════════════════════════
# ۳) Service — ApiLogger (لاگ‌گیری مرکزی)
# ═══════════════════════════════════════════════════════════════

API_LOGGER_SERVICE = r'''<?php

namespace App\Services;

use App\Models\ApiLog;
use Illuminate\Support\Facades\Http;

class ApiLogger
{
    /**
     * درخواست HTTP با لاگ‌گیری خودکار
     */
    public static function request(string $service, string $method, string $url, array $options = []): ?array
    {
        $start = microtime(true);

        $log = [
            'service'  => $service,
            'method'   => strtoupper($method),
            'url'      => mb_substr($url, 0, 1000),
            'request_body' => isset($options['json']) ? json_encode($options['json'], JSON_UNESCAPED_UNICODE) : null,
        ];

        try {
            $client = Http::timeout($options['timeout'] ?? 60)
                ->withOptions($options['withOptions'] ?? []);

            if (!empty($options['basic_auth'])) {
                $client = $client->withBasicAuth(...$options['basic_auth']);
            }
            if (!empty($options['headers'])) {
                $client = $client->withHeaders($options['headers']);
            }

            $response = $client->{strtolower($method)}($url, $options['json'] ?? $options['body'] ?? []);

            $duration = (int) round((microtime(true) - $start) * 1000);
            $body = $response->body();

            $itemsCount = null;
            $decoded = json_decode($body, true);
            if (is_array($decoded)) {
                if (isset($decoded[0])) $itemsCount = count($decoded);
            }

            ApiLog::record(array_merge($log, [
                'status_code'  => $response->status(),
                'duration_ms'  => $duration,
                'response_body' => mb_substr($body, 0, 5000),
                'items_count'  => $itemsCount,
            ]));

            return [
                'ok'     => $response->successful(),
                'status' => $response->status(),
                'body'   => $body,
                'json'   => $decoded,
                'ms'     => $duration,
            ];
        } catch (\Throwable $e) {
            $duration = (int) round((microtime(true) - $start) * 1000);

            ApiLog::record(array_merge($log, [
                'duration_ms' => $duration,
                'error'       => $e->getMessage(),
            ]));

            return [
                'ok'    => false,
                'error' => $e->getMessage(),
                'ms'    => $duration,
            ];
        }
    }

    /**
     * لاگ ساده (بدون درخواست)
     */
    public static function log(string $service, string $message, ?string $error = null): void
    {
        ApiLog::record([
            'service'       => $service,
            'method'        => 'LOG',
            'url'           => mb_substr($message, 0, 500),
            'response_body' => $error,
        ]);
    }
}
'''

# ═══════════════════════════════════════════════════════════════
# ۴) Livewire — Settings/Index (با همه تب‌ها)
# ═══════════════════════════════════════════════════════════════

SETTINGS_INDEX_PHP = r'''<?php

namespace App\Livewire\Settings;

use App\Models\ApiLog;
use App\Models\AppSetting;
use App\Models\Channel;
use App\Models\Metal;
use App\Models\Stone;
use App\Services\ApiLogger;
use App\Services\ProductSyncService;
use Livewire\Attributes\On;
use Livewire\Component;
use Livewire\WithFileUploads;

class Index extends Component
{
    use WithFileUploads;

    public string $tab = 'general';

    /* ═══════════════════════════════════════════════════════════
       تب کامرس
       ═══════════════════════════════════════════════════════════ */
    public string $commerce_url = '';
    public string $commerce_key = '';
    public string $commerce_secret = '';
    public string $commerce_sync_status = '';   // result
    public bool   $commerce_testing = false;
    public array  $commerce_test_result = [];
    public array  $commerce_sync_report = [];

    /* ═══════════════════════════════════════════════════════════
       تب ظاهر
       ═══════════════════════════════════════════════════════════ */
    public string $theme = 'light';
    public string $primary_color = '#0d9488';
    public string $density = 'normal';
    public string $direction = 'rtl';
    public string $font_family = 'Vazirmatn';

    /* ═══════════════════════════════════════════════════════════
       تب عمومی
       ═══════════════════════════════════════════════════════════ */
    public string $shop_name = 'جواهری مشاهیر';
    public string $shop_phone = '09151531301';
    public string $shop_address = '';
    public string $shop_postal = '';
    public string $shop_logo = '';             // base64
    public string $currency = 'تومان';

    /* ═══════════════════════════════════════════════════════════
       تب شناسنامه
       ═══════════════════════════════════════════════════════════ */
    public float $cert_width = 6.5;
    public float $cert_height = 6.5;
    public bool $cert_hide_desc = false;

    /* ═══════════════════════════════════════════════════════════
       تب برچسب
       ═══════════════════════════════════════════════════════════ */
    public int $label_width = 100;
    public int $label_height = 50;

    /* ═══════════════════════════════════════════════════════════
       تب رصد (Monitoring)
       ═══════════════════════════════════════════════════════════ */
    public string $monitor_filter = '';
    public array $monitor_stats = [];
    public array $monitor_logs = [];

    /* ═══════════════════════════════════════════════════════════
       Mount
       ═══════════════════════════════════════════════════════════ */
    public function mount(): void
    {
        $this->loadAllSettings();
        $this->refreshMonitor();
    }

    protected function loadAllSettings(): void
    {
        // کامرس
        $this->commerce_url    = (string) AppSetting::get('commerce_url', config('services.woocommerce.url', ''));
        $this->commerce_key    = (string) AppSetting::get('commerce_key', '');
        $this->commerce_secret = (string) AppSetting::get('commerce_secret', '');

        // ظاهر
        $this->theme         = (string) AppSetting::get('theme', 'light');
        $this->primary_color = (string) AppSetting::get('primary_color', '#0d9488');
        $this->density       = (string) AppSetting::get('density', 'normal');
        $this->direction     = (string) AppSetting::get('direction', 'rtl');
        $this->font_family   = (string) AppSetting::get('font_family', 'Vazirmatn');

        // عمومی
        $this->shop_name    = (string) AppSetting::get('shop_name', 'جواهری مشاهیر');
        $this->shop_phone   = (string) AppSetting::get('shop_phone', '09151531301');
        $this->shop_address = (string) AppSetting::get('shop_address', '');
        $this->shop_postal  = (string) AppSetting::get('shop_postal', '');
        $this->shop_logo    = (string) AppSetting::get('shop_logo', '');
        $this->currency     = (string) AppSetting::get('currency', 'تومان');

        // شناسنامه
        $this->cert_width     = (float) AppSetting::get('cert_width', 6.5);
        $this->cert_height    = (float) AppSetting::get('cert_height', 6.5);
        $this->cert_hide_desc = (bool) AppSetting::get('cert_hide_desc', false);

        // برچسب
        $this->label_width  = (int) AppSetting::get('label_width', 100);
        $this->label_height = (int) AppSetting::get('label_height', 50);
    }

    /* ═══════════════════════════════════════════════════════════
       ذخیره تب‌ها
       ═══════════════════════════════════════════════════════════ */
    public function saveGeneral(): void
    {
        AppSetting::putMany([
            'shop_name'    => $this->shop_name,
            'shop_phone'   => $this->shop_phone,
            'shop_address' => $this->shop_address,
            'shop_postal'  => $this->shop_postal,
            'shop_logo'    => $this->shop_logo,
            'currency'     => $this->currency,
        ], 'general');

        $this->dispatch('notify', type: 'success', message: 'تنظیمات عمومی ذخیره شد ✅');
    }

    public function saveAppearance(): void
    {
        AppSetting::putMany([
            'theme'         => $this->theme,
            'primary_color' => $this->primary_color,
            'density'       => $this->density,
            'direction'     => $this->direction,
            'font_family'   => $this->font_family,
        ], 'appearance');

        $this->dispatch('notify', type: 'success', message: 'ظاهر ذخیره شد ✅');
        $this->dispatch('theme-changed', theme: $this->theme, color: $this->primary_color);
    }

    public function saveCommerce(): void
    {
        AppSetting::putMany([
            'commerce_url'    => $this->commerce_url,
            'commerce_key'    => $this->commerce_key,
            'commerce_secret' => $this->commerce_secret,
        ], 'commerce');

        $this->dispatch('notify', type: 'success', message: 'تنظیمات کامرس ذخیره شد ✅');
    }

    public function saveCertificate(): void
    {
        AppSetting::putMany([
            'cert_width'     => $this->cert_width,
            'cert_height'    => $this->cert_height,
            'cert_hide_desc' => $this->cert_hide_desc,
        ], 'certificate');

        $this->dispatch('notify', type: 'success', message: 'تنظیمات شناسنامه ذخیره شد ✅');
    }

    public function saveLabel(): void
    {
        AppSetting::putMany([
            'label_width'  => $this->label_width,
            'label_height' => $this->label_height,
        ], 'label');

        $this->dispatch('notify', type: 'success', message: 'تنظیمات برچسب ذخیره شد ✅');
    }

    /* ═══════════════════════════════════════════════════════════
       تست اتصال WooCommerce
       ═══════════════════════════════════════════════════════════ */
    public function testCommerce(): void
    {
        $this->commerce_testing = true;
        $this->commerce_test_result = [];

        $url    = trim($this->commerce_url);
        $key    = trim($this->commerce_key);
        $secret = trim($this->commerce_secret);

        if (!$url || !$key || !$secret) {
            $this->commerce_test_result = [
                'ok'      => false,
                'message' => 'هر سه فیلد الزامی است',
            ];
            $this->commerce_testing = false;
            return;
        }

        // اصلاح URL اگر نیاز است
        $baseUrl = rtrim($url, '/');
        if (!str_contains($baseUrl, '/wp-json')) {
            $baseUrl .= '/wp-json/wc/v3';
        }
        $testUrl = $baseUrl . '/system_status';

        $result = ApiLogger::request('woocommerce', 'GET', $testUrl, [
            'basic_auth' => [$key, $secret],
            'timeout'    => 20,
        ]);

        if (!$result['ok']) {
            $this->commerce_test_result = [
                'ok'      => false,
                'message' => $result['error'] ?? ('HTTP ' . ($result['status'] ?? '?')),
                'ms'      => $result['ms'],
            ];
        } else {
            $data = $result['json'] ?? [];
            $this->commerce_test_result = [
                'ok'          => true,
                'message'     => 'اتصال موفق ✅',
                'ms'          => $result['ms'],
                'environment' => $data['environment']['version'] ?? '?',
                'wc_version'  => $data['environment']['wp_version'] ?? '?',
                'currency'    => $data['settings']['currency'] ?? '?',
            ];
        }

        $this->commerce_testing = false;
        $this->refreshMonitor();
    }

    /* ═══════════════════════════════════════════════════════════
       سینک محصولات
       ═══════════════════════════════════════════════════════════ */
    public function syncProducts(): void
    {
        // ذخیره تنظیمات قبل از سینک
        $this->saveCommerce();

        $this->commerce_sync_report = [
            'running' => true,
            'message' => 'در حال سینک محصولات...',
        ];

        try {
            $report = ProductSyncService::syncFromWoo(true);
            $this->commerce_sync_report = array_merge($report, [
                'running' => false,
                'success' => true,
            ]);

            $this->dispatch('notify', type: 'success',
                message: "سینک محصولات: {$report['total']} کل، {$report['created']} جدید، {$report['updated']} بروز");
        } catch (\Throwable $e) {
            $this->commerce_sync_report = [
                'running' => false,
                'success' => false,
                'message' => $e->getMessage(),
            ];
            $this->dispatch('notify', type: 'error', message: 'سینک ناموفق: ' . $e->getMessage());
        }

        $this->refreshMonitor();
    }

    /* ═══════════════════════════════════════════════════════════
       رصد API
       ═══════════════════════════════════════════════════════════ */
    public function refreshMonitor(): void
    {
        $q = ApiLog::query();

        if ($this->monitor_filter) {
            $q->where(function ($qq) {
                $qq->where('service', 'like', '%' . $this->monitor_filter . '%')
                   ->orWhere('url', 'like', '%' . $this->monitor_filter . '%')
                   ->orWhere('method', 'like', '%' . $this->monitor_filter . '%');
            });
        }

        // آمار
        $this->monitor_stats = [
            'total'    => ApiLog::count(),
            'today'    => ApiLog::whereDate('created_at', today())->count(),
            'errors'   => ApiLog::whereNotNull('error')->whereDate('created_at', '>=', now()->subDay())->count(),
            'avg_ms'   => (int) round(ApiLog::whereDate('created_at', '>=', now()->subDay())->avg('duration_ms') ?? 0),
            'success'  => ApiLog::whereDate('created_at', '>=', now()->subDay())
                            ->whereIn('status_code', [200, 201, 204])->count(),
        ];

        // لاگ‌های اخیر
        $this->monitor_logs = $q->latest('id')->limit(50)->get()->map(fn($l) => [
            'id'          => $l->id,
            'service'     => $l->service,
            'method'      => $l->method,
            'url'         => $l->url,
            'status_code' => $l->status_code,
            'duration_ms' => $l->duration_ms,
            'error'       => $l->error,
            'items_count' => $l->items_count,
            'created_at'  => $l->created_at?->format('H:i:s'),
            'created_date' => $l->created_at?->format('Y-m-d'),
        ])->toArray();
    }

    public function clearMonitor(): void
    {
        ApiLog::truncate();
        $this->refreshMonitor();
        $this->dispatch('notify', type: 'success', message: 'لاگ API پاک شد');
    }

    public function updatedMonitorFilter(): void
    {
        $this->refreshMonitor();
    }

    #[On('refresh-monitor')]
    public function onRefreshMonitor(): void
    {
        $this->refreshMonitor();
    }

    /* ═══════════════════════════════════════════════════════════
       تغییر تب
       ═══════════════════════════════════════════════════════════ */
    public function setTab(string $tab): void
    {
        $this->tab = $tab;
        if ($tab === 'monitor') $this->refreshMonitor();
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
            'php_version'      => PHP_VERSION,
            'laravel_version'  => app()->version(),
            'db_driver'        => config('database.default'),
            'orders_count'     => \App\Models\Order::count(),
            'customers_count'  => \App\Models\Customer::count(),
            'products_count'   => \App\Models\Product::count(),
            'certificates_count' => \App\Models\Certificate::count(),
            'storage_used'     => $this->humanFilesize($this->dirSize(storage_path('app'))),
            'disk_free'        => $this->humanFilesize(disk_free_space(storage_path())),
            'api_today'        => ApiLog::whereDate('created_at', today())->count(),
        ];
    }

    protected function dirSize(string $path): int
    {
        if (!is_dir($path)) return 0;
        $size = 0;
        foreach (new \RecursiveIteratorIterator(new \RecursiveDirectoryIterator($path, \FilesystemIterator::SKIP_DOTS)) as $file) {
            $size += $file->getSize();
        }
        return $size;
    }

    protected function humanFilesize(int $bytes, int $decimals = 2): string
    {
        $units = ['B', 'KB', 'MB', 'GB', 'TB'];
        $i = 0;
        while ($bytes >= 1024 && $i < count($units) - 1) {
            $bytes /= 1024;
            $i++;
        }
        return round($bytes, $decimals) . ' ' . $units[$i];
    }
}
'''

SETTINGS_INDEX_BLADE = r'''<div class="p-4 md:p-6 max-w-6xl mx-auto">
    <h1 class="text-xl md:text-2xl font-bold mb-4 flex items-center gap-2">
        ⚙️ تنظیمات
        <span class="badge badge-primary badge-sm">{{ config('app.version', '2.1.0') }}</span>
    </h1>

    {{-- ═══════ تب‌ها ═══════ --}}
    <div class="bg-base-100 rounded-2xl shadow border border-base-300 overflow-hidden">
        <div class="flex border-b border-base-300 bg-base-200/50 overflow-x-auto">
            @foreach([
                'general'     => ['⚙️', 'عمومی'],
                'appearance'  => ['🎨', 'ظاهر'],
                'commerce'    => ['🔌', 'کامرس'],
                'certificate' => ['💎', 'شناسنامه'],
                'label'       => ['🏷️', 'برچسب'],
                'monitor'     => ['📊', 'رصد API'],
                'health'      => ['🏥', 'سلامت'],
                'about'       => ['ℹ️', 'درباره'],
            ] as $key => $meta)
                <button wire:click="setTab('{{ $key }}')"
                        class="px-4 py-3 text-sm font-bold whitespace-nowrap border-b-2 transition
                            {{ $tab === $key ? 'border-primary text-primary bg-base-100' : 'border-transparent text-base-content/60 hover:text-base-content hover:bg-base-100/50' }}">
                    {{ $meta[0] }} {{ $meta[1] }}
                </button>
            @endforeach
        </div>

        <div class="p-4 md:p-6">

            {{-- ═══════════════════════════════════════════════════
                 تب عمومی
                 ═══════════════════════════════════════════════════ --}}
            @if($tab === 'general')
                <div class="space-y-4">
                    <h2 class="font-bold text-lg mb-3">اطلاعات فروشگاه</h2>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="form-control">
                            <label class="label"><span class="label-text font-bold text-xs">🏪 نام فروشگاه</span></label>
                            <input type="text" wire:model="shop_name" class="input input-bordered w-full">
                        </div>
                        <div class="form-control">
                            <label class="label"><span class="label-text font-bold text-xs">📱 تلفن</span></label>
                            <input type="text" wire:model="shop_phone" dir="ltr"
                                   class="input input-bordered w-full font-mono">
                        </div>
                        <div class="form-control md:col-span-2">
                            <label class="label"><span class="label-text font-bold text-xs">📍 آدرس</span></label>
                            <textarea wire:model="shop_address" rows="2" class="textarea textarea-bordered w-full"></textarea>
                        </div>
                        <div class="form-control">
                            <label class="label"><span class="label-text font-bold text-xs">📮 کدپستی</span></label>
                            <input type="text" wire:model="shop_postal" dir="ltr"
                                   class="input input-bordered w-full font-mono">
                        </div>
                        <div class="form-control">
                            <label class="label"><span class="label-text font-bold text-xs">💵 واحد پول</span></label>
                            <input type="text" wire:model="currency" class="input input-bordered w-full">
                        </div>
                    </div>

                    <div class="flex justify-end pt-3 border-t">
                        <button wire:click="saveGeneral" wire:loading.attr="disabled"
                                class="btn btn-success btn-sm">
                            <span wire:loading.remove wire:target="saveGeneral">💾 ذخیره</span>
                            <span wire:loading wire:target="saveGeneral">⏳...</span>
                        </button>
                    </div>
                </div>
            @endif

            {{-- ═══════════════════════════════════════════════════
                 تب ظاهر
                 ═══════════════════════════════════════════════════ --}}
            @if($tab === 'appearance')
                <div class="space-y-4">
                    <h2 class="font-bold text-lg mb-3">🎨 ظاهر برنامه</h2>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <div class="form-control">
                            <label class="label"><span class="label-text font-bold text-xs">🌓 تم</span></label>
                            <div class="flex gap-2">
                                @foreach(['light' => '☀️ روشن', 'dark' => '🌙 تیره', 'auto' => '🌗 خودکار'] as $k => $v)
                                    <label class="flex-1 cursor-pointer">
                                        <input type="radio" wire:model="theme" value="{{ $k }}" class="peer hidden">
                                        <div class="p-3 rounded-lg border-2 border-base-300 text-center text-xs font-bold
                                                    peer-checked:border-primary peer-checked:bg-primary/10">
                                            {{ $v }}
                                        </div>
                                    </label>
                                @endforeach
                            </div>
                        </div>

                        <div class="form-control">
                            <label class="label"><span class="label-text font-bold text-xs">📐 تراکم</span></label>
                            <div class="flex gap-2">
                                @foreach(['compact' => 'فشرده', 'normal' => 'معمولی', 'comfortable' => 'راحت'] as $k => $v)
                                    <label class="flex-1 cursor-pointer">
                                        <input type="radio" wire:model="density" value="{{ $k }}" class="peer hidden">
                                        <div class="p-3 rounded-lg border-2 border-base-300 text-center text-xs font-bold
                                                    peer-checked:border-primary peer-checked:bg-primary/10">
                                            {{ $v }}
                                        </div>
                                    </label>
                                @endforeach
                            </div>
                        </div>

                        <div class="form-control">
                            <label class="label"><span class="label-text font-bold text-xs">🎨 رنگ اصلی</span></label>
                            <div class="flex gap-2 items-center">
                                <input type="color" wire:model="primary_color"
                                       class="w-16 h-10 rounded-lg cursor-pointer border-2 border-base-300">
                                <input type="text" wire:model="primary_color" dir="ltr"
                                       class="input input-bordered flex-1 font-mono text-sm">
                            </div>
                        </div>

                        <div class="form-control">
                            <label class="label"><span class="label-text font-bold text-xs">🔤 فونت</span></label>
                            <select wire:model="font_family" class="select select-bordered w-full">
                                <option value="Vazirmatn">وزیرمتن</option>
                                <option value="Tahoma">تاهوما</option>
                                <option value="IRANSans">ایران‌سنس</option>
                                <option value="Yekan">یکان</option>
                            </select>
                        </div>
                    </div>

                    <div class="flex justify-end pt-3 border-t">
                        <button wire:click="saveAppearance" wire:loading.attr="disabled"
                                class="btn btn-success btn-sm">
                            <span wire:loading.remove wire:target="saveAppearance">💾 ذخیره</span>
                            <span wire:loading wire:target="saveAppearance">⏳...</span>
                        </button>
                    </div>
                </div>
            @endif

            {{-- ═══════════════════════════════════════════════════
                 تب کامرس (WooCommerce)
                 ═══════════════════════════════════════════════════ --}}
            @if($tab === 'commerce')
                <div class="space-y-5">
                    <h2 class="font-bold text-lg">🔌 اتصال به WooCommerce</h2>

                    <div class="alert alert-info py-2 text-xs">
                        <span>💡 برای ساخت کلید: وردپرس → WooCommerce → Settings → Advanced → REST API → Add key (با دسترسی Read/Write)</span>
                    </div>

                    <div class="space-y-3">
                        <div class="form-control">
                            <label class="label">
                                <span class="label-text font-bold text-xs">🌐 آدرس سایت</span>
                            </label>
                            <input type="text" wire:model="commerce_url" dir="ltr"
                                   placeholder="https://yoursite.com"
                                   class="input input-bordered w-full font-mono text-sm">
                            <span class="text-[10px] text-base-content/50 mt-1">
                                فقط آدرس اصلی. مسیر وردپرس خودکار اضافه می‌شود.
                            </span>
                        </div>

                        <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                            <div class="form-control">
                                <label class="label"><span class="label-text font-bold text-xs">🔑 Consumer Key</span></label>
                                <input type="text" wire:model="commerce_key" dir="ltr"
                                       placeholder="ck_xxxxxxxxxxxx"
                                       class="input input-bordered w-full font-mono text-sm">
                            </div>
                            <div class="form-control">
                                <label class="label"><span class="label-text font-bold text-xs">🔐 Consumer Secret</span></label>
                                <div class="relative">
                                    <input type="password" wire:model="commerce_secret" dir="ltr"
                                           placeholder="cs_xxxxxxxxxxxx"
                                           id="commerce-secret-input"
                                           class="input input-bordered w-full font-mono text-sm pr-12">
                                    <button type="button"
                                            onclick="const i=document.getElementById('commerce-secret-input'); i.type = i.type==='password'?'text':'password';"
                                            class="absolute left-2 top-1/2 -translate-y-1/2 btn btn-ghost btn-xs">
                                        👁️
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    {{-- نتیجه تست --}}
                    @if(!empty($commerce_test_result))
                        <div class="alert {{ $commerce_test_result['ok'] ? 'alert-success' : 'alert-error' }} py-3">
                            <div class="flex-1">
                                <div class="font-bold text-sm">
                                    {{ $commerce_test_result['ok'] ? '✅' : '❌' }}
                                    {{ $commerce_test_result['message'] }}
                                </div>
                                @if($commerce_test_result['ok'])
                                    <div class="text-xs mt-1">
                                        🕐 زمان پاسخ: {{ \App\Support\PersianNumber::toFa($commerce_test_result['ms'] ?? '?') }} ms
                                    </div>
                                    @if(!empty($commerce_test_result['wc_version']))
                                        <div class="text-xs">📦 WooCommerce: {{ $commerce_test_result['wc_version'] }}</div>
                                    @endif
                                    @if(!empty($commerce_test_result['currency']))
                                        <div class="text-xs">💵 واحد پول: {{ $commerce_test_result['currency'] }}</div>
                                    @endif
                                @endif
                            </div>
                        </div>
                    @endif

                    {{-- نتیجه سینک --}}
                    @if(!empty($commerce_sync_report))
                        <div class="alert {{ ($commerce_sync_report['success'] ?? false) ? 'alert-success' : 'alert-error' }}">
                            <div class="text-sm">
                                @if($commerce_sync_report['running'] ?? false)
                                    ⏳ {{ $commerce_sync_report['message'] }}
                                @elseif($commerce_sync_report['success'] ?? false)
                                    <div class="font-bold">✅ سینک کامل شد</div>
                                    <div class="text-xs mt-1">
                                        📦 کل: {{ \App\Support\PersianNumber::toFa($commerce_sync_report['total'] ?? 0) }}
                                        · ✨ جدید: {{ \App\Support\PersianNumber::toFa($commerce_sync_report['created'] ?? 0) }}
                                        · 🔄 بروز: {{ \App\Support\PersianNumber::toFa($commerce_sync_report['updated'] ?? 0) }}
                                        · ❌ خطا: {{ \App\Support\PersianNumber::toFa($commerce_sync_report['failed'] ?? 0) }}
                                    </div>
                                @else
                                    ❌ {{ $commerce_sync_report['message'] ?? 'خطا' }}
                                @endif
                            </div>
                        </div>
                    @endif

                    {{-- دکمه‌ها --}}
                    <div class="flex flex-wrap gap-2 pt-3 border-t">
                        <button wire:click="saveCommerce" wire:loading.attr="disabled"
                                class="btn btn-primary btn-sm">
                            <span wire:loading.remove wire:target="saveCommerce">💾 ذخیره</span>
                            <span wire:loading wire:target="saveCommerce">⏳...</span>
                        </button>

                        <button wire:click="testCommerce" wire:loading.attr="disabled"
                                class="btn btn-info btn-sm">
                            <span wire:loading.remove wire:target="testCommerce">🔌 تست اتصال</span>
                            <span wire:loading wire:target="testCommerce">⏳ در حال تست...</span>
                        </button>

                        <button wire:click="syncProducts" wire:loading.attr="disabled"
                                class="btn btn-success btn-sm">
                            <span wire:loading.remove wire:target="syncProducts">📥 سینک کامل محصولات</span>
                            <span wire:loading wire:target="syncProducts">⏳...</span>
                        </button>

                        <button wire:click="setTab('monitor')"
                                class="btn btn-outline btn-sm">
                            📊 رصد لاگ‌ها
                        </button>
                    </div>
                </div>
            @endif

            {{-- ═══════════════════════════════════════════════════
                 تب شناسنامه
                 ═══════════════════════════════════════════════════ --}}
            @if($tab === 'certificate')
                <div class="space-y-4">
                    <h2 class="font-bold text-lg mb-3">💎 تنظیمات شناسنامه</h2>

                    <div class="grid grid-cols-2 md:grid-cols-3 gap-3">
                        <div class="form-control">
                            <label class="label"><span class="label-text font-bold text-xs">📐 عرض (cm)</span></label>
                            <input type="number" step="0.1" wire:model.live="cert_width"
                                   class="input input-bordered" dir="ltr">
                        </div>
                        <div class="form-control">
                            <label class="label"><span class="label-text font-bold text-xs">📐 ارتفاع (cm)</span></label>
                            <input type="number" step="0.1" wire:model.live="cert_height"
                                   class="input input-bordered" dir="ltr">
                        </div>
                        <div class="form-control">
                            <label class="label"><span class="label-text font-bold text-xs">📏 پیش‌فرض‌ها</span></label>
                            <div class="flex gap-1 flex-wrap">
                                <button type="button" wire:click="$set('cert_width', 6.5); $set('cert_height', 6.5)"
                                        class="btn btn-outline btn-xs">۶.۵×۶.۵</button>
                                <button type="button" wire:click="$set('cert_width', 7); $set('cert_height', 7)"
                                        class="btn btn-outline btn-xs">۷×۷</button>
                                <button type="button" wire:click="$set('cert_width', 8); $set('cert_height', 6)"
                                        class="btn btn-outline btn-xs">۸×۶</button>
                            </div>
                        </div>
                    </div>

                    <label class="flex items-center gap-2 p-3 bg-base-200/50 rounded-lg cursor-pointer">
                        <input type="checkbox" wire:model="cert_hide_desc" class="checkbox checkbox-sm">
                        <span class="text-sm">🚫 حذف توضیحات کنار تصویر</span>
                    </label>

                    <div class="flex justify-end pt-3 border-t gap-2">
                        <a href="{{ route('certificates.designer') }}" class="btn btn-secondary btn-sm">
                            🎨 ویرایشگر طرح
                        </a>
                        <button wire:click="saveCertificate" wire:loading.attr="disabled"
                                class="btn btn-success btn-sm">
                            <span wire:loading.remove wire:target="saveCertificate">💾 ذخیره</span>
                            <span wire:loading wire:target="saveCertificate">⏳...</span>
                        </button>
                    </div>
                </div>
            @endif

            {{-- ═══════════════════════════════════════════════════
                 تب برچسب
                 ═══════════════════════════════════════════════════ --}}
            @if($tab === 'label')
                <div class="space-y-4">
                    <h2 class="font-bold text-lg mb-3">🏷️ تنظیمات برچسب</h2>

                    <div class="grid grid-cols-2 gap-3">
                        <div class="form-control">
                            <label class="label"><span class="label-text font-bold text-xs">📐 عرض (mm)</span></label>
                            <input type="number" wire:model="label_width" class="input input-bordered" dir="ltr">
                        </div>
                        <div class="form-control">
                            <label class="label"><span class="label-text font-bold text-xs">📐 ارتفاع (mm)</span></label>
                            <input type="number" wire:model="label_height" class="input input-bordered" dir="ltr">
                        </div>
                    </div>

                    <div class="flex justify-end pt-3 border-t">
                        <button wire:click="saveLabel" wire:loading.attr="disabled"
                                class="btn btn-success btn-sm">
                            <span wire:loading.remove wire:target="saveLabel">💾 ذخیره</span>
                            <span wire:loading wire:target="saveLabel">⏳...</span>
                        </button>
                    </div>
                </div>
            @endif

            {{-- ═══════════════════════════════════════════════════
                 تب رصد API
                 ═══════════════════════════════════════════════════ --}}
            @if($tab === 'monitor')
                <div class="space-y-4">
                    <div class="flex items-center justify-between flex-wrap gap-2">
                        <h2 class="font-bold text-lg">📊 رصد درخواست‌های API</h2>
                        <div class="flex gap-2">
                            <button wire:click="refreshMonitor" class="btn btn-outline btn-xs">🔄 به‌روزرسانی</button>
                            <button wire:click="clearMonitor" wire:confirm="پاک شود؟" class="btn btn-error btn-xs">🗑️ پاک</button>
                        </div>
                    </div>

                    {{-- آمار --}}
                    @if(!empty($monitor_stats))
                        <div class="grid grid-cols-2 md:grid-cols-5 gap-2">
                            <div class="bg-primary/10 rounded-lg p-3 text-center">
                                <div class="text-2xl font-bold text-primary">{{ \App\Support\PersianNumber::toFa($monitor_stats['total'] ?? 0) }}</div>
                                <div class="text-[10px] text-base-content/60">کل</div>
                            </div>
                            <div class="bg-info/10 rounded-lg p-3 text-center">
                                <div class="text-2xl font-bold text-info">{{ \App\Support\PersianNumber::toFa($monitor_stats['today'] ?? 0) }}</div>
                                <div class="text-[10px] text-base-content/60">امروز</div>
                            </div>
                            <div class="bg-success/10 rounded-lg p-3 text-center">
                                <div class="text-2xl font-bold text-success">{{ \App\Support\PersianNumber::toFa($monitor_stats['success'] ?? 0) }}</div>
                                <div class="text-[10px] text-base-content/60">موفق ۲۴س</div>
                            </div>
                            <div class="bg-error/10 rounded-lg p-3 text-center">
                                <div class="text-2xl font-bold text-error">{{ \App\Support\PersianNumber::toFa($monitor_stats['errors'] ?? 0) }}</div>
                                <div class="text-[10px] text-base-content/60">خطا ۲۴س</div>
                            </div>
                            <div class="bg-warning/10 rounded-lg p-3 text-center">
                                <div class="text-2xl font-bold text-warning">{{ \App\Support\PersianNumber::toFa($monitor_stats['avg_ms'] ?? 0) }}</div>
                                <div class="text-[10px] text-base-content/60">میانگین ms</div>
                            </div>
                        </div>
                    @endif

                    {{-- فیلتر --}}
                    <input type="text" wire:model.live.debounce.400ms="monitor_filter"
                           placeholder="🔍 فیلتر در سرویس، URL یا Method..."
                           class="input input-bordered input-sm w-full">

                    {{-- لیست لاگ‌ها --}}
                    <div class="border border-base-300 rounded-lg overflow-hidden max-h-[600px] overflow-y-auto">
                        @forelse($monitor_logs as $log)
                            <div class="p-2 border-b border-base-200 last:border-0 hover:bg-base-200/30"
                                 wire:key="log-{{ $log['id'] }}">
                                <div class="flex items-center gap-2 flex-wrap">
                                    {{-- status --}}
                                    @php
                                        $sc = $log['status_code'];
                                        $color = !$sc ? 'badge-ghost' : ($sc >= 200 && $sc < 300 ? 'badge-success' : ($sc >= 400 ? 'badge-error' : 'badge-warning'));
                                    @endphp
                                    <span class="badge {{ $color }} badge-xs font-mono">{{ $sc ?? '—' }}</span>

                                    {{-- method --}}
                                    <span class="badge badge-outline badge-xs font-mono">{{ $log['method'] }}</span>

                                    {{-- service --}}
                                    <span class="text-[10px] font-bold text-base-content/60">{{ $log['service'] }}</span>

                                    {{-- duration --}}
                                    @if($log['duration_ms'])
                                        <span class="text-[10px] font-mono text-base-content/50">
                                            ⏱️ {{ \App\Support\PersianNumber::toFa($log['duration_ms']) }}ms
                                        </span>
                                    @endif

                                    {{-- items --}}
                                    @if($log['items_count'])
                                        <span class="text-[10px] text-base-content/50">
                                            📦 {{ \App\Support\PersianNumber::toFa($log['items_count']) }}
                                        </span>
                                    @endif

                                    {{-- time --}}
                                    <span class="text-[10px] font-mono text-base-content/40 mr-auto" dir="ltr">
                                        {{ $log['created_at'] }}
                                    </span>
                                </div>
                                <div class="font-mono text-[10px] text-base-content/70 mt-1 truncate" dir="ltr"
                                     title="{{ $log['url'] }}">
                                    {{ mb_substr($log['url'], 0, 100) }}
                                </div>
                                @if($log['error'])
                                    <div class="text-[10px] text-error mt-1 truncate" title="{{ $log['error'] }}">
                                        ❌ {{ $log['error'] }}
                                    </div>
                                @endif
                            </div>
                        @empty
                            <div class="text-center py-8 text-base-content/50">
                                <div class="text-3xl mb-2 opacity-30">📊</div>
                                <div class="text-sm">هیچ لاگی ثبت نشده</div>
                                <div class="text-xs mt-1">بعد از تست اتصال WooCommerce، لاگ‌ها اینجا نمایش داده می‌شوند</div>
                            </div>
                        @endforelse
                    </div>
                </div>
            @endif

            {{-- ═══════════════════════════════════════════════════
                 تب سلامت سیستم
                 ═══════════════════════════════════════════════════ --}}
            @if($tab === 'health')
                <div class="space-y-4">
                    <h2 class="font-bold text-lg mb-3">🏥 سلامت سیستم</h2>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                        @foreach([
                            ['🖥️', 'PHP', $stats['php_version'] ?? '?', true],
                            ['⚡', 'Laravel', $stats['laravel_version'] ?? '?', true],
                            ['🗄️', 'Database', $stats['db_driver'] ?? '?', true],
                            ['💾', 'فضای مصرفی', $stats['storage_used'] ?? '?', true],
                            ['💿', 'فضای آزاد', $stats['disk_free'] ?? '?', true],
                            ['📊', 'API امروز', \App\Support\PersianNumber::toFa($stats['api_today'] ?? 0), true],
                        ] as $item)
                            <div class="flex items-center justify-between p-3 rounded-lg bg-base-200/50 border border-base-300">
                                <div class="flex items-center gap-2">
                                    <span class="text-xl">{{ $item[0] }}</span>
                                    <span class="text-sm font-bold">{{ $item[1] }}</span>
                                </div>
                                <div class="flex items-center gap-2">
                                    <span class="font-mono text-sm">{{ $item[2] }}</span>
                                    @if($item[3])
                                        <span class="badge badge-success badge-xs">✓</span>
                                    @else
                                        <span class="badge badge-error badge-xs">!</span>
                                    @endif
                                </div>
                            </div>
                        @endforeach
                    </div>

                    <div class="divider text-xs">داده‌ها</div>

                    <div class="grid grid-cols-2 md:grid-cols-4 gap-2">
                        @foreach([
                            ['📦', 'سفارش', $stats['orders_count'] ?? 0],
                            ['👥', 'مشتری', $stats['customers_count'] ?? 0],
                            ['🛍️', 'محصول', $stats['products_count'] ?? 0],
                            ['💎', 'شناسنامه', $stats['certificates_count'] ?? 0],
                        ] as $item)
                            <div class="bg-base-200/50 rounded-lg p-3 text-center border border-base-300">
                                <div class="text-3xl mb-1">{{ $item[0] }}</div>
                                <div class="text-xl font-bold text-primary">{{ \App\Support\PersianNumber::toFa($item[2]) }}</div>
                                <div class="text-[10px] text-base-content/60">{{ $item[1] }}</div>
                            </div>
                        @endforeach
                    </div>
                </div>
            @endif

            {{-- ═══════════════════════════════════════════════════
                 تب درباره
                 ═══════════════════════════════════════════════════ --}}
            @if($tab === 'about')
                <div class="space-y-5">
                    <div class="text-center py-6">
                        <div class="text-5xl mb-3">💎</div>
                        <h2 class="text-2xl font-bold">ShopGun V2</h2>
                        <p class="text-sm text-base-content/60 mt-1">شاپگان نسخه ۲</p>
                        <div class="badge badge-primary badge-lg mt-2">v{{ config('app.version', '2.1.0') }}</div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div class="card bg-base-200/50 border border-base-300">
                            <div class="card-body p-3">
                                <div class="text-xs font-bold text-base-content/60">🏢 سازنده</div>
                                <div class="text-sm font-bold mt-1">گروه هنری اقاقیا</div>
                            </div>
                        </div>
                        <div class="card bg-base-200/50 border border-base-300">
                            <div class="card-body p-3">
                                <div class="text-xs font-bold text-base-content/60">🧠 الگوریتم و کانفیگ</div>
                                <div class="text-sm font-bold mt-1">امیر حاجی قاسمی</div>
                            </div>
                        </div>
                        <div class="card bg-base-200/50 border border-base-300">
                            <div class="card-body p-3">
                                <div class="text-xs font-bold text-base-content/60">📍 محل</div>
                                <div class="text-sm font-bold mt-1">نیشابور</div>
                            </div>
                        </div>
                        <div class="card bg-base-200/50 border border-base-300">
                            <div class="card-body p-3">
                                <div class="text-xs font-bold text-base-content/60">📅 ساخت اولیه</div>
                                <div class="text-sm font-bold mt-1">بهمن ۱۴۰۲</div>
                            </div>
                        </div>
                        <div class="card bg-base-200/50 border border-base-300 md:col-span-2">
                            <div class="card-body p-3">
                                <div class="text-xs font-bold text-base-content/60">🚀 بازطراحی نسخه ۲</div>
                                <div class="text-sm font-bold mt-1">شهریور ۱۴۰۵</div>
                            </div>
                        </div>
                    </div>

                    <div class="divider text-xs">تغییرات نسخه ۲.۱.۰</div>

                    <div class="bg-base-200/50 rounded-lg p-4">
                        <ul class="space-y-2 text-sm">
                            <li class="flex items-start gap-2">
                                <span class="badge badge-success badge-xs mt-1">✓</span>
                                <span>سیستم کامل کاربران و دسترسی‌ها</span>
                            </li>
                            <li class="flex items-start gap-2">
                                <span class="badge badge-success badge-xs mt-1">✓</span>
                                <span>چند تلفن و چند آدرس برای هر مشتری</span>
                            </li>
                            <li class="flex items-start gap-2">
                                <span class="badge badge-success badge-xs mt-1">✓</span>
                                <span>CustomerPicker و ProductPicker هوشمند</span>
                            </li>
                            <li class="flex items-start gap-2">
                                <span class="badge badge-success badge-xs mt-1">✓</span>
                                <span>جدول محصولات محلی با sync از WooCommerce</span>
                            </li>
                            <li class="flex items-start gap-2">
                                <span class="badge badge-success badge-xs mt-1">✓</span>
                                <span>رصد زنده‌ی درخواست‌های API</span>
                            </li>
                            <li class="flex items-start gap-2">
                                <span class="badge badge-success badge-xs mt-1">✓</span>
                                <span>تنظیمات کامل: ظاهر، کامرس، شناسنامه، برچسب</span>
                            </li>
                            <li class="flex items-start gap-2">
                                <span class="badge badge-primary badge-xs mt-1">◉</span>
                                <span>ویرایشگر حرفه‌ای شناسنامه (در حال توسعه)</span>
                            </li>
                        </ul>
                    </div>

                    <div class="flex flex-wrap justify-center gap-2 pt-3 border-t">
                        <a href="https://github.com" target="_blank" class="btn btn-outline btn-sm">
                            📖 مستندات
                        </a>
                        <a href="#" class="btn btn-outline btn-sm">
                            🐛 گزارش مشکل
                        </a>
                        <a href="#" class="btn btn-outline btn-sm">
                            ✉️ تماس با ما
                        </a>
                    </div>
                </div>
            @endif

        </div>
    </div>
</div>
'''

# ═══════════════════════════════════════════════════════════════
# ۵) Append به WooCommerceService برای لاگ‌گیری
# ═══════════════════════════════════════════════════════════════

WOO_LOGGER_PATCH = r'''

    /* ═══════════════════════════════════════════════════════════
       Wrapper با لاگ‌گیری خودکار — فاز Settings
       ═══════════════════════════════════════════════════════════ */

    /**
     * درخواست GET با لاگ خودکار
     */
    protected function loggedGet(string $url, array $query = []): ?array
    {
        $full = $url . ($query ? '?' . http_build_query($query) : '');

        $result = \App\Services\ApiLogger::request('woocommerce', 'GET', $full, [
            'basic_auth' => [$this->key ?? '', $this->secret ?? ''],
            'timeout'    => 60,
        ]);

        if (!$result['ok']) {
            return null;
        }

        return $result['json'] ?? null;
    }
'''

# ═══════════════════════════════════════════════════════════════
# ۶) Route Update
# ═══════════════════════════════════════════════════════════════

ROUTES_PATCH = r'''
    // ═══ Settings (کامل) ═══
    // از قبل موجود است
'''

# ═══════════════════════════════════════════════════════════════
# ۷) AppServiceProvider — پاس دادن setting به view
# ═══════════════════════════════════════════════════════════════

def patch_app_provider():
    path = PROJECT / "app/Providers/AppServiceProvider.php"
    if not path.exists():
        print("  ⚠️ AppServiceProvider پیدا نشد")
        return

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'app_settings_shared' in content:
        print("  ⏭ AppServiceProvider از قبل patch شده")
        return

    # پیدا کردن boot()
    if 'public function boot(): void' not in content:
        print("  ⚠️ boot() پیدا نشد")
        return

    # اضافه کردن view share
    inject = '''    public function boot(): void
    {
        try {
            if (\\Illuminate\\Support\\Facades\\Schema::hasTable('app_settings')) {
                view()->share('appSettings', function () {
                    return [
                        'theme'         => \\App\\Models\\AppSetting::get('theme', 'light'),
                        'primary_color' => \\App\\Models\\AppSetting::get('primary_color', '#0d9488'),
                        'density'       => \\App\\Models\\AppSetting::get('density', 'normal'),
                        'shop_name'     => \\App\\Models\\AppSetting::get('shop_name', 'جواهری مشاهیر'),
                    ];
                });
            }
        } catch (\\Throwable $e) {
            // silent
        }
    }'''

    old = 'public function boot(): void\n    {\n        //\n    }'
    if old in content:
        content = content.replace(old, inject)
    else:
        # تلاش برای پیدا کردن boot با محتوای دلخواه
        import re
        pattern = r'public function boot\(\): void\s*\{[^}]*\}'
        if re.search(pattern, content):
            content = re.sub(pattern, inject, content, count=1)
        else:
            print("  ⚠️ boot() پیدا نشد برای جایگزینی")
            return

    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print("  ✓ AppServiceProvider patch شد")

# ═══════════════════════════════════════════════════════════════
# ۸) Layout — اعمال تم از settings
# ═══════════════════════════════════════════════════════════════

def patch_layout_theme():
    layout = PROJECT / "resources/views/components/layouts/app.blade.php"
    if not layout.exists():
        print("  ⚠️ Layout پیدا نشد")
        return

    with open(layout, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'app_settings_theme' in content:
        print("  ⏭ Layout از قبل patch شده")
        return

    # اضافه کردن style با متغیرهای CSS
    inject = '''{{-- ═══ Theme از AppSettings ═══ --}}
    @php
        try {
            $__theme = \\App\\Models\\AppSetting::get('theme', 'light');
            $__color = \\App\\Models\\AppSetting::get('primary_color', '#0d9488');
            $__density = \\App\\Models\\AppSetting::get('density', 'normal');
        } catch (\\Throwable $e) {
            $__theme = 'light';
            $__color = '#0d9488';
            $__density = 'normal';
        }
    @endphp
    <style id="app_settings_theme">
        :root {
            --sg-primary: {{ $__color }};
        }
        [data-theme="dark"] {
            --sg-primary: {{ $__color }};
        }
        .btn-primary { background-color: var(--sg-primary) !important; border-color: var(--sg-primary) !important; }
        .text-primary { color: var(--sg-primary) !important; }
        .border-primary { border-color: var(--sg-primary) !important; }
        .bg-primary { background-color: var(--sg-primary) !important; }
        @if($__density === 'compact')
            .card-body, .p-4 { padding: 0.75rem !important; }
            table td, table th { padding: 0.35rem 0.6rem !important; }
        @elseif($__density === 'comfortable')
            .card-body, .p-4 { padding: 1.5rem !important; }
            table td, table th { padding: 0.9rem 1rem !important; }
        @endif
    </style>
'''

    # اضافه قبل از </head>
    if '</head>' in content:
        content = content.replace('</head>', inject + '</head>', 1)
        with open(layout, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        print("  ✓ Layout patch شد (theme اعمال می‌شود)")
    else:
        print("  ⚠️ </head> پیدا نشد")

# ═══════════════════════════════════════════════════════════════
# ۹) Command — پاکسازی لاگ API
# ═══════════════════════════════════════════════════════════════

COMMAND_CLEANUP = r'''<?php

namespace App\Console\Commands;

use App\Models\ApiLog;
use Illuminate\Console\Command;

class CleanupApiLogs extends Command
{
    protected $signature = 'shopgun:cleanup-api-logs {--days=7}';
    protected $description = 'حذف لاگ‌های API قدیمی';

    public function handle(): int
    {
        $days = (int) $this->option('days');
        $count = ApiLog::where('created_at', '<', now()->subDays($days))->delete();
        $this->info("{$count} لاگ قدیمی‌تر از {$days} روز حذف شد.");
        return 0;
    }
}
'''

# ═══════════════════════════════════════════════════════════════
# اجرا
# ═══════════════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  ShopGun V2 — تنظیمات کامل                                    ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    # Backup
    print("📦 Backup...")
    for rel in [
        "app/Livewire/Settings/Index.php",
        "resources/views/livewire/settings/index.blade.php",
        "resources/views/components/layouts/app.blade.php",
        "app/Providers/AppServiceProvider.php",
        "app/Services/WooCommerceService.php",
    ]:
        backup(rel)

    # Migration
    print("\n📄 [1] Migration...")
    ts = datetime.now().strftime("%Y_%m_%d_%H%M%S")
    write(f"database/migrations/{ts}_create_app_settings_and_api_logs.php", MIG_SETTINGS)

    # Models
    print("\n📄 [2] Models...")
    write("app/Models/AppSetting.php", MODEL_APP_SETTING)
    write("app/Models/ApiLog.php", MODEL_API_LOG)

    # Service
    print("\n📄 [3] Service...")
    write("app/Services/ApiLogger.php", API_LOGGER_SERVICE)

    # Livewire
    print("\n📄 [4] Livewire Settings...")
    write("app/Livewire/Settings/Index.php", SETTINGS_INDEX_PHP)
    write("resources/views/livewire/settings/index.blade.php", SETTINGS_INDEX_BLADE)

    # Command
    print("\n📄 [5] Command...")
    write("app/Console/Commands/CleanupApiLogs.php", COMMAND_CLEANUP)

    # Patch AppServiceProvider
    print("\n🔧 [6] Patch AppServiceProvider...")
    patch_app_provider()

    # Patch Layout
    print("\n🔧 [7] Patch Layout...")
    patch_layout_theme()

    # Patch WooCommerceService
    print("\n🔧 [8] Patch WooCommerceService...")
    woo = PROJECT / "app/Services/WooCommerceService.php"
    if woo.exists():
        with open(woo, 'r', encoding='utf-8') as f:
            content = f.read()
        if 'loggedGet' not in content:
            idx = content.rstrip().rfind('}')
            if idx > 0:
                new_content = content[:idx] + WOO_LOGGER_PATCH + "\n}\n"
                with open(woo, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(new_content)
                print("  ✓ loggedGet اضافه شد")
        else:
            print("  ⏭ موجود")

    print("\n" + "═" * 64)
    print("✅ تمام!")
    print("═" * 64)
    print(f"""
📋 اجرا کن:

  cd {PROJECT}
  php artisan optimize:clear
  php artisan migrate
  php artisan view:clear
  php artisan route:clear

  ⚠️ سرور رو ببند و دوباره باز کن:
  php artisan serve

مرورگر: Ctrl+Shift+R

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 تب‌های تنظیمات (کامل):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ⚙️ عمومی        نام فروشگاه، تلفن، آدرس، کدپستی، واحد پول
  🎨 ظاهر          تم (روشن/تیره)، رنگ اصلی، تراکم، فونت
  🔌 کامرس         URL + Consumer Key + Consumer Secret
                    تست اتصال + سینک محصولات
  💎 شناسنامه     ابعاد، پیش‌فرض‌ها، مخفی‌سازی توضیحات
  🏷️ برچسب        عرض و ارتفاع
  📊 رصد API      همه‌ی درخواست‌ها + آمار + فیلتر + لاگ
  🏥 سلامت        PHP، Laravel، DB، فضای دیسک، تعداد رکوردها
  ℹ️ درباره        نسخه، سازنده، Change Log

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🧪 تست:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ۱. برو: /settings → تب کامرس
  ۲. URL سایت + Key + Secret رو وارد کن
  ۳. «💾 ذخیره» رو بزن
  ۴. «🔌 تست اتصال» رو بزن → نتیجه رو می‌بینی
  ۵. «📥 سینک کامل محصولات» → همه محصولات می‌آن
  ۶. تب «📊 رصد API» → همه‌ی درخواست‌ها ثبت شده
""")

if __name__ == "__main__":
    main()