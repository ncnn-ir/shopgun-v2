from pathlib import Path
import textwrap

PROJECT = Path.home() / "projects" / "shopgun-v2.1"

def write_file(rel, content):
    path = PROJECT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    print(f"✅ {rel}")

# =========================================================
# ۱. Customers/Create
# =========================================================

write_file("resources/views/livewire/customers/create.blade.php", r"""
<div class="p-4 md:p-6 max-w-3xl mx-auto">
    <div class="flex items-center gap-3 mb-6">
        <a href="{{ route('customers.index') }}" class="btn btn-ghost btn-sm">→</a>
        <h1 class="text-xl md:text-2xl font-bold">➕ مشتری جدید</h1>
    </div>

    <div class="card bg-base-100 shadow">
        <div class="card-body gap-4">

            <div class="form-control">
                <label class="label py-1"><span class="label-text font-bold text-sm">📱 تلفن *</span></label>
                <input type="text" wire:model="phone" dir="ltr" class="input input-bordered w-full font-mono" placeholder="09151234567" />
                @error('phone') <span class="text-error text-xs mt-1">{{ $message }}</span> @enderror
            </div>

            <div class="form-control">
                <label class="label py-1"><span class="label-text font-bold text-sm">👤 نام</span></label>
                <input type="text" wire:model="name" class="input input-bordered w-full" />
            </div>

            <div class="form-control">
                <label class="label py-1"><span class="label-text font-bold text-sm">📮 کدپستی</span></label>
                <input type="text" wire:model="postalCode" dir="ltr" class="input input-bordered w-full font-mono" />
            </div>

            <div class="form-control">
                <label class="label py-1"><span class="label-text font-bold text-sm">📍 آدرس</span></label>
                <textarea wire:model="address" class="textarea textarea-bordered w-full" rows="3"></textarea>
            </div>

            <div class="form-control">
                <label class="label py-1"><span class="label-text font-bold text-sm">📝 یادداشت</span></label>
                <textarea wire:model="notes" class="textarea textarea-bordered w-full" rows="2"></textarea>
            </div>

            <div class="flex flex-col-reverse md:flex-row justify-end gap-2 mt-4">
                <a href="{{ route('customers.index') }}" class="btn btn-ghost w-full md:w-auto">انصراف</a>
                <button wire:click="save" wire:loading.attr="disabled" class="btn btn-primary w-full md:w-auto">
                    <span wire:loading.remove wire:target="save">✅ ذخیره</span>
                    <span wire:loading wire:target="save">⏳...</span>
                </button>
            </div>
        </div>
    </div>
</div>
""")

# =========================================================
# ۲. Customers/Show
# =========================================================

