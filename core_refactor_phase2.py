#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShopGun V2 - Core Refactor Phase 2
====================================
- WooCatalog Sync (categories/attributes/terms در DB لوکال)
- ProductResolver (SKU مرکزی)
- Product Read Model
- Preview/Diff UI برای Bulk
- ارتقای BulkCreate برای استفاده از BulkEngine
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
# 1. MIGRATION — جداول Catalog
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
        // ═══ woo_categories ═══
        if (!Schema::hasTable('woo_categories')) {
            Schema::create('woo_categories', function (Blueprint $table) {
                $table->id();
                $table->unsignedBigInteger('woo_id')->unique()->index();
                $table->unsignedBigInteger('parent_woo_id')->nullable()->index();
                $table->string('name');
                $table->string('slug')->index();
                $table->text('description')->nullable();
                $table->unsignedInteger('count')->default(0);
                $table->json('image')->nullable();
                $table->integer('menu_order')->default(0);
                $table->timestamp('synced_at')->nullable();
                $table->timestamps();
            });
        }

        // ═══ woo_attributes ═══
        if (!Schema::hasTable('woo_attributes')) {
            Schema::create('woo_attributes', function (Blueprint $table) {
                $table->id();
                $table->unsignedBigInteger('woo_id')->unique()->index();
                $table->string('name');
                $table->string('slug')->unique()->index();
                $table->string('type', 30)->default('select');
                $table->string('order_by', 30)->default('menu_order');
                $table->boolean('has_archives')->default(false);
                $table->timestamp('synced_at')->nullable();
                $table->timestamps();
            });
        }

        // ═══ woo_attribute_terms ═══
        if (!Schema::hasTable('woo_attribute_terms')) {
            Schema::create('woo_attribute_terms', function (Blueprint $table) {
                $table->id();
                $table->unsignedBigInteger('woo_id')->unique()->index();
                $table->unsignedBigInteger('attribute_woo_id')->index();
                $table->string('name');
                $table->string('slug')->index();
                $table->text('description')->nullable();
                $table->unsignedInteger('count')->default(0);
                $table->integer('menu_order')->default(0);
                $table->timestamp('synced_at')->nullable();
                $table->timestamps();

                $table->index(['attribute_woo_id', 'name']);
            });
        }

        // ═══ woo_users ═══
        if (!Schema::hasTable('woo_users')) {
            Schema::create('woo_users', function (Blueprint $table) {
                $table->id();
                $table->unsignedBigInteger('woo_id')->unique()->index();
                $table->string('name');
                $table->string('slug')->nullable();
                $table->string('email')->nullable();
                $table->json('roles')->nullable();
                $table->timestamp('synced_at')->nullable();
                $table->timestamps();
            });
        }

        // ═══ product_identity — نگاشت SKU مرکزی ═══
        if (!Schema::hasTable('product_identities')) {
            Schema::create('product_identities', function (Blueprint $table) {
                $table->id();
                $table->string('sku', 100)->unique()->index();
                $table->unsignedBigInteger('local_product_id')->nullable()->index();
                $table->unsignedBigInteger('woo_product_id')->nullable()->index();
                $table->string('canonical_name')->nullable();
                $table->string('canonical_slug')->nullable();
                $table->decimal('last_known_price', 15, 2)->nullable();
                $table->decimal('last_known_weight', 10, 3)->nullable();
                $table->json('last_known_woo_data')->nullable();
                $table->unsignedInteger('sync_count')->default(0);
                $table->timestamp('last_synced_at')->nullable();
                $table->timestamps();
            });
        }
    }

    public function down(): void
    {
        Schema::dropIfExists('product_identities');
        Schema::dropIfExists('woo_users');
        Schema::dropIfExists('woo_attribute_terms');
        Schema::dropIfExists('woo_attributes');
        Schema::dropIfExists('woo_categories');
    }
};
'''

write(f'database/migrations/{ts}_create_woo_catalog_tables.php', MIGRATION)


# ═══════════════════════════════════════════════════════════════
# 2. MODELS
# ═══════════════════════════════════════════════════════════════

write('app/Models/WooCategory.php', '''<?php

