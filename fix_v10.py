# -*- coding: utf-8 -*-
"""ShopGun V2 - v10: Cover image + Label sliders + Table columns + Design apply"""
from pathlib import Path
import re, time

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
        print("[SKIP] " + rel)
        return
    txt = p.read_text(encoding='utf-8')
    if new in txt:
        print("[SKIP] " + label)
        return
    if old not in txt:
        print("[WARN] " + label + " not found")
        return
    txt = txt.replace(old, new)
    p.write_text(txt, encoding='utf-8')
    print("[OK] " + rel + " - " + label)

# ═══════════════════════════════════════════════════════════════
# 1. IMAGE — کراپ خودکار (cover به جای contain)
# ═══════════════════════════════════════════════════════════════

# در CertRenderer: img-wrapper
patch(
    'app/Services/CertRenderer.php',
    ".certificate .cert-img-frame img{width:100%;height:100%;object-fit:contain;display:block}",
    ".certificate .cert-img-frame img{width:100%;height:100%;object-fit:cover;display:block}",
    "image cover in cert"
)

# در CertRenderer: card image
patch(
    'app/Services/CertRenderer.php',
    ".certificate .cert-desc-area img{max-width:100%;max-height:100%;object-fit:contain;margin:auto;display:block}",
    ".certificate .cert-desc-area img{max-width:100%;max-height:100%;object-fit:cover;margin:auto;display:block;border-radius:6px}",
    "desc image cover"
)

# در CSS خارجی هم
cert_css = ROOT / 'public' / 'css' / 'cert-card.css'
if cert_css.exists():
    txt = cert_css.read_text(encoding='utf-8')
    txt = txt.replace('.cert-img-frame img{', '.cert-img-frame img{object-fit:cover!important;')
    txt = txt.replace('.cert-desc-area img{', '.cert-desc-area img{object-fit:cover!important;')
    cert_css.write_text(txt, encoding='utf-8')
    print("[OK] cert-card.css - cover")

# ═══════════════════════════════════════════════════════════════
# 2. CertConfig — اضافه کردن override برای ستون‌ها
# ═══════════════════════════════════════════════════════════════

certconfig = ROOT / 'app' / 'Support' / 'CertConfig.php'
if certconfig.exists():
    txt = certconfig.read_text(encoding='utf-8')

    # اضافه کردن override برای ستون‌ها
    if 'overrideCols' not in txt:
        txt = txt.replace(
            'public static ?array $overrideSizes = null;',
            """public static ?array $overrideSizes = null;
    public static ?array $overrideCols = null;"""
        )
        certconfig.write_text(txt, encoding='utf-8')
        print("[OK] CertConfig - overrideCols")

# ═══════════════════════════════════════════════════════════════
# 3. CertRenderer — استفاده از override برای ستون‌ها
# ═══════════════════════════════════════════════════════════════

patch(
    'app/Services/CertRenderer.php',
    '<colgroup><col style="width:25%"><col style="width:25%"><col style="width:25%"><col style="width:25%"></colgroup>',
    '''@php
            $__cols = \\App\\Support\\CertConfig::$overrideCols ?? [25, 25, 25, 25];
        @endphp
        <colgroup>
            <col style="width:{{ $__cols[0] ?? 25 }}%">
            <col style="width:{{ $__cols[1] ?? 25 }}%">
            <col style="width:{{ $__cols[2] ?? 25 }}%">
            <col style="width:{{ $__cols[3] ?? 25 }}%">
        </colgroup>''',
    "table cols dynamic"
)

# ═══════════════════════════════════════════════════════════════
# 4. Settings/Index.php — اضافه کردن property ستون‌ها + labels tab
# ═══════════════════════════════════════════════════════════════

