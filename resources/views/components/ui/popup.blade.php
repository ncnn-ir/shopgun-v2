{{--
   کامپوننت پاپ‌آپ استاندارد ShopGun
   استفاده:
     <x-ui.popup id="product-{{ $id }}" title="عنوان">
        محتوا
        <x-slot:footer>... دکمه‌ها ...</x-slot:footer>
     </x-ui.popup>
   باز کردن:  Livewire: $this->dispatch('open-popup-product-5')
               JS: window.dispatchEvent(new CustomEvent('open-popup-product-5'))
--}}

@props([
    'id'       => 'popup',
    'title'    => 'عنوان',
    'maxWidth' => '32rem',
    'zIndex'   => 9000,
])

<div
    x-data="{ open: false }"
    x-on:open-popup-{{ $id }}.window="open = true"
    x-on:close-popup-{{ $id }}.window="open = false"
    x-show="open"
    x-cloak
    @keydown.escape.window="open = false"
    class="sg-popup-backdrop"
    style="z-index: {{ $zIndex }};"
    x-transition:enter="transition ease-out duration-200"
    x-transition:enter-start="opacity-0"
    x-transition:enter-end="opacity-100"
>
    {{-- Backdrop — کلیک بیرون => بستن --}}
    <div class="absolute inset-0" @click="open = false"></div>

    {{-- Panel --}}
    <div
        class="sg-popup-panel sg-anim-scale"
        style="max-width: {{ $maxWidth }}; z-index: {{ $zIndex + 1 }};"
        @click.stop
    >
        <div class="sg-popup-header">
            <h3 class="font-bold text-base">{{ $title }}</h3>
            <button type="button" class="sg-btn-icon" @click="open = false" aria-label="بستن">✕</button>
        </div>

        <div class="sg-popup-body">
            {{ $slot }}
        </div>

        @isset($footer)
            <div class="sg-popup-footer">
                {{ $footer }}
            </div>
        @endisset
    </div>
</div>
