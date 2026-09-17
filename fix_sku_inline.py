# -*- coding: utf-8 -*-
"""ShopGun - SKU search داخل فرم Create"""
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
# 1. CREATE.PHP — با SKU search
# ═══════════════════════════════════════════════════════════════

CREATE = r'''<?php

namespace App\Livewire\Certificates;

use App\Models\AppSetting;
use App\Models\Certificate;
use App\Models\Customer;
use App\Models\Order;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use Illuminate\Support\Facades\Storage;
use Livewire\Attributes\On;
use Livewire\Component;
use Livewire\WithFileUploads;

class Create extends Component
{
    use WithFileUploads;

    public int $step = 1;
    public bool $show = false;
    public ?int $editingId = null;

    // ★ SKU Search
    public string $skuSearch = '';
    public string $searchStatus = '';
    public bool $searching = false;
    public ?array $searchedProduct = null;
    public ?string $productImageUrl = null;

    // سنگ
    public string $stoneName   = '';
    public string $stoneEn     = '';
    public string $stoneOrigin = 'نیشابور';
    public string $stoneFlag   = 'ir';
    public string $stoneIcon   = '💠';
    public string $metal       = 'نقره 925';
    public string $metalEn     = 'Silver 925';
    public string $metalCarat  = '925';

    public string $length    = '';
    public string $width     = '';
    public string $weight    = '';
    public string $brilliant = '0';

    public ?int $customerId = null;
    public ?int $orderId    = null;

    public $image = null;

    public array $stoneOptions = [
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
    ];

    public array $metalOptions = [
        ['name' => 'نقره 925',      'en' => 'Silver 925',      'carat' => '925'],
        ['name' => 'نقره 999',      'en' => 'Fine Silver',     'carat' => '999'],
        ['name' => 'طلا 18K',       'en' => 'Gold 18K',        'carat' => '750'],
        ['name' => 'طلا 21K',       'en' => 'Gold 21K',        'carat' => '875'],
        ['name' => 'طلا 22K',       'en' => 'Gold 22K',        'carat' => '916'],
        ['name' => 'طلا 24K',       'en' => 'Gold 24K',        'carat' => '999'],
        ['name' => 'پلاتین 950',    'en' => 'Platinum 950',    'carat' => '950'],
        ['name' => 'استیل',         'en' => 'Stainless Steel', 'carat' => '-'],
    ];

    #[On('open-cert-form')]
    public function openModal($certId = null): void
    {
        $this->resetForm();
        $this->editingId = is_numeric($certId) ? (int)$certId : null;

        if ($this->editingId) {
            $c = Certificate::find($this->editingId);
            if ($c) {
                $this->stoneName   = (string) ($c->stone_name ?? '');
                $this->stoneEn     = (string) ($c->stone_en ?? '');
                $this->stoneOrigin = (string) ($c->stone_origin ?? 'نیشابور');
                $this->stoneFlag   = (string) ($c->stone_flag ?? 'ir');
                $this->metal       = (string) ($c->metal ?? 'نقره 925');
                $this->metalEn     = (string) ($c->metal_en ?? '');
                $this->metalCarat  = (string) ($c->metal_carat ?? '');
                $this->length      = (string) ($c->length ?? '');
                $this->width       = (string) ($c->width ?? '');
                $this->weight      = (string) ($c->weight ?? '');
                $this->brilliant   = (string) ($c->brilliant ?? '0');
                $this->customerId  = $c->customer_id ? (int)$c->customer_id : null;
                $this->orderId     = $c->order_id ? (int)$c->order_id : null;
            }
        }

        $this->step = 1;
        $this->show = true;
    }

    public function closeModal(): void
    {
        $this->show = false;
        $this->resetForm();
    }

    protected function resetForm(): void
    {
        $this->step = 1;
        $this->skuSearch = '';
        $this->searchStatus = '';
        $this->searching = false;
        $this->searchedProduct = null;
        $this->productImageUrl = null;
        $this->stoneName = '';
        $this->stoneEn = '';
        $this->stoneOrigin = 'نیشابور';
        $this->stoneFlag = 'ir';
        $this->stoneIcon = '💠';
        $this->metal = 'نقره 925';
        $this->metalEn = 'Silver 925';
        $this->metalCarat = '925';
        $this->length = '';
        $this->width = '';
        $this->weight = '';
        $this->brilliant = '0';
        $this->customerId = null;
        $this->orderId = null;
        $this->image = null;
        $this->editingId = null;
        $this->resetErrorBag();
    }

    /* ═══════════════════════════════════════════════════════════
       ★ SKU SEARCH از سایت
       ═══════════════════════════════════════════════════════════ */
    public function searchBySku(): void
    {
        $sku = trim($this->skuSearch);
        if ($sku === '') {
            $this->searchStatus = '❌ کد SKU را وارد کنید';
            return;
        }

        $this->searching = true;
        $this->searchStatus = '⏳ در حال جستجو در سایت...';
        $this->searchedProduct = null;
        $this->productImageUrl = null;

        try {
            $url    = trim((string) AppSetting::get('commerce_url', ''));
            $key    = trim((string) AppSetting::get('commerce_key', ''));
            $secret = trim((string) AppSetting::get('commerce_secret', ''));

            if (!$url || !$key || !$secret) {
                $this->searchStatus = '❌ تنظیمات کامرس پر نشده — به تنظیمات → کامرس برو';
                $this->searching = false;
                return;
            }

            $base = rtrim($url, '/');
            if (!str_contains($base, '/wp-json')) $base .= '/wp-json/wc/v3';

            // جستجوی دقیق SKU
            $r = Http::withBasicAuth($key, $secret)
                ->timeout(15)
                ->get("{$base}/products", ['sku' => $sku, 'per_page' => 1]);

            if (!$r->successful()) {
                $this->searchStatus = '❌ خطای HTTP ' . $r->status();
                $this->searching = false;
                return;
            }

            $json = $r->json();
            if (empty($json) || !is_array($json)) {
                $this->searchStatus = "❌ محصولی با کد «{$sku}» در سایت پیدا نشد";
                $this->searching = false;
                return;
            }

            $p = $json[0];

            $this->searchedProduct = [
                'id'    => (int) ($p['id'] ?? 0),
                'sku'   => (string) ($p['sku'] ?? ''),
                'name'  => (string) ($p['name'] ?? ''),
                'price' => (float) ($p['price'] ?? 0),
                'image' => $p['images'][0]['src'] ?? null,
                'weight'=> (float) ($p['weight'] ?? 0),
            ];

            $this->productImageUrl = $this->searchedProduct['image'];

            // ★ پر کردن خودکار فرم
            $this->autoFillFromProduct($this->searchedProduct);

            $this->searchStatus = '✅ محصول پیدا شد: ' . $this->searchedProduct['name'];
            $this->step = 2; // برو به مرحله مشخصات

        } catch (\Throwable $e) {
            $this->searchStatus = '❌ ' . $e->getMessage();
            Log::error('SKU Search: ' . $e->getMessage());
        }

        $this->searching = false;
    }

    protected function autoFillFromProduct(array $product): void
    {
        $name = $product['name'] ?? '';

        // ─── وزن ───
        if (!empty($product['weight'])) {
            $this->weight = (string) $product['weight'];
        } elseif (preg_match('/([\d.]+)\s*(گرم|گرمی|gram|g)/u', $name, $m)) {
            $this->weight = $m[1];
        }

        // ─── سنگ ───
        $stoneKeywords = [
            ['fa' => 'فیروزه', 'en' => 'Turquoise',      'origin' => 'نیشابور',   'flag' => 'ir'],
            ['fa' => 'عقیق',   'en' => 'Agate',          'origin' => 'یمن',        'flag' => 'ye'],
            ['fa' => 'الماس',  'en' => 'Diamond',        'origin' => 'آفریقا',     'flag' => 'za'],
            ['fa' => 'یاقوت سرخ', 'en' => 'Ruby',        'origin' => 'میانمار',    'flag' => 'mm'],
            ['fa' => 'یاقوت کبود', 'en' => 'Blue Sapphire', 'origin' => 'سری‌لانکا', 'flag' => 'lk'],
            ['fa' => 'یاقوت',  'en' => 'Sapphire',       'origin' => 'سری‌لانکا',  'flag' => 'lk'],
            ['fa' => 'زمرد',   'en' => 'Emerald',        'origin' => 'کلمبیا',     'flag' => 'co'],
            ['fa' => 'توپاز',  'en' => 'Topaz',          'origin' => 'برزیل',      'flag' => 'br'],
            ['fa' => 'آمیتیست','en' => 'Amethyst',       'origin' => 'برزیل',      'flag' => 'br'],
            ['fa' => 'در نجف', 'en' => 'Najaf Pearl',    'origin' => 'عراق',       'flag' => 'iq'],
            ['fa' => 'اوپال',  'en' => 'Opal',           'origin' => 'استرالیا',   'flag' => 'au'],
            ['fa' => 'مرجان',  'en' => 'Coral',          'origin' => 'مدیترانه',   'flag' => 'it'],
            ['fa' => 'لاجورد', 'en' => 'Lapis Lazuli',   'origin' => 'افغانستان',  'flag' => 'af'],
            ['fa' => 'چشم ببر','en' => 'Tiger Eye',      'origin' => 'آفریقا',     'flag' => 'za'],
        ];

        foreach ($stoneKeywords as $s) {
            if (mb_strpos($name, $s['fa']) !== false) {
                $this->stoneName = $s['fa'];
                $this->stoneEn = $s['en'];
                $this->stoneOrigin = $s['origin'];
                $this->stoneFlag = $s['flag'];
                break;
            }
        }

        // ─── فلز ───
        if (mb_strpos($name, 'طلا') !== false || mb_stripos($name, 'gold') !== false) {
            if (mb_strpos($name, '18') !== false) {
                $this->metal = 'طلا 18K'; $this->metalEn = 'Gold 18K'; $this->metalCarat = '750';
            } elseif (mb_strpos($name, '21') !== false) {
                $this->metal = 'طلا 21K'; $this->metalEn = 'Gold 21K'; $this->metalCarat = '875';
            } elseif (mb_strpos($name, '22') !== false) {
                $this->metal = 'طلا 22K'; $this->metalEn = 'Gold 22K'; $this->metalCarat = '916';
            } else {
                $this->metal = 'طلا 18K'; $this->metalEn = 'Gold 18K'; $this->metalCarat = '750';
            }
        } elseif (mb_strpos($name, 'نقره') !== false || mb_stripos($name, 'silver') !== false) {
            $this->metal = 'نقره 925';
            $this->metalEn = 'Silver 925';
            $this->metalCarat = '925';
        } elseif (mb_strpos($name, 'پلاتین') !== false) {
            $this->metal = 'پلاتین 950';
            $this->metalEn = 'Platinum 950';
            $this->metalCarat = '950';
        }

        // ─── ابعاد (از نام) ───
        if (preg_match('/(\d+(?:\.\d+)?)\s*[*×xX]\s*(\d+(?:\.\d+)?)/', $name, $m)) {
            $this->length = $m[1];
            $this->width = $m[2];
        }
    }

    public function clearSearch(): void
    {
        $this->skuSearch = '';
        $this->searchStatus = '';
        $this->searchedProduct = null;
        $this->productImageUrl = null;
    }

    /* ═══════════════════════════════════════════════════════════
       Actions موجود
       ═══════════════════════════════════════════════════════════ */
    public function selectStone(int $index): void
    {
        $s = $this->stoneOptions[$index] ?? null;
        if (!$s) return;
        $this->stoneName   = $s['name'];
        $this->stoneEn     = $s['en'];
        $this->stoneOrigin = $s['origin'];
        $this->stoneFlag   = $s['flag'];
        $this->stoneIcon   = $s['icon'];
    }

    public function selectMetal(int $index): void
    {
        $m = $this->metalOptions[$index] ?? null;
        if (!$m) return;
        $this->metal      = $m['name'];
        $this->metalEn    = $m['en'];
        $this->metalCarat = $m['carat'];
    }

    public function nextStep(): void
    {
        if ($this->step === 1) {
            $this->validate([
                'stoneName' => 'required|string',
                'metal'     => 'required|string',
            ], [
                'stoneName.required' => 'سنگ را انتخاب کنید',
                'metal.required'     => 'فلز را انتخاب کنید',
            ]);
        }
        if ($this->step === 2) {
            $this->validate([
                'length' => 'required|numeric|min:0',
                'width'  => 'required|numeric|min:0',
                'weight' => 'required|numeric|min:0',
            ], [
                'length.required' => 'طول الزامی است',
                'width.required'  => 'عرض الزامی است',
                'weight.required' => 'وزن الزامی است',
            ]);
        }
        $this->step = min(3, $this->step + 1);
    }

    public function prevStep(): void
    {
        $this->step = max(1, $this->step - 1);
    }

    public function save()
    {
        $this->validate([
            'stoneName' => 'required|string|max:255',
            'metal'     => 'required|string|max:255',
            'length'    => 'nullable|numeric|min:0',
            'width'     => 'nullable|numeric|min:0',
            'weight'    => 'nullable|numeric|min:0',
            'image'     => 'nullable|image|max:5120',
        ]);

        $imagePath = null;

        // ★ اگه تصویر آپلود شده، از فرم
        if ($this->image) {
            try {
                $imagePath = $this->image->store('certificates', 'public');
            } catch (\Throwable $e) {
                Log::error('Cert image upload: ' . $e->getMessage());
            }
        }
        // ★ اگه نه، ولی از سایت اومده، دانلود کن
        elseif ($this->productImageUrl) {
            try {
                $img = Http::timeout(25)->get($this->productImageUrl)->body();
                $ext = 'jpg';
                if (preg_match('/\.(png|jpg|jpeg|webp)/i', $this->productImageUrl, $m)) {
                    $ext = strtolower($m[1]);
                }
                $fname = 'certificates/' . uniqid('cert_') . '.' . $ext;
                Storage::disk('public')->put($fname, $img);
                $imagePath = $fname;
            } catch (\Throwable $e) {
                Log::error('Cert image download: ' . $e->getMessage());
            }
        }

        if ($this->editingId) {
            $cert = Certificate::find($this->editingId);
            if (!$cert) {
                $this->dispatch('notify', type: 'error', message: 'شناسنامه پیدا نشد');
                return;
            }

            $data = [
                'stone_name'   => $this->stoneName,
                'stone_en'     => $this->stoneEn,
                'stone_origin' => $this->stoneOrigin,
                'stone_flag'   => $this->stoneFlag,
                'metal'        => $this->metal,
                'metal_en'     => $this->metalEn,
                'metal_carat'  => $this->metalCarat,
                'length'       => (float) ($this->length ?: 0),
                'width'        => (float) ($this->width ?: 0),
                'weight'       => (float) ($this->weight ?: 0),
                'brilliant'    => (int) ($this->brilliant ?: 0),
                'customer_id'  => $this->customerId ?: null,
                'order_id'     => $this->orderId ?: null,
            ];
            if ($imagePath) $data['image_path'] = $imagePath;

            $cert->update($data);
            $msg = "شناسنامه #{$cert->code} ویرایش شد.";
        } else {
            $code = Certificate::generateCode();
            $serial = Certificate::generateSerial($code, $this->stoneEn ?: $this->stoneName);

            $cert = Certificate::create([
                'code'         => $code,
                'serial'       => $serial,
                'sku'          => $this->searchedProduct['sku'] ?? null,
                'stone_name'   => $this->stoneName,
                'stone_en'     => $this->stoneEn,
                'stone_origin' => $this->stoneOrigin,
                'stone_flag'   => $this->stoneFlag,
                'metal'        => $this->metal,
                'metal_en'     => $this->metalEn,
                'metal_carat'  => $this->metalCarat,
                'length'       => (float) ($this->length ?: 0),
                'width'        => (float) ($this->width ?: 0),
                'weight'       => (float) ($this->weight ?: 0),
                'brilliant'    => (int) ($this->brilliant ?: 0),
                'image_path'   => $imagePath,
                'customer_id'  => $this->customerId ?: null,
                'order_id'     => $this->orderId ?: null,
                'issued_at'    => now(),
            ]);
            $msg = "شناسنامه #{$code} صادر شد.";
        }

        session()->flash('success', $msg);
        $this->closeModal();
        $this->dispatch('notify', type: 'success', message: $msg);
        $this->dispatch('cert-saved');
    }

    public function render()
    {
        return view('livewire.certificates.create', [
            'customers' => Customer::orderBy('name')->limit(200)->get(),
            'orders'    => Order::latest('id')->limit(100)->get(),
        ]);
    }
}
'''

