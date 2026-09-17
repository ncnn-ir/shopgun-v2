<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Spatie\Activitylog\Models\Activity;
use Spatie\Activitylog\Models\Concerns\LogsActivity;
use Spatie\Activitylog\Support\LogOptions;

class Certificate extends Model
{
    use LogsActivity;

    protected $fillable = [
        'code', 'serial', 'sku', 'stone_name', 'stone_en', 'stone_origin', 'stone_flag',
        'metal', 'metal_en', 'metal_carat', 'length', 'width', 'weight', 'brilliant',
        'image_path', 'order_id', 'customer_id', 'issued_at', 'design_data', 'meta',
    ];

    protected $casts = [
        'issued_at'   => 'datetime',
        'design_data' => 'array',
        'meta'        => 'array',
    ];

    public function getActivitylogOptions(): LogOptions
    {
        return LogOptions::defaults()
            ->logOnly(['code', 'stone_name', 'metal', 'weight'])
            ->logOnlyDirty()
            ->useLogName('certificate');
    }

    public function order(): BelongsTo    { return $this->belongsTo(Order::class); }
    public function customer(): BelongsTo { return $this->belongsTo(Customer::class); }

    public function activities()
    {
        return Activity::query()
            ->where('subject_type', $this->getMorphClass())
            ->where('subject_id', $this->getKey())
            ->latest();
    }

    public static function generateCode(): string
    {
        do { $code = (string) random_int(100000, 999999); }
        while (self::where('code', $code)->exists());
        return $code;
    }

    public static function generateSerial(string $code, string $stoneEn = 'XXX'): string
    {
        $now  = now();
        $ymd  = $now->format('ymd');
        $hm   = $now->format('Hi');
        $abbr = strtoupper(substr(preg_replace('/[^A-Za-z]/', '', $stoneEn), 0, 3)) ?: 'XXX';
        return "MJ-{$ymd}-{$hm}-{$code}-{$abbr}-A";
    }

    public function getPublicUrlAttribute(): string
    {
        return url("/Q/{$this->code}");
    }

    public function getQrUrlAttribute(): string
    {
        return 'https://api.qrserver.com/v1/create-qr-code/?size=300x300&margin=1&data='
            . urlencode($this->public_url);
    }

    // عدد بدون .00
    protected static function fmt($v): string
    {
        if ($v === null || $v === '') return '—';
        $f = (float) $v;
        if ($f == 0) return '0';
        if (floor($f) == $f) return (string) (int) $f;
        return rtrim(rtrim(number_format($f, 2, '.', ''), '0'), '.');
    }

    public function getLengthCleanAttribute(): string { return self::fmt($this->length); }
    public function getWidthCleanAttribute(): string  { return self::fmt($this->width); }
    public function getWeightCleanAttribute(): string { return self::fmt($this->weight); }
    public function getBrilliantCleanAttribute(): string { return self::fmt($this->brilliant); }

    public function getDimensionAttribute(): string
    {
        return $this->length_clean . '×' . $this->width_clean;
    }

    public function getDesignOrDefaultAttribute(): array
    {
        if (! empty($this->design_data) && is_array($this->design_data)) {
            return $this->design_data;
        }

        return [
            'version' => '1.0',
            'elements' => [
                ['id' => 'title',  'type' => 'text', 'text' => 'Certificate',           'x' => 180, 'y' => 30,  'fontSize' => 28, 'fill' => '#6b4423', 'fontWeight' => 'bold'],
                ['id' => 'stone',  'type' => 'text', 'text' => '{stoneEn}',             'x' => 160, 'y' => 90,  'fontSize' => 20, 'fill' => '#0369a1', 'fontWeight' => 'bold'],
                ['id' => 'metal',  'type' => 'text', 'text' => '{metal} ({carat})',     'x' => 160, 'y' => 130, 'fontSize' => 14, 'fill' => '#334155'],
                ['id' => 'size',   'type' => 'text', 'text' => '{length}×{width} mm',   'x' => 160, 'y' => 165, 'fontSize' => 12, 'fill' => '#334155'],
                ['id' => 'weight', 'type' => 'text', 'text' => 'Weight: {weight} gr',   'x' => 160, 'y' => 195, 'fontSize' => 12, 'fill' => '#334155'],
                ['id' => 'code',   'type' => 'text', 'text' => '#{code}',                'x' => 160, 'y' => 230, 'fontSize' => 14, 'fill' => '#b45309', 'fontWeight' => 'bold'],
                ['id' => 'qr',     'type' => 'qr',   'text' => '',                       'x' => 200, 'y' => 200, 'size' => 100],
            ],
        ];
    }
}
