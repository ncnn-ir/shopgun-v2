<div style="padding:14px" dir="rtl">

    <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;margin-bottom:16px">
        <h1 style="margin:0;font-size:20px;font-weight:700;color:#0d5c63">
            🎨 ویرایشگر شناسنامه
            @if($isGlobal)
                <span style="font-size:13px;font-weight:400;color:#d97706">(طرح پیش‌فرض همه)</span>
            @elseif($certificate)
                <span style="font-size:13px;font-weight:400;color:#64748b">#{{ $certificate->code }}</span>
            @endif
        </h1>
        <div style="display:flex;gap:6px;flex-wrap:wrap">
            <button type="button" id="btn-add-text" class="btn btn-primary btn-sm">➕ متن</button>
            <button type="button" id="btn-add-rect" class="btn btn-primary btn-sm">▭ کادر</button>
            <button type="button" id="btn-reset" class="btn btn-warning btn-sm">↺ ریست</button>
            <button type="button" id="btn-save" class="btn btn-success btn-sm">💾 ذخیره</button>
        </div>
    </div>

    @if($statusMessage)
        <div style="margin-bottom:12px;padding:10px 14px;background:#d1fae5;color:#065f46;border-radius:8px;font-weight:700;font-size:13px">
            {{ $statusMessage }}
        </div>
    @endif

    <div style="display:grid;grid-template-columns:1fr;gap:14px">

        <div style="background:#fff;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,.08);padding:16px;display:flex;justify-content:center;align-items:center;min-height:600px;background-image:repeating-conic-gradient(#f0f0f0 0% 25%, #fff 0% 50%);background-size:20px 20px">
            <div id="designer-loader" style="text-align:center;color:#94a3b8;font-size:13px">
                ⏳ در حال آماده‌سازی ویرایشگر...
            </div>
            <canvas id="cert-fabric-canvas" width="600" height="600" style="border:2px solid #b8860b;border-radius:8px;box-shadow:0 8px 24px rgba(0,0,0,.15);display:none"></canvas>
        </div>

        <div style="background:#fff;border-radius:12px;box-shadow:0 2px 8px rgba(0,0,0,.08);padding:16px">
            <h2 style="margin:0 0 12px;font-size:14px;font-weight:700;color:#0d5c63;padding-bottom:8px;border-bottom:1px solid #e2e8f0">✏️ خواص عنصر</h2>
            <div id="designer-props" style="color:#94a3b8;font-size:13px;text-align:center;padding:20px">
                یک عنصر انتخاب کنید
            </div>

            <div style="margin-top:16px;padding-top:16px;border-top:1px solid #e2e8f0">
                <h3 style="margin:0 0 10px;font-size:12px;font-weight:700;color:#64748b">🔤 متغیرها:</h3>
                <div style="display:flex;flex-wrap:wrap;gap:4px">
                    @foreach(['{code}', '{stoneEn}', '{stoneName}', '{metalEn}', '{metal}', '{carat}', '{length}', '{width}', '{weight}', '{brilliant}', '{serial}', '{origin}'] as $v)
                        <span onclick="navigator.clipboard.writeText('{{ $v }}');this.style.background='#fcd34d';setTimeout(()=>this.style.background='#fef3c7',400)"
                              style="padding:3px 8px;background:#fef3c7;color:#92400e;border-radius:6px;font-size:11px;font-family:monospace;cursor:pointer">{{ $v }}</span>
                    @endforeach
                </div>
            </div>
        </div>
    </div>

    @php
        $__cert = $certificate;
        $__designer = [
            'certId'   => $__cert ? $__cert->id : null,
            'isGlobal' => (bool) $isGlobal,
            'csrf'     => csrf_token(),
            'saveUrl'  => $isGlobal
                ? url('/api/cert/global-design')
                : ($__cert ? url('/certificates/' . $__cert->id . '/design') : ''),
        ];
        $__designJson = $designJson ?: 'null';
    @endphp

    <div id="designer-data-holder"
         data-config='@json($__designer)'
         data-design='{{ $__designJson }}'
         style="display:none"></div>
