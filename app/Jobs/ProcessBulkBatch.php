<?php

namespace App\Jobs;

use App\Application\Bulk\BulkEngine;
use App\Infrastructure\WooCommerce\WooCommerceClient;
use App\Models\BulkBatch;
use App\Models\BulkItem;
use App\Models\BulkRun;
use Illuminate\Bus\Queueable;
use Illuminate\Contracts\Queue\ShouldQueue;
use Illuminate\Foundation\Bus\Dispatchable;
use Illuminate\Queue\InteractsWithQueue;
use Illuminate\Queue\SerializesModels;
use Illuminate\Support\Facades\Log;

/**
 * ★ ProcessBulkBatch — پردازش هر batch در صف
 *
 * - Idempotent: هر آیتم با idempotency_key کنترل می‌شود
 * - Retry با backoff
 * - به‌روزرسانی counters run
 */
class ProcessBulkBatch implements ShouldQueue
{
    use Dispatchable, InteractsWithQueue, Queueable, SerializesModels;

    public int $tries = 3;
    public int $backoff = 5;
    public int $timeout = 300;

    public function __construct(public int $batchId) {}

    public function handle(): void
    {
        $batch = BulkBatch::with('items')->find($this->batchId);
        if (!$batch) return;
        if (in_array($batch->status, ['completed'])) return;

        $batch->update([
            'status' => 'processing',
            'attempts' => $batch->attempts + 1,
            'started_at' => now(),
        ]);

        $run = BulkRun::find($batch->run_id);
        if ($run) $run->update(['status' => 'processing']);

        $woo = (new WooCommerceClient())->module('bulk');

        // ساخت payload از آیتم‌های batch
        $payloads = [];
        $itemBySku = [];
        foreach ($batch->items as $item) {
            if ($item->status === 'success' || $item->status === 'draft_created') continue;
            if ($item->status === 'processing') continue;

            $payload = $this->buildPayload($item, $run);
            if (empty($payload)) continue;

            $payloads[] = $payload;
            $itemBySku[$payload['sku']] = $item;

            $item->update(['status' => 'processing', 'started_at' => now()]);
        }

        if (empty($payloads)) {
            $this->finalizeBatch($batch);
            return;
        }

        try {
            $r = $woo->batchProducts(['create' => $payloads]);
        } catch (\Throwable $e) {
            $this->handleBatchFailure($batch, $e->getMessage());
            return;
        }

        if (!$r['ok']) {
            $this->handleBatchFailure($batch, $r['error'] ?? 'خطای نامشخص');
            return;
        }

        $created = $r['body']['create'] ?? [];

        foreach ($created as $res) {
            $sku = $res['sku'] ?? null;
            if (!$sku || !isset($itemBySku[$sku])) continue;

            $item = $itemBySku[$sku];

            if (isset($res['id'])) {
                $item->update([
                    'status' => ($res['status'] ?? 'draft') === 'publish' ? 'success' : 'draft_created',
                    'woo_product_id' => $res['id'],
                    'response_payload' => $res,
                    'finished_at' => now(),
                ]);
            } else {
                $err = $res['error']['message'] ?? 'خطای نامشخص';
                $item->update([
                    'status' => 'failed',
                    'error_message' => $err,
                    'error_code' => $res['error']['code'] ?? null,
                    'response_payload' => $res,
                    'finished_at' => now(),
                ]);
            }
        }

        $this->finalizeBatch($batch);
    }

    protected function finalizeBatch(BulkBatch $batch): void
    {
        $success = $batch->items()->whereIn('status', ['success', 'draft_created'])->count();
        $failed = $batch->items()->where('status', 'failed')->count();

        $batch->update([
            'status' => $failed > 0 ? 'completed_with_errors' : 'completed',
            'success_count' => $success,
            'failed_count' => $failed,
            'finished_at' => now(),
        ]);

        // Recalc run
        $run = BulkRun::find($batch->run_id);
        if ($run) {
            $run->recalcCounters();

            // اگه همه batchها تمام شدن
            $pendingBatches = $run->batches()
                ->whereNotIn('status', ['completed', 'completed_with_errors', 'failed'])
                ->count();

            if ($pendingBatches === 0) {
                $run->update([
                    'status' => $run->failed_items > 0 ? 'completed_with_errors' : 'completed',
                    'finished_at' => now(),
                ]);
            }
        }
    }

