<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class AccountingTransaction extends Model
{
    protected $fillable = ['party_id','type','amount','description','reference','occurred_at','source','raw_sms','meta','user_id'];
    protected $casts = ['occurred_at' => 'datetime', 'meta' => 'array', 'amount' => 'float'];

    public function party() { return $this->belongsTo(AccountingParty::class, 'party_id'); }
    public function user()  { return $this->belongsTo(User::class); }
}
