from pathlib import Path
import textwrap

PROJECT = Path.home() / "projects" / "shopgun-v2.1"

def write_file(rel, content):
    path = PROJECT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    print(f"✅ {rel}")

# =========================================================
# Settings Index — با ریشه درست
# =========================================================

write_file("resources/views/livewire/settings/index.blade.php", r"""
<div class="p-4 md:p-6 space-y-5 max-w-4xl mx-auto">

    <div class="flex flex-wrap items-center justify-between gap-3">
        <h1 class="text-xl md:text-2xl font-bold">⚙️ تنظیمات</h1>
    </div>

    {{-- دسترسی سریع --}}
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <a href="{{ route('settings.label') ?? '#' }}"
           class="card bg-base-100 shadow hover:shadow-lg transition cursor-pointer">
            <div class="card-body p-4 text-center">
                <div class="text-3xl">🏷️</div>
                <div class="font-bold text-sm mt-2">تنظیمات برچسب</div>
            </div>
        </a>
        <a href="{{ route('settings.backup') ?? '#' }}"
           class="card bg-base-100 shadow hover:shadow-lg transition cursor-pointer">
            <div class="card-body p-4 text-center">
                <div class="text-3xl">💾</div>
                <div class="font-bold text-sm mt-2">پشتیبان‌گیری</div>
            </div>
        </a>
        <a href="{{ route('activity-log') }}"
           class="card bg-base-100 shadow hover:shadow-lg transition cursor-pointer">
            <div class="card-body p-4 text-center">
                <div class="text-3xl">📜</div>
                <div class="font-bold text-sm mt-2">لاگ فعالیت‌ها</div>
            </div>
        </a>
        <a href="{{ url('/integrations/woocommerce') }}"
           class="card bg-base-100 shadow hover:shadow-lg transition cursor-pointer">
            <div class="card-body p-4 text-center">
                <div class="text-3xl">🛒</div>
                <div class="font-bold text-sm mt-2">ووکامرس</div>
            </div>
        </a>
    </div>

    {{-- پروفایل --}}
    <div class="card bg-base-100 shadow">
        <div class="card-body">
            <h2 class="card-title text-base mb-3">👤 پروفایل کاربری</h2>

            @if (session('profile_success'))
                <div class="alert alert-success mb-3 text-sm"><span>{{ session('profile_success') }}</span></div>
            @endif

            <div class="space-y-3">
                <div class="form-control">
                    <label class="label py-1"><span class="label-text font-bold text-sm">نام</span></label>
                    <input type="text" wire:model="name" class="input input-bordered input-sm w-full" />
                    @error('name') <span class="text-error text-xs">{{ $message }}</span> @enderror
                </div>
                <div class="form-control">
                    <label class="label py-1"><span class="label-text font-bold text-sm">ایمیل</span></label>
                    <input type="email" wire:model="email" dir="ltr" class="input input-bordered input-sm w-full" />
                    @error('email') <span class="text-error text-xs">{{ $message }}</span> @enderror
                </div>
                <div class="flex justify-end">
                    <button wire:click="updateProfile" class="btn btn-primary btn-sm">💾 ذخیره</button>
                </div>
            </div>
        </div>
    </div>

    {{-- تغییر رمز --}}
    <div class="card bg-base-100 shadow">
        <div class="card-body">
            <h2 class="card-title text-base mb-3">🔐 تغییر رمز عبور</h2>

            @if (session('password_success'))
                <div class="alert alert-success mb-3 text-sm"><span>{{ session('password_success') }}</span></div>
            @endif

            <div class="space-y-3">
                <div class="form-control">
                    <label class="label py-1"><span class="label-text font-bold text-sm">رمز جدید</span></label>
                    <input type="password" wire:model="newPassword" dir="ltr" class="input input-bordered input-sm w-full" />
                    @error('newPassword') <span class="text-error text-xs">{{ $message }}</span> @enderror
                </div>
                <div class="form-control">
                    <label class="label py-1"><span class="label-text font-bold text-sm">تکرار رمز جدید</span></label>
                    <input type="password" wire:model="newPasswordConfirm" dir="ltr" class="input input-bordered input-sm w-full" />
                    @error('newPasswordConfirm') <span class="text-error text-xs">{{ $message }}</span> @enderror
                </div>
                <div class="flex justify-end">
                    <button wire:click="updatePassword" class="btn btn-warning btn-sm">🔐 تغییر</button>
                </div>
            </div>
        </div>
    </div>

    {{-- کاربران --}}
    <div class="card bg-base-100 shadow">
        <div class="card-body">
            <h2 class="card-title text-base mb-3">👥 کاربران سیستم</h2>
            <div class="overflow-x-auto">
                <table class="table table-zebra table-sm">
                    <thead>
                        <tr>
                            <th>#</th>
                            <th>نام</th>
                            <th>ایمیل</th>
                            <th>نقش</th>
                        </tr>
                    </thead>
                    <tbody>
                        @foreach($users as $u)
                            <tr>
                                <td>{{ $u->id }}</td>
                                <td class="font-bold">{{ $u->name }}</td>
                                <td class="font-mono text-xs" dir="ltr">{{ $u->email }}</td>
                                <td>
                                    @foreach($u->roles as $r)
                                        <span class="badge badge-primary badge-sm">{{ $r->name }}</span>
                                    @endforeach
                                </td>
                            </tr>
                        @endforeach
                    </tbody>
                </table>
            </div>
        </div>
    </div>

    {{-- درباره --}}
    <div class="card bg-base-100 shadow">
        <div class="card-body">
            <h2 class="card-title text-base mb-3">ℹ️ درباره سیستم</h2>
            <div class="text-sm space-y-1.5 leading-7 text-base-content/80">
                <div><strong>نام:</strong> شاپگان نسخه ۲ (ShopGun V2)</div>
                <div><strong>سازنده:</strong> گروه هنری اقاقیا</div>
                <div><strong>معماری:</strong> امیر حاجی قاسمی</div>
                <div><strong>Laravel:</strong> {{ app()->version() }}</div>
                <div><strong>PHP:</strong> {{ PHP_VERSION }}</div>
            </div>
        </div>
    </div>
</div>
""")

print()
print("═" * 60)
print("✅ Settings Index بازنویسی شد (ریشه دار)")
print("═" * 60)
print()
