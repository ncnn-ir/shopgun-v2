# -*- coding: utf-8 -*-
"""ShopGun V2 - v11: Fix CertRenderer error + unify sliders"""
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


# ═══════════════════════════════════════════════════════════════
# 1. FIX CertRenderer.php — حذف @php اشتباه در colgroup
# ═══════════════════════════════════════════════════════════════

certrenderer = ROOT / 'app' / 'Services' / 'CertRenderer.php'

if certrenderer.exists():
    txt = certrenderer.read_text(encoding='utf-8')

    # 1a. حذف @php...$__cols...@endphp
    txt = re.sub(
        r'@php\s*\n?\s*\$__cols[^\n]*\n?\s*@endphp\s*\n?',
        '',
        txt
    )

    # 1b. جایگزینی {{ $__cols[0] ?? 25 }} و غیره با مقادیر PHP خام
    # → اینها داخل heredoc PHP هستند، پس باید PHP خام بشن
    replacements = {
        '{{ $__cols[0] ?? 25 }}': '{$__c1}',
        '{{ $__cols[1] ?? 25 }}': '{$__c2}',
        '{{ $__cols[2] ?? 25 }}': '{$__c3}',
        '{{ $__cols[3] ?? 25 }}': '{$__c4}',
    }
    for old, new in replacements.items():
        txt = txt.replace(old, new)

    # 1c. اضافه کردن تعریف متغیرها در ابتدای buildCardInner
    marker = "protected static function buildCardInner(Certificate $cert, bool $includeStyle): string\n    {"

    if marker in txt and '$__c1 =' not in txt:
        extra = marker + '''

        // ★ ستون‌های داینامیک جدول
        $_c = \\App\\Support\\CertConfig::$overrideCols ?? [25, 25, 25, 25];
        $__c1 = $_c[0] ?? 25;
        $__c2 = $_c[1] ?? 25;
        $__c3 = $_c[2] ?? 25;
        $__c4 = $_c[3] ?? 25;'''
        txt = txt.replace(marker, extra, 1)

    certrenderer.write_text(txt, encoding='utf-8')
    print("[OK] CertRenderer.php - colgroup fixed")


# ═══════════════════════════════════════════════════════════════
# 2. SETTINGS VIEW — اهرم‌ها یکسان با برچسب پستی + پیش‌نمایش کنار
# ═══════════════════════════════════════════════════════════════

settings_path = ROOT / 'resources' / 'views' / 'livewire' / 'settings' / 'index.blade.php'

