# -*- coding: utf-8 -*-
"""ShopGun V2 - v8: Print + Popup + Public + Settings"""
from pathlib import Path
import re
import time
import subprocess
import os

ROOT = Path(r'D:\prodo\shopgun-v2.2')

def write(rel, content):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        p.rename(str(p) + '.bak-' + str(int(time.time())))
    p.write_text(content, encoding='utf-8')
    print("[OK] " + rel)

def patch(rel, old, new, label=''):
    p = ROOT / rel
    if not p.exists():
        print("[SKIP] " + rel + " not found")
        return False
    txt = p.read_text(encoding='utf-8')
    if new in txt:
        print("[SKIP] " + label + " already applied")
        return True
    if old not in txt:
        print("[WARN] " + label + " pattern not found")
        return False
    txt = txt.replace(old, new, 1)
    p.write_text(txt, encoding='utf-8')
    print("[OK] " + rel + " - " + label)
    return True

# ═══════════════════════════════════════════════════════════════
# 1. CERT RENDERER — چاپ بالا راست
# ═══════════════════════════════════════════════════════════════

patch(
    'app/Services/CertRenderer.php',
    "column-gap:' . $gap . 'cm;row-gap:2mm;justify-content:center;align-content:start;padding:0;width:100%}'",
    "column-gap:' . $gap . 'cm;row-gap:2mm;justify-content:start;align-content:start;padding:0;width:100%;direction:rtl}'",
    "print top-right align"
)

# ═══════════════════════════════════════════════════════════════
# 2. ROUTE — /Q/{code} و /certificates/print
# ═══════════════════════════════════════════════════════════════

routes_path = ROOT / 'routes' / 'web.php'
if routes_path.exists():
    txt = routes_path.read_text(encoding='utf-8')

    # روت public برای /Q/{code}
    if "cert.public" not in txt:
        marker = "Route::prefix('certificates')->name('certificates.')->group(function () {"
        new_route = """// عمومی: لینک کوتاه شناسنامه
    Route::get('/Q/{code}', function (string $code) {
        $cert = \\App\\Models\\Certificate::where('code', $code)->firstOrFail();
        return redirect()->route('certificates.show', $cert);
    })->name('cert.public');

    """
        if marker in txt:
            txt = txt.replace(marker, new_route + marker, 1)
            routes_path.write_text(txt, encoding='utf-8')
            print("[OK] route /Q/{code} اضافه شد")

    # روت print (اگر نبود)
    if "->name('certificates.print')" not in txt and "'certificates.print'" not in txt:
        marker = "Route::get('/designer/{certificate?}', CertificatesDesigner::class)->name('designer');"
        print_route = """Route::get('/print', function () {
            $ids = trim((string) request('ids', ''));
            $auto = request('auto', '0') === '1';
            $ids_arr = array_values(array_filter(array_map('intval', explode(',', $ids))));
            if (empty($ids_arr)) { abort(404); }

            $certs = \\App\\Models\\Certificate::whereIn('id', $ids_arr)->orderBy('id')->get()->all();
            if (empty($certs)) { abort(404); }

            $cols = count($certs) === 1 ? 1 : 3;
            $html = \\App\\Services\\CertRenderer::renderBatchHtml($certs, $cols);

            if ($auto) {
                $script = '<script>window.addEventListener("load",function(){setTimeout(function(){window.print()},700)})</script>';
                $html = str_replace('</body></html>', $script . '</body></html>', $html);
            }

            return response($html, 200)->header('Content-Type', 'text/html; charset=UTF-8');
        })->name('print');
        """
        if marker in txt:
            txt = txt.replace(marker, print_route + "        " + marker, 1)
            routes_path.write_text(txt, encoding='utf-8')
            print("[OK] route certificates.print اضافه شد")

# ═══════════════════════════════════════════════════════════════
# 3. VIEWMODAL — بازنویسی برای Livewire 3
# ═══════════════════════════════════════════════════════════════

