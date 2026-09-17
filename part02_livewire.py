from pathlib import Path
import textwrap

PROJECT = Path.home() / "projects" / "shopgun-v2.1"

if not PROJECT.exists():
    raise SystemExit(f"❌ پروژه پیدا نشد: {PROJECT}")

def write_file(relative_path, content):
    path = PROJECT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    existed = path.exists()
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    action = "🔁" if existed else "✅"
    print(f"{action} {relative_path}")

print("═" * 60)
print("🚀 مرحله ۲ — کامپوننت‌ها، ویوها، Layout، روت‌ها")
print("═" * 60)
print()

# =========================================================
# ۱. Layout اصلی
# =========================================================
print("📦 Layout...")

write_file("resources/views/components/layouts/app.blade.php", r"""
<!DOCTYPE html>
<html lang="fa" dir="rtl" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>ShopGun — شاپگان</title>

    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">

    @vite(['resources/css/app.css', 'resources/js/app.js'])
    @livewireStyles
</head>
<body class="min-h-screen bg-base-200 font-sans text-base-content">

    @auth
        <livewire:global-search />
    @endauth

    <div class="drawer lg:drawer-open">
        <input id="main-drawer" type="checkbox" class="drawer-toggle" />

        <div class="drawer-content flex flex-col min-h-screen">

            <header class="navbar bg-base-100 border-b border-base-300 sticky top-0 z-30 shadow-sm">
                <div class="flex-none lg:hidden">
                    <label for="main-drawer" class="btn btn-square btn-ghost">
                        <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
                        </svg>
                    </label>
                </div>

                <div class="flex-1 px-3 flex items-center gap-3">
                    <span class="text-lg font-extrabold text-primary">ShopGun</span>
                    <span class="text-xs text-base-content/60">v2.1</span>

                    <button
                        onclick="window.dispatchEvent(new KeyboardEvent('keydown', {key: 'k', ctrlKey: true}))"
                        class="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-base-200 hover:bg-base-300 text-xs text-base-content/60 border border-base-300">
                        <span>🔍 جستجو</span>
                        <kbd class="kbd kbd-xs">Ctrl+K</kbd>
                    </button>
                </div>

                <div class="flex-none gap-2 items-center flex">
                    @auth
                        <livewire:notification-center />
                    @endauth

                    <div class="dropdown dropdown-end">
                        <div tabindex="0" role="button" class="btn btn-ghost btn-sm gap-2">
                            <div class="avatar placeholder">
                                <div class="bg-primary text-primary-content rounded-full w-8">
                                    <span class="text-xs font-bold">
                                        {{ mb_substr(Auth::user()->name ?? '؟', 0, 1) }}
                                    </span>
                                </div>
                            </div>
                            <span class="hidden sm:inline text-xs">
                                {{ Auth::user()->name ?? 'کاربر' }}
                            </span>
                        </div>
                        <ul tabindex="0" class="dropdown-content menu bg-base-100 rounded-box z-[1] w-56 p-2 shadow">
                            <li><a href="{{ route('settings.index') }}">⚙️ تنظیمات</a></li>
                            <li><a href="{{ route('activity-log') }}">📜 لاگ فعالیت‌ها</a></li>
                            <li>
                                <form method="POST" action="{{ route('logout') }}">
                                    @csrf
                                    <button type="submit" class="w-full text-right">🚪 خروج</button>
                                </form>
                            </li>
                        </ul>
                    </div>
                </div>
            </header>

            <main class="flex-1">
                {{ $slot }}
            </main>

            <footer class="footer footer-center p-4 bg-base-100 border-t border-base-300 text-xs text-base-content/60">
                <aside><p>ShopGun V2.1 — گروه هنری اقاقیا — نیشابور</p></aside>
            </footer>
        </div>

        <div class="drawer-side z-40">
            <label for="main-drawer" class="drawer-overlay"></label>
            <aside class="w-64 min-h-full bg-base-100 border-l border-base-300 flex flex-col">

                <div class="p-5 border-b border-base-300">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-xl bg-primary text-primary-content flex items-center justify-center font-extrabold">S</div>
                        <div>
                            <div class="font-extrabold text-base">شاپگان</div>
                            <div class="text-[10px] text-base-content/50">ShopGun v2.1</div>
                        </div>
                    </div>
                </div>

                <ul class="menu menu-md gap-1 p-3 flex-1">
                    <li>
                        <a href="{{ route('dashboard') }}" class="{{ request()->routeIs('dashboard') ? 'active' : '' }}">
                            <span class="text-lg">🏠</span><span>داشبورد</span>
                        </a>
                    </li>
                    <li>
                        <a href="{{ route('orders.index') }}" class="{{ request()->routeIs('orders.*') ? 'active' : '' }}">
                            <span class="text-lg">📦</span><span>سفارشات</span>
                        </a>
                    </li>
                    <li>
                        <a href="{{ route('orders.courier-list') }}" class="{{ request()->routeIs('orders.courier-list') ? 'active' : '' }}">
                            <span class="text-lg">🚚</span><span>لیست مامور</span>
                        </a>
                    </li>
                    <li>
                        <a href="{{ route('customers.index') }}" class="{{ request()->routeIs('customers.*') ? 'active' : '' }}">
                            <span class="text-lg">👥</span><span>مشتریان</span>
                        </a>
                    </li>
                    <li>
                        <a href="{{ route('certificates.index') }}" class="{{ request()->routeIs('certificates.*') ? 'active' : '' }}">
                            <span class="text-lg">💎</span><span>شناسنامه‌ها</span>
                        </a>
                    </li>
                    <li>
                        <a href="{{ route('reports.index') }}" class="{{ request()->routeIs('reports.*') ? 'active' : '' }}">
                            <span class="text-lg">📊</span><span>گزارش‌ها</span>
                        </a>
                    </li>
                    <li>
                        <a href="{{ route('activity-log') }}" class="{{ request()->routeIs('activity-log') ? 'active' : '' }}">
                            <span class="text-lg">📜</span><span>لاگ</span>
                        </a>
                    </li>
                    <li>
                        <a href="{{ route('settings.index') }}" class="{{ request()->routeIs('settings.*') ? 'active' : '' }}">
                            <span class="text-lg">⚙️</span><span>تنظیمات</span>
                        </a>
                    </li>
                </ul>

                <div class="p-3 border-t border-base-300 text-[10px] text-center text-base-content/50">
                    گروه هنری اقاقیا — ۱۴۰۵
                </div>
            </aside>
        </div>
    </div>

    @livewireScripts
</body>
</html>
""")

