<?php

namespace App\Livewire\Products;

use App\Models\AppSetting;
use Illuminate\Support\Facades\Cache;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;
use Livewire\Component;

class BulkCreate extends Component
{
    public string $tab = 'form';  // form | queue

    // Connection test
    public bool $testing = false;
    public array $test_result = [];

    // Group fields
    public array $woo_categories = [];
    public array $selected_categories = [];
    public array $woo_attributes = [];
    public array $selected_attributes = []; // [attr_id => [term_ids]]
    public array $attr_terms = [];          // [attr_id => [terms]]
    public array $wp_users = [];
    public ?int $author_id = null;
    public string $status = 'draft';
    public string $date_created = '';

    // Image pattern
    public string $image_ext = 'jpg';
    public int $max_images = 4;

    // Stock defaults
    public bool $manage_stock = true;
    public string $stock_status = 'instock';
    public string $backorders = 'no';
    public bool $sold_individually = false;

    // Default short description
    public string $default_short_description = '';

    // Products — unique fields per product
    public array $products = [];

    // Processing
    public bool $processing = false;
    public bool $sending = false;
    public int $progress_sent = 0;
    public int $progress_total = 0;
    public int $progress_ok = 0;
    public int $progress_fail = 0;
    public array $log = [];

    // Detail modal
    public bool $show_detail = false;
    public ?array $detail = null;

    // ═══════════════════════════════════════════════════════════
    public function mount(): void
    {
        $this->loadLists();
        if (empty($this->products)) {
            $this->addRow();
        }
    }

    protected function loadLists(): void
    {
        try {
            $this->woo_categories = (array) AppSetting::get('woo_categories_cache', []);
            $this->woo_attributes = (array) AppSetting::get('woo_attributes_cache', []);
            $this->wp_users = (array) AppSetting::get('woo_users_cache', []);
        } catch (\Throwable $e) {}
    }

    protected function wooAuth(): ?array
    {
        $url    = trim((string) AppSetting::get('commerce_url', ''));
        $key    = trim((string) AppSetting::get('commerce_key', ''));
        $secret = trim((string) AppSetting::get('commerce_secret', ''));

        if (!$url || !$key || !$secret) return null;

        $base = rtrim($url, '/');
        if (!str_contains($base, '/wp-json')) $base .= '/wp-json/wc/v3';

        $wpBase = preg_replace('#/wc/v3$#', '', $base);

        return ['base' => $base, 'wp_base' => $wpBase, 'key' => $key, 'secret' => $secret];
    }

    protected function siteUrl(): string
    {
        return rtrim((string) AppSetting::get('commerce_url', ''), '/');
    }

    // ═══════════════════════════════════════════════════════════
    // Test connection + fetch categories/attributes/users
    // ═══════════════════════════════════════════════════════════
    public function testConnection(): void
    {
        @set_time_limit(60);
        $this->testing = true;
        $this->test_result = [];

        try {
            $auth = $this->wooAuth();
            if (!$auth) {
                $this->test_result = ['ok' => false, 'msg' => 'تنظیمات کامرس کامل نیست'];
                $this->testing = false;
                return;
            }

            $r = Http::withBasicAuth($auth['key'], $auth['secret'])
                ->timeout(20)->connectTimeout(10)
                ->get($auth['base'] . '/products', ['per_page' => 1]);

            if (!$r->successful()) {
                $this->test_result = ['ok' => false, 'msg' => 'HTTP ' . $r->status()];
                $this->testing = false;
                return;
            }

            $this->test_result = ['ok' => true, 'msg' => '✅ اتصال برقرار است'];

            // Categories
            $rc = Http::withBasicAuth($auth['key'], $auth['secret'])
                ->timeout(20)->get($auth['base'] . '/products/categories', ['per_page' => 100]);
            if ($rc->successful()) {
                $this->woo_categories = array_map(fn($c) => [
                    'id' => (int) ($c['id'] ?? 0),
                    'name' => (string) ($c['name'] ?? ''),
                    'slug' => (string) ($c['slug'] ?? ''),
                ], $rc->json() ?? []);
                AppSetting::put('woo_categories_cache', $this->woo_categories, 'commerce');
            }

            // Attributes
            $ra = Http::withBasicAuth($auth['key'], $auth['secret'])
                ->timeout(20)->get($auth['base'] . '/products/attributes');
            if ($ra->successful()) {
                $this->woo_attributes = array_map(fn($a) => [
                    'id' => (int) ($a['id'] ?? 0),
                    'name' => (string) ($a['name'] ?? ''),
                    'slug' => (string) ($a['slug'] ?? ''),
                ], $ra->json() ?? []);
                AppSetting::put('woo_attributes_cache', $this->woo_attributes, 'commerce');
            }

            // Users
            try {
                $ru = Http::withBasicAuth($auth['key'], $auth['secret'])
                    ->timeout(20)->get($auth['wp_base'] . '/wp/v2/users');
                if ($ru->successful()) {
                    $this->wp_users = array_map(fn($u) => [
                        'id' => (int) ($u['id'] ?? 0),
                        'name' => (string) ($u['name'] ?? ''),
                        'slug' => (string) ($u['slug'] ?? ''),
                    ], $ru->json() ?? []);
                    AppSetting::put('woo_users_cache', $this->wp_users, 'commerce');
                }
            } catch (\Throwable $e) {
                // users optional
            }

            Cache::forget('app_settings_all');
            $this->test_result['msg'] .= " — " . count($this->woo_categories) . " دسته، " . count($this->woo_attributes) . " ویژگی";

        } catch (\Throwable $e) {
            $this->test_result = ['ok' => false, 'msg' => $e->getMessage()];
        }

        $this->testing = false;
    }

