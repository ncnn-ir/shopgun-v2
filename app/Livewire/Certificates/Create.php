<?php

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

    public string $skuSearch = '';
    public string $searchStatus = '';
    public bool $searching = false;
    public ?array $searchedProduct = null;
    public ?string $productImageUrl = null;

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


    public function mount(): void
    {
        try {
            $savedStones = \App\Models\AppSetting::get('cert_stones', null);
            if (is_array($savedStones) && count($savedStones) > 0) {
                $this->stoneOptions = $savedStones;
            }

            $savedMetals = \App\Models\AppSetting::get('cert_metals', null);
            if (is_array($savedMetals) && count($savedMetals) > 0) {
                $this->metalOptions = $savedMetals;
            }
        } catch (\Throwable $e) {}
    }

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
       SKU SEARCH
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
                $this->searchStatus = '❌ تنظیمات کامرس پر نشده';
                $this->searching = false;
                return;
            }

            $base = rtrim($url, '/');
            if (!str_contains($base, '/wp-json')) $base .= '/wp-json/wc/v3';

            $r = Http::withBasicAuth($key, $secret)
                ->timeout(30)
                ->connectTimeout(15)
                ->retry(2, 2000)
                ->get("{$base}/products", ['sku' => $sku, 'per_page' => 1]);

            if (!$r->successful()) {
                $this->searchStatus = '❌ خطای HTTP ' . $r->status();
                $this->searching = false;
                return;
            }

            $json = $r->json();
            // اگه با sku دقیق پیدا نشد، با search امتحان کن
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

            $p = $json[0];

            $this->searchedProduct = [
                'id'         => (int) ($p['id'] ?? 0),
                'sku'        => (string) ($p['sku'] ?? ''),
                'name'       => (string) ($p['name'] ?? ''),
                'price'      => (float) ($p['price'] ?? 0),
                'image'      => $p['images'][0]['src'] ?? null,
                'weight'     => (float) ($p['weight'] ?? 0),
                'attributes' => array_map(fn($a) => [
                    'name' => $a['name'] ?? '',
                    'options' => $a['options'] ?? [],
                ], $p['attributes'] ?? []),
                'description'=> strip_tags($p['short_description'] ?? $p['description'] ?? ''),
                'dim_length' => (float) ($p['dimensions']['length'] ?? 0),
                'dim_width'  => (float) ($p['dimensions']['width'] ?? 0),
                'dim_height' => (float) ($p['dimensions']['height'] ?? 0),
            ];

            $this->productImageUrl = $this->searchedProduct['image'];

            // ★ پر کردن خودکار
            $this->autoFillFromProduct($this->searchedProduct);

            $this->searchStatus = '✅ محصول پیدا شد: ' . $this->searchedProduct['name'];
            $this->step = 2;

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

        // ─── ابعاد ───
        // ۱. از فیلد dimensions ووکامرس
        if (!empty($product['dim_length'])) {
            $this->length = (string) $product['dim_length'];
        }
        if (!empty($product['dim_width'])) {
            $this->width = (string) $product['dim_width'];
        }

        // ۲. اگه خالی بود، از نام استخراج کن
        if (empty($this->length) || empty($this->width)) {
            // الگوهای مختلف: 15×12 ، 15*12 ، 15x12 ، 15 در 12
            $patterns = [
                '/(\d+(?:\.\d+)?)\s*[*×xX]\s*(\d+(?:\.\d+)?)/u',
                '/(\d+(?:\.\d+)?)\s*(?:در|به)\s*(\d+(?:\.\d+)?)/u',
                '/طول\s*[:=]?\s*(\d+(?:\.\d+)?).*?عرض\s*[:=]?\s*(\d+(?:\.\d+)?)/u',
            ];

            foreach ($patterns as $pattern) {
                if (preg_match($pattern, $name, $m)) {
                    if (empty($this->length)) $this->length = $m[1];
                    if (empty($this->width))  $this->width  = $m[2];
                    break;
                }
            }
        }

        // ─── سنگ — معادل‌یابی با stoneOptions ───
        $matched = false;

        // لیست معادل‌ها: کلید واژه‌های هر سنگ
        $stoneKeywords = [
            'فیروزه عجمی'   => ['فیروزه عجمی', 'عجمی', 'Turquoise Ajami', 'firouzeh ajami'],
            'فیروزه شجری'   => ['فیروزه شجری', 'شجری', 'Turquoise Shajari'],
            'فیروزه'        => ['فیروزه', 'Turquoise', 'firouzeh'],
            'عقیق یمانی'    => ['عقیق یمانی', 'یمانی', 'Yemeni Agate'],
            'عقیق سلیمانی'  => ['عقیق سلیمانی', 'سلیمانی', 'Solomoni'],
            'عقیق شجر'      => ['عقیق شجر', 'شجر', 'Dendritic'],
            'عقیق'          => ['عقیق', 'Agate', 'aqiq'],
            'در نجف'        => ['در نجف', 'نجف', 'Najaf'],
            'الماس'         => ['الماس', 'Diamond', 'almas'],
            'یاقوت سرخ'     => ['یاقوت سرخ', 'یاقوت سرخ', 'Ruby', 'سرخ'],
            'یاقوت کبود'    => ['یاقوت کبود', 'کبود', 'Blue Sapphire', 'Sapphire'],
            'یاقوت'         => ['یاقوت', 'Yaqoot'],
            'زمرد'          => ['زمرد', 'Emerald', 'zomorod'],
            'توپاز'         => ['توپاز', 'Topaz'],
            'آمیتیست'       => ['آمیتیست', 'Amethyst'],
        ];

        foreach ($stoneKeywords as $stoneKey => $keywords) {
            foreach ($keywords as $kw) {
                if (mb_strpos($name, $kw) !== false) {
                    // ★ این سنگ در stoneOptions وجود داره؟
                    foreach ($this->stoneOptions as $opt) {
                        if ($opt['name'] === $stoneKey) {
                            // ★ انتخاب از لیست — باعث می‌شه در گرید هایلایت بشه
                            $this->stoneName   = $opt['name'];
                            $this->stoneEn     = $opt['en'];
                            $this->stoneOrigin = $opt['origin'];
                            $this->stoneFlag   = $opt['flag'];
                            $this->stoneIcon   = $opt['icon'];
                            $matched = true;
                            break 3;
                        }
                    }
                }
            }
        }

        // اگه معادل پیدا نشد ولی کلمه سنگ بود
        if (!$matched) {
            foreach (['فیروزه', 'عقیق', 'الماس', 'یاقوت', 'زمرد', 'توپاز', 'در نجف', 'آمیتیست'] as $genericStone) {
                if (mb_strpos($name, $genericStone) !== false) {
                    $this->stoneName = $genericStone;
                    $this->stoneEn = '—';
                    $this->stoneOrigin = '';
                    $this->stoneFlag = 'ir';
                    break;
                }
            }
        }

        // ─── برلیان از ویژگی‌ها ───
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
                        if (preg_match('/(\d+)/', $opt, $m)) {
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
            if (preg_match('/(?:برلیان|brilliant)[^\d]*(\d+)/iu', $desc, $m)) {
                $this->brilliant = $m[1];
            }
        }

        // ─── فلز — معادل‌یابی با metalOptions ───
        $metalMatched = false;

        if (preg_match('/طلا\s*(18|21|22|24)/u', $name, $m)) {
            $k = 'طلا ' . $m[1] . 'K';
            foreach ($this->metalOptions as $opt) {
                if ($opt['name'] === $k) {
                    $this->metal = $opt['name'];
                    $this->metalEn = $opt['en'];
                    $this->metalCarat = $opt['carat'];
                    $metalMatched = true;
                    break;
                }
            }
        }

        if (!$metalMatched) {
            if (mb_strpos($name, 'طلا') !== false || mb_stripos($name, 'gold') !== false) {
                $this->metal = 'طلا 18K';
                $this->metalEn = 'Gold 18K';
                $this->metalCarat = '750';
            } elseif (mb_strpos($name, 'نقره') !== false || mb_stripos($name, 'silver') !== false) {
                $this->metal = 'نقره 925';
                $this->metalEn = 'Silver 925';
                $this->metalCarat = '925';
            } elseif (mb_strpos($name, 'پلاتین') !== false) {
                $this->metal = 'پلاتین 950';
                $this->metalEn = 'Platinum 950';
                $this->metalCarat = '950';
            }
        }
    }

    public function clearSearch(): void
    {
        $this->skuSearch = '';
        $this->searchStatus = '';
        $this->searchedProduct = null;
        $this->productImageUrl = null;
    }

    /* ═══════════════════════════════════════════════════════════ */
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

        try {
            $imagePath = null;
            if ($this->image) {
                $imagePath = $this->image->store('certificates', 'public');
            } elseif ($this->productImageUrl) {
                $img = \Illuminate\Support\Facades\Http::timeout(25)->get($this->productImageUrl)->body();
                $ext = 'jpg';
                if (preg_match('/\.(png|jpg|jpeg|webp)/i', $this->productImageUrl, $m)) {
                    $ext = strtolower($m[1]);
                }
                $fname = 'certificates/' . uniqid('cert_') . '.' . $ext;
                \Illuminate\Support\Facades\Storage::disk('public')->put($fname, $img);
                $imagePath = $fname;
            }

            // ★ استفاده از Action واحد
            $action = new \App\Application\Actions\IssueCertificateAction();

            if ($this->editingId) {
                $cert = \App\Models\Certificate::find($this->editingId);
                if (!$cert) {
                    $this->dispatch('notify', type: 'error', message: 'شناسنامه پیدا نشد');
                    return;
                }

                $data = [
                    'stone_name' => $this->stoneName,
                    'stone_en' => $this->stoneEn,
                    'stone_origin' => $this->stoneOrigin,
                    'stone_flag' => $this->stoneFlag,
                    'metal' => $this->metal,
                    'metal_en' => $this->metalEn,
                    'metal_carat' => $this->metalCarat,
                    'length' => (float) ($this->length ?: 0),
                    'width' => (float) ($this->width ?: 0),
                    'weight' => (float) ($this->weight ?: 0),
                    'brilliant' => (int) ($this->brilliant ?: 0),
                    'customer_id' => $this->customerId ?: null,
                    'order_id' => $this->orderId ?: null,
                    'sku' => $this->searchedProduct['sku'] ?? null,
                ];
                if ($imagePath) $data['image_path'] = $imagePath;

                $cert->update($data);
                $msg = "شناسنامه #{$cert->code} ویرایش شد.";
            } else {
                $cert = $action->execute([
                    'stone_name' => $this->stoneName,
                    'stone_en' => $this->stoneEn,
                    'stone_origin' => $this->stoneOrigin,
                    'stone_flag' => $this->stoneFlag,
                    'metal' => $this->metal,
                    'metal_en' => $this->metalEn,
                    'metal_carat' => $this->metalCarat,
                    'length' => (float) ($this->length ?: 0),
                    'width' => (float) ($this->width ?: 0),
                    'weight' => (float) ($this->weight ?: 0),
                    'brilliant' => (int) ($this->brilliant ?: 0),
                    'image_path' => $imagePath,
                    'image_url' => $this->productImageUrl,
                    'customer_id' => $this->customerId ?: null,
                    'order_id' => $this->orderId ?: null,
                    'sku' => $this->searchedProduct['sku'] ?? null,
                ]);
                $msg = "شناسنامه #{$cert->code} صادر شد.";
            }

            session()->flash('success', $msg);
            $this->closeModal();
            $this->dispatch('notify', type: 'success', message: $msg);
            $this->dispatch('cert-saved');

        } catch (\Throwable $e) {
            $this->dispatch('notify', type: 'error', message: 'خطا: ' . $e->getMessage());
        }
    }

    public function render()
    {
        return view('livewire.certificates.create', [
            'customers' => Customer::orderBy('name')->limit(200)->get(),
            'orders'    => Order::latest('id')->limit(100)->get(),
        ]);
    }
}
