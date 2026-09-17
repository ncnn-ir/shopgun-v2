# -*- coding: utf-8 -*-
"""ShopGun - Fix download + fetch stones + برلیان + JSON import"""
from pathlib import Path
import time, re

ROOT = Path(r'D:\prodo\shopgun-v2.2')

def write(rel, content):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        p.rename(str(p) + '.bak-' + str(int(time.time())))
    p.write_text(content, encoding='utf-8')
    print("[OK] " + rel)


# ═══════════════════════════════════════════════════════════════
# 1. SETTINGS/INDEX.PHP — اضافه کردن متدهای fetch + import
# ═══════════════════════════════════════════════════════════════

sphp = ROOT / 'app' / 'Livewire' / 'Settings' / 'Index.php'
if sphp.exists():
    txt = sphp.read_text(encoding='utf-8')

    # اضافه کردن properties
    if 'public string $fetch_status' not in txt:
        txt = txt.replace(
            "public ?int $editing_metal_idx = null;",
            """public ?int $editing_metal_idx = null;

    // ★ Fetch از سایت
    public string $fetch_status = '';
    public bool $fetching = false;
    public int $fetch_limit = 200;

    // ★ JSON Import
    public string $json_input = '';
    public string $json_status = '';
    public $json_file = null;"""
        )

    # اضافه کردن متدها
    if 'public function fetchStonesFromWoo' not in txt:
        methods = '''
    /* ═══════════════════════════════════════════════════════════
       ★ FETCH STONES FROM WOOCOMMERCE
       ═══════════════════════════════════════════════════════════ */
    public function fetchStonesFromWoo(): void
    {
        $this->fetching = true;
        $this->fetch_status = '⏳ در حال دریافت محصولات از سایت...';

        try {
            $url    = trim((string) AppSetting::get('commerce_url', ''));
            $key    = trim((string) AppSetting::get('commerce_key', ''));
            $secret = trim((string) AppSetting::get('commerce_secret', ''));

            if (!$url || !$key || !$secret) {
                $this->fetch_status = '❌ تنظیمات کامرس پر نشده';
                $this->fetching = false;
                return;
            }

            $base = rtrim($url, '/');
            if (!str_contains($base, '/wp-json')) $base .= '/wp-json/wc/v3';

            // دریافت محصولات
            $page = 1;
            $allProducts = [];
            $perPage = 100;

            while ($page <= 5 && count($allProducts) < $this->fetch_limit) {
                $r = \\Illuminate\\Support\\Facades\\Http::withBasicAuth($key, $secret)
                    ->timeout(30)
                    ->connectTimeout(15)
                    ->retry(2, 2000)
                    ->get("{$base}/products", [
                        'per_page' => $perPage,
                        'page' => $page,
                        'status' => 'publish',
                    ]);

                if (!$r->successful()) {
                    if ($page === 1) {
                        $this->fetch_status = '❌ خطای HTTP ' . $r->status();
                        $this->fetching = false;
                        return;
                    }
                    break;
                }

                $products = $r->json();
                if (empty($products)) break;

                $allProducts = array_merge($allProducts, $products);
                if (count($products) < $perPage) break;
                $page++;
            }

            if (empty($allProducts)) {
                $this->fetch_status = '❌ محصولی از سایت دریافت نشد';
                $this->fetching = false;
                return;
            }

            // استخراج سنگ‌ها از نام + ویژگی‌ها
            $foundStones = [];
            $foundMetals = [];
            $stoneKeywords = [
                'فیروزه عجمی'   => ['origin' => 'نیشابور',   'flag' => 'ir', 'icon' => '💠'],
                'فیروزه شجری'   => ['origin' => 'نیشابور',   'flag' => 'ir', 'icon' => '💠'],
                'فیروزه'        => ['origin' => 'نیشابور',   'flag' => 'ir', 'icon' => '💠'],
                'عقیق یمانی'    => ['origin' => 'یمن',        'flag' => 'ye', 'icon' => '🔴'],
                'عقیق سلیمانی'  => ['origin' => 'یمن',        'flag' => 'ye', 'icon' => '❤️'],
                'عقیق شجر'      => ['origin' => 'یمن',        'flag' => 'ye', 'icon' => '🌿'],
                'عقیق'          => ['origin' => 'یمن',        'flag' => 'ye', 'icon' => '🔴'],
                'در نجف'        => ['origin' => 'عراق',       'flag' => 'iq', 'icon' => '⚪'],
                'الماس'         => ['origin' => 'آفریقا',     'flag' => 'za', 'icon' => '💎'],
                'یاقوت سرخ'     => ['origin' => 'میانمار',    'flag' => 'mm', 'icon' => '❤️'],
                'یاقوت کبود'    => ['origin' => 'سری‌لانکا',  'flag' => 'lk', 'icon' => '🔵'],
                'یاقوت'         => ['origin' => 'سری‌لانکا',  'flag' => 'lk', 'icon' => '💙'],
                'زمرد'          => ['origin' => 'کلمبیا',     'flag' => 'co', 'icon' => '🟢'],
                'توپاز'         => ['origin' => 'برزیل',      'flag' => 'br', 'icon' => '💛'],
                'آمیتیست'       => ['origin' => 'برزیل',      'flag' => 'br', 'icon' => '🟣'],
                'اوپال'         => ['origin' => 'استرالیا',   'flag' => 'au', 'icon' => '🌈'],
                'مرجان'         => ['origin' => 'مدیترانه',   'flag' => 'it', 'icon' => '🟠'],
                'لاجورد'        => ['origin' => 'افغانستان',  'flag' => 'af', 'icon' => '💙'],
                'چشم ببر'       => ['origin' => 'آفریقا',     'flag' => 'za', 'icon' => '🐯'],
                'آکوامارین'     => ['origin' => 'برزیل',      'flag' => 'br', 'icon' => '💧'],
                'سیترین'       => ['origin' => 'برزیل',      'flag' => 'br', 'icon' => '🍋'],
                'پریدوت'       => ['origin' => 'مصر',        'flag' => 'eg', 'icon' => '🟩'],
                'مروارید'       => ['origin' => 'خلیج فارس',  'flag' => 'ir', 'icon' => '⚪'],
                'حدید'          => ['origin' => 'ایران',      'flag' => 'ir', 'icon' => '⚫'],
                'یشم'           => ['origin' => 'چین',        'flag' => 'cn', 'icon' => '🟢'],
                'رز کوارتز'     => ['origin' => 'برزیل',      'flag' => 'br', 'icon' => '🌸'],
            ];

            foreach ($allProducts as $p) {
                $name = $p['name'] ?? '';
                $attrs = $p['attributes'] ?? [];

                // از نام
                foreach ($stoneKeywords as $key => $meta) {
                    if (mb_strpos($name, $key) !== false) {
                        if (!isset($foundStones[$key])) {
                            $foundStones[$key] = [
                                'name' => $key,
                                'en' => $this->guessEnName($key),
                                'origin' => $meta['origin'],
                                'flag' => $meta['flag'],
                                'icon' => $meta['icon'],
                            ];
                        }
                    }
                }

                // از attributes
                foreach ($attrs as $attr) {
                    $attrName = $attr['name'] ?? '';
                    $options = $attr['options'] ?? [];

                    if (mb_strpos($attrName, 'سنگ') !== false) {
                        foreach ($options as $opt) {
                            if (!isset($foundStones[$opt])) {
                                $foundStones[$opt] = [
                                    'name' => $opt,
                                    'en' => $this->guessEnName($opt),
                                    'origin' => '—',
                                    'flag' => 'ir',
                                    'icon' => '💎',
                                ];
                            }
                        }
                    }

                    if (mb_strpos($attrName, 'فلز') !== false || mb_strpos($attrName, 'عیار') !== false) {
                        foreach ($options as $opt) {
                            if (!isset($foundMetals[$opt])) {
                                $foundMetals[$opt] = [
                                    'name' => $opt,
                                    'en' => $opt,
                                    'carat' => $this->guessCarat($opt),
                                ];
                            }
                        }
                    }
                }
            }

            // ادغام با لیست موجود
            $existingNames = array_column($this->cert_stones, 'name');
            $added = 0;
            foreach ($foundStones as $s) {
                if (!in_array($s['name'], $existingNames, true)) {
                    $this->cert_stones[] = $s;
                    $added++;
                }
            }

            $existingMetals = array_column($this->cert_metals, 'name');
            $metalsAdded = 0;
            foreach ($foundMetals as $m) {
                if (!in_array($m['name'], $existingMetals, true)) {
                    $this->cert_metals[] = $m;
                    $metalsAdded++;
                }
            }

            // ذخیره
            AppSetting::put('cert_stones', $this->cert_stones, 'certificate');
            AppSetting::put('cert_metals', $this->cert_metals, 'certificate');
            Cache::forget('app_settings_all');

            $this->fetch_status = "✅ {$added} سنگ جدید + {$metalsAdded} فلز جدید از " . count($allProducts) . " محصول سایت اضافه شد";

        } catch (\\Throwable $e) {
            $this->fetch_status = '❌ ' . $e->getMessage();
        }

        $this->fetching = false;
    }

    protected function guessEnName(string $fa): string
    {
        $map = [
            'فیروزه' => 'Turquoise', 'عقیق' => 'Agate', 'الماس' => 'Diamond',
            'یاقوت' => 'Sapphire', 'زمرد' => 'Emerald', 'توپاز' => 'Topaz',
            'آمیتیست' => 'Amethyst', 'اوپال' => 'Opal', 'مرجان' => 'Coral',
            'لاجورد' => 'Lapis Lazuli', 'چشم ببر' => 'Tiger Eye',
            'مروارید' => 'Pearl', 'حدید' => 'Hematite', 'یشم' => 'Jade',
            'آکوامارین' => 'Aquamarine', 'سیترین' => 'Citrine',
            'پریدوت' => 'Peridot', 'رز کوارتز' => 'Rose Quartz',
        ];
        foreach ($map as $k => $v) {
            if (mb_strpos($fa, $k) !== false) return $v;
        }
        return $fa;
    }

    protected function guessCarat(string $metal): string
    {
        if (preg_match('/(18|21|22|24)/', $metal, $m)) {
            return match ($m[1]) {
                '18' => '750', '21' => '875', '22' => '916', '24' => '999',
                default => '925',
            };
        }
        if (mb_strpos($metal, 'نقره') !== false || mb_strpos($metal, 'silver') !== false) {
            return '925';
        }
        if (mb_strpos($metal, 'پلاتین') !== false) return '950';
        return '-';
    }

    /* ═══════════════════════════════════════════════════════════
       ★ JSON IMPORT
       ═══════════════════════════════════════════════════════════ */
    public function importStonesJson(): void
    {
        $this->json_status = '⏳ در حال پردازش...';

        $json = trim($this->json_input);
        if ($json === '') {
            $this->json_status = '❌ JSON خالی است';
            return;
        }

        try {
            $data = json_decode($json, true);
            if (!is_array($data)) {
                $this->json_status = '❌ JSON نامعتبر';
                return;
            }

            // پشتیبانی از چند فرمت: {stones: [...]} یا [...]
            $stones = $data['stones'] ?? $data;

            if (!is_array($stones)) {
                $this->json_status = '❌ ساختار نامعتبر — باید آرایه باشد';
                return;
            }

            $existing = array_column($this->cert_stones, 'name');
            $added = 0;
            $updated = 0;

            foreach ($stones as $s) {
                if (!is_array($s)) continue;
                $name = trim((string) ($s['name'] ?? ''));
                if ($name === '') continue;

                $stone = [
                    'name' => $name,
                    'en' => (string) ($s['en'] ?? $s['name_en'] ?? $name),
                    'origin' => (string) ($s['origin'] ?? '—'),
                    'flag' => (string) ($s['flag'] ?? 'ir'),
                    'icon' => (string) ($s['icon'] ?? '💎'),
                ];

                $idx = array_search($name, $existing, true);
                if ($idx !== false) {
                    $this->cert_stones[$idx] = $stone;
                    $updated++;
                } else {
                    $this->cert_stones[] = $stone;
                    $existing[] = $name;
                    $added++;
                }
            }

            AppSetting::put('cert_stones', $this->cert_stones, 'certificate');
            Cache::forget('app_settings_all');

            $this->json_status = "✅ {$added} سنگ اضافه + {$updated} سنگ بروزرسانی شد";
            $this->json_input = '';
            $this->loadStonesMetals();

        } catch (\\Throwable $e) {
            $this->json_status = '❌ ' . $e->getMessage();
        }
    }

    public function clearAllStones(): void
    {
        AppSetting::put('cert_stones', [], 'certificate');
        Cache::forget('app_settings_all');
        $this->cert_stones = [];
        $this->dispatch('notify', type: 'success', message: 'همه سنگ‌ها پاک شدند');
    }

    public function resetStonesToDefault(): void
    {
        $this->cert_stones = $this->defaultStones();
        AppSetting::put('cert_stones', $this->cert_stones, 'certificate');
        Cache::forget('app_settings_all');
        $this->dispatch('notify', type: 'success', message: 'بازگشت به پیش‌فرض');
    }
'''
        txt = txt.replace('    public function render()', methods + '\n    public function render()', 1)

    sphp.write_text(txt, encoding='utf-8')
    print("[OK] Settings/Index.php - fetch + import")


