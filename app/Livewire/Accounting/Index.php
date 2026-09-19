<?php

namespace App\Livewire\Accounting;

use Livewire\Component;

class Index extends Component
{
    public string $tab = 'transactions';

    public function render()
    {
        // اگه جدول‌های حسابداری وجود دارن، داده‌ها رو بارگذاری کن
        $transactions = collect();
        $parties = collect();
        $stats = [
            'total_credit' => 0,
            'total_debit'  => 0,
            'balance'      => 0,
            'count'        => 0,
            'parties'      => 0,
        ];
        $smsInbox = collect();

        try {
            if (class_exists(\App\Models\AccountingTransaction::class)) {
                $transactions = \App\Models\AccountingTransaction::with('party')
                    ->orderByDesc('occurred_at')->paginate(20);
                $parties = \App\Models\AccountingParty::withCount('transactions')
                    ->orderBy('name')->get();
                $stats['total_credit'] = (float) \App\Models\AccountingTransaction::where('type','credit')->sum('amount');
                $stats['total_debit']  = (float) \App\Models\AccountingTransaction::where('type','debit')->sum('amount');
                $stats['balance']      = $stats['total_credit'] - $stats['total_debit'];
                $stats['count']        = \App\Models\AccountingTransaction::count();
                $stats['parties']      = \App\Models\AccountingParty::count();
                $smsInbox = \App\Models\AccountingSmsInbox::with(['party','transaction'])
                    ->orderByDesc('created_at')->limit(10)->get();
            }
        } catch (\Throwable $e) {
            // اگه جدول‌ها نبودن، صفحه خالی ولی سالم نمایش داده می‌شه
        }

        return view('livewire.accounting.index', compact('transactions','parties','stats','smsInbox'))
            ->layout('components.layouts.app');
    }
}
