<div class="relative">
    <input
        type="text"
        wire:model.live.debounce.400ms="value"
        dir="ltr"
        inputmode="tel"
        placeholder="{{ $placeholder }}"
        class="input input-bordered font-mono w-full text-base"
        autocomplete="off" />

    @if($showDropdown && count($suggestions) > 0)
        <div class="absolute top-full right-0 left-0 mt-1 bg-base-100 border-2 border-primary rounded-lg shadow-xl z-[60] max-h-80 overflow-y-auto">
            @foreach($suggestions as $s)
                <button
                    type="button"
                    wire:click="select(@js($s['phone']), @js($s['name']), @js($s['address']), @js($s['postal']))"
                    class="w-full text-right p-3 hover:bg-base-200 border-b border-base-200 last:border-0 transition">
                    <div class="flex justify-between items-center gap-2">
                        <div class="flex-1 min-w-0">
                            <div class="font-bold text-sm text-primary truncate">
                                {{ $s['name'] ?: '—' }}
                            </div>
                            <div class="font-mono text-xs text-base-content/60 mt-0.5" dir="ltr">
                                {{ $s['phone'] }}
                            </div>
                        </div>
                        <div class="badge badge-warning badge-sm whitespace-nowrap">
                            {{ $s['count'] }} سفارش
                        </div>
                    </div>
                </button>
            @endforeach
        </div>
    @endif
</div>