VIEWMODAL_PHP = r'''<?php

namespace App\Livewire\Certificates;

use App\Models\Certificate;
use App\Services\CertRenderer;
use Livewire\Attributes\On;
use Livewire\Component;

class ViewModal extends Component
{
    public bool $show = false;
    public ?int $certId = null;
    public ?Certificate $certificate = null;
    public string $cardHtml = '';
    public string $batchHtml = '';

    #[On('open-cert-view')]
    public function open(int $certId): void
    {
        $this->certId = $certId;
        $this->certificate = Certificate::with(['customer', 'order'])->find($certId);

        if ($this->certificate) {
            try {
                $this->cardHtml = CertRenderer::renderCard($this->certificate);
                $this->batchHtml = CertRenderer::renderBatchHtml([$this->certificate], 1);
            } catch (\Throwable $e) {
                $this->cardHtml = '<div style="padding:20px;color:#dc2626">خطا در رندر: ' . htmlspecialchars($e->getMessage()) . '</div>';
            }
        }
        $this->show = true;
    }

    public function close(): void
    {
        $this->show = false;
        $this->certId = null;
        $this->certificate = null;
        $this->cardHtml = '';
        $this->batchHtml = '';
    }

    public function print(): void
    {
        if (!$this->certificate) return;
        $this->dispatch('open-print-window', url: route('certificates.print', [
            'ids' => $this->certificate->id,
            'auto' => 1,
        ]));
    }

    public function editDesign(): void
    {
        if (!$this->certificate) return;
        $url = route('certificates.designer', $this->certificate->id);
        $this->dispatch('open-new-tab', url: $url);
    }

    public function edit(): void
    {
        if (!$this->certificate) return;
        $id = $this->certificate->id;
        $this->close();
        $this->dispatch('open-cert-form', certId: $id);
    }

    public function delete(): void
    {
        if (!$this->certificate) return;
        $code = $this->certificate->code;
        $this->certificate->delete();
        $this->close();
        $this->dispatch('cert-saved');
        $this->dispatch('notify', type: 'success', message: "شناسنامه #{$code} حذف شد");
    }

    public function render()
    {
        return view('livewire.certificates.view-modal');
    }
}
'''

write('app/Livewire/Certificates/ViewModal.php', VIEWMODAL_PHP)

