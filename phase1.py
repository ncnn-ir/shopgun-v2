#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║  ShopGun V2 — فاز ۱                                          ║
║  حذف localStorage + Customer/Product کامل                    ║
║  سازنده: گروه هنری اقاقیا                                     ║
╚══════════════════════════════════════════════════════════════╝
"""
import shutil
from pathlib import Path
from datetime import datetime

PROJECT = Path(r"D:\prodo\shopgun-v2.1")
if not PROJECT.exists():
    PROJECT = Path(input("مسیر پروژه: ").strip().strip('"'))
    if not PROJECT.exists():
        print("❌ مسیر پیدا نشد"); exit(1)

# ═══════════════════════════════════════════════════════════════
# ابزار
# ═══════════════════════════════════════════════════════════════
def write(rel, content):
    full = PROJECT / rel
    full.parent.mkdir(parents=True, exist_ok=True)
    with open(full, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print(f"  ✓ {rel}")

def backup(rel):
    src = PROJECT / rel
    if not src.exists(): return
    bd = PROJECT / "storage/backups"; bd.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(src, bd / f"{src.stem}_{ts}.bak")

def append_if_missing(rel, marker, content):
    full = PROJECT / rel
    if not full.exists():
        return False
    with open(full, 'r', encoding='utf-8') as f:
        text = f.read()
    if marker in text:
        return False
    with open(full, 'a', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print(f"  ✎ {rel} (افزوده شد)")
    return True

# ═══════════════════════════════════════════════════════════════
# ۱) Migrations
# ═══════════════════════════════════════════════════════════════

MIG_CUSTOMER_PHONES = r'''<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        if (Schema::hasTable('customer_phones')) return;

        Schema::create('customer_phones', function (Blueprint $table) {
            $table->id();
            $table->foreignId('customer_id')->constrained()->cascadeOnDelete();
            $table->string('phone', 20)->index();
            $table->string('label', 50)->nullable(); // موبایل اصلی، منزل، محل کار
            $table->boolean('is_primary')->default(false);
            $table->timestamp('verified_at')->nullable();
            $table->string('note', 255)->nullable();
            $table->timestamps();

            $table->unique(['customer_id', 'phone']);
            $table->index(['phone', 'is_primary']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('customer_phones');
    }
};
'''

MIG_CUSTOMER_ADDRESSES = r'''<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        if (Schema::hasTable('customer_addresses')) return;

        Schema::create('customer_addresses', function (Blueprint $table) {
            $table->id();
            $table->foreignId('customer_id')->constrained()->cascadeOnDelete();
            $table->string('label', 50)->nullable();     // منزل، محل کار
            $table->string('province', 50)->nullable();
            $table->string('city', 80)->nullable();
            $table->text('address')->nullable();
            $table->string('postal_code', 20)->nullable()->index();
            $table->boolean('is_primary')->default(false);
            $table->decimal('lat', 10, 7)->nullable();
            $table->decimal('lng', 10, 7)->nullable();
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('customer_addresses');
    }
};
'''

MIG_PRODUCTS = r'''<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        if (Schema::hasTable('products')) return;

        Schema::create('products', function (Blueprint $table) {
            $table->id();

            // شناسه‌ها
            $table->string('sku', 100)->unique()->index();
            $table->unsignedBigInteger('wc_id')->nullable()->unique()->index();
            $table->string('barcode', 100)->nullable()->index();

            // اطلاعات اصلی
            $table->string('name', 255);
            $table->string('slug', 255)->nullable();
            $table->text('description')->nullable();
            $table->text('short_description')->nullable();

            // قیمت
            $table->decimal('price', 15, 2)->default(0);
            $table->decimal('regular_price', 15, 2)->nullable();
            $table->decimal('sale_price', 15, 2)->nullable();

            // موجودی
            $table->integer('stock_quantity')->nullable();
            $table->string('stock_status', 30)->default('instock');

            // ابعاد
            $table->decimal('weight', 10, 3)->nullable();
            $table->decimal('length', 10, 2)->nullable();
            $table->decimal('width', 10, 2)->nullable();
            $table->decimal('height', 10, 2)->nullable();

            // ارتباط با سنگ/فلز
            $table->foreignId('stone_id')->nullable()->constrained('stones')->nullOnDelete();
            $table->foreignId('metal_id')->nullable()->constrained('metals')->nullOnDelete();

            // تصاویر
            $table->string('image_path', 500)->nullable();
            $table->string('image_url', 500)->nullable();

            // JSON fields
            $table->json('gallery')->nullable();
            $table->json('categories')->nullable();
            $table->json('attributes')->nullable();
            $table->json('tags')->nullable();
            $table->json('wc_data')->nullable();       // خام از WooCommerce

            // وضعیت
            $table->boolean('is_active')->default(true);
            $table->timestamp('synced_at')->nullable();

            $table->timestamps();

            $table->index(['is_active', 'stock_status']);
            $table->index('name');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('products');
    }
};
'''

MIG_LEGACY_DATA = r'''<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Support\Facades\DB;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    /**
     * مهاجرت داده‌های قدیمی Customer به جداول جدید
     */
    public function up(): void
    {
        if (!Schema::hasTable('customers')) return;
        if (!Schema::hasTable('customer_phones')) return;

        $now = now();

        // مشتریانی که حداقل یک phone دارند ولی هنوز در customer_phones نیستند
        $customers = DB::table('customers')
            ->whereNotNull('phone')
            ->where('phone', '!=', '')
            ->get();

        $insertPhones = [];
        $insertAddresses = [];

        foreach ($customers as $c) {
            // بررسی اینکه آیا از قبل رکورد تلفن دارد
            $exists = DB::table('customer_phones')
                ->where('customer_id', $c->id)
                ->exists();
            if ($exists) continue;

            $normalized = $this->normalizePhone($c->phone);
            if (!$normalized) continue;

            $insertPhones[] = [
                'customer_id' => $c->id,
                'phone'       => $normalized,
                'label'       => 'اصلی',
                'is_primary'  => true,
                'created_at'  => $now,
                'updated_at'  => $now,
            ];

            // آدرس قدیمی
            $addr = $c->address ?? null;
            $postal = $c->postal_code ?? $c->postal ?? null;

            if ($addr || $postal) {
                $addrExists = DB::table('customer_addresses')
                    ->where('customer_id', $c->id)
                    ->exists();
                if (!$addrExists) {
                    $insertAddresses[] = [
                        'customer_id'  => $c->id,
                        'label'        => 'اصلی',
                        'province'     => null,
                        'city'         => null,
                        'address'      => $addr,
                        'postal_code'  => $postal,
                        'is_primary'   => true,
                        'created_at'   => $now,
                        'updated_at'   => $now,
                    ];
                }
            }
        }

        foreach (array_chunk($insertPhones, 500) as $chunk) {
            DB::table('customer_phones')->insert($chunk);
        }
        foreach (array_chunk($insertAddresses, 500) as $chunk) {
            DB::table('customer_addresses')->insert($chunk);
        }
    }

    protected function normalizePhone(?string $phone): string
    {
        $s = preg_replace('/\D/', '', (string) $phone);
        if (str_starts_with($s, '0098')) $s = substr($s, 4);
        elseif (str_starts_with($s, '98') && strlen($s) > 10) $s = substr($s, 2);
        if (str_starts_with($s, '0') && strlen($s) > 10) $s = substr($s, 1);
        return $s;
    }

    public function down(): void
    {
        DB::table('customer_phones')->truncate();
        DB::table('customer_addresses')->truncate();
    }
};
'''

# ═══════════════════════════════════════════════════════════════
# ۲) Models
# ═══════════════════════════════════════════════════════════════

MODEL_CUSTOMER_PHONE = r'''<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class CustomerPhone extends Model
{
    protected $fillable = [
        'customer_id', 'phone', 'label', 'is_primary', 'verified_at', 'note',
    ];

    protected $casts = [
        'is_primary'  => 'boolean',
        'verified_at' => 'datetime',
    ];

    public function customer(): BelongsTo
    {
        return $this->belongsTo(Customer::class);
    }

    public function scopePrimary($q)
    {
        return $q->where('is_primary', true);
    }

    /**
     * نمایش با فرمت خوانا: 0915 153 1301
     */
    public function getFormattedAttribute(): string
    {
        $p = $this->phone;
        if (strlen($p) === 10) {
            return substr($p, 0, 3) . ' ' . substr($p, 3, 3) . ' ' . substr($p, 6, 4);
        }
        if (strlen($p) === 11 && $p[0] === '0') {
            return substr($p, 0, 4) . ' ' . substr($p, 4, 3) . ' ' . substr($p, 7, 4);
        }
        return $p;
    }

    public function getDisplayAttribute(): string
    {
        return ($this->label ? "({$this->label}) " : '') . $this->formatted;
    }
}
'''

MODEL_CUSTOMER_ADDRESS = r'''<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class CustomerAddress extends Model
{
    protected $fillable = [
        'customer_id', 'label', 'province', 'city', 'address',
        'postal_code', 'is_primary', 'lat', 'lng',
    ];

    protected $casts = [
        'is_primary' => 'boolean',
        'lat'        => 'float',
        'lng'        => 'float',
    ];

    public function customer(): BelongsTo
    {
        return $this->belongsTo(Customer::class);
    }

    public function scopePrimary($q)
    {
        return $q->where('is_primary', true);
    }

    /**
     * آدرس کامل یک خطی
     */
    public function getFullAddressAttribute(): string
    {
        $parts = array_filter([
            $this->province,
            $this->city,
            $this->address,
        ]);
        return implode(' - ', $parts);
    }

    public function getShortAttribute(): string
    {
        $loc = array_filter([$this->city, $this->province]);
        $loc = implode('، ', $loc);
        $addr = mb_substr((string) $this->address, 0, 40);
        return trim($loc . ($addr ? ' - ' . $addr : ''));
    }
}
'''

MODEL_PRODUCT = r'''<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class Product extends Model
{
    protected $fillable = [
        'sku', 'wc_id', 'barcode', 'name', 'slug',
        'description', 'short_description',
        'price', 'regular_price', 'sale_price',
        'stock_quantity', 'stock_status',
        'weight', 'length', 'width', 'height',
        'stone_id', 'metal_id',
        'image_path', 'image_url',
        'gallery', 'categories', 'attributes', 'tags', 'wc_data',
        'is_active', 'synced_at',
    ];

    protected $casts = [
        'price'          => 'decimal:2',
        'regular_price'  => 'decimal:2',
        'sale_price'     => 'decimal:2',
        'weight'         => 'decimal:3',
        'length'         => 'decimal:2',
        'width'          => 'decimal:2',
        'height'         => 'decimal:2',
        'stock_quantity' => 'integer',
        'gallery'        => 'array',
        'categories'     => 'array',
        'attributes'     => 'array',
        'tags'           => 'array',
        'wc_data'        => 'array',
        'is_active'      => 'boolean',
        'synced_at'      => 'datetime',
    ];

    public function stone(): BelongsTo   { return $this->belongsTo(Stone::class); }
    public function metal(): BelongsTo   { return $this->belongsTo(Metal::class); }

    public function scopeActive($q)      { return $q->where('is_active', true); }
    public function scopeInStock($q)     { return $q->where('stock_status', 'instock'); }

    /**
     * جستجوی هوشمند: SKU → name → barcode → wc_id
     */
    public function scopeSearch($q, string $term)
    {
        $term = trim($term);
        if ($term === '') return $q;

        $q->where(function ($qq) use ($term) {
            $qq->where('sku', 'like', "%{$term}%")
               ->orWhere('name', 'like', "%{$term}%")
               ->orWhere('barcode', 'like', "%{$term}%")
               ->orWhere('wc_id', 'like', "%{$term}%");
        });

        return $q;
    }

    /**
     * تصویر نهایی
     */
    public function getImageSrcAttribute(): ?string
    {
        if (!empty($this->image_path)) {
            return asset('storage/' . $this->image_path);
        }
        return $this->image_url ?: null;
    }

    public function getPriceFormattedAttribute(): string
    {
        return number_format((float) $this->price);
    }

    /**
     * ساخت از WooCommerce product
     */
    public static function upsertFromWoo(array $wc): self
    {
        $sku = $wc['sku'] ?? null;
        if (!$sku) {
            $sku = 'PROD-' . ($wc['id'] ?? uniqid());
        }

        $data = [
            'sku'               => $sku,
            'wc_id'             => $wc['id'] ?? null,
            'name'              => $wc['name'] ?? '',
            'slug'              => $wc['slug'] ?? null,
            'description'       => $wc['description'] ?? null,
            'short_description' => $wc['short_description'] ?? null,
            'price'             => (float) ($wc['price'] ?? 0),
            'regular_price'     => (float) ($wc['regular_price'] ?? 0),
            'sale_price'        => isset($wc['sale_price']) && $wc['sale_price'] !== '' ? (float) $wc['sale_price'] : null,
            'stock_quantity'    => isset($wc['stock_quantity']) ? (int) $wc['stock_quantity'] : null,
            'stock_status'      => $wc['stock_status'] ?? 'instock',
            'weight'            => !empty($wc['weight']) ? (float) $wc['weight'] : null,
            'length'            => isset($wc['dimensions']['length']) && $wc['dimensions']['length'] !== '' ? (float) $wc['dimensions']['length'] : null,
            'width'             => isset($wc['dimensions']['width']) && $wc['dimensions']['width'] !== '' ? (float) $wc['dimensions']['width'] : null,
            'height'            => isset($wc['dimensions']['height']) && $wc['dimensions']['height'] !== '' ? (float) $wc['dimensions']['height'] : null,
            'image_url'         => $wc['images'][0]['src'] ?? null,
            'gallery'           => array_map(fn($i) => $i['src'] ?? null, $wc['images'] ?? []),
            'categories'        => array_map(fn($c) => ['id' => $c['id'] ?? null, 'name' => $c['name'] ?? ''], $wc['categories'] ?? []),
            'attributes'        => array_map(fn($a) => ['name' => $a['name'] ?? '', 'options' => $a['options'] ?? []], $wc['attributes'] ?? []),
            'tags'              => array_map(fn($t) => ['id' => $t['id'] ?? null, 'name' => $t['name'] ?? ''], $wc['tags'] ?? []),
            'wc_data'           => $wc,
            'is_active'         => ($wc['status'] ?? 'publish') === 'publish',
            'synced_at'         => now(),
        ];

        return static::updateOrCreate(['sku' => $sku], $data);
    }
}
'''

# ═══════════════════════════════════════════════════════════════
# ۳) Customer Model — اضافه کردن متدها
# ═══════════════════════════════════════════════════════════════

CUSTOMER_METHODS = r'''

    /* ═══════════════════════════════════════════════════════════
       فاز ۱ — چند تلفن و چند آدرس
       ═══════════════════════════════════════════════════════════ */

    public function phones(): \Illuminate\Database\Eloquent\Relations\HasMany
    {
        return $this->hasMany(\App\Models\CustomerPhone::class)
            ->orderByDesc('is_primary')
            ->orderBy('id');
    }

    public function addresses(): \Illuminate\Database\Eloquent\Relations\HasMany
    {
        return $this->hasMany(\App\Models\CustomerAddress::class)
            ->orderByDesc('is_primary')
            ->orderBy('id');
    }

    public function primaryPhone(): ?\App\Models\CustomerPhone
    {
        return $this->phones()->where('is_primary', true)->first()
            ?? $this->phones()->first();
    }

    public function primaryAddress(): ?\App\Models\CustomerAddress
    {
        return $this->addresses()->where('is_primary', true)->first()
            ?? $this->addresses()->first();
    }

    /**
     * نرمال‌سازی شماره تلفن: 09151531301 → 9151531301
     */
    public static function normalizePhone(?string $phone): string
    {
        $s = preg_replace('/\D/', '', (string) $phone);
        if (str_starts_with($s, '0098')) $s = substr($s, 4);
        elseif (str_starts_with($s, '98') && strlen($s) > 10) $s = substr($s, 2);
        if (str_starts_with($s, '0') && strlen($s) > 10) $s = substr($s, 1);
        return $s;
    }

    /**
     * پیدا کردن مشتری با تلفن (چند فرمت)
     */
    public static function findByPhone(string $phone): ?self
    {
        $normalized = self::normalizePhone($phone);
        if ($normalized === '') return null;

        // ۱) از جدول جدید customer_phones
        if (\Illuminate\Support\Facades\Schema::hasTable('customer_phones')) {
            $cp = \App\Models\CustomerPhone::where('phone', $normalized)->first();
            if ($cp) return $cp->customer;
        }

        // ۲) Fallback: فیلد قدیمی
        return self::where('phone', $normalized)
            ->orWhere('phone', '0' . $normalized)
            ->orWhere('phone', '+98' . $normalized)
            ->orWhere('phone', '98' . $normalized)
            ->first();
    }

    /**
     * افزودن شماره تلفن (با نرمال‌سازی خودکار)
     */
    public function addPhone(string $phone, ?string $label = null, bool $primary = false): ?\App\Models\CustomerPhone
    {
        $normalized = self::normalizePhone($phone);
        if ($normalized === '') return null;

        // اگر از قبل وجود دارد، فقط آپدیت کن
        $existing = $this->phones()->where('phone', $normalized)->first();
        if ($existing) {
            if ($label)  $existing->update(['label' => $label]);
            if ($primary) {
                $this->phones()->update(['is_primary' => false]);
                $existing->update(['is_primary' => true]);
            }
            return $existing;
        }

        if ($primary) {
            $this->phones()->update(['is_primary' => false]);
        }

        $isFirst = $this->phones()->count() === 0;

        $cp = $this->phones()->create([
            'phone'      => $normalized,
            'label'      => $label,
            'is_primary' => $primary || $isFirst,
        ]);

        // همگام‌سازی فیلد قدیمی
        if ($isFirst && empty($this->phone)) {
            $this->update(['phone' => $normalized]);
        } elseif ($primary) {
            $this->update(['phone' => $normalized]);
        }

        return $cp;
    }

    /**
     * افزودن آدرس
     */
    public function addAddress(array $data, bool $primary = false): \App\Models\CustomerAddress
    {
        if ($primary) {
            $this->addresses()->update(['is_primary' => false]);
        }

        $isFirst = $this->addresses()->count() === 0;

        $ca = $this->addresses()->create([
            'label'       => $data['label']       ?? null,
            'province'    => $data['province']    ?? null,
            'city'        => $data['city']        ?? null,
            'address'     => $data['address']     ?? '',
            'postal_code' => $data['postal_code'] ?? null,
            'lat'         => $data['lat']         ?? null,
            'lng'         => $data['lng']         ?? null,
            'is_primary'  => $primary || $isFirst,
        ]);

        // همگام‌سازی فیلد قدیمی
        if ($isFirst) {
            $this->update([
                'address'     => $data['address']     ?? $this->address,
                'postal_code' => $data['postal_code'] ?? $this->postal_code ?? null,
            ]);
        }

        return $ca;
    }

    /**
     * لیست شماره تلفن‌ها به صورت رشته
     */
    public function getPhonesListAttribute(): string
    {
        return $this->phones->pluck('phone')->implode(' / ');
    }

    /**
     * لیست آدرس‌ها
     */
    public function getAddressesListAttribute(): string
    {
        return $this->addresses->map(fn($a) => $a->short)->implode(' | ');
    }
'''

# ═══════════════════════════════════════════════════════════════
# ۴) Service — ProductSyncService
# ═══════════════════════════════════════════════════════════════

PRODUCT_SYNC_SERVICE = r'''<?php

namespace App\Services;

use App\Models\Product;
use Illuminate\Support\Facades\Log;

class ProductSyncService
{
    /**
     * سینک محصولات از WooCommerce به دیتابیس
     *
     * @param  bool  $full  اگر false، فقط تغییرات ۳۰ روز اخیر
     * @return array  گزارش
     */
    public static function syncFromWoo(bool $full = true): array
    {
        $report = [
            'total'   => 0,
            'created' => 0,
            'updated' => 0,
            'failed'  => 0,
            'errors'  => [],
        ];

        try {
            $wc = app(WooCommerceService::class);
        } catch (\Throwable $e) {
            $report['errors'][] = 'WooCommerceService بارگذاری نشد: ' . $e->getMessage();
            return $report;
        }

        $page = 1;
        $perPage = 100;
        $maxPages = 200;

        while ($page <= $maxPages) {
            $raw = null;
            try {
                $raw = $wc->getProducts(['per_page' => $perPage, 'page' => $page]);
            } catch (\Throwable $e) {
                $report['errors'][] = "page {$page}: " . $e->getMessage();
                break;
            }

            if (!is_array($raw) || empty($raw)) break;

            foreach ($raw as $item) {
                $report['total']++;
                try {
                    $sku = $item['sku'] ?? null;
                    $exists = $sku ? Product::where('sku', $sku)->exists() : false;

                    Product::upsertFromWoo($item);

                    if ($exists) $report['updated']++;
                    else         $report['created']++;
                } catch (\Throwable $e) {
                    $report['failed']++;
                    $report['errors'][] = 'item ' . ($item['id'] ?? '?') . ': ' . $e->getMessage();
                }
            }

            if (count($raw) < $perPage) break;
            $page++;
        }

        return $report;
    }

    /**
     * سینک محصولات از آرایه‌ی آماده (مثلاً از localStorage قدیمی)
     */
    public static function syncFromArray(array $products): array
    {
        $report = ['created' => 0, 'updated' => 0, 'failed' => 0];

        foreach ($products as $p) {
            try {
                $sku = $p['sku'] ?? null;
                if (!$sku) continue;

                $exists = Product::where('sku', $sku)->exists();

                Product::updateOrCreate(['sku' => $sku], [
                    'sku'               => $sku,
                    'wc_id'             => $p['id'] ?? null,
                    'name'              => $p['title'] ?? $p['name'] ?? '',
                    'price'             => (float) ($p['price'] ?? 0),
                    'regular_price'     => (float) ($p['regularPrice'] ?? 0),
                    'stock_quantity'    => isset($p['stock']) ? (int) $p['stock'] : null,
                    'stock_status'      => $p['stockStatus'] ?? 'instock',
                    'image_url'         => $p['image'] ?? null,
                    'categories'        => is_string($p['categories'] ?? null)
                        ? array_map('trim', explode('،', $p['categories']))
                        : ($p['categories'] ?? []),
                    'attributes'        => $p['attributes'] ?? [],
                    'weight'            => !empty($p['weight']) ? (float) $p['weight'] : null,
                    'synced_at'         => now(),
                    'is_active'         => true,
                ]);

                if ($exists) $report['updated']++;
                else         $report['created']++;
            } catch (\Throwable $e) {
                $report['failed']++;
            }
        }

        return $report;
    }
}
'''

# ═══════════════════════════════════════════════════════════════
# ۵) Livewire — CustomerPicker
# ═══════════════════════════════════════════════════════════════

CUSTOMER_PICKER_PHP = r'''<?php

namespace App\Livewire\Components;

use App\Models\Customer;
use Livewire\Attributes\On;
use Livewire\Component;

class CustomerPicker extends Component
{
    /** شناسه مشتری انتخاب‌شده */
    public ?int $customerId = null;

    /** متن جستجو */
    public string $query = '';

    /** نتیجه‌ها */
    public array $results = [];

    /** حالت: search | selected | new */
    public string $mode = 'search';

    /** اطلاعات مشتری انتخاب‌شده برای نمایش */
    public array $selectedData = [];

    /** فرم مشتری جدید */
    public string $newName = '';
    public string $newPhone = '';
    public string $newAddress = '';
    public string $newPostal = '';

    /** پیشوند کانتینر برای رویداد */
    public string $eventPrefix = 'customer';

    /** نمایش inline */
    public bool $compact = false;

    public function mount(?int $customerId = null, string $eventPrefix = 'customer', bool $compact = false): void
    {
        $this->eventPrefix = $eventPrefix;
        $this->compact = $compact;

        if ($customerId) {
            $this->loadCustomer($customerId);
        }
    }

    public function updatedQuery(): void
    {
        $q = trim($this->query);
        if (mb_strlen($q) < 2) {
            $this->results = [];
            return;
        }

        $normalized = Customer::normalizePhone($q);

        // جستجو در تلفن‌های جدید + فیلد قدیمی + نام
        $this->results = Customer::query()
            ->withCount('orders')
            ->with(['phones', 'addresses'])
            ->where(function ($qq) use ($q, $normalized) {
                if ($normalized !== '') {
                    $qq->whereHas('phones', fn($p) => $p->where('phone', 'like', "%{$normalized}%"))
                       ->orWhere('phone', 'like', "%{$normalized}%");
                }
                $qq->orWhere('name', 'like', "%{$q}%");
            })
            ->orderByDesc('id')
            ->limit(15)
            ->get()
            ->map(fn($c) => [
                'id'         => $c->id,
                'name'       => $c->name ?: '—',
                'phone'      => $c->primaryPhone()?->formatted
                                ?? $c->phone
                                ?? '—',
                'phone_raw'  => $c->primaryPhone()?->phone ?? $c->phone,
                'address'    => $c->primaryAddress()?->short ?? $c->address ?? '',
                'postal'     => $c->primaryAddress()?->postal_code ?? $c->postal_code ?? '',
                'orders'     => $c->orders_count ?? 0,
                'last_at'    => $c->updated_at?->toIso8601String(),
            ])
            ->toArray();
    }

    public function selectCustomer(int $id): void
    {
        $this->loadCustomer($id);
        $this->dispatch("{$this->eventPrefix}-selected", customerId: $id, data: $this->selectedData);
    }

    public function loadCustomer(int $id): void
    {
        $c = Customer::with(['phones', 'addresses'])->find($id);
        if (!$c) return;

        $primaryPhone = $c->primaryPhone();
        $primaryAddr  = $c->primaryAddress();

        $this->customerId = $c->id;
        $this->selectedData = [
            'id'          => $c->id,
            'name'        => $c->name,
            'phone'       => $primaryPhone?->phone ?? $c->phone,
            'phone_fmt'   => $primaryPhone?->formatted ?? $c->phone,
            'phone_label' => $primaryPhone?->label,
            'address'     => $primaryAddr?->address ?? $c->address,
            'city'        => $primaryAddr?->city,
            'province'    => $primaryAddr?->province,
            'postal_code' => $primaryAddr?->postal_code ?? $c->postal_code,
            'extra_phones'    => $c->phones->pluck('phone')->toArray(),
            'extra_addresses' => $c->addresses->pluck('short')->toArray(),
        ];
        $this->mode = 'selected';
        $this->query = '';
        $this->results = [];
    }

    public function clearSelection(): void
    {
        $this->customerId = null;
        $this->selectedData = [];
        $this->mode = 'search';
        $this->query = '';
        $this->results = [];
        $this->dispatch("{$this->eventPrefix}-cleared");
    }

    public function startNew(): void
    {
        $this->mode = 'new';
        $this->newName = '';
        $this->newPhone = $this->query; // پیش‌پر کردن
        $this->newAddress = '';
        $this->newPostal = '';
    }

    public function cancelNew(): void
    {
        $this->mode = 'search';
    }

    public function createCustomer(): void
    {
        $this->validate([
            'newName'    => 'required|string|max:120',
            'newPhone'   => 'required|string|max:20',
            'newAddress' => 'nullable|string|max:500',
            'newPostal'  => 'nullable|string|max:20',
        ], [], [
            'newName'    => 'نام',
            'newPhone'   => 'تلفن',
            'newAddress' => 'آدرس',
            'newPostal'  => 'کدپستی',
        ]);

        $normalized = Customer::normalizePhone($this->newPhone);
        if ($normalized === '') {
            $this->addError('newPhone', 'شماره تلفن نامعتبر');
            return;
        }

        // بررسی تکراری
        $existing = Customer::findByPhone($normalized);
        if ($existing) {
            $this->selectCustomer($existing->id);
            return;
        }

        $customer = Customer::create([
            'name'        => $this->newName,
            'phone'       => $normalized,
            'address'     => $this->newAddress,
            'postal_code' => $this->newPostal,
        ]);

        $customer->addPhone($normalized, 'اصلی', true);
        if ($this->newAddress || $this->newPostal) {
            $customer->addAddress([
                'address'     => $this->newAddress,
                'postal_code' => $this->newPostal,
            ], true);
        }

        $this->loadCustomer($customer->id);
        $this->dispatch("{$this->eventPrefix}-selected", customerId: $customer->id, data: $this->selectedData);
    }

    #[On('customer-picker-set')]
    public function setCustomer(?int $id = null): void
    {
        if ($id) $this->loadCustomer($id);
    }

    public function render()
    {
        return view('livewire.components.customer-picker');
    }
}
'''

CUSTOMER_PICKER_BLADE = r'''<div class="customer-picker" wire:key="cp-{{ $this->getId() }}">
    {{-- ═══ حالت جستجو ═══ --}}
    @if($mode === 'search')
        <div class="relative">
            <div class="flex items-center gap-2 bg-base-100 border-2 border-base-300 focus-within:border-primary rounded-xl px-3 py-2 transition">
                <span class="text-base-content/40">🔍</span>
                <input type="text"
                       wire:model.live.debounce.250ms="query"
                       placeholder="تلفن یا نام مشتری..."
                       class="flex-1 bg-transparent border-0 outline-none text-sm"
                       autocomplete="off"
                       dir="auto">
                @if($query)
                    <button type="button" wire:click="$set('query','')" class="btn btn-ghost btn-xs btn-circle">✕</button>
                @endif
            </div>

            {{-- نتایج --}}
            @if(count($results) > 0)
                <div class="absolute z-50 top-full left-0 right-0 mt-2 bg-base-100 border border-base-300 rounded-xl shadow-2xl max-h-80 overflow-y-auto">
                    @foreach($results as $r)
                        <button type="button"
                                wire:click="selectCustomer({{ $r['id'] }})"
                                wire:key="cpr-{{ $r['id'] }}"
                                class="w-full text-right px-4 py-3 hover:bg-base-200 border-b border-base-200 last:border-0 transition">
                            <div class="flex items-center justify-between gap-3">
                                <div class="flex-1 min-w-0">
                                    <div class="font-bold text-sm truncate">{{ $r['name'] }}</div>
                                    <div class="text-xs font-mono text-base-content/60 mt-0.5" dir="ltr">
                                        {{ $r['phone'] }}
                                    </div>
                                    @if($r['address'])
                                        <div class="text-[10px] text-base-content/50 mt-0.5 truncate">
                                            📍 {{ $r['address'] }}
                                        </div>
                                    @endif
                                </div>
                                @if($r['orders'] > 0)
                                    <div class="badge badge-primary badge-sm shrink-0">
                                        {{ \App\Support\PersianNumber::toFa($r['orders']) }} سفارش
                                    </div>
                                @else
                                    <div class="badge badge-ghost badge-sm shrink-0">جدید</div>
                                @endif
                            </div>
                        </button>
                    @endforeach
                </div>
            @elseif(mb_strlen(trim($query)) >= 2)
                <div class="absolute z-50 top-full left-0 right-0 mt-2 bg-base-100 border border-base-300 rounded-xl shadow-2xl p-4">
                    <div class="text-center text-sm text-base-content/60 mb-3">
                        مشتری‌ای پیدا نشد
                    </div>
                    <button type="button" wire:click="startNew"
                            class="btn btn-primary btn-sm w-full">
                        ➕ ایجاد مشتری جدید با تلفن «{{ $query }}»
                    </button>
                </div>
            @endif
        </div>

        {{-- راهنمای سریع --}}
        <div class="text-[10px] text-base-content/40 mt-1 px-1">
            💡 با تایپ ۲ رقم به بالا جستجو شروع می‌شود
        </div>

    {{-- ═══ حالت مشتری جدید ═══ --}}
    @elseif($mode === 'new')
        <div class="border-2 border-primary/30 rounded-xl p-4 bg-primary/5 space-y-3">
            <div class="flex items-center justify-between mb-1">
                <div class="font-bold text-sm text-primary">➕ مشتری جدید</div>
                <button type="button" wire:click="cancelNew" class="btn btn-ghost btn-xs">انصراف</button>
            </div>

            <div class="grid grid-cols-2 gap-2">
                <div>
                    <label class="text-[10px] font-bold text-base-content/60">نام *</label>
                    <input type="text" wire:model="newName"
                           class="input input-bordered input-sm w-full" autofocus>
                    @error('newName') <span class="text-error text-[10px]">{{ $message }}</span> @enderror
                </div>
                <div>
                    <label class="text-[10px] font-bold text-base-content/60">📱 تلفن *</label>
                    <input type="text" wire:model="newPhone" dir="ltr"
                           class="input input-bordered input-sm w-full font-mono">
                    @error('newPhone') <span class="text-error text-[10px]">{{ $message }}</span> @enderror
                </div>
            </div>

            <div>
                <label class="text-[10px] font-bold text-base-content/60">📍 آدرس</label>
                <textarea wire:model="newAddress" rows="2"
                          class="textarea textarea-bordered textarea-sm w-full"></textarea>
            </div>

            <div>
                <label class="text-[10px] font-bold text-base-content/60">📮 کدپستی</label>
                <input type="text" wire:model="newPostal" dir="ltr"
                       class="input input-bordered input-sm w-full font-mono">
            </div>

            <button type="button" wire:click="createCustomer"
                    wire:loading.attr="disabled"
                    class="btn btn-success btn-sm w-full">
                <span wire:loading.remove wire:target="createCustomer">✅ ذخیره و انتخاب</span>
                <span wire:loading wire:target="createCustomer">⏳...</span>
            </button>
        </div>

    {{-- ═══ حالت انتخاب‌شده ═══ --}}
    @elseif($mode === 'selected')
        <div class="border-2 border-success/40 rounded-xl p-3 bg-success/5">
            <div class="flex items-start justify-between gap-3">
                <div class="flex-1 min-w-0">
                    <div class="flex items-center gap-2">
                        <span class="badge badge-success badge-sm">✓</span>
                        <span class="font-bold text-sm truncate">{{ $selectedData['name'] ?? '—' }}</span>
                    </div>
                    <div class="text-xs font-mono text-base-content/70 mt-1" dir="ltr">
                        {{ $selectedData['phone_fmt'] ?? $selectedData['phone'] ?? '—' }}
                    </div>
                    @if(!empty($selectedData['address']))
                        <div class="text-[11px] text-base-content/60 mt-1">
                            📍 {{ $selectedData['address'] }}
                            @if(!empty($selectedData['postal_code']))
                                <span class="font-mono">({{ $selectedData['postal_code'] }})</span>
                            @endif
                        </div>
                    @endif
                    @if(count($selectedData['extra_phones'] ?? []) > 1)
                        <div class="text-[10px] text-base-content/40 mt-1">
                            📞 {{ count($selectedData['extra_phones']) }} شماره ثبت شده
                        </div>
                    @endif
                </div>
                <button type="button" wire:click="clearSelection"
                        class="btn btn-ghost btn-xs" title="تغییر مشتری">
                    🔄
                </button>
            </div>
        </div>
    @endif
</div>
'''

# ═══════════════════════════════════════════════════════════════
# ۶) Livewire — ProductPicker
# ═══════════════════════════════════════════════════════════════

PRODUCT_PICKER_PHP = r'''<?php

namespace App\Livewire\Components;

use App\Models\Product;
use Livewire\Attributes\On;
use Livewire\Component;

class ProductPicker extends Component
{
    /** متن جستجو */
    public string $query = '';

    /** نتایج */
    public array $results = [];

    /** سبد */
    public array $cart = [];

    /** پیشوند رویدادها */
    public string $eventPrefix = 'products';

    /** نمایش compact */
    public bool $compact = false;

    /** جستجو در WooCommerce آنلاین */
    public bool $searchOnline = true;

    public function mount(array $cart = [], string $eventPrefix = 'products', bool $compact = false): void
    {
        $this->cart = $cart;
        $this->eventPrefix = $eventPrefix;
        $this->compact = $compact;
    }

    public function updatedQuery(): void
    {
        $q = trim($this->query);
        if (mb_strlen($q) < 2) {
            $this->results = [];
            return;
        }

        // ۱) اول جستجو در دیتابیس محلی
        $local = Product::query()
            ->active()
            ->search($q)
            ->orderByRaw("CASE WHEN sku = ? THEN 0 WHEN sku LIKE ? THEN 1 ELSE 2 END", [$q, $q . '%'])
            ->limit(20)
            ->get()
            ->map(fn($p) => $this->formatResult($p))
            ->toArray();

        $this->results = $local;

        // ۲) اگر کم بود و WooCommerce فعال است، آنلاین جستجو کن
        if (count($local) < 5 && $this->searchOnline) {
            $this->searchOnlineProducts($q);
        }
    }

    protected function searchOnlineProducts(string $q): void
    {
        try {
            $wc = app(\App\Services\WooCommerceService::class);
            $remote = $wc->getProducts(['search' => $q, 'per_page' => 10]);
            if (!is_array($remote)) return;

            $existingSkus = array_column($this->results, 'sku');
            foreach ($remote as $wcItem) {
                $sku = $wcItem['sku'] ?? null;
                if (!$sku || in_array($sku, $existingSkus, true)) continue;

                $product = Product::upsertFromWoo($wcItem);
                $this->results[] = $this->formatResult($product);
            }
        } catch (\Throwable $e) {
            // ignore
        }
    }

    protected function formatResult(Product $p): array
    {
        return [
            'id'            => $p->id,
            'sku'           => $p->sku,
            'name'          => $p->name,
            'price'         => (float) $p->price,
            'price_fmt'     => $p->price_formatted,
            'image'         => $p->image_src,
            'stock'         => $p->stock_quantity,
            'stock_status'  => $p->stock_status,
            'category'      => is_array($p->categories) ? ($p->categories[0]['name'] ?? null) : null,
        ];
    }

    public function addProduct(int $id): void
    {
        $p = Product::find($id);
        if (!$p) return;

        // اگر از قبل در سبد هست، فقط تعداد را ۱ اضافه کن
        foreach ($this->cart as $i => $item) {
            if (($item['product_id'] ?? null) === $p->id) {
                $this->cart[$i]['qty'] = ((int) ($item['qty'] ?? 1)) + 1;
                $this->recalcItem($i);
                $this->emitCart();
                return;
            }
        }

        $this->cart[] = [
            'product_id'   => $p->id,
            'sku'          => $p->sku,
            'title'        => $p->name,
            'price'        => (float) $p->price,
            'qty'          => 1,
            'image'        => $p->image_src,
            'certNeeded'   => false,
        ];

        $this->query = '';
        $this->results = [];
        $this->emitCart();
    }

    public function addBySku(string $sku): void
    {
        $sku = trim($sku);
        if ($sku === '') return;

        $p = Product::where('sku', $sku)->first();
        if (!$p) {
            // جستجو آنلاین
            try {
                $wc = app(\App\Services\WooCommerceService::class);
                $remote = $wc->getProducts(['sku' => $sku, 'per_page' => 1]);
                if (is_array($remote) && !empty($remote)) {
                    $p = Product::upsertFromWoo($remote[0]);
                }
            } catch (\Throwable $e) {}
        }

        if ($p) {
            $this->addProduct($p->id);
        }
    }

    public function updateQty(int $index, int $qty): void
    {
        if (!isset($this->cart[$index])) return;
        $qty = max(1, min(999, $qty));
        $this->cart[$index]['qty'] = $qty;
        $this->recalcItem($index);
        $this->emitCart();
    }

    public function updatePrice(int $index, $price): void
    {
        if (!isset($this->cart[$index])) return;
        $price = (float) preg_replace('/[^\d.]/', '', (string) $price);
        $this->cart[$index]['price'] = $price;
        $this->emitCart();
    }

    public function toggleCert(int $index): void
    {
        if (!isset($this->cart[$index])) return;
        $this->cart[$index]['certNeeded'] = !($this->cart[$index]['certNeeded'] ?? false);
        $this->emitCart();
    }

    public function removeItem(int $index): void
    {
        unset($this->cart[$index]);
        $this->cart = array_values($this->cart);
        $this->emitCart();
    }

    public function clearCart(): void
    {
        $this->cart = [];
        $this->emitCart();
    }

    protected function recalcItem(int $index): void
    {
        // فقط برای محاسبه‌ی نمایشی، خود مبلغ در parent محاسبه می‌شود
    }

    protected function emitCart(): void
    {
        $this->dispatch("{$this->eventPrefix}-updated", cart: $this->cart);
    }

    #[On('product-picker-set')]
    public function setCart(array $cart = []): void
    {
        $this->cart = $cart;
    }

    public function render()
    {
        $total = 0;
        foreach ($this->cart as $it) {
            $total += ((float) ($it['price'] ?? 0)) * ((int) ($it['qty'] ?? 1));
        }

        return view('livewire.components.product-picker', [
            'total' => $total,
        ]);
    }
}
'''

PRODUCT_PICKER_BLADE = r'''<div class="product-picker space-y-3">
    {{-- ═══ جستجو ═══ --}}
    <div class="relative">
        <div class="flex items-center gap-2 bg-base-100 border-2 border-base-300 focus-within:border-primary rounded-xl px-3 py-2 transition">
            <span class="text-base-content/40">🛍️</span>
            <input type="text"
                   wire:model.live.debounce.250ms="query"
                   wire:keydown.enter="addBySku($event.target.value); $event.target.value=''; $wire.set('query','')"
                   placeholder="SKU، نام یا بارکد محصول..."
                   class="flex-1 bg-transparent border-0 outline-none text-sm font-mono"
                   autocomplete="off"
                   dir="auto">
            @if($query)
                <button type="button" wire:click="$set('query','')" class="btn btn-ghost btn-xs btn-circle">✕</button>
            @endif
        </div>

        @if(count($results) > 0)
            <div class="absolute z-50 top-full left-0 right-0 mt-2 bg-base-100 border border-base-300 rounded-xl shadow-2xl max-h-96 overflow-y-auto">
                @foreach($results as $r)
                    <button type="button"
                            wire:click="addProduct({{ $r['id'] }})"
                            wire:key="ppr-{{ $r['id'] }}"
                            class="w-full text-right px-3 py-3 hover:bg-base-200 border-b border-base-200 last:border-0 transition flex items-center gap-3">
                        @if($r['image'])
                            <img src="{{ $r['image'] }}" alt="" class="w-12 h-12 object-cover rounded-lg border border-base-300 bg-white shrink-0">
                        @else
                            <div class="w-12 h-12 rounded-lg border border-base-300 bg-base-200 flex items-center justify-center text-lg shrink-0">💎</div>
                        @endif
                        <div class="flex-1 min-w-0">
                            <div class="font-bold text-xs truncate">{{ $r['name'] }}</div>
                            <div class="text-[10px] font-mono text-base-content/50 mt-0.5" dir="ltr">{{ $r['sku'] }}</div>
                            @if($r['category'])
                                <div class="text-[10px] text-base-content/40 mt-0.5">🏷️ {{ $r['category'] }}</div>
                            @endif
                        </div>
                        <div class="text-left shrink-0">
                            <div class="text-xs font-bold text-primary">{{ $r['price_fmt'] }}</div>
                            @if($r['stock'] !== null)
                                <div class="text-[10px] {{ $r['stock'] > 0 ? 'text-success' : 'text-error' }}">
                                    موجودی: {{ \App\Support\PersianNumber::toFa($r['stock']) }}
                                </div>
                            @endif
                        </div>
                    </button>
                @endforeach
            </div>
        @endif
    </div>

    {{-- ═══ سبد ═══ --}}
    @if(count($cart) > 0)
        <div class="border border-base-300 rounded-xl overflow-hidden">
            <div class="bg-base-200/60 px-3 py-2 flex items-center justify-between">
                <span class="text-xs font-bold">🛒 سبد ({{ \App\Support\PersianNumber::toFa(count($cart)) }})</span>
                <button type="button" wire:click="clearCart" class="text-[10px] text-error hover:underline">پاک کردن</button>
            </div>
            <div class="divide-y divide-base-200">
                @foreach($cart as $i => $item)
                    <div class="p-3 space-y-2" wire:key="cart-{{ $i }}-{{ $item['product_id'] ?? '' }}">
                        <div class="flex items-start gap-2">
                            <div class="flex-1 min-w-0">
                                <div class="text-xs font-bold truncate">{{ $item['title'] ?? '—' }}</div>
                                @if(!empty($item['sku']))
                                    <div class="text-[10px] font-mono text-base-content/50" dir="ltr">{{ $item['sku'] }}</div>
                                @endif
                            </div>
                            <button type="button" wire:click="removeItem({{ $i }})"
                                    class="btn btn-ghost btn-xs text-error shrink-0">🗑️</button>
                        </div>
                        <div class="grid grid-cols-3 gap-2 items-end">
                            <div>
                                <label class="text-[10px] text-base-content/60">تعداد</label>
                                <input type="number" min="1" max="999"
                                       value="{{ $item['qty'] ?? 1 }}"
                                       wire:change="updateQty({{ $i }}, $event.target.value)"
                                       class="input input-bordered input-xs w-full text-center" dir="ltr">
                            </div>
                            <div>
                                <label class="text-[10px] text-base-content/60">قیمت</label>
                                <input type="text"
                                       value="{{ number_format((float) ($item['price'] ?? 0)) }}"
                                       wire:change="updatePrice({{ $i }}, $event.target.value)"
                                       class="input input-bordered input-xs w-full text-left font-mono" dir="ltr">
                            </div>
                            <div class="text-left pb-1">
                                <label class="text-[10px] text-base-content/60">جمع</label>
                                <div class="text-xs font-bold text-primary">
                                    {{ number_format(((float) ($item['price'] ?? 0)) * ((int) ($item['qty'] ?? 1))) }}
                                </div>
                            </div>
                        </div>
                        <label class="flex items-center gap-2 cursor-pointer">
                            <input type="checkbox"
                                   {{ !empty($item['certNeeded']) ? 'checked' : '' }}
                                   wire:change="toggleCert({{ $i }})"
                                   class="checkbox checkbox-xs checkbox-primary">
                            <span class="text-[10px] text-base-content/70">نیاز به شناسنامه</span>
                        </label>
                    </div>
                @endforeach
            </div>
            <div class="bg-primary/10 px-3 py-2 flex items-center justify-between border-t border-base-300">
                <span class="text-xs font-bold">جمع کل:</span>
                <span class="text-sm font-bold text-primary">
                    {{ number_format($total) }} تومان
                </span>
            </div>
        </div>
    @else
        <div class="border-2 border-dashed border-base-300 rounded-xl p-6 text-center">
            <div class="text-3xl mb-2 opacity-30">🛒</div>
            <div class="text-xs text-base-content/60">محصولی اضافه نشده</div>
            <div class="text-[10px] text-base-content/40 mt-1">
                SKU را تایپ کن و Enter بزن یا از نتایج انتخاب کن
            </div>
        </div>
    @endif
</div>
'''

# ═══════════════════════════════════════════════════════════════
# ۷) Command — migrate legacy customer data
# ═══════════════════════════════════════════════════════════════

COMMAND_MIGRATE = r'''<?php

namespace App\Console\Commands;

use App\Models\Customer;
use Illuminate\Console\Command;

class MigrateLegacyCustomerData extends Command
{
    protected $signature = 'shopgun:migrate-legacy-customer-data
                            {--force : بدون تأییدیه اجرا شود}';

    protected $description = 'مهاجرت داده‌های قدیمی مشتریان به جدول‌های جدید (customer_phones, customer_addresses)';

    public function handle(): int
    {
        $total = Customer::count();
        if ($total === 0) {
            $this->info('هیچ مشتری‌ای وجود ندارد.');
            return 0;
        }

        if (!$this->option('force') && !$this->confirm("{$total} مشتری پردازش می‌شود. ادامه؟")) {
            return 0;
        }

        $bar = $this->output->createProgressBar($total);
        $bar->start();

        $phoneAdded = 0;
        $addrAdded  = 0;
        $skipped    = 0;

        Customer::with(['phones', 'addresses'])->chunk(200, function ($customers) use (&$phoneAdded, &$addrAdded, &$skipped, $bar) {
            foreach ($customers as $c) {
                // تلفن
                if ($c->phones->isEmpty() && !empty($c->phone)) {
                    $cp = $c->addPhone($c->phone, 'اصلی', true);
                    if ($cp) $phoneAdded++;
                } else {
                    $skipped++;
                }

                // آدرس
                if ($c->addresses->isEmpty()) {
                    $addr = $c->address ?? null;
                    $postal = $c->postal_code ?? $c->postal ?? null;
                    if ($addr || $postal) {
                        $c->addAddress([
                            'address'     => $addr,
                            'postal_code' => $postal,
                        ], true);
                        $addrAdded++;
                    }
                }

                $bar->advance();
            }
        });

        $bar->finish();
        $this->newLine(2);

        $this->table(
            ['مورد', 'تعداد'],
            [
                ['تلفن اضافه شده',    $phoneAdded],
                ['آدرس اضافه شده',    $addrAdded],
                ['بدون تغییر',         $skipped],
                ['کل مشتریان',        $total],
            ]
        );

        return 0;
    }
}
'''

# ═══════════════════════════════════════════════════════════════
# ۸) صفحه تست pickerها
# ═══════════════════════════════════════════════════════════════

TEST_PICKERS_PHP = r'''<?php

namespace App\Livewire\Dev;

use Livewire\Component;

class TestPickers extends Component
{
    public ?int $customerId = null;
    public array $customerData = [];
    public array $cart = [];

    protected $listeners = [
        'customer-selected' => 'onCustomerSelected',
        'customer-cleared'  => 'onCustomerCleared',
        'products-updated'  => 'onProductsUpdated',
    ];

    public function onCustomerSelected(int $customerId, array $data): void
    {
        $this->customerId = $customerId;
        $this->customerData = $data;
    }

    public function onCustomerCleared(): void
    {
        $this->customerId = null;
        $this->customerData = [];
    }

    public function onProductsUpdated(array $cart): void
    {
        $this->cart = $cart;
    }

    public function render()
    {
        $total = 0;
        foreach ($this->cart as $it) {
            $total += ((float) ($it['price'] ?? 0)) * ((int) ($it['qty'] ?? 1));
        }

        return view('livewire.dev.test-pickers', compact('total'))
            ->layout('components.layouts.app');
    }
}
'''

TEST_PICKERS_BLADE = r'''<div class="p-4 md:p-6 max-w-4xl mx-auto space-y-6">
    <div class="flex items-center gap-3 mb-2">
        <h1 class="text-xl md:text-2xl font-bold">🧪 تست Pickerها</h1>
        <span class="badge badge-warning">فاز ۱</span>
    </div>

    <div class="alert alert-info py-2 text-sm">
        <span>این صفحه برای تست کامپوننت‌های جدید است. بعد از تأیید، این پیکرها در فرم سفارش جایگزین می‌شوند.</span>
    </div>

    {{-- ═══ Customer Picker ═══ --}}
    <div class="card bg-base-100 shadow border">
        <div class="card-body">
            <h2 class="font-bold text-base mb-3">👤 انتخاب مشتری</h2>
            <livewire:components.customer-picker
                :customer-id="$customerId"
                event-prefix="customer" />

            @if($customerId)
                <div class="mt-4 p-3 bg-success/5 border border-success/30 rounded-lg">
                    <div class="text-xs font-bold mb-2 text-success">✓ مشتری انتخاب شده (ID: {{ $customerId }})</div>
                    <pre class="text-[10px] bg-base-200 p-2 rounded overflow-x-auto" dir="ltr">{{ json_encode($customerData, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT) }}</pre>
                </div>
            @endif
        </div>
    </div>

    {{-- ═══ Product Picker ═══ --}}
    <div class="card bg-base-100 shadow border">
        <div class="card-body">
            <h2 class="font-bold text-base mb-3">🛍️ انتخاب محصولات</h2>
            <livewire:components.product-picker event-prefix="products" />

            @if(count($cart) > 0)
                <div class="mt-4 p-3 bg-primary/5 border border-primary/30 rounded-lg">
                    <div class="text-xs font-bold mb-2 text-primary">🛒 سبد ({{ count($cart) }} آیتم)</div>
                    <pre class="text-[10px] bg-base-200 p-2 rounded overflow-x-auto" dir="ltr">{{ json_encode($cart, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT) }}</pre>
                    <div class="text-sm font-bold mt-2 text-primary">
                        جمع: {{ number_format($total) }} تومان
                    </div>
                </div>
            @endif
        </div>
    </div>
</div>
'''

# ═══════════════════════════════════════════════════════════════
# ۹) Route injection
# ═══════════════════════════════════════════════════════════════

ROUTE_PATCH = r'''

    // ═══ Dev: تست Pickerها (فاز ۱) ═══
    Route::middleware('auth')->get('/dev/pickers', \App\Livewire\Dev\TestPickers::class)->name('dev.pickers');
'''

# ═══════════════════════════════════════════════════════════════
# ۱۰) WooCommerceService — افزودن متد syncToDatabase
# ═══════════════════════════════════════════════════════════════

WOO_APPEND = r'''

    /* ═══════════════════════════════════════════════════════════
       فاز ۱ — سینک محصولات به دیتابیس محلی
       ═══════════════════════════════════════════════════════════ */

    /**
     * سینک محصولات WooCommerce به جدول products
     */
    public function syncProductsToDatabase(int $perPage = 100): array
    {
        return \App\Services\ProductSyncService::syncFromWoo(true);
    }
'''

# ═══════════════════════════════════════════════════════════════
# اجرا
# ═══════════════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  ShopGun V2 — فاز ۱: Customer/Product کامل                    ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    # Backup
    print("📦 Backup از فایل‌های موجود...")
    for rel in [
        "app/Models/Customer.php",
        "app/Services/WooCommerceService.php",
        "routes/web.php",
    ]:
        backup(rel)

    # Migrations با timestamp متوالی
    print("\n📄 Migrations...")
    ts = datetime.now().strftime("%Y_%m_%d_%H%M%S")
    write(f"database/migrations/{ts}_001_create_customer_phones_table.php", MIG_CUSTOMER_PHONES)
    write(f"database/migrations/{ts}_002_create_customer_addresses_table.php", MIG_CUSTOMER_ADDRESSES)
    write(f"database/migrations/{ts}_003_create_products_table.php", MIG_PRODUCTS)
    write(f"database/migrations/{ts}_004_migrate_legacy_customer_data.php", MIG_LEGACY_DATA)

    # Models
    print("\n📄 Models...")
    write("app/Models/CustomerPhone.php", MODEL_CUSTOMER_PHONE)
    write("app/Models/CustomerAddress.php", MODEL_CUSTOMER_ADDRESS)
    write("app/Models/Product.php", MODEL_PRODUCT)

    # Append به Customer model
    print("\n✎ Customer model — افزودن relations...")
    if append_if_missing("app/Models/Customer.php", "public function phones()", CUSTOMER_METHODS):
        pass
    else:
        print("  ⏭ از قبل موجود")

    # Service
    print("\n📄 Services...")
    write("app/Services/ProductSyncService.php", PRODUCT_SYNC_SERVICE)

    # Command
    print("\n📄 Commands...")
    write("app/Console/Commands/MigrateLegacyCustomerData.php", COMMAND_MIGRATE)

    # Livewire Components
    print("\n📄 Livewire Components...")
    write("app/Livewire/Components/CustomerPicker.php", CUSTOMER_PICKER_PHP)
    write("app/Livewire/Components/ProductPicker.php", PRODUCT_PICKER_PHP)

    # Views
    print("\n📄 Views...")
    write("resources/views/livewire/components/customer-picker.blade.php", CUSTOMER_PICKER_BLADE)
    write("resources/views/livewire/components/product-picker.blade.php", PRODUCT_PICKER_BLADE)

    # Dev test page
    print("\n📄 Dev test page...")
    write("app/Livewire/Dev/TestPickers.php", TEST_PICKERS_PHP)
    write("resources/views/livewire/dev/test-pickers.blade.php", TEST_PICKERS_BLADE)

    # Route — append
    print("\n✎ Routes...")
    routes_path = PROJECT / "routes/web.php"
    if routes_path.exists():
        with open(routes_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if '/dev/pickers' not in content:
            # داخل آخرین گروه auth middleware اضافه کن
            # پیدا کردن آخرین });
            idx = content.rstrip().rfind('});')
            if idx > 0:
                new_content = content[:idx] + ROUTE_PATCH + "\n" + content[idx:]
                with open(routes_path, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(new_content)
                print("  ✓ /dev/pickers اضافه شد")
        else:
            print("  ⏭ از قبل موجود")

    # WooCommerce append
    print("\n✎ WooCommerceService...")
    if append_if_missing("app/Services/WooCommerceService.php", "syncProductsToDatabase", WOO_APPEND):
        pass

    print("\n" + "═" * 64)
    print("✅ تمام! همه فایل‌ها ساخته شدند.")
    print("═" * 64)
    print(f"""