write('app/Livewire/Certificates/Create.php', CREATE)


# ═══════════════════════════════════════════════════════════════
# 2. CREATE.BLADE — با کادر سرچ SKU بالای مرحله ۱
# ═══════════════════════════════════════════════════════════════

BLADE = r'''<div>
@if($show)
<div style="position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:97;display:flex;align-items:flex-start;justify-content:center;padding:10px;overflow-y:auto"
     wire:key="cert-form-{{ $editingId ?? 'new' }}"
     @keydown.escape.window="$wire.closeModal()">

    <div style="background:#fff;width:100%;max-width:880px;margin:10px auto;border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,.4);overflow:hidden;direction:rtl;font-family:Vazirmatn,Tahoma,sans-serif">

        <div style="background:linear-gradient(135deg,#1a5276,#0d3b5e);color:#fff;padding:14px 18px;display:flex;align-items:center;justify-content:space-between">
            <h2 style="margin:0;font-size:16px;font-weight:700">
                {{ $editingId ? '✏️ ویرایش شناسنامه' : '💎 شناسنامه جدید' }}
            </h2>
            <button type="button" wire:click="closeModal" style="width:32px;height:32px;border-radius:50%;background:rgba(255,255,255,.2);color:#fff;border:none;cursor:pointer;font-size:15px">X</button>
        </div>

        <div style="padding:16px;max-height:calc(100vh - 180px);overflow-y:auto">

            {{-- ★★★ کادر سرچ SKU — فقط در حالت ایجاد، بالای همه --}}
            @if(!$editingId)
                <div style="margin-bottom:18px;padding:14px;background:linear-gradient(135deg,#f0fdf4,#dcfce7);border:2px solid #16a34a;border-radius:12px">
                    <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px">
                        <label style="font-size:13px;font-weight:700;color:#15803d">
                            🔍 جستجوی خودکار از سایت (اختیاری)
                        </label>
                        @if($searchedProduct)
                            <button type="button" wire:click="clearSearch"
                                    style="background:#fee2e2;color:#dc2626;border:none;padding:4px 10px;border-radius:6px;font-size:11px;cursor:pointer;font-weight:700">
                                ✕ پاک کردن
                            </button>
                        @endif
                    </div>

                    <div style="display:flex;gap:8px">
                        <input type="text" wire:model="skuSearch"
                               wire:keydown.enter="searchBySku"
                               dir="ltr"
                               placeholder="کد SKU محصول را وارد کنید (مثلاً 35440)"
                               style="flex:1;padding:11px 14px;border:2px solid #cbd5e1;border-radius:10px;font-family:monospace;font-size:14px;background:#fff;box-sizing:border-box;outline:none">

                        <button type="button" wire:click="searchBySku"
                                wire:loading.attr="disabled"
                                style="padding:11px 22px;background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;border:none;border-radius:10px;font-weight:700;cursor:pointer;font-size:13px;min-width:110px">
                            <span wire:loading.remove wire:target="searchBySku">⚡ جستجو</span>
                            <span wire:loading wire:target="searchBySku">⏳...</span>
                        </button>
                    </div>

                    @if($searchStatus)
                        <div style="margin-top:10px;font-size:12px;font-weight:700;color:{{ str_starts_with($searchStatus, '✅') ? '#15803d' : (str_starts_with($searchStatus, '⏳') ? '#0891b2' : '#dc2626') }}">
                            {{ $searchStatus }}
                        </div>
                    @endif

                    @if($searchedProduct)
                        <div style="margin-top:10px;padding:10px;background:#fff;border-radius:8px;border:1px solid #e2e8f0;display:flex;gap:10px;align-items:center">
                            @if(!empty($searchedProduct['image']))
                                <img src="{{ $searchedProduct['image'] }}" style="width:60px;height:60px;object-fit:cover;border-radius:8px;border:1px solid #e2e8f0">
                            @endif
                            <div style="flex:1;min-width:0">
                                <div style="font-weight:700;font-size:13px;color:#1e293b">{{ $searchedProduct['name'] }}</div>
                                <div style="font-size:11px;color:#64748b;margin-top:2px">
                                    SKU: <span style="font-family:monospace" dir="ltr">{{ $searchedProduct['sku'] }}</span>
                                    &nbsp;·&nbsp;
                                    {{ number_format($searchedProduct['price']) }} تومان
                                </div>
                            </div>
                        </div>
                    @endif
                </div>

                {{-- جداکننده --}}
                <div style="display:flex;align-items:center;gap:10px;margin:16px 0">
                    <div style="flex:1;height:1px;background:#e2e8f0"></div>
                    <span style="font-size:11px;color:#94a3b8;font-weight:700">یا دستی وارد کنید</span>
                    <div style="flex:1;height:1px;background:#e2e8f0"></div>
                </div>
            @endif

            {{-- Steps --}}
            <div style="display:flex;justify-content:space-between;margin-bottom:24px;position:relative;padding:0 20px">
                <div style="position:absolute;top:18px;left:60px;right:60px;height:2px;background:#e2e8f0;z-index:0"></div>
                @foreach([1 => 'سنگ و فلز', 2 => 'مشخصات', 3 => 'تصویر'] as $num => $label)
                    <div style="position:relative;z-index:1;display:flex;flex-direction:column;align-items:center;flex:1">
                        <div style="width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;
                            background:{{ $step >= $num ? 'linear-gradient(135deg,#1a5276,#0d3b5e)' : '#f1f5f9' }};
                            color:{{ $step >= $num ? '#fff' : '#64748b' }};">
                            {{ $num }}
                        </div>
                        <div style="font-size:11px;font-weight:700;margin-top:6px;color:{{ $step >= $num ? '#1a5276' : '#94a3b8' }}">{{ $label }}</div>
                    </div>
                @endforeach
            </div>

            {{-- STEP 1 --}}
            @if($step === 1)
                <div style="margin-bottom:20px">
                    <h3 style="font-size:14px;font-weight:700;color:#1a5276;margin:0 0 12px">💎 سنگ را انتخاب کنید</h3>
                    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:8px">
                        @foreach($stoneOptions as $i => $s)
                            <button type="button" wire:click="selectStone({{ $i }})"
                                    style="padding:10px 4px;border:2px solid {{ $stoneName === $s['name'] ? '#c9a84c' : '#e2e8f0' }};background:{{ $stoneName === $s['name'] ? '#fef3c7' : '#fff' }};border-radius:10px;cursor:pointer">
                                <div style="font-size:26px;margin-bottom:4px">{{ $s['icon'] }}</div>
                                <div style="font-size:11px;font-weight:700;color:#1e293b">{{ $s['name'] }}</div>
                            </button>
                        @endforeach
                    </div>
                    @error('stoneName') <div style="color:#dc2626;font-size:11px;margin-top:8px">{{ $message }}</div> @enderror
                </div>

                <div>
                    <h3 style="font-size:14px;font-weight:700;color:#1a5276;margin:0 0 12px">⚙️ فلز را انتخاب کنید</h3>
                    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(100px,1fr));gap:8px">
                        @foreach($metalOptions as $i => $m)
                            <button type="button" wire:click="selectMetal({{ $i }})"
                                    style="padding:12px 6px;border:2px solid {{ $metal === $m['name'] ? '#c9a84c' : '#e2e8f0' }};background:{{ $metal === $m['name'] ? '#fef3c7' : '#fff' }};border-radius:10px;cursor:pointer;font-weight:700;font-size:12px;color:#1e293b">
                                {{ $m['name'] }}
                            </button>
                        @endforeach
                    </div>
                    @error('metal') <div style="color:#dc2626;font-size:11px;margin-top:8px">{{ $message }}</div> @enderror
                </div>
            @endif

            {{-- STEP 2 --}}
            @if($step === 2)
                <div style="background:linear-gradient(135deg,#fef3c7,#fde68a);padding:10px 14px;border-radius:10px;margin-bottom:16px;font-size:13px;font-weight:700;color:#78350f">
                    💎 {{ $stoneName }} — ⚙️ {{ $metal }}
                </div>

                <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:14px">
                    <div>
                        <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">طول (mm)</label>
                        <input type="number" step="0.01" wire:model="length" dir="ltr"
                               style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-family:monospace;font-size:13px;background:#f8fafc;box-sizing:border-box;text-align:center">
                        @error('length') <div style="color:#dc2626;font-size:10px;margin-top:3px">{{ $message }}</div> @enderror
                    </div>
                    <div>
                        <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">عرض (mm)</label>
                        <input type="number" step="0.01" wire:model="width" dir="ltr"
                               style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-family:monospace;font-size:13px;background:#f8fafc;box-sizing:border-box;text-align:center">
                        @error('width') <div style="color:#dc2626;font-size:10px;margin-top:3px">{{ $message }}</div> @enderror
                    </div>
                    <div>
                        <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">وزن (گرم)</label>
                        <input type="number" step="0.001" wire:model="weight" dir="ltr"
                               style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-family:monospace;font-size:13px;background:#f8fafc;box-sizing:border-box;text-align:center">
                        @error('weight') <div style="color:#dc2626;font-size:10px;margin-top:3px">{{ $message }}</div> @enderror
                    </div>
                    <div>
                        <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">عیار</label>
                        <input type="text" value="{{ $metalCarat }}" readonly dir="ltr"
                               style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-family:monospace;font-size:13px;background:#e2e8f0;box-sizing:border-box;text-align:center">
                    </div>
                    <div>
                        <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">برلیان</label>
                        <input type="number" wire:model="brilliant" dir="ltr"
                               style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-family:monospace;font-size:13px;background:#f8fafc;box-sizing:border-box;text-align:center">
                    </div>
                </div>
            @endif

            {{-- STEP 3 --}}
            @if($step === 3)
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:16px">
                    <div>
                        <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">👤 مشتری (اختیاری)</label>
                        <select wire:model="customerId" style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:13px;background:#f8fafc;box-sizing:border-box">
                            <option value="">— بدون مشتری —</option>
                            @foreach($customers as $c)
                                <option value="{{ $c->id }}">{{ $c->name }} — {{ $c->phone }}</option>
                            @endforeach
                        </select>
                    </div>
                    <div>
                        <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">📦 سفارش (اختیاری)</label>
                        <select wire:model="orderId" style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:13px;background:#f8fafc;box-sizing:border-box">
                            <option value="">— بدون سفارش —</option>
                            @foreach($orders as $o)
                                <option value="{{ $o->id }}">#{{ $o->order_number }}</option>
                            @endforeach
                        </select>
                    </div>
                </div>

                <div>
                    <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">📸 تصویر محصول</label>

                    {{-- اگه از سایت اومده --}}
                    @if($productImageUrl && !$image)
                        <div style="padding:10px;background:#f0fdf4;border:1.5px solid #16a34a;border-radius:8px;margin-bottom:8px">
                            <div style="font-size:11px;font-weight:700;color:#15803d;margin-bottom:6px">✅ تصویر از سایت گرفته شد</div>
                            <img src="{{ $productImageUrl }}" style="max-width:120px;border-radius:8px;border:2px solid #c9a84c">
                        </div>
                    @endif

                    {{-- آپلود دستی --}}
                    <input type="file" wire:model="image" accept="image/*"
                           style="width:100%;padding:8px;border:1.5px dashed #cbd5e1;border-radius:8px;background:#f8fafc;box-sizing:border-box">
                    <div wire:loading wire:target="image" style="font-size:11px;color:#0891b2;margin-top:4px">⏳ در حال آپلود...</div>

                    @if($image)
                        <div style="margin-top:10px">
                            <div style="font-size:11px;font-weight:700;color:#0891b2;margin-bottom:4px">📤 تصویر آپلود شده شما</div>
                            <img src="{{ $image->temporaryUrl() }}" style="max-width:120px;border-radius:10px;border:2px solid #c9a84c">
                        </div>
                    @endif

                    @error('image') <div style="color:#dc2626;font-size:10px;margin-top:3px">{{ $message }}</div> @enderror
                </div>
            @endif
        </div>

        <div style="padding:12px 18px;background:#f8fafc;border-top:1px solid #e2e8f0;display:flex;justify-content:space-between;gap:8px">
            <div>
                @if($step > 1)
                    <button type="button" wire:click="prevStep"
                            style="padding:9px 18px;background:#f1f5f9;color:#475569;border:1.5px solid #cbd5e1;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">→ قبل</button>
                @endif
            </div>
            <div style="display:flex;gap:8px">
                <button type="button" wire:click="closeModal"
                        style="padding:9px 18px;background:#fff;color:#475569;border:1.5px solid #cbd5e1;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">انصراف</button>
                @if($step < 3)
                    <button type="button" wire:click="nextStep"
                            style="padding:9px 22px;background:linear-gradient(135deg,#1a5276,#0d3b5e);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">بعد ←</button>
                @else
                    <button type="button" wire:click="save" wire:loading.attr="disabled"
                            style="padding:9px 22px;background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">
                        <span wire:loading.remove wire:target="save">✓ ذخیره</span>
                        <span wire:loading wire:target="save">⏳...</span>
                    </button>
                @endif
            </div>
        </div>
    </div>
</div>
@endif
</div>
'''