VIEWMODAL_VIEW = r'''<div>
@if($show && $certificate)
<div style="position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:96;display:flex;align-items:flex-start;justify-content:center;padding:10px;overflow-y:auto"
     @keydown.escape.window="$wire.close()">

    <div style="background:#fff;width:100%;max-width:820px;margin:10px auto;border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,.4);overflow:hidden;direction:rtl;font-family:Vazirmatn,Tahoma,sans-serif">

        <div style="background:linear-gradient(135deg,#1a5276,#0d3b5e);color:#fff;padding:14px 18px;display:flex;align-items:center;justify-content:space-between">
            <div>
                <h2 style="margin:0;font-size:16px;font-weight:700">شناسنامه #{{ $certificate->code }}</h2>
                <div style="font-size:11px;opacity:.8;font-family:monospace;margin-top:2px" dir="ltr">{{ $certificate->serial }}</div>
            </div>
            <button type="button" wire:click="close" style="width:32px;height:32px;border-radius:50%;background:rgba(255,255,255,.2);color:#fff;border:none;cursor:pointer;font-size:15px">X</button>
        </div>

        <div style="padding:16px;max-height:calc(100vh - 180px);overflow-y:auto">

            {{-- پیش‌نمایش کارت --}}
            <div style="background:repeating-conic-gradient(#f0f0f0 0% 25%, #fff 0% 50%) 50% / 20px 20px;border-radius:12px;padding:16px;display:flex;justify-content:center;overflow:auto;margin-bottom:16px">
                <div style="transform-origin:top center;max-width:100%">
                    {!! $cardHtml !!}
                </div>
            </div>

            {{-- اطلاعات --}}
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px">
                <div style="padding:10px;background:#f8fafc;border-radius:8px">
                    <div style="font-size:10px;color:#94a3b8;margin-bottom:2px">💎 سنگ</div>
                    <div style="font-size:13px;font-weight:700">{{ $certificate->stone_name }}</div>
                </div>
                <div style="padding:10px;background:#f8fafc;border-radius:8px">
                    <div style="font-size:10px;color:#94a3b8;margin-bottom:2px">⚙️ فلز</div>
                    <div style="font-size:13px">{{ $certificate->metal }} ({{ $certificate->metal_carat }})</div>
                </div>
                <div style="padding:10px;background:#f8fafc;border-radius:8px">
                    <div style="font-size:10px;color:#94a3b8;margin-bottom:2px">📐 ابعاد</div>
                    <div style="font-size:13px">{{ $certificate->length }}×{{ $certificate->width }} mm</div>
                </div>
                <div style="padding:10px;background:#f8fafc;border-radius:8px">
                    <div style="font-size:10px;color:#94a3b8;margin-bottom:2px">⚖️ وزن</div>
                    <div style="font-size:13px">{{ $certificate->weight }} gr</div>
                </div>
                <div style="padding:10px;background:#f8fafc;border-radius:8px">
                    <div style="font-size:10px;color:#94a3b8;margin-bottom:2px">👤 مشتری</div>
                    <div style="font-size:13px">{{ $certificate->customer?->name ?? '—' }}</div>
                </div>
                <div style="padding:10px;background:#f8fafc;border-radius:8px">
                    <div style="font-size:10px;color:#94a3b8;margin-bottom:2px">📅 تاریخ صدور</div>
                    <div style="font-size:13px">{{ \App\Support\PersianDate::format($certificate->issued_at ?? $certificate->created_at, 'Y/m/d') }}</div>
                </div>
            </div>

            {{-- لینک عمومی --}}
            <div style="padding:10px 12px;background:#eff6ff;border-radius:8px;font-size:12px;margin-bottom:14px;display:flex;align-items:center;gap:8px;flex-wrap:wrap">
                <span style="color:#1e40af;font-weight:700">🔗 لینک عمومی:</span>
                <code style="font-family:monospace;font-size:11px;background:#fff;padding:4px 8px;border-radius:6px;direction:ltr">{{ $certificate->public_url }}</code>
                <button type="button"
                        onclick="navigator.clipboard.writeText('{{ $certificate->public_url }}');this.textContent='✓ کپی شد';setTimeout(()=>this.textContent='📋 کپی',1500)"
                        style="background:#1e40af;color:#fff;border:none;padding:4px 10px;border-radius:6px;font-size:11px;cursor:pointer;font-weight:700">📋 کپی</button>
            </div>
        </div>

        <div style="padding:12px 18px;background:#f8fafc;border-top:1px solid #e2e8f0;display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap">
            <button type="button" wire:click="delete"
                    wire:confirm="شناسنامه حذف شود؟"
                    style="padding:9px 16px;background:#fee2e2;color:#dc2626;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">
                🗑️ حذف
            </button>

            <div style="display:flex;gap:6px;flex-wrap:wrap">
                <a href="{{ route('certificates.show', $certificate) }}" wire:navigate
                   style="padding:9px 16px;background:#fff;color:#475569;border:1.5px solid #cbd5e1;border-radius:8px;font-weight:700;text-decoration:none;font-size:13px">
                    صفحه کامل
                </a>
                <a href="{{ route('certificates.designer', $certificate->id) }}" wire:navigate
                   style="padding:9px 16px;background:#7c3aed;color:#fff;border:none;border-radius:8px;font-weight:700;text-decoration:none;font-size:13px">
                    🎨 ویرایشگر
                </a>
                <button type="button" onclick="window.open('{{ route('certificates.print', ['ids' => $certificate->id, 'auto' => 1]) }}', '_blank')"
                        style="padding:9px 16px;background:#1a5276;color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">
                    🖨️ چاپ
                </button>
                <button type="button" wire:click="edit"
                        style="padding:9px 16px;background:#16a34a;color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">
                    ✏️ ویرایش
                </button>
            </div>
        </div>
    </div>
</div>
@endif
</div>
'''