if settings_path.exists():
    txt = settings_path.read_text(encoding='utf-8')

    NEW_CERT = '''        @if($tab === 'certificate')
            <div style="display:grid;grid-template-columns:1fr;gap:14px">
                @media (min-width: 1024px) {
                    & { grid-template-columns: 1fr 1fr; }
                }
            </div>
            <div class="cert-2col">

                {{-- ستون اهرم‌ها --}}
                <div>
                    <div class="sg-settings-card">
                        <h3>📏 ابعاد کارت</h3>
                        <div class="field-grid-2">
                            <div class="field">
                                <label>📐 عرض (cm)</label>
                                <input type="number" step="0.1" min="3" max="15" wire:model.live.debounce.300ms="cert_width" dir="ltr">
                            </div>
                            <div class="field">
                                <label>📐 ارتفاع (cm)</label>
                                <input type="number" step="0.1" min="3" max="15" wire:model.live.debounce.300ms="cert_height" dir="ltr">
                            </div>
                        </div>
                        <div class="btn-row-4">
                            <button type="button" wire:click="setCertPreset(6.5,6.5)" class="btn btn-outline btn-xs">۶.۵×۶.۵</button>
                            <button type="button" wire:click="setCertPreset(7,7)" class="btn btn-outline btn-xs">۷×۷</button>
                            <button type="button" wire:click="setCertPreset(8,6)" class="btn btn-outline btn-xs">۸×۶</button>
                        </div>
                    </div>

                    <div class="sg-settings-card" style="margin-top:14px">
                        <h3>🖼️ تصویر محصول (کراپ خودکار)</h3>
                        <div class="sg-slider">
                            <label>عرض تصویر</label>
                            <input type="range" min="40" max="300" step="5" wire:model.live.debounce.200ms="cert_img_w" class="sg-range">
                            <span>{{ $cert_img_w }}px</span>
                        </div>
                        <div class="sg-slider">
                            <label>ارتفاع تصویر</label>
                            <input type="range" min="40" max="300" step="5" wire:model.live.debounce.200ms="cert_img_h" class="sg-range">
                            <span>{{ $cert_img_h }}px</span>
                        </div>
                    </div>

                    <div class="sg-settings-card" style="margin-top:14px">
                        <h3>📱 QR و لوگو</h3>
                        <div class="sg-slider">
                            <label>اندازه QR</label>
                            <input type="range" min="20" max="120" step="2" wire:model.live.debounce.200ms="cert_qr_size" class="sg-range">
                            <span>{{ $cert_qr_size }}px</span>
                        </div>
                        <div class="sg-slider">
                            <label>عرض لوگو</label>
                            <input type="range" min="10" max="100" step="2" wire:model.live.debounce.200ms="cert_logo_w" class="sg-range">
                            <span>{{ $cert_logo_w }}px</span>
                        </div>
                        <div class="sg-slider">
                            <label>ارتفاع لوگو</label>
                            <input type="range" min="10" max="100" step="2" wire:model.live.debounce.200ms="cert_logo_h" class="sg-range">
                            <span>{{ $cert_logo_h }}px</span>
                        </div>
                    </div>

                    <div class="sg-settings-card" style="margin-top:14px">
                        <h3>🔤 فونت‌ها</h3>
                        <div class="sg-slider">
                            <label>عنوان</label>
                            <input type="range" min="8" max="40" wire:model.live.debounce.200ms="cert_title_font" class="sg-range">
                            <span>{{ $cert_title_font }}px</span>
                        </div>
                        <div class="sg-slider">
                            <label>کد</label>
                            <input type="range" min="6" max="30" wire:model.live.debounce.200ms="cert_code_font" class="sg-range">
                            <span>{{ $cert_code_font }}px</span>
                        </div>
                        <div class="sg-slider">
                            <label>توضیحات</label>
                            <input type="range" min="5" max="20" wire:model.live.debounce.200ms="cert_desc_font" class="sg-range">
                            <span>{{ $cert_desc_font }}px</span>
                        </div>
                    </div>

                    <div class="sg-settings-card" style="margin-top:14px">
                        <h3>📊 عرض ستون‌های جدول (مجموع = ۱۰۰)</h3>
                        <div class="sg-slider">
                            <label>ستون ۱</label>
                            <input type="range" min="10" max="50" wire:model.live.debounce.200ms="cert_col1" class="sg-range">
                            <span>{{ $cert_col1 }}%</span>
                        </div>
                        <div class="sg-slider">
                            <label>ستون ۲</label>
                            <input type="range" min="10" max="50" wire:model.live.debounce.200ms="cert_col2" class="sg-range">
                            <span>{{ $cert_col2 }}%</span>
                        </div>
                        <div class="sg-slider">
                            <label>ستون ۳</label>
                            <input type="range" min="10" max="50" wire:model.live.debounce.200ms="cert_col3" class="sg-range">
                            <span>{{ $cert_col3 }}%</span>
                        </div>
                        <div class="sg-slider">
                            <label>ستون ۴</label>
                            <input type="range" min="10" max="50" wire:model.live.debounce.200ms="cert_col4" class="sg-range">
                            <span>{{ $cert_col4 }}%</span>
                        </div>
                    </div>

                    <div class="sg-settings-card" style="margin-top:14px">
                        <label style="display:flex;align-items:center;gap:8px;cursor:pointer">
                            <input type="checkbox" wire:model.live="cert_hide_desc" class="checkbox checkbox-primary checkbox-sm">
                            <span style="font-size:13px;font-weight:700">مخفی کردن توضیحات</span>
                        </label>

                        <div style="display:flex;justify-content:flex-end;gap:8px;padding-top:14px;border-top:1px solid var(--border);margin-top:14px">
                            <a href="{{ route('certificates.index') }}" wire:navigate class="btn btn-outline btn-sm">🎴 لیست</a>
                            <button wire:click="saveCertificate" class="btn btn-success btn-sm">💾 ذخیره</button>
                        </div>
                    </div>
                </div>

                {{-- ستون پیش‌نمایش --}}
                <div>
                    <div class="sg-settings-card" style="position:sticky;top:14px">
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
        settings_path.write_text(txt, encoding='utf-8')
        print("[OK] settings cert tab replaced")


# ═══════════════════════════════════════════════════════════════
# 3. CSS — اهرم‌ها مثل برچسب پستی
# ═══════════════════════════════════════════════════════════════

css_path = ROOT / 'public' / 'css' / 'extra.css'

if css_path.exists():
    txt = css_path.read_text(encoding='utf-8')

    CERT_CSS = '''

