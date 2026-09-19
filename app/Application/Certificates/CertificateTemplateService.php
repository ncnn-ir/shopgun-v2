<?php

namespace App\Application\Certificates;

use App\Models\CertificateTemplate;
use App\Models\AppSetting;
use Illuminate\Support\Facades\Cache;

/**
 * ★ CertificateTemplateService
 * مدیریت قالب‌های شناسنامه
 */
class CertificateTemplateService
{
    /**
     * لیست قالب‌های موجود (برای select)
     */
    public static function available(): \Illuminate\Database\Eloquent\Collection
    {
        return CertificateTemplate::available()->orderByDesc('is_default')->orderBy('name')->get();
    }

    /**
     * قالب پیش‌فرض
     */
    public static function default(): ?CertificateTemplate
    {
        return CertificateTemplate::findDefault();
    }

    /**
     * ایجاد قالب جدید
     */
    public static function create(array $data): CertificateTemplate
    {
        $slug = self::uniqueSlug($data['slug'] ?? $data['name']);

        return CertificateTemplate::create([
            'name' => $data['name'],
            'slug' => $slug,
            'description' => $data['description'] ?? null,
            'version' => $data['version'] ?? '1.0',
            'status' => 'draft',
            'design_data' => $data['design_data'] ?? null,
            'sizes' => $data['sizes'] ?? self::defaultSizes(),
            'logos' => $data['logos'] ?? [],
            'colors' => $data['colors'] ?? self::defaultColors(),
            'created_by' => auth()->id(),
        ]);
    }

    /**
     * کپی از قالب موجود
     */
    public static function duplicate(int $templateId, ?string $newName = null): ?CertificateTemplate
    {
        $tpl = CertificateTemplate::find($templateId);
        if (!$tpl) return null;

        $new = $tpl->duplicate();
        if ($newName) $new->update(['name' => $newName]);
        return $new;
    }

    /**
     * تنظیم به عنوان پیش‌فرض
     */
    public static function setDefault(int $templateId): void
    {
        CertificateTemplate::where('is_default', true)->update(['is_default' => false]);
        CertificateTemplate::where('id', $templateId)->update(['is_default' => true]);
        Cache::forget('cert_template_default');
    }

    /**
     * اعمال قالب روی یک شناسنامه
     */
    public static function applyToCertificate(int $templateId, \App\Models\Certificate $cert): void
    {
        $tpl = CertificateTemplate::find($templateId);
        if (!$tpl) return;

        $cert->update([
            'template_id' => $tpl->id,
            'design_data' => $tpl->design_data,
        ]);

        $tpl->increment('certificates_count');
    }

    // ═══════════════════════════════════════════════════════════
    public static function uniqueSlug(string $base): string
    {
        $slug = preg_replace('/[^a-z0-9-]+/i', '-', strtolower($base));
        $slug = trim(preg_replace('/-+/', '-', $slug), '-');
        if ($slug === '') $slug = 'template';

        $original = $slug;
        $i = 2;
        while (CertificateTemplate::where('slug', $slug)->exists()) {
            $slug = $original . '-' . $i;
            $i++;
        }
        return $slug;
    }

    public static function defaultSizes(): array
    {
        return [
            'width' => 6.5, 'height' => 6.5,
            'img_w' => 120, 'img_h' => 120,
            'qr_size' => 40, 'logo_w' => 28, 'logo_h' => 22,
            'code_font' => 11, 'title_font' => 20, 'desc_font' => 7,
            'col1' => 25, 'col2' => 25, 'col3' => 25, 'col4' => 25,
            'hide_desc' => false,
        ];
    }

    public static function defaultColors(): array
    {
        return [
            'primary' => '#1a5276',
            'gold' => '#c9a84c',
            'bg' => '#fffef9',
            'brown' => '#6b4423',
            'teal' => '#0d5c63',
        ];
    }
}
