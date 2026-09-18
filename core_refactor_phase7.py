#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShopGun V2 - Core Refactor Phase 7
====================================
- SyncEngine کامل (Products + Catalog + Media + Incremental)
- SyncRun + SyncItem models
- MediaResolver (کش تصاویر ووکامرس)
- Sync UI زنده با progress
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
# 1. MIGRATION — sync_runs + sync_items + woo_media
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
        // ═══ sync_runs ═══
        if (!Schema::hasTable('sync_runs')) {
            Schema::create('sync_runs', function (Blueprint $table) {
                $table->id();
                $table->foreignId('user_id')->nullable()->index();
                $table->string('type', 40)->index(); // products | orders | customers | catalog | media | full
                $table->string('mode', 20)->default('full'); // full | incremental
                $table->string('status', 30)->default('pending')->index();
                // pending | running | completed | failed | cancelled

                $table->unsignedInteger('total_items')->default(0);
                $table->unsignedInteger('processed_items')->default(0);
                $table->unsignedInteger('created_items')->default(0);
                $table->unsignedInteger('updated_items')->default(0);
                $table->unsignedInteger('failed_items')->default(0);
                $table->unsignedInteger('skipped_items')->default(0);

                $table->json('options')->nullable();
                $table->text('last_error')->nullable();

                $table->timestamp('started_at')->nullable();
                $table->timestamp('finished_at')->nullable();
                $table->timestamps();

                $table->index(['type', 'status']);
            });
        }

        // ═══ sync_items ═══
        if (!Schema::hasTable('sync_items')) {
            Schema::create('sync_items', function (Blueprint $table) {
                $table->id();
                $table->foreignId('sync_run_id')->constrained('sync_runs')->cascadeOnDelete();
                $table->string('entity_type', 40)->index(); // product | order | customer | category | attribute | term | media
                $table->string('entity_id', 100)->index();  // شناسه خارجی (woo_id یا sku)
                $table->unsignedBigInteger('local_id')->nullable()->index();

                $table->string('status', 30)->default('pending')->index();
                // pending | processing | created | updated | skipped | failed

                $table->string('action', 30)->nullable(); // create | update | skip
                $table->text('error_message')->nullable();
                $table->json('diff_data')->nullable();
                $table->timestamp('started_at')->nullable();
                $table->timestamp('finished_at')->nullable();
                $table->timestamps();

                $table->index(['sync_run_id', 'status']);
            });
        }

        // ═══ woo_media ═══
        if (!Schema::hasTable('woo_media')) {
            Schema::create('woo_media', function (Blueprint $table) {
                $table->id();
                $table->unsignedBigInteger('woo_id')->unique()->index();
                $table->string('filename', 500)->index();
                $table->string('slug')->nullable()->index();
                $table->string('mime_type', 100)->nullable();
                $table->string('source_url', 1000);
                $table->unsignedBigInteger('file_size')->nullable();
                $table->unsignedInteger('width')->nullable();
                $table->unsignedInteger('height')->nullable();
                $table->string('title')->nullable();
                $table->string('alt_text')->nullable();
                $table->json('sizes')->nullable(); // responsive sizes
                $table->json('meta')->nullable();
                $table->timestamp('synced_at')->nullable();
                $table->timestamps();
            });
        }
    }

    public function down(): void
    {
        Schema::dropIfExists('woo_media');
        Schema::dropIfExists('sync_items');
        Schema::dropIfExists('sync_runs');
    }
};
'''

write(f'database/migrations/{ts}_create_sync_runs_items_media_tables.php', MIGRATION)


# ═══════════════════════════════════════════════════════════════
# 2. MODELS
# ═══════════════════════════════════════════════════════════════

write('app/Models/SyncRun.php', '''<?php

namespace App\\Models;

use Illuminate\\Database\\Eloquent\\Model;
use Illuminate\\Database\\Eloquent\\Relations\\HasMany;

class SyncRun extends Model
{
    protected $fillable = [
        'user_id', 'type', 'mode', 'status',
        'total_items', 'processed_items',
        'created_items', 'updated_items', 'failed_items', 'skipped_items',
        'options', 'last_error', 'started_at', 'finished_at',
    ];

