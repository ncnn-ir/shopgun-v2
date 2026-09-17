# -*- coding: utf-8 -*-
"""ShopGun V2 - v9: Fix CertConfig + Sliders + 2-column preview"""
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
# 1. FIX CertConfig.php — رفع خطای \$ + تقدم override
# ═══════════════════════════════════════════════════════════════

certconfig = ROOT / 'app' / 'Support' / 'CertConfig.php'
if certconfig.exists():
    txt = certconfig.read_text(encoding='utf-8')

    # رفع بک‌اسلش اضافه قبل از $
    txt = txt.replace('\\$', '$')

    # اصلاح تقدم override (override باید آخر اعمال بشه)
    old = """        if (self::$overrideSizes !== null) {
            $d = array_merge($d, self::$overrideSizes);
        }

        return is_array($saved) ? array_merge($d, $saved) : $d;"""

    new = """        $result = is_array($saved) ? array_merge($d, $saved) : $d;

        if (self::$overrideSizes !== null) {
            $result = array_merge($result, self::$overrideSizes);
        }

        return $result;"""

    if old in txt:
        txt = txt.replace(old, new)
        print("[OK] CertConfig - override priority fixed")

    certconfig.write_text(txt, encoding='utf-8')
    print("[OK] CertConfig.php - \\$ fixed")

# ═══════════════════════════════════════════════════════════════
# 2. SETTINGS VIEW — فقط بخش certificate رو جایگزین کن
# ═══════════════════════════════════════════════════════════════

settings_path = ROOT / 'resources' / 'views' / 'livewire' / 'settings' / 'index.blade.php'
if settings_path.exists():
    txt = settings_path.read_text(encoding='utf-8')

    # الگوی جدید برای بخش certificate
    NEW_CERT_SECTION = '''        @if($tab === 'certificate')
            <div class="cert-settings-layout">

                {{-- ستون اهرم‌ها --}}
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
                        <h3>🖼️ ابعاد تصویر محصول</h3>
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

                {{-- ستون پیش‌نمایش --}}
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

    # پیدا کردن و جایگزینی
    pattern = r"        @if\(\$tab === 'certificate'\).*?        @endif"
    match = re.search(pattern, txt, flags=re.DOTALL)
    if match:
        txt = txt[:match.start()] + NEW_CERT_SECTION + '\n' + txt[match.end():]
        settings_path.write_text(txt, encoding='utf-8')
        print("[OK] settings/index.blade.php - cert tab replaced")
    else:
        print("[WARN] certificate section not found")

# ═══════════════════════════════════════════════════════════════
# 3. CSS — layout و اسلایدرهای تمیز
# ═══════════════════════════════════════════════════════════════

css_path = ROOT / 'public' / 'css' / 'extra.css'
if css_path.exists():
    txt = css_path.read_text(encoding='utf-8')

    CERT_CSS = '''

/* ═══════════════════════════════════════════════════════════
   Cert Settings — 2-column + DaisyUI sliders
   ═══════════════════════════════════════════════════════════ */

.cert-settings-layout {
    display: flex;
    flex-direction: column;
    gap: 14px;
}
@media (min-width: 1024px) {
    .cert-settings-layout {
        flex-direction: row;
        align-items: flex-start;
    }
    .cert-settings-layout > .sliders-col {
        flex: 0 0 420px;
    }
    .cert-settings-layout > .preview-col {
        flex: 1;
        position: sticky;
        top: 14px;
        align-self: flex-start;
    }
}

.cert-slider-group {
    margin-bottom: 16px;
}

.cert-slider-label {
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 12px;
    font-weight: 700;
    color: var(--primary, #1a5276);
    margin-bottom: 8px;
}

.cert-slider-label .font-mono {
    font-family: ui-monospace, monospace;
    color: var(--gold-dark, #8b6914);
    font-size: 11px;
    background: rgba(201,168,76,.12);
    padding: 2px 8px;
    border-radius: 6px;
}

/* اسلایدر DaisyUI را تزئین کن */
.cert-slider-group .range {
    height: 8px;
}
.cert-slider-group .range::-webkit-slider-thumb {
    background: var(--gold, #c9a84c);
    border: 2px solid #fff;
    box-shadow: 0 2px 6px rgba(201,168,76,.4);
}

/* پیش‌نمایش کارت */
.cert-preview-stage {
    background: repeating-conic-gradient(#f0f0f0 0% 25%, #fff 0% 50%) 50% / 20px 20px;
    border-radius: 12px;
    padding: 16px;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: auto;
    min-height: 340px;
}
.cert-preview-stage .certificate {
    box-shadow: 0 4px 16px rgba(0,0,0,.12);
    transform-origin: top center;
    max-width: 100%;
}
'''

    if 'Cert Settings — 2-column' not in txt:
        css_path.write_text(txt + CERT_CSS, encoding='utf-8')
        print("[OK] CSS added to extra.css")

print()
print("=" * 60)
print("DONE")
print("=" * 60)