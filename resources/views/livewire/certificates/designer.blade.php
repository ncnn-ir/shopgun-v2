<div class="p-4 md:p-6" dir="rtl" x-data="designerPage()" x-init="boot()">
    <div class="flex items-center justify-between mb-4 flex-wrap gap-2">
        <h1 class="text-2xl font-bold" style="color:#0d5c63;">
            🎨 ویرایشگر
            @if($isGlobal)
                <span class="text-sm font-normal text-amber-600">(طرح پیش‌فرض همه شناسنامه‌ها)</span>
            @elseif($certificate)
                <span class="text-sm font-normal text-gray-500">#{{ $certificate->code }}</span>
            @endif
        </h1>
        <div class="flex gap-2 flex-wrap">
            <button type="button" onclick="window.ShopGunDesigner.addText()"
                    class="px-3 py-2 bg-teal-600 text-white rounded-lg text-sm hover:bg-teal-700">➕ متن</button>
            <button type="button" onclick="window.ShopGunDesigner.addRect()"
                    class="px-3 py-2 bg-teal-600 text-white rounded-lg text-sm hover:bg-teal-700">▭ کادر</button>
            <button type="button" onclick="window.ShopGunDesigner.resetToDefault()"
                    class="px-3 py-2 bg-amber-500 text-white rounded-lg text-sm font-bold hover:bg-amber-600">↺ ریست</button>
            <button type="button" onclick="window.ShopGunDesigner.saveDesign()"
                    class="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-bold hover:bg-green-700">
                💾 {{ $isGlobal ? 'ذخیره برای همه' : 'ذخیره' }}
            </button>
        </div>
    </div>

    @if($statusMessage)
        <div class="mb-3 p-3 rounded-lg text-sm font-bold" style="background:#d1fae5;color:#065f46;">
            {{ $statusMessage }}
        </div>
    @endif

    <div class="grid grid-cols-1 lg:grid-cols-4 gap-4">
        <div class="lg:col-span-3 bg-white rounded-xl shadow p-4 flex justify-center items-center"
             style="background: repeating-conic-gradient(#f0f0f0 0% 25%, #ffffff 0% 50%) 50% / 20px 20px; min-height: 640px;">
            <div x-show="!ready" class="text-center text-gray-400 text-sm">
                ⏳ در حال آماده‌سازی ویرایشگر...
            </div>
            <canvas x-show="ready" id="cert-fabric-canvas" width="600" height="600"
                    style="border: 2px solid #b8860b; border-radius: 8px; box-shadow: 0 8px 24px rgba(0,0,0,.15);"></canvas>
        </div>

        <div class="lg:col-span-1 bg-white rounded-xl shadow p-4">
            <h2 class="text-sm font-bold mb-3 pb-2 border-b" style="color:#0d5c63;">✏️ خواص عنصر</h2>
            <div id="designer-props" class="text-gray-400 text-xs text-center py-6">
                یک عنصر انتخاب کنید
            </div>

            <div class="mt-4 pt-4 border-t">
                <h3 class="text-xs font-bold text-gray-600 mb-2">🔤 متغیرها (کلیک = کپی):</h3>
                <div class="flex flex-wrap gap-1">
                    @foreach(['{code}', '{stoneEn}', '{stoneName}', '{metalEn}', '{metal}', '{carat}', '{length}', '{width}', '{weight}', '{brilliant}', '{serial}', '{origin}', '{image}', '{qr}', '{logo}'] as $v)
                        <span class="px-2 py-1 bg-amber-100 text-amber-800 rounded text-xs font-mono cursor-pointer hover:bg-amber-200"
                              onclick="navigator.clipboard.writeText('{{ $v }}'); this.style.background='#fcd34d'; setTimeout(()=>this.style.background='#fef3c7', 300);"
                              title="کلیک = کپی">{{ $v }}</span>
                    @endforeach
                </div>
                <p class="text-[10px] text-gray-500 mt-2 leading-relaxed">
                    💡 این متغیرها در متن‌ها جایگزین می‌شوند:<br>
                    <code>{stoneEn}</code> → نام انگلیسی سنگ<br>
                    <code>{code}</code> → کد شناسنامه<br>
                    <code>{image}</code> → خود تصویر واقعی جایگزین می‌شود (توسط نام image)
                </p>
            </div>
        </div>
    </div>

    {{-- ★★★ داده JSON داخل script tag — بدون مشکل کوتیشن ★★★ --}}
    <script type="application/json" id="designer-config">@json([
        'certId'   => $certificate?->id,
        'isGlobal' => $isGlobal,
    ])</script>

    <script type="application/json" id="designer-data">{!! $designJson ?: 'null' !!}</script>
</div>

<script>
document.addEventListener('alpine:init', function () {
    Alpine.data('designerPage', function () {
        return {
            ready: false,
            tries: 0,
            certId: null,
            isGlobal: false,
            designData: null,

            boot() {
                var self = this;
                try {
                    var cfg = JSON.parse(document.getElementById('designer-config').textContent || '{}');
                    self.certId = cfg.certId;
                    self.isGlobal = !!cfg.isGlobal;

                    var raw = document.getElementById('designer-data').textContent || 'null';
                    self.designData = JSON.parse(raw);
                } catch (e) {
                    console.warn('parse failed:', e);
                    self.designData = null;
                }

                var check = function () {
                    if (window.ShopGunDesigner) {
                        self.ready = true;
                        self.$nextTick(function () {
                            window.ShopGunDesigner.init(self.certId, self.designData, self.isGlobal);
                        });
                    } else {
                        self.tries++;
                        if (self.tries > 80) { console.error('ShopGunDesigner not found'); return; }
                        setTimeout(check, 120);
                    }
                };
                check();
            }
        };
    });
});
</script>
