# -*- coding: utf-8 -*-
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
# 1. CERTCONFIG.PHP — اضافه کردن overrideStoneOptions
# ═══════════════════════════════════════════════════════════════

cc = ROOT / 'app' / 'Support' / 'CertConfig.php'
if cc.exists():
    txt = cc.read_text(encoding='utf-8')
    if 'stones()' not in txt or 'public static function stones' not in txt:
        method = '''
    /**
     * ★ لیست سنگ‌ها از AppSetting
     */
    public static function stones(): array
    {
        try {
            if (\\Illuminate\\Support\\Facades\\Schema::hasTable('app_settings')) {
                $s = AppSetting::get('cert_stones', null);
                if (is_array($s) && !empty($s)) return $s;
            }
        } catch (\\Throwable $e) {}
        return [];
    }

    /**
     * ★ لیست فلزات از AppSetting
     */
    public static function metals(): array
    {
        try {
            if (\\Illuminate\\Support\\Facades\\Schema::hasTable('app_settings')) {
                $m = AppSetting::get('cert_metals', null);
                if (is_array($m) && !empty($m)) return $m;
            }
        } catch (\\Throwable $e) {}
        return [];
    }
'''
        txt = txt.replace('    public static function resolveUrl', method + '\n    public static function resolveUrl', 1)
        cc.write_text(txt, encoding='utf-8')
        print("[OK] CertConfig - stones()/metals()")


# ═══════════════════════════════════════════════════════════════
# 2. SETTINGS/INDEX.PHP — اضافه کردن methods سنگ/فلز
# ═══════════════════════════════════════════════════════════════

