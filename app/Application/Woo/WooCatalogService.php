<?php

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