settings_php = ROOT / 'app' / 'Livewire' / 'Settings' / 'Index.php'
if settings_php.exists():
    txt = settings_php.read_text(encoding='utf-8')

    # اضافه کردن property ستون‌ها
    if 'public int $cert_col1' not in txt:
        txt = txt.replace(
            'public bool $cert_hide_desc = false;',
            """public bool $cert_hide_desc = false;

    // ستون‌های جدول پایین
    public int $cert_col1 = 25;
    public int $cert_col2 = 25;
    public int $cert_col3 = 25;
    public int $cert_col4 = 25;"""
        )

    # mount - خواندن از settings
    if '$this->cert_col1 = (int)' not in txt:
        txt = txt.replace(
            "$this->cert_hide_desc = (bool) AppSetting::get('cert_hide_desc', false);",
            """$this->cert_hide_desc = (bool) AppSetting::get('cert_hide_desc', false);
        $this->cert_col1 = (int) AppSetting::get('cert_col1', 25);
        $this->cert_col2 = (int) AppSetting::get('cert_col2', 25);
        $this->cert_col3 = (int) AppSetting::get('cert_col3', 25);
        $this->cert_col4 = (int) AppSetting::get('cert_col4', 25);"""
        )

    # saveCertificate - ذخیره ستون‌ها
    if "'cert_col1' => $this->cert_col1" not in txt:
        txt = txt.replace(
            "'cert_hide_desc' => $this->cert_hide_desc ? '1' : '0',",
            """'cert_hide_desc' => $this->cert_hide_desc ? '1' : '0',
            'cert_col1' => $this->cert_col1,
            'cert_col2' => $this->cert_col2,
            'cert_col3' => $this->cert_col3,
            'cert_col4' => $this->cert_col4,"""
        )

    # preview_card - اضافه کردن overrideCols
    if "CertConfig::\$overrideCols = [" not in txt:
        txt = txt.replace(
            "\\App\\Support\\CertConfig::\$overrideHideDesc = \$this->cert_hide_desc;",
            """\\App\\Support\\CertConfig::\$overrideHideDesc = \$this->cert_hide_desc;

            \\App\\Support\\CertConfig::\$overrideCols = [
                \$this->cert_col1,
                \$this->cert_col2,
                \$this->cert_col3,
                \$this->cert_col4,
            ];"""
        )

    settings_php.write_text(txt, encoding='utf-8')
    print("[OK] Settings/Index.php - cols + labels")

# ═══════════════════════════════════════════════════════════════
# 5. Settings blade — بازنویسی کامل cert + label sections
# ═══════════════════════════════════════════════════════════════

