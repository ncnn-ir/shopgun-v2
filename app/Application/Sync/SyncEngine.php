<?php

namespace App\Application\Sync;

use App\Application\Products\ProductResolver;
use App\Application\Woo\WooCatalogService;
use App\Infrastructure\WooCommerce\WooCommerceClient;
use App\Models\Product;
use App\Models\SyncItem;
use App\Models\SyncRun;
use App\Models\WooMedia;
use Illuminate\Support\Facades\Log;

/**
 * ★ SyncEngine — موتور واحد سینک
 *
 * Pipeline:
 *   Create Run → Enumerate → Process Items → Reconcile → Report
 */
class SyncEngine
{
    protected WooCommerceClient $woo;

    public function __construct()
    {
        $this->woo = (new WooCommerceClient())->module('sync');
    }

    // ═══════════════════════════════════════════════════════════
    // Create Run
    // ═══════════════════════════════════════════════════════════
    public function createRun(string $type, string $mode = 'full', array $options = []): SyncRun
    {
        return SyncRun::create([
            'user_id' => auth()->id(),
            'type' => $type,
            'mode' => $mode,
            'status' => 'pending',
            'options' => $options,
        ]);
    }

    // ═══════════════════════════════════════════════════════════
    // Products Sync
    // ═══════════════════════════════════════════════════════════
    public function syncProducts(SyncRun $run, int $perPage = 50, int $maxPages = 200): void
    {
        $run->update(['status' => 'running', 'started_at' => now()]);

        $page = 1;
        $total = 0;

        while ($page <= $maxPages) {
            $r = $this->woo->products([
                'per_page' => $perPage,
                'page' => $page,
                'status' => 'publish',
            ]);

            if (!$r['ok']) {
                $run->update(['last_error' => $r['error'] ?? 'خطای HTTP']);
                break;
            }

            $items = $r['body'] ?? [];
            if (empty($items) || !is_array($items)) break;

            foreach ($items as $woo) {
                $total++;
                $this->processProductItem($run, $woo);
            }

            $run->update(['total_items' => $total]);
            $run->recalcCounters();

            if (count($items) < $perPage) break;
            $page++;
        }

        $this->finalizeRun($run);
    }

    protected function processProductItem(SyncRun $run, array $woo): void
    {
        $wooId = $woo['id'] ?? null;
        if (!$wooId) return;

        $sku = $woo['sku'] ?? null;
        if (!$sku) $sku = 'WC-' . $wooId;

        $item = SyncItem::create([
            'sync_run_id' => $run->id,
            'entity_type' => 'product',
            'entity_id' => (string) $wooId,
            'status' => 'processing',
            'started_at' => now(),
        ]);

        try {
            $exists = Product::where('sku', $sku)->exists();
            $product = Product::upsertFromWoo($woo);

            // ProductIdentity
            try {
                (new ProductResolver())->touchFromWoo($woo);
            } catch (\Throwable $e) {}

            $item->update([
                'local_id' => $product->id,
                'status' => $exists ? 'updated' : 'created',
                'action' => $exists ? 'update' : 'create',
                'finished_at' => now(),
            ]);
        } catch (\Throwable $e) {
            $item->update([
                'status' => 'failed',
                'error_message' => $e->getMessage(),
                'finished_at' => now(),
            ]);
        }
    }

    // ═══════════════════════════════════════════════════════════
    // Catalog Sync
    // ═══════════════════════════════════════════════════════════
    public function syncCatalog(SyncRun $run): void
    {
        $run->update(['status' => 'running', 'started_at' => now()]);

        try {
            $service = new WooCatalogService();
            $report = $service->syncAll();

            $run->update([
                'total_items' => $report['categories'] + $report['attributes'] + $report['terms'] + $report['users'],
                'processed_items' => $report['categories'] + $report['attributes'] + $report['terms'] + $report['users'],
                'created_items' => $report['categories'] + $report['attributes'] + $report['terms'] + $report['users'],
            ]);
        } catch (\Throwable $e) {
            $run->update(['last_error' => $e->getMessage()]);
        }

        $this->finalizeRun($run);
    }

    // ═══════════════════════════════════════════════════════════
    // Media Sync
    // ═══════════════════════════════════════════════════════════
    public function syncMedia(SyncRun $run, int $perPage = 100): void
    {
        $run->update(['status' => 'running', 'started_at' => now()]);

        $page = 1;
        $total = 0;

        while ($page <= 50) {
            try {
                $r = $this->woo->mediaList($perPage, $page);
            } catch (\Throwable $e) {
                $run->update(['last_error' => $e->getMessage()]);
                break;
            }

            if (!$r['ok']) {
                $run->update(['last_error' => $r['error'] ?? 'خطای HTTP']);
                break;
            }

            $items = $r['body'] ?? [];
            if (empty($items) || !is_array($items)) break;

            foreach ($items as $media) {
                $total++;
                $this->processMediaItem($run, $media);
            }

            $run->update(['total_items' => $total]);
            $run->recalcCounters();

            if (count($items) < $perPage) break;
            $page++;
        }

        $this->finalizeRun($run);
    }