    // ═══════════════════════════════════════════════════════════
    // Products management
    // ═══════════════════════════════════════════════════════════
    public function addRow(): void
    {
        $this->products[] = [
            'sku' => '',
            'title_fa' => '',
            'slug_en' => '',
            'weight' => '',
            'length' => '',
            'width' => '',
            'height' => '',
            'regular_price' => '',
            'sale_price' => '',
            'stock_quantity' => '',
            'short_description' => '',
            'status' => '',  // خالی = از گروه
            'checked' => true,
        ];
    }

    public function removeRow(int $i): void
    {
        if (!isset($this->products[$i])) return;
        array_splice($this->products, $i, 1);
        if (empty($this->products)) $this->addRow();
    }

    public function clearAll(): void
    {
        $this->products = [];
        $this->addRow();
    }

    public function addBulkSkus(): void
    {
        // پارس لیست SKU از textarea
        $this->products = [];
        foreach (array_filter(array_map('trim', preg_split('/[\s,;]+/u', $this->bulk_skus ?? ''))) as $sku) {
            $this->products[] = [
                'sku' => $sku,
                'title_fa' => $this->bulk_title_fa ?? '',
                'slug_en' => $this->bulk_slug_en ?? '',
                'weight' => $this->bulk_weight ?? '',
                'length' => $this->bulk_length ?? '',
                'width' => $this->bulk_width ?? '',
                'height' => $this->bulk_height ?? '',
                'regular_price' => $this->bulk_regular_price ?? '',
                'sale_price' => $this->bulk_sale_price ?? '',
                'stock_quantity' => $this->bulk_stock ?? '',
                'short_description' => '',
                'status' => '',
                'checked' => true,
            ];
        }
        if (empty($this->products)) $this->addRow();
    }

    public string $bulk_skus = '';
    public string $bulk_title_fa = '';
    public string $bulk_slug_en = '';
    public string $bulk_weight = '';
    public string $bulk_length = '';
    public string $bulk_width = '';
    public string $bulk_height = '';
    public string $bulk_regular_price = '';
    public string $bulk_sale_price = '';
    public string $bulk_stock = '';

    // ═══════════════════════════════════════════════════════════
    // Image URL prediction
    // ═══════════════════════════════════════════════════════════
    protected function predictImageUrls(string $sku): array
    {
        if ($sku === '') return [];
        $site = $this->siteUrl();
        if (!$site) return [];

        $now = now();
        $year = $now->format('Y');
        $month = $now->format('m');
        $ext = $this->image_ext ?: 'jpg';

        $urls = [];
        for ($i = 0; $i < $this->max_images; $i++) {
            $filename = "{$i}-{$sku}.{$ext}";
            // حالت پیش‌فرض
            $urls[] = "{$site}/wp-content/uploads/{$year}/{$month}/{$filename}";
        }
        return $urls;
    }

    protected function verifyImageExists(string $url): bool
    {
        try {
            $r = Http::timeout(5)->connectTimeout(3)->head($url);
            return $r->successful();
        } catch (\Throwable $e) {
            return false;
        }
    }

