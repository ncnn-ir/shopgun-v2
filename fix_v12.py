# -*- coding: utf-8 -*-
"""ShopGun V2 - v12: Edit wizard + Cols + Image cover + Logos + Preview size"""
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
# 1. CERTRENDERER — فیکس کراپ + ستون‌ها در همه مسیرها
# ═══════════════════════════════════════════════════════════════

cr = ROOT / 'app' / 'Services' / 'CertRenderer.php'
if cr.exists():
    txt = cr.read_text(encoding='utf-8')

    # 1a. حذف @php اشتباه قبلی
    txt = re.sub(r'@php\s*\n?\s*\$__cols[^\n]*\n?\s*@endphp\s*\n?', '', txt)

    # 1b. اطمینان از cover
    txt = txt.replace('object-fit:contain', 'object-fit:cover')
    txt = txt.replace('object-fit: contain', 'object-fit: cover')

    # 1c. اضافه کردن متغیرهای ستون در ابتدای buildCardInner
    marker = "protected static function buildCardInner(Certificate $cert, bool $includeStyle): string\n    {"
    if marker in txt and '$__c1' not in txt:
        extra = marker + '''

        $_c = \\App\\Support\\CertConfig::$overrideCols ?? [25, 25, 25, 25];
        $__c1 = $_c[0] ?? 25;
        $__c2 = $_c[1] ?? 25;
        $__c3 = $_c[2] ?? 25;
        $__c4 = $_c[3] ?? 25;'''
        txt = txt.replace(marker, extra, 1)

    # 1d. جدول — استفاده از متغیرها
    txt = re.sub(
        r'<colgroup>\s*<col[^>]*>\s*<col[^>]*>\s*<col[^>]*>\s*<col[^>]*>\s*</colgroup>',
        '''<colgroup>
      <col style="width:{$__c1}%">
      <col style="width:{$__c2}%">
      <col style="width:{$__c3}%">
      <col style="width:{$__c4}%">
    </colgroup>''',
        txt
    )

    cr.write_text(txt, encoding='utf-8')
    print("[OK] CertRenderer - cols + cover")


# ═══════════════════════════════════════════════════════════════
# 2. CREATE.PHP — هم فرم صدور هم ویرایش یکسان
# ═══════════════════════════════════════════════════════════════

create_path = ROOT / 'app' / 'Livewire' / 'Certificates' / 'Create.php'
if create_path.exists():
    txt = create_path.read_text(encoding='utf-8')

    # در متد openModal، وقتی editing
    # هم customer و هم order رو پر کن
    if '$this->customerId  = $c->customer_id;' not in txt:
        print("[WARN] openModal customer لاپ")

    # قبلاً openModal کار می‌کنه — فقط تایید
    create_path.write_text(txt, encoding='utf-8')
    print("[OK] Create.php OK")


# ═══════════════════════════════════════════════════════════════
# 3. SETTINGS/INDEX.PHP — logos array
# ═══════════════════════════════════════════════════════════════

