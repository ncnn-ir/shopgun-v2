<?php

namespace App\Application\Bulk;

use App\Infrastructure\WooCommerce\WooCommerceClient;
use App\Models\BulkItem;
use App\Models\BulkRun;
use App\Models\AppSetting;
use Illuminate\Support\Facades\Log;

/**
 * ★ BulkEngine — موتور پردازش ثبت گروهی
 *
 * Pipeline:
 *   Create Run → Validate → Preview → Queue → Batch → Reconcile → Report
 */
class BulkEngine
{
    protected WooCommerceClient $woo;

    public function __construct()
    {
        $this->woo = (new WooCommerceClient())->module('bulk');
    }

    /**
     * ایجاد Run جدید از آرایه محصولات
     */
    public function createRun(array $items, array $settings = []): BulkRun
    {
        $run = BulkRun::create([
            'user_id' => auth()->id(),
            'source' => $settings['source'] ?? 'manual',
            'mode' => $settings['mode'] ?? 'create',
            'status' => 'draft',
            'total_items' => count($items),
            'settings_snapshot' => $settings,
        ]);

        foreach ($items as $idx => $item) {
            $sku = trim((string) ($item['sku'] ?? ''));
            if ($sku === '') continue;

            BulkItem::create([
                'run_id' => $run->id,
                'sku' => $sku,
                'status' => 'pending',
                'idempotency_key' => hash('sha256', $run->id . '|' . $sku),
                'input_data' => $item,
            ]);
        }

        $run->update(['total_items' => $run->items()->count()]);
        return $run;
    }

    /**
     * ★ Validate — بررسی خطاها قبل از ارسال
     */
    public function validate(BulkRun $run): array
    {
        $run->update(['status' => 'validating']);

        $seenSkus = [];
        $wooSkuCache = [];
        $validCount = 0;
        $warningCount = 0;

        foreach ($run->items as $item) {
            $input = $item->input_data ?? [];
            $warnings = [];
            $isValid = true;

            $sku = $item->sku;

            // SKU تکراری در همین run
            if (isset($seenSkus[$sku])) {
                $warnings[] = 'SKU در همین لیست تکرار شده';
                $isValid = false;
            }
            $seenSkus[$sku] = true;

            // بررسی وجود SKU در سایت
            if (!isset($wooSkuCache[$sku])) {
                try {
                    $r = $this->woo->productBySku($sku);
                    $wooSkuCache[$sku] = ($r['ok'] && !empty($r['body'])) ? $r['body'][0] ?? null : null;
                } catch (\Throwable $e) {
                    $wooSkuCache[$sku] = null;
                }
            }

            $wooProduct = $wooSkuCache[$sku];
            if ($wooProduct) {
                $warnings[] = 'SKU قبلاً در سایت موجود است (ID: ' . ($wooProduct['id'] ?? '?') . ')';
                $item->update([
                    'woo_product_id' => $wooProduct['id'] ?? null,
                ]);
            }

            // فیلدهای اجباری
            if (empty($input['title_fa'])) {
                $warnings[] = 'عنوان فارسی خالی است';
            }
            if (empty($input['regular_price'])) {
                $warnings[] = 'قیمت خالی است';
            }

            $item->update([
                'status' => $isValid ? 'valid' : 'invalid',
                'validation_warnings' => $warnings,
            ]);

            if ($isValid) $validCount++;
            else $warningCount++;
        }

        $run->update([
            'status' => 'preview',
            'validated_items' => $validCount,
        ]);

        return [
            'valid' => $validCount,
            'warnings' => $warningCount,
            'total' => $run->items()->count(),
        ];
    }

    /**
     * ★ Build Diff برای نمایش
     */
    public function buildDiff(BulkRun $run): array
    {
        $diff = [];
        foreach ($run->items as $item) {
            $input = $item->input_data ?? [];
            $woo = $item->response_payload ?? [];

            $itemDiff = [
                'sku' => $item->sku,
                'status' => $item->status,
                'exists_in_woo' => !empty($item->woo_product_id),
                'changes' => [],
            ];

            if ($item->woo_product_id && $item->response_payload) {
                // مقایسه قیمت
                if (isset($woo['regular_price']) && (string) $woo['regular_price'] !== (string) ($input['regular_price'] ?? '')) {
                    $itemDiff['changes'][] = [
                        'field' => 'قیمت',
                        'old' => $woo['regular_price'],
                        'new' => $input['regular_price'] ?? '',
                    ];
                }
                // مقایسه وزن
                if (isset($woo['weight']) && (string) $woo['weight'] !== (string) ($input['weight'] ?? '')) {
                    $itemDiff['changes'][] = [
                        'field' => 'وزن',
                        'old' => $woo['weight'],
                        'new' => $input['weight'] ?? '',
                    ];
                }
            }

            $diff[] = $itemDiff;
            $item->update(['diff_data' => $itemDiff]);
        }
        return $diff;
    }

    /**
     * ★ Queue — تبدیل به batch و ارسال به queue
     */
    public function queue(BulkRun $run): void
    {
        $run->update([
            'status' => 'queued',
            'started_at' => now(),
        ]);

        // فقط آیتم‌های valid
        $items = $run->items()->where('status', 'valid')->get();
        $chunks = $items->chunk(90);

        $sequence = 1;
        foreach ($chunks as $chunk) {
            $batch = \App\Models\BulkBatch::create([
                'run_id' => $run->id,
                'sequence' => $sequence,
                'status' => 'pending',
                'items_count' => $chunk->count(),
            ]);

            foreach ($chunk as $item) {
                $item->update([
                    'batch_id' => $batch->id,
                    'status' => 'queued',
                ]);
            }

            // Dispatch Job
            \App\Jobs\ProcessBulkBatch::dispatch($batch->id)
                ->onQueue('bulk')
                ->delay(now()->addSeconds(($sequence - 1) * 2));

            $sequence++;
        }
    }

    /**
     * ★ Cancel Run
     */
    public function cancel(BulkRun $run): void
    {
        $run->update([
            'status' => 'cancelled',
            'finished_at' => now(),
        ]);
    }

    /**
     * ★ Retry Failed Items
     */
    public function retryFailed(BulkRun $run): void
    {
        $failed = $run->items()->where('status', 'failed')->get();
        if ($failed->isEmpty()) return;

        $newRun = $this->createRun(
            $failed->map(fn($i) => $i->input_data)->filter()->toArray(),
            array_merge($run->settings_snapshot ?? [], ['source' => 'retry'])
        );

        // فوراً valid کن و queue
        $newRun->items()->update(['status' => 'valid']);
        $newRun->update(['validated_items' => $newRun->items()->count()]);
        $this->queue($newRun);
    }
}
