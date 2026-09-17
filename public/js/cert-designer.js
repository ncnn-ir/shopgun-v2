/* ShopGun Designer v3 */
(function() {
    'use strict';

    var canvas = null;
    var currentConfig = {};
    var CANVAS_W = 600;
    var CANVAS_H = 600;

    function loadFabric(cb) {
        if (typeof fabric !== 'undefined') { cb(); return; }
        var s = document.createElement('script');
        s.src = 'https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.2.4/fabric.min.js';
        s.onload = cb;
        s.onerror = function() {
            console.error('Fabric.js failed to load from CDN');
            document.getElementById('designer-loader').innerHTML =
                '<span style="color:#dc2626">❌ Fabric.js بارگذاری نشد. اینترنت چک کن.</span>';
        };
        document.head.appendChild(s);
    }

    function init() {
        var configEl = document.getElementById('designer-config');
        var dataEl = document.getElementById('designer-data');
        var canvasEl = document.getElementById('cert-fabric-canvas');
        var loader = document.getElementById('designer-loader');

        if (!configEl || !canvasEl) {
            console.error('Designer elements not found');
            return;
        }

        try {
            currentConfig = JSON.parse(configEl.textContent || '{}');
        } catch (e) { currentConfig = {}; }

        var designData = null;
        try {
            if (dataEl) designData = JSON.parse(dataEl.textContent || 'null');
        } catch (e) { designData = null; }

        loadFabric(function() {
            if (canvas) { try { canvas.dispose(); } catch (e) {} }

            canvas = new fabric.Canvas('cert-fabric-canvas', {
                width: CANVAS_W,
                height: CANVAS_H,
                backgroundColor: '#fffef9',
                preserveObjectStacking: true
            });

            canvasEl.style.display = 'block';
            if (loader) loader.style.display = 'none';

            var hasDesign = designData && designData.objects && designData.objects.length > 0;

            if (hasDesign) {
                try {
                    designData.objects.forEach(function(o) {
                        if (o.pathAlign === 'baseline') o.pathAlign = null;
                        if (o.textBaseline === 'alphabetical') o.textBaseline = 'alphabetic';
                    });
                    canvas.loadFromJSON(designData, function() {
                        canvas.renderAll();
                        bindEvents();
                    });
                } catch (e) {
                    console.warn('loadFromJSON failed:', e);
                    buildDefault();
                    bindEvents();
                }
            } else {
                buildDefault();
                bindEvents();
            }

            bindButtons();
        });
    }

    function buildDefault() {
        var brown = '#6b4423';
        var gold = '#b8860b';
        var teal = '#0d5c63';

        // Image placeholder
        canvas.add(new fabric.Rect({
            left: 40, top: 40, width: 180, height: 180,
            fill: '#f8f5ef', stroke: gold, strokeWidth: 2,
            rx: 8, ry: 8, name: 'image_frame'
        }));

        // Title
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

        // Data rows
        var rows = [
            { name: 'stone', y: 160, t: 'Stone: {stoneEn}' },
            { name: 'metal', y: 190, t: 'Metal: {metalEn} ({carat})' },
            { name: 'size', y: 220, t: 'Size: {length}x{width} mm' },
            { name: 'weight', y: 250, t: 'Weight: {weight} gr' },
            { name: 'code', y: 290, t: '#{code}' }
        ];

        rows.forEach(function(r) {
            canvas.add(new fabric.IText(r.t, {
                left: 560, top: r.y, fontSize: 14,
                fontFamily: 'Inter', fill: '#1e293b',
                originX: 'right', originY: 'top', name: r.name
            }));
        });

        // QR placeholder
        canvas.add(new fabric.Rect({
            left: 40, top: 400, width: 80, height: 80,
            fill: '#fff', stroke: teal, strokeWidth: 2,
            rx: 4, ry: 4, name: 'qr_frame'
        }));

        canvas.add(new fabric.IText('QR', {
            left: 80, top: 435, fontSize: 16,
            fontFamily: 'monospace', fill: teal,
            originX: 'center', originY: 'center', name: 'qr_label'
        }));

        canvas.renderAll();
    }

    function bindEvents() {
        canvas.on('selection:created', updateProps);
        canvas.on('selection:updated', updateProps);
        canvas.on('selection:cleared', function() {
            var p = document.getElementById('designer-props');
            if (p) p.innerHTML = '<div style="color:#94a3b8;font-size:13px;text-align:center;padding:20px">یک عنصر انتخاب کنید</div>';
        });
    }

    function updateProps() {
        var a = canvas.getActiveObject();
        var p = document.getElementById('designer-props');
        if (!a || !p) return;

        var isText = (a.type === 'i-text' || a.type === 'text' || a.type === 'textbox');
        var isRect = (a.type === 'rect');

        var h = '<div style="font-size:12px;font-weight:700;color:#0d5c63;margin-bottom:12px;padding-bottom:6px;border-bottom:1px solid #e2e8f0">'
              + (a.name || a.type).toUpperCase() + '</div>';

        h += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:10px">';
        h += '<label style="font-size:11px">X<input type="number" id="p-x" value="' + Math.round(a.left) + '" style="width:100%;padding:5px;border:1px solid #cbd5e1;border-radius:6px;font-size:12px"></label>';
        h += '<label style="font-size:11px">Y<input type="number" id="p-y" value="' + Math.round(a.top) + '" style="width:100%;padding:5px;border:1px solid #cbd5e1;border-radius:6px;font-size:12px"></label>';
        h += '</div>';

        if (isText) {
            var txt = (a.text || '').replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/"/g, '&quot;');
            h += '<label style="font-size:11px;display:block;margin-bottom:8px">متن<textarea id="p-text" rows="2" style="width:100%;padding:5px;border:1px solid #cbd5e1;border-radius:6px;font-size:12px;font-family:monospace">' + txt + '</textarea></label>';
            h += '<label style="font-size:11px;display:block;margin-bottom:8px">اندازه فونت<input type="number" id="p-fs" value="' + (a.fontSize || 14) + '" style="width:100%;padding:5px;border:1px solid #cbd5e1;border-radius:6px;font-size:12px"></label>';
            h += '<label style="font-size:11px;display:block;margin-bottom:8px">رنگ متن<input type="color" id="p-fill" value="' + (a.fill || '#000000') + '" style="width:100%;height:32px;padding:2px;border:1px solid #cbd5e1;border-radius:6px"></label>';
            h += '<label style="font-size:11px;display:block;margin-bottom:8px">فونت<input type="text" id="p-ff" value="' + (a.fontFamily || 'Inter') + '" style="width:100%;padding:5px;border:1px solid #cbd5e1;border-radius:6px;font-size:12px"></label>';
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

    function applyProps() {
        var a = canvas.getActiveObject(); if (!a) return;

        var x = parseFloat((document.getElementById('p-x') || {}).value);
        var y = parseFloat((document.getElementById('p-y') || {}).value);
        if (!isNaN(x)) a.set('left', x);
        if (!isNaN(y)) a.set('top', y);

        var t = document.getElementById('p-text'); if (t) a.set('text', t.value);
        var fs = document.getElementById('p-fs'); if (fs) a.set('fontSize', parseFloat(fs.value));
        var f = document.getElementById('p-fill'); if (f) a.set('fill', f.value);
        var ff = document.getElementById('p-ff'); if (ff) a.set('fontFamily', ff.value);
        var st = document.getElementById('p-stroke'); if (st) a.set('stroke', st.value);
        var w = document.getElementById('p-w'); var h = document.getElementById('p-h');
        if (w && h) {
            a.set('width', parseFloat(w.value) / (a.scaleX || 1));
            a.set('height', parseFloat(h.value) / (a.scaleY || 1));
        }
        a.setCoords();
        canvas.renderAll();
    }

    function deleteActive() {
        var a = canvas.getActiveObject();
        if (a) { canvas.remove(a); canvas.discardActiveObject(); canvas.renderAll(); }
    }

    function addText() {
        if (!canvas) return;
        var t = new fabric.IText('متن جدید', {
            left: 300, top: 300, fontSize: 16,
            fontFamily: 'Inter', fill: '#1e293b', originX: 'center'
        });
        canvas.add(t); canvas.setActiveObject(t); canvas.renderAll();
    }

    function addRect() {
        if (!canvas) return;
        var r = new fabric.Rect({
            left: 250, top: 250, width: 120, height: 80,
            fill: 'transparent', stroke: '#b8860b', strokeWidth: 1.5, rx: 6, ry: 6
        });
        canvas.add(r); canvas.setActiveObject(r); canvas.renderAll();
    }

    function save() {
        if (!canvas) { alert('Canvas آماده نیست'); return; }

        var json = canvas.toJSON(['selectable','evented','name']);
        json.canvas_width = CANVAS_W;
        json.canvas_height = CANVAS_H;
        var str = JSON.stringify(json);

        var isGlobal = currentConfig.isGlobal;
        var eventName = isGlobal ? 'global-designer-save' : 'designer-save';

        if (window.Livewire && window.Livewire.dispatch) {
            try {
                window.Livewire.dispatch(eventName, { json: str });
                showToast('✓ ذخیره شد');
                return;
            } catch (e) { console.warn(e); }
        }

        // fallback: fetch
        var url = currentConfig.saveUrl;
        if (!url) { alert('آدرس ذخیره نامعتبر'); return; }

        fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': currentConfig.csrf || ''
            },
            body: JSON.stringify({ design_data: json })
        }).then(function(r) { return r.json(); })
          .then(function() { showToast('✓ ذخیره شد'); })
          .catch(function(e) { alert('خطا: ' + e.message); });
    }

    function showToast(msg) {
        var t = document.createElement('div');
        t.style.cssText = 'position:fixed;bottom:20px;right:20px;background:#16a34a;color:#fff;padding:12px 20px;border-radius:10px;font-weight:700;z-index:9999;box-shadow:0 4px 12px rgba(0,0,0,.3)';
        t.textContent = msg;
        document.body.appendChild(t);
        setTimeout(function() { t.remove(); }, 2000);
    }

    function reset() {
        if (!canvas) return;
        if (!confirm('طرح ریست شود؟ تغییرات ذخیره نشده از دست می‌رود.')) return;
        canvas.clear();
        canvas.setBackgroundColor('#fffef9', function() {});
        buildDefault();
        canvas.renderAll();
    }

    function bindButtons() {
        var bt = document.getElementById('btn-add-text');
        var br = document.getElementById('btn-add-rect');
        var bs = document.getElementById('btn-save');
        var breset = document.getElementById('btn-reset');

        if (bt) bt.onclick = addText;
        if (br) br.onclick = addRect;
        if (bs) bs.onclick = save;
        if (breset) breset.onclick = reset;
    }

    window.ShopGunDesigner = {
        init: init,
        applyProps: applyProps,
        deleteActive: deleteActive,
        addText: addText,
        addRect: addRect,
        saveDesign: save,
        resetToDefault: reset,
        getCanvas: function() { return canvas; }
    };

    // Auto-init when DOM ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            setTimeout(init, 100);
        });
    } else {
        setTimeout(init, 100);
    }

    // Livewire navigate re-init
    document.addEventListener('livewire:navigated', function() {
        setTimeout(init, 200);
    });
})();
