<div class="p-3 bg-base-200/50 rounded-lg" dir="rtl">
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
        <div>
            <div class="text-base-content/60">آدرس:</div>
            <div class="font-bold">{{ $row->address ?? '—' }}</div>
        </div>
        <div>
            <div class="text-base-content/60">کدپستی:</div>
            <div class="font-mono font-bold">{{ $row->postal_code ?? '—' }}</div>
        </div>
        <div>
            <div class="text-base-content/60">کانال:</div>
            <div class="font-bold">{{ $row->channel?->name ?? '—' }}</div>
        </div>
        <div>
            <div class="text-base-content/60">یادداشت:</div>
            <div>{{ $row->notes ?? '—' }}</div>
        </div>
    </div>
</div>