write('resources/views/livewire/certificates/view-modal.blade.php', VIEWMODAL_VIEW)

# ═══════════════════════════════════════════════════════════════
# 4. CERT INDEX — دکمه نمایش به جای لینک
# ═══════════════════════════════════════════════════════════════

cert_index = ROOT / 'resources' / 'views' / 'livewire' / 'certificates' / 'index.blade.php'
if cert_index.exists():
    txt = cert_index.read_text(encoding='utf-8')

    # عوض کردن لینک view به دکمه dispatch
    txt = txt.replace(
        '<a href="{{ route(\'certificates.show\', $c) }}" wire:navigate class="sg-action-btn view">👁️</a>',
        '<button type="button" onclick="Livewire.dispatch(\'open-cert-view\', { certId: {{ $c->id }} })" class="sg-action-btn view">👁️</button>'
    )

    cert_index.write_text(txt, encoding='utf-8')
    print("[OK] certificates/index - دکمه view به dispatch عوض شد")

# ═══════════════════════════════════════════════════════════════
# 5. LAYOUT — اضافه کردن ViewModal
# ═══════════════════════════════════════════════════════════════

layout = ROOT / 'resources' / 'views' / 'components' / 'layouts' / 'app.blade.php'
if layout.exists():
    txt = layout.read_text(encoding='utf-8')

    if '<livewire:certificates.view-modal' not in txt:
        marker = '<livewire:certificates.create'
        if marker in txt:
            txt = txt.replace(
                marker,
                '<livewire:certificates.view-modal :key="\'cvm\'" />\n    ' + marker,
                1
            )
            layout.write_text(txt, encoding='utf-8')
            print("[OK] layout - cert ViewModal اضافه شد")
        else:
            # اگه create نبود، قبل از orders بذار
            marker2 = '<livewire:orders.form-modal'
            if marker2 in txt:
                txt = txt.replace(
                    marker2,
                    '<livewire:certificates.view-modal :key="\'cvm\'" />\n    ' + marker2,
                    1
                )
                layout.write_text(txt, encoding='utf-8')
                print("[OK] layout - cert ViewModal اضافه شد")

# ═══════════════════════════════════════════════════════════════
# 6. SETTINGS — Cert tab with sliders + side preview
# ═══════════════════════════════════════════════════════════════

