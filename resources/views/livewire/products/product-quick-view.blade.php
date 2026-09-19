<div>
@if($open)
<div class="sg-modal-backdrop"
     wire:click.self="close"
     @keydown.escape.window="$wire.close()"
     style="position:fixed;inset:0;z-index:99999;background:rgba(15,23,42,.55);backdrop-filter:blur(4px);display:flex;align-items:center;justify-content:center;padding:16px">
  <div class="sg-modal" @click.stop style="background:#fff;border-radius:16px;max-width:680px;width:100%;max-height:90vh;overflow:hidden;display:flex;flex-direction:column;box-shadow:0 25px 50px -12px rgba(0,0,0,.4);direction:rtl">
    <div class="sg-modal-header" style="padding:14px 18px;border-bottom:1px solid #e2e8f0;display:flex;justify-content:space-between;align-items:center">
      <div>
        <div class="sg-modal-title" style="font-size:15px;font-weight:800">💎 {{ $p['name'] ?? 'محصول' }}</div>
        @if(!empty($p['sku']))<div style="font-size:11px;color:#94a3b8;margin-top:2px">SKU: {{ $p['sku'] }}</div>@endif
      </div>
      <button type="button" wire:click="close" style="width:34px;height:34px;border-radius:8px;border:none;background:transparent;cursor:pointer;font-size:18px;color:#64748b">✕</button>
    </div>
    <div class="sg-modal-body" style="padding:16px 18px;overflow-y:auto">
      @if($error)
        <div style="padding:30px;text-align:center">
          <div style="font-size:48px;opacity:.4;margin-bottom:8px">🔍</div>
          <div style="color:#dc2626;font-weight:600">{{ $error }}</div>
        </div>
      @elseif(empty($p))
        <div style="padding:30px;text-align:center;color:#94a3b8">⏳ در حال بارگذاری...</div>
      @else
        <div style="display:grid;grid-template-columns:200px 1fr;gap:18px">
          <div style="aspect-ratio:1;background:#f8fafc;border-radius:12px;border:1px solid #e2e8f0;display:flex;align-items:center;justify-content:center;overflow:hidden">
            @if(!empty($p['image']))
              <img src="{{ $p['image'] }}" alt="" style="width:100%;height:100%;object-fit:contain" onerror="this.parentNode.innerHTML='<span style=&quot;font-size:48px;opacity:.3&quot;>📦</span>'" />
            @else
              <span style="font-size:48px;opacity:.3">📦</span>
            @endif
          </div>
          <div>
            <div style="font-size:16px;font-weight:800;color:#1e293b;margin-bottom:12px">{{ $p['name'] }}</div>
            @if(!empty($p['sku']))
              <div style="display:flex;gap:10px;padding:6px 0;font-size:12.5px"><span style="color:#64748b;min-width:100px">🔖 کد:</span><span style="font-family:monospace;background:#f1f5f9;padding:2px 8px;border-radius:6px">{{ $p['sku'] }}</span></div>
            @endif
            @if(!empty($p['price']))
              <div style="display:flex;gap:10px;padding:6px 0;font-size:12.5px"><span style="color:#64748b;min-width:100px">💰 قیمت:</span><span style="color:#059669;font-weight:700;font-family:monospace">{{ \App\Support\PersianNumber::toFa(number_format((float)$p['price'])) }} تومان</span></div>
            @endif
            @if(!empty($p['updated']))
              <div style="display:flex;gap:10px;padding:6px 0;font-size:12.5px"><span style="color:#64748b;min-width:100px">🕐 بروزرسانی:</span><span>{{ $p['updated'] }}</span></div>
            @endif
            <div style="margin-top:14px;padding-top:12px;border-top:1px solid #f1f5f9">
              @if(!empty($p['url']))<a href="{{ $p['url'] }}" target="_blank" class="sg-btn sg-btn-indigo">🔗 مشاهده در سایت</a>@endif
            </div>
          </div>
        </div>
      @endif
    </div>
  </div>
</div>
@endif
</div>