write_file("resources/views/components/layouts/guest.blade.php", r"""
<!DOCTYPE html>
<html lang="fa" dir="rtl" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ورود — ShopGun</title>
    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">
    @vite(['resources/css/app.css', 'resources/js/app.js'])
    @livewireStyles
</head>
<body class="min-h-screen bg-base-200 font-sans">
    {{ $slot }}
    @livewireScripts
</body>
</html>
""")

# =========================================================
# ۲. Auth Login
# =========================================================
print()
print("📦 Auth...")

write_file("app/Livewire/Auth/Login.php", r"""
<?php

namespace App\Livewire\Auth;

use Illuminate\Support\Facades\Auth;
use Livewire\Component;

class Login extends Component
{
    public string $email = '';
    public string $password = '';
    public bool $remember = false;

    public function login()
    {
        $this->validate([
            'email'    => 'required|email',
            'password' => 'required|min:6',
        ], [
            'email.required'    => 'ایمیل الزامی است.',
            'email.email'       => 'ایمیل معتبر نیست.',
            'password.required' => 'رمز عبور الزامی است.',
            'password.min'      => 'رمز عبور حداقل ۶ کاراکتر.',
        ]);

        if (! Auth::attempt(['email' => $this->email, 'password' => $this->password], $this->remember)) {
            $this->addError('email', 'ایمیل یا رمز عبور اشتباه است.');
            return;
        }

        session()->regenerate();

        return redirect()->intended(route('dashboard'));
    }

    public function render()
    {
        return view('livewire.auth.login')
            ->layout('components.layouts.guest');
    }
}
""")

