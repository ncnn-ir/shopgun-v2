# -*- coding: utf-8 -*-
"""ShopGun V2 - v13: Fix preview + Remove designer + Download + Templates"""
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

def patch(rel, old, new, label='', count=1):
    p = ROOT / rel
    if not p.exists():
        print("[SKIP] " + rel + " not found")
        return
    txt = p.read_text(encoding='utf-8')
    if new in txt:
        print("[SKIP] " + label)
        return
    if old not in txt:
        print("[WARN] " + label + " pattern not found")
        return
    txt = txt.replace(old, new, count)
    p.write_text(txt, encoding='utf-8')
    print("[OK] " + label)


# ═══════════════════════════════════════════════════════════════
# 1. FIX preview_card — با دیباگ کامل
# ═══════════════════════════════════════════════════════════════

sphp = ROOT / 'app' / 'Livewire' / 'Settings' / 'Index.php'
if sphp.exists():
    txt = sphp.read_text(encoding='utf-8')

    # پیدا کردن متد preview_card و جایگزینی کامل
    pattern = r"    public function getPreviewCardProperty\(\): string\s*\{.*?\n    \}"
    
    NEW_PREVIEW = '''    public function getPreviewCardProperty(): string
    {
        try {
            // ★ پاک کردن cache override ها
            \\App\\Support\\CertConfig::$overrideSizes = null;
            \\App\\Support\\CertConfig::$overrideCols = null;
            \\App\\Support\\CertConfig::$overrideHideDesc = null;

            $cert = \\App\\Models\\Certificate::latest('id')->first();
            if (!$cert) {
                $cert = new \\App\\Models\\Certificate([
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

            // ★ override ابعاد
            \\App\\Support\\CertConfig::$overrideSizes = [
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

            \\App\\Support\\CertConfig::$overrideCols = [
                $this->cert_col1,
                $this->cert_col2,
                $this->cert_col3,
                $this->cert_col4,
            ];

            \\App\\Support\\CertConfig::$overrideHideDesc = $this->cert_hide_desc;

            $html = \\App\\Services\\CertRenderer::renderCard($cert);

            if (empty($html)) {
                return '<div style="padding:20px;color:#dc2626;font-size:12px">HTML خالی برگشت</div>';
            }

            return $html;

        } catch (\\Throwable $e) {
            return '<div style="padding:16px;background:#fee2e2;color:#991b1b;border-radius:8px;font-size:12px;text-align:right;direction:rtl">'
                 . '<b>خطا در پیش‌نمایش:</b><br>'
                 . htmlspecialchars($e->getMessage())
                 . '<br><br><small style="opacity:.7">' . htmlspecialchars(basename($e->getFile())) . ':' . $e->getLine() . '</small>'
                 . '</div>';
        }
    }'''

    # جایگزینی متد قدیمی
    new_txt, n = re.subn(pattern, NEW_PREVIEW, txt, flags=re.DOTALL)
    if n > 0:
        sphp.write_text(new_txt, encoding='utf-8')
        print("[OK] preview_card - بازنویسی با debug")
    else:
        print("[WARN] preview_card pattern not found")


# ═══════════════════════════════════════════════════════════════
# 2. TEMPLATES — متدهای ذخیره/بارگذاری طرح
# ═══════════════════════════════════════════════════════════════

if sphp.exists():
    txt = sphp.read_text(encoding='utf-8')

    if 'saveTemplate' not in txt:
        methods = '''
    /* ═══════════════════════════════════════════════════════════
       TEMPLATES — ذخیره طرح‌های مختلف
       ═══════════════════════════════════════════════════════════ */
    public array $templates = [];
    public string $new_template_name = '';

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
            'id'          => uniqid('tpl_'),
            'name'        => $name,
            'created_at'  => now()->toIso8601String(),
            'settings'    => [
                'cert_width'  => $this->cert_width,
                'cert_height' => $this->cert_height,
                'cert_img_w'  => $this->cert_img_w,
                'cert_img_h'  => $this->cert_img_h,
                'cert_qr_size'=> $this->cert_qr_size,
                'cert_logo_w' => $this->cert_logo_w,
                'cert_logo_h' => $this->cert_logo_h,
                'cert_code_font'  => $this->cert_code_font,
                'cert_title_font' => $this->cert_title_font,
                'cert_desc_font'  => $this->cert_desc_font,
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
        \\Illuminate\\Support\\Facades\\Cache::forget('app_settings_all');

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

        $s = $tpl['settings'] ?? [];
        foreach ($s as $k => $v) {
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
        \\Illuminate\\Support\\Facades\\Cache::forget('app_settings_all');
        $this->loadTemplates();
        $this->dispatch('notify', type: 'success', message: 'حذف شد');
    }
'''
        txt = txt.replace('    public function render()', methods + '\n    public function render()', 1)

        # در mount
        if '$this->loadTemplates();' not in txt:
            txt = txt.replace(
                "$this->bg_image = (string) AppSetting::get('bg_image', '');",
                "$this->bg_image = (string) AppSetting::get('bg_image', '');\n        $this->loadTemplates();"
            )

        sphp.write_text(txt, encoding='utf-8')
        print("[OK] Settings/Index.php - templates")