namespace App\\Models;

use Illuminate\\Database\\Eloquent\\Model;

class WooCategory extends Model
{
    protected $table = 'woo_categories';

    protected $fillable = [
        'woo_id', 'parent_woo_id', 'name', 'slug', 'description',
        'count', 'image', 'menu_order', 'synced_at',
    ];

    protected $casts = [
        'image' => 'array',
        'synced_at' => 'datetime',
    ];

    public function scopeOrdered($q)
    {
        return $q->orderBy('menu_order')->orderBy('name');
    }
}
''')

write('app/Models/WooAttribute.php', '''<?php

namespace App\\Models;

use Illuminate\\Database\\Eloquent\\Model;
use Illuminate\\Database\\Eloquent\\Relations\\HasMany;

class WooAttribute extends Model
{
    protected $table = 'woo_attributes';

    protected $fillable = [
        'woo_id', 'name', 'slug', 'type', 'order_by', 'has_archives', 'synced_at',
    ];

    protected $casts = [
        'has_archives' => 'boolean',
        'synced_at' => 'datetime',
    ];

    public function terms(): HasMany
    {
        return $this->hasMany(WooAttributeTerm::class, 'attribute_woo_id', 'woo_id')
            ->orderBy('menu_order')
            ->orderBy('name');
    }
}
''')

write('app/Models/WooAttributeTerm.php', '''<?php

namespace App\\Models;

use Illuminate\\Database\\Eloquent\\Model;

class WooAttributeTerm extends Model
{
    protected $table = 'woo_attribute_terms';

    protected $fillable = [
        'woo_id', 'attribute_woo_id', 'name', 'slug', 'description',
        'count', 'menu_order', 'synced_at',
    ];

    protected $casts = [
        'synced_at' => 'datetime',
    ];
}
''')

write('app/Models/WooUser.php', '''<?php

namespace App\\Models;

use Illuminate\\Database\\Eloquent\\Model;

class WooUser extends Model
{
    protected $table = 'woo_users';

    protected $fillable = ['woo_id', 'name', 'slug', 'email', 'roles', 'synced_at'];
    protected $casts = ['roles' => 'array', 'synced_at' => 'datetime'];
}
''')

write('app/Models/ProductIdentity.php', '''<?php

namespace App\\Models;

use Illuminate\\Database\\Eloquent\\Model;

class ProductIdentity extends Model
{
    protected $fillable = [
        'sku', 'local_product_id', 'woo_product_id',
        'canonical_name', 'canonical_slug',
        'last_known_price', 'last_known_weight',
        'last_known_woo_data', 'sync_count', 'last_synced_at',
    ];

    protected $casts = [
        'last_known_woo_data' => 'array',
        'last_known_price' => 'decimal:2',
        'last_known_weight' => 'decimal:3',
        'last_synced_at' => 'datetime',
    ];

    public function getWooEditUrlAttribute(): ?string
    {
        if (!$this->woo_product_id) return null;
        $site = rtrim((string) AppSetting::get('commerce_url', ''), '/');
        return $site ? "{$site}/wp-admin/post.php?post={$this->woo_product_id}&action=edit" : null;
    }
}
''')


# ═══════════════════════════════════════════════════════════════
# 3. WooCatalogService — Sync کل کاتالوگ
# ═══════════════════════════════════════════════════════════════

write('app/Application/Woo/WooCatalogService.php', r'''<?php

namespace App\Application\Woo;

use App\Infrastructure\WooCommerce\WooCommerceClient;
use App\Models\WooAttribute;
use App\Models\WooAttributeTerm;
use App\Models\WooCategory;
use App\Models\WooUser;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Log;

/**
 * ★ WooCatalogService
 * سینک کردن دسته‌ها، ویژگی‌ها، اصطلاحات، کاربران از ووکامرس به DB لوکال
 *
 * بعد از sync، همه ماژول‌ها از همین cache لوکال استفاده می‌کنند
 * نه اینکه هر بار HTTP بزنند.
 */
class WooCatalogService
{
    protected WooCommerceClient $woo;

