# -*- coding: utf-8 -*-
"""ShopGun - WooCommerce Attributes browser"""
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
# 1. Settings/Index.php — اضافه کردن متدهای Attributes
# ═══════════════════════════════════════════════════════════════

sphp = ROOT / 'app' / 'Livewire' / 'Settings' / 'Index.php'
if sphp.exists():
    txt = sphp.read_text(encoding='utf-8')

    # Properties
    if 'public array $woo_attributes' not in txt:
        txt = txt.replace(
            "public string $json_status = '';",
            """public string $json_status = '';

    // ★ WooCommerce Attributes
    public array $woo_attributes = [];
    public int $woo_stone_attribute_id = 0;
    public string $woo_stone_attribute_name = '';
    public int $woo_metal_attribute_id = 0;
    public string $woo_metal_attribute_name = '';
    public array $woo_stone_terms = [];
    public array $woo_metal_terms = [];
    public string $woo_attr_status = '';
    public bool $woo_attr_loading = false;"""
        )

    # در mount — لود مقادیر ذخیره‌شده
    if "$this->woo_stone_attribute_id = (int) AppSetting::get" not in txt:
        txt = txt.replace(
            "$this->loadStonesMetals();",
            """$this->woo_stone_attribute_id = (int) AppSetting::get('woo_stone_attribute_id', 0);
        $this->woo_stone_attribute_name = (string) AppSetting::get('woo_stone_attribute_name', '');
        $this->woo_metal_attribute_id = (int) AppSetting::get('woo_metal_attribute_id', 0);
        $this->woo_metal_attribute_name = (string) AppSetting::get('woo_metal_attribute_name', '');

        $this->loadStonesMetals();"""
        )

    # Methods
    if 'public function fetchWooAttributes' not in txt:
        methods = '''
    /* ═══════════════════════════════════════════════════════════
       ★ WOOCOMMERCE ATTRIBUTES
       ═══════════════════════════════════════════════════════════ */

    protected function wooAuth(): ?array
    {
        $url    = trim((string) AppSetting::get('commerce_url', ''));
        $key    = trim((string) AppSetting::get('commerce_key', ''));
        $secret = trim((string) AppSetting::get('commerce_secret', ''));

        if (!$url || !$key || !$secret) return null;

        $base = rtrim($url, '/');
        if (!str_contains($base, '/wp-json')) $base .= '/wp-json/wc/v3';

        return ['base' => $base, 'key' => $key, 'secret' => $secret];
    }

    /**
     * دریافت لیست ویژگی‌های سراسری ووکامرس
     */
    public function fetchWooAttributes(): void
    {
        @set_time_limit(60);
        $this->woo_attr_loading = true;
        $this->woo_attr_status = '⏳ دریافت ویژگی‌ها...';

        try {
            $auth = $this->wooAuth();
            if (!$auth) {
                $this->woo_attr_status = '❌ اطلاعات کامرس پر نشده';
                $this->woo_attr_loading = false;
                return;
            }

            $r = \\Illuminate\\Support\\Facades\\Http::withBasicAuth($auth['key'], $auth['secret'])
                ->timeout(20)
                ->connectTimeout(10)
                ->get("{$auth['base']}/products/attributes");

            if (!$r->successful()) {
                $this->woo_attr_status = '❌ خطای HTTP ' . $r->status();
                $this->woo_attr_loading = false;
                return;
            }

            $raw = $r->json() ?? [];

            $this->woo_attributes = array_map(function ($a) {
                return [
                    'id' => (int) ($a['id'] ?? 0),
                    'name' => (string) ($a['name'] ?? ''),
                    'slug' => (string) ($a['slug'] ?? ''),
                    'type' => (string) ($a['type'] ?? 'select'),
                    'order_by' => (string) ($a['order_by'] ?? 'menu_order'),
                    'has_archives' => (bool) ($a['has_archives'] ?? false),
                ];
            }, $raw);

            $this->woo_attr_status = "✅ " . count($this->woo_attributes) . " ویژگی پیدا شد";

        } catch (\\Throwable $e) {
            $this->woo_attr_status = '❌ ' . $e->getMessage();
        }

        $this->woo_attr_loading = false;
    }

    /**
     * دریافت اصطلاحات (terms) یک ویژگی
     */
    protected function fetchTermsFor(int $attrId): array
    {
        try {
            $auth = $this->wooAuth();
            if (!$auth) return [];

            $r = \\Illuminate\\Support\\Facades\\Http::withBasicAuth($auth['key'], $auth['secret'])
                ->timeout(30)
                ->connectTimeout(10)
                ->get("{$auth['base']}/products/attributes/{$attrId}/terms", [
                    'per_page' => 100,
                ]);

            if (!$r->successful()) return [];

            $raw = $r->json() ?? [];
            return array_map(function ($t) {
                return [
                    'id' => (int) ($t['id'] ?? 0),
                    'name' => (string) ($t['name'] ?? ''),
                    'slug' => (string) ($t['slug'] ?? ''),
                    'count' => (int) ($t['count'] ?? 0),
                ];
            }, $raw);

        } catch (\\Throwable $e) {
            return [];
        }
    }

    /**
     * انتخاب ویژگی برای سنگ
     */
    public function pickStoneAttribute(int $attrId): void
    {
        $this->woo_stone_attribute_id = $attrId;

        // پیدا کردن نام
        $this->woo_stone_attribute_name = '';
        foreach ($this->woo_attributes as $a) {
            if ($a['id'] === $attrId) {
                $this->woo_stone_attribute_name = $a['name'];
                break;
            }
        }

        // دریافت terms
        $this->woo_stone_terms = $this->fetchTermsFor($attrId);

        AppSetting::put('woo_stone_attribute_id', $attrId, 'commerce');
        AppSetting::put('woo_stone_attribute_name', $this->woo_stone_attribute_name, 'commerce');
        Cache::forget('app_settings_all');

        $this->woo_attr_status = "✅ ویژگی سنگ: «{$this->woo_stone_attribute_name}» با " . count($this->woo_stone_terms) . " اصطلاح";
    }

    /**
     * انتخاب ویژگی برای فلز
     */
    public function pickMetalAttribute(int $attrId): void
    {
        $this->woo_metal_attribute_id = $attrId;

        $this->woo_metal_attribute_name = '';
        foreach ($this->woo_attributes as $a) {
            if ($a['id'] === $attrId) {
                $this->woo_metal_attribute_name = $a['name'];
                break;
            }
        }

        $this->woo_metal_terms = $this->fetchTermsFor($attrId);

        AppSetting::put('woo_metal_attribute_id', $attrId, 'commerce');
        AppSetting::put('woo_metal_attribute_name', $this->woo_metal_attribute_name, 'commerce');
        Cache::forget('app_settings_all');

        $this->woo_attr_status = "✅ ویژگی فلز: «{$this->woo_metal_attribute_name}» با " . count($this->woo_metal_terms) . " اصطلاح";
    }

    /**
     * اعمال اصطلاحات انتخاب‌شده به عنوان لیست سنگ‌ها
     */
    public function applyWooTermsAsStones(): void
    {
        if (empty($this->woo_stone_terms)) {
            $this->woo_attr_status = '❌ اول یک ویژگی سنگ انتخاب کن';
            return;
        }

        $existingNames = array_column($this->cert_stones, 'name');
        $added = 0;

        foreach ($this->woo_stone_terms as $t) {
            $name = trim($t['name']);
            if ($name === '') continue;
            if (in_array($name, $existingNames, true)) continue;

            // تلاش برای تشخیص origin/flag/icon
            $meta = $this->guessStoneMeta($name);

            $this->cert_stones[] = [
                'name' => $name,
                'en' => $this->guessEnName($name),
                'origin' => $meta['origin'],
                'flag' => $meta['flag'],
                'icon' => $meta['icon'],
            ];
            $existingNames[] = $name;
            $added++;
        }

        AppSetting::put('cert_stones', $this->cert_stones, 'certificate');
        Cache::forget('app_settings_all');

        $this->woo_attr_status = "✅ {$added} سنگ از ویژگی‌های ووکامرس اضافه شد";
        $this->loadStonesMetals();
    }

    /**
     * اعمال اصطلاحات فلز
     */
    public function applyWooTermsAsMetals(): void
    {
        if (empty($this->woo_metal_terms)) {
            $this->woo_attr_status = '❌ اول یک ویژگی فلز انتخاب کن';
            return;
        }

        $existing = array_column($this->cert_metals, 'name');
        $added = 0;

        foreach ($this->woo_metal_terms as $t) {
            $name = trim($t['name']);
            if ($name === '') continue;
            if (in_array($name, $existing, true)) continue;

            $this->cert_metals[] = [
                'name' => $name,
                'en' => $name,
                'carat' => $this->guessCarat($name),
            ];
            $existing[] = $name;
            $added++;
        }

        AppSetting::put('cert_metals', $this->cert_metals, 'certificate');
        Cache::forget('app_settings_all');

        $this->woo_attr_status = "✅ {$added} فلز اضافه شد";
        $this->loadStonesMetals();
    }

    /**
     * حدس origin/flag/icon سنگ بر اساس نام
     */
    protected function guessStoneMeta(string $name): array
    {
        $map = [
            'فیروزه' => ['origin' => 'نیشابور', 'flag' => 'ir', 'icon' => '💠'],
            'عقیق' => ['origin' => 'یمن', 'flag' => 'ye', 'icon' => '🔴'],
            'در نجف' => ['origin' => 'عراق', 'flag' => 'iq', 'icon' => '⚪'],
            'الماس' => ['origin' => 'آفریقا', 'flag' => 'za', 'icon' => '💎'],
            'یاقوت سرخ' => ['origin' => 'میانمار', 'flag' => 'mm', 'icon' => '❤️'],
            'یاقوت کبود' => ['origin' => 'سری‌لانکا', 'flag' => 'lk', 'icon' => '🔵'],
            'یاقوت' => ['origin' => 'سری‌لانکا', 'flag' => 'lk', 'icon' => '💙'],
            'زمرد' => ['origin' => 'کلمبیا', 'flag' => 'co', 'icon' => '🟢'],
            'توپاز' => ['origin' => 'برزیل', 'flag' => 'br', 'icon' => '💛'],
            'آمیتیست' => ['origin' => 'برزیل', 'flag' => 'br', 'icon' => '🟣'],
            'اوپال' => ['origin' => 'استرالیا', 'flag' => 'au', 'icon' => '🌈'],
            'مرجان' => ['origin' => 'مدیترانه', 'flag' => 'it', 'icon' => '🟠'],
            'لاجورد' => ['origin' => 'افغانستان', 'flag' => 'af', 'icon' => '💙'],
            'چشم ببر' => ['origin' => 'آفریقا', 'flag' => 'za', 'icon' => '🐯'],
            'آکوامارین' => ['origin' => 'برزیل', 'flag' => 'br', 'icon' => '💧'],
            'سیترین' => ['origin' => 'برزیل', 'flag' => 'br', 'icon' => '🍋'],
            'پریدوت' => ['origin' => 'مصر', 'flag' => 'eg', 'icon' => '🟩'],
            'مروارید' => ['origin' => 'خلیج فارس', 'flag' => 'ir', 'icon' => '⚪'],
            'حدید' => ['origin' => 'ایران', 'flag' => 'ir', 'icon' => '⚫'],
            'یشم' => ['origin' => 'چین', 'flag' => 'cn', 'icon' => '🟢'],
            'رز کوارتز' => ['origin' => 'برزیل', 'flag' => 'br', 'icon' => '🌸'],
        ];

        foreach ($map as $k => $v) {
            if (mb_strpos($name, $k) !== false) return $v;
        }

        return ['origin' => '—', 'flag' => 'ir', 'icon' => '💎'];
    }
'''
        txt = txt.replace('    public function render()', methods + '\n    public function render()', 1)

    sphp.write_text(txt, encoding='utf-8')
    print("[OK] Settings/Index.php - attributes methods")


