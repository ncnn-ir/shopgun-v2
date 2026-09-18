<?php

namespace App\Livewire\Products;

use App\Application\Bulk\BulkEngine;
use App\Models\AppSetting;
use App\Models\BulkItem;
use App\Models\BulkRun;
use App\Models\WooAttribute;
use App\Models\WooCategory;
use App\Models\WooUser;
use Illuminate\Support\Facades\Cache;
use Livewire\Component;

/**
 * ★ BulkCreate v3
 * حالا از BulkEngine و cache لوکال کاتالوگ استفاده می‌کند
 */
class BulkCreate extends Component
{
    public string $tab = 'form';

    // Connection
    public bool $testing = false;
    public array $test_result = [];

    // ★ Caches (از DB لوکال)
    public array $woo_categories = [];
    public array $woo_attributes = [];
    public array $wp_users = [];
    public array $attr_terms = [];

    // Group settings
    public array $selected_categories = [];
    public ?int $author_id = null;
    public string $status = 'draft';
    public string $date_created = '';
    public string $image_ext = 'jpg';
    public int $max_images = 6;

    // Stock
    public bool $manage_stock = true;
    public string $stock_status = 'instock';
    public string $backorders = 'no';
    public bool $sold_individually = false;

    // Short desc
    public string $default_short_description = '';

    // Price calculator
    public string $price_per_gram = '';

    // ★ Attributes as columns
    public array $visible_attributes = [];

    // Products
    public array $products = [];
    public string $bulk_skus = '';

    // ★ Current run + preview
    public ?int $current_run_id = null;
    public array $run_summary = [];
    public array $preview_data = [];
    public bool $showing_preview = false;

    // Processing
    public bool $sending = false;
    public int $progress_sent = 0;
    public int $progress_total = 0;
    public int $progress_ok = 0;
    public int $progress_fail = 0;
    public array $log = [];

    // Detail
    public bool $show_detail = false;
    public ?array $detail = null;

    // History
    public string $history_filter = '';
    public string $history_search = '';

    // ═══════════════════════════════════════════════════════════
    public function mount(): void
    {
        $this->loadCaches();
        $this->loadVisibleAttributes();
        if (empty($this->products)) $this->addRow();
    }

    protected function loadCaches(): void
    {
        // ★ از DB لوکال می‌خوانیم
        try {
            $this->woo_categories = WooCategory::ordered()->get()->map(fn($c) => [
                'id' => (int) $c->woo_id,
                'name' => $c->name,
                'slug' => $c->slug,
            ])->toArray();

            $this->woo_attributes = WooAttribute::orderBy('name')->get()->map(fn($a) => [
                'id' => (int) $a->woo_id,
                'name' => $a->name,
                'slug' => $a->slug,
            ])->toArray();

            $this->wp_users = WooUser::orderBy('name')->get()->map(fn($u) => [
                'id' => (int) $u->woo_id,
                'name' => $u->name,
            ])->toArray();
        } catch (\Throwable $e) {}
    }

    protected function loadVisibleAttributes(): void
    {
        $v = (array) AppSetting::get('bulk_visible_attributes', []);
        foreach ($v as $id) {
            $this->visible_attributes[(string) $id] = true;
        }
    }

    // ═══════════════════════════════════════════════════════════
    public function testConnection(): void
    {
        @set_time_limit(60);
        $this->testing = true;
        $this->test_result = [];

        try {
            $client = new \App\Infrastructure\WooCommerce\WooCommerceClient();
            $r = $client->testConnection();

            if (!$r['ok']) {
                $this->test_result = ['ok' => false, 'msg' => '❌ ' . ($r['error'] ?? 'خطا')];
                $this->testing = false;
                return;
            }

            $this->test_result = ['ok' => true, 'msg' => '✅ اتصال برقرار است — برای دریافت کاتالوگ از تنظیمات استفاده کن'];

        } catch (\Throwable $e) {
            $this->test_result = ['ok' => false, 'msg' => '❌ ' . $e->getMessage()];
        }
        $this->testing = false;
    }

    // ═══════════════════════════════════════════════════════════
    public function loadAttrTerms(int $attrId): void
    {
        if (isset($this->attr_terms[$attrId])) return;

        // ★ از DB لوکال
        $terms = \App\Models\WooAttributeTerm::where('attribute_woo_id', $attrId)
            ->orderBy('menu_order')->orderBy('name')->get();

        $this->attr_terms[$attrId] = $terms->map(fn($t) => [
            'id' => (int) $t->woo_id,
            'name' => $t->name,
        ])->toArray();
    }