# ═══════════════════════════════════════════════════════════════
# 3. CERT ROUTE — download PNG
# ═══════════════════════════════════════════════════════════════

routes = ROOT / 'routes' / 'web.php'
if routes.exists():
    txt = routes.read_text(encoding='utf-8')
    if 'certificates.download' not in txt and "->name('download')" not in txt:
        marker = "Route::get('/designer/{certificate?}', CertificatesDesigner::class)->name('designer');"
        dl_route = """Route::get('/{certificate}/download', function (\\App\\Models\\Certificate $certificate) {
            return view('livewire.certificates.download', compact('certificate'));
        })->name('download');

        """
        if marker in txt:
            txt = txt.replace(marker, dl_route + marker, 1)
            routes.write_text(txt, encoding='utf-8')
            print("[OK] route download اضافه شد")


# ═══════════════════════════════════════════════════════════════
# 4. VIEW MODAL — حذف ویرایشگر + دکمه دانلود
# ═══════════════════════════════════════════════════════════════

vm = ROOT / 'resources' / 'views' / 'livewire' / 'certificates' / 'view-modal.blade.php'
if vm.exists():
    txt = vm.read_text(encoding='utf-8')

    # حذف لینک ویرایشگر قدیمی
    txt = re.sub(
        r'<a href="\{\{ route\(.certificates\.designer.[^<]*</a>\s*',
        '',
        txt
    )

    # اضافه کردن دکمه دانلود PNG قبل از چاپ
    if 'downloadPng' not in txt:
        old_btn = '<button type="button" onclick="window.open(\'{{ route(\'certificates.print\''
        new_btn = '''<button type="button" onclick="downloadPng()"
                        style="padding:9px 16px;background:#0891b2;color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">
                    📥 دانلود
                </button>
                <button type="button" onclick="window.open(\'{{ route(\'certificates.print\''''
        if old_btn in txt:
            txt = txt.replace(old_btn, new_btn, 1)

    # اضافه کردن اسکریپت downloadPng
    if 'function downloadPng' not in txt and 'downloadPng()' in txt:
        script = '''
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script>
function downloadPng() {
    var el = document.querySelector('.cert-preview-stage .certificate, .certificate');
    if (!el) { alert('کارت پیدا نشد'); return; }

    var clone = el.cloneNode(true);
    var w = el.offsetWidth || 600;
    var h = el.offsetHeight || 600;

    // حذف transform برای کپچر دقیق
    clone.style.transform = 'none';
    clone.style.boxShadow = 'none';
    clone.style.width = w + 'px';
    clone.style.height = h + 'px';

    var wrap = document.createElement('div');
    wrap.style.cssText = 'position:fixed;left:-99999px;top:0;background:#fffef9;width:' + w + 'px;height:' + h + 'px';
    wrap.appendChild(clone);
    document.body.appendChild(wrap);

    if (window.html2canvas) {
        html2canvas(clone, {
            scale: 3,
            backgroundColor: '#fffef9',
            useCORS: true,
            logging: false,
            width: w,
            height: h
        }).then(function(canvas) {
            wrap.remove();
            var a = document.createElement('a');
            a.download = 'certificate-{{ $certificate->code ?? "card" }}.png';
            a.href = canvas.toDataURL('image/png');
            a.click();
        }).catch(function(e) {
            wrap.remove();
            alert('خطا: ' + e.message);
        });
    } else {
        // بارگذاری html2canvas
        var s = document.createElement('script');
        s.src = 'https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js';
        s.onload = function() { downloadPng(); };
        document.head.appendChild(s);
    }
}
</script>
'''
        txt = txt.replace('</div>\n@endif', '</div>\n@endif' + script, 1)
        txt = txt.replace('</div>\n@endif\n</div>', '</div>\n@endif\n' + script + '\n</div>', 1)

    vm.write_text(txt, encoding='utf-8')
    print("[OK] view-modal - remove designer + download")


# ═══════════════════════════════════════════════════════════════
# 5. CERT INDEX — دکمه دانلود PNG برای هر ردیف
# ═══════════════════════════════════════════════════════════════

