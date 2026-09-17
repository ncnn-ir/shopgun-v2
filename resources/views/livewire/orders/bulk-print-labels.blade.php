<div>
    <iframe style="position:fixed;inset:0;width:100%;height:100%;border:0;z-index:9999;"
        srcdoc="
        <!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><title>چاپ برچسب‌ها</title>
        <style>
            @page{size:A4;margin:5mm}
            *{box-sizing:border-box;margin:0;padding:0;font-family:Tahoma,sans-serif}
            body{background:#f0f0f0;padding:10px}
            .no-print{padding:12px;text-align:center;background:#fff;margin-bottom:12px;border-radius:8px}
            .no-print button{padding:8px 16px;background:#1a5276;color:#fff;border:none;border-radius:6px;cursor:pointer;margin:0 4px;font-family:inherit}
            .labels-container{display:grid;grid-template-columns:repeat(2,100mm);gap:5mm;justify-content:center}
            .label{width:100mm;height:65mm;background:#fff;border:2px solid #000;padding:3mm;display:flex;flex-direction:column;page-break-inside:avoid;overflow:hidden}
            .label-header{display:flex;justify-content:space-between;align-items:center;border-bottom:2px solid #000;padding-bottom:2mm;margin-bottom:2mm}
            .customer-name{font-size:18px;font-weight:bold;flex:1;overflow:hidden}
            .insurance-tag{background:#000;color:#fff;padding:2px 10px;border-radius:20px;font-size:13px;font-weight:bold}
            .addr-box{border:2px solid #000;border-radius:6px;padding:2mm;font-size:14px;line-height:1.5;font-weight:600;flex:1;overflow:hidden;margin-bottom:2mm}
            .contact-row{display:flex;gap:3mm;margin-bottom:2mm}
            .contact-tag{flex:1;display:flex;align-items:center;gap:4px}
            .contact-tag .lbl{background:#000;color:#fff;padding:2px 8px;border-radius:5px;font-size:11px;font-weight:bold}
            .contact-tag .val{flex:1;border:2px solid #000;border-radius:5px;padding:2px 8px;font-size:15px;font-weight:bold;font-family:monospace;text-align:center}
            .meta-row{display:flex;gap:5px;justify-content:space-between;font-size:11px}
            .meta-row span{background:#000;color:#fff;padding:2px 10px;border-radius:10px;font-weight:bold}
            @media print{body{background:#fff;padding:0}.no-print{display:none!important}}
        </style></head><body>
        <div class='no-print'><button onclick='window.print()'>🖨️ چاپ {{ count($orders) }} برچسب</button><button onclick='history.back()' style='background:#eee;color:#333'>✕ بستن</button></div>
        @if(empty($orders))<div style='text-align:center;padding:40px;color:#999'>سفارشی انتخاب نشده</div>
        @else
        <div class='labels-container'>
            @foreach($orders as $order)
            <div class='label'>
                <div class='label-header'>
                    <div class='customer-name'>{{ $order->customer?->name ?? 'مشتری' }}</div>
                    @if($order->insurance > 0)<div class='insurance-tag'>بیمه: {{ number_format((float) $order->insurance) }}</div>@endif
                </div>
                <div class='addr-box'>{{ $order->address ?? '—' }}</div>
                <div class='contact-row'>
                    <div class='contact-tag'><span class='lbl'>تلفن</span><span class='val'>{{ $order->phone ?? '—' }}</span></div>
                    <div class='contact-tag'><span class='lbl'>کدپستی</span><span class='val'>{{ $order->postal_code ?? '—' }}</span></div>
                </div>
                <div class='meta-row'><span>#{{ $order->order_number }}</span><span>{{ $order->created_at?->format('Y/m/d') }}</span></div>
            </div>
            @endforeach
        </div>
        @endif
        </body></html>
        ">
    </iframe>
</div>