    public function toggleVisibleAttribute(int $attrId): void
    {
        $key = (string) $attrId;
        if (!empty($this->visible_attributes[$key])) {
            unset($this->visible_attributes[$key]);
        } else {
            $this->visible_attributes[$key] = true;
            $this->loadAttrTerms($attrId);
        }
        AppSetting::put('bulk_visible_attributes', array_keys($this->visible_attributes), 'commerce');
        Cache::forget('app_settings_all');
    }

    // ═══════════════════════════════════════════════════════════
    public function addRow(): void
    {
        $this->products[] = $this->blankRow();
    }

    protected function blankRow(): array
    {
        return [
            'sku' => '', 'title_fa' => '', 'slug_en' => '',
            'weight' => '', 'length' => '', 'width' => '', 'height' => '',
            'regular_price' => '', 'sale_price' => '', 'stock_quantity' => '',
            'short_description' => '', 'status' => '',
            'attr_values' => [], 'checked' => true,
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
        $this->products = [$this->blankRow()];
    }

    public function addBulkSkus(): void
    {
        $skus = array_filter(array_map('trim', preg_split('/[\s,;،\n]+/u', $this->bulk_skus)));
        if (empty($skus)) return;

        $this->products = [];
        foreach ($skus as $sku) {
            $row = $this->blankRow();
            $row['sku'] = $sku;
            $this->products[] = $row;
        }
        $this->bulk_skus = '';
    }

    public function applyPricePerGram(): void
    {
        $ppg = (float) str_replace(',', '', $this->price_per_gram);
        if ($ppg <= 0) {
            $this->dispatch('notify', type: 'error', message: 'قیمت هر گرم را وارد کن');
            return;
        }
        $count = 0;
        foreach ($this->products as $i => $p) {
            $w = (float) ($p['weight'] ?? 0);
            if ($w <= 0) continue;
            $this->products[$i]['regular_price'] = (string) ((int) round($w * $ppg));
            $count++;
        }
        $this->dispatch('notify', type: 'success', message: "قیمت {$count} محصول محاسبه شد");
    }

    // ═══════════════════════════════════════════════════════════
    // ★ Preview — ساخت Run و نمایش diff
    // ═══════════════════════════════════════════════════════════
    public function buildPreview(): void
    {
        @set_time_limit(300);

        $toSend = array_values(array_filter($this->products, fn($p) => !empty($p['checked']) && !empty($p['sku'])));
        if (empty($toSend)) {
            $this->dispatch('notify', type: 'error', message: 'محصولی انتخاب نشده');
            return;
        }

        $this->showing_preview = true;
        $this->run_summary = ['status' => 'processing', 'msg' => '⏳ در حال تحلیل...'];

        try {
            $engine = new BulkEngine();
            $settings = $this->settingsSnapshot();

            $run = $engine->createRun($toSend, $settings);
            $this->current_run_id = $run->id;

            $val = $engine->validate($run);
            $diff = $engine->buildDiff($run);

            $this->run_summary = [
                'run_id' => $run->id,
                'total' => $val['total'],
                'valid' => $val['valid'],
                'warnings' => $val['warnings'],
            ];

            $this->preview_data = $run->items->map(function ($item) {
                return [
                    'id' => $item->id,
                    'sku' => $item->sku,
                    'status' => $item->status,
                    'warnings' => $item->validation_warnings ?? [],
                    'exists_in_woo' => !empty($item->woo_product_id),
                    'woo_id' => $item->woo_product_id,
                    'title_fa' => $item->input_data['title_fa'] ?? '',
                    'price' => $item->input_data['regular_price'] ?? '',
                ];
            })->toArray();

        } catch (\Throwable $e) {
            $this->run_summary = ['status' => 'error', 'msg' => '❌ ' . $e->getMessage()];
        }
    }

    /**
     * ارسال نهایی از preview
     */
    public function confirmSend(): void
    {
        if (!$this->current_run_id) {
            $this->dispatch('notify', type: 'error', message: 'اول Preview بگیر');
            return;
        }

        try {
            $engine = new BulkEngine();
            $run = BulkRun::find($this->current_run_id);
            if (!$run) {
                $this->dispatch('notify', type: 'error', message: 'Run پیدا نشد');
                return;
            }

            $engine->queue($run);

            $this->sending = true;
            $this->progress_total = $run->items()->count();
            $this->tab = 'queue';

            $this->dispatch('notify', type: 'success', message: "به صف ارسال شد ({$this->progress_total} آیتم)");

        } catch (\Throwable $e) {
            $this->dispatch('notify', type: 'error', message: '❌ ' . $e->getMessage());
        }
    }

    public function refreshProgress(): void
    {
        if (!$this->current_run_id) return;
        $run = BulkRun::find($this->current_run_id);
        if (!$run) return;

        $run->recalcCounters();

        $this->progress_total = $run->total_items;
        $this->progress_sent = $run->success_items + $run->failed_items;
        $this->progress_ok = $run->success_items;
        $this->progress_fail = $run->failed_items;

        // Log زنده از bulk_items
        $this->log = $run->items()
            ->orderByDesc('finished_at')
            ->limit(30)
            ->get()
            ->map(fn($i) => [
                'time' => $i->finished_at?->format('H:i:s') ?? '—',
                'msg' => match ($i->status) {
                    'success' => "✅ {$i->sku} → ID {$i->woo_product_id}",
                    'draft_created' => "📝 {$i->sku} → پیش‌نویس {$i->woo_product_id}",
                    'failed' => "❌ {$i->sku}: " . mb_substr($i->error_message ?? '?', 0, 60),
                    'processing' => "⏳ {$i->sku} در حال پردازش...",
                    'queued' => "🕐 {$i->sku} در صف...",
                    default => "{$i->sku} — {$i->status}",
                },
                'type' => match ($i->status) {
                    'success', 'draft_created' => 'success',
                    'failed' => 'error',
                    default => 'info',
                },
            ])
            ->toArray();
    }

    public function cancelRun(): void
    {
        if (!$this->current_run_id) return;
        $engine = new BulkEngine();
        $run = BulkRun::find($this->current_run_id);
        if ($run) $engine->cancel($run);
        $this->dispatch('notify', type: 'success', message: 'لغو شد');
    }

    public function retryFailed(): void
    {
        if (!$this->current_run_id) return;
        $engine = new BulkEngine();
        $run = BulkRun::find($this->current_run_id);
        if (!$run) return;
        $engine->retryFailed($run);
        $this->dispatch('notify', type: 'success', message: 'آیتم‌های ناموفق به صف جدید اضافه شدند');
    }

    protected function settingsSnapshot(): array
    {
        return [
            'status' => $this->status,
            'author_id' => $this->author_id,
            'date_created' => $this->date_created,
            'image_ext' => $this->image_ext,
            'max_images' => $this->max_images,
            'manage_stock' => $this->manage_stock,
            'stock_status' => $this->stock_status,
            'backorders' => $this->backorders,
            'sold_individually' => $this->sold_individually,
            'default_short_description' => $this->default_short_description,
            'categories' => $this->selected_categories,
            'attributes' => array_keys($this->visible_attributes),
            'source' => 'manual',
            'mode' => 'create',
        ];
    }

    // ═══════════════════════════════════════════════════════════
    // Detail modal (preview تصاویر)
    // ═══════════════════════════════════════════════════════════
    public function showDetail(int $i): void
    {
        if (!isset($this->products[$i])) return;
        $p = $this->products[$i];
        $sku = trim((string) $p['sku']);

        $siteUrl = rtrim((string) AppSetting::get('commerce_url', ''), '/');
        $now = now();
        $urls = [];
        for ($j = 0; $j < $this->max_images; $j++) {
            $urls[] = "{$siteUrl}/wp-content/uploads/{$now->year}/{$now->month}/{$j}-{$sku}.{$this->image_ext}";
        }

        $this->detail = [
            'product' => $p,
            'images' => $urls,
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
        $history = [];
        if ($this->tab === 'history') {
            $q = BulkRun::withCount(['items']);
            if ($this->history_filter) {
                $q->where('status', $this->history_filter);
            }
            if ($this->history_search) {
                $q->whereHas('items', fn($iq) => $iq->where('sku', 'like', "%{$this->history_search}%"));
            }
            $history = $q->latest('id')->limit(50)->get();
        }

        return view('livewire.products.bulk-create', [
            'history' => $history,
        ])->layout('components.layouts.app');
    }
}
