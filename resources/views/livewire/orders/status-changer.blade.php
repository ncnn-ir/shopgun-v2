@teleport('body')
<div>
@if($open && $order)
<div class="sg-modal-backdrop" data-layer="status" wire:click.self="close">
    <div class="sg-modal sg-modal-md" @click.stop>
        <div class="sg-modal-header">
            <div>
                <div class="sg-modal-title">🔄 تغییر وضعیت سفارش #{{ $order->order_number }}</div>
                <div class="sg-modal-subtitle">رویداد با تاریخ و ساعت دقیق ثبت می‌شود</div>
            </div>
            <button class="sg-modal-close" wire:click="close">✕</button>
        </div>
        <div class="sg-modal-body">
            <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:8px">
                @foreach($catalog as $key => $meta)
                    <button type="button" wire:click="$set('event_key','{{ $key }}')"
                        style="padding:10px;border-radius:10px;border:2px solid {{ $event_key === $key ? $meta[2] : '#e2e8f0' }};
                               background:{{ $event_key === $key ? $meta[2].'15' : '#fff' }};
                               color:{{ $event_key === $key ? $meta[2] : '#475569' }};
                               cursor:pointer;font-family:inherit;font-size:11.5px;font-weight:600;
                               display:flex;align-items:center;gap:6px;text-align:right">
                        <span style="font-size:16px">{{ $meta[1] }}</span>
                        <span>{{ $meta[0] }}</span>
                    </button>
                @endforeach
            </div>

            <textarea wire:model="notes" rows="3" class="sg-textarea"
                style="margin-top:14px" placeholder="یادداشت اختیاری..."></textarea>

            @error('event_key')<div style="color:#dc2626;font-size:11px;margin-top:6px">{{ $message }}</div>@enderror

            <div style="display:flex;gap:8px;justify-content:flex-end;margin-top:14px;padding-top:14px;border-top:1px solid #f1f5f9">
                <button wire:click="close" class="sg-btn sg-btn-gray">انصراف</button>
                <button wire:click="save" class="sg-btn sg-btn-green" @if(!$event_key) disabled @endif>✅ ثبت</button>
            </div>
        </div>
    </div>
</div>
@endif
</div>
@endteleport
