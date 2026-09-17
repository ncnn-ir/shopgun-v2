<div class="min-h-screen flex items-center justify-center p-4 bg-base-200">
    <div class="card bg-base-100 shadow-xl w-full max-w-md">
        <div class="card-body">

            <div class="text-center mb-6">
                <div class="text-5xl mb-2">💎</div>
                <h1 class="text-2xl font-extrabold text-primary">ShopGun</h1>
                <p class="text-xs text-base-content/60 mt-1">ورود به سامانه شاپگان</p>
            </div>

            <form wire:submit="login" class="space-y-4">
                <div class="form-control">
                    <label class="label"><span class="label-text font-bold">📧 ایمیل</span></label>
                    <input type="email" wire:model="email" dir="ltr"
                           class="input input-bordered" placeholder="admin@shopgun.local" autofocus />
                    @error('email')
                        <label class="label"><span class="label-text-alt text-error">{{ $message }}</span></label>
                    @enderror
                </div>

                <div class="form-control">
                    <label class="label"><span class="label-text font-bold">🔐 رمز عبور</span></label>
                    <input type="password" wire:model="password" dir="ltr"
                           class="input input-bordered" placeholder="••••••••" />
                    @error('password')
                        <label class="label"><span class="label-text-alt text-error">{{ $message }}</span></label>
                    @enderror
                </div>

                <label class="label cursor-pointer justify-start gap-3">
                    <input type="checkbox" wire:model="remember" class="checkbox checkbox-sm" />
                    <span class="label-text">مرا به خاطر بسپار</span>
                </label>

                <button type="submit" class="btn btn-primary w-full">🚪 ورود</button>
            </form>

            <div class="divider text-xs">حساب‌های نمونه</div>
            <div class="text-xs space-y-1 text-base-content/60 font-mono" dir="ltr">
                <div>admin@shopgun.local / admin1234</div>
                <div>sales@shopgun.local / sales1234</div>
            </div>
        </div>
    </div>
</div>
