<div>
    <iframe style="position:fixed;inset:0;width:100%;height:100%;border:0;z-index:9999;"
        srcdoc="
        <!DOCTYPE html>
        <html lang='fa' dir='rtl'>
        <head>
            <meta charset='UTF-8'>
            <title>چاپ شناسنامه‌ها</title>
            <style>
                @page { size: A4; margin: 8mm; }
                * { box-sizing: border-box; margin: 0; padding: 0; }
                body { font-family: Tahoma, sans-serif; background: #fff; }
                .no-print { padding: 12px; text-align: center; background: #f0f0f0; margin-bottom: 8px; }
                .no-print button { padding: 8px 16px; cursor: pointer; font-family: inherit; margin: 0 4px; border: none; border-radius: 6px; background: #14b8a6; color: #fff; }
                .grid { display: grid; grid-template-columns: repeat(3, 65mm); gap: 3mm; justify-content: center; }
                .cert { width: 65mm; height: 65mm; border: 1px solid #b8860b; background: #fffef9; padding: 3mm; display: flex; flex-direction: column; overflow: hidden; page-break-inside: avoid; position: relative; }
                .cert-title { text-align: center; font-family: serif; font-size: 11px; font-weight: bold; color: #6b4423; margin-bottom: 1.5mm; border-bottom: 1px solid #b8860b; padding-bottom: 1mm; }
                .cert-img { width: 22mm; height: 22mm; object-fit: contain; float: left; margin: 0 0 1mm 1mm; border: 1px solid #b8860b; background: #fff; }
                .cert-row { font-size: 7.5px; line-height: 1.5; color: #2c3e50; }
                .cert-row b { color: #0369a1; }
                .cert-qr { position: absolute; bottom: 2mm; left: 2mm; width: 14mm; height: 14mm; }
                .cert-code { position: absolute; bottom: 2mm; right: 2mm; font-family: monospace; font-size: 7px; font-weight: bold; color: #8b6914; }
                .cert-serial { position: absolute; top: 1mm; left: 2mm; font-family: monospace; font-size: 5.5px; color: #999; direction: ltr; }
                @media print { .no-print { display: none !important; } }
            </style>
        </head>
        <body>
            <div class='no-print'>
                <button onclick='window.print()'>🖨️ چاپ A4</button>
                <span style='margin: 0 12px; font-size: 12px;'>{{ count($certificates) }} شناسنامه</span>
                <button onclick='history.back()' style='background:#eee;color:#333;'>✕ بستن</button>
            </div>
            @if(empty($certificates))
                <div style='text-align: center; padding: 40px; color: #999;'>شناسنامه‌ای انتخاب نشده</div>
            @else
                <div class='grid'>
                    @foreach($certificates as $cert)
                        <div class='cert'>
                            <div class='cert-serial'>{{ $cert->serial }}</div>
                            <div class='cert-title'>Certificate of Authenticity</div>
                            @if($cert->image_path)
                                <img src='{{ asset('storage/' . $cert->image_path) }}' class='cert-img' alt=''>
                            @endif
                            <div class='cert-row'><b>Stone:</b> {{ $cert->stone_en ?: $cert->stone_name }}</div>
                            <div class='cert-row'><b>Metal:</b> {{ $cert->metal_en ?: $cert->metal }} ({{ $cert->metal_carat }})</div>
                            <div class='cert-row'><b>Origin:</b> {{ $cert->stone_origin }}</div>
                            <div class='cert-row'><b>Size:</b> {{ $cert->length }}×{{ $cert->width }} mm</div>
                            <div class='cert-row'><b>Weight:</b> {{ $cert->weight }} gr</div>
                            <div class='cert-row'><b>Brilliant:</b> {{ $cert->brilliant }}</div>
                            <img src='{{ $cert->qr_url }}' class='cert-qr' alt=''>
                            <div class='cert-code'>#{{ $cert->code }}</div>
                        </div>
                    @endforeach
                </div>
            @endif
        </body>
        </html>
        ">
    </iframe>
</div>