    public function __construct()
    {
        $this->woo = (new WooCommerceClient())->module('catalog');
    }

    /**
     * سینک همه کاتالوگ در یک عملیات
     */
    public function syncAll(): array
    {
        $report = [
            'categories' => 0,
            'attributes' => 0,
            'terms' => 0,
            'users' => 0,
            'errors' => [],
        ];

        try {
            $report['categories'] = $this->syncCategories();
        } catch (\Throwable $e) {
            $report['errors'][] = 'Categories: ' . $e->getMessage();
        }

        try {
            $attrs = $this->syncAttributes();
            $report['attributes'] = count($attrs);

            foreach ($attrs as $attr) {
                try {
                    $report['terms'] += $this->syncAttributeTerms($attr['woo_id']);
                } catch (\Throwable $e) {
                    $report['errors'][] = "Terms of {$attr['name']}: " . $e->getMessage();
                }
            }
        } catch (\Throwable $e) {
            $report['errors'][] = 'Attributes: ' . $e->getMessage();
        }

        try {
            $report['users'] = $this->syncUsers();
        } catch (\Throwable $e) {
            $report['errors'][] = 'Users: ' . $e->getMessage();
        }

        return $report;
    }

    // ═══════════════════════════════════════════════════════════
    public function syncCategories(): int
    {
        $count = 0;
        $page = 1;

        while ($page <= 10) {
            $r = $this->woo->categories(['per_page' => 100, 'page' => $page]);
            if (!$r['ok']) break;

            $items = $r['body'] ?? [];
            if (empty($items) || !is_array($items)) break;

            DB::transaction(function () use ($items, &$count) {
                foreach ($items as $c) {
                    WooCategory::updateOrCreate(
                        ['woo_id' => $c['id']],
                        [
                            'parent_woo_id' => $c['parent'] ?? 0,
                            'name' => $c['name'] ?? '',
                            'slug' => $c['slug'] ?? '',
                            'description' => $c['description'] ?? null,
                            'count' => (int) ($c['count'] ?? 0),
                            'image' => $c['image'] ?? null,
                            'menu_order' => (int) ($c['menu_order'] ?? 0),
                            'synced_at' => now(),
                        ]
                    );
                    $count++;
                }
            });

            if (count($items) < 100) break;
            $page++;
        }

        return $count;
    }

    // ═══════════════════════════════════════════════════════════
    public function syncAttributes(): array
    {
        $r = $this->woo->attributes();
        if (!$r['ok']) {
            throw new \RuntimeException($r['error'] ?? 'خطا در دریافت ویژگی‌ها');
        }

        $items = $r['body'] ?? [];
        $result = [];

        DB::transaction(function () use ($items, &$result) {
            foreach ($items as $a) {
                $model = WooAttribute::updateOrCreate(
                    ['woo_id' => $a['id']],
                    [
                        'name' => $a['name'] ?? '',
                        'slug' => $a['slug'] ?? '',
                        'type' => $a['type'] ?? 'select',
                        'order_by' => $a['order_by'] ?? 'menu_order',
                        'has_archives' => (bool) ($a['has_archives'] ?? false),
                        'synced_at' => now(),
                    ]
                );
                $result[] = [
                    'woo_id' => $a['id'],
                    'name' => $model->name,
                    'slug' => $model->slug,
                ];
            }
        });

        return $result;
    }

    // ═══════════════════════════════════════════════════════════
    public function syncAttributeTerms(int $attrWooId): int
    {
        $r = $this->woo->attributeTerms($attrWooId);
        if (!$r['ok']) return 0;

        $items = $r['body'] ?? [];
        if (empty($items) || !is_array($items)) return 0;

        $count = 0;
        DB::transaction(function () use ($items, $attrWooId, &$count) {
            foreach ($items as $t) {
                WooAttributeTerm::updateOrCreate(
                    ['woo_id' => $t['id']],
                    [
                        'attribute_woo_id' => $attrWooId,
                        'name' => $t['name'] ?? '',
                        'slug' => $t['slug'] ?? '',
                        'description' => $t['description'] ?? null,
                        'count' => (int) ($t['count'] ?? 0),
                        'menu_order' => (int) ($t['menu_order'] ?? 0),
                        'synced_at' => now(),
                    ]
                );
                $count++;
            }
        });

        return $count;
    }

