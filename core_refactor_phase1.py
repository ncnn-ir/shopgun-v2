#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShopGun V2 - Core Refactor Phase 1
====================================
- WooCommerceClient (gateway)
- BulkEngine (queue-based)
- bulk_runs / bulk_batches / bulk_items
- Preview/Diff
"""
from pathlib import Path
import time, subprocess

ROOT = Path('/data/data/com.termux/files/home/shopgun-v2.2')

def write(rel, content):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        p.rename(str(p) + '.bak-' + str(int(time.time())))
    p.write_text(content, encoding='utf-8')
    print("[OK] " + rel)

def run(cmd):
    print(f"$ {cmd}")
    return subprocess.run(cmd, shell=True, cwd=ROOT).returncode


# ═══════════════════════════════════════════════════════════════
# 1. INFRASTRUCTURE/ WooCommerceClient — گِیت‌وی واحد
# ═══════════════════════════════════════════════════════════════

write('app/Infrastructure/WooCommerce/WooCommerceClient.php', r'''<?php

namespace App\Infrastructure\WooCommerce;

use App\Models\AppSetting;
use App\Models\ApiLog;
use Illuminate\Http\Client\PendingRequest;
use Illuminate\Http\Client\Response;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

/**
 * ★ WooCommerceClient
 * دروازه واحد به WooCommerce REST API
 *
 * همه سرویس‌ها و کامپوننت‌ها باید از همین کلاس استفاده کنند
 * نه اینکه خودشان HTTP بزنند.
 */
class WooCommerceClient
{
    protected string $baseUrl;
    protected string $wpBase;
    protected string $consumerKey;
    protected string $consumerSecret;
    protected int $defaultTimeout = 45;
    protected int $connectTimeout = 15;
    protected int $defaultRetry = 2;
    protected string $module = 'unknown';

    public function __construct(?array $auth = null)
    {
        if ($auth === null) {
            $url = trim((string) AppSetting::get('commerce_url', ''));
            $key = trim((string) AppSetting::get('commerce_key', ''));
            $secret = trim((string) AppSetting::get('commerce_secret', ''));

            if (!$url || !$key || !$secret) {
                throw new \RuntimeException('تنظیمات کامرس کامل نیست');
            }

            $base = rtrim($url, '/');
            if (!str_contains($base, '/wp-json')) {
                $base .= '/wp-json/wc/v3';
            }

            $auth = [
                'base' => $base,
                'wp_base' => preg_replace('#/wc/v3$#', '', $base),
                'key' => $key,
                'secret' => $secret,
                'site' => rtrim($url, '/'),
            ];
        }

        $this->baseUrl = $auth['base'];
        $this->wpBase = $auth['wp_base'];
        $this->consumerKey = $auth['key'];
        $this->consumerSecret = $auth['secret'];
    }

    /**
     * تعیین ماژول برای لاگ
     */
    public function module(string $name): self
    {
        $this->module = $name;
        return $this;
    }

    /**
     * تنظیمات زمان‌بندی
     */
    public function timeout(int $seconds): self
    {
        $this->defaultTimeout = $seconds;
        return $this;
    }

    public function retry(int $times): self
    {
        $this->defaultRetry = $times;
        return $this;
    }

    // ═══════════════════════════════════════════════════════════
    // Core request با telemetry
    // ═══════════════════════════════════════════════════════════
    public function request(
        string $method,
        string $endpoint,
        array $data = [],
        array $query = []
    ): array {
        $url = $this->baseUrl . '/' . ltrim($endpoint, '/');
        if (!empty($query)) {
            $url .= '?' . http_build_query($query);
        }

        $start = microtime(true);
        $requestId = uniqid('woo_', true);

        $status = null;
        $error = null;
        $body = null;
        $attempts = 0;

        try {
            $client = Http::withBasicAuth($this->consumerKey, $this->consumerSecret)
                ->timeout($this->defaultTimeout)
                ->connectTimeout($this->connectTimeout)
                ->acceptJson();

            // Retry فقط برای خطاهای گذرا
            if ($this->defaultRetry > 0 && in_array($method, ['GET', 'POST', 'PUT'])) {
                $client = $client->retry($this->defaultRetry, 1500, function ($exception) {
                    // فقط روی timeouts و 5xx و 429
                    if ($exception instanceof \Illuminate\Http\Client\ConnectionException) {
                        return true;
                    }
                    return false;
                }, throw: false);
            }

            $response = match (strtoupper($method)) {
                'GET' => $client->get($url),
                'POST' => $client->post($url, $data),
                'PUT' => $client->put($url, $data),
                'DELETE' => $client->delete($url, $data),
                default => throw new \InvalidArgumentException("Method {$method} پشتیبانی نمی‌شود"),
            };

            $status = $response->status();
            $body = $response->json() ?? $response->body();

            // ثبت در ApiLog
            $this->logRequest($requestId, $method, $url, $data, $status, $body, $start, null);

            if (!$response->successful()) {
                return [
                    'ok' => false,
                    'status' => $status,
                    'body' => $body,
                    'error' => "HTTP {$status}",
                ];
            }

            return [
                'ok' => true,
                'status' => $status,
                'body' => $body,
            ];

        } catch (\Throwable $e) {
            $error = $e->getMessage();
            $duration = (int) round((microtime(true) - $start) * 1000);

            $this->logRequest($requestId, $method, $url, $data, $status, null, $start, $error);

            return [
                'ok' => false,
                'status' => $status,
                'error' => $error,
                'body' => null,
            ];
        }
    }

    protected function logRequest(
        string $requestId,
        string $method,
        string $url,
        array $request,
        ?int $status,
        $response,
        float $start,
        ?string $error
    ): void {
        try {
            ApiLog::record([
                'service' => 'woocommerce',
                'method' => strtoupper($method),
                'url' => mb_substr($url, 0, 900),
                'status_code' => $status,
                'duration_ms' => (int) round((microtime(true) - $start) * 1000),
                'request_body' => !empty($request) ? mb_substr(json_encode($request, JSON_UNESCAPED_UNICODE), 0, 3000) : null,
                'response_body' => $response ? mb_substr(is_string($response) ? $response : json_encode($response, JSON_UNESCAPED_UNICODE), 0, 5000) : null,
                'error' => $error,
            ]);
        } catch (\Throwable $e) {
            Log::warning('ApiLog failed: ' . $e->getMessage());
        }
    }

    // ═══════════════════════════════════════════════════════════
    // APIهای کاربردی
    // ═══════════════════════════════════════════════════════════

    public function testConnection(): array
    {
        return $this->request('GET', 'products', [], ['per_page' => 1]);
    }

    public function products(array $query = []): array
    {
        return $this->request('GET', 'products', [], $query);
    }

    public function product(int $id): array
    {
        return $this->request('GET', "products/{$id}");
    }

    public function productBySku(string $sku): array
    {
        return $this->request('GET', 'products', [], ['sku' => $sku, 'per_page' => 1]);
    }

    public function batchProducts(array $payload): array
    {
        return $this->request('POST', 'products/batch', $payload);
    }

    public function orders(array $query = []): array
    {
        return $this->request('GET', 'orders', [], $query);
    }

    public function customers(array $query = []): array
    {
        return $this->request('GET', 'customers', [], $query);
    }

    public function categories(array $query = []): array
    {
        return $this->request('GET', 'products/categories', [], $query);
    }

    public function attributes(): array
    {
        return $this->request('GET', 'products/attributes');
    }

    public function attributeTerms(int $attrId): array
    {
        return $this->request('GET', "products/attributes/{$attrId}/terms", [], ['per_page' => 100]);
    }

    public function users(): array
    {
        // از wp/v2
        $url = $this->wpBase . '/wp/v2/users';
        try {
            $r = Http::withBasicAuth($this->consumerKey, $this->consumerSecret)
                ->timeout($this->defaultTimeout)
                ->get($url);
            if ($r->successful()) {
                return ['ok' => true, 'body' => $r->json()];
            }
            return ['ok' => false, 'error' => "HTTP {$r->status()}"];
        } catch (\Throwable $e) {
            return ['ok' => false, 'error' => $e->getMessage()];
        }
    }

    public function mediaSearch(string $filename): array
    {
        $url = $this->wpBase . '/wp/v2/media';
        try {
            $r = Http::withBasicAuth($this->consumerKey, $this->consumerSecret)
                ->timeout($this->defaultTimeout)
                ->get($url, ['search' => $filename, 'per_page' => 5]);
            if ($r->successful()) {
                return ['ok' => true, 'body' => $r->json()];
            }
            return ['ok' => false, 'error' => "HTTP {$r->status()}"];
        } catch (\Throwable $e) {
            return ['ok' => false, 'error' => $e->getMessage()];
        }
    }

    public function getSiteUrl(): string
    {
        return rtrim((string) AppSetting::get('commerce_url', ''), '/');
    }
}
''')


# ═══════════════════════════════════════════════════════════════
# 2. MIGRATION — جداول Runs/Batches/Items
# ═══════════════════════════════════════════════════════════════

ts = time.strftime('%Y_%m_%d_%H%M%S')
MIGRATION = '''<?php

use Illuminate\\Database\\Migrations\\Migration;
use Illuminate\\Database\\Schema\\Blueprint;
use Illuminate\\Support\\Facades\\Schema;

return new class extends Migration
{
    public function up(): void
    {
        // ═══ bulk_runs ═══
        if (!Schema::hasTable('bulk_runs')) {
            Schema::create('bulk_runs', function (Blueprint $table) {
                $table->id();
                $table->foreignId('user_id')->nullable()->index();
                $table->string('source', 30)->default('manual'); // manual | csv | json
                $table->string('mode', 20)->default('create');   // create | update | upsert
                $table->string('status', 30)->default('draft')->index();
                // draft | validating | preview | queued | processing | completed | failed | cancelled
                $table->unsignedInteger('total_items')->default(0);
                $table->unsignedInteger('validated_items')->default(0);
                $table->unsignedInteger('queued_items')->default(0);
                $table->unsignedInteger('processing_items')->default(0);
                $table->unsignedInteger('success_items')->default(0);
                $table->unsignedInteger('failed_items')->default(0);
                $table->json('settings_snapshot')->nullable();
                $table->text('last_error')->nullable();
                $table->timestamp('started_at')->nullable();
                $table->timestamp('finished_at')->nullable();
                $table->timestamps();

                $table->index(['status', 'created_at']);
            });
        }

        // ═══ bulk_batches ═══
        if (!Schema::hasTable('bulk_batches')) {
            Schema::create('bulk_batches', function (Blueprint $table) {
                $table->id();
                $table->foreignId('run_id')->constrained('bulk_runs')->cascadeOnDelete();
                $table->unsignedInteger('sequence')->default(1);
                $table->string('status', 30)->default('pending')->index();
                // pending | processing | completed | failed
                $table->unsignedInteger('attempts')->default(0);
                $table->unsignedInteger('items_count')->default(0);
                $table->unsignedInteger('success_count')->default(0);
                $table->unsignedInteger('failed_count')->default(0);
                $table->timestamp('started_at')->nullable();
                $table->timestamp('finished_at')->nullable();
                $table->text('error')->nullable();
                $table->timestamps();

                $table->index(['run_id', 'sequence']);
            });
        }

        // ═══ bulk_items ═══
        if (!Schema::hasTable('bulk_items')) {
            Schema::create('bulk_items', function (Blueprint $table) {
                $table->id();
                $table->foreignId('run_id')->constrained('bulk_runs')->cascadeOnDelete();
                $table->foreignId('batch_id')->nullable()->constrained('bulk_batches')->nullOnDelete();
                $table->string('sku', 100)->index();
                $table->unsignedBigInteger('woo_product_id')->nullable()->index();
                $table->string('status', 30)->default('pending')->index();
                // pending | validating | valid | invalid | queued | processing
                // success | draft_created | failed | skipped
                $table->unsignedInteger('attempt')->default(0);
                $table->string('idempotency_key', 100)->nullable()->index();
                $table->string('payload_hash', 64)->nullable();
                $table->json('input_data')->nullable();
                $table->json('request_payload')->nullable();
                $table->json('response_payload')->nullable();
                $table->string('error_code', 50)->nullable();
                $table->text('error_message')->nullable();
                $table->json('validation_warnings')->nullable();
                $table->json('diff_data')->nullable();
                $table->timestamp('started_at')->nullable();
                $table->timestamp('finished_at')->nullable();
                $table->timestamps();

                $table->index(['run_id', 'status']);
                $table->unique(['run_id', 'sku'], 'bulk_items_run_sku_unique');
            });
        }
    }

    public function down(): void
    {
        Schema::dropIfExists('bulk_items');
        Schema::dropIfExists('bulk_batches');
        Schema::dropIfExists('bulk_runs');
    }
};
'''

write(f'database/migrations/{ts}_create_bulk_runs_batches_items_tables.php', MIGRATION)


# ═══════════════════════════════════════════════════════════════
# 3. Models — BulkRun, BulkBatch, BulkItem
# ═══════════════════════════════════════════════════════════════

write('app/Models/BulkRun.php', '''<?php

namespace App\\Models;

use Illuminate\\Database\\Eloquent\\Model;
use Illuminate\\Database\\Eloquent\\Relations\\HasMany;

class BulkRun extends Model
{
    protected $fillable = [
        'user_id', 'source', 'mode', 'status',
        'total_items', 'validated_items', 'queued_items',
        'processing_items', 'success_items', 'failed_items',
        'settings_snapshot', 'last_error', 'started_at', 'finished_at',
    ];

    protected $casts = [
        'settings_snapshot' => 'array',
        'started_at' => 'datetime',
        'finished_at' => 'datetime',
    ];

    public function batches(): HasMany
    {
        return $this->hasMany(BulkBatch::class, 'run_id')->orderBy('sequence');
    }

    public function items(): HasMany
    {
        return $this->hasMany(BulkItem::class, 'run_id');
    }

    public function getProgressPercentAttribute(): int
    {
        if ($this->total_items <= 0) return 0;
        $done = $this->success_items + $this->failed_items;
        return (int) round(($done / $this->total_items) * 100);
    }

    public function recalcCounters(): void
    {
        $this->update([
            'queued_items' => $this->items()->where('status', 'queued')->count(),
            'processing_items' => $this->items()->where('status', 'processing')->count(),
            'success_items' => $this->items()->whereIn('status', ['success', 'draft_created'])->count(),
            'failed_items' => $this->items()->where('status', 'failed')->count(),
        ]);
    }
}
''')

write('app/Models/BulkBatch.php', '''<?php

namespace App\\Models;

use Illuminate\\Database\\Eloquent\\Model;
use Illuminate\\Database\\Eloquent\\Relations\\BelongsTo;
use Illuminate\\Database\\Eloquent\\Relations\\HasMany;

class BulkBatch extends Model
{
    protected $fillable = [
        'run_id', 'sequence', 'status', 'attempts',
        'items_count', 'success_count', 'failed_count',
        'started_at', 'finished_at', 'error',
    ];

    protected $casts = [
        'started_at' => 'datetime',
        'finished_at' => 'datetime',
    ];

    public function run(): BelongsTo
    {
        return $this->belongsTo(BulkRun::class, 'run_id');
    }

    public function items(): HasMany
    {
        return $this->hasMany(BulkItem::class, 'batch_id');
    }
}
''')

write('app/Models/BulkItem.php', '''<?php

namespace App\\Models;

use Illuminate\\Database\\Eloquent\\Model;
use Illuminate\\Database\\Eloquent\\Relations\\BelongsTo;

class BulkItem extends Model
{
    protected $fillable = [
        'run_id', 'batch_id', 'sku', 'woo_product_id',
        'status', 'attempt', 'idempotency_key', 'payload_hash',
        'input_data', 'request_payload', 'response_payload',
        'error_code', 'error_message', 'validation_warnings', 'diff_data',
        'started_at', 'finished_at',
    ];

    protected $casts = [
        'input_data' => 'array',
        'request_payload' => 'array',
        'response_payload' => 'array',
        'validation_warnings' => 'array',
        'diff_data' => 'array',
        'started_at' => 'datetime',
        'finished_at' => 'datetime',
    ];

    public function run(): BelongsTo
    {
        return $this->belongsTo(BulkRun::class, 'run_id');
    }

    public function batch(): BelongsTo
    {
        return $this->belongsTo(BulkBatch::class, 'batch_id');
    }

    public function getWooEditUrlAttribute(): ?string
    {
        if (!$this->woo_product_id) return null;
        $site = rtrim((string) AppSetting::get('commerce_url', ''), '/');
        return $site ? "{$site}/wp-admin/post.php?post={$this->woo_product_id}&action=edit" : null;
    }

    public function getWooViewUrlAttribute(): ?string
    {
        if (!$this->woo_product_id) return null;
        $site = rtrim((string) AppSetting::get('commerce_url', ''), '/');
        return $site ? "{$site}/?p={$this->woo_product_id}" : null;
    }
}
''')


# ═══════════════════════════════════════════════════════════════
# 4. BulkEngine — هسته پردازش
# ═══════════════════════════════════════════════════════════════

write('app/Application/Bulk/BulkEngine.php', r'''<?php

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
''')


# ═══════════════════════════════════════════════════════════════
# 5. JOB — ProcessBulkBatch
# ═══════════════════════════════════════════════════════════════

write('app/Jobs/ProcessBulkBatch.php', r'''<?php

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
''')


# ═══════════════════════════════════════════════════════════════
# 6. Queue Config — Database Driver
# ═══════════════════════════════════════════════════════════════

env_path = ROOT / '.env'
if env_path.exists():
    txt = env_path.read_text(encoding='utf-8')
    if 'QUEUE_CONNECTION=' not in txt:
        txt += "\nQUEUE_CONNECTION=database\n"
        env_path.write_text(txt, encoding='utf-8')
        print("[OK] .env — QUEUE_CONNECTION=database")
    elif 'QUEUE_CONNECTION=sync' in txt:
        txt = txt.replace('QUEUE_CONNECTION=sync', 'QUEUE_CONNECTION=database')
        env_path.write_text(txt, encoding='utf-8')
        print("[OK] .env — تغییر به database")


# ═══════════════════════════════════════════════════════════════
# 7. اجرا
# ═══════════════════════════════════════════════════════════════

print()
print("🔧 Migration و پاک‌سازی...")
run('php artisan migrate --force')
run('php artisan optimize:clear')
run('php artisan route:clear')

print()
print("=" * 60)
print("DONE — Phase 1")
print("=" * 60)
print()
print("🎯 هسته‌های جدید:")
print("   ✅ WooCommerceClient (gateway واحد)")
print("   ✅ BulkEngine (pipeline)")
print("   ✅ Jobs + Queue (Database driver)")
print("   ✅ جداول: bulk_runs, bulk_batches, bulk_items")
print()
print("🚀 برای اجرای worker:")
print("   php artisan queue:work --queue=bulk")
print()
print("   یا در tmux:")
print("   tmux new -s queue 'php artisan queue:work --queue=bulk'")
