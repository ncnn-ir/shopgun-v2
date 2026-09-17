<div>
    @if($show && $certificate)
    <div class="fixed inset-0 z-[85] flex items-start justify-center p-4 overflow-y-auto"
         @keydown.escape.window="$wire.close()">

        <div class="fixed inset-0 bg-black/70 backdrop-blur-md" wire:click="close"></div>

        <div class="relative bg-base-100 rounded-2xl shadow-2xl w-full max-w-3xl my-8 md:my-16 border border-base-300">

            <div class="flex items-center justify-between p-4 border-b border-base-300 bg-gradient-to-l from-cyan-500/10 to-transparent rounded-t-2xl">
                <div class="flex items-center gap-3">
                    <div class="w-9 h-9 rounded-lg flex items-center justify-center text-white shadow" style="background: linear-gradient(135deg, #14b8a6, #0891b2);">💎</div>
                    <div>
                        <h2 class="font-bold text-base">شناسنامه #{{ $certificate->code }}</h2>
                        <div class="text-xs text-base-content/60 font-mono" dir="ltr">{{ $certificate->serial }}</div>
                    </div>
                </div>
                <button wire:click="close" class="btn btn-ghost btn-sm btn-circle">✕</button>
            </div>

            <div class="p-5 space-y-4 max-h-[calc(100vh-14rem)] overflow-y-auto">

                {{-- ★ کارت مستقیم --}}
                <div class="flex justify-center bg-base-200/50 rounded-lg p-4">
                    <div id="viewModalScaleWrap" style="transform-origin: top center;">
                        <div class="cert-modal-display">
                            {!! $cardHtml !!}
                        </div>
                    </div>
                </div>

                <div class="grid grid-cols-2 md:grid-cols-3 gap-2 text-sm">
                    <div class="p-3 rounded-lg bg-base-200/50">
                        <div class="text-[10px] text-base-content/60">💎 سنگ</div>
                        <div class="font-bold mt-0.5">{{ $certificate->stone_name }}</div>
                    </div>
                    <div class="p-3 rounded-lg bg-base-200/50">
                        <div class="text-[10px] text-base-content/60">⚙️ فلز</div>
                        <div class="mt-0.5">{{ $certificate->metal }} ({{ $certificate->metal_carat }})</div>
                    </div>
                    <div class="p-3 rounded-lg bg-base-200/50">
                        <div class="text-[10px] text-base-content/60">📐 ابعاد</div>
                        <div class="mt-0.5">{{ $certificate->dimension }} mm</div>
                    </div>
                    <div class="p-3 rounded-lg bg-base-200/50">
                        <div class="text-[10px] text-base-content/60">⚖️ وزن</div>
                        <div class="mt-0.5">{{ $certificate->weight_clean }} gr</div>
                    </div>
                    <div class="p-3 rounded-lg bg-base-200/50">
                        <div class="text-[10px] text-base-content/60">👤 مشتری</div>
                        <div class="mt-0.5">{{ $certificate->customer?->name ?? '—' }}</div>
                    </div>
                    <div class="p-3 rounded-lg bg-base-200/50">
                        <div class="text-[10px] text-base-content/60">📅 صدور</div>
                        <div class="mt-0.5 text-xs">{{ \App\Support\PersianDate::format($certificate->issued_at ?? now(), 'Y/m/d') }}</div>
                    </div>
                </div>
            </div>

            <div class="p-4 border-t border-base-300 flex flex-wrap justify-end gap-2 rounded-b-2xl bg-base-200/50">
                <button wire:click="close" class="btn btn-ghost btn-sm">بستن</button>
                <button onclick="printCertModal()" class="btn btn-info btn-sm">🖨️ چاپ</button>
                <button onclick="exportCertModalPng()" class="btn btn-success btn-sm">📸 PNG</button>
                <a href="{{ route('certificates.show', $certificate) }}" class="btn btn-outline btn-sm">صفحه کامل</a>
            </div>
        </div>
    </div>
    @endif
</div>

@if($show && $certificate)
<script type="text/template" id="cert-modal-batch-template">{!! $batchHtml !!}</script>
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script>
(function () {
    function scaleCard() {
        var wrap = document.querySelector('.cert-modal-display .certificate');
        if (!wrap) return;
        var box = wrap.parentNode.parentNode;
        var maxW = box.clientWidth - 32;
        var w = wrap.offsetWidth || 245;
        var s = Math.min(1, maxW / w);
        var target = document.getElementById('viewModalScaleWrap');
        if (!target) return;
        target.style.transform = 'scale(' + s + ')';
        target.style.height = (wrap.offsetHeight * s) + 'px';
    }
    setTimeout(scaleCard, 200);
    window.addEventListener('resize', scaleCard);

    window.printCertModal = function () {
        var tmpl = document.getElementById('cert-modal-batch-template');
        if (!tmpl) { alert('کارت پیدا نشد'); return; }
        var iframe = document.createElement('iframe');
        iframe.style.cssText = 'position:fixed;left:-99999px;top:0;width:0;height:0;border:0;';
        document.body.appendChild(iframe);
        var doc = iframe.contentDocument || iframe.contentWindow.document;
        doc.open(); doc.write(tmpl.innerHTML); doc.close();
        setTimeout(function () {
            try { iframe.contentWindow.focus(); iframe.contentWindow.print(); } catch (e) {}
            setTimeout(function () { if (iframe.parentNode) document.body.removeChild(iframe); }, 3000);
        }, 800);
    };

    window.exportCertModalPng = function () {
        var el = document.querySelector('.cert-modal-display .certificate');
        if (!el) { alert('کارت پیدا نشد'); return; }
        if (typeof html2canvas !== 'function') { alert('html2canvas آماده نیست'); return; }

        var clone = el.cloneNode(true);
        var pxW = el.offsetWidth, pxH = el.offsetHeight;
        clone.style.width = pxW + 'px';
        clone.style.height = pxH + 'px';
        clone.style.boxShadow = 'none';

        var hidden = document.createElement('div');
        hidden.style.cssText = 'position:fixed;left:-99999px;top:0;background:#fffef9;width:' + pxW + 'px;height:' + pxH + 'px;';
        hidden.appendChild(clone);
        document.body.appendChild(hidden);

        setTimeout(function () {
            html2canvas(clone, {
                scale: 3, backgroundColor: '#fffef9',
                useCORS: true, allowTaint: false, logging: false,
                width: pxW, height: pxH, windowWidth: pxW, windowHeight: pxH
            }).then(function (canvas) {
                if (hidden.parentNode) document.body.removeChild(hidden);
                var a = document.createElement('a');
                a.download = 'certificate-{{ $certificate->code ?? "cert" }}.png';
                a.href = canvas.toDataURL('image/png');
                a.click();
            }).catch(function (e) {
                if (hidden.parentNode) document.body.removeChild(hidden);
                alert('خطا در ساخت PNG');
            });
        }, 300);
    };
})();
</script>
@endif