write('resources/views/livewire/certificates/create.blade.php', BLADE)


# ═══════════════════════════════════════════════════════════════
# 3. حذف AutoCreate از layout
# ═══════════════════════════════════════════════════════════════

layout = ROOT / 'resources' / 'views' / 'components' / 'layouts' / 'app.blade.php'
if layout.exists():
    txt = layout.read_text(encoding='utf-8')
    txt = re.sub(r'\s*<livewire:certificates\.auto-create[^>]*/>\s*', '\n    ', txt)
    layout.write_text(txt, encoding='utf-8')
    print("[OK] layout - حذف auto-create")


# ═══════════════════════════════════════════════════════════════
# 4. حذف دکمه صدور خودکار از table page
# ═══════════════════════════════════════════════════════════════

tp = ROOT / 'resources' / 'views' / 'livewire' / 'tables' / 'certificates-table-page.blade.php'
if tp.exists():
    txt = tp.read_text(encoding='utf-8')
    txt = re.sub(
        r'<button[^>]*onclick="Livewire\.dispatch\(\'open-auto-cert\'\)"[^>]*>.*?</button>\s*',
        '',
        txt,
        flags=re.DOTALL
    )
    tp.write_text(txt, encoding='utf-8')
    print("[OK] table page - حذف دکمه صدور خودکار")


print()
print("=" * 60)
print("DONE")
print("=" * 60)
print("  php artisan view:clear")
print("  php artisan optimize:clear")
print("  php artisan serve")