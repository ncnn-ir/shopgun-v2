<div>
@if($show && $certificate)
<div style="position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:96;display:flex;align-items:flex-start;justify-content:center;padding:10px;overflow-y:auto"
     @keydown.escape.window="$wire.close()">

    <div style="background:#fff;width:100%;max-width:820px;margin:10px auto;border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,.4);overflow:hidden;direction:rtl;font-family:Vazirmatn,Tahoma,sans-serif">

        <div style="background:linear-gradient(135deg,#1a5276,#0d3b5e);color:#fff;padding:14px 18px;display:flex;align-items:center;justify-content:space-between">
            <div>
                <h2 style="margin:0;font-size:16px;font-weight:700">شناسنامه #{{ $certificate->code }}</h2>
                <div style="font-size:11px;opacity:.8;font-family:monospace;margin-top:2px" dir="ltr">{{ $certificate->serial }}</div>
            </div>
            <button type="button" wire:click="close" style="width:32px;height:32px;border-radius:50%;background:rgba(255,255,255,.2);color:#fff;border:none;cursor:pointer;font-size:15px">X</button>
        </div>

        <div style="padding:16px;max-height:calc(100vh - 180px);overflow-y:auto">

            <div id="cert-card-area" style="background:repeating-conic-gradient(#f0f0f0 0% 25%, #fff 0% 50%) 50% / 20px 20px;border-radius:12px;padding:16px;display:flex;justify-content:center;overflow:auto;margin-bottom:16px">
                <div style="transform-origin:top center;max-width:100%">
                    {!! $cardHtml !!}
                </div>
            </div>

            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px">
                <div style="padding:10px;background:#f8fafc;border-radius:8px">
                    <div style="font-size:10px;color:#94a3b8">💎 سنگ</div>
                    <div style="font-size:13px;font-weight:700">{{ $certificate->stone_name }}</div>
                </div>
                <div style="padding:10px;background:#f8fafc;border-radius:8px">
                    <div style="font-size:10px;color:#94a3b8">⚙️ فلز</div>
                    <div style="font-size:13px">{{ $certificate->metal }} ({{ $certificate->metal_carat }})</div>
                </div>
                <div style="padding:10px;background:#f8fafc;border-radius:8px">
                    <div style="font-size:10px;color:#94a3b8">📐 ابعاد</div>
                    <div style="font-size:13px">{{ $certificate->length }}×{{ $certificate->width }} mm</div>
                </div>
                <div style="padding:10px;background:#f8fafc;border-radius:8px">
                    <div style="font-size:10px;color:#94a3b8">⚖️ وزن</div>
                    <div style="font-size:13px">{{ $certificate->weight }} gr</div>
                </div>
            </div>
        </div>

        <div style="padding:12px 18px;background:#f8fafc;border-top:1px solid #e2e8f0;display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap">
            <button type="button" wire:click="delete" wire:confirm="حذف شود؟"
                    style="padding:9px 16px;background:#fee2e2;color:#dc2626;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">
                🗑️ حذف
            </button>

            <div style="display:flex;gap:6px;flex-wrap:wrap">
                <button type="button" onclick="downloadCertModal()"
                        style="padding:9px 16px;background:#0891b2;color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">
                    📥 دانلود PNG
                </button>
                <button type="button" onclick="window.open('{{ route('certificates.print', ['ids' => $certificate->id, 'auto' => 1]) }}', '_blank')"
                        style="padding:9px 16px;background:#1a5276;color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">
                    🖨️ چاپ
                </button>
                <button type="button" wire:click="edit"
                        style="padding:9px 16px;background:#16a34a;color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">
                    ✏️ ویرایش
                </button>
            </div>
        </div>
    </div>
</div>
@endif
</div>

<script>
window.downloadCertModal = function() {
    var certId = {{ $certificate->id ?? 0 }};
    if (!certId) { alert('شناسنامه پیدا نشد'); return; }
    // ★ باز کردن صفحه رندر در تب جدید
    var w = window.open('/certificates/' + certId + '/render?download=1', '_blank', 'width=900,height=900');
    if (!w) { alert('پاپ‌آپ بلاک شده — لطفا اجازه بده'); }
};
</script>