sphp = ROOT / 'app' / 'Livewire' / 'Settings' / 'Index.php'
if sphp.exists():
    txt = sphp.read_text(encoding='utf-8')

    # اضافه کردن properties
    if 'public array $cert_stones' not in txt:
        txt = txt.replace(
            "public string \$bg_image = '';",
            """public string $bg_image = '';

    // ★ سنگ و فلز
    public array $cert_stones = [];
    public array $cert_metals = [];
    public string $new_stone_name = '';
    public string $new_stone_en = '';
    public string $new_stone_origin = '';
    public string $new_stone_flag = 'ir';
    public string $new_stone_icon = '💎';
    public string $new_metal_name = '';
    public string $new_metal_en = '';
    public string $new_metal_carat = '925';
    public ?int $editing_stone_idx = null;
    public ?int $editing_metal_idx = null;"""
        )

    # mount
    if "$this->cert_stones = " not in txt:
        txt = txt.replace(
            "$this->loadTemplates();",
            """$this->loadStonesMetals();
        $this->loadTemplates();"""
        )

    # methods
    if 'public function loadStonesMetals' not in txt:
        methods = '''
    /* ═══════════════════════════════════════════════════════════
       STONES / METALS
       ═══════════════════════════════════════════════════════════ */

    protected function defaultStones(): array
    {
        return [
            ['name' => 'فیروزه عجمی',   'en' => 'Turquoise Ajami',   'origin' => 'نیشابور',   'flag' => 'ir', 'icon' => '💠'],
            ['name' => 'فیروزه شجری',   'en' => 'Turquoise Shajari', 'origin' => 'نیشابور',   'flag' => 'ir', 'icon' => '💠'],
            ['name' => 'عقیق یمانی',    'en' => 'Yemeni Agate',      'origin' => 'یمن',        'flag' => 'ye', 'icon' => '🔴'],
            ['name' => 'عقیق سلیمانی',  'en' => 'Solomoni Agate',    'origin' => 'یمن',        'flag' => 'ye', 'icon' => '❤️'],
            ['name' => 'عقیق شجر',      'en' => 'Dendritic Agate',   'origin' => 'یمن',        'flag' => 'ye', 'icon' => '🌿'],
            ['name' => 'در نجف',        'en' => 'Najaf Pearl',       'origin' => 'عراق',       'flag' => 'iq', 'icon' => '⚪'],
            ['name' => 'الماس',         'en' => 'Diamond',           'origin' => 'آفریقا',     'flag' => 'za', 'icon' => '💎'],
            ['name' => 'یاقوت سرخ',     'en' => 'Ruby',              'origin' => 'میانمار',    'flag' => 'mm', 'icon' => '❤️'],
            ['name' => 'یاقوت کبود',    'en' => 'Blue Sapphire',     'origin' => 'سری‌لانکا',  'flag' => 'lk', 'icon' => '🔵'],
            ['name' => 'زمرد',          'en' => 'Emerald',           'origin' => 'کلمبیا',     'flag' => 'co', 'icon' => '🟢'],
            ['name' => 'توپاز',         'en' => 'Topaz',             'origin' => 'برزیل',      'flag' => 'br', 'icon' => '💛'],
            ['name' => 'آمیتیست',       'en' => 'Amethyst',          'origin' => 'برزیل',      'flag' => 'br', 'icon' => '🟣'],
            ['name' => 'اوپال',         'en' => 'Opal',              'origin' => 'استرالیا',   'flag' => 'au', 'icon' => '🌈'],
            ['name' => 'مرجان',         'en' => 'Coral',             'origin' => 'مدیترانه',   'flag' => 'it', 'icon' => '🟠'],
            ['name' => 'لاجورد',        'en' => 'Lapis Lazuli',      'origin' => 'افغانستان',  'flag' => 'af', 'icon' => '💙'],
            ['name' => 'چشم ببر',       'en' => 'Tiger Eye',         'origin' => 'آفریقا',     'flag' => 'za', 'icon' => '🐯'],
            ['name' => 'آکوامارین',     'en' => 'Aquamarine',        'origin' => 'برزیل',      'flag' => 'br', 'icon' => '💧'],
            ['name' => 'سیترین',       'en' => 'Citrine',           'origin' => 'برزیل',      'flag' => 'br', 'icon' => '🍋'],
            ['name' => 'پریدوت',       'en' => 'Peridot',           'origin' => 'مصر',        'flag' => 'eg', 'icon' => '🟩'],
            ['name' => 'مروارید',       'en' => 'Pearl',             'origin' => 'خلیج فارس',  'flag' => 'ir', 'icon' => '⚪'],
            ['name' => 'فیروزه',        'en' => 'Turquoise',         'origin' => 'نیشابور',   'flag' => 'ir', 'icon' => '💠'],
            ['name' => 'عقیق',          'en' => 'Agate',             'origin' => 'یمن',        'flag' => 'ye', 'icon' => '🔴'],
            ['name' => 'یاقوت',         'en' => 'Sapphire',          'origin' => 'سری‌لانکا',  'flag' => 'lk', 'icon' => '💙'],
        ];
    }

    protected function defaultMetals(): array
    {
        return [
            ['name' => 'نقره 925',      'en' => 'Silver 925',      'carat' => '925'],
            ['name' => 'نقره 999',      'en' => 'Fine Silver',     'carat' => '999'],
            ['name' => 'طلا 18K',       'en' => 'Gold 18K',        'carat' => '750'],
            ['name' => 'طلا 21K',       'en' => 'Gold 21K',        'carat' => '875'],
            ['name' => 'طلا 22K',       'en' => 'Gold 22K',        'carat' => '916'],
            ['name' => 'طلا 24K',       'en' => 'Gold 24K',        'carat' => '999'],
            ['name' => 'پلاتین 950',    'en' => 'Platinum 950',    'carat' => '950'],
            ['name' => 'استیل',         'en' => 'Stainless Steel', 'carat' => '-'],
            ['name' => 'رودیم',         'en' => 'Rhodium',         'carat' => '-'],
            ['name' => 'پالادیوم',      'en' => 'Palladium',       'carat' => '-'],
        ];
    }

    public function loadStonesMetals(): void
    {
        $s = AppSetting::get('cert_stones', null);
        $this->cert_stones = is_array($s) && !empty($s) ? $s : $this->defaultStones();

        $m = AppSetting::get('cert_metals', null);
        $this->cert_metals = is_array($m) && !empty($m) ? $m : $this->defaultMetals();
    }

    public function addStone(): void
    {
        $name = trim($this->new_stone_name);
        if ($name === '') {
            $this->dispatch('notify', type: 'error', message: 'نام سنگ الزامی است');
            return;
        }

        $stone = [
            'name'   => $name,
            'en'     => trim($this->new_stone_en) ?: $name,
            'origin' => trim($this->new_stone_origin) ?: '—',
            'flag'   => $this->new_stone_flag ?: 'ir',
            'icon'   => $this->new_stone_icon ?: '💎',
        ];

        if ($this->editing_stone_idx !== null && isset($this->cert_stones[$this->editing_stone_idx])) {
            $this->cert_stones[$this->editing_stone_idx] = $stone;
            $msg = "سنگ «{$name}» ویرایش شد";
        } else {
            $this->cert_stones[] = $stone;
            $msg = "سنگ «{$name}» اضافه شد";
        }

        AppSetting::put('cert_stones', $this->cert_stones, 'certificate');
        Cache::forget('app_settings_all');

        // Reset
        $this->new_stone_name = '';
        $this->new_stone_en = '';
        $this->new_stone_origin = '';
        $this->new_stone_flag = 'ir';
        $this->new_stone_icon = '💎';
        $this->editing_stone_idx = null;

        $this->loadStonesMetals();
        $this->dispatch('notify', type: 'success', message: $msg);
    }

    public function editStone(int $idx): void
    {
        if (!isset($this->cert_stones[$idx])) return;
        $s = $this->cert_stones[$idx];
        $this->editing_stone_idx = $idx;
        $this->new_stone_name = $s['name'] ?? '';
        $this->new_stone_en = $s['en'] ?? '';
        $this->new_stone_origin = $s['origin'] ?? '';
        $this->new_stone_flag = $s['flag'] ?? 'ir';
        $this->new_stone_icon = $s['icon'] ?? '💎';
    }

    public function removeStone(int $idx): void
    {
        if (!isset($this->cert_stones[$idx])) return;
        array_splice($this->cert_stones, $idx, 1);
        AppSetting::put('cert_stones', $this->cert_stones, 'certificate');
        Cache::forget('app_settings_all');
        $this->loadStonesMetals();
        $this->dispatch('notify', type: 'success', message: 'حذف شد');
    }

    public function addMetal(): void
    {
        $name = trim($this->new_metal_name);
        if ($name === '') {
            $this->dispatch('notify', type: 'error', message: 'نام فلز الزامی است');
            return;
        }

        $metal = [
            'name'  => $name,
            'en'    => trim($this->new_metal_en) ?: $name,
            'carat' => trim($this->new_metal_carat) ?: '925',
        ];

        if ($this->editing_metal_idx !== null && isset($this->cert_metals[$this->editing_metal_idx])) {
            $this->cert_metals[$this->editing_metal_idx] = $metal;
        } else {
            $this->cert_metals[] = $metal;
        }

        AppSetting::put('cert_metals', $this->cert_metals, 'certificate');
        Cache::forget('app_settings_all');

        $this->new_metal_name = '';
        $this->new_metal_en = '';
        $this->new_metal_carat = '925';
        $this->editing_metal_idx = null;

        $this->loadStonesMetals();
        $this->dispatch('notify', type: 'success', message: 'ذخیره شد');
    }

    public function editMetal(int $idx): void
    {
        if (!isset($this->cert_metals[$idx])) return;
        $m = $this->cert_metals[$idx];
        $this->editing_metal_idx = $idx;
        $this->new_metal_name = $m['name'] ?? '';
        $this->new_metal_en = $m['en'] ?? '';
        $this->new_metal_carat = $m['carat'] ?? '925';
    }

    public function removeMetal(int $idx): void
    {
        if (!isset($this->cert_metals[$idx])) return;
        array_splice($this->cert_metals, $idx, 1);
        AppSetting::put('cert_metals', $this->cert_metals, 'certificate');
        Cache::forget('app_settings_all');
        $this->loadStonesMetals();
        $this->dispatch('notify', type: 'success', message: 'حذف شد');
    }

    public function cancelStoneEdit(): void
    {
        $this->editing_stone_idx = null;
        $this->new_stone_name = '';
        $this->new_stone_en = '';
        $this->new_stone_origin = '';
        $this->new_stone_flag = 'ir';
        $this->new_stone_icon = '💎';
    }
'''
        txt = txt.replace('    public function render()', methods + '\n    public function render()', 1)

    sphp.write_text(txt, encoding='utf-8')
    print("[OK] Settings/Index.php - stones/metals")


