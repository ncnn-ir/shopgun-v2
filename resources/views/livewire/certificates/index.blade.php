<div>
    <div class="sg-toolbar">
        <div class="sg-toolbar-right">
            <input type="text" wire:model.live.debounce.400ms="search" placeholder="🔍 کد/SKU/سنگ..." class="form-control" style="width:220px">
        </div>
        <div style="display:flex;gap:6px">
            <a href="{{ route('certificates.designer') }}" wire:navigate class="btn btn-secondary btn-sm">🎨 ویرایشگر</a>
            <a href="{{ route('certificates.create') }}" wire:navigate class="btn btn-primary">➕ شناسنامه جدید</a>
        </div>
    </div>

    <div class="sg-table-container">
        <div class="sg-table-header">
            <h2>💎 شناسنامه‌ها <span style="background:var(--gold);color:var(--primary);padding:2px 10px;border-radius:20px;font-size:10.5px;font-weight:700">{{ \App\Support\PersianNumber::toFa($certificates->total()) }}</span></h2>
        </div>
        <div class="sg-table-scroll">
            <table class="sg-table">
                <thead><tr><th>#</th><th>کد</th><th>تصویر</th><th>سنگ</th><th>فلز</th><th>ابعاد</th><th>وزن</th><th>تاریخ</th><th>عملیات</th></tr></thead>
                <tbody>
                    @forelse($certificates as $c)
                        <tr wire:key="cert-{{ $c->id }}">
                            <td><span class="sg-row-num">{{ \App\Support\PersianNumber::toFa($loop->iteration) }}</span></td>
                            <td><strong>{{ $c->code }}</strong>@if($c->sku)<div style="font-size:10px;opacity:.6;direction:ltr">{{ $c->sku }}</div>@endif</td>
                            <td>
                                @if($c->display_image)
                                    <img src="{{ $c->display_image }}" style="width:38px;height:38px;object-fit:cover;border-radius:8px;border:2px solid var(--border)">
                                @else
                                    <div style="width:38px;height:38px;background:#f5f5f5;border-radius:8px;display:flex;align-items:center;justify-content:center">💎</div>
                                @endif
                            </td>
                            <td><span style="background:var(--bg);padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600">{{ $c->stone_name }}</span></td>
                            <td>{{ $c->metal_en ?? $c->metal }}</td>
                            <td>{{ $c->length_clean }}×{{ $c->width_clean }}</td>
                            <td>{{ $c->weight_clean }}</td>
                            <td style="font-size:10.5px">{{ \App\Support\PersianDate::format($c->issued_at ?? $c->created_at, 'Y/m/d') }}</td>
                            <td>
                                <div class="sg-action-btns">
                                    <a href="{{ route('certificates.show', $c) }}" wire:navigate class="sg-action-btn view">👁️</a>
                                    <a href="{{ route('certificates.designer', $c) }}" wire:navigate class="sg-action-btn edit">🎨</a>
                                    <button wire:click="delete({{ $c->id }})" wire:confirm="حذف شود؟" class="sg-action-btn delete">🗑️</button>
                                </div>
                            </td>
                        </tr>
                    @empty
                        <tr><td colspan="9"><div style="text-align:center;padding:40px;color:var(--text-light)"><div style="font-size:44px;opacity:.5">💎</div><p>شناسنامه‌ای نیست</p></div></td></tr>
                    @endforelse
                </tbody>
            </table>
        </div>
        <div style="padding:14px">{{ $certificates->links() }}</div>
    </div>
</div>