# ═══════════════════════════════════════════════════════════════
# 2. DOWNLOAD PNG — روش server-side render (نهایی)
# ═══════════════════════════════════════════════════════════════

vm = ROOT / 'resources' / 'views' / 'livewire' / 'certificates' / 'view-modal.blade.php'
if vm.exists():
    txt = vm.read_text(encoding='utf-8')

    # حذف اسکریپت‌های قدیمی
    txt = re.sub(
        r'<script[^>]*html2canvas[^>]*></script>\s*<script>.*?</script>',
        '',
        txt,
        flags=re.DOTALL
    )

    # ★ روش جدید: باز کردن تب جدید با کارت خالص، سپس کاربر راست‌کلیک → Save
    NEW_SCRIPT = '''
<script>
window.downloadCertModal = function() {
    var certId = {{ $certificate->id ?? 0 }};
    if (!certId) { alert('شناسنامه پیدا نشد'); return; }
    // ★ باز کردن صفحه رندر در تب جدید
    var w = window.open('/certificates/' + certId + '/render?download=1', '_blank', 'width=900,height=900');
    if (!w) { alert('پاپ‌آپ بلاک شده — لطفا اجازه بده'); }
};
</script>
'''

    last = txt.rfind('</div>')
    if last > 0:
        txt = txt[:last] + '</div>\n' + NEW_SCRIPT
    else:
        txt += NEW_SCRIPT

    vm.write_text(txt, encoding='utf-8')
    print("[OK] view-modal - download جدید")


