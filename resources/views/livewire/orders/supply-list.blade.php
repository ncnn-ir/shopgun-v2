<div style="direction:rtl" wire:poll.30s>

    {{-- Header --}}
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:14px">
        <div>
            <h1 style="margin:0;font-size:20px;font-weight:700;color:var(--sg-text)">📋 لیست تأمین — محصولات فروش رفته</h1>
            <p style="margin:4px 0 0;font-size:11.5px;color:var(--sg-text-muted)">
                {{ \App\Support\PersianNumber::toFa($totalSkus) }} محصول فروش رفته از سفارشات
            </p>
        </div>
        <a href="{{ route('orders.index') }}" wire:navigate class="sg-btn sg-btn-ghost">
            ← سفارشات
        </a>
    </div>

    {{-- Filters --}}
    <div class="sg-card" style="margin-bottom:12px">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
            <div class="sg-field" style="margin:0">
                <label>🔍 جستجو</label>
                <input type="text" wire:model.live.debounce.400ms="search" placeholder="SKU یا نام...">
            </div>
            <div class="sg-field" style="margin:0">
                <label>مرتب‌سازی</label>
                <select wire:model.live="sortBy">
                    <option value="sold_count">بیشترین فروش</option>
                    <option value="total_revenue">بیشترین درآمد</option>
                    <option value="last_sold_at">جدیدترین فروش</option>
                    <option value="sku">کد SKU</option>
                </select>
            </div>
        </div>
    </div>

    {{-- List --}}
    @if($items->isEmpty())
        <div class="sg-card" style="text-align:center;padding:40px">
            <div style="font-size:44px;opacity:.4">📋</div>
            <div style="font-size:13px;color:var(--sg-text-muted);margin-top:8px">محصولی فروش نرفته یا SKU ثبت نشده</div>
        </div>
    @else
        <div style="display:grid;grid-template-columns:1fr;gap:8px">
            @foreach($items as $item)
                <div wire:key="supply-{{ md5($item->sku) }}"
                     wire:click="showProduct('{{ addslashes($item->sku) }}')"
                     class="sg-card"
                     style="cursor:pointer;padding:10px 12px;transition:var(--sg-t-fast)"
                     onmouseover="this.style.boxShadow='var(--sg-shadow)';this.style.transform='translateY(-1px)'"
                     onmouseout="this.style.boxShadow='';this.style.transform=''">

                    <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap">
                        {{-- SKU --}}
                        <span style="font-family:var(--sg-font-mono);font-weight:700;color:var(--sg-primary);font-size:12.5px;min-width:60px">
                            {{ $item->sku }}
                        </span>

                        {{-- Title --}}
                        <span style="flex:1;min-width:120px;font-weight:700;font-size:12.5px;color:var(--sg-text)" class="sg-truncate">
                            {{ $item->title }}
                        </span>

                        {{-- Sold count --}}
                        <span style="display:inline-flex;align-items:center;gap:4px;padding:3px 10px;border-radius:99px;background:rgba(16,185,129,.12);color:#059669;font-size:11px;font-weight:700">
                            🛒 {{ \App\Support\PersianNumber::toFa($item->sold_count) }} عدد
                        </span>

                        {{-- Orders count --}}
                        <span style="display:inline-flex;align-items:center;gap:4px;padding:3px 10px;border-radius:99px;background:rgba(59,130,246,.12);color:#1e40af;font-size:11px;font-weight:700">
                            📦 {{ \App\Support\PersianNumber::toFa($item->orders_count) }} سفارش
                        </span>

                        {{-- Revenue --}}
                        <span style="font-family:var(--sg-font-mono);font-weight:700;color:var(--sg-success);font-size:12px">
                            {{ number_format((float) $item->total_revenue) }}
                        </span>

                        {{-- Last date --}}
                        <span style="font-family:var(--sg-font-mono);font-size:10.5px;color:var(--sg-text-muted)">
                            {{ $item->last_sold_at ? \App\Support\PersianDate::format($item->last_sold_at, 'Y/m/d') : '—' }}
                        </span>

                        {{-- Arrow --}}
                        <span style="color:var(--sg-accent);font-size:16px">👁️</span>
                    </div>
                </div>
            @endforeach
        </div>

        <div style="padding:14px 0">{{ $items->links() }}</div>
    @endif

    {{-- ═══ Product Popup ═══ --}}
    @if($showProductPopup && $productPopup)
        <div style="position:fixed;inset:0;background:rgba(15,23,42,.75);backdrop-filter:blur(6px);z-index:9999;display:flex;align-items:center;justify-content:center;padding:12px"
             wire:click.self="closeProductPopup" @keydown.escape.window="$wire.closeProductPopup()">

            <div style="background:var(--sg-bg-card);border-radius:16px;max-width:420px;width:100%;overflow:hidden;box-shadow:var(--sg-shadow-xl)"
                 wire:click.stop>

                {{-- Header --}}
                <div style="padding:12px 16px;background:linear-gradient(135deg,var(--sg-primary),var(--sg-primary-hover));color:#fff;display:flex;justify-content:space-between;align-items:center">
                    <span style="font-weight:700;font-size:14px">🛍️ اطلاعات محصول</span>
                    <button wire:click="closeProductPopup" style="width:28px;height:28px;border-radius:50%;background:rgba(255,255,255,.2);border:none;color:#fff;cursor:pointer;font-size:13px">✕</button>
                </div>

                {{-- Image --}}
                <div style="aspect-ratio:1.2;background:#f8fafc;display:flex;align-items:center;justify-content:center;overflow:hidden">
                    @if(!empty($productPopup['image']))
                        <img src="{{ $productPopup['image'] }}" alt=""
                             style="width:100%;height:100%;object-fit:cover"
                             onerror="this.replaceWith(document.createTextNode('💎'))" crossorigin="anonymous">
                    @else
                        <div style="font-size:56px;color:#cbd5e1">💎</div>
                    @endif
                </div>

                {{-- Info --}}
                <div style="padding:14px">
                    <div style="font-weight:700;font-size:14px;color:var(--sg-text);margin-bottom:8px">
                        {{ $productPopup['title'] ?? '—' }}
                    </div>

                    <div style="font-family:var(--sg-font-mono);font-size:11.5px;color:var(--sg-text-muted);margin-bottom:10px" dir="ltr">
                        SKU: {{ $productPopup['sku'] ?? '—' }}
                    </div>

                    {{-- Grid --}}
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px">
                        <div style="padding:8px;background:var(--sg-bg-soft);border-radius:8px">
                            <div style="font-size:10px;color:var(--sg-text-muted);margin-bottom:2px">💰 قیمت</div>
                            <div style="font-family:var(--sg-font-mono);font-weight:700;color:var(--sg-success);font-size:12.5px">
                                {{ number_format((float) ($productPopup['price'] ?? 0)) }}
                            </div>
                        </div>
                        <div style="padding:8px;background:var(--sg-bg-soft);border-radius:8px">
                            <div style="font-size:10px;color:var(--sg-text-muted);margin-bottom:2px">⚖️ وزن</div>
                            <div style="font-family:var(--sg-font-mono);font-weight:700;font-size:12.5px">
                                {{ $productPopup['weight'] ?: '—' }} {{ $productPopup['weight'] ? 'گرم' : '' }}
                            </div>
                        </div>
                        <div style="padding:8px;background:var(--sg-bg-soft);border-radius:8px">
                            <div style="font-size:10px;color:var(--sg-text-muted);margin-bottom:2px">📐 ابعاد</div>
                            <div style="font-family:var(--sg-font-mono);font-weight:700;font-size:11.5px">
                                @if(!empty($productPopup['dimensions']))
                                    {{ $productPopup['dimensions']['length'] ?: '—' }} × {{ $productPopup['dimensions']['width'] ?: '—' }}
                                    @if(!empty($productPopup['dimensions']['height']))
                                        × {{ $productPopup['dimensions']['height'] }}
                                    @endif
                                @else — @endif
                            </div>
                        </div>
                        <div style="padding:8px;background:var(--sg-bg-soft);border-radius:8px">
                            <div style="font-size:10px;color:var(--sg-text-muted);margin-bottom:2px">📦 موجودی</div>
                            <div style="font-family:var(--sg-font-mono);font-weight:700;font-size:12.5px;
                                @if($productPopup['stock_status'] === 'instock') color:#10b981
                                @elseif($productPopup['stock_status'] === 'outofstock') color:#ef4444
                                @else color:var(--sg-text) @endif">
                                @if($productPopup['stock'] !== null)
                                    {{ \App\Support\PersianNumber::toFa($productPopup['stock']) }}
                                    {{ $productPopup['stock_status'] === 'instock' ? '✓' : ($productPopup['stock_status'] === 'outofstock' ? '✗' : '') }}
                                @else — @endif
                            </div>
                        </div>
                    </div>

                    {{-- Actions --}}
                    @if($productPopup['edit_url'] || $productPopup['view_url'])
                        <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:10px">
                            @if($productPopup['view_url'])
                                <a href="{{ $productPopup['view_url'] }}" target="_blank" class="sg-btn sg-btn-primary sg-btn-sm" style="flex:1">
                                    🌐 نمایش در سایت
                                </a>
                            @endif
                            @if($productPopup['edit_url'])
                                <a href="{{ $productPopup['edit_url'] }}" target="_blank" class="sg-btn sg-btn-ghost sg-btn-sm" style="flex:1">
                                    ✏️ ویرایش
                                </a>
                            @endif
                        </div>
                    @endif
                </div>
            </div>
        </div>
    @endif
</div>