    // ═══════════════════════════════════════════════════════════
    // Build product payload
    // ═══════════════════════════════════════════════════════════
    protected function buildPayload(array $p): array
    {
        $sku = trim((string) ($p['sku'] ?? ''));
        if ($sku === '') return [];

        $titleFa = trim((string) ($p['title_fa'] ?? ''));
        $slugEn = trim((string) ($p['slug_en'] ?? ''));

        // name: {title} {sku}
        $name = trim($titleFa . ' ' . $sku);
        $slug = trim($slugEn . ' ' . $sku);
        if ($slug !== '') {
            $slug = preg_replace('/\s+/', '-', $slug);
        }

        $data = [
            'name' => $name,
            'sku' => $sku,
            'type' => 'simple',
            'status' => $p['status'] ?: $this->status,
            'regular_price' => (string) ($p['regular_price'] ?? ''),
            'sale_price' => (string) ($p['sale_price'] ?? ''),
            'description' => '',
            'short_description' => $p['short_description'] ?: $this->default_short_description,
            'manage_stock' => $this->manage_stock,
            'stock_status' => $this->stock_status,
            'backorders' => $this->backorders,
            'sold_individually' => $this->sold_individually,
        ];

        if ($slug !== '') $data['slug'] = $slug;

        // stock quantity logic
        if ($this->manage_stock && $p['stock_quantity'] !== '') {
            $qty = (int) $p['stock_quantity'];
            $data['stock_quantity'] = $qty;
            if ($qty <= 0 && $this->backorders === 'no') {
                $data['stock_status'] = 'outofstock';
            } else {
                $data['stock_status'] = 'instock';
            }
        }

        // weight
        if ($p['weight'] !== '') $data['weight'] = (string) $p['weight'];

        // dimensions
        $dim = [];
        if ($p['length'] !== '') $dim['length'] = (string) $p['length'];
        if ($p['width'] !== '')  $dim['width']  = (string) $p['width'];
        if ($p['height'] !== '') $dim['height'] = (string) $p['height'];
        if (!empty($dim)) $data['dimensions'] = $dim;

        // categories
        if (!empty($this->selected_categories)) {
            $data['categories'] = array_map(fn($id) => ['id' => (int) $id], $this->selected_categories);
        }

        // attributes
        if (!empty($this->selected_attributes)) {
            $attrs = [];
            foreach ($this->selected_attributes as $attrId => $termIds) {
                if (empty($termIds)) continue;
                $attrs[] = [
                    'id' => (int) $attrId,
                    'visible' => true,
                    'variation' => false,
                    'options' => array_map(fn($tid) => $this->termName((int) $attrId, (int) $tid), $termIds),
                ];
            }
            if (!empty($attrs)) $data['attributes'] = $attrs;
        }

        // author
        if ($this->author_id) $data['author'] = (int) $this->author_id;

        // date
        if ($this->date_created) {
            $data['date_created'] = $this->date_created;
        }

        // images
        $urls = $this->predictImageUrls($sku);
        if (!empty($urls)) {
            $images = [];
            foreach ($urls as $idx => $url) {
                $images[] = ['src' => $url, 'position' => $idx];
            }
            $data['images'] = $images;
        }

        return $data;
    }

    protected function termName(int $attrId, int $termId): string
    {
        if (isset($this->attr_terms[$attrId])) {
            foreach ($this->attr_terms[$attrId] as $t) {
                if ((int) $t['id'] === $termId) return (string) $t['name'];
            }
        }
        return (string) $termId;
    }

