<?php

namespace App\Application\Actions;

use App\Application\Certificates\CertificateSnapshotService;
use App\Models\Certificate;
use App\Models\Customer;
use App\Models\Order;
use App\Models\ProductIdentity;
use App\Application\Notifications\NotificationService;

/**
 * ★ IssueCertificateAction
 * نقطه واحد صدور شناسنامه
 */
class IssueCertificateAction
{
    /**
     * @param array $data {
     *   stone_name, stone_en, stone_origin, stone_flag,
     *   metal, metal_en, metal_carat,
     *   length, width, weight, brilliant,
     *   image_path, image_url,
     *   customer_id, order_id, sku, design_data
     * }
     */
    public function execute(array $data): Certificate
    {
        // ۱. تولید کد و سریال
        $code = Certificate::generateCode();
        $serial = Certificate::generateSerial($code, $data['stone_en'] ?? $data['stone_name'] ?? 'XXX');

        // ۲. اگر SKU داشت، ProductIdentity را بروز کن
        if (!empty($data['sku'])) {
            $this->resolveProductIdentity($data['sku']);
        }

        // ۳. ایجاد شناسنامه
        $cert = Certificate::create([
            'code' => $code,
            'serial' => $serial,
            'sku' => $data['sku'] ?? null,
            'stone_name' => $data['stone_name'] ?? '',
            'stone_en' => $data['stone_en'] ?? null,
            'stone_origin' => $data['stone_origin'] ?? null,
            'stone_flag' => $data['stone_flag'] ?? null,
            'metal' => $data['metal'] ?? '',
            'metal_en' => $data['metal_en'] ?? null,
            'metal_carat' => $data['metal_carat'] ?? null,
            'length' => (float) ($data['length'] ?? 0),
            'width' => (float) ($data['width'] ?? 0),
            'weight' => (float) ($data['weight'] ?? 0),
            'brilliant' => (int) ($data['brilliant'] ?? 0),
            'image_path' => $data['image_path'] ?? null,
            'image_url' => $data['image_url'] ?? null,
            'customer_id' => $data['customer_id'] ?? null,
            'order_id' => $data['order_id'] ?? null,
            'design_data' => $data['design_data'] ?? null,
            'issued_at' => now(),
        ]);

        // ۴. Snapshot (خودکار توسط Observer انجام می‌شود — این fallback)
        try {
            CertificateSnapshotService::capture($cert, 'issued');
        } catch (\Throwable $e) {}

        // ۵. اعلان
        try {
            NotificationService::toAll(
                type: 'certificate_issued',
                title: "شناسنامه #{$code} صادر شد",
                message: ($data['stone_name'] ?? '') . ' — ' . ($data['metal'] ?? ''),
                icon: '💎',
                url: route('certificates.show', $cert),
                data: ['certificate_id' => $cert->id],
            );
        } catch (\Throwable $e) {}

        return $cert;
    }

    protected function resolveProductIdentity(string $sku): ?ProductIdentity
    {
        try {
            $resolver = new \App\Application\Products\ProductResolver();
            return $resolver->resolve($sku, true);
        } catch (\Throwable $e) {
            return null;
        }
    }
}
