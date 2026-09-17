<div class="relative" x-data="{ open: @entangle('showDropdown') }" @click.outside="open = false">
    <input
        type="text"
        wire:model.live.debounce.500ms="value"
        dir="ltr"
        placeholder="SKU یا نام محصول..."
        class="input input-bordered font-mono w-full"
        autocomplete="off" />

    @if($showDropdown && count($suggestions) > 0)
        <div class="absolute top-full right-0 left-0 mt-1 bg-base-100 border-2 border-primary rounded-lg shadow-xl z-50 max-h-80 overflow-y-auto">
            @foreach($suggestions as $s)
                <button
                    type="button"
                    wire:click="select('{{ $s['sku'] }}', @js($s['title']), {{ $s['price'] }})"
                    class="w-full text-right p-3 hover:bg-base-200 border-b border-base-200 last:border-0">
                    <div class="flex items-center gap-3">
                        @if($s['image'])
                            <img src="{{ $s['image'] }}" class="w-10 h-10 rounded object-cover flex-shrink-0" />
                        @else
                            <div class="w-10 h-10 rounded bg-base-200 flex items-center justify-center flex-shrink-0">💎</div>
                        @endif
                        <div class="flex-1 min-w-0">
                            <div class="font-bold text-sm text-primary truncate">{{ $s['title'] }}</div>
                            <div class="font-mono text-xs text-base-content/60" dir="ltr">{{ $s['sku'] }}</div>
                        </div>
                        <div class="text-left flex-shrink-0">
                            <div class="font-bold text-xs text-warning">{{ number_format($s['price']) }}</div>
                            @if($s['stock'] !== null)
                                <div class="text-[10px] text-success">موجودی: {{ $s['stock'] }}</div>
                            @endif
                        </div>
                    </div>
                </button>
            @endforeach
        </div>
    @endif
</div>