</div>

{{-- Fabric.js از CDN --}}
@assets
<script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.2.4/fabric.min.js"></script>
@endassets

@script
<script>
(function () {
    'use strict';

    function boot() {
        var holder = document.getElementById('designer-data-holder');
        var canvasEl = document.getElementById('cert-fabric-canvas');
        var loader = document.getElementById('designer-loader');

        if (!holder || !canvasEl) {
            setTimeout(boot, 200);
            return;
        }
        if (typeof fabric === 'undefined') {
            setTimeout(boot, 200);
            return;
        }

        var config = {};
        var designData = null;
        try { config = JSON.parse(holder.dataset.config || '{}'); } catch (e) {}
        try { designData = JSON.parse(holder.dataset.design || 'null'); } catch (e) {}

        if (canvasEl.__fabric) {
            try { canvasEl.__fabric.dispose(); } catch (e) {}
            canvasEl.__fabric = null;
        }

        var canvas = new fabric.Canvas('cert-fabric-canvas', {
            width: 600, height: 600,
            backgroundColor: '#fffef9',
            preserveObjectStacking: true
        });
        canvasEl.__fabric = canvas;
        canvasEl.style.display = 'block';
        if (loader) loader.style.display = 'none';

        var hasDesign = designData && designData.objects && designData.objects.length > 0;

        if (hasDesign) {
            try {
                designData.objects.forEach(function (o) {
                    if (o.pathAlign === 'baseline') o.pathAlign = null;
                    if (o.textBaseline === 'alphabetical') o.textBaseline = 'alphabetic';
                });
                canvas.loadFromJSON(designData, function () {
                    canvas.renderAll();
                    bindEvents(canvas);
                });
            } catch (e) {
                console.warn('loadFromJSON failed:', e);
                buildDefault(canvas);
                bindEvents(canvas);
            }
        } else {
            buildDefault(canvas);
            bindEvents(canvas);
        }

        bindButtons(canvas, config);

        window.ShopGunDesigner = {
            canvas: canvas,
            applyProps: function () { applyProps(canvas); },
            deleteActive: function () { deleteActive(canvas); },
            addText: function () { addText(canvas); },
            addRect: function () { addRect(canvas); },
            saveDesign: function () { save(canvas, config); },
            resetToDefault: function () { reset(canvas); },
        };
    }

    function buildDefault(canvas) {
        var brown = '#6b4423', gold = '#b8860b', teal = '#0d5c63';

        canvas.add(new fabric.Rect({
            left: 40, top: 40, width: 180, height: 180,
            fill: '#f8f5ef', stroke: gold, strokeWidth: 2,
            rx: 8, ry: 8, name: 'image_frame'
        }));

        canvas.add(new fabric.IText('Certificate', {
            left: 560, top: 50, fontSize: 42,
            fontFamily: 'Great Vibes', fill: brown,
            originX: 'right', originY: 'top', name: 'title'
        }));

        canvas.add(new fabric.IText('Quality Guarantee', {
            left: 560, top: 105, fontSize: 14,
            fontFamily: 'Playfair Display', fontStyle: 'italic',
            fill: brown, originX: 'right', originY: 'top', name: 'subtitle'
        }));

        var rows = [
            { name: 'stone', y: 160, t: 'Stone: {stoneEn}' },
            { name: 'metal', y: 190, t: 'Metal: {metalEn} ({carat})' },
            { name: 'size', y: 220, t: 'Size: {length}x{width} mm' },
            { name: 'weight', y: 250, t: 'Weight: {weight} gr' },
            { name: 'code', y: 290, t: '#{code}' }
        ];
        rows.forEach(function (r) {
            canvas.add(new fabric.IText(r.t, {
                left: 560, top: r.y, fontSize: 14,
                fontFamily: 'Inter', fill: '#1e293b',
                originX: 'right', originY: 'top', name: r.name
            }));
        });

        canvas.add(new fabric.Rect({
            left: 40, top: 400, width: 80, height: 80,
            fill: '#fff', stroke: teal, strokeWidth: 2,
            rx: 4, ry: 4, name: 'qr_frame'
        }));
        canvas.add(new fabric.IText('QR', {
            left: 80, top: 440, fontSize: 16,
            fontFamily: 'monospace', fill: teal,
            originX: 'center', originY: 'center', name: 'qr_label'
        }));
        canvas.renderAll();
    }

    function bindEvents(canvas) {
        canvas.on('selection:created', function () { updateProps(canvas); });
        canvas.on('selection:updated', function () { updateProps(canvas); });
        canvas.on('selection:cleared', function () {
            var p = document.getElementById('designer-props');
            if (p) p.innerHTML = '<div style="color:#94a3b8;font-size:13px;text-align:center;padding:20px">یک عنصر انتخاب کنید</div>';
        });
    }

    function updateProps(canvas) {
        var a = canvas.getActiveObject();
        var p = document.getElementById('designer-props');
        if (!a || !p) return;

        var isText = (a.type === 'i-text' || a.type === 'text' || a.type === 'textbox');
        var isRect = (a.type === 'rect');

        var h = '<div style="font-size:12px;font-weight:700;color:#0d5c63;margin-bottom:12px;padding-bottom:6px;border-bottom:1px solid #e2e8f0">' + (a.name || a.type).toUpperCase() + '</div>';

        h += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px">';
        h += '<label style="font-size:11px">X<input type="number" id="p-x" value="' + Math.round(a.left) + '" style="width:100%;padding:5px;border:1px solid #cbd5e1;border-radius:6px;font-size:12px"></label>';
        h += '<label style="font-size:11px">Y<input type="number" id="p-y" value="' + Math.round(a.top) + '" style="width:100%;padding:5px;border:1px solid #cbd5e1;border-radius:6px;font-size:12px"></label>';
        h += '</div>';

        if (isText) {
            var txt = (a.text || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
            h += '<label style="font-size:11px;display:block;margin-bottom:8px">متن<textarea id="p-text" rows="2" style="width:100%;padding:5px;border:1px solid #cbd5e1;border-radius:6px;font-size:12px;font-family:monospace">' + txt + '</textarea></label>';
            h += '<label style="font-size:11px;display:block;margin-bottom:8px">فونت<input type="number" id="p-fs" value="' + (a.fontSize || 14) + '" style="width:100%;padding:5px;border:1px solid #cbd5e1;border-radius:6px;font-size:12px"></label>';
            h += '<label style="font-size:11px;display:block;margin-bottom:8px">رنگ<input type="color" id="p-fill" value="' + (a.fill || '#000000') + '" style="width:100%;height:32px;padding:2px;border:1px solid #cbd5e1;border-radius:6px"></label>';
        }
        if (isRect) {
            h += '<label style="font-size:11px;display:block;margin-bottom:8px">عرض<input type="number" id="p-w" value="' + Math.round(a.width * (a.scaleX || 1)) + '" style="width:100%;padding:5px;border:1px solid #cbd5e1;border-radius:6px;font-size:12px"></label>';
            h += '<label style="font-size:11px;display:block;margin-bottom:8px">ارتفاع<input type="number" id="p-h" value="' + Math.round(a.height * (a.scaleY || 1)) + '" style="width:100%;padding:5px;border:1px solid #cbd5e1;border-radius:6px;font-size:12px"></label>';
            h += '<label style="font-size:11px;display:block;margin-bottom:8px">رنگ خط<input type="color" id="p-stroke" value="' + (a.stroke || '#000000') + '" style="width:100%;height:32px;padding:2px;border:1px solid #cbd5e1;border-radius:6px"></label>';
        }

        h += '<button type="button" onclick="window.ShopGunDesigner.applyProps()" style="width:100%;margin-top:8px;padding:8px;background:#16a34a;color:#fff;border:none;border-radius:8px;font-weight:700;font-size:12px;cursor:pointer">✓ اعمال</button>';
        h += '<button type="button" onclick="window.ShopGunDesigner.deleteActive()" style="width:100%;margin-top:6px;padding:8px;background:#dc2626;color:#fff;border:none;border-radius:8px;font-weight:700;font-size:12px;cursor:pointer">🗑️ حذف</button>';

        p.innerHTML = h;
    }

    function applyProps(canvas) {
        var a = canvas.getActiveObject(); if (!a) return;
        var x = parseFloat((document.getElementById('p-x') || {}).value);
        var y = parseFloat((document.getElementById('p-y') || {}).value);
        if (!isNaN(x)) a.set('left', x);
        if (!isNaN(y)) a.set('top', y);
        var t = document.getElementById('p-text'); if (t) a.set('text', t.value);
        var fs = document.getElementById('p-fs'); if (fs) a.set('fontSize', parseFloat(fs.value));
        var f = document.getElementById('p-fill'); if (f) a.set('fill', f.value);
        var st = document.getElementById('p-stroke'); if (st) a.set('stroke', st.value);
        var w = document.getElementById('p-w'), h = document.getElementById('p-h');
        if (w && h) {
            a.set('width', parseFloat(w.value) / (a.scaleX || 1));
            a.set('height', parseFloat(h.value) / (a.scaleY || 1));
        }
        a.setCoords();
        canvas.renderAll();
    }

    function deleteActive(canvas) {
        var a = canvas.getActiveObject();
        if (a) { canvas.remove(a); canvas.discardActiveObject(); canvas.renderAll(); }
    }

    function addText(canvas) {
        var t = new fabric.IText('متن جدید', {
            left: 300, top: 300, fontSize: 16,
            fontFamily: 'Inter', fill: '#1e293b', originX: 'center'
        });
        canvas.add(t); canvas.setActiveObject(t); canvas.renderAll();
    }

    function addRect(canvas) {
        var r = new fabric.Rect({
            left: 250, top: 250, width: 120, height: 80,
            fill: 'transparent', stroke: '#b8860b', strokeWidth: 1.5, rx: 6, ry: 6
        });
        canvas.add(r); canvas.setActiveObject(r); canvas.renderAll();
    }

    function save(canvas, config) {
        var json = canvas.toJSON(['selectable', 'evented', 'name']);
        json.canvas_width = 600;
        json.canvas_height = 600;
        var str = JSON.stringify(json);

        var event = config.isGlobal ? 'global-designer-save' : 'designer-save';

        if (window.Livewire && window.Livewire.dispatch) {
            try {
                window.Livewire.dispatch(event, { json: str });
                toast('✓ ذخیره شد');
                return;
            } catch (e) { console.warn(e); }
        }
    }

    function toast(msg) {
        var t = document.createElement('div');
        t.style.cssText = 'position:fixed;bottom:20px;right:20px;background:#16a34a;color:#fff;padding:12px 20px;border-radius:10px;font-weight:700;z-index:9999';
        t.textContent = msg;
        document.body.appendChild(t);
        setTimeout(function () { t.remove(); }, 2000);
    }

    function reset(canvas) {
        if (!confirm('طرح ریست شود؟')) return;
        canvas.clear();
        canvas.setBackgroundColor('#fffef9', function () {});
        buildDefault(canvas);
        canvas.renderAll();
    }

    function bindButtons(canvas, config) {
        var bt = document.getElementById('btn-add-text');
        var br = document.getElementById('btn-add-rect');
        var bs = document.getElementById('btn-save');
        var breset = document.getElementById('btn-reset');
        if (bt) bt.onclick = function () { addText(canvas); };
        if (br) br.onclick = function () { addRect(canvas); };
        if (bs) bs.onclick = function () { save(canvas, config); };
        if (breset) breset.onclick = function () { reset(canvas); };
    }

    setTimeout(boot, 150);
})();
</script>
@endscript