    protected function processMediaItem(SyncRun $run, array $media): void
    {
        $wooId = $media['id'] ?? null;
        if (!$wooId) return;

        $item = SyncItem::create([
            'sync_run_id' => $run->id,
            'entity_type' => 'media',
            'entity_id' => (string) $wooId,
            'status' => 'processing',
            'started_at' => now(),
        ]);

        try {
            $exists = WooMedia::where('woo_id', $wooId)->exists();

            // استخراج نام فایل
            $sourceUrl = $media['source_url'] ?? '';
            $filename = basename(parse_url($sourceUrl, PHP_URL_PATH) ?: '');

            $data = [
                'woo_id' => $wooId,
                'filename' => $filename,
                'slug' => $media['slug'] ?? null,
                'mime_type' => $media['mime_type'] ?? null,
                'source_url' => $sourceUrl,
                'file_size' => $media['media_details']['filesize'] ?? null,
                'width' => $media['media_details']['width'] ?? null,
                'height' => $media['media_details']['height'] ?? null,
                'title' => $media['title']['rendered'] ?? null,
                'alt_text' => $media['alt_text'] ?? null,
                'sizes' => $media['media_details']['sizes'] ?? null,
                'meta' => $media['media_details'] ?? null,
                'synced_at' => now(),
            ];

            WooMedia::updateOrCreate(['woo_id' => $wooId], $data);

            $item->update([
                'status' => $exists ? 'updated' : 'created',
                'action' => $exists ? 'update' : 'create',
                'finished_at' => now(),
            ]);
        } catch (\Throwable $e) {
            $item->update([
                'status' => 'failed',
                'error_message' => $e->getMessage(),
                'finished_at' => now(),
            ]);
        }
    }

    // ═══════════════════════════════════════════════════════════
    // Full Sync — همه چیز
    // ═══════════════════════════════════════════════════════════
    public function syncFull(SyncRun $run): void
    {
        $run->update(['status' => 'running', 'started_at' => now()]);

        // ۱. Catalog
        try {
            $service = new WooCatalogService();
            $service->syncAll();
        } catch (\Throwable $e) {
            Log::warning('Full sync catalog failed: ' . $e->getMessage());
        }

        // ۲. Products
        try {
            $this->syncProductsInternal($run);
        } catch (\Throwable $e) {
            Log::warning('Full sync products failed: ' . $e->getMessage());
        }

        // ۳. Media (اختیاری — فقط اگر options.media = true)
        if (!empty($run->options['media'])) {
            try {
                $this->syncMediaInternal($run);
            } catch (\Throwable $e) {
                Log::warning('Full sync media failed: ' . $e->getMessage());
            }
        }

        $this->finalizeRun($run);
    }

    protected function syncProductsInternal(SyncRun $run): void
    {
        $page = 1;
        $perPage = 50;
        $total = $run->total_items;

        while ($page <= 200) {
            $r = $this->woo->products(['per_page' => $perPage, 'page' => $page, 'status' => 'publish']);
            if (!$r['ok']) break;

            $items = $r['body'] ?? [];
            if (empty($items)) break;

            foreach ($items as $woo) {
                $total++;
                $this->processProductItem($run, $woo);
            }

            $run->update(['total_items' => $total]);
            $run->recalcCounters();

            if (count($items) < $perPage) break;
            $page++;
        }
    }

    protected function syncMediaInternal(SyncRun $run): void
    {
        $page = 1;
        $perPage = 100;
        $total = $run->total_items;

        while ($page <= 50) {
            $r = $this->woo->mediaList($perPage, $page);
            if (!$r['ok']) break;

            $items = $r['body'] ?? [];
            if (empty($items)) break;

            foreach ($items as $media) {
                $total++;
                $this->processMediaItem($run, $media);
            }

            $run->update(['total_items' => $total]);
            $run->recalcCounters();

            if (count($items) < $perPage) break;
            $page++;
        }
    }

    // ═══════════════════════════════════════════════════════════
    // Finalize
    // ═══════════════════════════════════════════════════════════
    protected function finalizeRun(SyncRun $run): void
    {
        $run->recalcCounters();
        $run->update([
            'status' => $run->failed_items > 0 ? 'completed_with_errors' : 'completed',
            'finished_at' => now(),
        ]);
    }

    public function cancel(SyncRun $run): void
    {
        $run->update(['status' => 'cancelled', 'finished_at' => now()]);
    }
}
