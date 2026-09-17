<?php

use Illuminate\Support\Facades\Route;
use Illuminate\Support\Facades\Auth;
use App\Livewire\Auth\Login;
use App\Livewire\Dashboard;
use App\Livewire\ActivityLog;
use App\Livewire\About;
use App\Livewire\FileManagerPage;
use App\Livewire\Users\Index as UsersIndex;
use App\Livewire\Roles\Index as RolesIndex;
use App\Livewire\Shipments\Index as ShipmentsIndex;
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
use App\Livewire\Certificates\Designer as CertificatesDesigner;
use App\Livewire\Reports\Index as ReportsIndex;
use App\Livewire\Settings\Index as SettingsIndex;
use App\Livewire\Settings\Stones as SettingsStones;
use App\Livewire\Settings\Metals as SettingsMetals;
use App\Livewire\Settings\Channels as SettingsChannels;

/*
|--------------------------------------------------------------------------
| Web Routes — ShopGun V2
|--------------------------------------------------------------------------
*/

Route::get('/', fn () => redirect('/dashboard'));

/*
|--------------------------------------------------------------------------
| Guest Routes
|--------------------------------------------------------------------------
*/
Route::middleware('guest')->group(function () {
    Route::get('/login', Login::class)->name('login');
});

/*
|--------------------------------------------------------------------------
| Authenticated Routes
|--------------------------------------------------------------------------
*/
Route::middleware('auth')->group(function () {

    // ═══ Logout ═══
    Route::post('/logout', function () {
        Auth::logout();
        request()->session()->invalidate();
        request()->session()->regenerateToken();
        return redirect('/login');
    })->name('logout');

    // ═══ Dashboard ═══
    Route::get('/dashboard', Dashboard::class)->name('dashboard');
    Route::get('/about', About::class)->name('about');
    Route::get('/activity-log', ActivityLog::class)->name('activity-log');

    // ═══ Users Management ═══
    Route::get('/users', UsersIndex::class)->name('users.index');

    // ═══ Roles & Permissions ═══
    Route::get('/roles', RolesIndex::class)->name('roles.index');

    // ═══ Shipments ═══
    Route::get('/shipments', ShipmentsIndex::class)->name('shipments.index');

    // ═══ File Manager ═══
    Route::get('/file-manager', FileManagerPage::class)->name('file-manager');

    // ═══ Form Builder ═══
    Route::get('/forms', fn() => view('livewire.form-builder-page'))->name('forms.index');

    // ═══ Orders ═══
    Route::prefix('orders')->name('orders.')->group(function () {
        Route::get('/', OrdersIndex::class)->name('index');
        Route::get('/create', OrdersCreate::class)->name('create');
        Route::get('/import-tipax', ImportTipax::class)->name('import-tipax');
        Route::get('/courier-list', OrdersCourierList::class)->name('courier-list');
        Route::get('/bulk-print-labels', OrdersBulkPrintLabels::class)->name('bulk-print-labels');
        Route::get('/{order}/print-label', OrdersPrintLabel::class)->name('print-label');
        Route::get('/{order}/edit', OrdersEdit::class)->name('edit');
        Route::get('/{order}', OrdersShow::class)->name('show');
    });

    // ═══ Customers ═══
    Route::prefix('customers')->name('customers.')->group(function () {
        Route::get('/', CustomersIndex::class)->name('index');
        Route::get('/create', CustomersCreate::class)->name('create');
        Route::get('/{customer}/edit', CustomersEdit::class)->name('edit');
        Route::get('/{customer}', CustomersShow::class)->name('show');
    });

    // ═══ Certificates ═══
    Route::prefix('certificates')->name('certificates.')->group(function () {
        Route::get('/', CertificatesIndex::class)->name('index');
        Route::get('/create', CertificatesCreate::class)->name('create');
        Route::get('/designer/{certificate?}', CertificatesDesigner::class)->name('designer');
        Route::get('/{certificate}', CertificatesShow::class)->name('show');
    });

    // ═══ Reports ═══
    Route::get('/reports', ReportsIndex::class)->name('reports.index');

    // ═══ Reports - Export CSV ═══
    Route::get('/reports/export/excel', function () {
        $range = request('range', 'today');
        $start = match ($range) {
            'today' => now()->startOfDay(),
            'week'  => now()->subDays(7)->startOfDay(),
            'month' => now()->subDays(30)->startOfDay(),
            'year'  => now()->startOfYear(),
            default => now()->startOfDay(),
        };

        $orders = \App\Models\Order::where('created_at', '>=', $start)->get();

        $filename = 'report-' . now()->format('Ymd-His') . '.csv';
        header('Content-Type: text/csv; charset=UTF-8');
        header('Content-Disposition: attachment; filename="' . $filename . '"');

        $handle = fopen('php://output', 'w');
        fprintf($handle, chr(0xEF) . chr(0xBB) . chr(0xBF));
        fputcsv($handle, ['شماره سفارش', 'مشتری', 'تلفن', 'مبلغ', 'بیمه', 'وضعیت', 'تاریخ']);

        foreach ($orders as $o) {
            fputcsv($handle, [
                $o->order_number,
                $o->customer_name ?? '—',
                $o->phone,
                $o->amount,
                $o->insurance,
                $o->status,
                \App\Support\PersianDate::format($o->created_at, 'Y/m/d'),
            ]);
        }

        fclose($handle);
        exit;
    })->name('reports.export.excel');

    // ═══ Settings ═══
    Route::prefix('settings')->name('settings.')->group(function () {
        Route::get('/', SettingsIndex::class)->name('index');
        Route::get('/stones', SettingsStones::class)->name('stones');
        Route::get('/metals', SettingsMetals::class)->name('metals');
        Route::get('/health', \App\Livewire\Settings\Health::class)->name('health');
        Route::get('/labels', \App\Livewire\Settings\Labels::class)->name('labels');
        Route::get('/channels', \App\Livewire\Settings\Channels::class)->name('channels');
        Route::get('/health', \App\Livewire\Settings\Health::class)->name('health');
        Route::get('/labels', \App\Livewire\Settings\Labels::class)->name('labels');
        Route::get('/channels', \App\Livewire\Settings\Channels::class)->name('channels');
        Route::get('/channels', SettingsChannels::class)->name('channels');

        Route::post('/theme', function () {
            \App\Models\AppSetting::put('theme', request('theme'), 'appearance');
            return response()->json(['ok' => true]);
        })->name('update-theme');

        Route::post('/header-logo', function () {
            \App\Models\AppSetting::put('header_logo', request('logo'), 'appearance');
            return response()->json(['ok' => true]);
        })->name('update-header-logo');
    });
});
