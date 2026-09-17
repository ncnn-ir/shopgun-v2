<div>
    <iframe style="position:fixed;inset:0;width:100%;height:100%;border:0;z-index:9999;"
        srcdoc="
        <!DOCTYPE html><html lang='fa' dir='rtl'><head><meta charset='UTF-8'><title>لیست مامور</title>
        <style>
            @page{size:A4;margin:8mm}
            *{box-sizing:border-box;margin:0;padding:0;font-family:Tahoma,sans-serif}
            body{padding:12px}
            .no-print{padding:12px;text-align:center;margin-bottom:12px}
            .no-print button{padding:8px 16px;background:#1a5276;color:#fff;border:none;border-radius:6px;cursor:pointer;margin:0 4px;font-family:inherit}
            h1{text-align:center;color:#1a5276;font-size:16px;margin-bottom:6px}
            .subtitle{text-align:center;color:#666;font-size:11px;margin-bottom:10px;border-bottom:2px solid #1a5276;padding-bottom:8px}
            table{width:100%;border-collapse:collapse}
            thead th{background:#1a5276;color:#fff;padding:7px 5px;font-size:10.5px;border:1px solid #0d3b5e}
            tbody td{padding:6px 5px;border:1px solid #999;font-size:10.5px;text-align:right}
            tbody tr:nth-child(even){background:#f9f9f9}
            .center{text-align:center!important}.mono{font-family:monospace;direction:ltr}
            .sign{margin-top:40px;display:flex;justify-content:space-around;font-size:11px}
            .sign div{border-top:1px solid #333;padding-top:4px;min-width:150px;text-align:center}
            @media print{.no-print{display:none!important}}
        </style></head><body>
        <div class='no-print'><button onclick='window.print()'>🖨️ چاپ</button><button onclick='history.back()' style='background:#eee;color:#333'>✕ بستن</button></div>
        <h1>📦 لیست سفارشات تحویل به مامور</h1>
        <div class='subtitle'>ShopGun — {{ now()->format('Y/m/d H:i') }} — تعداد: {{ count($orders) }}</div>
        @if(empty($orders))<p style='text-align:center;padding:40px;color:#999'>سفارشی نیست</p>
        @else
        <table><thead><tr><th>ردیف</th><th>شماره</th><th>نام</th><th>تلفن</th><th>کدپستی</th><th>آدرس</th><th>بیمه</th></tr></thead>
        <tbody>
        @foreach($orders as $i => $o)
        <tr><td class='center'>{{ $i+1 }}</td><td class='center mono'>{{ $o->order_number }}</td><td>{{ $o->customer?->name }}</td><td class='center mono'>{{ $o->phone }}</td><td class='center mono'>{{ $o->postal_code }}</td><td style='font-size:10px'>{{ \Illuminate\Support\Str::limit($o->address, 80) }}</td><td class='center'>{{ number_format((float) $o->insurance) }}</td></tr>
        @endforeach
        </tbody></table>
        <div class='sign'><div>امضاء تحویل‌دهنده</div><div>امضاء مامور</div></div>
        @endif
        </body></html>
        ">
    </iframe>
</div>
