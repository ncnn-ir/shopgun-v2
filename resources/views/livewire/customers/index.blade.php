<div>
    <div class="sg-toolbar">
        <div class="sg-toolbar-right">
            <input type="text" wire:model.live.debounce.400ms="search" placeholder="🔍 جستجو..." class="form-control" style="width:220px">
            <select wire:model.live="filter" class="form-control" style="width:auto;display:inline-block">
                <option value="">همه</option>
                <option value="has_orders">با سفارش</option>
                <option value="no_orders">بدون سفارش</option>
            </select>
        </div>
        <a href="{{ route('customers.create') }}" wire:navigate class="btn btn-primary">➕ مشتری جدید</a>
    </div>

    <div class="sg-table-container">
        <div class="sg-table-header">
            <h2>👥 مشتریان <span style="background:var(--gold);color:var(--primary);padding:2px 10px;border-radius:20px;font-size:10.5px;font-weight:700">{{ \App\Support\PersianNumber::toFa($customers->total()) }}</span></h2>
        </div>
        <div class="sg-table-scroll">
            <table class="sg-table">
                <thead><tr><th>#</th><th>نام</th><th>تلفن</th><th>کدپستی</th><th>سفارشات</th><th>عملیات</th></tr></thead>
                <tbody>
                    @forelse($customers as $c)
                        <tr wire:key="c-{{ $c->id }}">
                            <td><span class="sg-row-num">{{ \App\Support\PersianNumber::toFa($loop->iteration) }}</span></td>
                            <td><strong>{{ $c->name ?? '—' }}</strong></td>
                            <td dir="ltr" style="font-family:monospace;font-size:11px">{{ $c->phone ?? '—' }}</td>
                            <td dir="ltr">{{ $c->postal_code ?? '—' }}</td>
                            <td>{{ \App\Support\PersianNumber::toFa($c->orders_count) }}</td>
                            <td>
                                <div class="sg-action-btns">
                                    <a href="{{ route('customers.show', $c) }}" wire:navigate class="sg-action-btn view">👁️</a>
                                    <a href="{{ route('customers.edit', $c) }}" wire:navigate class="sg-action-btn edit">✏️</a>
                                    <button wire:click="delete({{ $c->id }})" wire:confirm="حذف شود؟" class="sg-action-btn delete">🗑️</button>
                                </div>
                            </td>
                        </tr>
                    @empty
                        <tr><td colspan="6"><div style="text-align:center;padding:40px;color:var(--text-light)"><div style="font-size:44px;opacity:.5">👥</div><p>مشتری‌ای نیست</p></div></td></tr>
                    @endforelse
                </tbody>
            </table>
        </div>
        <div style="padding:14px">{{ $customers->links() }}</div>
    </div>
</div>