    // ═══════════════════════════════════════════════════════════
    public function syncUsers(): int
    {
        $r = $this->woo->users();
        if (!$r['ok']) return 0;

        $items = $r['body'] ?? [];
        if (empty($items) || !is_array($items)) return 0;

        $count = 0;
        DB::transaction(function () use ($items, &$count) {
            foreach ($items as $u) {
                WooUser::updateOrCreate(
                    ['woo_id' => $u['id']],
                    [
                        'name' => $u['name'] ?? '',
                        'slug' => $u['slug'] ?? '',
                        'email' => $u['email'] ?? null,
                        'roles' => $u['roles'] ?? [],
                        'synced_at' => now(),
                    ]
                );
                $count++;
            }
        });

        return $count;
    }

    // ═══════════════════════════════════════════════════════════
    public function getLastSync(): ?string
    {
        return WooCategory::max('synced_at')
            ?? WooAttribute::max('synced_at');
    }
}
''')


# ═══════════════════════════════════════════════════════════════
# 4. ProductResolver — نگاشت SKU مرکزی
# ═══════════════════════════════════════════════════════════════

write('app/Application/Products/ProductResolver.php', r'''<?php

namespace App\Application\Products;

use App\Infrastructure\WooCommerce\WooCommerceClient;
use App\Models\ProductIdentity;
use App\Models\Certificate;
use App\Models\OrderItem;
use App\Models\Product;
use Illuminate\Support\Facades\Log;

/**
 * ★ ProductResolver
 * SKU مرکزی — همه ماژول‌ها برای یافتن محصول از این استفاده می‌کنند
 *
 * - resolve(sku) → ProductIdentity یا null
 * - enrich(sku) → گرفتن اطلاعات از Woo در صورت نیاز
 * - certificates(sku) → شناسنامه‌های مرتبط
 * - orderItems(sku) → سفارشات مرتبط
 */
class ProductResolver
{
    protected WooCommerceClient $woo;

    public function __construct()
    {
        $this->woo = (new WooCommerceClient())->module('resolver');
    }

    /**
     * یافتن یا ساخت ProductIdentity
     */
    public function resolve(string $sku, bool $fetchFromWooIfMissing = false): ?ProductIdentity
    {
        $sku = trim($sku);
        if ($sku === '') return null;

        $identity = ProductIdentity::where('sku', $sku)->first();
        if ($identity) return $identity;

        // اگه در local Product بود
        $local = Product::where('sku', $sku)->first();
        if ($local) {
            return $this->touchFromLocal($local);
        }

        // از Woo بگیر
        if ($fetchFromWooIfMissing) {
            return $this->enrichFromWoo($sku);
        }

        return null;
    }

    /**
     * بروزرسانی از Product local
     */
    public function touchFromLocal(Product $product): ProductIdentity
    {
        return ProductIdentity::updateOrCreate(
            ['sku' => $product->sku],
            [
                'local_product_id' => $product->id,
                'woo_product_id' => $product->wc_id,
                'canonical_name' => $product->name,
                'last_known_price' => $product->price,
                'last_known_weight' => $product->weight,
                'last_synced_at' => now(),
            ]
        );
    }

    /**
     * غنی‌سازی از Woo
     */
    public function enrichFromWoo(string $sku): ?ProductIdentity
    {
        try {
            $r = $this->woo->productBySku($sku);
            if (!$r['ok'] || empty($r['body'])) return null;

            $p = $r['body'][0] ?? null;
            if (!$p) return null;

            return $this->touchFromWoo($p);
        } catch (\Throwable $e) {
            Log::warning("ProductResolver enrich failed for {$sku}: " . $e->getMessage());
            return null;
        }
    }

