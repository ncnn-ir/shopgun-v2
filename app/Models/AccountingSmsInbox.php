<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class AccountingSmsInbox extends Model
{
    protected $fillable = ['raw_text','parsed_data','status','transaction_id','party_id'];
    protected $casts = ['parsed_data' => 'array'];

    public function transaction() { return $this->belongsTo(AccountingTransaction::class, 'transaction_id'); }
    public function party()       { return $this->belongsTo(AccountingParty::class, 'party_id'); }
}