write_file("resources/views/livewire/customers/show.blade.php", r"""
<div class="p-4 md:p-6 max-w-4xl mx-auto">
    <div class="flex flex-wrap items-center justify-between gap-3 mb-6">
        <div class="flex items-center gap-3">
            <a href="{{ route('customers.index') }}" class="btn btn-ghost btn-sm">→</a>
            <h1 class="text-xl md:text-2xl font-bold">👤 {{ $customer->name ?? $customer->phone }}</h1>
        </div>
        <div class="flex gap-2">
            <a href="{{ route('customers.edit', $customer) }}" class="btn btn-warning btn-sm">✏️ ویرایش</a>
            <button wire:click="delete" wire:confirm="حذف شود؟" class="btn btn-error btn-sm">🗑️</button>
        </div>
    </div>

    @if (session('success'))
        <div class="alert alert-success mb-4 text-sm"><span>{{ session('success') }}</span></div>
    @endif

    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 mb-4">
        <div class="card bg-primary text-primary-content shadow">
            <div class="card-body p-4">
                <div class="text-xs opacity-80">تعداد سفارش</div>
                <div class="text-2xl font-bold">{{ number_format($orders->count()) }}</div>
            </div>
        </div>
        <div class="card bg-success text-success-content shadow">
            <div class="card-body p-4">
                <div class="text-xs opacity-80">مجموع خرید</div>
                <div class="text-xl font-bold">{{ number_format((float) $totalAmount) }}</div>
            </div>
        </div>
        <div class="card bg-base-100 shadow">
            <div class="card-body p-4">
                <div class="text-xs text-base-content/60">اولین سفارش</div>
                <div class="text-sm font-bold">{{ $orders->last()?->created_at?->format('Y/m/d') ?? '—' }}</div>
            </div>
        </div>
        <div class="card bg-base-100 shadow">
            <div class="card-body p-4">
                <div class="text-xs text-base-content/60">آخرین سفارش</div>
                <div class="text-sm font-bold">{{ $orders->first()?->created_at?->format('Y/m/d') ?? '—' }}</div>
            </div>
        </div>
    </div>

    <div class="card bg-base-100 shadow mb-4">
        <div class="card-body">
            <h2 class="card-title text-base mb-2">📋 اطلاعات تماس</h2>
            <div class="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                <div class="flex justify-between p-2 rounded bg-base-200/50">
                    <span class="text-base-content/60">تلفن:</span>
                    <span class="font-mono" dir="ltr">{{ $customer->phone }}</span>
                </div>
                <div class="flex justify-between p-2 rounded bg-base-200/50">
                    <span class="text-base-content/60">کدپستی:</span>
                    <span class="font-mono" dir="ltr">{{ $customer->postal_code ?? '—' }}</span>
                </div>
            </div>
            <div class="mt-3 text-sm leading-7 p-2 rounded bg-base-200/50">
                <strong>آدرس:</strong> {{ $customer->address ?? '—' }}
            </div>
        </div>
    </div>

    <div class="card bg-base-100 shadow mb-4">
        <div class="card-body">
            <div class="flex justify-between items-center mb-3">
                <h2 class="card-title text-base">📦 سفارشات</h2>
                <a href="{{ route('orders.create') }}" class="btn btn-primary btn-xs">➕ سفارش جدید</a>
            </div>
            @if($orders->isEmpty())
                <p class="text-sm text-base-content/50">هنوز سفارشی نیست.</p>
            @else
                <div class="overflow-x-auto">
                    <table class="table table-zebra table-sm">
                        <thead>
                            <tr><th>#</th><th>وضعیت</th><th>کانال</th><th>بیمه</th><th>تاریخ</th><th></th></tr>
                        </thead>
                        <tbody>
                            @foreach($orders as $o)
                                <tr>
                                    <td class="font-mono font-bold">{{ $o->order_number }}</td>
                                    <td><span class="badge badge-{{ $o->status_color }} badge-sm">{{ $o->status_label }}</span></td>
                                    <td class="text-xs">{{ $o->channel?->icon }} {{ $o->channel?->name ?? '—' }}</td>
                                    <td>{{ number_format((float) $o->insurance) }}</td>
                                    <td class="text-xs">{{ $o->created_at?->format('Y/m/d') }}</td>
                                    <td><a href="{{ route('orders.show', $o) }}" class="btn btn-ghost btn-xs">👁️</a></td>
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
            <h2 class="card-title text-base mb-3">📜 تاریخچه</h2>
            @if($activities->isEmpty())
                <p class="text-sm text-base-content/50">تغییری ثبت نشده.</p>
            @else
                <div class="space-y-2">
                    @foreach($activities as $a)
                        <div class="flex gap-3 text-sm border-r-2 border-primary/30 pr-3 py-1">
                            <div class="text-xs text-base-content/50 whitespace-nowrap">{{ $a->created_at?->format('Y/m/d H:i') }}</div>
                            <div class="flex-1 font-bold">{{ $a->description }}</div>
                        </div>
                    @endforeach
                </div>
            @endif
        </div>
    </div>
</div>
""")

# =========================================================
# ۳. Customers/Edit
# =========================================================

