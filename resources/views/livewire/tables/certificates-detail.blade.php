<div class="p-3 bg-base-200/50 rounded-lg" dir="rtl">
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
        <div>
            <div class="text-base-content/60">سریال:</div>
            <div class="font-mono font-bold" dir="ltr">{{ $row->serial ?? '—' }}</div>
        </div>
        <div>
            <div class="text-base-content/60">اصالت:</div>
            <div>{{ $row->stone_origin ?? '—' }} ({{ $row->stone_flag ?? '—' }})</div>
        </div>
        <div>
            <div class="text-base-content/60">عیار:</div>
            <div class="font-mono">{{ $row->metal_carat ?? '—' }}</div>
        </div>
        <div>
            <div class="text-base-content/60">مشتری:</div>
            <div>{{ $row->customer?->name ?? '—' }}</div>
        </div>
        <div>
            <div class="text-base-content/60">تصویر محصول:</div>
            <div>
                @if($row->image_path)
                    <a href="{{ asset('storage/' . $row->image_path) }}" target="_blank" class="link link-primary text-xs">مشاهده</a>
                @else
                    —
                @endif
            </div>
        </div>
        <div>
            <div class="text-base-content/60">لینک عمومی:</div>
            <div>
                <a href="{{ $row->public_url }}" target="_blank" class="link link-primary text-xs">{{ $row->code }}</a>
            </div>
        </div>
    </div>
</div>
