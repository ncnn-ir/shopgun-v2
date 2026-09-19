<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class AccountingParty extends Model
{
    protected $fillable = ['type','name','company','phone','national_code','card_number','iban','notes','is_active'];
    protected $casts = ['is_active' => 'bool'];

    public const TYPES = [
        'manufacturer' => ['🏭', 'سازنده'],
        'staff'        => ['👤', 'پرسنل'],
        'customer'     => ['👥', 'مشتری'],
        'supplier'     => ['📦', 'تامین‌کننده'],
        'other'        => ['🏷', 'سایر'],
    ];

    public function transactions()
    {
        return $this->hasMany(AccountingTransaction::class, 'party_id');
    }

    public function getBalanceAttribute(): float
    {
        try {
            $credit = (float) $this->transactions()->where('type', 'credit')->sum('amount');
            $debit  = (float) $this->transactions()->where('type', 'debit')->sum('amount');
            return $credit - $debit;
        } catch (\Throwable $e) {
            return 0;
        }
    }

    public function getTypeMetaAttribute(): array
    {
        return self::TYPES[$this->type] ?? self::TYPES['other'];
    }
}