write_file("resources/views/livewire/customers/edit.blade.php", r"""
<div class="p-4 md:p-6 max-w-3xl mx-auto">
    <div class="flex items-center gap-3 mb-6">
        <a href="{{ route('customers.show', $customer) }}" class="btn btn-ghost btn-sm">→</a>
        <h1 class="text-xl md:text-2xl font-bold">✏️ ویرایش مشتری</h1>
    </div>

    <div class="card bg-base-100 shadow">
        <div class="card-body gap-4">

            <div class="form-control">
                <label class="label py-1"><span class="label-text font-bold text-sm">📱 تلفن *</span></label>
                <input type="text" wire:model="phone" dir="ltr" class="input input-bordered w-full font-mono" />
                @error('phone') <span class="text-error text-xs mt-1">{{ $message }}</span> @enderror
            </div>

            <div class="form-control">
                <label class="label py-1"><span class="label-text font-bold text-sm">👤 نام</span></label>
                <input type="text" wire:model="name" class="input input-bordered w-full" />
            </div>

            <div class="form-control">
                <label class="label py-1"><span class="label-text font-bold text-sm">📮 کدپستی</span></label>
                <input type="text" wire:model="postalCode" dir="ltr" class="input input-bordered w-full font-mono" />
            </div>

            <div class="form-control">
                <label class="label py-1"><span class="label-text font-bold text-sm">📍 آدرس</span></label>
                <textarea wire:model="address" class="textarea textarea-bordered w-full" rows="3"></textarea>
            </div>

            <div class="form-control">
                <label class="label py-1"><span class="label-text font-bold text-sm">📝 یادداشت</span></label>
                <textarea wire:model="notes" class="textarea textarea-bordered w-full" rows="2"></textarea>
            </div>

            <div class="flex flex-col-reverse md:flex-row justify-end gap-2 mt-4">
                <a href="{{ route('customers.show', $customer) }}" class="btn btn-ghost w-full md:w-auto">انصراف</a>
                <button wire:click="save" wire:loading.attr="disabled" class="btn btn-primary w-full md:w-auto">
                    <span wire:loading.remove wire:target="save">✅ ذخیره</span>
                    <span wire:loading wire:target="save">⏳...</span>
                </button>
            </div>
        </div>
    </div>
</div>
""")

# =========================================================
# ۴. Customers/Index (make sure root exists)
# =========================================================

write_file("resources/views/livewire/customers/index.blade.php", r"""
<div class="p-4 md:p-6 space-y-4">

    <div class="flex flex-wrap items-center justify-between gap-3">
        <h1 class="text-xl md:text-2xl font-bold">👥 مشتریان</h1>
        <a href="{{ route('customers.create') }}" class="btn btn-primary btn-sm">➕ مشتری جدید</a>
    </div>

    <div class="bg-base-100 rounded-lg shadow border p-3">
        <input type="text" wire:model.live.debounce.400ms="search"
               placeholder="🔍 جستجو نام یا تلفن..." class="input input-bordered input-sm w-full md:w-80" />
    </div>

    <div class="bg-base-100 rounded-lg shadow border overflow-hidden">
        <div class="pro-table-wrap">
            <table class="pro-table">
                <thead>
                    <tr>
                        <th style="width:50px;">#</th>
                        <th>نام</th>
                        <th>تلفن</th>
                        <th>کدپستی</th>
                        <th>سفارش</th>
                        <th>آدرس</th>
                        <th>عملیات</th>
                    </tr>
                </thead>
                <tbody>
                    @forelse($customers as $c)
                        <tr>
                            <td>{{ $c->id }}</td>
                            <td class="font-bold">
                                <a href="{{ route('customers.show', $c) }}" class="link link-primary">
                                    {{ $c->name ?? '—' }}
                                </a>
                            </td>
                            <td class="font-mono text-xs" dir="ltr">{{ $c->phone }}</td>
                            <td class="font-mono text-xs" dir="ltr">{{ $c->postal_code ?? '—' }}</td>
                            <td><span class="badge badge-primary badge-sm">{{ $c->orders_count }}</span></td>
                            <td class="text-xs">{{ \Illuminate\Support\Str::limit($c->address, 40) }}</td>
                            <td>
                                <div class="flex gap-1">
                                    <a href="{{ route('customers.show', $c) }}" class="btn btn-ghost btn-xs">👁️</a>
                                    <a href="{{ route('customers.edit', $c) }}" class="btn btn-ghost btn-xs">✏️</a>
                                </div>
                            </td>
                        </tr>
                    @empty
                        <tr><td colspan="7" class="text-center py-8 text-base-content/50">مشتری‌ای نیست</td></tr>
                    @endforelse
                </tbody>
            </table>
        </div>
    </div>

    <div>{{ $customers->links() }}</div>
</div>
""")

