<div>
    @foreach($stack as $idx => $popup)
        <div class="sg-popup-layer open"
             style="z-index: {{ $popup['zIndex'] }}"
             wire:key="popup-{{ $popup['id'] }}"
             @click.self="$wire.dispatch('popup-close', { id: '{{ $popup['id'] }}' })">

            <div class="sg-popup-backdrop"
                 @click="$wire.dispatch('popup-close', { id: '{{ $popup['id'] }}' })"></div>

            <div class="sg-popup" @click.stop>
                @livewire($popup['component'], $popup['params'], key($popup['id']))
            </div>
        </div>
    @endforeach

    <script>
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            let stack = @js($stack);
            if (stack.length > 0) {
                let top = stack[stack.length - 1];
                Livewire.dispatch('popup-close', { id: top.id });
            }
        }
    });
    </script>
</div>