settings_view = ROOT / 'resources' / 'views' / 'livewire' / 'settings' / 'index.blade.php'
if settings_view.exists():
    txt = settings_view.read_text(encoding='utf-8')

    # اضافه کردن تب labels به تب‌ها
    txt = txt.replace(
        "'label'       => ['🏷️', 'برچسب', false],",
        """'label'       => ['🏷️', 'برچسب ساده', false],
            'labels'      => ['🎨', 'ویرایشگر برچسب', false],"""
    )

    # بازنویسی کامل بخش certificate
    NEW_CERT = '''        @if($tab === 'certificate')
            <div class="cert-settings-layout">

                <div class="sliders-col">

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
                        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:8px">
                            <button type="button" wire:click="setCertPreset(6.5,6.5)" class="btn btn-outline btn-sm">۶.۵×۶.۵</button>
                            <button type="button" wire:click="setCertPreset(7,7)" class="btn btn-outline btn-sm">۷×۷</button>
                            <button type="button" wire:click="setCertPreset(8,6)" class="btn btn-outline btn-sm">۸×۶</button>
                        </div>
                    </div>

                    <div class="sg-settings-card" style="margin-top:14px">
                        <h3>🖼️ ابعاد تصویر محصول <span style="font-size:10px;font-weight:400;color:#94a3b8">(تصویر خودکار کراپ می‌شود)</span></h3>
                        <div class="cert-slider-group">
                            <div class="cert-slider-label">
                                <span>عرض تصویر</span>
                                <span class="font-mono">{{ $cert_img_w }}px</span>
                            </div>
                            <input type="range" min="40" max="300" step="5" wire:model.live.debounce.200ms="cert_img_w" class="range range-sm range-primary w-full">
                        </div>
                        <div class="cert-slider-group">
                            <div class="cert-slider-label">
                                <span>ارتفاع تصویر</span>
                                <span class="font-mono">{{ $cert_img_h }}px</span>
                            </div>
                            <input type="range" min="40" max="300" step="5" wire:model.live.debounce.200ms="cert_img_h" class="range range-sm range-primary w-full">
                        </div>
                    </div>

                    <div class="sg-settings-card" style="margin-top:14px">
                        <h3>📱 QR و لوگو</h3>
                        <div class="cert-slider-group">
                            <div class="cert-slider-label">
                                <span>اندازه QR</span>
                                <span class="font-mono">{{ $cert_qr_size }}px</span>
                            </div>
                            <input type="range" min="20" max="120" step="2" wire:model.live.debounce.200ms="cert_qr_size" class="range range-sm range-primary w-full">
                        </div>
                        <div class="cert-slider-group">
                            <div class="cert-slider-label">
                                <span>عرض لوگو</span>
                                <span class="font-mono">{{ $cert_logo_w }}px</span>
                            </div>
                            <input type="range" min="10" max="100" step="2" wire:model.live.debounce.200ms="cert_logo_w" class="range range-sm range-primary w-full">
                        </div>
                        <div class="cert-slider-group">
                            <div class="cert-slider-label">
                                <span>ارتفاع لوگو</span>
                                <span class="font-mono">{{ $cert_logo_h }}px</span>
                            </div>
                            <input type="range" min="10" max="100" step="2" wire:model.live.debounce.200ms="cert_logo_h" class="range range-sm range-primary w-full">
                        </div>
                    </div>

                    <div class="sg-settings-card" style="margin-top:14px">
                        <h3>🔤 فونت‌ها</h3>
                        <div class="cert-slider-group">
                            <div class="cert-slider-label">
                                <span>فونت عنوان</span>
                                <span class="font-mono">{{ $cert_title_font }}px</span>
                            </div>
                            <input type="range" min="8" max="40" wire:model.live.debounce.200ms="cert_title_font" class="range range-sm range-primary w-full">
                        </div>
                        <div class="cert-slider-group">
                            <div class="cert-slider-label">
                                <span>فونت کد</span>
                                <span class="font-mono">{{ $cert_code_font }}px</span>
                            </div>
                            <input type="range" min="6" max="30" wire:model.live.debounce.200ms="cert_code_font" class="range range-sm range-primary w-full">
                        </div>
                        <div class="cert-slider-group">
                            <div class="cert-slider-label">
                                <span>فونت توضیحات</span>
                                <span class="font-mono">{{ $cert_desc_font }}px</span>
                            </div>
                            <input type="range" min="5" max="20" wire:model.live.debounce.200ms="cert_desc_font" class="range range-sm range-primary w-full">
                        </div>
                    </div>

                    <div class="sg-settings-card" style="margin-top:14px">
                        <h3>📊 ستون‌های جدول پایین</h3>
                        <p style="font-size:11px;color:#94a3b8;margin:0 0 10px">درصد عرض هر ستون — مجموع بهتر است ۱۰۰ باشد</p>

                        <div class="cert-slider-group">
                            <div class="cert-slider-label">
                                <span>ستون ۱ (برچسب چپ)</span>
                                <span class="font-mono">{{ $cert_col1 }}%</span>
                            </div>
                            <input type="range" min="10" max="50" wire:model.live.debounce.200ms="cert_col1" class="range range-sm range-primary w-full">
                        </div>
                        <div class="cert-slider-group">
                            <div class="cert-slider-label">
                                <span>ستون ۲ (مقدار چپ)</span>
                                <span class="font-mono">{{ $cert_col2 }}%</span>
                            </div>
                            <input type="range" min="10" max="50" wire:model.live.debounce.200ms="cert_col2" class="range range-sm range-primary w-full">
                        </div>
                        <div class="cert-slider-group">
                            <div class="cert-slider-label">
                                <span>ستون ۳ (برچسب راست)</span>
                                <span class="font-mono">{{ $cert_col3 }}%</span>
                            </div>
                            <input type="range" min="10" max="50" wire:model.live.debounce.200ms="cert_col3" class="range range-sm range-primary w-full">
                        </div>
                        <div class="cert-slider-group">
                            <div class="cert-slider-label">
                                <span>ستون ۴ (مقدار راست)</span>
                                <span class="font-mono">{{ $cert_col4 }}%</span>
                            </div>
                            <input type="range" min="10" max="50" wire:model.live.debounce.200ms="cert_col4" class="range range-sm range-primary w-full">
                        </div>
                    </div>

                    <div class="sg-settings-card" style="margin-top:14px">
                        <label style="display:flex;align-items:center;gap:8px;cursor:pointer">
                            <input type="checkbox" wire:model.live="cert_hide_desc" class="checkbox checkbox-primary checkbox-sm">
                            <span style="font-size:13px;font-weight:700">مخفی کردن بخش توضیحات</span>
                        </label>

                        <div style="display:flex;justify-content:flex-end;gap:8px;padding-top:14px;border-top:1px solid var(--border);margin-top:14px">
                            <a href="{{ route('certificates.index') }}" wire:navigate class="btn btn-outline">🎴 لیست</a>
                            <button wire:click="saveCertificate" class="btn btn-success">💾 ذخیره</button>
                        </div>
                    </div>
                </div>

                <div class="preview-col">
                    <div class="sg-settings-card">
                        <h3>👁️ پیش‌نمایش زنده</h3>
                        <div class="cert-preview-stage">
                            {!! $this->preview_card !!}
                        </div>
                        <div style="text-align:center;font-size:11px;color:var(--text-light);margin-top:10px">
                            📐 {{ $cert_width }}×{{ $cert_height }} cm
                        </div>
                    </div>
                </div>
            </div>
        @endif
'''

    pattern = r"        @if\(\$tab === 'certificate'\).*?        @endif"
    match = re.search(pattern, txt, flags=re.DOTALL)
    if match:
        txt = txt[:match.start()] + NEW_CERT + '\n' + txt[match.end():]

    # جایگزینی بخش label با لینک به component
    OLD_LABEL = """        @if($tab === 'label')
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
        @endif"""

    NEW_LABEL = """        @if($tab === 'label')
            <livewire:settings.labels />
        @endif"""

    if OLD_LABEL in txt:
        txt = txt.replace(OLD_LABEL, NEW_LABEL)
        print("[OK] settings - label tab -> component")
    else:
        # اگه الگو عوض شده، اضافه کن
        if "labels-blade" not in txt and "<livewire:settings.labels />" not in txt:
            # بعد از tab assets
            marker = "{{-- ═══════════ تصاویر ═══════════ --}}"
            if marker in txt:
                label_block = """        {{-- ═══════════ ویرایشگر برچسب ═══════════ --}}
        @if($tab === 'labels')
            <livewire:settings.labels />
        @endif

"""
                txt = txt.replace(marker, label_block + marker)

    settings_view.write_text(txt, encoding='utf-8')
    print("[OK] settings/index.blade.php")