SETTINGS_PHP = r'''<?php

namespace App\Livewire\Settings;

use App\Models\AppSetting;
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

    // Label
    public int $label_width = 100;
    public int $label_height = 50;

    // Assets
    public string $bg_image = '';

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

        $this->label_width = (int) AppSetting::get('label_width', 100);
        $this->label_height = (int) AppSetting::get('label_height', 50);

        $this->bg_image = (string) AppSetting::get('bg_image', '');
    }

    public function setTab(string $tab): void
    {
        $this->tab = $tab;
    }

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
        $this->dispatch('notify', type: 'success', message: 'ذخیره شد');
    }

    public function saveCommerce(): void
    {
        AppSetting::putMany([
            'commerce_url' => $this->commerce_url,
            'commerce_key' => $this->commerce_key,
            'commerce_secret' => $this->commerce_secret,
        ], 'commerce');
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
        ], 'certificate');

        \Illuminate\Support\Facades\Cache::forget('app_settings_all');
        $this->dispatch('notify', type: 'success', message: 'تنظیمات ذخیره شد');
    }

    public function setCertPreset(float $w, float $h): void
    {
        $this->cert_width = $w;
        $this->cert_height = $h;
    }

    public function getPreviewCardProperty(): string
    {
        try {
            $cert = \App\Models\Certificate::latest('id')->first();
            if (!$cert) {
                $cert = new \App\Models\Certificate([
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

            \App\Support\CertConfig::$overrideSizes = [
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

            \App\Support\CertConfig::$overrideHideDesc = $this->cert_hide_desc;

            return \App\Services\CertRenderer::renderCard($cert);
        } catch (\Throwable $e) {
            return '<div style="padding:20px;color:#dc2626;font-size:12px">خطا: ' . htmlspecialchars($e->getMessage()) . '</div>';
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

write('app/Livewire/Settings/Index.php', SETTINGS_PHP)

# CertConfig override برای hide_desc
patch(
    'app/Support/CertConfig.php',
    'public static ?array $overrideSizes = null;',
    "public static ?array $overrideSizes = null;\n    public static ?bool \$overrideHideDesc = null;",
    "overrideHideDesc prop"
)

patch(
    'app/Support/CertConfig.php',
    "public static function hideDesc(): bool\n    {\n        try {",
    "public static function hideDesc(): bool\n    {\n        if (self::\$overrideHideDesc !== null) return self::\$overrideHideDesc;\n        try {",
    "hideDesc override"
)

# Settings blade — بازنویسی کامل
SETTINGS_VIEW = r'''<div style="padding:0 0 18px" dir="rtl">

    <div style="padding:0 14px 14px">
        <h1 style="font-size:20px;font-weight:700">⚙️ تنظیمات</h1>
    </div>

    {{-- تب‌ها --}}
    <div class="sg-settings-tabs">
        @foreach([
            'general'     => ['⚙️', 'عمومی', false],
            'appearance'  => ['🎨', 'ظاهر', false],
            'commerce'    => ['🔌', 'اتصالات', false],
            'certificate' => ['💎', 'شناسنامه', false],
            'label'       => ['🏷️', 'برچسب', false],
            'assets'      => ['🖼️', 'تصاویر', false],
            'health'      => ['🩺', 'سلامت', true],
        ] as $key => $meta)
            <button wire:click="setTab('{{ $key }}')"
                    class="sg-settings-tab {{ $tab === $key ? 'active' : '' }}">
                <span>{{ $meta[0] }}</span>
                <span>{{ $meta[1] }}</span>
                @if($meta[2])<span class="badge-new">🆕</span>@endif
            </button>
        @endforeach
    </div>

    <div style="padding:0 14px">

        {{-- ═══════════ عمومی ═══════════ --}}
        @if($tab === 'general')
            <div class="sg-settings-card">
                <h3>اطلاعات فروشگاه</h3>
                <div class="form-grid">
                    <div class="field col-6">
                        <label>🏪 نام فروشگاه</label>
                        <input type="text" wire:model="shop_name">
                    </div>
                    <div class="field col-6">
                        <label>📱 تلفن</label>
                        <input type="text" wire:model="shop_phone" dir="ltr">
                    </div>
                    <div class="field col-12">
                        <label>📍 آدرس</label>
                        <textarea wire:model="shop_address" rows="2"></textarea>
                    </div>
                    <div class="field col-4">
                        <label>📮 کدپستی</label>
                        <input type="text" wire:model="shop_postal" dir="ltr">
                    </div>
                    <div class="field col-4">
                        <label>📧 ایمیل</label>
                        <input type="email" wire:model="shop_email" dir="ltr">
                    </div>
                    <div class="field col-4">
                        <label>💵 واحد پول</label>
                        <input type="text" wire:model="currency">
                    </div>
                </div>
                <div style="display:flex;justify-content:flex-end;padding-top:14px;border-top:1px solid var(--border)">
                    <button wire:click="saveGeneral" class="btn btn-success">💾 ذخیره</button>
                </div>
            </div>
        @endif

        {{-- ═══════════ ظاهر ═══════════ --}}
        @if($tab === 'appearance')
            <div class="sg-settings-card">
                <h3>ظاهر برنامه</h3>
                <div class="form-grid">
                    <div class="field col-6">
                        <label>🌓 تم</label>
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px">
                            @foreach(['light'=>'☀️ روشن','dark'=>'🌙 تیره'] as $k=>$v)
                                <button type="button" wire:click="$set('theme','{{ $k }}')"
                                        class="btn {{ $theme===$k ? 'btn-primary' : 'btn-outline' }} btn-sm">{{ $v }}</button>
                            @endforeach
                        </div>
                    </div>
                    <div class="field col-6">
                        <label>📐 تراکم</label>
                        <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px">
                            @foreach(['compact'=>'فشرده','normal'=>'معمولی','comfortable'=>'راحت'] as $k=>$v)
                                <button type="button" wire:click="$set('density','{{ $k }}')"
                                        class="btn {{ $density===$k ? 'btn-primary' : 'btn-outline' }} btn-xs">{{ $v }}</button>
                            @endforeach
                        </div>
                    </div>
                    <div class="field col-6">
                        <label>🎨 رنگ اصلی</label>
                        <input type="color" wire:model.live="primary_color" style="height:42px;padding:4px;cursor:pointer">
                    </div>
                    <div class="field col-6">
                        <label>✨ رنگ تاکیدی</label>
                        <input type="color" wire:model.live="accent_color" style="height:42px;padding:4px;cursor:pointer">
                    </div>
                </div>
                <div style="display:flex;justify-content:flex-end;padding-top:14px;border-top:1px solid var(--border)">
                    <button wire:click="saveAppearance" class="btn btn-success">💾 ذخیره</button>
                </div>
            </div>
        @endif

        {{-- ═══════════ کامرس ═══════════ --}}
        @if($tab === 'commerce')
            <div class="sg-settings-card">
                <h3>🔌 اتصال به WooCommerce</h3>
                <div class="form-grid">
                    <div class="field col-12">
                        <label>🌐 آدرس سایت</label>
                        <input type="text" wire:model="commerce_url" dir="ltr" placeholder="https://yoursite.com">
                    </div>
                    <div class="field col-6">
                        <label>🔑 Consumer Key</label>
                        <input type="text" wire:model="commerce_key" dir="ltr">
                    </div>
                    <div class="field col-6">
                        <label>🔐 Consumer Secret</label>
                        <input type="password" wire:model="commerce_secret" dir="ltr">
                    </div>
                </div>
                @if(!empty($commerce_test_result))
                    <div style="padding:10px;border-radius:8px;margin-top:10px;background:{{ $commerce_test_result['ok'] ? '#d1fae5' : '#fee2e2' }};color:{{ $commerce_test_result['ok'] ? '#065f46' : '#991b1b' }};font-weight:700;font-size:13px">
                        {{ $commerce_test_result['ok'] ? '✓' : '✗' }} {{ $commerce_test_result['message'] }}
                    </div>
                @endif
                <div style="display:flex;gap:6px;padding-top:14px;border-top:1px solid var(--border);margin-top:14px;flex-wrap:wrap">
                    <button wire:click="saveCommerce" class="btn btn-primary">💾 ذخیره</button>
                    <button wire:click="testCommerce" class="btn btn-secondary">🔌 تست اتصال</button>
                </div>
            </div>
        @endif

        {{-- ═══════════ شناسنامه — اسلایدر + پیش‌نمایش ═══════════ --}}
        @if($tab === 'certificate')
            <div style="display:grid;grid-template-columns:1fr;gap:14px">

                {{-- پیش‌نمایش زنده --}}
                <div class="sg-settings-card" style="position:sticky;top:0">
                    <h3>👁️ پیش‌نمایش زنده</h3>
                    <div style="background:repeating-conic-gradient(#f0f0f0 0% 25%, #fff 0% 50%) 50% / 20px 20px;border-radius:12px;padding:20px;display:flex;justify-content:center;overflow:auto;min-height:350px;align-items:center">
                        {!! $this->preview_card !!}
                    </div>
                    <div style="display:flex;justify-content:space-between;gap:8px;padding-top:14px;border-top:1px solid var(--border);margin-top:14px;flex-wrap:wrap">
                        <span style="font-size:11px;color:#64748b;align-self:center">
                            📐 {{ $cert_width }}×{{ $cert_height }} cm
                        </span>
                        <button wire:click="saveCertificate" class="btn btn-success">💾 ذخیره تنظیمات</button>
                    </div>
                </div>

                {{-- اسلایدرها --}}
                <div class="sg-settings-card">
                    <h3>📏 ابعاد کارت</h3>
                    <div class="form-grid">
                        <div class="field col-6">
                            <label>📐 عرض (cm)</label>
                            <input type="number" step="0.1" min="3" max="15" wire:model.live.debounce.300ms="cert_width" dir="ltr">
                        </div>
                        <div class="field col-6">
                            <label>📐 ارتفاع (cm)</label>
                            <input type="number" step="0.1" min="3" max="15" wire:model.live.debounce.300ms="cert_height" dir="ltr">
                        </div>
                    </div>
                    <div style="display:flex;gap:6px;flex-wrap:wrap">
                        <button type="button" wire:click="setCertPreset(6.5,6.5)" class="btn btn-outline btn-sm">۶.۵×۶.۵</button>
                        <button type="button" wire:click="setCertPreset(7,7)" class="btn btn-outline btn-sm">۷×۷</button>
                        <button type="button" wire:click="setCertPreset(8,6)" class="btn btn-outline btn-sm">۸×۶</button>
                        <button type="button" wire:click="setCertPreset(10,7)" class="btn btn-outline btn-sm">۱۰×۷</button>
                    </div>

                    <h3 style="margin-top:20px">🖼️ ابعاد تصویر محصول</h3>
                    <div class="form-grid">
                        <div class="field col-6">
                            <label>عرض تصویر: <span dir="ltr" style="font-family:monospace">{{ $cert_img_w }}px</span></label>
                            <input type="range" min="40" max="300" step="5" wire:model.live.debounce.200ms="cert_img_w" style="width:100%;accent-color:var(--gold)">
                        </div>
                        <div class="field col-6">
                            <label>ارتفاع تصویر: <span dir="ltr" style="font-family:monospace">{{ $cert_img_h }}px</span></label>
                            <input type="range" min="40" max="300" step="5" wire:model.live.debounce.200ms="cert_img_h" style="width:100%;accent-color:var(--gold)">
                        </div>
                    </div>

                    <h3 style="margin-top:20px">📱 ابعاد QR</h3>
                    <div class="field col-12">
                        <label>اندازه QR: <span dir="ltr" style="font-family:monospace">{{ $cert_qr_size }}px</span></label>
                        <input type="range" min="20" max="120" step="2" wire:model.live.debounce.200ms="cert_qr_size" style="width:100%;accent-color:var(--gold)">
                    </div>

                    <h3 style="margin-top:20px">🏷️ لوگو</h3>
                    <div class="form-grid">
                        <div class="field col-6">
                            <label>عرض لوگو: <span dir="ltr" style="font-family:monospace">{{ $cert_logo_w }}px</span></label>
                            <input type="range" min="10" max="100" step="2" wire:model.live.debounce.200ms="cert_logo_w" style="width:100%;accent-color:var(--gold)">
                        </div>
                        <div class="field col-6">
                            <label>ارتفاع لوگو: <span dir="ltr" style="font-family:monospace">{{ $cert_logo_h }}px</span></label>
                            <input type="range" min="10" max="100" step="2" wire:model.live.debounce.200ms="cert_logo_h" style="width:100%;accent-color:var(--gold)">
                        </div>
                    </div>

                    <h3 style="margin-top:20px">🔤 فونت‌ها</h3>
                    <div class="field col-12">
                        <label>فونت عنوان: <span dir="ltr" style="font-family:monospace">{{ $cert_title_font }}px</span></label>
                        <input type="range" min="8" max="40" wire:model.live.debounce.200ms="cert_title_font" style="width:100%;accent-color:var(--gold)">
                    </div>
                    <div class="field col-12" style="margin-top:8px">
                        <label>فونت کد: <span dir="ltr" style="font-family:monospace">{{ $cert_code_font }}px</span></label>
                        <input type="range" min="6" max="30" wire:model.live.debounce.200ms="cert_code_font" style="width:100%;accent-color:var(--gold)">
                    </div>
                    <div class="field col-12" style="margin-top:8px">
                        <label>فونت توضیحات: <span dir="ltr" style="font-family:monospace">{{ $cert_desc_font }}px</span></label>
                        <input type="range" min="5" max="20" wire:model.live.debounce.200ms="cert_desc_font" style="width:100%;accent-color:var(--gold)">
                    </div>

                    <label style="display:flex;align-items:center;gap:8px;padding:10px;background:rgba(0,0,0,.03);border-radius:8px;cursor:pointer;margin-top:14px">
                        <input type="checkbox" wire:model.live="cert_hide_desc" style="width:18px;height:18px;accent-color:var(--gold)">
                        <span style="font-size:13px;font-weight:700">مخفی کردن بخش توضیحات</span>
                    </label>
                </div>
            </div>
        @endif

        {{-- ═══════════ برچسب ═══════════ --}}
        @if($tab === 'label')
            <div class="sg-settings-card">
                <h3>📐 اندازه برچسب پستی</h3>
                <div class="form-grid">
                    <div class="field col-6">
                        <label>📐 عرض (mm)</label>
                        <input type="number" wire:model="label_width" dir="ltr">
                    </div>
                    <div class="field col-6">
                        <label>📐 ارتفاع (mm)</label>
                        <input type="number" wire:model="label_height" dir="ltr">
                    </div>
                </div>
            </div>
        @endif

        {{-- ═══════════ تصاویر ═══════════ --}}
        @if($tab === 'assets')
            <div class="sg-settings-card">
                <h3>🖼️ پس‌زمینه شناسنامه</h3>
                @if($bg_image)
                    <div style="margin-bottom:12px;display:flex;gap:8px;align-items:center">
                        <img src="{{ $bg_image }}" style="max-width:120px;border-radius:10px;border:2px solid var(--gold)">
                    </div>
                @endif
                <div class="field col-12">
                    <label>آپلود تصویر جدید</label>
                    <input type="file" wire:model="bg_image" accept="image/*" class="form-control">
                </div>
            </div>
        @endif

        {{-- ═══════════ سلامت ═══════════ --}}
        @if($tab === 'health')
            <livewire:settings.health />
        @endif
    </div>
</div>
'''

write('resources/views/livewire/settings/index.blade.php', SETTINGS_VIEW)

# ═══════════════════════════════════════════════════════════════
# 7. DESIGNER — دکمه‌های واضح‌تر برای fabric
# ═══════════════════════════════════════════════════════════════

# تنظیمات رنگ‌های انتخاب در CertRenderer
patch(
    'public/js/cert-designer.js',
    'canvas = new fabric.Canvas("cert-fabric-canvas", {',
    '''fabric.Object.prototype.set({
            transparentCorners: false,
            cornerColor: '#c9a84c',
            cornerStrokeColor: '#1a5276',
            borderColor: '#c9a84c',
            cornerSize: 12,
            cornerStyle: 'circle',
            padding: 6,
        });

        canvas = new fabric.Canvas("cert-fabric-canvas", {''',
    "fabric controls styling"
)

print()
print("=" * 60)
print("DONE")
print("=" * 60)
print()
print("Run:")
print("  php artisan view:clear")
print("  php artisan optimize:clear")
print("  php artisan serve")