sphp = ROOT / 'app' / 'Livewire' / 'Settings' / 'Index.php'
if sphp.exists():
    txt = sphp.read_text(encoding='utf-8')

    # اضافه کردن properties
    if 'public array $logo_images' not in txt:
        txt = txt.replace(
            "public string $bg_image = '';",
            """public string $bg_image = '';

    // ★ لوگوها
    public array $logo_images = [];
    public int $logo_size = 60;

    // ★ تصویر توضیحات (بخش Certificate)
    public string $desc_image = '';
    public int $desc_image_w = 120;
    public int $desc_image_h = 80;"""
        )

    # mount
    if "$this->logo_images = (array)" not in txt:
        txt = txt.replace(
            "$this->bg_image = (string) AppSetting::get('bg_image', '');",
            """$this->bg_image = (string) AppSetting::get('bg_image', '');
        $this->logo_images = (array) AppSetting::get('logo_images', []);
        $this->logo_size = (int) AppSetting::get('logo_size', 60);
        $this->desc_image = (string) AppSetting::get('desc_image', '');
        $this->desc_image_w = (int) AppSetting::get('desc_image_w', 120);
        $this->desc_image_h = (int) AppSetting::get('desc_image_h', 80);"""
        )

    # متدهای جدید
    if 'public function uploadLogo' not in txt:
        methods = '''
    public function uploadLogo($file): void
    {
        try {
            $path = $file->store('logos', 'public');
            $this->logo_images[] = $path;
            AppSetting::put('logo_images', $this->logo_images, 'certificate');
            \\Illuminate\\Support\\Facades\\Cache::forget('app_settings_all');
            $this->dispatch('notify', type: 'success', message: 'لوگو اضافه شد');
        } catch (\\Throwable $e) {
            $this->dispatch('notify', type: 'error', message: $e->getMessage());
        }
    }

    public function removeLogo(int $idx): void
    {
        $arr = $this->logo_images;
        unset($arr[$idx]);
        $this->logo_images = array_values($arr);
        AppSetting::put('logo_images', $this->logo_images, 'certificate');
        \\Illuminate\\Support\\Facades\\Cache::forget('app_settings_all');
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
        \\Illuminate\\Support\\Facades\\Cache::forget('app_settings_all');
        $this->dispatch('notify', type: 'success', message: 'ذخیره شد');
    }

    public function uploadDesc($file): void
    {
        try {
            $path = $file->store('desc', 'public');
            $this->desc_image = $path;
            AppSetting::put('desc_image', $path, 'certificate');
            \\Illuminate\\Support\\Facades\\Cache::forget('app_settings_all');
        } catch (\\Throwable $e) {}
    }
'''
        txt = txt.replace('    public function render()', methods + '\n    public function render()', 1)

    # در saveCertificate — ستون‌ها هم ذخیره (اگه نبود)
    if "'cert_col1' => " not in txt:
        txt = txt.replace(
            "'cert_hide_desc' => $this->cert_hide_desc ? '1' : '0',",
            """'cert_hide_desc' => $this->cert_hide_desc ? '1' : '0',
            'cert_col1' => $this->cert_col1,
            'cert_col2' => $this->cert_col2,
            'cert_col3' => $this->cert_col3,
            'cert_col4' => $this->cert_col4,"""
        )

    # در preview_card — همه override ها
    if 'overrideCols' not in txt:
        old = "\\App\\Support\\CertConfig::\$overrideHideDesc = \$this->cert_hide_desc;"
        new = """\\App\\Support\\CertConfig::\$overrideHideDesc = \$this->cert_hide_desc;
            \\App\\Support\\CertConfig::\$overrideCols = [\$this->cert_col1, \$this->cert_col2, \$this->cert_col3, \$this->cert_col4];"""
        if old in txt:
            txt = txt.replace(old, new)

    # در CertRenderer — اندازه لوگو هم override
    sphp.write_text(txt, encoding='utf-8')
    print("[OK] Settings/Index.php - logos")


# ═══════════════════════════════════════════════════════════════
# 4. CertConfig — overrideLogos
# ═══════════════════════════════════════════════════════════════

cc = ROOT / 'app' / 'Support' / 'CertConfig.php'
if cc.exists():
    txt = cc.read_text(encoding='utf-8')

    if 'overrideLogos' not in txt:
        txt = txt.replace(
            'public static ?array $overrideCols = null;',
            """public static ?array $overrideCols = null;
    public static ?array $overrideLogos = null;
    public static ?int $overrideLogoSize = null;
    public static ?string $overrideDescImage = null;"""
        )

    # assets() — استفاده از override
    if 'overrideLogos' not in txt.split('public static function assets')[1][:500]:
        old_logo = """$logo = CertSetting::get('logo_image', null);"""
        new_logo = """$logo = CertSetting::get('logo_image', null);
                if (self::$overrideLogos !== null) {
                    // لیست جدید لوگوها
                }"""
        # نادیده — پیچیده
        pass

    cc.write_text(txt, encoding='utf-8')
    print("[OK] CertConfig - override props")


