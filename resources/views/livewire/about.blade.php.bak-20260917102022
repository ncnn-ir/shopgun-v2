<div class="p-4 md:p-6 max-w-4xl mx-auto" dir="rtl">

    <div class="text-center mb-6">
        <div class="text-6xl mb-3">💎</div>
        <h1 class="text-3xl font-extrabold text-primary">ShopGun V2</h1>
        <p class="text-sm text-base-content/60 mt-1">جواهری مشاهیر — مدیریت سفارشات و شناسنامه</p>
        <p class="text-xs text-base-content/40 mt-1">گروه هنری اقاقیا</p>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        <div class="card bg-base-100 shadow border border-base-300">
            <div class="card-body p-4 text-center">
                <div class="text-3xl mb-2">📦</div>
                <div class="text-2xl font-bold text-primary">
                    {{ \App\Support\PersianNumber::toFa($stats['orders']) }}
                </div>
                <div class="text-xs text-base-content/60">سفارش</div>
            </div>
        </div>
        <div class="card bg-base-100 shadow border border-base-300">
            <div class="card-body p-4 text-center">
                <div class="text-3xl mb-2">👥</div>
                <div class="text-2xl font-bold text-primary">
                    {{ \App\Support\PersianNumber::toFa($stats['customers']) }}
                </div>
                <div class="text-xs text-base-content/60">مشتری</div>
            </div>
        </div>
        <div class="card bg-base-100 shadow border border-base-300">
            <div class="card-body p-4 text-center">
                <div class="text-3xl mb-2">🛍️</div>
                <div class="text-2xl font-bold text-primary">
                    {{ \App\Support\PersianNumber::toFa($stats['products']) }}
                </div>
                <div class="text-xs text-base-content/60">محصول</div>
            </div>
        </div>
        <div class="card bg-base-100 shadow border border-base-300">
            <div class="card-body p-4 text-center">
                <div class="text-3xl mb-2">💎</div>
                <div class="text-2xl font-bold text-primary">
                    {{ \App\Support\PersianNumber::toFa($stats['certificates']) }}
                </div>
                <div class="text-xs text-base-content/60">شناسنامه</div>
            </div>
        </div>
    </div>

    <div class="card bg-base-100 shadow border border-base-300 mb-4">
        <div class="card-body p-4">
            <h2 class="font-bold text-base mb-3">⚙️ اطلاعات فنی</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-2">
                <div class="flex justify-between p-2 bg-base-200/50 rounded">
                    <span class="text-base-content/60 text-sm">Laravel</span>
                    <span class="font-mono font-bold text-xs">{{ app()->version() }}</span>
                </div>
                <div class="flex justify-between p-2 bg-base-200/50 rounded">
                    <span class="text-base-content/60 text-sm">PHP</span>
                    <span class="font-mono font-bold text-xs">{{ PHP_VERSION }}</span>
                </div>
                <div class="flex justify-between p-2 bg-base-200/50 rounded">
                    <span class="text-base-content/60 text-sm">محیط</span>
                    <span class="font-mono text-xs">{{ app()->environment() }}</span>
                </div>
                <div class="flex justify-between p-2 bg-base-200/50 rounded">
                    <span class="text-base-content/60 text-sm">دیتابیس</span>
                    <span class="font-mono text-xs">{{ config('database.default') }}</span>
                </div>
            </div>
        </div>
    </div>

    <div class="card bg-base-100 shadow border border-base-300">
        <div class="card-body p-4">
            <h2 class="font-bold text-base mb-3">🔗 لینک‌های مفید</h2>
            <div class="flex flex-wrap gap-2">
                <a href="https://laravel.com/docs" target="_blank" class="btn btn-outline btn-sm">📖 Laravel Docs</a>
                <a href="https://livewire.laravel.com/docs" target="_blank" class="btn btn-outline btn-sm">⚡ Livewire</a>
                <a href="https://daisyui.com" target="_blank" class="btn btn-outline btn-sm">🌸 DaisyUI</a>
                <a href="{{ route('settings.health') }}" wire:navigate class="btn btn-primary btn-sm">🩺 سلامت سیستم</a>
            </div>
        </div>
    </div>

    <div class="text-center mt-6 text-xs text-base-content/40">
        ساخته‌شده توسط گروه هنری اقاقیا — ۱۴۰۵
    </div>
</div>