# ═══════════════════════════════════════════════════════════════
# 3. ROUTE — render با پارامتر download
# ═══════════════════════════════════════════════════════════════

routes = ROOT / 'routes' / 'web.php'
if routes.exists():
    txt = routes.read_text(encoding='utf-8')

    # پیدا و جایگزینی بلوک render
    old_render = """Route::get('/render/{certificate}', function (\\App\\Models\\Certificate $certificate) {
            $html = \\App\\Services\\CertRenderer::renderHtml($certificate);
            return response($html, 200)->header('Content-Type', 'text/html; charset=UTF-8');
        })->name('render');"""

    new_render = """Route::get('/render/{certificate}', function (\\App\\Models\\Certificate $certificate) {
            $html = \\App\\Services\\CertRenderer::renderHtml($certificate);

            $download = request('download', '0') === '1';
            if ($download) {
                // صفحه با دکمه دانلود client-side
                $html = str_replace('</body></html>', '
                    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
                    <script>
                    window.addEventListener("load", function() {
                        // ★ پاک‌سازی oklch
                        var card = document.querySelector(".certificate");
                        if (card) {
                            var all = [card].concat(Array.from(card.querySelectorAll("*")));
                            all.forEach(function(el) {
                                try {
                                    var cs = window.getComputedStyle(el);
                                    ["color","backgroundColor","borderTopColor","borderRightColor","borderBottomColor","borderLeftColor","fill","stroke"].forEach(function(p) {
                                        var v = cs[p];
                                        if (v && v.indexOf("oklch") !== -1) {
                                            el.style[p] = "rgb(150,150,150)";
                                        }
                                    });
                                } catch(e) {}
                            });

                            setTimeout(function() {
                                html2canvas(card, {
                                    scale: 3,
                                    backgroundColor: "#fffef9",
                                    useCORS: true,
                                    allowTaint: true,
                                    logging: false
                                }).then(function(canvas) {
                                    var a = document.createElement("a");
                                    a.download = "certificate-' . $certificate->code . '.png";
                                    a.href = canvas.toDataURL("image/png");
                                    a.click();
                                    document.getElementById("dl-status").innerHTML = "✅ ذخیره شد — می‌توانید تب را ببندید";
                                }).catch(function(e) {
                                    document.getElementById("dl-status").innerHTML = "❌ " + e.message;
                                });
                            }, 1500);
                        }
                    });
                    </script>
                    <div id="dl-status" style="position:fixed;bottom:20px;left:20px;background:#16a34a;color:#fff;padding:12px 20px;border-radius:10px;font-family:Vazirmatn;font-weight:700;z-index:9999">⏳ در حال آماده‌سازی دانلود...</div>
                </body></html>', $html);
            }

            return response($html, 200)->header('Content-Type', 'text/html; charset=UTF-8');
        })->name('render');"""

    if old_render in txt:
        txt = txt.replace(old_render, new_render)
        routes.write_text(txt, encoding='utf-8')
        print("[OK] routes - render با download")


