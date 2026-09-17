<?php

namespace App\Livewire\Certificates;

use App\Models\AppSetting;
use App\Models\Certificate;
use App\Models\Customer;
use Illuminate\Support\Facades\Http;
use Livewire\Attributes\On;
use Livewire\Component;

class AutoCreate extends Component
{
    public bool $show = false;
    public string $sku = '';
    public string $status = '';
    public bool $searching = false;
    public array $product = [];

    // فیلدهای قابل ویرایش
    public string $stoneName   = '';
    public string $stoneEn     = '';
    public string $stoneOrigin = '';
    public string $stoneFlag   = 'ir';
    public string $metal       = 'نقره 925';
    public string $metalEn     = 'Silver 925';
    public string $metalCarat  = '925';
    public string $length      = '';
    public string $width       = '';
    public string $weight      = '';
    public string $brilliant   = '0';
    public ?int $customerId    = null;
    public string $previewHtml = '';

    #[On('open-auto-cert')]
    public function open(): void
    {
        $this->resetForm();
        $this->show = true;
    }

    public function close(): void
    {
        $this->show = false;
        $this->resetForm();
    }

    protected function resetForm(): void
    {
        $this->sku = '';
        $this->status = '';
        $this->product = [];
        $this->stoneName = '';
        $this->stoneEn = '';
        $this->stoneOrigin = '';
        $this->stoneFlag = 'ir';
        $this->metal = 'نقره 925';
        $this->metalEn = 'Silver 925';
        $this->metalCarat = '925';
        $this->length = '';
        $this->width = '';
        $this->weight = '';
        $this->brilliant = '0';
        $this->customerId = null;
        $this->previewHtml = '';
        $this->status = '';
    }

    public function searchBySku(): void
    {
        $sku = trim($this->sku);
        if ($sku === '') {
            $this->status = '❌ SKU را وارد کن';
            return;
        }

        $this->searching = true;
        $this->status = '⏳ در حال جستجو در سایت...';
        $this->product = [];

        try {
            $url    = trim((string) AppSetting::get('commerce_url', ''));
            $key    = trim((string) AppSetting::get('commerce_key', ''));
            $secret = trim((string) AppSetting::get('commerce_secret', ''));

            if (!$url || !$key || !$secret) {
                $this->status = '❌ تنظیمات کامرس خالی است';
                $this->searching = false;
                return;
            }

            $base = rtrim($url, '/');
            if (!str_contains($base, '/wp-json')) $base .= '/wp-json/wc/v3';

            // ★ جستجوی دقیق SKU
            $r = Http::withBasicAuth($key, $secret)
                ->timeout(15)
                ->get("{$base}/products", ['sku' => $sku, 'per_page' => 1]);

            if (!$r->successful()) {
                $this->status = '❌ خطای HTTP ' . $r->status();
                $this->searching = false;
                return;
            }

            $json = $r->json();
            if (empty($json) || !is_array($json)) {
                $this->status = '❌ محصولی با SKU «' . e($sku) . '» پیدا نشد';
                $this->searching = false;
                return;
            }

            $p = $json[0];
            $this->product = [
                'id' => (int) ($p['id'] ?? 0),
                'sku' => (string) ($p['sku'] ?? ''),
                'name' => (string) ($p['name'] ?? ''),
                'price' => (float) ($p['price'] ?? 0),
                'image' => $p['images'][0]['src'] ?? null,
                'images' => array_map(fn($i) => $i['src'] ?? null, $p['images'] ?? []),
                'description' => strip_tags($p['short_description'] ?? $p['description'] ?? ''),
                'weight' => (float) ($p['weight'] ?? 0),
                'categories' => array_map(fn($c) => $c['name'] ?? '', $p['categories'] ?? []),
                'attributes' => array_map(fn($a) => ['name' => $a['name'] ?? '', 'options' => $a['options'] ?? []], $p['attributes'] ?? []),
            ];

            // ★ تلاش برای استخراج اطلاعات از نام/توضیحات
            $this->autoFillFromProduct();
            $this->updatePreview();

            $this->status = '✅ محصول پیدا شد: ' . $this->product['name'];

        } catch (\Throwable $e) {
            $this->status = '❌ ' . $e->getMessage();
        }

        $this->searching = false;
    }