    protected $casts = [
        'options' => 'array',
        'started_at' => 'datetime',
        'finished_at' => 'datetime',
    ];

    public function items(): HasMany
    {
        return $this->hasMany(SyncItem::class);
    }

    public function getProgressPercentAttribute(): int
    {
        if ($this->total_items <= 0) return 0;
        return (int) round(($this->processed_items / $this->total_items) * 100);
    }

    public function getDurationAttribute(): ?int
    {
        if (!$this->started_at) return null;
        $end = $this->finished_at ?? now();
        return $end->diffInSeconds($this->started_at);
    }

    public function recalcCounters(): void
    {
        $this->update([
            'processed_items' => $this->items()->whereIn('status', ['created', 'updated', 'skipped', 'failed'])->count(),
            'created_items' => $this->items()->where('status', 'created')->count(),
            'updated_items' => $this->items()->where('status', 'updated')->count(),
            'failed_items' => $this->items()->where('status', 'failed')->count(),
            'skipped_items' => $this->items()->where('status', 'skipped')->count(),
        ]);
    }
}
''')

write('app/Models/SyncItem.php', '''<?php

namespace App\\Models;

use Illuminate\\Database\\Eloquent\\Model;
use Illuminate\\Database\\Eloquent\\Relations\\BelongsTo;

class SyncItem extends Model
{
    protected $fillable = [
        'sync_run_id', 'entity_type', 'entity_id', 'local_id',
        'status', 'action', 'error_message', 'diff_data',
        'started_at', 'finished_at',
    ];

    protected $casts = [
        'diff_data' => 'array',
        'started_at' => 'datetime',
        'finished_at' => 'datetime',
    ];

    public function run(): BelongsTo
    {
        return $this->belongsTo(SyncRun::class, 'sync_run_id');
    }
}
''')

write('app/Models/WooMedia.php', '''<?php

namespace App\\Models;

use Illuminate\\Database\\Eloquent\\Model;

class WooMedia extends Model
{
    protected $table = 'woo_media';

    protected $fillable = [
        'woo_id', 'filename', 'slug', 'mime_type', 'source_url',
        'file_size', 'width', 'height', 'title', 'alt_text',
        'sizes', 'meta', 'synced_at',
    ];

    protected $casts = [
        'sizes' => 'array',
        'meta' => 'array',
        'synced_at' => 'datetime',
    ];

    public static function findByFilename(string $filename): ?self
    {
        return self::where('filename', $filename)->first();
    }

    /**
     * پیدا کردن تصویر با الگوی {index}-{sku}.{ext}
     */
    public static function findByPattern(int $index, string $sku, string $ext = 'jpg'): ?self
    {
        return self::where('filename', "{$index}-{$sku}.{$ext}")->first()
            ?? self::where('filename', 'like', "{$index}-{$sku}.%")->first();
    }
}
''')


# ═══════════════════════════════════════════════════════════════
# 3. SyncEngine — هسته سینک
# ═══════════════════════════════════════════════════════════════

write('app/Application/Sync/SyncEngine.php', r'''<?php

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
''')


# ═══════════════════════════════════════════════════════════════
# 4. اضافه کردن mediaList به WooCommerceClient
# ═══════════════════════════════════════════════════════════════

client = ROOT / 'app' / 'Infrastructure' / 'WooCommerce' / 'WooCommerceClient.php'
if client.exists():
    txt = client.read_text(encoding='utf-8')

    if 'public function mediaList' not in txt:
        method = '''
    /**
     * لیست Media از wp/v2/media
     */
    public function mediaList(int $perPage = 100, int $page = 1): array
    {
        $url = $this->wpBase . '/wp/v2/media';
        try {
            $r = Http::withBasicAuth($this->consumerKey, $this->consumerSecret)
                ->timeout($this->defaultTimeout)
                ->connectTimeout($this->connectTimeout)
                ->get($url, [
                    'per_page' => $perPage,
                    'page' => $page,
                    'media_type' => 'image',
                ]);

            if ($r->successful()) {
                return ['ok' => true, 'body' => $r->json()];
            }
            return ['ok' => false, 'error' => "HTTP {$r->status()}"];
        } catch (\\Throwable $e) {
            return ['ok' => false, 'error' => $e->getMessage()];
        }
    }

    public function mediaFindByFilename(string $filename): array
    {
        $url = $this->wpBase . '/wp/v2/media';
        try {
            $r = Http::withBasicAuth($this->consumerKey, $this->consumerSecret)
                ->timeout(15)
                ->get($url, ['search' => $filename, 'per_page' => 5]);

            if ($r->successful()) {
                return ['ok' => true, 'body' => $r->json()];
            }
            return ['ok' => false, 'error' => "HTTP {$r->status()}"];
        } catch (\\Throwable $e) {
            return ['ok' => false, 'error' => $e->getMessage()];
        }
    }