/* ═══════════════════════════════════════════════════════════
   Cert Settings v11 — اهرم‌ها یکسان با برچسب پستی
   ═══════════════════════════════════════════════════════════ */

.cert-2col {
    display: grid;
    grid-template-columns: 1fr;
    gap: 14px;
}
@media (min-width: 1024px) {
    .cert-2col {
        grid-template-columns: 1fr 1fr;
        align-items: flex-start;
    }
}

.field-grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 10px;
}

.btn-row-4 {
    display: flex;
    gap: 6px;
    flex-wrap: wrap;
    margin-top: 10px;
}

/* ═══ اهرم استاندارد — مثل برچسب پستی ═══ */
.sg-slider {
    display: grid;
    grid-template-columns: 90px 1fr 60px;
    gap: 10px;
    align-items: center;
    margin-bottom: 14px;
}
.sg-slider > label {
    font-size: 12px;
    font-weight: 700;
    color: var(--primary, #1a5276);
}
.sg-slider > span {
    font-family: ui-monospace, monospace;
    font-size: 11px;
    color: var(--gold-dark, #8b6914);
    background: rgba(201,168,76,.12);
    padding: 2px 6px;
    border-radius: 6px;
    text-align: center;
    direction: ltr;
}

/* اهرم */
.sg-range {
    -webkit-appearance: none;
    appearance: none;
    width: 100%;
    height: 6px;
    background: linear-gradient(to left, var(--gold, #c9a84c), var(--gold-light, #f0d68a));
    border-radius: 3px;
    outline: none;
    cursor: pointer;
}
.sg-range::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 20px;
    height: 20px;
    background: #fff;
    border: 3px solid var(--gold, #c9a84c);
    border-radius: 50%;
    cursor: pointer;
    box-shadow: 0 2px 6px rgba(0,0,0,.15);
    transition: transform .1s;
}
.sg-range::-webkit-slider-thumb:hover {
    transform: scale(1.15);
}
.sg-range::-moz-range-thumb {
    width: 18px;
    height: 18px;
    background: #fff;
    border: 3px solid var(--gold, #c9a84c);
    border-radius: 50%;
    cursor: pointer;
    box-shadow: 0 2px 6px rgba(0,0,0,.15);
}

/* پیش‌نمایش */
.cert-preview-stage {
    background: repeating-conic-gradient(#f0f0f0 0% 25%, #fff 0% 50%) 50% / 20px 20px;
    border-radius: 12px;
    padding: 20px;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: auto;
    min-height: 400px;
    border: 1px solid #e2e8f0;
}
.cert-preview-stage .certificate {
    box-shadow: 0 4px 20px rgba(0,0,0,.1);
    transform-origin: top center;
    max-width: 100%;
}

@media (max-width: 500px) {
    .sg-slider {
        grid-template-columns: 70px 1fr 50px;
        gap: 6px;
    }
    .sg-slider > label { font-size: 11px; }
    .sg-slider > span { font-size: 10px; }
}
'''

    if 'Cert Settings v11' not in txt:
        css_path.write_text(txt + CERT_CSS, encoding='utf-8')
        print("[OK] CSS added")


print()
print("=" * 60)
print("DONE")
print("=" * 60)
print()
print("Run:")
print("  php artisan view:clear")
print("  php artisan optimize:clear")
print("  php artisan serve")