    protected function handleBatchFailure(BulkBatch $batch, string $error): void
    {
        Log::error("BulkBatch #{$batch->id} failed: {$error}");

        $batch->update([
            'status' => 'failed',
            'error' => $error,
            'finished_at' => now(),
        ]);

        // همه آیتم‌های processing → failed
        foreach ($batch->items()->where('status', 'processing')->get() as $item) {
            $item->update([
                'status' => 'failed',
                'error_message' => $error,
                'finished_at' => now(),
            ]);
        }

        $run = BulkRun::find($batch->run_id);
        if ($run) $run->recalcCounters();

        throw new \RuntimeException("BulkBatch failed: {$error}");
    }

    protected function buildPayload(BulkItem $item, ?BulkRun $run): array
    {
        $input = $item->input_data ?? [];
        $settings = $run?->settings_snapshot ?? [];

        $sku = $item->sku;
        $titleFa = trim((string) ($input['title_fa'] ?? ''));
        $slugEn = trim((string) ($input['slug_en'] ?? ''));

        $payload = [
            'name' => trim($titleFa . ' ' . $sku) ?: $sku,
            'sku' => $sku,
            'type' => 'simple',
            'status' => $input['status'] ?? $settings['status'] ?? 'draft',
            'regular_price' => (string) ($input['regular_price'] ?? ''),
            'short_description' => $input['short_description'] ?? $settings['default_short_description'] ?? '',
            'manage_stock' => $settings['manage_stock'] ?? true,
            'stock_status' => $settings['stock_status'] ?? 'instock',
            'backorders' => $settings['backorders'] ?? 'no',
            'sold_individually' => $settings['sold_individually'] ?? false,
        ];

        if ($slugEn !== '') {
            $payload['slug'] = preg_replace('/\s+/', '-', $slugEn . ' ' . $sku);
        }
        if (!empty($input['sale_price'])) $payload['sale_price'] = (string) $input['sale_price'];
        if (!empty($input['weight'])) $payload['weight'] = (string) $input['weight'];
        if (!empty($input['stock_quantity'])) {
            $payload['stock_quantity'] = (int) $input['stock_quantity'];
        }

        $dim = [];
        if (!empty($input['length'])) $dim['length'] = (string) $input['length'];
        if (!empty($input['width'])) $dim['width'] = (string) $input['width'];
        if (!empty($input['height'])) $dim['height'] = (string) $input['height'];
        if (!empty($dim)) $payload['dimensions'] = $dim;

        // Categories
        if (!empty($settings['categories'])) {
            $payload['categories'] = array_map(fn($id) => ['id' => (int) $id], $settings['categories']);
        }

        // Attributes
        if (!empty($input['attr_values']) && !empty($settings['attributes'])) {
            $attrs = [];
            foreach ($input['attr_values'] as $attrId => $names) {
                if (empty($names)) continue;
                $attrs[] = [
                    'id' => (int) $attrId,
                    'visible' => true,
                    'variation' => false,
                    'options' => is_array($names) ? $names : [$names],
                ];
            }
            if (!empty($attrs)) $payload['attributes'] = $attrs;
        }

        // Author
        if (!empty($settings['author_id'])) $payload['author'] = (int) $settings['author_id'];
        if (!empty($settings['date_created'])) $payload['date_created'] = $settings['date_created'];

        // ★ Images — پیش‌بینی URL
        $imageExt = $settings['image_ext'] ?? 'jpg';
        $maxImages = (int) ($settings['max_images'] ?? 6);
        $siteUrl = rtrim((string) \App\Models\AppSetting::get('commerce_url', ''), '/');
        if ($siteUrl) {
            $now = now();
            $images = [];
            for ($i = 0; $i < $maxImages; $i++) {
                $images[] = [
                    'src' => "{$siteUrl}/wp-content/uploads/{$now->year}/{$now->month}/{$i}-{$sku}.{$imageExt}",
                    'position' => $i,
                ];
            }
            $payload['images'] = $images;
        }

        return $payload;
    }
}