write_file("resources/views/livewire/auth/login.blade.php", r"""
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
""")

# =========================================================
# ۳. Dashboard
# =========================================================
print()
print("📦 Dashboard...")

write_file("app/Livewire/Dashboard.php", r"""
<?php

namespace App\Livewire;

use App\Models\Channel;
use App\Models\Customer;
use App\Models\Order;
use Livewire\Component;

class Dashboard extends Component
{
    public function render()
    {
        $todayStart = now()->startOfDay();

        $stats = [
            'orders_total'    => Order::count(),
            'orders_today'    => Order::where('created_at', '>=', $todayStart)->count(),
            'orders_pending'  => Order::where('status', 'pending')->count(),
            'orders_check'    => Order::where('status', 'final-check')->count(),
            'orders_courier'  => Order::where('status', 'courier')->count(),
            'customers_total' => Customer::count(),
            'customers_today' => Customer::where('created_at', '>=', $todayStart)->count(),
            'amount_total'    => (float) Order::sum('amount'),
            'amount_today'    => (float) Order::where('created_at', '>=', $todayStart)->sum('amount'),
        ];

        $recentOrders = Order::with(['customer', 'channel'])
            ->latest('id')->limit(8)->get();

        $channels = Channel::where('is_active', true)
            ->withCount('orders')->orderByDesc('orders_count')->get();

        return view('livewire.dashboard', compact('stats', 'recentOrders', 'channels'))
            ->layout('components.layouts.app');
    }
}
""")