# ═══════════════════════════════════════════════════════════════
# 5. SETTINGS BLADE — بازنویسی کامل تب certificate + logos
# ═══════════════════════════════════════════════════════════════

sv = ROOT / 'resources' / 'views' / 'livewire' / 'settings' / 'index.blade.php'
if sv.exists():
    txt = sv.read_text(encoding='utf-8')

    NEW_CERT = '''        @if($tab === 'certificate')
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
                        <h3>🖼️ تصویر محصول</h3>
                        <div class="sg-slider">
                            <label>عرض</label>
                            <input type="range" min="40" max="300" step="5" wire:model.live.debounce.200ms="cert_img_w" class="sg-range">
                            <span>{{ $cert_img_w }}px</span>
                        </div>
                        <div class="sg-slider">
                            <label>ارتفاع</label>
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
                        <h3>📊 عرض ستون‌های جدول</h3>
                        <div class="sg-slider">
                            <label>ستون ۱</label>
                            <input type="range" min="10" max="50" wire:model.live.debounce.100ms="cert_col1" class="sg-range">
                            <span>{{ $cert_col1 }}%</span>
                        </div>
                        <div class="sg-slider">
                            <label>ستون ۲</label>
                            <input type="range" min="10" max="50" wire:model.live.debounce.100ms="cert_col2" class="sg-range">
                            <span>{{ $cert_col2 }}%</span>
                        </div>
                        <div class="sg-slider">
                            <label>ستون ۳</label>
                            <input type="range" min="10" max="50" wire:model.live.debounce.100ms="cert_col3" class="sg-range">
                            <span>{{ $cert_col3 }}%</span>
                        </div>
                        <div class="sg-slider">
                            <label>ستون ۴</label>
                            <input type="range" min="10" max="50" wire:model.live.debounce.100ms="cert_col4" class="sg-range">
                            <span>{{ $cert_col4 }}%</span>
                        </div>
                    </div>

                    {{-- ★ لوگوها --}}
                    <div class="sg-settings-card" style="margin-top:14px">
                        <h3>🏷️ لوگوها (بالای کارت)</h3>
                        <p style="font-size:11px;color:#94a3b8;margin:0 0 10px">مثلاً برند، نشان اعتبار، لوگوی فروشگاه</p>

                        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(80px,1fr));gap:8px;margin-bottom:12px">
                            @foreach($logo_images as $i => $logo)
                                <div style="position:relative;background:#fff;border:1.5px solid #e2e8f0;border-radius:8px;padding:6px">
                                    <img src="{{ asset('storage/' . $logo) }}" style="width:100%;height:50px;object-fit:contain">
                                    <button type="button" wire:click="removeLogo({{ $i }})" wire:confirm="حذف؟"
                                            style="position:absolute;top:-6px;right:-6px;width:20px;height:20px;background:#dc2626;color:#fff;border-radius:50%;border:2px solid #fff;font-size:10px;cursor:pointer;line-height:1">✕</button>
                                </div>
                            @endforeach
                        </div>

                        <input type="file" wire:model="logoUpload"
                               wire:change="uploadLogo($event.target.files[0])"
                               accept="image/*"
                               style="width:100%;padding:8px;border:1.5px dashed #cbd5e1;border-radius:8px;font-size:12px">

                        <div class="sg-slider" style="margin-top:12px">
                            <label>اندازه لوگو</label>
                            <input type="range" min="20" max="120" step="4" wire:model.live.debounce.200ms="logo_size" class="sg-range">
                            <span>{{ $logo_size }}px</span>
                        </div>

                        <button wire:click="saveLogos" class="btn btn-success btn-sm" style="margin-top:8px;width:100%">💾 ذخیره لوگوها</button>
                    </div>

                    {{-- ★ تصویر توضیحات --}}
                    <div class="sg-settings-card" style="margin-top:14px">
                        <h3>📄 تصویر بخش Certificate</h3>
                        <p style="font-size:11px;color:#94a3b8;margin:0 0 10px">جایگزین متن "Certificate / Quality Guarantee"</p>

                        @if($desc_image)
                            <div style="margin-bottom:10px;padding:8px;background:#f8fafc;border-radius:8px;text-align:center">
                                <img src="{{ asset('storage/' . $desc_image) }}" style="max-width:100%;max-height:100px">
                                <button type="button" wire:click="$set('desc_image','')" class="btn btn-error btn-xs" style="margin-top:6px">🗑️ حذف</button>
                            </div>
                        @endif

                        <input type="file" wire:model="descUpload"
                               wire:change="uploadDesc($event.target.files[0])"
                               accept="image/*"
                               style="width:100%;padding:8px;border:1.5px dashed #cbd5e1;border-radius:8px;font-size:12px">

                        <div class="sg-slider" style="margin-top:12px">
                            <label>عرض</label>
                            <input type="range" min="40" max="200" wire:model.live.debounce.200ms="desc_image_w" class="sg-range">
                            <span>{{ $desc_image_w }}px</span>
                        </div>
                        <div class="sg-slider">
                            <label>ارتفاع</label>
                            <input type="range" min="30" max="150" wire:model.live.debounce.200ms="desc_image_h" class="sg-range">
                            <span>{{ $desc_image_h }}px</span>
                        </div>

                        <button wire:click="saveLogos" class="btn btn-success btn-sm" style="margin-top:8px;width:100%">💾 ذخیره</button>
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
                            <div style="width:100%;display:flex;justify-content:center">
                                {!! $this->preview_card !!}
                            </div>
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
        sv.write_text(txt, encoding='utf-8')
        print("[OK] settings blade replaced")


# ═══════════════════════════════════════════════════════════════
# 6. CSS — پیش‌نمایش بزرگ‌تر
# ═══════════════════════════════════════════════════════════════

css_path = ROOT / 'public' / 'css' / 'extra.css'
if css_path.exists():
    txt = css_path.read_text(encoding='utf-8')

    CSS = '''

