<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class CertificateTemplate extends Model
{
    protected $fillable = [
        'name', 'slug', 'description', 'version', 'status',
        'design_data', 'sizes', 'logos', 'colors',
        'is_default', 'is_global', 'certificates_count',
        'created_by', 'published_at', 'archived_at',
    ];

    protected $casts = [
        'design_data' => 'array',
        'sizes' => 'array',
        'logos' => 'array',
        'colors' => 'array',
        'is_default' => 'boolean',
        'is_global' => 'boolean',
        'published_at' => 'datetime',
        'archived_at' => 'datetime',
    ];

    public function certificates(): HasMany
    {
        return $this->hasMany(Certificate::class, 'template_id');
    }

    public function scopePublished($q)
    {
        return $q->where('status', 'published');
    }

    public function scopeAvailable($q)
    {
        return $q->whereIn('status', ['draft', 'published']);
    }

    public static function findDefault(): ?self
    {
        return self::where('is_default', true)->published()->first()
            ?? self::published()->latest('id')->first();
    }

    public function publish(): void
    {
        $this->update([
            'status' => 'published',
            'published_at' => now(),
        ]);
    }

    public function archive(): void
    {
        $this->update([
            'status' => 'archived',
            'archived_at' => now(),
        ]);
    }

    public function duplicate(): self
    {
        $new = $this->replicate(['slug', 'is_default', 'certificates_count', 'published_at']);
        $new->name = $this->name . ' (کپی)';
        $new->slug = $this->slug . '-copy-' . uniqid();
        $new->version = $this->version;
        $new->status = 'draft';
        $new->is_default = false;
        $new->certificates_count = 0;
        $new->save();
        return $new;
    }
}