# ═══════════════════════════════════════════════════════════════
# 3. SETTINGS BLADE — اضافه کردن تب سنگ/فلز
# ═══════════════════════════════════════════════════════════════

sv = ROOT / 'resources' / 'views' / 'livewire' / 'settings' / 'index.blade.php'
if sv.exists():
    txt = sv.read_text(encoding='utf-8')

    # اضافه کردن tab به لیست
    if "'stones'" not in txt.split('sg-settings-tabs')[1].split('</div>')[0]:
        txt = txt.replace(
            "'labels'      => ['🎨', 'ویرایشگر برچسب', false],",
            "'stones'      => ['💠', 'سنگ/فلز', false],\n            'labels'      => ['🎨', 'ویرایشگر برچسب', false],"
        )

    # بخش محتوای stones — قبل از labels یا بعد از certificate
    STONES_HTML = '''
        {{-- ═══════════ سنگ و فلز ═══════════ --}}
        @if($tab === 'stones')
            <div style="display:grid;grid-template-columns:1fr;gap:14px">

                {{-- سنگ‌ها --}}
                <div class="sg-settings-card">
                    <h3>💎 سنگ‌ها ({{ \App\Support\PersianNumber::toFa(count($cert_stones)) }})</h3>

                    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:8px;margin-bottom:16px">
                        @foreach($cert_stones as $i => $s)
                            <div style="position:relative;background:#fff;border:2px solid #e2e8f0;border-radius:10px;padding:8px;text-align:center">
                                <div style="font-size:24px;margin-bottom:4px">{{ $s['icon'] ?? '💎' }}</div>
                                <div style="font-size:11px;font-weight:700;color:#1e293b">{{ $s['name'] }}</div>
                                <div style="font-size:9px;color:#94a3b8">{{ $s['origin'] ?? '' }}</div>
                                <div style="display:flex;gap:3px;margin-top:6px;justify-content:center">
                                    <button type="button" wire:click="editStone({{ $i }})"
                                            style="background:#e0e7ff;color:#3730a3;border:none;width:24px;height:24px;border-radius:6px;font-size:11px;cursor:pointer;font-weight:700">✏️</button>
                                    <button type="button" wire:click="removeStone({{ $i }})" wire:confirm="حذف شود؟"
                                            style="background:#fee2e2;color:#dc2626;border:none;width:24px;height:24px;border-radius:6px;font-size:11px;cursor:pointer">🗑️</button>
                                </div>
                            </div>
                        @endforeach
                    </div>

                    <h3 style="margin-top:16px">{{ $editing_stone_idx !== null ? '✏️ ویرایش سنگ' : '➕ افزودن سنگ جدید' }}</h3>
                    <div class="form-grid">
                        <div class="field col-6">
                            <label>نام فارسی</label>
                            <input type="text" wire:model="new_stone_name" placeholder="مثلاً: فیروزه عجمی">
                        </div>
                        <div class="field col-6">
                            <label>نام انگلیسی</label>
                            <input type="text" wire:model="new_stone_en" dir="ltr" placeholder="Turquoise Ajami">
                        </div>
                        <div class="field col-4">
                            <label>اصالت</label>
                            <input type="text" wire:model="new_stone_origin" placeholder="نیشابور">
                        </div>
                        <div class="field col-4">
                            <label>پرچم</label>
                            <select wire:model="new_stone_flag" style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px">
                                <option value="ir">🇮🇷 ایران</option>
                                <option value="ye">🇾🇪 یمن</option>
                                <option value="iq">🇮🇶 عراق</option>
                                <option value="af">🇦🇫 افغانستان</option>
                                <option value="za">🇿🇦 آفریقا</option>
                                <option value="mm">🇲🇲 میانمار</option>
                                <option value="co">🇨🇴 کلمبیا</option>
                                <option value="lk">🇱🇰 سری‌لانکا</option>
                                <option value="br">🇧🇷 برزیل</option>
                                <option value="au">🇦🇺 استرالیا</option>
                                <option value="it">🇮🇹 ایتالیا</option>
                                <option value="eg">🇪🇬 مصر</option>
                            </select>
                        </div>
                        <div class="field col-4">
                            <label>آیکون</label>
                            <input type="text" wire:model="new_stone_icon" style="text-align:center;font-size:20px">
                        </div>
                    </div>

                    <div style="display:flex;gap:6px;margin-top:10px">
                        <button type="button" wire:click="addStone" class="btn btn-primary">
                            {{ $editing_stone_idx !== null ? '✏️ ویرایش' : '➕ افزودن' }}
                        </button>
                        @if($editing_stone_idx !== null)
                            <button type="button" wire:click="cancelStoneEdit" class="btn btn-ghost">انصراف</button>
                        @endif
                    </div>
                </div>

                {{-- فلزات --}}
                <div class="sg-settings-card">
                    <h3>⚙️ فلزات ({{ \App\Support\PersianNumber::toFa(count($cert_metals)) }})</h3>

                    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:8px;margin-bottom:16px">
                        @foreach($cert_metals as $i => $m)
                            <div style="background:#f8fafc;border:1.5px solid #e2e8f0;border-radius:8px;padding:10px;display:flex;align-items:center;justify-content:space-between">
                                <div>
                                    <div style="font-weight:700;font-size:12px;color:#1e293b">{{ $m['name'] }}</div>
                                    <div style="font-size:10px;color:#94a3b8" dir="ltr">{{ $m['carat'] ?? '' }}</div>
                                </div>
                                <div style="display:flex;gap:3px">
                                    <button type="button" wire:click="editMetal({{ $i }})"
                                            style="background:#e0e7ff;color:#3730a3;border:none;width:22px;height:22px;border-radius:5px;font-size:10px;cursor:pointer">✏️</button>
                                    <button type="button" wire:click="removeMetal({{ $i }})" wire:confirm="حذف شود؟"
                                            style="background:#fee2e2;color:#dc2626;border:none;width:22px;height:22px;border-radius:5px;font-size:10px;cursor:pointer">🗑️</button>
                                </div>
                            </div>
                        @endforeach
                    </div>

                    <h3 style="margin-top:16px">{{ $editing_metal_idx !== null ? '✏️ ویرایش فلز' : '➕ افزودن فلز' }}</h3>
                    <div class="form-grid">
                        <div class="field col-4">
                            <label>نام فارسی</label>
                            <input type="text" wire:model="new_metal_name" placeholder="نقره 925">
                        </div>
                        <div class="field col-4">
                            <label>نام انگلیسی</label>
                            <input type="text" wire:model="new_metal_en" dir="ltr" placeholder="Silver 925">
                        </div>
                        <div class="field col-4">
                            <label>عیار</label>
                            <input type="text" wire:model="new_metal_carat" dir="ltr" placeholder="925">
                        </div>
                    </div>
                    <button type="button" wire:click="addMetal" class="btn btn-primary" style="margin-top:10px">
                        {{ $editing_metal_idx !== null ? '✏️ ویرایش' : '➕ افزودن' }}
                    </button>
                </div>
            </div>
        @endif
'''

    # درج قبل از labels
    marker = "        {{-- ویرایشگر برچسب --}}"
    if marker in txt and "{{-- ═══════════ سنگ و فلز ═══════════ --}}" not in txt:
        txt = txt.replace(marker, STONES_HTML + '\n' + marker, 1)
    elif "{{-- ═══════════ سنگ و فلز ═══════════ --}}" not in txt:
        # قبل از health
        marker2 = "        {{-- سلامت --}}"
        if marker2 in txt:
            txt = txt.replace(marker2, STONES_HTML + '\n' + marker2, 1)

    sv.write_text(txt, encoding='utf-8')
    print("[OK] settings blade - stones tab")


