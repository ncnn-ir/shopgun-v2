<div class="p-4 md:p-6 max-w-5xl mx-auto">

    <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
        <div class="flex items-center gap-3">
            <a href="{{ route('certificates.index') }}" class="btn btn-ghost btn-sm">→</a>
            <div>
                <h1 class="text-xl md:text-2xl font-bold">شناسنامه #{{ $certificate->code }}</h1>
                <div class="text-xs text-base-content/60 mt-0.5 font-mono" dir="ltr">{{ $certificate->serial }}</div>
            </div>
        </div>
        <div class="flex flex-wrap gap-2">
            <a href="{{ $certificate->public_url }}" target="_blank" class="btn btn-outline btn-sm">🔗 لینک</a>
            <a href="{{ route('certificates.designer', $certificate->id) }}" class="btn btn-secondary btn-sm">🎨 ویرایشگر</a>
            <button onclick="window.open('{{ route("certificates.print", ["ids" => $certificate->id, "auto" => 1]) }}', '_blank')" class="btn btn-info btn-sm">🖨️ چاپ</button>
            <button onclick="exportCurrentCertPng()" class="btn btn-success btn-sm">📸 PNG</button>
            <button wire:click="delete" wire:confirm="حذف شود؟" class="btn btn-error btn-sm">🗑️</button>
        </div>
    </div>

    @if (session('success'))
        <div class="alert alert-success mb-4 text-sm"><span>{{ session('success') }}</span></div>
    @endif

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">

        {{-- ★ کارت مستقیم --}}
        <div class="lg:col-span-2 card bg-base-100 shadow border">
            <div class="card-body items-center">
                <h2 class="font-bold text-base mb-3 w-full">🎴 پیش‌نمایش کارت</h2>

                <div class="bg-base-200 rounded-lg p-4 flex justify-center overflow-auto w-full">
                    {{-- نمایش کارت با scale --}}
                    <div id="cert-scale-wrap" style="transform-origin: top center;">
                        <div class="cert-display-wrap">
                            {!! $cardHtml !!}
                        </div>
                    </div>
                </div>

                <div class="text-xs text-base-content/60 mt-2">
                    ابعاد: {{ $sizes['width'] }}×{{ $sizes['height'] }} سانتی‌متر
                </div>
            </div>
        </div>

        <div class="card bg-base-100 shadow border">
            <div class="card-body">
                <h2 class="font-bold text-base mb-3">📋 مشخصات</h2>
                <div class="space-y-2 text-sm">
                    <div class="flex justify-between p-2 rounded bg-base-200/50">
                        <span class="text-base-content/60">💎 سنگ:</span>
                        <span class="font-bold">{{ $certificate->stone_name }}</span>
                    </div>
                    <div class="flex justify-between p-2 rounded bg-base-200/50">
                        <span class="text-base-content/60">⚙️ فلز:</span>
                        <span>{{ $certificate->metal }} ({{ $certificate->metal_carat }})</span>
                    </div>
                    <div class="flex justify-between p-2 rounded bg-base-200/50">
                        <span class="text-base-content/60">📐 ابعاد:</span>
                        <span>{{ $certificate->dimension }} mm</span>
                    </div>
                    <div class="flex justify-between p-2 rounded bg-base-200/50">
                        <span class="text-base-content/60">⚖️ وزن:</span>
                        <span>{{ $certificate->weight_clean }} gr</span>
                    </div>
                    @if($certificate->customer)
                        <div class="flex justify-between p-2 rounded bg-base-200/50">
                            <span class="text-base-content/60">👤 مشتری:</span>
                            <a href="{{ route('customers.show', $certificate->customer) }}" class="link link-primary font-bold">
                                {{ $certificate->customer->name }}
                            </a>
                        </div>
                    @endif
                </div>
            </div>
        </div>
    </div>
</div>

{{-- ★ template برای چاپ --}}


<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script>
(function () {
    // ★ اسکیل کارت برای fit شدن در ظرف
    function scaleCard() {
        var wrap = document.querySelector('.cert-display-wrap .certificate');
        if (!wrap) return;
        var box = wrap.parentNode.parentNode;
        var maxW = box.clientWidth - 32;
        var w = wrap.offsetWidth || 245;
        var s = Math.min(1, maxW / w);
        document.getElementById('cert-scale-wrap').style.transform = 'scale(' + s + ')';
        // اصلاح ارتفاع ظرف
        document.getElementById('cert-scale-wrap').style.height = (wrap.offsetHeight * s) + 'px';
    }
    document.addEventListener('DOMContentLoaded', function () {
        setTimeout(scaleCard, 200);
        window.addEventListener('resize', scaleCard);
    });

    // ★ پیدا کردن عنصر کارت
    window.getCertShowEl = function () {
        return document.querySelector('.cert-display-wrap .certificate');
    };

    // ★ چاپ
    

    // ★ PNG
    window.exportCurrentCertPng = function () {
        var el = window.getCertShowEl();
        if (!el) { alert('کارت پیدا نشد'); return; }
        if (typeof html2canvas !== 'function') { alert('html2canvas آماده نیست'); return; }

        // clone برای capture
        var clone = el.cloneNode(true);
        var pxW = el.offsetWidth;
        var pxH = el.offsetHeight;
        clone.style.width = pxW + 'px';
        clone.style.height = pxH + 'px';
        clone.style.boxShadow = 'none';

        var hidden = document.createElement('div');
        hidden.style.cssText = 'position:fixed;left:-99999px;top:0;background:#fffef9;padding:0;width:' + pxW + 'px;height:' + pxH + 'px;';
        hidden.appendChild(clone);
        document.body.appendChild(hidden);

        // oklch fix
        var all = [clone].concat(Array.from(clone.querySelectorAll('*')));
        all.forEach(function (n) {
            var cs = window.getComputedStyle(n);
            ['color', 'backgroundColor', 'borderTopColor', 'borderRightColor', 'borderBottomColor', 'borderLeftColor'].forEach(function (prop) {
                var v = cs[prop];
                if (v && v.indexOf('oklch') !== -1) {
                    try { n.style[prop] = 'rgb(100,100,100)'; } catch (e) {}
                }
            });
        });

        setTimeout(function () {
            html2canvas(clone, {
                scale: 3, backgroundColor: '#fffef9',
                useCORS: true, allowTaint: false, logging: false,
                width: pxW, height: pxH, windowWidth: pxW, windowHeight: pxH
            }).then(function (canvas) {
                if (hidden.parentNode) document.body.removeChild(hidden);
                var a = document.createElement('a');
                a.download = 'certificate-{{ $certificate->code }}.png';
                a.href = canvas.toDataURL('image/png');
                a.click();
            }).catch(function (e) {
                if (hidden.parentNode) document.body.removeChild(hidden);
                console.error(e);
                alert('خطا در ساخت PNG');
            });
        }, 300);
    };
})();
</script>