# ═══════════════════════════════════════════════════════════════
# 4. SETTINGS BLADE — اضافه کردن بخش fetch + import
# ═══════════════════════════════════════════════════════════════

sv = ROOT / 'resources' / 'views' / 'livewire' / 'settings' / 'index.blade.php'
if sv.exists():
    txt = sv.read_text(encoding='utf-8')

    # پیدا کردن بخش stones و اضافه کردن fetch+import قبل از آن
    marker = '{{-- ═══════════ سنگ و فلز ═══════════ --}}'

    FETCH_IMPORT = '''
        {{-- ═══════════ Fetch + Import سنگ‌ها ═══════════ --}}
        @if($tab === 'stones')

            {{-- Fetch از سایت --}}
            <div class="sg-settings-card" style="margin-bottom:14px;background:linear-gradient(135deg,#eff6ff,#dbeafe);border-color:#3b82f6">
                <h3 style="color:#1e40af">🌐 دریافت سنگ‌ها از سایت</h3>
                <p style="font-size:12px;color:#1e40af;margin:0 0 12px;opacity:.85">
                    محصولات را از ووکامرس می‌خواند و سنگ‌ها/فلزات موجود در نام و ویژگی‌های آن‌ها را استخراج می‌کند
                </p>

                <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center">
                    <label style="font-size:12px;font-weight:700;color:#1e40af">تعداد محصولات:</label>
                    <input type="number" wire:model="fetch_limit" min="50" max="1000" step="50"
                           style="width:100px;padding:7px 10px;border:1.5px solid #93c5fd;border-radius:6px;font-family:monospace;text-align:center">

                    <button type="button" wire:click="fetchStonesFromWoo"
                            wire:loading.attr="disabled"
                            style="padding:9px 22px;background:linear-gradient(135deg,#3b82f6,#1e40af);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">
                        <span wire:loading.remove wire:target="fetchStonesFromWoo">🌐 دریافت از سایت</span>
                        <span wire:loading wire:target="fetchStonesFromWoo">⏳ در حال دریافت...</span>
                    </button>
                </div>

                @if($fetch_status)
                    <div style="margin-top:10px;padding:8px 12px;border-radius:6px;font-size:12px;font-weight:700;
                        background:{{ str_starts_with($fetch_status, '✅') ? '#d1fae5' : (str_starts_with($fetch_status, '⏳') ? '#dbeafe' : '#fee2e2') }};
                        color:{{ str_starts_with($fetch_status, '✅') ? '#065f46' : (str_starts_with($fetch_status, '⏳') ? '#1e40af' : '#991b1b') }}">
                        {{ $fetch_status }}
                    </div>
                @endif
            </div>

            {{-- JSON Import --}}
            <div class="sg-settings-card" style="margin-bottom:14px;background:linear-gradient(135deg,#fef3c7,#fde68a);border-color:#d97706">
                <h3 style="color:#78350f">📥 ایمپورت سنگ‌ها از JSON</h3>

                <details style="margin-bottom:10px">
                    <summary style="cursor:pointer;font-size:12px;font-weight:700;color:#78350f;padding:6px 0">
                        📋 فرمت JSON مورد قبول (کلیک کن)
                    </summary>

                    <div style="background:#fff;border:1px solid #fbbf24;border-radius:8px;padding:12px;margin-top:8px;direction:ltr;font-family:monospace;font-size:11px;white-space:pre-wrap;overflow-x:auto;max-height:300px">
{
  "stones": [
    {
      "name": "فیروزه عجمی",
      "en": "Turquoise Ajami",
      "origin": "نیشابور",
      "flag": "ir",
      "icon": "💠"
    },
    {
      "name": "عقیق یمانی",
      "en": "Yemeni Agate",
      "origin": "یمن",
      "flag": "ye",
      "icon": "🔴"
    }
  ]
}
                    </div>

                    <div style="margin-top:10px;font-size:11px;color:#78350f;line-height:1.8">
                        <b>راهنما:</b><br>
                        • <code>stones</code> — آرایه‌ای از سنگ‌ها (اختیاری، می‌توانی مستقیم آرایه بفرستی)<br>
                        • <code>name</code> — نام فارسی سنگ (اجباری)<br>
                        • <code>en</code> — نام انگلیسی<br>
                        • <code>origin</code> — اصالت (مثلاً «نیشابور»)<br>
                        • <code>flag</code> — کد دو حرفی کشور (ir, ye, iq, af, za, mm, lk, co, br, au, it, eg, cn)<br>
                        • <code>icon</code> — ایموجی آیکون<br>
                        • اگر سنگی از قبل موجود باشد، <b>بروزرسانی</b> می‌شود<br>
                        • اگر جدید باشد، <b>اضافه</b> می‌شود
                    </div>
                </details>

                <textarea wire:model="json_input" rows="6" placeholder='{"stones": [{"name": "...", "en": "...", ...}]}'
                          style="width:100%;padding:10px;border:1.5px solid #fbbf24;border-radius:8px;font-family:monospace;font-size:12px;box-sizing:border-box;direction:ltr;background:#fff;resize:vertical"></textarea>

                <div style="display:flex;gap:6px;margin-top:10px;flex-wrap:wrap">
                    <button type="button" wire:click="importStonesJson"
                            wire:loading.attr="disabled"
                            style="padding:8px 18px;background:linear-gradient(135deg,#d97706,#92400e);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">
                        <span wire:loading.remove wire:target="importStonesJson">📥 ایمپورت</span>
                        <span wire:loading wire:target="importStonesJson">⏳...</span>
                    </button>

                    <button type="button" wire:click="$set('json_input','')"
                            style="padding:8px 18px;background:#fff;color:#475569;border:1.5px solid #cbd5e1;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">
                        پاک کردن
                    </button>
                </div>

                @if($json_status)
                    <div style="margin-top:10px;padding:8px 12px;border-radius:6px;font-size:12px;font-weight:700;
                        background:{{ str_starts_with($json_status, '✅') ? '#d1fae5' : '#fee2e2' }};
                        color:{{ str_starts_with($json_status, '✅') ? '#065f46' : '#991b1b' }}">
                        {{ $json_status }}
                    </div>
                @endif
            </div>

            {{-- ابزارها --}}
            <div class="sg-settings-card" style="margin-bottom:14px">
                <h3>🛠️ ابزارها</h3>
                <div style="display:flex;gap:6px;flex-wrap:wrap">
                    <button type="button" wire:click="resetStonesToDefault" wire:confirm="همه سنگ‌ها به پیش‌فرض برگردند؟"
                            style="padding:7px 14px;background:#f1f5f9;color:#475569;border:1.5px solid #cbd5e1;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">
                        ↺ بازگشت به پیش‌فرض
                    </button>
                    <button type="button" wire:click="clearAllStones" wire:confirm="همه سنگ‌ها پاک شوند؟"
                            style="padding:7px 14px;background:#fee2e2;color:#dc2626;border:1.5px solid #fca5a5;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">
                        🗑️ پاک کردن همه
                    </button>
                </div>
            </div>
        @endif

'''

    if marker in txt and 'دریافت سنگ‌ها از سایت' not in txt:
        txt = txt.replace(marker, FETCH_IMPORT + marker, 1)
        sv.write_text(txt, encoding='utf-8')
        print("[OK] settings blade - fetch + import")