    /**
     * بروزرسانی از Woo data
     */
    public function touchFromWoo(array $wooData): ProductIdentity
    {
        $sku = $wooData['sku'] ?? null;
        if (!$sku) throw new \InvalidArgumentException('SKU یافت نشد');

        $existing = ProductIdentity::where('sku', $sku)->first();

        return ProductIdentity::updateOrCreate(
            ['sku' => $sku],
            [
                'woo_product_id' => $wooData['id'] ?? null,
                'canonical_name' => $wooData['name'] ?? null,
                'canonical_slug' => $wooData['slug'] ?? null,
                'last_known_price' => $wooData['price'] ?? null,
                'last_known_weight' => $wooData['weight'] ?? null,
                'last_known_woo_data' => $wooData,
                'sync_count' => ($existing?->sync_count ?? 0) + 1,
                'last_synced_at' => now(),
            ]
        );
    }

    /**
     * شناسنامه‌های مرتبط با SKU
     */
    public function certificates(string $sku): \Illuminate\Database\Eloquent\Collection
    {
        return Certificate::where('sku', $sku)->get();
    }

    /**
     * سفارشات مرتبط با SKU
     */
    public function orderItems(string $sku): \Illuminate\Database\Eloquent\Collection
    {
        return OrderItem::where('sku', $sku)->with('order')->get();
    }

    /**
     * Snapshot کامل برای Preview/Diff
     */
    public function snapshot(string $sku): array
    {
        $identity = $this->resolve($sku, true);

        return [
            'sku' => $sku,
            'in_local' => (bool) $identity?->local_product_id,
            'in_woo' => (bool) $identity?->woo_product_id,
            'woo_id' => $identity?->woo_product_id,
            'canonical_name' => $identity?->canonical_name,
            'last_price' => $identity?->last_known_price,
            'last_weight' => $identity?->last_known_weight,
            'woo_data' => $identity?->last_known_woo_data,
            'edit_url' => $identity?->woo_edit_url,
            'certificates_count' => $this->certificates($sku)->count(),
            'order_items_count' => $this->orderItems($sku)->count(),
        ];
    }
}
''')


# ═══════════════════════════════════════════════════════════════
# 5. COMMAND — sync Woo catalog
# ═══════════════════════════════════════════════════════════════

write('app/Console/Commands/SyncWooCatalog.php', '''<?php

namespace App\\Console\\Commands;

use App\\Application\\Woo\\WooCatalogService;
use App\\Models\\AppSetting;
use Illuminate\\Console\\Command;

class SyncWooCatalog extends Command
{
    protected $signature = 'shopgun:sync-catalog';
    protected $description = 'سینک دسته‌ها، ویژگی‌ها، اصطلاحات و کاربران ووکامرس';

    public function handle(): int
    {
        @set_time_limit(600);

        $this->info('🔄 شروع سینک کاتالوگ...');

        try {
            $service = new WooCatalogService();
            $report = $service->syncAll();

            $this->newLine();
            $this->table(['مورد', 'تعداد'], [
                ['دسته‌ها', $report['categories']],
                ['ویژگی‌ها', $report['attributes']],
                ['اصطلاحات', $report['terms']],
                ['کاربران', $report['users']],
            ]);

            if (!empty($report['errors'])) {
                $this->newLine();
                $this->warn('خطاها:');
                foreach ($report['errors'] as $err) {
                    $this->line('  • ' . $err);
                }
            }

            AppSetting::put('woo_catalog_last_sync', now()->toIso8601String(), 'commerce');
            \\Illuminate\\Support\\Facades\\Cache::forget('app_settings_all');

            $this->newLine();
            $this->info('✅ سینک کامل شد');
            return 0;

        } catch (\\Throwable $e) {
            $this->error('❌ ' . $e->getMessage());
            return 1;
        }
    }
}
''')


# ═══════════════════════════════════════════════════════════════
# 6. SETTINGS — Property برای آخرین سینک کاتالوگ
# ═══════════════════════════════════════════════════════════════

sphp = ROOT / 'app' / 'Livewire' / 'Settings' / 'Index.php'
if sphp.exists():
    txt = sphp.read_text(encoding='utf-8')

    if 'public string $woo_catalog_last_sync' not in txt:
        txt = txt.replace(
            "public string $woo_sync_status = '';",
            "public string $woo_sync_status = '';\n    public string $woo_catalog_last_sync = '';\n    public array $woo_catalog_stats = [];"
        )

    if "$this->woo_catalog_last_sync = (string) AppSetting::get" not in txt:
        txt = txt.replace(
            "$this->woo_last_cust_sync = (string) AppSetting::get('woo_last_cust_sync', '');",
            "$this->woo_last_cust_sync = (string) AppSetting::get('woo_last_cust_sync', '');\n            $this->woo_catalog_last_sync = (string) AppSetting::get('woo_catalog_last_sync', '');"
        )

    if 'public function syncWooCatalog' not in txt:
        method = '''
    public function syncWooCatalog(): void
    {
        $this->woo_syncing = true;
        $this->woo_sync_status = '⏳ در حال سینک کاتالوگ...';
        @set_time_limit(600);

        try {
            \\Illuminate\\Support\\Facades\\Artisan::call('shopgun:sync-catalog');
            $output = \\Illuminate\\Support\\Facades\\Artisan::output();
            $this->woo_sync_status = '✅ کاتالوگ سینک شد';
            $this->woo_catalog_last_sync = now()->toIso8601String();
            AppSetting::put('woo_catalog_last_sync', $this->woo_catalog_last_sync, 'commerce');
            Cache::forget('app_settings_all');
        } catch (\\Throwable $e) {
            $this->woo_sync_status = '❌ ' . $e->getMessage();
        }

        $this->woo_syncing = false;
    }