# =========================================================
# ۵. Certificates/Index
# =========================================================

write_file("resources/views/livewire/certificates/index.blade.php", r"""
<div class="p-4 md:p-6 space-y-4">

    @if (session('success'))
        <div class="alert alert-success text-sm py-2"><span>{{ session('success') }}</span></div>
    @endif

    <div class="flex flex-wrap items-center justify-between gap-3">
        <h1 class="text-xl md:text-2xl font-bold">💎 شناسنامه‌ها</h1>
        <a href="{{ route('certificates.create') }}" class="btn btn-primary btn-sm">➕ شناسنامه جدید</a>
    </div>

    <div class="bg-base-100 rounded-lg shadow border p-3">
        <input type="text" wire:model.live.debounce.400ms="search"
               placeholder="🔍 کد، SKU، سنگ..." class="input input-bordered input-sm w-full md:w-80" />
    </div>

    <div class="bg-base-100 rounded-lg shadow border overflow-hidden">
        <div class="pro-table-wrap">
            <table class="pro-table">
                <thead>
                    <tr>
                        <th>کد</th>
                        <th>SKU</th>
                        <th>سنگ</th>
                        <th>فلز</th>
                        <th>ابعاد</th>
                        <th>وزن</th>
                        <th>مشتری</th>
                        <th>تاریخ</th>
                        <th>عملیات</th>
                    </tr>
                </thead>
                <tbody>
                    @forelse($certificates as $c)
                        <tr>
                            <td class="font-mono font-bold">
                                <a href="{{ route('certificates.show', $c) }}" class="link link-primary">{{ $c->code }}</a>
                            </td>
                            <td class="font-mono text-xs" dir="ltr">{{ $c->sku ?? '—' }}</td>
                            <td><span class="badge badge-outline badge-sm">{{ $c->stone_name }}</span></td>
                            <td class="text-xs">{{ $c->metal_en ?? $c->metal }}</td>
                            <td class="text-xs">{{ $c->length }}×{{ $c->width }}</td>
                            <td class="text-xs">{{ $c->weight }}</td>
                            <td class="text-xs">{{ $c->customer?->name ?? '—' }}</td>
                            <td class="text-xs">{{ $c->issued_at?->format('Y/m/d') }}</td>
                            <td>
                                <div class="flex gap-1">
                                    <a href="{{ route('certificates.show', $c) }}" class="btn btn-ghost btn-xs">👁️</a>
                                    <button wire:click="delete({{ $c->id }})" wire:confirm="حذف شود؟" class="btn btn-ghost btn-xs text-error">🗑️</button>
                                </div>
                            </td>
                        </tr>
                    @empty
                        <tr><td colspan="9" class="text-center py-8 text-base-content/50">شناسنامه‌ای نیست</td></tr>
                    @endforelse
                </tbody>
            </table>
        </div>
    </div>

    <div>{{ $certificates->links() }}</div>
</div>
""")

# =========================================================
# ۶. Reports/Index
# =========================================================

