<header style="background:linear-gradient(135deg,var(--sg-primary),var(--sg-primary-hover));color:var(--sg-text-inverse);padding:12px 18px;display:flex;justify-content:space-between;align-items:center;gap:12px;box-shadow:var(--sg-shadow-sm);position:sticky;top:0;z-index:var(--sg-z-sticky)">

    {{-- عنوان صفحه --}}
    <div style="flex:1;min-width:0">
        <h1 style="margin:0;font-size:16px;font-weight:700">
            {{ $title ?? 'جواهری مشاهیر' }}
        </h1>
        <p style="margin:2px 0 0;font-size:11px;opacity:.8">{{ $subtitle ?? 'مدیریت سفارشات و شناسنامه' }}</p>
    </div>

    {{-- Actions --}}
    <div style="display:flex;align-items:center;gap:8px">
        <livewire:notification-center />

        <button type="button" onclick="sgToggleTheme()" title="تم"
                style="width:38px;height:38px;border-radius:50%;background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.2);color:#fff;cursor:pointer;font-size:15px;display:flex;align-items:center;justify-content:center">
            <span id="themeToggleIcon">🌙</span>
        </button>

        <a href="{{ route('settings.index') }}" wire:navigate title="تنظیمات"
           style="width:38px;height:38px;border-radius:50%;background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.2);color:#fff;cursor:pointer;font-size:15px;display:flex;align-items:center;justify-content:center;text-decoration:none">
            ⚙️
        </a>
    </div>
</header>