    protected function autoFillFromProduct(): void
    {
        $name = $this->product['name'] ?? '';

        // وزن
        if (!empty($this->product['weight'])) {
            $this->weight = (string) $this->product['weight'];
        } else {
            // از نام بگیر
            if (preg_match('/([\d.]+)\s*(گرم|گرمى|gram|g)/u', $name, $m)) {
                $this->weight = $m[1];
            }
        }

        // سنگ
        $stoneKeywords = [
            'فیروزه' => ['فیروزه', 'Turquoise', 'ir'],
            'عقیق'   => ['عقیق', 'Agate', 'ye'],
            'الماس'  => ['الماس', 'Diamond', 'za'],
            'یاقوت'  => ['یاقوت', 'Ruby', 'mm'],
            'زمرد'   => ['زمرد', 'Emerald', 'co'],
            'توپاز'  => ['توپاز', 'Topaz', 'br'],
            'در نجف' => ['در نجف', 'Najaf', 'iq'],
            'آمیتیست'=> ['آمیتیست', 'Amethyst', 'br'],
        ];

        foreach ($stoneKeywords as $fa => $meta) {
            if (mb_strpos($name, $fa) !== false) {
                $this->stoneName = $fa;
                $this->stoneEn = $meta[1];
                $this->stoneFlag = $meta[2];
                break;
            }
        }

        // فلز
        if (mb_strpos($name, 'طلا') !== false) {
            $this->metal = 'طلا 18K';
            $this->metalEn = 'Gold 18K';
            $this->metalCarat = '750';
        } elseif (mb_strpos($name, 'نقره') !== false) {
            $this->metal = 'نقره 925';
            $this->metalEn = 'Silver 925';
            $this->metalCarat = '925';
        }

        // ابعاد
        if (preg_match('/(\d+)\s*[*×x]\s*(\d+)/', $name, $m)) {
            $this->length = $m[1];
            $this->width = $m[2];
        }
    }

    public function updated(): void
    {
        $this->updatePreview();
    }

    public function updatePreview(): void
    {
        if (empty($this->stoneName) && empty($this->stoneEn)) {
            $this->previewHtml = '';
            return;
        }

        try {
            $cert = new Certificate([
                'code' => '123456',
                'serial' => 'MJ-TEMP-' . rand(1000, 9999),
                'stone_name' => $this->stoneName ?: 'سنگ',
                'stone_en' => $this->stoneEn ?: '',
                'stone_origin' => $this->stoneOrigin,
                'stone_flag' => $this->stoneFlag,
                'metal' => $this->metal,
                'metal_en' => $this->metalEn,
                'metal_carat' => $this->metalCarat,
                'length' => (float) ($this->length ?: 0),
                'width' => (float) ($this->width ?: 0),
                'weight' => (float) ($this->weight ?: 0),
                'brilliant' => (int) ($this->brilliant ?: 0),
                'image_url' => $this->product['image'] ?? null,
                'issued_at' => now(),
            ]);
            $this->previewHtml = \App\Services\CertRenderer::renderCard($cert);
        } catch (\Throwable $e) {
            $this->previewHtml = '<div style="padding:20px;color:#dc2626">خطا: ' . htmlspecialchars($e->getMessage()) . '</div>';
        }
    }

    public function save(): void
    {
        $this->validate([
            'stoneName' => 'required|string|max:255',
            'metal' => 'required|string|max:255',
        ]);

        $code = Certificate::generateCode();
        $serial = Certificate::generateSerial($code, $this->stoneEn ?: $this->stoneName);

        $cert = Certificate::create([
            'code' => $code,
            'serial' => $serial,
            'sku' => $this->product['sku'] ?? null,
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
            'issued_at' => now(),
        ]);

        // تصویر محصول رو ذخیره کن
        if (!empty($this->product['image'])) {
            try {
                $img = Http::timeout(20)->get($this->product['image'])->body();
                $fname = 'certificates/' . $code . '.jpg';
                \Illuminate\Support\Facades\Storage::disk('public')->put($fname, $img);
                $cert->update(['image_path' => $fname]);
            } catch (\Throwable $e) {}
        }

        session()->flash('success', "شناسنامه #{$code} صادر شد.");
        $this->close();
        $this->dispatch('notify', type: 'success', message: "شناسنامه #{$code} صادر شد");
        $this->dispatch('cert-saved');

    }

    public function render()
    {
        return view('livewire.certificates.auto-create');
    }
}