# ═══════════════════════════════════════════════════════════════
# 5. CREATE.PHP — برلیان از ویژگی‌های سایت
# ═══════════════════════════════════════════════════════════════

cp = ROOT / 'app' / 'Livewire' / 'Certificates' / 'Create.php'
if cp.exists():
    txt = cp.read_text(encoding='utf-8')

    # در searchBySku، attributes رو استخراج کن
    if "'attributes' =>" not in txt.split('$this->searchedProduct = [')[1].split('];')[0] if '$this->searchedProduct = [' in txt else False:
        txt = txt.replace(
            "'weight'     => (float) ($p['weight'] ?? 0),",
            """'weight'     => (float) ($p['weight'] ?? 0),
                'attributes' => array_map(fn($a) => [
                    'name' => $a['name'] ?? '',
                    'options' => $a['options'] ?? [],
                ], $p['attributes'] ?? []),
                'description'=> strip_tags($p['short_description'] ?? $p['description'] ?? ''),"""
        )

    # در autoFillFromProduct، برلیان رو استخراج کن
    if 'برلیان' not in txt.split('autoFillFromProduct')[1][:2000] if 'autoFillFromProduct' in txt else True:
        # اضافه در انتهای autoFillFromProduct قبل از بستن brace
        marker = "        // ─── فلز — معادل‌یابی با metalOptions ───"
        brilliant_code = '''        // ─── برلیان از ویژگی‌ها ───
        $attrs = $product['attributes'] ?? [];
        foreach ($attrs as $attr) {
            $an = $attr['name'] ?? '';
            if (mb_strpos($an, 'برلیان') !== false || mb_stripos($an, 'brilliant') !== false) {
                $opts = $attr['options'] ?? [];
                if (!empty($opts)) {
                    // اولین مقدار عددی
                    foreach ($opts as $opt) {
                        if (is_numeric($opt)) {
                            $this->brilliant = (string) ((int) $opt);
                            break;
                        }
                        if (preg_match('/(\\d+)/', $opt, $m)) {
                            $this->brilliant = $m[1];
                            break;
                        }
                    }
                }
            }
        }

        // اگه برلیان صفر ماند، از توضیحات بگیر
        if ($this->brilliant === '0' && !empty($product['description'])) {
            $desc = $product['description'];
            if (preg_match('/(?:برلیان|brilliant)[^\\d]*(\\d+)/iu', $desc, $m)) {
                $this->brilliant = $m[1];
            }
        }

'''
        if marker in txt:
            txt = txt.replace(marker, brilliant_code + marker, 1)

    cp.write_text(txt, encoding='utf-8')
    print("[OK] Create.php - برلیان")


print()
print("=" * 60)
print("DONE")
print("=" * 60)
print("  php artisan view:clear")
print("  php artisan optimize:clear")
print("  php artisan serve")