    // ═══════════════════════════════════════════════════════════
    // Send batch
    // ═══════════════════════════════════════════════════════════
    public function sendBatch(): void
    {
        @set_time_limit(600);
        @ini_set('max_execution_time', '600');

        $auth = $this->wooAuth();
        if (!$auth) {
            $this->log[] = ['time' => now()->format('H:i:s'), 'msg' => '❌ تنظیمات کامرس کامل نیست', 'type' => 'error'];
            return;
        }

        // فیلتر محصولات انتخاب‌شده
        $toSend = array_values(array_filter($this->products, fn($p) => !empty($p['checked']) && !empty($p['sku'])));
        if (empty($toSend)) {
            $this->log[] = ['time' => now()->format('H:i:s'), 'msg' => '❌ محصولی انتخاب نشده', 'type' => 'error'];
            return;
        }

        // Build payloads
        $payloads = [];
        foreach ($toSend as $p) {
            $data = $this->buildPayload($p);
            if (!empty($data)) $payloads[] = $data;
        }

        if (empty($payloads)) {
            $this->log[] = ['time' => now()->format('H:i:s'), 'msg' => '❌ داده‌ای برای ارسال نیست', 'type' => 'error'];
            return;
        }

        $this->processing = true;
        $this->sending = true;
        $this->progress_total = count($payloads);
        $this->progress_sent = 0;
        $this->progress_ok = 0;
        $this->progress_fail = 0;
        $this->log = [];
        $this->log[] = ['time' => now()->format('H:i:s'), 'msg' => "🚀 شروع ارسال {$this->progress_total} محصول", 'type' => 'info'];

        // Split to chunks of 90
        $chunks = array_chunk($payloads, 90);

        foreach ($chunks as $chunkIdx => $chunk) {
            $this->log[] = [
                'time' => now()->format('H:i:s'),
                'msg' => "📦 ارسال دسته " . ($chunkIdx + 1) . " از " . count($chunks) . " (" . count($chunk) . " آیتم)",
                'type' => 'info',
            ];

            try {
                $r = Http::withBasicAuth($auth['key'], $auth['secret'])
                    ->timeout(120)
                    ->connectTimeout(15)
                    ->post($auth['base'] . '/products/batch', [
                        'create' => $chunk,
                    ]);

                if (!$r->successful()) {
                    $this->log[] = [
                        'time' => now()->format('H:i:s'),
                        'msg' => "❌ خطای HTTP " . $r->status() . " — " . mb_substr($r->body(), 0, 300),
                        'type' => 'error',
                    ];
                    $this->progress_fail += count($chunk);
                    $this->progress_sent += count($chunk);
                    continue;
                }

                $body = $r->json();
                $created = $body['create'] ?? [];
                $ok = 0;
                $fail = 0;

                foreach ($created as $item) {
                    if (isset($item['id'])) {
                        $ok++;
                        $this->log[] = [
                            'time' => now()->format('H:i:s'),
                            'msg' => "✅ SKU " . ($item['sku'] ?? '?') . " منتشر شد (ID: " . $item['id'] . ")",
                            'type' => 'success',
                        ];
                    } else {
                        $fail++;
                        $errMsg = $item['error']['message'] ?? ($item['message'] ?? 'خطای نامشخص');
                        $this->log[] = [
                            'time' => now()->format('H:i:s'),
                            'msg' => "❌ خطا: " . $errMsg,
                            'type' => 'error',
                        ];
                    }
                }

                $this->progress_ok += $ok;
                $this->progress_fail += $fail;
                $this->progress_sent += count($chunk);

            } catch (\Throwable $e) {
                $this->log[] = [
                    'time' => now()->format('H:i:s'),
                    'msg' => "❌ " . $e->getMessage(),
                    'type' => 'error',
                ];
                $this->progress_fail += count($chunk);
                $this->progress_sent += count($chunk);
            }

            // 1s delay
            if ($chunkIdx < count($chunks) - 1) {
                sleep(1);
            }
        }

        $this->log[] = [
            'time' => now()->format('H:i:s'),
            'msg' => "🏁 تمام شد — موفق: {$this->progress_ok} · ناموفق: {$this->progress_fail}",
            'type' => 'info',
        ];

        $this->sending = false;
        $this->tab = 'queue';
    }

    // ═══════════════════════════════════════════════════════════
    // Attributes selection
    // ═══════════════════════════════════════════════════════════
    public function loadAttrTerms(int $attrId): void
    {
        if (isset($this->attr_terms[$attrId])) return;
        $auth = $this->wooAuth();
        if (!$auth) return;

        try {
            $r = Http::withBasicAuth($auth['key'], $auth['secret'])
                ->timeout(20)
                ->get("{$auth['base']}/products/attributes/{$attrId}/terms", ['per_page' => 100]);

            if ($r->successful()) {
                $this->attr_terms[$attrId] = array_map(fn($t) => [
                    'id' => (int) ($t['id'] ?? 0),
                    'name' => (string) ($t['name'] ?? ''),
                ], $r->json() ?? []);
            }
        } catch (\Throwable $e) {}
    }

    public function toggleAttrTerm(int $attrId, int $termId): void
    {
        $this->loadAttrTerms($attrId);
        if (!isset($this->selected_attributes[$attrId])) {
            $this->selected_attributes[$attrId] = [];
        }
        $arr = $this->selected_attributes[$attrId];
        if (in_array($termId, $arr, true)) {
            $this->selected_attributes[$attrId] = array_values(array_diff($arr, [$termId]));
        } else {
            $arr[] = $termId;
            $this->selected_attributes[$attrId] = $arr;
        }
    }

    // ═══════════════════════════════════════════════════════════
    // Detail modal
    // ═══════════════════════════════════════════════════════════
    public function showDetail(int $i): void
    {
        if (!isset($this->products[$i])) return;
        $p = $this->products[$i];
        $sku = trim((string) $p['sku']);
        $urls = $this->predictImageUrls($sku);

        $this->detail = [
            'product' => $p,
            'images' => $urls,
            'site' => $this->siteUrl(),
        ];
        $this->show_detail = true;
    }

    public function closeDetail(): void
    {
        $this->show_detail = false;
        $this->detail = null;
    }

    // ═══════════════════════════════════════════════════════════
    public function render()
    {
        return view('livewire.products.bulk-create')
            ->layout('components.layouts.app');
    }
}