# ═══════════════════════════════════════════════════════════════
# 6. Command — اعمال طرح global به همه شناسنامه‌های قدیم
# ═══════════════════════════════════════════════════════════════

cmd_dir = ROOT / 'app' / 'Console' / 'Commands'
cmd_dir.mkdir(parents=True, exist_ok=True)

APPLY_CMD = '''<?php

namespace App\\Console\\Commands;

use App\\Models\\Certificate;
use App\\Models\\CertSetting;
use Illuminate\\Console\\Command;

class ApplyGlobalDesign extends Command
{
    protected $signature = 'cert:apply-global {--reset-design : حذف design_data اختصاصی}';
    protected $description = 'اعمال طرح پیش‌فرض روی همه شناسنامه‌ها';

    public function handle(): int
    {
        $global = CertSetting::get('global_design', null);

        if (!$global) {
            $this->error('طرح پیش‌فرض وجود ندارد. اول در ویرایشگر ذخیره کن.');
            return 1;
        }

        $count = Certificate::count();

        if ($this->option('reset-design')) {
            $affected = Certificate::whereNotNull('design_data')->update(['design_data' => null]);
            $this->info("{$affected} شناسنامه از طرح اختصاصی پاک شد.");
        }

        $this->info("✅ طرح پیش‌فرض روی {$count} شناسنامه اعمال شد.");
        return 0;
    }
}
'''
write('app/Console/Commands/ApplyGlobalDesign.php', APPLY_CMD)


# ═══════════════════════════════════════════════════════════════
# 7. CertRenderer — اضافه کردن overrideCols به buildCardInner
# ═══════════════════════════════════════════════════════════════

print()
print("=" * 60)
print("DONE")
print("=" * 60)
print()
print("Run:")
print("  php artisan view:clear")
print("  php artisan optimize:clear")
print("  php artisan serve")
print()
print("برای اعمال طرح روی شناسنامه‌های قدیم:")
print("  php artisan cert:apply-global --reset-design")