@props([
    'id' => 'modal',
    'title' => 'عنوان',
    'icon' => '📋',
    'maxWidth' => '2xl',
])

@php
    $maxWidthClass = match($maxWidth) {
        'sm'  => 'max-w-md',
        'md'  => 'max-w-xl',
        'lg'  => 'max-w-2xl',
        'xl'  => 'max-w-3xl',
        '2xl' => 'max-w-4xl',
        '3xl' => 'max-w-5xl',
        default => 'max-w-2xl',
    };
@endphp

<div id="{{ $id }}" class="fixed inset-0 z-[90] hidden items-start justify-center p-4 overflow-y-auto">
    {{-- Backdrop --}}
    <div class="modal-backdrop fixed inset-0 bg-black/60 backdrop-blur-md transition-opacity duration-300 opacity-0"
         onclick="closeModal('{{ $id }}')"></div>

    {{-- Panel --}}
    <div class="modal-panel relative bg-base-100 rounded-2xl shadow-2xl w-full {{ $maxWidthClass }} my-8 md:my-16
                border border-base-300 transform transition-all duration-300 opacity-0 scale-95 translate-y-4">

        {{-- Header --}}
        <div class="flex items-center justify-between p-4 border-b border-base-300 bg-gradient-to-l from-primary/10 to-transparent rounded-t-2xl sticky top-0 z-10">
            <div class="flex items-center gap-3">
                <div class="w-9 h-9 rounded-lg bg-gradient-to-br from-cyan-500 to-teal-600 flex items-center justify-center text-white text-base shadow">
                    {{ $icon }}
                </div>
                <h2 class="font-bold text-base">{{ $title }}</h2>
            </div>
            <button type="button" onclick="closeModal('{{ $id }}')" class="btn btn-ghost btn-sm btn-circle">✕</button>
        </div>

        {{-- Body --}}
        <div class="p-5 max-h-[calc(100vh-16rem)] overflow-y-auto">
            {{ $slot }}
        </div>

        {{-- Footer --}}
        @if(isset($footer))
            <div class="p-4 border-t border-base-300 flex justify-end gap-2 rounded-b-2xl bg-base-200/50">
                {{ $footer }}
            </div>
        @endif
    </div>
</div>

@once
@push('scripts')
<script>
    function openModal(id) {
        const m = document.getElementById(id);
        if (!m) return;
        m.classList.remove('hidden');
        m.classList.add('flex');
        document.body.style.overflow = 'hidden';
        requestAnimationFrame(() => {
            m.querySelector('.modal-backdrop').classList.remove('opacity-0');
            m.querySelector('.modal-panel').classList.remove('opacity-0', 'scale-95', 'translate-y-4');
        });
    }

    function closeModal(id) {
        const m = document.getElementById(id);
        if (!m) return;
        m.querySelector('.modal-backdrop').classList.add('opacity-0');
        m.querySelector('.modal-panel').classList.add('opacity-0', 'scale-95', 'translate-y-4');
        setTimeout(() => {
            m.classList.add('hidden');
            m.classList.remove('flex');
            document.body.style.overflow = '';
        }, 250);
    }

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            document.querySelectorAll('.modal-panel').forEach(p => {
                const m = p.closest('[id]');
                if (m && ! m.classList.contains('hidden')) closeModal(m.id);
            });
        }
    });
</script>
@endpush
@endonce