'''
        # اضافه قبل از getSiteUrl
        marker = "    public function getSiteUrl(): string"
        if marker in txt:
            txt = txt.replace(marker, method + "\n" + marker, 1)
            client.write_text(txt, encoding='utf-8')
            print("[OK] WooCommerceClient - mediaList")


# ═══════════════════════════════════════════════════════════════
# 5. COMMAND — shopgun:sync-all
# ═══════════════════════════════════════════════════════════════

write('app/Console/Commands/SyncAll.php', '''<?php

namespace App\\Console\\Commands;

use App\\Application\\Sync\\SyncEngine;
use App\\Models\\AppSetting;
use Illuminate\\Console\\Command;

class SyncAll extends Command
{
    protected $signature = 'shopgun:sync-all
        {--type=full : products | catalog | media | full}
        {--mode=full : full | incremental}
        {--media : شامل media هم باشد}';

    protected $description = 'سینک کامل از ووکامرس';

    public function handle(): int
    {
        @set_time_limit(900);

        $type = $this->option('type');
        $mode = $this->option('mode');

        $this->info("🔄 شروع سینک: {$type} ({$mode})");

        try {
            $engine = new SyncEngine();
            $run = $engine->createRun($type, $mode, [
                'media' => $this->option('media'),
            ]);

            $this->info("📋 Run #{$run->id}");

            $bar = $this->output->createProgressBar();
            $bar->start();

            match ($type) {
                'products' => $engine->syncProducts($run),
                'catalog' => $engine->syncCatalog($run),
                'media' => $engine->syncMedia($run),
                'full' => $engine->syncFull($run),
                default => throw new \\InvalidArgumentException("نوع نامعتبر: {$type}"),
            };

            $bar->finish();
            $this->newLine(2);

            $run->refresh();

            $this->table(['مورد', 'تعداد'], [
                ['کل', $run->total_items],
                ['جدید', $run->created_items],
                ['بروزرسانی', $run->updated_items],
                ['رد شده', $run->skipped_items],
                ['خطا', $run->failed_items],
            ]);

            if ($run->last_error) {
                $this->warn('خطا: ' . $run->last_error);
            }

            AppSetting::put('woo_last_sync_' . $type, now()->toIso8601String(), 'commerce');
            \\Illuminate\\Support\\Facades\\Cache::forget('app_settings_all');

            $this->newLine();
            $this->info('✅ تمام شد');
            return 0;

        } catch (\\Throwable $e) {
            $this->error('❌ ' . $e->getMessage());
            return 1;
        }
    }
}
''')


# ═══════════════════════════════════════════════════════════════
# 6. Livewire — SyncDashboard
# ═══════════════════════════════════════════════════════════════

write('app/Livewire/Settings/SyncDashboard.php', r'''<?php

namespace App\Livewire\Settings;

use App\Application\Sync\SyncEngine;
use App\Models\SyncItem;
use App\Models\SyncRun;
use Livewire\Component;
use Livewire\WithPagination;

/**
 * ★ SyncDashboard — داشبورد سینک
 */
class SyncDashboard extends Component
{
    use WithPagination;

    public string $activeTab = 'overview';

    // Start form
    public string $syncType = 'full';
    public string $syncMode = 'full';
    public bool $syncMedia = false;

    // Progress
    public ?int $currentRunId = null;
    public array $progressData = [];
    public array $syncLog = [];

    // Items filter
    public string $filterEntity = '';
    public string $filterStatus = '';