'''
        txt = txt.replace('    public function render()', method + '\n    public function render()', 1)

    sphp.write_text(txt, encoding='utf-8')
    print("[OK] Settings/Index.php - syncWooCatalog")


# ═══════════════════════════════════════════════════════════════
# 7. SETTINGS BLADE — دکمه سینک کاتالوگ
# ═══════════════════════════════════════════════════════════════

sv = ROOT / 'resources' / 'views' / 'livewire' / 'settings' / 'index.blade.php'
if sv.exists():
    txt = sv.read_text(encoding='utf-8')

    CATALOG_BTN = '''
                    <button type="button" wire:click="syncWooCatalog" wire:loading.attr="disabled"
                            style="padding:7px 16px;background:linear-gradient(135deg,#7c3aed,#5b21b6);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">
                        <span wire:loading.remove wire:target="syncWooCatalog">🔄 سینک کاتالوگ (دسته/ویژگی/کاربر)</span>
                        <span wire:loading wire:target="syncWooCatalog">⏳...</span>
                    </button>
'''

    # درج قبل از بستن بخش دکمه‌های sync
    marker = '<button type="button" wire:click="syncCustomersFromWoo" wire:loading.attr="disabled"'
    if marker in txt and '🔄 سینک کاتالوگ' not in txt:
        txt = txt.replace(marker, CATALOG_BTN + '\n                    ' + marker, 1)
        sv.write_text(txt, encoding='utf-8')
        print("[OK] settings blade - sync catalog button")


# ═══════════════════════════════════════════════════════════════
# 8. BulkCreate — ارتقا برای استفاده از BulkEngine + Preview
# ═══════════════════════════════════════════════════════════════

# نگه داشتن نسخه قدیمی برای fallback — نسخه جدید در ادامه نوشته می‌شود
write('app/Livewire/Products/BulkCreate.php', r'''<?php

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
''')


# ═══════════════════════════════════════════════════════════════
# 9. VIEW — اضافه کردن Preview tab
# ═══════════════════════════════════════════════════════════════

bv = ROOT / 'resources' / 'views' / 'livewire' / 'products' / 'bulk-create.blade.php'
if bv.exists():
    txt = bv.read_text(encoding='utf-8')

    # تغییر دکمه اصلی: تبدیل «ارسال» به «پیش‌نمایش»
    txt = txt.replace(
        '''@if($tab === 'form')
                <button type="button" wire:click="sendBatch" wire:loading.attr="disabled"
                        wire:confirm="ارسال محصولات انتخاب‌شده؟"
                        style="padding:7px 20px;background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px;height:36px">
                    <span wire:loading.remove wire:target="sendBatch">🚀 ارسال</span>
                    <span wire:loading wire:target="sendBatch">⏳...</span>
                </button>
            @endif''',
        '''@if($tab === 'form')
                <button type="button" wire:click="buildPreview" wire:loading.attr="disabled"
                        style="padding:7px 20px;background:linear-gradient(135deg,#7c3aed,#5b21b6);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px;height:36px">
                    <span wire:loading.remove wire:target="buildPreview">👁️ پیش‌نمایش</span>
                    <span wire:loading wire:target="buildPreview">⏳...</span>
                </button>
            @endif'''
    )

    # اضافه کردن section Preview قبل از tab form close
    PREVIEW_SECTION = '''
        {{-- ══════ Preview Section ══════ --}}
        @if($showing_preview)
            <div class="sg-settings-card" style="margin-bottom:14px;border:2px solid #7c3aed;background:linear-gradient(135deg,#faf5ff,#f3e8ff)">
                <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:12px">
                    <h3 style="margin:0;color:#5b21b6">👁️ پیش‌نمایش ارسال</h3>
                    <button wire:click="$set('showing_preview', false)"
                            style="background:#fff;color:#7c3aed;border:1.5px solid #c4b5fd;border-radius:8px;padding:5px 12px;font-weight:700;cursor:pointer;font-size:11px">✕ بستن</button>
                </div>

                @if(($run_summary['status'] ?? '') === 'processing')
                    <div style="text-align:center;padding:20px;color:#7c3aed;font-size:13px">{{ $run_summary['msg'] }}</div>
                @elseif(($run_summary['status'] ?? '') === 'error')
                    <div style="padding:10px;background:#fee2e2;color:#991b1b;border-radius:8px;font-size:12px">{{ $run_summary['msg'] }}</div>
                @else
                    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:12px">
                        <div style="padding:10px;background:#fff;border-radius:8px;text-align:center">
                            <div style="font-size:22px;font-weight:800;color:#1a5276">{{ \\App\\Support\\PersianNumber::toFa($run_summary['total'] ?? 0) }}</div>
                            <div style="font-size:10.5px;color:#64748b;font-weight:700">کل</div>
                        </div>
                        <div style="padding:10px;background:#d1fae5;border-radius:8px;text-align:center">
                            <div style="font-size:22px;font-weight:800;color:#065f46">{{ \\App\\Support\\PersianNumber::toFa($run_summary['valid'] ?? 0) }}</div>
                            <div style="font-size:10.5px;color:#065f46;font-weight:700">معتبر</div>
                        </div>
                        <div style="padding:10px;background:#fef3c7;border-radius:8px;text-align:center">
                            <div style="font-size:22px;font-weight:800;color:#92400e">{{ \\App\\Support\\PersianNumber::toFa($run_summary['warnings'] ?? 0) }}</div>
                            <div style="font-size:10.5px;color:#92400e;font-weight:700">هشدار</div>
                        </div>
                    </div>

                    <div style="max-height:300px;overflow-y:auto;border:1px solid #ddd6fe;border-radius:8px;background:#fff">
                        <table style="width:100%;border-collapse:collapse;font-size:11px">
                            <thead style="background:#f3e8ff;position:sticky;top:0">
                                <tr>
                                    <th style="padding:5px;text-align:right;color:#5b21b6">SKU</th>
                                    <th style="padding:5px;text-align:right;color:#5b21b6">عنوان</th>
                                    <th style="padding:5px;text-align:right;color:#5b21b6">وضعیت</th>
                                    <th style="padding:5px;text-align:right;color:#5b21b6">هشدارها</th>
                                </tr>
                            </thead>
                            <tbody>
                                @foreach($preview_data as $pv)
                                    <tr style="border-bottom:1px solid #f3e8ff">
                                        <td style="padding:5px;font-family:monospace;font-weight:700">{{ $pv['sku'] }}</td>
                                        <td style="padding:5px;font-size:10.5px">{{ \\Illuminate\\Support\\Str::limit($pv['title_fa'], 30) }}</td>
                                        <td style="padding:5px">
                                            @if($pv['exists_in_woo'])
                                                <span style="background:#fef3c7;color:#92400e;padding:1px 6px;border-radius:8px;font-size:9.5px;font-weight:700">🔄 موجود</span>
                                            @else
                                                <span style="background:#d1fae5;color:#065f46;padding:1px 6px;border-radius:8px;font-size:9.5px;font-weight:700">✨ جدید</span>
                                            @endif
                                        </td>
                                        <td style="padding:5px;font-size:10px;color:#92400e">
                                            @foreach($pv['warnings'] as $w)
                                                <div>⚠️ {{ $w }}</div>
                                            @endforeach
                                        </td>
                                    </tr>
                                @endforeach
                            </tbody>
                        </table>
                    </div>

                    <div style="display:flex;gap:8px;margin-top:14px;justify-content:flex-end;flex-wrap:wrap">
                        <button wire:click="$set('showing_preview', false)"
                                style="padding:9px 18px;background:#fff;color:#475569;border:1.5px solid #cbd5e1;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">انصراف</button>
                        <button wire:click="confirmSend" wire:loading.attr="disabled"
                                wire:confirm="ارسال {{ $run_summary['valid'] ?? 0 }} محصول به صف؟"
                                style="padding:9px 22px;background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">
                            <span wire:loading.remove wire:target="confirmSend">🚀 ارسال به صف ({{ \\App\\Support\\PersianNumber::toFa($run_summary['valid'] ?? 0) }} آیتم)</span>
                            <span wire:loading wire:target="confirmSend">⏳...</span>
                        </button>
                    </div>
                @endif
            </div>
        @endif