# ═══════════════════════════════════════════════════════════════
# 4. CREATE.PHP — سنگ/فلز از AppSetting + timeout بالاتر
# ═══════════════════════════════════════════════════════════════

cp = ROOT / 'app' / 'Livewire' / 'Certificates' / 'Create.php'
if cp.exists():
    txt = cp.read_text(encoding='utf-8')

    # mount برای پر کردن stoneOptions از AppSetting
    if 'public function mount' not in txt:
        mount_method = '''
    public function mount(): void
    {
        // ★ بارگذاری سنگ/فلز از تنظیمات
        $savedStones = \\App\\Models\\AppSetting::get('cert_stones', null);
        if (is_array($savedStones) && !empty($savedStones)) {
            $this->stoneOptions = $savedStones;
        }

        $savedMetals = \\App\\Models\\AppSetting::get('cert_metals', null);
        if (is_array($savedMetals) && !empty($savedMetals)) {
            $this->metalOptions = $savedMetals;
        }
    }

'''
        txt = txt.replace('    #[On(\'open-cert-form\')]', mount_method + '    #[On(\'open-cert-form\')]', 1)

    # ★ timeout بالاتر + retry
    txt = txt.replace(
        "$r = Http::withBasicAuth($key, $secret)\n                ->timeout(15)\n                ->get(\"{$base}/products\", ['sku' => $sku, 'per_page' => 1]);",
        "$r = Http::withBasicAuth($key, $secret)\n                ->timeout(30)\n                ->connectTimeout(15)\n                ->retry(2, 2000)\n                ->get(\"{$base}/products\", ['sku' => $sku, 'per_page' => 1]);"
    )

    # اگه پیدا نشد، جستجوی fallback با search
    old_fail = '''            if (empty($json) || !is_array($json)) {
                $this->searchStatus = "❌ محصولی با کد «{$sku}» پیدا نشد";
                $this->searching = false;
                return;
            }

            $p = $json[0];'''
    
    new_fail = '''            // اگه با sku دقیق پیدا نشد، با search امتحان کن
            if (empty($json) || !is_array($json)) {
                $this->searchStatus = '⏳ با sku دقیق نبود — جستجوی سراسری...';
                $r2 = Http::withBasicAuth($key, $secret)
                    ->timeout(30)->connectTimeout(15)
                    ->get("{$base}/products", ['search' => $sku, 'per_page' => 5]);
                if ($r2->successful()) {
                    $json = $r2->json();
                }
            }

            if (empty($json) || !is_array($json)) {
                $this->searchStatus = "❌ محصولی با کد «{$sku}» پیدا نشد";
                $this->searching = false;
                return;
            }

            $p = $json[0];'''
    
    if old_fail in txt:
        txt = txt.replace(old_fail, new_fail, 1)
        print("[OK] Create.php - fallback search")

    cp.write_text(txt, encoding='utf-8')
    print("[OK] Create.php - mount + timeout")