write_file("resources/views/livewire/dashboard.blade.php", r"""
<div class="p-6 space-y-6">

    <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
            <h1 class="text-2xl font-bold">🏠 داشبورد</h1>
            <div class="text-xs text-base-content/60 mt-1">{{ now()->format('Y/m/d H:i') }}</div>
        </div>
        <a href="{{ route('orders.create') }}" class="btn btn-primary btn-sm">➕ سفارش جدید</a>
    </div>

    <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div class="card bg-primary text-primary-content shadow">
            <div class="card-body p-4">
                <div class="text-xs opacity-80">📦 کل سفارشات</div>
                <div class="text-3xl font-extrabold mt-1">{{ number_format($stats['orders_total']) }}</div>
                <div class="text-xs opacity-80 mt-2">امروز: {{ number_format($stats['orders_today']) }}</div>
            </div>
        </div>
        <div class="card bg-success text-success-content shadow">
            <div class="card-body p-4">
                <div class="text-xs opacity-80">👥 کل مشتریان</div>
                <div class="text-3xl font-extrabold mt-1">{{ number_format($stats['customers_total']) }}</div>
                <div class="text-xs opacity-80 mt-2">امروز: {{ number_format($stats['customers_today']) }}</div>
            </div>
        </div>
        <div class="card bg-warning text-warning-content shadow">
            <div class="card-body p-4">
                <div class="text-xs opacity-80">📝 در انتظار</div>
                <div class="text-3xl font-extrabold mt-1">{{ number_format($stats['orders_pending']) }}</div>
                <div class="text-xs opacity-80 mt-2">چک نهایی: {{ number_format($stats['orders_check']) }}</div>
            </div>
        </div>
        <div class="card bg-info text-info-content shadow">
            <div class="card-body p-4">
                <div class="text-xs opacity-80">💰 مجموع فروش</div>
                <div class="text-xl font-extrabold mt-1" dir="ltr">{{ number_format($stats['amount_total']) }}</div>
                <div class="text-xs opacity-80 mt-2" dir="ltr">امروز: {{ number_format($stats['amount_today']) }}</div>
            </div>
        </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
        <a href="{{ route('orders.index', ['statusFilter' => 'pending']) }}" class="card bg-base-100 shadow hover:shadow-lg transition">
            <div class="card-body p-4 flex-row items-center justify-between">
                <div>
                    <div class="text-sm text-base-content/60">📝 ثبت سفارش</div>
                    <div class="text-2xl font-bold">{{ number_format($stats['orders_pending']) }}</div>
                </div>
                <div class="text-4xl">📝</div>
            </div>
        </a>
        <a href="{{ route('orders.index', ['statusFilter' => 'final-check']) }}" class="card bg-base-100 shadow hover:shadow-lg transition">
            <div class="card-body p-4 flex-row items-center justify-between">
                <div>
                    <div class="text-sm text-base-content/60">🔍 چک نهایی</div>
                    <div class="text-2xl font-bold">{{ number_format($stats['orders_check']) }}</div>
                </div>
                <div class="text-4xl">🔍</div>
            </div>
        </a>
        <a href="{{ route('orders.index', ['statusFilter' => 'courier']) }}" class="card bg-base-100 shadow hover:shadow-lg transition">
            <div class="card-body p-4 flex-row items-center justify-between">
                <div>
                    <div class="text-sm text-base-content/60">🚚 تحویل مامور</div>
                    <div class="text-2xl font-bold">{{ number_format($stats['orders_courier']) }}</div>
                </div>
                <div class="text-4xl">🚚</div>
            </div>
        </a>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">
        <div class="card bg-base-100 shadow lg:col-span-2">
            <div class="card-body">
                <div class="flex justify-between items-center mb-3">
                    <h2 class="card-title text-base">📋 آخرین سفارشات</h2>
                    <a href="{{ route('orders.index') }}" class="btn btn-ghost btn-xs">همه →</a>
                </div>
                @if($recentOrders->isEmpty())
                    <p class="text-sm text-base-content/50">هنوز سفارشی نیست.</p>
                @else
                    <div class="overflow-x-auto">
                        <table class="table table-sm">
                            <thead><tr><th>#</th><th>مشتری</th><th>وضعیت</th><th>تاریخ</th></tr></thead>
                            <tbody>
                                @foreach($recentOrders as $order)
                                    <tr>
                                        <td class="font-mono font-bold">
                                            <a href="{{ route('orders.show', $order) }}" class="link link-primary">{{ $order->order_number }}</a>
                                        </td>
                                        <td class="text-sm">{{ $order->customer?->name ?? '—' }}</td>
                                        <td><span class="badge badge-{{ $order->status_color }} badge-sm">{{ $order->status_label }}</span></td>
                                        <td class="text-xs">{{ $order->created_at?->format('m/d H:i') }}</td>
                                    </tr>
                                @endforeach
                            </tbody>
                        </table>
                    </div>
                @endif
            </div>
        </div>

        <div class="card bg-base-100 shadow">
            <div class="card-body">
                <h2 class="card-title text-base mb-3">🌐 کانال‌ها</h2>
                @php $maxCount = $channels->max('orders_count') ?: 1; @endphp
                @forelse($channels as $channel)
                    <div class="mb-3">
                        <div class="flex justify-between text-sm mb-1">
                            <span>{{ $channel->icon }} {{ $channel->name }}</span>
                            <span class="font-bold">{{ number_format($channel->orders_count) }}</span>
                        </div>
                        <div class="w-full bg-base-200 rounded-full h-2">
                            <div class="h-2 rounded-full" style="width: {{ round(($channel->orders_count / $maxCount) * 100) }}%; background-color: {{ $channel->color ?? '#1a5276' }};"></div>
                        </div>
                    </div>
                @empty
                    <p class="text-sm text-base-content/50">کانالی ثبت نشده.</p>
                @endforelse
            </div>
        </div>
    </div>
</div>
""")

print()
print("═" * 60)
print("✅ مرحله ۲ (بخش ۱) — Layout, Auth, Dashboard کامل شد")
print("═" * 60)
print()
print("📌 حالا اسکریپت بخش ۲ رو اجرا کن (part02b_livewire.py)")
print()