write_file("resources/views/livewire/reports/index.blade.php", r"""
<div class="p-4 md:p-6 space-y-4">

    <div class="flex flex-wrap items-center justify-between gap-3">
        <h1 class="text-xl md:text-2xl font-bold">📊 گزارش‌ها</h1>
        <div class="flex gap-1 bg-base-100 rounded-lg p-1 shadow border">
            <button wire:click="$set('range', 'today')" class="btn btn-xs {{ $range === 'today' ? 'btn-primary' : 'btn-ghost' }}">امروز</button>
            <button wire:click="$set('range', '7days')" class="btn btn-xs {{ $range === '7days' ? 'btn-primary' : 'btn-ghost' }}">۷ روز</button>
            <button wire:click="$set('range', '30days')" class="btn btn-xs {{ $range === '30days' ? 'btn-primary' : 'btn-ghost' }}">۳۰ روز</button>
            <button wire:click="$set('range', 'year')" class="btn btn-xs {{ $range === 'year' ? 'btn-primary' : 'btn-ghost' }}">امسال</button>
        </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div class="card bg-base-100 shadow border">
            <div class="card-body p-4">
                <div class="text-xs text-base-content/60">📦 تعداد سفارشات</div>
                <div class="text-2xl font-extrabold mt-1">{{ number_format($totalCount) }}</div>
            </div>
        </div>
        <div class="card bg-base-100 shadow border">
            <div class="card-body p-4">
                <div class="text-xs text-base-content/60">💰 مجموع فروش</div>
                <div class="text-2xl font-extrabold mt-1" dir="ltr">{{ number_format($totalAmount) }}</div>
            </div>
        </div>
        <div class="card bg-base-100 shadow border">
            <div class="card-body p-4">
                <div class="text-xs text-base-content/60">📊 میانگین هر سفارش</div>
                <div class="text-2xl font-extrabold mt-1" dir="ltr">{{ number_format($avgAmount) }}</div>
            </div>
        </div>
    </div>

    <div class="card bg-base-100 shadow border">
        <div class="card-body">
            <h2 class="font-bold text-base mb-4">📈 روند سفارشات</h2>
            <div style="height: 300px;"><canvas id="dailyChart"></canvas></div>
        </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="card bg-base-100 shadow border">
            <div class="card-body">
                <h2 class="font-bold text-base mb-4">📊 تفکیک وضعیت</h2>
                <div style="height: 250px;"><canvas id="statusChart"></canvas></div>
            </div>
        </div>
        <div class="card bg-base-100 shadow border">
            <div class="card-body">
                <h2 class="font-bold text-base mb-4">🌐 توزیع کانال‌ها</h2>
                <div style="height: 250px;"><canvas id="channelChart"></canvas></div>
            </div>
        </div>
    </div>

    <div class="card bg-base-100 shadow border">
        <div class="card-body">
            <h2 class="font-bold text-base mb-4">🏆 مشتریان برتر</h2>
            @forelse($topCustomers as $i => $c)
                <div class="flex items-center gap-3 py-2 border-b border-base-200 last:border-0">
                    <div class="w-8 h-8 rounded-full bg-primary text-primary-content flex items-center justify-center font-bold text-sm">{{ $i + 1 }}</div>
                    <div class="flex-1">
                        <a href="{{ route('customers.show', $c) }}" class="link link-hover font-bold text-sm">{{ $c->name ?? 'بدون نام' }}</a>
                        <div class="text-xs text-base-content/60 font-mono" dir="ltr">{{ $c->phone }}</div>
                    </div>
                    <div class="badge badge-primary">{{ $c->orders_count }} سفارش</div>
                </div>
            @empty
                <p class="text-sm text-base-content/50">داده‌ای نیست.</p>
            @endforelse
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script>
document.addEventListener('livewire:init', () => {
    let dailyChart, statusChart, channelChart;
    function initCharts() {
        if (dailyChart) dailyChart.destroy();
        if (statusChart) statusChart.destroy();
        if (channelChart) channelChart.destroy();
        Chart.defaults.font.family = 'Vazirmatn, Tahoma, sans-serif';
        Chart.defaults.font.size = 11;

        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        const gridColor = isDark ? 'rgba(125, 211, 208, 0.1)' : 'rgba(148, 163, 184, 0.2)';
        const textColor = isDark ? '#7dd3d0' : '#475569';

        const dc = document.getElementById('dailyChart');
        if (dc) dailyChart = new Chart(dc, {
            type: 'line',
            data: {
                labels: @json($dailyLabels),
                datasets: [
                    { label: 'تعداد', data: @json($dailyCounts), borderColor: '#14b8a6', backgroundColor: 'rgba(20,184,166,.1)', tension: .3, fill: true, yAxisID: 'y' },
                    { label: 'مبلغ', data: @json($dailyAmounts), borderColor: '#0ea5e9', backgroundColor: 'rgba(14,165,233,.1)', tension: .3, fill: true, yAxisID: 'y1', hidden: true }
                ]
            },
            options: { responsive: true, maintainAspectRatio: false,
                plugins: { legend: { labels: { color: textColor } } },
                scales: {
                    y: { position: 'right', ticks: { color: textColor }, grid: { color: gridColor } },
                    y1: { position: 'left', grid: { drawOnChartArea: false }, ticks: { color: textColor } },
                    x: { ticks: { color: textColor }, grid: { color: gridColor } }
                }
            }
        });

        const sc = document.getElementById('statusChart');
        if (sc) statusChart = new Chart(sc, {
            type: 'doughnut',
            data: {
                labels: ['📝 ثبت سفارش', '🔍 چک نهایی', '🚚 تحویل مامور'],
                datasets: [{ data: @json($byStatus), backgroundColor: ['#f59e0b', '#0ea5e9', '#10b981'], borderWidth: 2, borderColor: isDark ? '#0a1414' : '#fff' }]
            },
            options: { responsive: true, maintainAspectRatio: false,
                plugins: { legend: { position: 'bottom', labels: { color: textColor } } }
            }
        });

        const cc = document.getElementById('channelChart');
        if (cc) channelChart = new Chart(cc, {
            type: 'bar',
            data: {
                labels: @json($channelLabels),
                datasets: [{ label: 'تعداد', data: @json($channelCounts), backgroundColor: @json($channelColors), borderWidth: 1 }]
            },
            options: { responsive: true, maintainAspectRatio: false, indexAxis: 'y',
                plugins: { legend: { display: false } },
                scales: {
                    x: { ticks: { color: textColor }, grid: { color: gridColor } },
                    y: { ticks: { color: textColor }, grid: { color: gridColor } }
                }
            }
        });
    }
    initCharts();
    Livewire.hook('morph.updated', () => setTimeout(initCharts, 100));
});
</script>
""")

