<div>
@if($open)
<div class="sg-modal-backdrop"
     wire:click.self="close"
     @keydown.escape.window="$wire.close()"
     style="position:fixed;inset:0;z-index:99990;background:rgba(15,23,42,.55);backdrop-filter:blur(4px);display:flex;align-items:center;justify-content:center;padding:16px;overflow-y:auto">
  <div @click.stop style="background:#fff;border-radius:16px;max-width:1100px;width:100%;max-height:92vh;overflow:hidden;display:flex;flex-direction:column;box-shadow:0 25px 50px -12px rgba(0,0,0,.4);direction:rtl">
    <div style="padding:14px 18px;border-bottom:1px solid #e2e8f0;display:flex;justify-content:space-between;align-items:center">
      <div>
        <div style="font-size:15px;font-weight:800">📦 لیست تامین</div>
        <div style="font-size:11px;color:#94a3b8;margin-top:2px">تیک = پیدا شد → بعد تحویل واحد ارسال</div>
      </div>
      <button type="button" wire:click="close" style="width:34px;height:34px;border-radius:8px;background:transparent;border:none;cursor:pointer;font-size:18px;color:#64748b">✕</button>
    </div>
    <div style="padding:16px 18px;overflow-y:auto;flex:1">

      <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-bottom:14px">
        <button type="button" wire:click="$set('filter','pending')" style="padding:12px;border-radius:12px;border:2px solid {{ $filter==='pending' ? '#d97706' : '#e2e8f0' }};background:{{ $filter==='pending' ? '#f59e0b' : '#fff' }};color:{{ $filter==='pending' ? '#fff' : '#475569' }};cursor:pointer;font-family:inherit">
          <div style="font-size:22px;font-weight:700">{{ \App\Support\PersianNumber::toFa($stats['pending']) }}</div>
          <div style="font-size:11px">⏳ در انتظار</div>
        </button>
        <button type="button" wire:click="$set('filter','found')" style="padding:12px;border-radius:12px;border:2px solid {{ $filter==='found' ? '#2563eb' : '#e2e8f0' }};background:{{ $filter==='found' ? '#3b82f6' : '#fff' }};color:{{ $filter==='found' ? '#fff' : '#475569' }};cursor:pointer;font-family:inherit">
          <div style="font-size:22px;font-weight:700">{{ \App\Support\PersianNumber::toFa($stats['found']) }}</div>
          <div style="font-size:11px">✅ پیدا شده</div>
        </button>
        <button type="button" wire:click="$set('filter','delivered')" style="padding:12px;border-radius:12px;border:2px solid {{ $filter==='delivered' ? '#059669' : '#e2e8f0' }};background:{{ $filter==='delivered' ? '#10b981' : '#fff' }};color:{{ $filter==='delivered' ? '#fff' : '#475569' }};cursor:pointer;font-family:inherit">
          <div style="font-size:22px;font-weight:700">{{ \App\Support\PersianNumber::toFa($stats['delivered']) }}</div>
          <div style="font-size:11px">🚚 تحویل ارسال</div>
        </button>
      </div>

      <div style="display:flex;gap:8px;margin-bottom:12px;flex-wrap:wrap">
        <input type="text" wire:model.live.debounce.400ms="search" placeholder="🔍 جستجو..." style="flex:1;min-width:180px;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:10px;font-size:12.5px;font-family:inherit" />
        <select wire:model.live="statusFilter" style="padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:10px;font-size:12.5px;font-family:inherit;min-width:160px">
          <option value="">همه وضعیت‌ها</option>
          @foreach($statusOptions as $k => $v)
            <option value="{{ $k }}">{{ $v }}</option>
          @endforeach
        </select>
      </div>

      @if(count($selected))
        <div style="padding:10px;background:#eef2ff;border:1px solid #a5b4fc;border-radius:10px;margin-bottom:12px;display:flex;gap:8px;align-items:center;font-size:12px">
          <strong>{{ count($selected) }} انتخاب</strong>
          <button wire:click="bulkMarkFound" class="sg-btn sg-btn-blue">✅ پیدا شد</button>
          <button wire:click="bulkDeliver" class="sg-btn sg-btn-green">🚚 تحویل ارسال</button>
        </div>
      @endif

      <div style="display:flex;flex-direction:column;gap:10px">
        @forelse($orders as $order)
          @php
            if ($order->isDeliveredToShipping()) $sb = ['#d1fae5','#065f46','🚚 تحویل ارسال'];
            elseif ($order->isSupplyFound()) $sb = ['#dbeafe','#1e40af','✅ پیدا شده'];
            else $sb = ['#fef3c7','#92400e','⏳ در انتظار'];
          @endphp
          <div style="border:1px solid #e2e8f0;border-radius:12px;padding:12px;background:#fff" wire:key="sc-{{ $order->id }}">
            <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;padding-bottom:8px;border-bottom:1px solid #f1f5f9;margin-bottom:8px">
              <div style="display:flex;align-items:center;gap:8px;flex-wrap:wrap">
                <input type="checkbox" wire:model.live="selected" value="{{ $order->id }}" style="width:18px;height:18px;accent-color:#c9a84c" />
                <span style="font-family:monospace;font-weight:700;color:#4f46e5;font-size:12.5px">#{{ $order->order_number }}</span>
                <x-channel-badge :channel="$order->sales_channel" />
                <span style="display:inline-block;padding:2px 8px;border-radius:999px;font-size:10.5px;font-weight:600;background:{{ $sb[0] }};color:{{ $sb[1] }}">{{ $sb[2] }}</span>
              </div>
              <div style="font-family:monospace;font-size:10.5px;color:#94a3b8">{{ \App\Support\PersianDate::format($order->created_at, 'Y/m/d H:i') }}</div>
            </div>

            <div style="display:flex;align-items:center;gap:6px;font-size:12px;color:#475569;margin-bottom:10px;flex-wrap:wrap">
              👤 <b>{{ trim(($order->customer->first_name ?? '') . ' ' . ($order->customer->last_name ?? '')) ?: '—' }}</b>
              @if($order->phone || $order->customer?->phone) <span dir="ltr" style="color:#94a3b8">| {{ $order->phone ?? $order->customer->phone }}</span> @endif
            </div>

            <div style="display:flex;flex-direction:column;gap:6px;margin-bottom:10px">
              @foreach(($order->items ?? collect()) as $item)
                @php
                  $prod = null;
                  if ($item->product_id) $prod = \App\Models\Product::find($item->product_id);
                  if (!$prod && !empty($item->sku)) $prod = \App\Models\Product::where('sku',$item->sku)->first();
                  $img = $item->image ?? null;
                  if (!$img) { try { $img = \App\Support\ProductImage::resolve($prod); } catch (\Throwable $e) {} }
                @endphp
                <div wire:click="$dispatch('openProductView', { productId: {{ $prod->id ?? 0 }}, sku: '{{ $item->sku ?? '' }}' })"
                     style="display:flex;align-items:center;gap:10px;padding:8px;background:#f8fafc;border-radius:10px;border:1px solid #f1f5f9;cursor:pointer">
                  <div style="width:52px;height:52px;border-radius:8px;background:#fff;border:1px solid #e2e8f0;display:flex;align-items:center;justify-content:center;overflow:hidden;flex-shrink:0">
                    @if($img)
                      <img src="{{ $img }}" alt="" loading="lazy" style="width:100%;height:100%;object-fit:cover" onerror="this.parentNode.innerHTML='<span style=&quot;font-size:22px&quot;>📦</span>'" />
                    @else
                      <span style="font-size:22px">📦</span>
                    @endif
                  </div>
                  <div style="flex:1;min-width:0">
                    <div style="font-weight:600;font-size:12.5px;color:#1e293b;margin-bottom:3px">
                      {{ $item->title ?? $item->name ?? $prod->name ?? '—' }}
                      @if($item->quantity > 1)<span style="background:#fef3c7;color:#92400e;padding:1px 6px;border-radius:5px;font-size:10px;margin-right:4px">×{{ $item->quantity }}</span>@endif
                    </div>
                    <div style="display:flex;gap:10px;font-size:11px;flex-wrap:wrap">
                      @if($item->sku || $prod?->sku)<span style="font-family:monospace;color:#94a3b8">SKU: {{ $item->sku ?? $prod->sku }}</span>@endif
                      @if($item->price)<span style="color:#059669;font-weight:700;font-family:monospace">💰 {{ \App\Support\PersianNumber::toFa(number_format($item->price)) }}</span>@endif
                    </div>
                  </div>
                  <span style="padding:6px 10px;border-radius:8px;background:#eef2ff;color:#4338ca;font-size:11px;font-weight:700">🔍</span>
                </div>
              @endforeach
            </div>

            <div style="display:flex;flex-wrap:wrap;gap:6px;padding-top:8px;border-top:1px solid #f1f5f9">
              <button type="button" wire:click="$dispatch('open-order-view', { orderId: {{ $order->id }} })" class="sg-btn sg-btn-indigo">👁 مشاهده سفارش</button>
              @if($order->isAwaitingSupply())
                <button wire:click="markFound({{ $order->id }})" class="sg-btn sg-btn-blue">✅ پیدا شد</button>
              @elseif($order->isSupplyFound())
                <button wire:click="deliverToShipping({{ $order->id }})" class="sg-btn sg-btn-green">🚚 تحویل ارسال</button>
                <button wire:click="unmarkFound({{ $order->id }})" class="sg-btn sg-btn-gray">↺</button>
              @else
                <span style="font-size:11.5px;color:#059669;font-weight:600;padding:5px 0">✓ تحویل شد</span>
              @endif
            </div>
          </div>
        @empty
          <div style="padding:40px;text-align:center;color:#94a3b8;font-size:13px">🎉 چیزی برای تامین نیست</div>
        @endforelse
      </div>

      @if($orders->hasPages())<div style="padding:10px;text-align:center">{{ $orders->links() }}</div>@endif
    </div>
  </div>
</div>
@endif
</div>