# ═══════════════════════════════════════════════════════════════
# 5. DOWNLOAD PNG — بازنویسی رادیکال
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

    # ★ روش جدید: کپی مستقیم از DOM، بدون fetch
    NEW_SCRIPT = '''
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script>
async function downloadCertModal() {
    try {
        var source = document.querySelector('#cert-card-area .certificate');
        if (!source) { alert('کارت پیدا نشد در DOM'); return; }

        // ★ clone با ابعاد اصلی
        var w = source.offsetWidth || 600;
        var h = source.offsetHeight || 600;

        var clone = source.cloneNode(true);
        clone.style.transform = 'none';
        clone.style.boxShadow = 'none';
        clone.style.margin = '0';
        clone.style.width = w + 'px';
        clone.style.height = h + 'px';

        // ★ کانتینر مخفی
        var wrap = document.createElement('div');
        wrap.style.cssText = 'position:fixed;left:-99999px;top:0;background:#fffef9;padding:0;margin:0;width:' + w + 'px;height:' + h + 'px;overflow:hidden;z-index:-1';
        wrap.appendChild(clone);
        document.body.appendChild(wrap);

        // ★ حذف oklch
        var allEls = [clone, ...clone.querySelectorAll('*')];
        allEls.forEach(function(el) {
            var cs = window.getComputedStyle(el);
            ['color','backgroundColor','borderTopColor','borderRightColor','borderBottomColor','borderLeftColor','outlineColor','fill','stroke'].forEach(function(prop) {
                var val = cs[prop];
                if (val && val.includes('oklch')) {
                    el.style[prop] = '#888888';
                }
            });
        });

        // ★ منتظر تصاویر
        var imgs = clone.querySelectorAll('img');
        var promises = Array.from(imgs).map(function(img) {
            if (img.complete) return Promise.resolve();
            return new Promise(function(resolve) {
                img.onload = resolve;
                img.onerror = resolve;
                setTimeout(resolve, 3000);
            });
        });
        await Promise.all(promises);

        // ★ اجرا html2canvas
        var canvas = await html2canvas(clone, {
            scale: 3,
            backgroundColor: '#fffef9',
            useCORS: true,
            allowTaint: true,
            logging: false,
            width: w,
            height: h,
            windowWidth: w,
            windowHeight: h,
            imageTimeout: 0
        });

        wrap.remove();

        // ★ دانلود
        var dataUrl = canvas.toDataURL('image/png');
        var a = document.createElement('a');
        a.download = 'certificate-{{ $certificate->code ?? "card" }}.png';
        a.href = dataUrl;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);

    } catch (err) {
        console.error('Download error:', err);
        alert('خطا در دانلود:\\n' + err.message);
    }
}

// دکمه دانلود با onclick
window.downloadCertModal = downloadCertModal;
</script>
'''

    # درج قبل از بستن آخرین div
    last_div = txt.rfind('</div>')
    if last_div > 0:
        txt = txt[:last_div] + '</div>\n' + NEW_SCRIPT
    else:
        txt += NEW_SCRIPT

    vm.write_text(txt, encoding='utf-8')
    print("[OK] view-modal - download جدید")


# ═══════════════════════════════════════════════════════════════
# 6. حذف route table و فایل‌های PowerGrid
# ═══════════════════════════════════════════════════════════════

routes = ROOT / 'routes' / 'web.php'
if routes.exists():
    txt = routes.read_text(encoding='utf-8')
    txt = re.sub(r"\s*Route::get\('/table'[^;]*;\s*", '\n        ', txt)
    routes.write_text(txt, encoding='utf-8')
    print("[OK] routes - حذف /table")


# ═══════════════════════════════════════════════════════════════
# 7. CertConfig — override for stones
# ═══════════════════════════════════════════════════════════════

print()
print("=" * 60)
print("DONE")
print("=" * 60)
print("  php artisan view:clear")
print("  php artisan optimize:clear")
print("  php artisan serve")