ci = ROOT / 'resources' / 'views' / 'livewire' / 'certificates' / 'index.blade.php'
if ci.exists():
    txt = ci.read_text(encoding='utf-8')

    # اضافه کردن دکمه دانلود قبل از دکمه حذف
    old = '<button wire:click="delete({{ $c->id }})" wire:confirm="حذف شود؟" class="sg-action-btn delete">🗑️</button>'
    new = '''<button type="button" onclick="downloadCertPng({{ $c->id }}, '{{ $c->code }}')" class="sg-action-btn" title="دانلود" style="background:rgba(8,145,178,.15);color:#0891b2">📥</button>
                                    <button wire:click="delete({{ $c->id }})" wire:confirm="حذف شود؟" class="sg-action-btn delete">🗑️</button>'''
    if old in txt and 'downloadCertPng' not in txt:
        txt = txt.replace(old, new)

    # اسکریپت
    if 'function downloadCertPng' not in txt:
        script = '''
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script>
function downloadCertPng(id, code) {
    // لود کارت از طریق fetch به یک صفحه موقت
    fetch('/certificates/' + id, { headers: { 'X-Requested-With': 'XMLHttpRequest' } })
        .then(function(r) { return r.text(); })
        .then(function(html) {
            var div = document.createElement('div');
            div.innerHTML = html;
            var card = div.querySelector('.certificate');
            if (!card) { alert('کارت پیدا نشد'); return; }

            div.style.cssText = 'position:fixed;left:-99999px;top:0;background:#fffef9';
            document.body.appendChild(div);

            html2canvas(card, {
                scale: 3,
                backgroundColor: '#fffef9',
                useCORS: true,
                logging: false
            }).then(function(canvas) {
                div.remove();
                var a = document.createElement('a');
                a.download = 'cert-' + code + '.png';
                a.href = canvas.toDataURL('image/png');
                a.click();
            }).catch(function(e) {
                div.remove();
                alert('خطا: ' + e.message);
            });
        });
}
</script>
'''
        txt = txt + script

    ci.write_text(txt, encoding='utf-8')
    print("[OK] certificates/index - download button")


# ═══════════════════════════════════════════════════════════════
# 6. SETTINGS BLADE — اضافه کردن بخش templates
# ═══════════════════════════════════════════════════════════════

sv = ROOT / 'resources' / 'views' / 'livewire' / 'settings' / 'index.blade.php'
if sv.exists():
    txt = sv.read_text(encoding='utf-8')

    if 'cert_templates' not in txt and 'Templates' not in txt:
        # اضافه کردن قبل از دکمه ذخیره نهایی
        marker = '{{-- ★ تصویر بخش Certificate --}}'

        templates_block = '''{{-- ★ طرح‌های آماده --}}
                    <div class="sg-settings-card" style="margin-top:14px">
                        <h3>💾 طرح‌های آماده</h3>
                        <p style="font-size:11px;color:#94a3b8;margin:0 0 10px">تنظیمات فعلی رو با یک نام ذخیره کن تا بعداً استفاده کنی</p>

                        <div style="display:flex;gap:6px;margin-bottom:12px">
                            <input type="text" wire:model="new_template_name"
                                   placeholder="نام طرح مثلاً: طرح بزرگ"
                                   style="flex:1;padding:8px 10px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:12px">
                            <button wire:click="saveTemplate" class="btn btn-primary btn-sm">➕ ذخیره</button>
                        </div>

                        @if(count($templates))
                            <div style="display:flex;flex-direction:column;gap:6px">
                                @foreach($templates as $tpl)
                                    <div style="display:flex;align-items:center;justify-content:space-between;padding:10px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px">
                                        <div>
                                            <div style="font-weight:700;font-size:12px">{{ $tpl['name'] }}</div>
                                            <div style="font-size:10px;color:#94a3b8">
                                                {{ \\App\\Support\\PersianDate::format($tpl['created_at'] ?? now(), 'Y/m/d H:i') }}
                                            </div>
                                        </div>
                                        <div style="display:flex;gap:4px">
                                            <button wire:click="loadTemplate('{{ $tpl['id'] }}')"
                                                    style="background:#1a5276;color:#fff;border:none;padding:5px 10px;border-radius:6px;font-size:11px;cursor:pointer;font-weight:700">
                                                بارگذاری
                                            </button>
                                            <button wire:click="deleteTemplate('{{ $tpl['id'] }}')"
                                                    wire:confirm="حذف شود؟"
                                                    style="background:#fee2e2;color:#dc2626;border:none;padding:5px 8px;border-radius:6px;font-size:11px;cursor:pointer">
                                                🗑️
                                            </button>
                                        </div>
                                    </div>
                                @endforeach
                            </div>
                        @else
                            <div style="padding:16px;text-align:center;color:#94a3b8;font-size:11px">
                                هنوز طرحی ذخیره نکردی
                            </div>
                        @endif
                    </div>

                    '''

        if marker in txt:
            txt = txt.replace(marker, templates_block + marker, 1)
            sv.write_text(txt, encoding='utf-8')
            print("[OK] settings - templates section")


# ═══════════════════════════════════════════════════════════════
# 7. CertRenderer — گارد اضافی برای preview
# ═══════════════════════════════════════════════════════════════

cr = ROOT / 'app' / 'Services' / 'CertRenderer.php'
if cr.exists():
    txt = cr.read_text(encoding='utf-8')

    # در renderCard اضافه کن try
    old = "public static function renderCard(Certificate $cert): string\n    {"
    new = """public static function renderCard(Certificate $cert): string
    {
        try {"""
    if old in txt and 'try {' not in txt[:txt.find(old) + 100] if old in txt else False:
        pass  # بدون دست زدن

    cr.write_text(txt, encoding='utf-8')


print()
print("=" * 60)
print("DONE")
print("=" * 60)
print("  php artisan view:clear")
print("  php artisan optimize:clear")
print("  php artisan serve")