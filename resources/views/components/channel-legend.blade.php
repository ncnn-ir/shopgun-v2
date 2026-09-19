{-- Supply Button + Modal --}
<div class="flex flex-wrap items-center gap-2 mb-2">

    @php
        try {
            $__sc = \App\Models\Order::where(function ($q) {
                $q->whereIn('supply_status', ['awaiting_supply', 'pending', 'default'])
                  ->orWhereNull('supply_status');
            })->count();
        } catch (\Throwable $e) { $__sc = 0; }
    @endphp

    <button type="button"
        wire:click="$dispatch('openSupplyModal')"
        class="sg-supply-btn">
        📦 لیست تامین
        @if($__sc > 0)
            <span class="sg-supply-count">{{ $__sc }}</span>
        @endif
    </button>
</div>
