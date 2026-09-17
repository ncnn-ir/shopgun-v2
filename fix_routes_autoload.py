from pathlib import Path
import textwrap

PROJECT = Path.home() / "projects" / "shopgun-v2.1"

def write_file(rel, content):
    path = PROJECT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    print(f"✅ {rel}")

# =========================================================
# ۱. Settings Index — استفاده از Route::has به جای route()
# =========================================================

write_file("resources/views/livewire/settings/index.blade.php", r"""
<div class="p-4 md:p-6 space-y-5 max-w-4xl mx-auto">

    <h1 class="text-xl md:text-2xl font-bold">⚙️ تنظیمات</h1>

    {{-- دسترسی سریع --}}
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        @if(\Illuminate\Support\Facades\Route::has('settings.label'))
            <a href="{{ route('settings.label') }}" class="card bg-base-100 shadow hover:shadow-lg transition cursor-pointer">
                <div class="card-body p-4 text-center">
                    <div class="text-3xl">🏷️</div>
                    <div class="font-bold text-sm mt-2">تنظیمات برچسب</div>
                </div>
            </a>
        @endif

        @if(\Illuminate\Support\Facades\Route::has('settings.backup'))
            <a href="{{ route('settings.backup') }}" class="card bg-base-100 shadow hover:shadow-lg transition cursor-pointer">
                <div class="card-body p-4 text-center">
                    <div class="text-3xl">💾</div>
                    <div class="font-bold text-sm mt-2">پشتیبان‌گیری</div>
                </div>
            </a>
        @endif

        @if(\Illuminate\Support\Facades\Route::has('activity-log'))
            <a href="{{ route('activity-log') }}" class="card bg-base-100 shadow hover:shadow-lg transition cursor-pointer">
                <div class="card-body p-4 text-center">
                    <div class="text-3xl">📜</div>
                    <div class="font-bold text-sm mt-2">لاگ فعالیت‌ها</div>
                </div>
            </a>
        @endif

        @if(\Illuminate\Support\Facades\Route::has('integrations.woocommerce'))
            <a href="{{ route('integrations.woocommerce') }}" class="card bg-base-100 shadow hover:shadow-lg transition cursor-pointer">
                <div class="card-body p-4 text-center">
                    <div class="text-3xl">🛒</div>
                    <div class="font-bold text-sm mt-2">ووکامرس</div>
                </div>
            </a>
        @endif
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
                        <tr><th>#</th><th>نام</th><th>ایمیل</th><th>نقش</th></tr>
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

# =========================================================
# ۲. روت‌های نهایی — با همه چیز
# =========================================================

write_file("routes/web.php", r"""
<?php

use Illuminate\Support\Facades\Route;
use Illuminate\Support\Facades\Auth;
use App\Livewire\Auth\Login;
use App\Livewire\Dashboard;
use App\Livewire\ActivityLog;
use App\Livewire\Orders\Index as OrdersIndex;
use App\Livewire\Orders\Create as OrdersCreate;
use App\Livewire\Orders\Show as OrdersShow;
use App\Livewire\Orders\Edit as OrdersEdit;
use App\Livewire\Orders\PrintLabel as OrdersPrintLabel;
use App\Livewire\Orders\BulkPrintLabels as OrdersBulkPrintLabels;
use App\Livewire\Orders\CourierList as OrdersCourierList;
use App\Livewire\Orders\ImportTipax;
use App\Livewire\Customers\Index as CustomersIndex;
use App\Livewire\Customers\Create as CustomersCreate;
use App\Livewire\Customers\Show as CustomersShow;
use App\Livewire\Customers\Edit as CustomersEdit;
use App\Livewire\Certificates\Index as CertificatesIndex;
use App\Livewire\Certificates\Create as CertificatesCreate;
use App\Livewire\Certificates\Show as CertificatesShow;
use App\Livewire\Reports\Index as ReportsIndex;
use App\Livewire\Settings\Index as SettingsIndex;

Route::get('/', fn () => redirect('/dashboard'));

Route::middleware('guest')->group(function () {
    Route::get('/login', Login::class)->name('login');
});

Route::middleware('auth')->group(function () {
    Route::post('/logout', function () {
        Auth::logout();
        request()->session()->invalidate();
        request()->session()->regenerateToken();
        return redirect('/login');
    })->name('logout');

    Route::get('/dashboard', Dashboard::class)->name('dashboard');
    Route::get('/activity-log', ActivityLog::class)->name('activity-log');

    // ---- Orders ----
    Route::prefix('orders')->name('orders.')->group(function () {
        Route::get('/', OrdersIndex::class)->name('index');
        Route::get('/create', OrdersCreate::class)->name('create');
        Route::get('/import-tipax', ImportTipax::class)->name('import-tipax');
        Route::get('/courier-list', OrdersCourierList::class)->name('courier-list');
        Route::get('/bulk-print-labels', OrdersBulkPrintLabels::class)->name('bulk-print-labels');

        // مسیرهای پویا آخر
        Route::get('/{order}/print-label', OrdersPrintLabel::class)->name('print-label');
        Route::get('/{order}/edit', OrdersEdit::class)->name('edit');
        Route::get('/{order}', OrdersShow::class)->name('show');
    });

    // ---- Customers ----
    Route::prefix('customers')->name('customers.')->group(function () {
        Route::get('/', CustomersIndex::class)->name('index');
        Route::get('/create', CustomersCreate::class)->name('create');
        Route::get('/{customer}/edit', CustomersEdit::class)->name('edit');
        Route::get('/{customer}', CustomersShow::class)->name('show');
    });

    // ---- Certificates ----
    Route::prefix('certificates')->name('certificates.')->group(function () {
        Route::get('/', CertificatesIndex::class)->name('index');
        Route::get('/create', CertificatesCreate::class)->name('create');
        Route::get('/{certificate}', CertificatesShow::class)->name('show');
    });

    // ---- Reports ----
    Route::get('/reports', ReportsIndex::class)->name('reports.index');

    // ---- Settings ----
    Route::get('/settings', SettingsIndex::class)->name('settings.index');
});
""")

# =========================================================
# ۳. بررسی وجود Certificates\Show
# =========================================================

cert_show = PROJECT / "app/Livewire/Certificates/Show.php"
if cert_show.exists():
    print(f"✅ Certificates/Show.php موجود است ({cert_show.stat().st_size} bytes)")
else:
    print("❌ Certificates/Show.php پیدا نشد — می‌سازم...")
    write_file("app/Livewire/Certificates/Show.php", r"""
<?php

namespace App\Livewire\Certificates;

use App\Models\Certificate;
use Livewire\Component;

class Show extends Component
{
    public Certificate $certificate;

    public function mount(Certificate $certificate): void
    {
        $this->certificate = $certificate->load(['customer', 'order']);
    }

    public function delete()
    {
        $code = $this->certificate->code;
        $this->certificate->delete();
        session()->flash('success', "شناسنامه #{$code} حذف شد.");
        return redirect()->route('certificates.index');
    }

    public function render()
    {
        return view('livewire.certificates.show')
            ->layout('components.layouts.app');
    }
}
""")

# =========================================================
# ۴. بررسی Certificates/Index
# =========================================================

cert_index = PROJECT / "app/Livewire/Certificates/Index.php"
if cert_index.exists():
    print(f"✅ Certificates/Index.php موجود است")
else:
    print("❌ Certificates/Index.php پیدا نشد — می‌سازم...")
    write_file("app/Livewire/Certificates/Index.php", r"""
<?php

namespace App\Livewire\Certificates;

use App\Models\Certificate;
use Livewire\Component;
use Livewire\WithPagination;

class Index extends Component
{
    use WithPagination;
    public string $search = '';

    public function updatingSearch(): void { $this->resetPage(); }

    public function delete(int $id): void
    {
        Certificate::find($id)?->delete();
        session()->flash('success', 'شناسنامه حذف شد.');
    }

    public function render()
    {
        $certificates = Certificate::query()
            ->with(['customer', 'order'])
            ->when($this->search, function ($q) {
                $q->where(function ($qq) {
                    $qq->where('code', 'like', "%{$this->search}%")
                       ->orWhere('serial', 'like', "%{$this->search}%")
                       ->orWhere('sku', 'like', "%{$this->search}%")
                       ->orWhere('stone_name', 'like', "%{$this->search}%");
                });
            })
            ->latest('id')->paginate(20);

        return view('livewire.certificates.index', compact('certificates'))
            ->layout('components.layouts.app');
    }
}
""")

# =========================================================
# ۵. print-a4 component (اگه لینک داره)
# =========================================================

print_a4 = PROJECT / "app/Livewire/Certificates/PrintA4.php"
if not print_a4.exists():
    print("✅ Certificates/PrintA4.php ساخته می‌شود...")
    write_file("app/Livewire/Certificates/PrintA4.php", r"""
<?php

namespace App\Livewire\Certificates;

use App\Models\Certificate;
use Livewire\Component;

class PrintA4 extends Component
{
    public array $certificates = [];

    public function mount(): void
    {
        $ids = request()->query('ids', '');
        $idArray = array_filter(explode(',', $ids));

        if (empty($idArray)) {
            $this->certificates = [];
            return;
        }

        $this->certificates = Certificate::whereIn('id', $idArray)
            ->orderBy('id')
            ->get()
            ->all();
    }

    public function render()
    {
        return view('livewire.certificates.print-a4')
            ->layout('components.layouts.app');
    }
}
""")

print()
print("═" * 60)
print("✅ همه اصلاحات انجام شد")
print("═" * 60)
print()
print("📌 اجرا کن:")
print("   composer dump-autoload")
print("   php artisan optimize:clear")
print("   php artisan route:list | grep certificates")
print("   php artisan serve --host=0.0.0.0 --port=8000")
print()
