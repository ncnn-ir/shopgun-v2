<div>
@if($open && $order)
<div class="sg-modal-backdrop"
     wire:click.self="close"
     @keydown.escape.window="$wire.close()"
     style="position:fixed;inset:0;z-index:99995;background:rgba(15,23,42,.7);backdrop-filter:blur(6px);display:flex;align-items:flex-start;justify-content:center;padding:20px;overflow-y:auto">

  <div @click.stop style="background:#fff;border-radius:18px;max-width:700px;width:100%;margin:auto;box-shadow:0 30px 60px -12px rgba(0,0,0,.5);direction:rtl;overflow:hidden;animation:sgSlideUp .25s ease-out">

    {{-- ═══ HEADER با گرادیانت ═══ --}}
    <div style="background:linear-gradient(135deg,#1a5276 0%,#0d3b5e 100%);color:#fff;padding:18px 22px;position:relative;overflow:hidden">
      <div style="position:absolute;top:-20px;left:-20px;width:120px;height:120px;background:rgba(201,168,76,.15);border-radius:50%;pointer-events:none"></div>
      <div style="position:absolute;bottom:-40px;right:-30px;width:150px;height:150px;background:rgba(201,168,76,.08);border-radius:50%;pointer-events:none"></div>

      <div style="position:relative;display:flex;justify-content:space-between;align-items:flex-start;gap:12px">
        <div style="flex:1;min-width:0">
          <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;margin-bottom:6px">
            <h2 style="margin:0;font-size:17px;font-weight:800">
              📋 سفارش #{{ $order['number'] }}
            </h2>
            <span style="display:inline-flex;align-items:center;gap:4px;padding:3px 10px;border-radius:999px;font-size:11px;font-weight:700;background:{{ $order['status_bg'] }};color:{{ $order['status_color'] }}">
              {{ $order['status_icon'] }} {{ $order['status_label'] }}
            </span>
          </div>
          <div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;font-size:11.5px;opacity:.85">
            <span>📅 {{ \App\Support\PersianDate::format($order['created'], 'Y/m/d H:i') }}</span>
            @if($order['channel'])
              <x-channel-badge :channel="$order['channel']" />
            @endif
          </div>
        </div>
        <button type="button" wire:click="close"
          style="width:36px;height:36px;border-radius:10px;background:rgba(255,255,255,.15);color:#fff;border:none;cursor:pointer;font-size:16px;display:flex;align-items:center;justify-content:center;transition:all .15s;flex-shrink:0"
          onmouseover="this.style.background='rgba(255,255,255,.25)'"
          onmouseout="this.style.background='rgba(255,255,255,.15)'">
          ✕
        </button>
      </div>
    </div>

    {{-- ═══ BODY ═══ --}}
    <div style="padding:20px 22px;max-height:calc(100vh - 200px);overflow-y:auto">

      {{-- ═══════ TIMELINE افقی ═══════ --}}
      @if(count($order['timeline']) > 0)
        <div style="margin-bottom:22px">
          <div style="font-size:12px;font-weight:700;color:#64748b;margin-bottom:14px">📊 مراحل سفارش</div>
          <div style="position:relative;padding:0 8px">
            {{-- خط پس زمینه --}}
            <div style="position:absolute;top:18px;left:30px;right:30px;height:2px;background:#e2e8f0;z-index:0"></div>

            <div style="display:flex;justify-content:space-between;position:relative;z-index:1">
              @foreach($order['timeline'] as $step)
                <div style="flex:1;text-align:center;min-width:60px">
                  <div style="width:36px;height:36px;border-radius:50%;margin:0 auto 6px;display:flex;align-items:center;justify-content:center;font-size:14px;background:#10b981;color:#fff;box-shadow:0 0 0 4px rgba(16,185,129,.15);font-weight:700">
                    ✓
                  </div>
                  <div style="font-size:10.5px;font-weight:700;color:#059669;line-height:1.3;margin-bottom:2px">
                    {{ $step['label'] }}
                  </div>
                  @if($step['date'])
                    <div style="font-family:monospace;font-size:9px;color:#94a3b8">
                      {{ \App\Support\PersianDate::format($step['date'], 'm/d') }}<br>
                      {{ \App\Support\PersianDate::format($step['date'], 'H:i') }}
                    </div>
                  @endif
                </div>
              @endforeach
            </div>
          </div>
        </div>
      @endif

      {{-- ═══════ مبلغ و اطلاعات کلی ═══════ --}}
      <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:10px;margin-bottom:18px">
        <div style="background:linear-gradient(135deg,#d1fae5,#a7f3d0);border:1px solid #6ee7b7;border-radius:12px;padding:12px">
          <div style="font-size:10.5px;color:#065f46;font-weight:700;margin-bottom:4px">💰 مبلغ کل</div>
          <div style="font-size:16px;font-weight:800;color:#065f46;font-family:monospace">
            {{ \App\Support\PersianNumber::toFa(number_format($order['amount'])) }}
            <span style="font-size:11px;font-weight:500;opacity:.7">تومان</span>
          </div>
        </div>
        @if($order['insurance'] > 0)
          <div style="background:linear-gradient(135deg,#fef3c7,#fde68a);border:1px solid #fcd34d;border-radius:12px;padding:12px">
            <div style="font-size:10.5px;color:#92400e;font-weight:700;margin-bottom:4px">🛡️ بیمه</div>
            <div style="font-size:16px;font-weight:800;color:#92400e;font-family:monospace">
              {{ \App\Support\PersianNumber::toFa(number_format($order['insurance'])) }}
            </div>
          </div>
        @else
          <div style="background:linear-gradient(135deg,#eef2ff,#e0e7ff);border:1px solid #a5b4fc;border-radius:12px;padding:12px">
            <div style="font-size:10.5px;color:#3730a3;font-weight:700;margin-bottom:4px">📦 تعداد اقلام</div>
            <div style="font-size:16px;font-weight:800;color:#3730a3;font-family:monospace">
              {{ \App\Support\PersianNumber::toFa(count($order['items'])) }}
            </div>
          </div>
        @endif
      </div>

      {{-- ═══════ اطلاعات مشتری ═══════ --}}
      <div style="background:#f8fafc;border-radius:14px;padding:14px;margin-bottom:16px">
        <div style="font-size:12px;font-weight:700;color:#475569;margin-bottom:12px;display:flex;align-items:center;gap:6px">
          👤 اطلاعات مشتری
        </div>

        <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:12px;font-size:12.5px">
          <div>
            <div style="font-size:10.5px;color:#94a3b8;margin-bottom:3px">نام</div>
            <div style="font-weight:700;color:#1e293b">{{ $order['customer']['name'] }}</div>
          </div>
          @if($order['customer']['phone'])
            <div>
              <div style="font-size:10.5px;color:#94a3b8;margin-bottom:3px">موبایل</div>
              <div style="font-family:monospace;font-weight:700;color:#1e293b" dir="ltr">
                {{ $order['customer']['phone'] }}
              </div>
            </div>
          @endif
          @if($order['customer']['email'])
            <div style="grid-column:1/-1">
              <div style="font-size:10.5px;color:#94a3b8;margin-bottom:3px">ایمیل</div>
              <div style="font-family:monospace;color:#1e293b;font-size:11.5px" dir="ltr">
                {{ $order['customer']['email'] }}
              </div>
            </div>
          @endif
        </div>
      </div>

      {{-- ═══════ آدرس ═══════ --}}
      @if($order['address'] || $order['postal'])
        <div style="background:#f8fafc;border-radius:14px;padding:14px;margin-bottom:16px">
          <div style="font-size:12px;font-weight:700;color:#475569;margin-bottom:10px;display:flex;align-items:center;gap:6px">
            📍 آدرس ارسال
          </div>
          @if($order['address'])
            <div style="font-size:12.5px;color:#1e293b;line-height:1.8;margin-bottom:8px">
              {{ $order['address'] }}
            </div>
          @endif
          @if($order['postal'])
            <div style="display:inline-flex;align-items:center;gap:6px;font-family:monospace;font-size:11.5px;background:#fff;border:1px solid #e2e8f0;padding:4px 10px;border-radius:8px;color:#475569">
              📮 کدپستی: {{ $order['postal'] }}
            </div>
          @endif
        </div>
      @endif

      {{-- ═══════ پیگیری پستی ═══════ --}}
      @if($order['tracking'] || $order['carrier'])
        <div style="background:linear-gradient(135deg,#eff6ff,#dbeafe);border:1px solid #93c5fd;border-radius:14px;padding:14px;margin-bottom:16px">
          <div style="font-size:12px;font-weight:700;color:#1e40af;margin-bottom:8px">🚚 اطلاعات ارسال</div>
          <div style="display:flex;flex-wrap:wrap;gap:14px;font-size:12px;color:#1e40af">
            @if($order['carrier'])
              <span><b>پست:</b> {{ $order['carrier'] }}</span>
            @endif
            @if($order['tracking'])
              <span style="font-family:monospace"><b>کد رهگیری:</b> {{ $order['tracking'] }}</span>
            @endif
          </div>
        </div>
      @endif

      {{-- ═══════ اقلام ═══════ --}}
      <div style="margin-bottom:16px">
        <div style="font-size:12px;font-weight:700;color:#475569;margin-bottom:10px;display:flex;align-items:center;justify-content:space-between">
          <span>📦 اقلام سفارش</span>
          <span style="font-size:10.5px;color:#94a3b8;font-weight:500">{{ \App\Support\PersianNumber::toFa(count($order['items'])) }} قلم</span>
        </div>

        @forelse($order['items'] as $idx => $item)
          <div style="display:flex;align-items:center;gap:10px;padding:10px;background:#fff;border:1px solid #e2e8f0;border-radius:12px;margin-bottom:8px">
            <div style="width:44px;height:44px;border-radius:10px;background:linear-gradient(135deg,#f1f5f9,#e2e8f0);display:flex;align-items:center;justify-content:center;font-size:20px;flex-shrink:0">
              💎
            </div>
            <div style="flex:1;min-width:0">
              <div style="font-weight:700;font-size:12.5px;color:#1e293b;margin-bottom:3px;overflow:hidden;text-overflow:ellipsis">
                {{ $item['title'] }}
              </div>
              <div style="display:flex;flex-wrap:wrap;gap:10px;font-size:10.5px;color:#64748b">
                @if($item['sku'])
                  <span style="font-family:monospace">SKU: {{ $item['sku'] }}</span>
                @endif
                <span>تعداد: {{ \App\Support\PersianNumber::toFa($item['qty']) }}</span>
                <span style="font-family:monospace">{{ \App\Support\PersianNumber::toFa(number_format($item['price'])) }} ×</span>
              </div>
            </div>
            <div style="font-family:monospace;font-weight:800;color:#059669;font-size:13px;white-space:nowrap">
              {{ \App\Support\PersianNumber::toFa(number_format($item['line'])) }}
            </div>
          </div>
        @empty
          <div style="text-align:center;padding:24px;color:#94a3b8;font-size:12px;background:#f8fafc;border-radius:12px">
            هیچ قلمی ثبت نشده
          </div>
        @endforelse
      </div>

      {{-- ═══════ یادداشت‌ها ═══════ --}}
      @if($order['customer_note'] || $order['note'])
        <div style="background:linear-gradient(135deg,#fef3c7,#fde68a);border:1px solid #fcd34d;border-radius:14px;padding:14px;margin-bottom:16px">
          <div style="font-size:12px;font-weight:700;color:#92400e;margin-bottom:8px">📝 یادداشت‌ها</div>
          @if($order['customer_note'])
            <div style="font-size:12px;color:#78350f;margin-bottom:6px;line-height:1.7">
              <b>یادداشت مشتری:</b> {{ $order['customer_note'] }}
            </div>
          @endif
          @if($order['note'])
            <div style="font-size:12px;color:#78350f;line-height:1.7">
              <b>یادداشت داخلی:</b> {{ $order['note'] }}
            </div>
          @endif
        </div>
      @endif

    </div>

    {{-- ═══ FOOTER با دکمه‌ها ═══ --}}
    <div style="padding:14px 22px;background:#f8fafc;border-top:1px solid #e2e8f0;display:flex;flex-wrap:wrap;gap:8px;align-items:center">

      {{-- تغییر وضعیت --}}
      <div style="display:flex;gap:4px;flex-wrap:wrap">
        <button type="button" wire:click="changeStatus('pending')"
          class="sg-btn" style="padding:7px 12px;border-radius:9px;font-size:11px;font-weight:700;cursor:pointer;border:none;font-family:inherit;background:{{ $order['status']==='pending' ? '#f59e0b' : '#fef3c7' }};color:{{ $order['status']==='pending' ? '#fff' : '#92400e' }}">
          📝 ثبت
        </button>
        <button type="button" wire:click="changeStatus('final-check')"
          class="sg-btn" style="padding:7px 12px;border-radius:9px;font-size:11px;font-weight:700;cursor:pointer;border:none;font-family:inherit;background:{{ $order['status']==='final-check' ? '#3b82f6' : '#dbeafe' }};color:{{ $order['status']==='final-check' ? '#fff' : '#1e40af' }}">
          🔍 چک
        </button>
        <button type="button" wire:click="changeStatus('courier')"
          class="sg-btn" style="padding:7px 12px;border-radius:9px;font-size:11px;font-weight:700;cursor:pointer;border:none;font-family:inherit;background:{{ $order['status']==='courier' ? '#10b981' : '#d1fae5' }};color:{{ $order['status']==='courier' ? '#fff' : '#065f46' }}">
          🚚 مامور
        </button>
        <button type="button" wire:click="changeStatus('completed')"
          class="sg-btn" style="padding:7px 12px;border-radius:9px;font-size:11px;font-weight:700;cursor:pointer;border:none;font-family:inherit;background:{{ $order['status']==='completed' ? '#059669' : '#d1fae5' }};color:{{ $order['status']==='completed' ? '#fff' : '#065f46' }}">
          ✅ تکمیل
        </button>
      </div>

      <div style="flex:1"></div>

      <button type="button" wire:click="close"
        style="padding:8px 18px;border-radius:10px;font-size:12.5px;font-weight:700;cursor:pointer;border:1.5px solid #cbd5e1;background:#fff;color:#475569;font-family:inherit">
        بستن
      </button>
    </div>

  </div>
</div>
@endif

@once
<style>
@keyframes sgSlideUp {
  from { opacity: 0; transform: translateY(20px) scale(.98); }
  to   { opacity: 1; transform: translateY(0) scale(1); }
}
</style>
@endonce

</div>
