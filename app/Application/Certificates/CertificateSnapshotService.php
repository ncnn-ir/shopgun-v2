<?php

namespace App\Application\Certificates;

use App\Models\Certificate;
use App\Models\CertificateSnapshot;
use App\Models\ProductIdentity;
use Illuminate\Support\Facades\Log;

/**
 * ★ CertificateSnapshotService
 *
 * نگه‌داشتن snapshot از شناسنامه در لحظات کلیدی
 * - صدور
 * - ویرایش
 * - چاپ مجدد
 * - تغییر طرح
 *
 * ★ چرا؟ اگر قیمت/وزن محصول در WooCommerce عوض شود،
 *   شناسنامه صادرشده قدیمی نباید تغییر کند.
 */
class CertificateSnapshotService
{
    /**
     * ثبت snapshot جدید
     */
    public static function capture(Certificate $certificate, string $event = 'issued', ?array $productData = null): CertificateSnapshot
    {
        $sku = $certificate->sku;

        // اگه productData داده نشده ولی SKU داریم، از ProductIdentity بگیر
        if ($productData === null && $sku) {
            $identity = ProductIdentity::where('sku', $sku)->first();
            if ($identity) {
                $productData = $identity->last_known_woo_data;
            }
        }

        return CertificateSnapshot::create([
            'certificate_id' => $certificate->id,
            'event' => $event,
            'sku' => $sku,
            'stone_name' => $certificate->stone_name,
            'stone_en' => $certificate->stone_en,
            'metal' => $certificate->metal,
            'metal_carat' => $certificate->metal_carat,
            'length' => $certificate->length,
            'width' => $certificate->width,
            'weight' => $certificate->weight,
            'brilliant' => $certificate->brilliant,
            'image_path' => $certificate->image_path,
            'image_url' => $certificate->image_url,
            'product_data' => $productData,
            'meta' => [
                'ip' => request()?->ip(),
                'ua' => substr(request()?->userAgent() ?? '', 0, 200),
            ],
            'changed_by' => auth()->id(),
            'captured_at' => now(),
        ]);
    }

    /**
     * لیست snapshot های یک شناسنامه
     */
    public static function history(Certificate $certificate): \Illuminate\Database\Eloquent\Collection
    {
        return CertificateSnapshot::where('certificate_id', $certificate->id)
            ->latest('captured_at')
            ->get();
    }

    /**
     * تفاوت دو snapshot
     */
    public static function diff(CertificateSnapshot $old, CertificateSnapshot $new): array
    {
        $fields = ['stone_name', 'stone_en', 'metal', 'metal_carat', 'length', 'width', 'weight', 'brilliant'];
        $diff = [];

        foreach ($fields as $f) {
            if ((string) $old->$f !== (string) $new->$f) {
                $diff[] = [
                    'field' => $f,
                    'old' => $old->$f,
                    'new' => $new->$f,
                ];
            }
        }

        return $diff;
    }
}