# =========================================================
# ۷. Reports/Livewire
# =========================================================

write_file("app/Livewire/Reports/Index.php", r"""
<?php

namespace App\Livewire\Reports;

use App\Models\Channel;
use App\Models\Customer;
use App\Models\Order;
use Livewire\Component;

class Index extends Component
{
    public string $range = '7days';

    public function render()
    {
        $start = match ($this->range) {
            'today'  => now()->startOfDay(),
            '7days'  => now()->subDays(7)->startOfDay(),
            '30days' => now()->subDays(30)->startOfDay(),
            'year'   => now()->startOfYear(),
            default  => now()->subDays(7)->startOfDay(),
        };

        $orders = Order::where('created_at', '>=', $start)->get();
        $totalCount  = $orders->count();
        $totalAmount = (float) $orders->sum('amount');
        $avgAmount   = $totalCount > 0 ? $totalAmount / $totalCount : 0;

        $days = match ($this->range) {
            'today' => 1, '7days' => 7, '30days' => 30, 'year' => 12, default => 7,
        };

        $dailyLabels = []; $dailyCounts = []; $dailyAmounts = [];

        if ($this->range === 'year') {
            for ($i = 11; $i >= 0; $i--) {
                $ms = now()->subMonths($i)->startOfMonth();
                $me = now()->subMonths($i)->endOfMonth();
                $dailyLabels[]  = $ms->format('Y/m');
                $dailyCounts[]  = Order::whereBetween('created_at', [$ms, $me])->count();
                $dailyAmounts[] = (float) Order::whereBetween('created_at', [$ms, $me])->sum('amount');
            }
        } else {
            for ($i = $days - 1; $i >= 0; $i--) {
                $date = now()->subDays($i);
                $ds = $date->copy()->startOfDay();
                $de = $date->copy()->endOfDay();
                $dailyLabels[]  = $date->format('m/d');
                $dailyCounts[]  = Order::whereBetween('created_at', [$ds, $de])->count();
                $dailyAmounts[] = (float) Order::whereBetween('created_at', [$ds, $de])->sum('amount');
            }
        }

        $byStatus = [
            Order::where('status', 'pending')->where('created_at', '>=', $start)->count(),
            Order::where('status', 'final-check')->where('created_at', '>=', $start)->count(),
            Order::where('status', 'courier')->where('created_at', '>=', $start)->count(),
        ];

        $channels = Channel::withCount(['orders' => fn ($q) => $q->where('created_at', '>=', $start)])
            ->orderByDesc('orders_count')->get();

        $channelLabels = $channels->pluck('name')->toArray();
        $channelCounts = $channels->pluck('orders_count')->toArray();
        $channelColors = $channels->pluck('color')->toArray();

        $topCustomers = Customer::has('orders')->withCount('orders')->orderByDesc('orders_count')->limit(5)->get();

        return view('livewire.reports.index', compact(
            'totalCount', 'totalAmount', 'avgAmount',
            'dailyLabels', 'dailyCounts', 'dailyAmounts',
            'byStatus', 'channelLabels', 'channelCounts', 'channelColors', 'topCustomers'
        ))->layout('components.layouts.app');
    }
}
""")