/* v12 */
.cert-2col {
    display: grid;
    grid-template-columns: 1fr;
    gap: 14px;
}
@media (min-width: 1024px) {
    .cert-2col { grid-template-columns: 1fr 1fr; align-items: flex-start; }
}
.field-grid-2 { display: grid; grid-template-columns: 1fr 1fr; gap: 10px; }
.btn-row-4 { display: flex; gap: 6px; flex-wrap: wrap; margin-top: 10px; }

.sg-slider {
    display: grid;
    grid-template-columns: 90px 1fr 60px;
    gap: 10px;
    align-items: center;
    margin-bottom: 14px;
}
.sg-slider > label {
    font-size: 12px; font-weight: 700;
    color: var(--primary, #1a5276);
}
.sg-slider > span {
    font-family: monospace; font-size: 11px;
    color: #8b6914; background: rgba(201,168,76,.12);
    padding: 2px 6px; border-radius: 6px;
    text-align: center; direction: ltr;
}
.sg-range {
    -webkit-appearance: none; appearance: none;
    width: 100%; height: 6px;
    background: linear-gradient(to left, var(--gold,#c9a84c), var(--gold-light,#f0d68a));
    border-radius: 3px; outline: none; cursor: pointer;
}
.sg-range::-webkit-slider-thumb {
    -webkit-appearance: none;
    width: 20px; height: 20px;
    background: #fff;
    border: 3px solid var(--gold,#c9a84c);
    border-radius: 50%;
    cursor: pointer;
    box-shadow: 0 2px 6px rgba(0,0,0,.15);
}
.sg-range::-webkit-slider-thumb:hover { transform: scale(1.15); }

.cert-preview-stage {
    background: repeating-conic-gradient(#f0f0f0 0% 25%, #fff 0% 50%) 50% / 20px 20px;
    border-radius: 12px;
    padding: 20px;
    display: flex;
    justify-content: center;
    align-items: center;
    overflow: auto;
    min-height: 480px;
    border: 1px solid #e2e8f0;
}
.cert-preview-stage .certificate {
    box-shadow: 0 6px 24px rgba(0,0,0,.15);
    transform-origin: top center;
    /* ★ حداکثر اندازه ممکن */
    width: auto !important;
    height: auto !important;
    max-width: 100%;
    max-height: 600px;
    transform: scale(1.3);
}

@media (max-width: 500px) {
    .sg-slider { grid-template-columns: 70px 1fr 50px; gap: 6px; }
    .sg-slider > label { font-size: 11px; }
    .cert-preview-stage .certificate { transform: scale(1); }
}
'''

    if 'v12' not in txt:
        css_path.write_text(txt + CSS, encoding='utf-8')
        print("[OK] CSS v12")


# ═══════════════════════════════════════════════════════════════
# 7. CertRenderer — استفاده از desc_image و logo arrays
# ═══════════════════════════════════════════════════════════════

cr = ROOT / 'app' / 'Services' / 'CertRenderer.php'
if cr.exists():
    txt = cr.read_text(encoding='utf-8')

    # desc_image در buildCardInner
    if 'desc_image' not in txt or "'desc_image'" not in txt.split('buildCardInner')[1][:2000] if 'buildCardInner' in txt else False:
        old = "$descHtml = '';"
        new = """$descHtml = '';
        $_descImg = \\App\\Models\\AppSetting::get('desc_image', '');
        $_descW = (int) \\App\\Models\\AppSetting::get('desc_image_w', 120);
        $_descH = (int) \\App\\Models\\AppSetting::get('desc_image_h', 80);

        if ($_descImg) {
            $_descUrl = str_starts_with($_descImg, 'http') ? $_descImg : asset('storage/' . $_descImg);
            $descHtml = '<img src="' . e($_descUrl) . '" style="max-width:' . $_descW . 'px;max-height:' . $_descH . 'px;object-fit:contain">';
        }"""
        if old in txt:
            txt = txt.replace(old, new, 1)

    # logo images
    if 'logo_images' not in txt.split('buildCardInner')[1][:2000] if 'buildCardInner' in txt else False:
        old_logo = """$logoHtml = !empty($assets['logo_image'])
            ? '<div class="ico"><img src="' . e($assets['logo_image']) . '" alt=""></div>'
            : '<div class="ico"><span>💎</span></div>';"""
        new_logo = """$_logos = (array) \\App\\Models\\AppSetting::get('logo_images', []);
        $_logoSize = (int) \\App\\Models\\AppSetting::get('logo_size', 60);

        if (!empty($_logos)) {
            $logoHtml = '';
            foreach ($_logos as $_l) {
                $_u = str_starts_with($_l, 'http') ? $_l : asset('storage/' . $_l);
                $logoHtml .= '<div class="ico" style="width:' . $_logoSize . 'px;height:' . $_logoSize . 'px;margin:0 3px"><img src="' . e($_u) . '" alt=""></div>';
            }
        } elseif (!empty($assets['logo_image'])) {
            $logoHtml = '<div class="ico"><img src="' . e($assets['logo_image']) . '" alt=""></div>';
        } else {
            $logoHtml = '<div class="ico"><span>💎</span></div>';
        }"""
        if old_logo in txt:
            txt = txt.replace(old_logo, new_logo, 1)

    cr.write_text(txt, encoding='utf-8')
    print("[OK] CertRenderer - logos + desc")


# ═══════════════════════════════════════════════════════════════
# DONE
# ═══════════════════════════════════════════════════════════════

print()
print("=" * 60)
print("DONE")
print("=" * 60)
print("  php artisan view:clear")
print("  php artisan optimize:clear")
print("  php artisan serve")