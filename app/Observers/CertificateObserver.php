<?php

namespace App\Observers;

use App\Application\Certificates\CertificateSnapshotService;
use App\Models\Certificate;
use App\Models\AppNotification;
use Illuminate\Support\Facades\Route;

class CertificateObserver
{
    public function created(Certificate $certificate): void
    {
        try {
            CertificateSnapshotService::capture($certificate, 'issued');

            if (Route::has('certificates.show')) {
                AppNotification::broadcast(
                    type: 'certificate_created',
                    title: "شناسنامه جدید #{$certificate->code}",
                    message: ($certificate->stone_name ?? '') . ' — ' . ($certificate->metal ?? ''),
                    icon: '💎',
                    url: route('certificates.show', $certificate),
                    data: ['certificate_id' => $certificate->id],
                );
            }
        } catch (\Throwable $e) {
            \Log::warning('CertificateSnapshot created failed: ' . $e->getMessage());
        }
    }

    public function updated(Certificate $certificate): void
    {
        try {
            $changedFields = array_keys($certificate->getDirty());
            $important = ['stone_name', 'stone_en', 'metal', 'metal_carat', 'length', 'width', 'weight', 'brilliant', 'image_path'];

            $hasImportant = !empty(array_intersect($changedFields, $important));
            if (!$hasImportant) return;

            CertificateSnapshotService::capture($certificate, 'updated');
        } catch (\Throwable $e) {
            \Log::warning('CertificateSnapshot updated failed: ' . $e->getMessage());
        }
    }
}
