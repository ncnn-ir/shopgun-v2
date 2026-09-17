<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Spatie\Activitylog\Models\Activity;
use Spatie\Activitylog\Models\Concerns\LogsActivity;
use Spatie\Activitylog\Support\LogOptions;

class Customer extends Model
{
    use LogsActivity;

    protected $fillable = ['name', 'phone', 'postal_code', 'address', 'notes', 'meta'];
    protected $casts = ['meta' => 'array'];

    public function getActivitylogOptions(): LogOptions
    {
        return LogOptions::defaults()
            ->logOnly(['name', 'phone', 'address', 'postal_code'])
            ->logOnlyDirty()
            ->useLogName('customer');
    }

    public function orders(): HasMany
    {
        return $this->hasMany(Order::class);
    }

    public function activities()
    {
        return Activity::query()
            ->where('subject_type', $this->getMorphClass())
            ->where('subject_id', $this->getKey())
            ->latest();
    }

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

    public static function normalizePhone(?string $phone): string
    {
        $s = preg_replace('/\D/', '', (string) $phone);
        if (str_starts_with($s, '0098')) $s = substr($s, 4);
        elseif (str_starts_with($s, '98') && strlen($s) > 10) $s = substr($s, 2);
        if (str_starts_with($s, '0') && strlen($s) > 10) $s = substr($s, 1);
        return $s;
    }

    public static function findByPhone(string $phone): ?self
    {
        $normalized = self::normalizePhone($phone);
        if ($normalized === '') return null;

        if (\Illuminate\Support\Facades\Schema::hasTable('customer_phones')) {
            $cp = \App\Models\CustomerPhone::where('phone', $normalized)->first();
            if ($cp) return $cp->customer;
        }

        return self::where('phone', $normalized)
            ->orWhere('phone', '0' . $normalized)
            ->orWhere('phone', '+98' . $normalized)
            ->orWhere('phone', '98' . $normalized)
            ->first();
    }

    public function addPhone(string $phone, ?string $label = null, bool $primary = false): ?\App\Models\CustomerPhone
    {
        $normalized = self::normalizePhone($phone);
        if ($normalized === '') return null;

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

        if ($isFirst && empty($this->phone)) {
            $this->update(['phone' => $normalized]);
        } elseif ($primary) {
            $this->update(['phone' => $normalized]);
        }

        return $cp;
    }

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

        if ($isFirst) {
            $this->update([
                'address'     => $data['address']     ?? $this->address,
                'postal_code' => $data['postal_code'] ?? $this->postal_code ?? null,
            ]);
        }

        return $ca;
    }

    public function getPhonesListAttribute(): string
    {
        return $this->phones->pluck('phone')->implode(' / ');
    }

    public function getAddressesListAttribute(): string
    {
        return $this->addresses->map(fn($a) => $a->short)->implode(' | ');
    }

}