📋 حالا این دستورات رو اجرا کن:

  cd {PROJECT}
  php artisan optimize:clear
  php artisan migrate
  php artisan shopgun:migrate-legacy-customer-data
  php artisan route:clear
  php artisan view:clear

  ⚠️ سرور رو ببند و دوباره باز کن:
  php artisan serve

🌐 سپس این آدرس‌ها رو باز کن:

  http://127.0.0.1:8000/dev/pickers   ← تست Pickerها

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 چه چیزی ساخته شد:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✅ جدول customer_phones  → چند تلفن برای هر مشتری
  ✅ جدول customer_addresses → چند آدرس برای هر مشتری
  ✅ جدول products          → محصولات محلی (سینک با WooCommerce)
  ✅ 3 مدل: CustomerPhone, CustomerAddress, Product
  ✅ Customer model ارتقاء یافت:
     • $customer->phones          → همه تلفن‌ها
     • $customer->addPhone(...)   → افزودن تلفن
     • $customer->addAddress(...)  → افزودن آدرس
     • Customer::findByPhone(...) → پیدا کردن با تلفن
  ✅ CustomerPicker   → جستجوی هوشمند مشتری
  ✅ ProductPicker    → جستجو + سبد خرید
  ✅ Command: shopgun:migrate-legacy-customer-data
  ✅ ProductSyncService → سینک WooCommerce → DB
  ✅ صفحه /dev/pickers برای تست

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 قدم بعدی (بعد از تأیید تست):
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  • جایگزینی فیلدهای ساده‌ی تلفن/آدرس در فرم سفارش با CustomerPicker
  • جایگزینی inputهای محصول در فرم سفارش با ProductPicker
  • به‌روزرسانی Customer Profile برای نمایش چند تلفن/آدرس
""")

if __name__ == "__main__":
    main()