'''

    # درج قبل از "Bulk SKU add"
    marker = '{{-- Bulk SKU add --}}'
    if marker in txt and 'Preview Section' not in txt:
        txt = txt.replace(marker, PREVIEW_SECTION + marker, 1)
        bv.write_text(txt, encoding='utf-8')
        print("[OK] bulk-create.blade.php — preview section")

    # تبدیل sendBatch در queue tab به دکمه‌های جدید
    # (این بخش را نگه می‌داریم چون refreshProgress برای queue هست)


# ═══════════════════════════════════════════════════════════════
# 10. اضافه کردن refresh auto در queue tab
# ═══════════════════════════════════════════════════════════════

# در Queue tab، wire:poll اضافه کنیم
bv2 = ROOT / 'resources' / 'views' / 'livewire' / 'products' / 'bulk-create.blade.php'
if bv2.exists():
    txt = bv2.read_text(encoding='utf-8')
    if 'wire:poll' not in txt:
        # در div اصلی Queue tab
        txt = txt.replace(
            "@if($tab === 'queue')\n        <div class=\"sg-settings-card\">\n            <h3>📊 گزارش پیشرفت</h3>",
            "@if($tab === 'queue')\n        <div class=\"sg-settings-card\" wire:poll.3s=\"refreshProgress\">\n            <h3>📊 گزارش پیشرفت (auto-refresh)</h3>"
        )
        bv2.write_text(txt, encoding='utf-8')
        print("[OK] bulk-create — auto refresh")


# ═══════════════════════════════════════════════════════════════
# 11. اجرا
# ═══════════════════════════════════════════════════════════════

print()
print("🔧 Migration و پاک‌سازی...")
run('php artisan migrate --force')
run('php artisan optimize:clear')
run('php artisan route:clear')
run('php artisan view:clear')

print()
print("=" * 60)
print("DONE — Phase 2")
print("=" * 60)
print()
print("🎯 هسته‌های جدید:")
print("   ✅ WooCatalogService — سینک دسته/ویژگی/اصطلاحات/کاربران")
print("   ✅ جداول: woo_categories, woo_attributes, woo_attribute_terms, woo_users")
print("   ✅ ProductResolver — SKU مرکزی")
print("   ✅ جدول: product_identities")
print("   ✅ Preview/Diff UI در Bulk")
print("   ✅ Command: shopgun:sync-catalog")
print()
print("🚀 مراحل بعدی:")
print("   1. php artisan shopgun:sync-catalog")
print("   2. php artisan queue:work --queue=bulk")
print("   3. برو /products/bulk — دکمه «پیش‌نمایش» رو بزن")