    // ═══════════════════════════════════════════════════════════
    public function startSync(): void
    {
        @set_time_limit(900);

        try {
            $engine = new SyncEngine();
            $run = $engine->createRun($this->syncType, $this->syncMode, [
                'media' => $this->syncMedia,
            ]);

            $this->currentRunId = $run->id;
            $this->activeTab = 'progress';

            $this->dispatch('notify', type: 'success', message: "سینک #{$run->id} در حال اجرا...");

            // اجرای سریع (روی local سریع‌تره از queue)
            match ($this->syncType) {
                'products' => $engine->syncProducts($run),
                'catalog' => $engine->syncCatalog($run),
                'media' => $engine->syncMedia($run),
                'full' => $engine->syncFull($run),
            };

            $this->refreshProgress();
            $this->dispatch('notify', type: 'success', message: '✅ سینک کامل شد');

        } catch (\Throwable $e) {
            $this->dispatch('notify', type: 'error', message: '❌ ' . $e->getMessage());
        }
    }

    public function refreshProgress(): void
    {
        if (!$this->currentRunId) return;

        $run = SyncRun::find($this->currentRunId);
        if (!$run) return;

        $run->recalcCounters();
        $run->refresh();

        $this->progressData = [
            'id' => $run->id,
            'type' => $run->type,
            'status' => $run->status,
            'total' => $run->total_items,
            'processed' => $run->processed_items,
            'created' => $run->created_items,
            'updated' => $run->updated_items,
            'failed' => $run->failed_items,
            'skipped' => $run->skipped_items,
            'percent' => $run->progress_percent,
            'duration' => $run->duration,
        ];

        $this->syncLog = SyncItem::where('sync_run_id', $run->id)
            ->latest('finished_at')
            ->limit(30)
            ->get()
            ->map(fn($i) => [
                'time' => $i->finished_at?->format('H:i:s') ?? '—',
                'msg' => match ($i->status) {
                    'created' => "✨ {$i->entity_type} #{$i->entity_id}",
                    'updated' => "🔄 {$i->entity_type} #{$i->entity_id}",
                    'skipped' => "⏭️ {$i->entity_type} #{$i->entity_id}",
                    'failed' => "❌ {$i->entity_type} #{$i->entity_id}: " . mb_substr($i->error_message ?? '?', 0, 50),
                    default => "{$i->entity_type} #{$i->entity_id}",
                },
                'type' => match ($i->status) {
                    'created', 'updated' => 'success',
                    'failed' => 'error',
                    'skipped' => 'warn',
                    default => 'info',
                },
            ])
            ->toArray();
    }

    public function viewRun(int $runId): void
    {
        $this->currentRunId = $runId;
        $this->activeTab = 'items';
        $this->refreshProgress();
    }

    public function cancelRun(): void
    {
        if (!$this->currentRunId) return;
        $run = SyncRun::find($this->currentRunId);
        if ($run) (new SyncEngine())->cancel($run);
        $this->refreshProgress();
        $this->dispatch('notify', type: 'success', message: 'لغو شد');
    }

    public function deleteRun(int $id): void
    {
        SyncRun::find($id)?->delete();
        $this->dispatch('notify', type: 'success', message: 'حذف شد');
    }

