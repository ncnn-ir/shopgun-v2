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
        Route::get('/supply-list', \App\Livewire\Orders\SupplyList::class)->name('supply-list');

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
    // عمومی: لینک کوتاه شناسنامه
    Route::get('/Q/{code}', function (string $code) {
        $cert = \App\Models\Certificate::where('code', $code)->firstOrFail();
        return redirect()->route('certificates.show', $cert);
    })->name('cert.public');

    Route::prefix('certificates')->name('certificates.')->group(function () {
        Route::get('/', CertificatesIndex::class)->name('index');
        Route::get('/create', CertificatesCreate::class)->name('create');

        // ★ ترتیب مهم: مسیرهای خاص قبل از wildcard
        Route::get('/render/{certificate}', function (\App\Models\Certificate $certificate) {
            $html = \App\Services\CertRenderer::renderHtml($certificate);

            $download = request('download', '0') === '1';
            if ($download) {
                // صفحه با دکمه دانلود client-side
                $html = str_replace('</body></html>', '
                    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
                    <script>
                    window.addEventListener("load", function() {
                        // ★ پاک‌سازی oklch
                        var card = document.querySelector(".certificate");
                        if (card) {
                            var all = [card].concat(Array.from(card.querySelectorAll("*")));
                            all.forEach(function(el) {
                                try {
                                    var cs = window.getComputedStyle(el);
                                    ["color","backgroundColor","borderTopColor","borderRightColor","borderBottomColor","borderLeftColor","fill","stroke"].forEach(function(p) {
                                        var v = cs[p];
                                        if (v && v.indexOf("oklch") !== -1) {
                                            el.style[p] = "rgb(150,150,150)";
                                        }
                                    });
                                } catch(e) {}
                            });

                            setTimeout(function() {
                                html2canvas(card, {
                                    scale: 3,
                                    backgroundColor: "#fffef9",
                                    useCORS: true,
                                    allowTaint: true,
                                    logging: false
                                }).then(function(canvas) {
                                    var a = document.createElement("a");
                                    a.download = "certificate-' . $certificate->code . '.png";
                                    a.href = canvas.toDataURL("image/png");
                                    a.click();
                                    document.getElementById("dl-status").innerHTML = "✅ ذخیره شد — می‌توانید تب را ببندید";
                                }).catch(function(e) {
                                    document.getElementById("dl-status").innerHTML = "❌ " + e.message;
                                });
                            }, 1500);
                        }
                    });
                    </script>
                    <div id="dl-status" style="position:fixed;bottom:20px;left:20px;background:#16a34a;color:#fff;padding:12px 20px;border-radius:10px;font-family:Vazirmatn;font-weight:700;z-index:9999">⏳ در حال آماده‌سازی دانلود...</div>
                </body></html>', $html);
            }

            return response($html, 200)->header('Content-Type', 'text/html; charset=UTF-8');
        })->name('render');

        Route::get('/print', function () {
            $ids = trim((string) request('ids', ''));
            $auto = request('auto', '0') === '1';
            $ids_arr = array_values(array_filter(array_map('intval', explode(',', $ids))));
            if (empty($ids_arr)) abort(404);

            $certs = \App\Models\Certificate::whereIn('id', $ids_arr)->orderBy('id')->get()->all();
            if (empty($certs)) abort(404);

            $cols = count($certs) === 1 ? 1 : 3;
            $html = \App\Services\CertRenderer::renderBatchHtml($certs, $cols);

            if ($auto) {
                $script = '<script>window.addEventListener("load",function(){setTimeout(function(){window.print()},900)})</script>';
                $html = str_replace('</body></html>', $script . '</body></html>', $html);
            }
            return response($html, 200)->header('Content-Type', 'text/html; charset=UTF-8');
        })->name('print');

        // ★ جدول حرفه‌ای PowerGrid
        Route::get('/designer/{certificate?}', CertificatesDesigner::class)->name('designer');

        // ★ wildcard آخر
        Route::get('/{certificate}', CertificatesShow::class)->name('show');
    });

    // ═══ Bulk Products ═══
    Route::get('/products/bulk', \App\Livewire\Products\BulkCreate::class)->name('products.bulk');
    Route::get('/products/bulk/run/{run}', \App\Livewire\Products\BulkRunDetail::class)->name('products.bulk.run');

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
        Route::get('/sync', \App\Livewire\Settings\SyncDashboard::class)->name('sync');
        Route::get('/labels', \App\Livewire\Settings\Labels::class)->name('labels');
        Route::get('/channels', \App\Livewire\Settings\Channels::class)->name('channels');
        Route::get('/health', \App\Livewire\Settings\Health::class)->name('health');
        Route::get('/sync', \App\Livewire\Settings\SyncDashboard::class)->name('sync');
        Route::get('/labels', \App\Livewire\Settings\Labels::class)->name('labels');
        Route::get('/channels', \App\Livewire\Settings\Channels::class)->name('channels');
        Route::get('/channels', SettingsChannels::class)->name('channels');

        Route::post('/design-style', function () {
            \App\Models\AppSetting::put('design_style', request('style', 'material'), 'appearance');
            \Illuminate\Support\Facades\Cache::forget('app_settings_all');
            return response()->json(['ok' => true]);
        })->name('update-design-style');

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