# ═══════════════════════════════════════════════════════════════
# 2. Settings blade — اضافه کردن بخش ویژگی‌های ووکامرس
# ═══════════════════════════════════════════════════════════════

sv = ROOT / 'resources' / 'views' / 'livewire' / 'settings' / 'index.blade.php'
if sv.exists():
    txt = sv.read_text(encoding='utf-8')

    # اگه قبلاً اضافه شده، حذف کن
    if 'ویژگی‌های ووکامرس' in txt:
        # حذف bloc قبلی
        old = re.search(
            r'\{\{-- ═══════════ ویژگی‌های ووکامرس.*?@endif\s*\n',
            txt,
            flags=re.DOTALL
        )
        if old:
            txt = txt[:old.start()] + txt[old.end():]

    ATTRIBUTES_HTML = '''
        {{-- ═══════════ ویژگی‌های ووکامرس ═══════════ --}}
        @if($tab === 'stones')
            <div class="sg-settings-card" style="margin-bottom:14px;background:linear-gradient(135deg,#eef2ff,#e0e7ff);border-color:#6366f1">
                <h3 style="color:#3730a3">🌐 اتصال به ویژگی‌های ووکامرس</h3>
                <p style="font-size:12px;color:#3730a3;margin:0 0 12px;opacity:.85">
                    لیست ویژگی‌ها (Attributes) و اصطلاحات (Terms) را از سایت می‌خواند. یک ویژگی را به عنوان «سنگ» و یکی را به عنوان «فلز» انتخاب کن.
                </p>

                <button type="button" wire:click="fetchWooAttributes"
                        wire:loading.attr="disabled"
                        style="padding:9px 22px;background:linear-gradient(135deg,#6366f1,#4338ca);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">
                    <span wire:loading.remove wire:target="fetchWooAttributes">🌐 دریافت لیست ویژگی‌ها</span>
                    <span wire:loading wire:target="fetchWooAttributes">⏳ در حال دریافت...</span>
                </button>

                @if($woo_attr_status)
                    <div style="margin-top:10px;padding:8px 12px;border-radius:6px;font-size:12px;font-weight:700;
                        background:{{ str_starts_with($woo_attr_status, '✅') ? '#d1fae5' : (str_starts_with($woo_attr_status, '⏳') ? '#dbeafe' : '#fee2e2') }};
                        color:{{ str_starts_with($woo_attr_status, '✅') ? '#065f46' : (str_starts_with($woo_attr_status, '⏳') ? '#1e40af' : '#991b1b') }}">
                        {{ $woo_attr_status }}
                    </div>
                @endif

                @if(count($woo_attributes) > 0)
                    <div style="margin-top:14px">
                        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;flex-wrap:wrap;gap:8px">
                            <div style="font-size:12px;font-weight:700;color:#3730a3">
                                ویژگی‌ها ({{ \\App\\Support\\PersianNumber::toFa(count($woo_attributes)) }})
                            </div>
                            @if($woo_stone_attribute_id || $woo_metal_attribute_id)
                                <div style="font-size:11px;color:#3730a3;display:flex;gap:8px;flex-wrap:wrap">
                                    @if($woo_stone_attribute_id)
                                        <span style="background:#d1fae5;padding:3px 8px;border-radius:6px">💎 سنگ: <b>{{ $woo_stone_attribute_name }}</b></span>
                                    @endif
                                    @if($woo_metal_attribute_id)
                                        <span style="background:#d1fae5;padding:3px 8px;border-radius:6px">⚙️ فلز: <b>{{ $woo_metal_attribute_name }}</b></span>
                                    @endif
                                </div>
                            @endif
                        </div>

                        <div style="max-height:400px;overflow-y:auto;border:1px solid #c7d2fe;border-radius:8px;background:#fff">
                            <table style="width:100%;border-collapse:collapse;font-size:12px">
                                <thead style="position:sticky;top:0;background:#eef2ff;z-index:1">
                                    <tr>
                                        <th style="padding:8px;text-align:right;color:#3730a3">نام</th>
                                        <th style="padding:8px;text-align:right;color:#3730a3">slug</th>
                                        <th style="padding:8px;text-align:right;color:#3730a3">انتخاب</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    @foreach($woo_attributes as $a)
                                        <tr wire:key="woo-attr-{{ $a['id'] }}" style="border-bottom:1px solid #f1f5f9">
                                            <td style="padding:8px;font-weight:700;color:#1e293b">{{ $a['name'] }}</td>
                                            <td style="padding:8px;font-family:monospace;font-size:11px;color:#64748b" dir="ltr">{{ $a['slug'] }}</td>
                                            <td style="padding:8px">
                                                <div style="display:flex;gap:4px;flex-wrap:wrap">
                                                    <button type="button"
                                                            wire:click="pickStoneAttribute({{ $a['id'] }})"
                                                            wire:loading.attr="disabled"
                                                            style="padding:5px 10px;border:1.5px solid {{ $woo_stone_attribute_id === $a['id'] ? '#16a34a' : '#cbd5e1' }};background:{{ $woo_stone_attribute_id === $a['id'] ? '#d1fae5' : '#fff' }};color:{{ $woo_stone_attribute_id === $a['id'] ? '#065f46' : '#475569' }};border-radius:6px;font-size:11px;font-weight:700;cursor:pointer">
                                                        💎 سنگ
                                                    </button>
                                                    <button type="button"
                                                            wire:click="pickMetalAttribute({{ $a['id'] }})"
                                                            wire:loading.attr="disabled"
                                                            style="padding:5px 10px;border:1.5px solid {{ $woo_metal_attribute_id === $a['id'] ? '#16a34a' : '#cbd5e1' }};background:{{ $woo_metal_attribute_id === $a['id'] ? '#d1fae5' : '#fff' }};color:{{ $woo_metal_attribute_id === $a['id'] ? '#065f46' : '#475569' }};border-radius:6px;font-size:11px;font-weight:700;cursor:pointer">
                                                        ⚙️ فلز
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    @endforeach
                                </tbody>
                            </table>
                        </div>
                    </div>
                @endif

                {{-- اصطلاحات سنگ --}}
                @if(count($woo_stone_terms) > 0)
                    <div style="margin-top:16px;padding:12px;background:#fff;border:1.5px solid #16a34a;border-radius:10px">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;flex-wrap:wrap;gap:8px">
                            <div style="font-weight:700;color:#15803d;font-size:13px">
                                💎 اصطلاحات «{{ $woo_stone_attribute_name }}» ({{ \\App\\Support\\PersianNumber::toFa(count($woo_stone_terms)) }})
                            </div>
                            <button type="button" wire:click="applyWooTermsAsStones"
                                    wire:confirm="همه این اصطلاحات به سنگ‌های شما اضافه شوند؟"
                                    style="padding:7px 16px;background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">
                                ➕ افزودن همه به سنگ‌ها
                            </button>
                        </div>
                        <div style="max-height:250px;overflow-y:auto;display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:6px">
                            @foreach($woo_stone_terms as $t)
                                <div style="padding:6px 10px;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:6px;font-size:11px;display:flex;justify-content:space-between;align-items:center;gap:4px">
                                    <span style="font-weight:700;color:#1e293b;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ $t['name'] }}</span>
                                    @if($t['count'] > 0)
                                        <span style="background:#16a34a;color:#fff;padding:1px 6px;border-radius:8px;font-size:9px;font-weight:700">{{ $t['count'] }}</span>
                                    @endif
                                </div>
                            @endforeach
                        </div>
                    </div>
                @endif

                {{-- اصطلاحات فلز --}}
                @if(count($woo_metal_terms) > 0)
                    <div style="margin-top:16px;padding:12px;background:#fff;border:1.5px solid #0891b2;border-radius:10px">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;flex-wrap:wrap;gap:8px">
                            <div style="font-weight:700;color:#0e7490;font-size:13px">
                                ⚙️ اصطلاحات «{{ $woo_metal_attribute_name }}» ({{ \\App\\Support\\PersianNumber::toFa(count($woo_metal_terms)) }})
                            </div>
                            <button type="button" wire:click="applyWooTermsAsMetals"
                                    wire:confirm="همه این اصطلاحات به فلزات شما اضافه شوند؟"
                                    style="padding:7px 16px;background:linear-gradient(135deg,#0891b2,#0e7490);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">
                                ➕ افزودن همه به فلزات
                            </button>
                        </div>
                        <div style="max-height:200px;overflow-y:auto;display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:6px">
                            @foreach($woo_metal_terms as $t)
                                <div style="padding:6px 10px;background:#ecfeff;border:1px solid #a5f3fc;border-radius:6px;font-size:11px;display:flex;justify-content:space-between;align-items:center;gap:4px">
                                    <span style="font-weight:700;color:#1e293b;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ $t['name'] }}</span>
                                    @if($t['count'] > 0)
                                        <span style="background:#0891b2;color:#fff;padding:1px 6px;border-radius:8px;font-size:9px;font-weight:700">{{ $t['count'] }}</span>
                                    @endif
                                </div>
                            @endforeach
                        </div>
                    </div>
                @endif
            </div>
        @endif

'''

    # درج قبل از بخش Fetch قبلی
    marker = "{{-- ═══════════ Fetch + Import سنگ‌ها ═══════════ --}}"
    if marker in txt:
        txt = txt.replace(marker, ATTRIBUTES_HTML + marker, 1)
        sv.write_text(txt, encoding='utf-8')
        print("[OK] settings blade - attributes UI")
    else:
        # قبل از marker اصلی سنگ و فلز
        marker2 = '{{-- ═══════════ سنگ و فلز ═══════════ --}}'
        if marker2 in txt:
            txt = txt.replace(marker2, ATTRIBUTES_HTML + marker2, 1)
            sv.write_text(txt, encoding='utf-8')
            print("[OK] settings blade - attributes UI (alt)")


print()
print("=" * 60)
print("DONE")
print("=" * 60)
print("  php artisan view:clear")
print("  php artisan optimize:clear")
print("  php artisan serve")