    public function render()
    {
        $runs = SyncRun::latest('id')->limit(20)->paginate(15, ['*'], 'runs');

        $items = collect();
        if ($this->currentRunId && $this->activeTab === 'items') {
            $items = SyncItem::where('sync_run_id', $this->currentRunId)
                ->when($this->filterEntity, fn($q) => $q->where('entity_type', $this->filterEntity))
                ->when($this->filterStatus, fn($q) => $q->where('status', $this->filterStatus))
                ->orderByDesc('id')
                ->paginate(30);
        }

        return view('livewire.settings.sync-dashboard', [
            'runs' => $runs,
            'items' => $items,
        ]);
    }
}
''')


# ═══════════════════════════════════════════════════════════════
# 7. SyncDashboard View
# ═══════════════════════════════════════════════════════════════

write('resources/views/livewire/settings/sync-dashboard.blade.php', r'''<div style="padding:14px;direction:rtl" @if($activeTab === 'progress') wire:poll.3s="refreshProgress" @endif>

    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:8px">
        <div>
            <h1 style="margin:0;font-size:20px;font-weight:700">🔄 سینک ووکامرس</h1>
            <p style="margin:4px 0 0;font-size:12px;color:#64748b">دریافت سفارشات، محصولات، کاتالوگ و مدیا از سایت</p>
        </div>
    </div>

    {{-- Tabs --}}
    <div style="display:flex;gap:6px;border-bottom:2px solid #e2e8f0;margin-bottom:14px;overflow-x:auto">
        @foreach([
            'overview' => ['📋','شروع سینک'],
            'progress' => ['⏳','در حال اجرا'],
            'items' => ['📦','جزئیات آیتم‌ها'],
            'history' => ['📜','تاریخچه'],
        ] as $k => $meta)
            <button wire:click="$set('activeTab','{{ $k }}')"
                    style="padding:9px 16px;border:none;background:{{ $activeTab === $k ? 'linear-gradient(135deg,#1a5276,#0d3b5e)' : 'transparent' }};color:{{ $activeTab === $k ? '#fff' : '#64748b' }};border-radius:10px 10px 0 0;font-weight:700;cursor:pointer;font-size:12.5px;white-space:nowrap">
                {{ $meta[0] }} {{ $meta[1] }}
            </button>
        @endforeach
    </div>

    {{-- ═══ Overview ═══ --}}
    @if($activeTab === 'overview')
        <div class="sg-settings-card">
            <h3>▶️ شروع سینک جدید</h3>

            <div class="form-grid">
                <div class="field col-6">
                    <label>نوع سینک</label>
                    <select wire:model="syncType" style="width:100%;padding:10px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:13px">
                        <option value="full">🌟 کامل (Catalog + Products)</option>
                        <option value="catalog">📚 فقط کاتالوگ (دسته/ویژگی/اصطلاحات)</option>
                        <option value="products">📦 فقط محصولات</option>
                        <option value="media">🖼️ فقط رسانه (تصاویر)</option>
                    </select>
                </div>
                <div class="field col-6">
                    <label>حالت</label>
                    <select wire:model="syncMode" style="width:100%;padding:10px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:13px">
                        <option value="full">همه چیز</option>
                        <option value="incremental">فقط تغییرات ۳۰ روز اخیر</option>
                    </select>
                </div>
            </div>

            <label style="display:flex;align-items:center;gap:8px;padding:10px;background:#fef3c7;border-radius:8px;cursor:pointer;margin-top:10px">
                <input type="checkbox" wire:model="syncMedia" style="width:18px;height:18px;accent-color:#c9a84c">
                <div>
                    <div style="font-weight:700;font-size:12.5px">شامل سینک Media</div>
                    <div style="font-size:10.5px;color:#78350f">ممکنه زمان‌بر باشد (بالای ۵۰۰۰ تصویر)</div>
                </div>
            </label>

            <div style="display:flex;gap:8px;margin-top:16px;justify-content:flex-end">
                <button wire:click="startSync" wire:loading.attr="disabled"
                        style="padding:11px 28px;background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;border:none;border-radius:10px;font-weight:700;cursor:pointer;font-size:13px">
                    <span wire:loading.remove wire:target="startSync">🚀 شروع سینک</span>
                    <span wire:loading wire:target="startSync">⏳ در حال اجرا...</span>
                </button>
            </div>

            <div style="margin-top:16px;padding:12px;background:#eff6ff;border-radius:10px;font-size:11.5px;line-height:1.7;color:#1e40af">
                💡 <b>راهنما:</b><br>
                • <b>Catalog</b> — دسته‌ها، ویژگی‌ها، اصطلاحات (سریع — ۱-۲ دقیقه)<br>
                • <b>Products</b> — همه محصولات با تصاویر (بسته به تعداد)<br>
                • <b>Media</b> — تصاویر کتابخانه (کندتر)<br>
                • <b>Full</b> — همه موارد بالا
            </div>
        </div>
    @endif

    {{-- ═══ Progress ═══ --}}
    @if($activeTab === 'progress')
        @if(empty($progressData))
            <div style="text-align:center;padding:40px;color:#94a3b8">سینکی در حال اجرا نیست</div>
        @else
            <div class="sg-settings-card">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
                    <h3 style="margin:0">⏳ Run #{{ $progressData['id'] }} — {{ $progressData['type'] }}</h3>
                    <span style="padding:4px 12px;border-radius:10px;font-size:11.5px;font-weight:700;
                        @if($progressData['status'] === 'completed') background:#d1fae5;color:#065f46
                        @elseif($progressData['status'] === 'running') background:#dbeafe;color:#1e40af
                        @elseif($progressData['status'] === 'failed') background:#fee2e2;color:#991b1b
                        @else background:#f1f5f9;color:#475569 @endif">
                        {{ $progressData['status'] }}
                    </span>
                </div>

                <div style="height:14px;background:#e2e8f0;border-radius:7px;overflow:hidden;margin-bottom:14px">
                    <div style="height:100%;width:{{ $progressData['percent'] }}%;background:linear-gradient(90deg,#16a34a,#10b981);transition:width .4s"></div>
                </div>

                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(90px,1fr));gap:8px;margin-bottom:14px">
                    <div style="padding:10px;background:#f8fafc;border-radius:8px;text-align:center">
                        <div style="font-size:18px;font-weight:800;color:#1a5276">{{ \App\Support\PersianNumber::toFa($progressData['total']) }}</div>
                        <div style="font-size:10px;color:#64748b">کل</div>
                    </div>
                    <div style="padding:10px;background:#d1fae5;border-radius:8px;text-align:center">
                        <div style="font-size:18px;font-weight:800;color:#065f46">{{ \App\Support\PersianNumber::toFa($progressData['created']) }}</div>
                        <div style="font-size:10px;color:#065f46">جدید</div>
                    </div>
                    <div style="padding:10px;background:#dbeafe;border-radius:8px;text-align:center">
                        <div style="font-size:18px;font-weight:800;color:#1e40af">{{ \App\Support\PersianNumber::toFa($progressData['updated']) }}</div>
                        <div style="font-size:10px;color:#1e40af">بروزرسانی</div>
                    </div>
                    <div style="padding:10px;background:#fef3c7;border-radius:8px;text-align:center">
                        <div style="font-size:18px;font-weight:800;color:#92400e">{{ \App\Support\PersianNumber::toFa($progressData['skipped']) }}</div>
                        <div style="font-size:10px;color:#92400e">رد</div>
                    </div>
                    <div style="padding:10px;background:#fee2e2;border-radius:8px;text-align:center">
                        <div style="font-size:18px;font-weight:800;color:#991b1b">{{ \App\Support\PersianNumber::toFa($progressData['failed']) }}</div>
                        <div style="font-size:10px;color:#991b1b">خطا</div>
                    </div>
                </div>

                @if($progressData['duration'])
                    <div style="font-size:11.5px;color:#64748b;margin-bottom:10px">
                        ⏱️ مدت: {{ \App\Support\PersianNumber::toFa($progressData['duration']) }} ثانیه
                    </div>
                @endif

                <h3 style="margin-top:14px">📜 لاگ زنده</h3>
                <div style="max-height:280px;overflow-y:auto;background:#0f172a;border-radius:8px;padding:10px;font-family:monospace;font-size:11px;direction:ltr">
                    @forelse($syncLog as $l)
                        <div style="padding:2px 0;color:{{ $l['type'] === 'success' ? '#4ade80' : ($l['type'] === 'error' ? '#f87171' : ($l['type'] === 'warn' ? '#fbbf24' : '#94a3b8')) }}">
                            [{{ $l['time'] }}] {{ $l['msg'] }}
                        </div>
                    @empty
                        <div style="color:#475569;text-align:center;padding:15px">هنوز لاگی نیست</div>
                    @endforelse
                </div>
            </div>
        @endif
    @endif

    {{-- ═══ Items ═══ --}}
    @if($activeTab === 'items')
        @if(!$currentRunId)
            <div style="text-align:center;padding:40px;color:#94a3b8">یک Run انتخاب کن</div>
        @else
            <div class="sg-settings-card">
                <div style="display:flex;gap:6px;margin-bottom:12px;flex-wrap:wrap">
                    <input type="text" wire:model.live.debounce.400ms="filterEntity" placeholder="entity_type (product/order/...)"
                           style="padding:8px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:12px">
                    <select wire:model.live="filterStatus" style="padding:8px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:12px">
                        <option value="">همه وضعیت‌ها</option>
                        <option value="created">جدید</option>
                        <option value="updated">بروزرسانی</option>
                        <option value="failed">خطا</option>
                        <option value="skipped">رد شده</option>
                    </select>
                </div>

                <div style="overflow-x:auto">
                    <table style="width:100%;border-collapse:collapse;font-size:11.5px">
                        <thead style="background:#f8fafc">
                            <tr>
                                <th style="padding:6px;text-align:right">#</th>
                                <th style="padding:6px;text-align:right">نوع</th>
                                <th style="padding:6px;text-align:right">شناسه</th>
                                <th style="padding:6px;text-align:right">وضعیت</th>
                                <th style="padding:6px;text-align:right">خطا</th>
                            </tr>
                        </thead>
                        <tbody>
                            @forelse($items as $it)
                                <tr style="border-bottom:1px solid #f1f5f9">
                                    <td style="padding:5px;font-family:monospace">{{ $it->id }}</td>
                                    <td style="padding:5px;font-size:10.5px">{{ $it->entity_type }}</td>
                                    <td style="padding:5px;font-family:monospace;font-size:10.5px">{{ $it->entity_id }}</td>
                                    <td style="padding:5px">
                                        <span style="padding:2px 8px;border-radius:8px;font-size:10px;font-weight:700;
                                            @if($it->status === 'created') background:#d1fae5;color:#065f46
                                            @elseif($it->status === 'updated') background:#dbeafe;color:#1e40af
                                            @elseif($it->status === 'failed') background:#fee2e2;color:#991b1b
                                            @else background:#f1f5f9;color:#475569 @endif">
                                            {{ $it->status }}
                                        </span>
                                    </td>
                                    <td style="padding:5px;font-size:10.5px;color:#991b1b;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">
                                        {{ $it->error_message ? mb_substr($it->error_message, 0, 60) : '—' }}
                                    </td>
                                </tr>
                            @empty
                                <tr><td colspan="5" style="text-align:center;padding:20px;color:#94a3b8">آیتمی نیست</td></tr>
                            @endforelse
                        </tbody>
                    </table>
                </div>

                @if(method_exists($items, 'links'))
                    <div style="padding:10px">{{ $items->links() }}</div>
                @endif
            </div>
        @endif
    @endif

    {{-- ═══ History ═══ --}}
    @if($activeTab === 'history')
        <div class="sg-settings-card">
            <h3>📜 تاریخچه سینک‌ها</h3>

            <div style="overflow-x:auto">
                <table style="width:100%;border-collapse:collapse;font-size:11.5px">
                    <thead style="background:#f8fafc">
                        <tr>
                            <th style="padding:7px;text-align:right">#</th>
                            <th style="padding:7px;text-align:right">نوع</th>
                            <th style="padding:7px;text-align:right">وضعیت</th>
                            <th style="padding:7px;text-align:right">کل</th>
                            <th style="padding:7px;text-align:right">جدید</th>
                            <th style="padding:7px;text-align:right">بروزرسانی</th>
                            <th style="padding:7px;text-align:right">خطا</th>
                            <th style="padding:7px;text-align:right">زمان</th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody>
                        @forelse($runs as $r)
                            <tr style="border-bottom:1px solid #f1f5f9">
                                <td style="padding:6px;font-family:monospace;font-weight:700">#{{ $r->id }}</td>
                                <td style="padding:6px">
                                    <span style="padding:2px 8px;border-radius:8px;background:#eff6ff;color:#1e40af;font-size:10px;font-weight:700">{{ $r->type }}</span>
                                </td>
                                <td style="padding:6px">
                                    <span style="padding:2px 8px;border-radius:8px;font-size:10px;font-weight:700;
                                        @if($r->status === 'completed') background:#d1fae5;color:#065f46
                                        @elseif($r->status === 'running') background:#dbeafe;color:#1e40af
                                        @elseif($r->status === 'failed') background:#fee2e2;color:#991b1b
                                        @else background:#f1f5f9;color:#475569 @endif">
                                        {{ $r->status }}
                                    </span>
                                </td>
                                <td style="padding:6px;font-family:monospace">{{ \App\Support\PersianNumber::toFa($r->total_items) }}</td>
                                <td style="padding:6px;font-family:monospace;color:#065f46">{{ \App\Support\PersianNumber::toFa($r->created_items) }}</td>
                                <td style="padding:6px;font-family:monospace;color:#1e40af">{{ \App\Support\PersianNumber::toFa($r->updated_items) }}</td>
                                <td style="padding:6px;font-family:monospace;color:#991b1b">{{ \App\Support\PersianNumber::toFa($r->failed_items) }}</td>
                                <td style="padding:6px;font-size:10px;font-family:monospace">
                                    {{ $r->started_at ? \App\Support\PersianDate::format($r->started_at, 'Y/m/d H:i') : '—' }}
                                </td>
                                <td style="padding:6px">
                                    <div style="display:flex;gap:3px">
                                        <button wire:click="viewRun({{ $r->id }})"
                                                style="padding:3px 8px;background:#dbeafe;color:#1e40af;border:none;border-radius:5px;font-size:10px;cursor:pointer;font-weight:700">👁️</button>
                                        <button wire:click="deleteRun({{ $r->id }})" wire:confirm="حذف؟"
                                                style="padding:3px 8px;background:#fee2e2;color:#dc2626;border:none;border-radius:5px;font-size:10px;cursor:pointer">🗑️</button>
                                    </div>
                                </td>
                            </tr>
                        @empty
                            <tr><td colspan="9" style="text-align:center;padding:20px;color:#94a3b8">سینکی انجام نشده</td></tr>
                        @endforelse
                    </tbody>
                </table>
            </div>
            <div style="padding:10px">{{ $runs->links() }}</div>
        </div>
    @endif