# =========================================================
# ۸. Activity Log
# =========================================================

write_file("resources/views/livewire/activity-log.blade.php", r"""
<div class="p-4 md:p-6 space-y-4">
    <div class="flex flex-wrap items-center justify-between gap-3">
        <h1 class="text-xl md:text-2xl font-bold">📜 لاگ فعالیت‌ها</h1>
        <div class="flex flex-wrap gap-2">
            <input type="text" wire:model.live.debounce.400ms="search" placeholder="🔍 جستجو..."
                   class="input input-bordered input-sm w-52" />
            <select wire:model.live="logNameFilter" class="select select-bordered select-sm">
                <option value="">همه لاگ‌ها</option>
                @foreach($logNames as $name)
                    <option value="{{ $name }}">{{ $name }}</option>
                @endforeach
            </select>
        </div>
    </div>

    <div class="bg-base-100 rounded-lg shadow border overflow-hidden">
        <div class="pro-table-wrap">
            <table class="pro-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>تاریخ</th>
                        <th>کاربر</th>
                        <th>لاگ</th>
                        <th>رویداد</th>
                        <th>توضیح</th>
                    </tr>
                </thead>
                <tbody>
                    @forelse($activities as $a)
                        <tr>
                            <td class="text-xs">{{ $a->id }}</td>
                            <td class="text-xs whitespace-nowrap">{{ $a->created_at?->format('Y/m/d H:i:s') }}</td>
                            <td class="text-xs">{{ $a->causer?->name ?? 'سیستم' }}</td>
                            <td><span class="badge badge-outline badge-sm">{{ $a->log_name }}</span></td>
                            <td><span class="badge badge-primary badge-sm">{{ $a->event }}</span></td>
                            <td class="text-xs">{{ $a->description }}</td>
                        </tr>
                    @empty
                        <tr><td colspan="6" class="text-center py-8 text-base-content/50">لاگی نیست</td></tr>
                    @endforelse
                </tbody>
            </table>
        </div>
    </div>

    <div>{{ $activities->links() }}</div>
</div>
""")

print()
print("═" * 60)
print("✅ همه ویوهای Customers, Certificates, Reports, ActivityLog بازنویسی شدن")
print("═" * 60)
print()
print("📌 اجرا کن:")
print("   php artisan optimize:clear")
print("   php artisan serve --host=0.0.0.0 --port=8000")
print()