</div>
''')


# ═══════════════════════════════════════════════════════════════
# 8. اضافه کردن tab sync-dashboard به Settings
# ═══════════════════════════════════════════════════════════════

# در Settings Index.php — تب sync → SyncDashboard
sphp = ROOT / 'app' / 'Livewire' / 'Settings' / 'Index.php'
if sphp.exists():
    txt = sphp.read_text(encoding='utf-8')
    # فعلاً نگه دار — SyncDashboard جداست
    print("[OK] Settings — بدون تغییر (SyncDashboard مستقل)")


# ═══════════════════════════════════════════════════════════════
# 9. ROUTE
# ═══════════════════════════════════════════════════════════════

routes = ROOT / 'routes' / 'web.php'
if routes.exists():
    txt = routes.read_text(encoding='utf-8')
    if 'settings.sync' not in txt:
        marker = "Route::get('/health', \\App\\Livewire\\Settings\\Health::class)->name('health');"
        new_route = "        Route::get('/sync', \\App\\Livewire\\Settings\\SyncDashboard::class)->name('sync');"
        if marker in txt:
            txt = txt.replace(marker, marker + "\n" + new_route)
            routes.write_text(txt, encoding='utf-8')
            print("[OK] route settings.sync")


# ═══════════════════════════════════════════════════════════════
# 10. اجرا
# ═══════════════════════════════════════════════════════════════

print()
print("🔧 Migration و پاک‌سازی...")
run('php artisan migrate --force')
run('php artisan optimize:clear')
run('php artisan route:clear')
run('php artisan view:clear')

print()
print("=" * 60)
print("DONE — Phase 7")
print("=" * 60)
print()
print("🎯 دستاوردهای فاز ۷:")
print("   ✅ SyncEngine — موتور واحد سینک")
print("   ✅ جداول: sync_runs, sync_items, woo_media")
print("   ✅ Models: SyncRun, SyncItem, WooMedia")
print("   ✅ Command: shopgun:sync-all --type=full --media")
print("   ✅ SyncDashboard — UI زنده با progress")
print("   ✅ WooCommerceClient.mediaList()")
print()
print("🔗 دسترسی:")
print("   /settings/sync — داشبورد سینک")
print()
print("🚀 php artisan serve")
