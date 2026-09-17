(function () {
  'use strict';

  // ═══════ Fix: alphabetical → alphabetic ═══════
  (function fixBaseline() {
    if (typeof CanvasRenderingContext2D === 'undefined') return;
    try {
      var proto = CanvasRenderingContext2D.prototype;
      var desc = Object.getOwnPropertyDescriptor(proto, 'textBaseline');
      if (desc && desc.set) {
        Object.defineProperty(proto, 'textBaseline', {
          configurable: true,
          get: desc.get,
          set: function (v) {
            if (v === 'alphabetical') v = 'alphabetic';
            return desc.set.call(this, v);
          }
        });
      }
    } catch (e) { /* silent */ }
  })();

  // ═══════ Silence warning ═══════
  var _warn = console.warn;
  console.warn = function () {
    var m = arguments[0];
    if (typeof m === 'string' && m.indexOf('alphabetical') !== -1) return;
    _warn.apply(console, arguments);
  };

  var canvas = null;
  var currentCertId = null;
  var isGlobal = false;
  var CANVAS_W = 600;
  var CANVAS_H = 600;
  var PLACEHOLDER_IMG = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="180" height="180"><rect width="180" height="180" fill="%23eeeeee"/><text x="90" y="95" font-family="sans-serif" font-size="14" fill="%23888888" text-anchor="middle">تصویر محصول</text></svg>';
  var PLACEHOLDER_QR = 'https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=SAMPLE';
  var PLACEHOLDER_LOGO = 'data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" width="80" height="80"><rect width="80" height="80" fill="%23fef3c7"/><text x="40" y="45" font-family="sans-serif" font-size="12" fill="%23b8860b" text-anchor="middle">لوگو</text></svg>';

  function loadFabric(cb) {
    if (typeof fabric !== 'undefined') { cb(); return; }
    var s = document.createElement('script');
    s.src = 'https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.2.4/fabric.min.js';
    s.onload = cb;
    s.onerror = function () { console.error('fabric.js load failed'); };
    document.head.appendChild(s);
  }

  function init(certId, designData, globalMode) {
    currentCertId = certId;
    isGlobal = !!globalMode;
    loadFabric(function () {
      var el = document.getElementById('cert-fabric-canvas');
      if (!el) { setTimeout(function () { init(certId, designData, globalMode); }, 150); return; }
      if (canvas) { try { canvas.dispose(); } catch (e) {} canvas = null; }

      canvas = new fabric.Canvas('cert-fabric-canvas', {
        width: CANVAS_W,
        height: CANVAS_H,
        backgroundColor: '#fffef9',
        preserveObjectStacking: true
      });

      var hasDesign = designData && designData.objects && designData.objects.length > 0;

      if (hasDesign) {
        try {
          // Remove invalid pathAlign from objects
          designData.objects.forEach(function (o) {
            if (o.pathAlign === 'baseline') o.pathAlign = null;
            if (o.textBaseline === 'alphabetical') o.textBaseline = 'alphabetic';
          });
          canvas.loadFromJSON(designData, function () {
            canvas.renderAll();
            bind();
          });
        } catch (e) {
          console.warn('loadFromJSON failed, fallback to default', e);
          buildDefaultDesign();
          bind();
        }
      } else {
        buildDefaultDesign();
        bind();
      }
    });
  }

  // ═══════ طرح پیش‌فرض با نمونه‌های واقعی ═══════
  function buildDefaultDesign() {
    var brown   = '#6b4423';
    var gold    = '#b8860b';
    var teal    = '#0d5c63';
    var primary = '#1a5276';
    var textCol = '#2c3e50';

    // ---- FRAME تصویر + IMAGE ----
    fabric.Image.fromURL(PLACEHOLDER_IMG, function (img) {
      img.set({
        left: 40, top: 40, width: 180, height: 180,
        name: 'image', selectable: true, evented: true
      });
      canvas.add(img);
      canvas.sendToBack(img);
      canvas.renderAll();
    }, { crossOrigin: 'anonymous' });

    canvas.add(new fabric.Rect({
      left: 40, top: 40, width: 180, height: 180,
      fill: 'transparent', stroke: gold, strokeWidth: 3,
      rx: 8, ry: 8, name: 'image_frame', selectable: true
    }));

    // ---- متغیر تصویر ----
    canvas.add(new fabric.IText('{image}', {
      left: 130, top: 225, width: 100,
      fontSize: 10, fontFamily: 'monospace',
      fill: '#999999', originX: 'center', originY: 'top',
      name: 'image_var', selectable: true
    }));

    // ---- عنوان ----
    canvas.add(new fabric.IText('Certificate', {
      left: 560, top: 50, fontSize: 42,
      fontFamily: 'Great Vibes', fill: brown,
      originX: 'right', originY: 'top',
      name: 'title', selectable: true
    }));

    canvas.add(new fabric.IText('Quality Guarantee', {
      left: 560, top: 105, fontSize: 14,
      fontFamily: 'Playfair Display', fontStyle: 'italic',
      fill: brown, originX: 'right', originY: 'top',
      name: 'subtitle', selectable: true
    }));

    // ---- description ----
    canvas.add(new fabric.IText(
      'This certificate is only for authenticity\nof purchased product.',
      {
        left: 560, top: 140, fontSize: 10,
        fontFamily: 'Playfair Display',
        fill: brown, originX: 'right', originY: 'top',
        textAlign: 'right', lineHeight: 1.4,
        name: 'description', selectable: true
      }
    ));

    // ---- امضا ----
    canvas.add(new fabric.IText('Quality Guarantee', {
      left: 560, top: 195, fontSize: 22,
      fontFamily: 'Great Vibes', fill: brown,
      originX: 'right', originY: 'top',
      name: 'signature', selectable: true
    }));

    canvas.add(new fabric.Line([420, 235, 560, 235], {
      stroke: brown, strokeWidth: 1,
      name: 'sig_line', selectable: true
    }));

    // ---- QR نمونه ----
    fabric.Image.fromURL(PLACEHOLDER_QR, function (img) {
      img.set({
        left: 40, top: 400, width: 70, height: 70,
        name: 'qr_image', selectable: true, evented: true
      });
      canvas.add(img);
      canvas.renderAll();
    }, { crossOrigin: 'anonymous' });

    canvas.add(new fabric.Rect({
      left: 40, top: 400, width: 70, height: 70,
      fill: 'transparent', stroke: teal, strokeWidth: 2,
      rx: 4, ry: 4, name: 'qr_frame', selectable: true
    }));

    canvas.add(new fabric.IText('{qr}', {
      left: 75, top: 473, fontSize: 9,
      fontFamily: 'monospace', fill: '#999999',
      originX: 'center', originY: 'top',
      name: 'qr_var', selectable: true
    }));

    // ---- لوگو نمونه ----
    fabric.Image.fromURL(PLACEHOLDER_LOGO, function (img) {
      img.set({
        left: 130, top: 400, width: 60, height: 60,
        name: 'logo_image', selectable: true, evented: true
      });
      canvas.add(img);
      canvas.renderAll();
    }, { crossOrigin: 'anonymous' });

    canvas.add(new fabric.Rect({
      left: 130, top: 400, width: 60, height: 60,
      fill: 'transparent', stroke: gold, strokeWidth: 2,
      rx: 4, ry: 4, name: 'logo_frame', selectable: true
    }));

    canvas.add(new fabric.IText('{logo}', {
      left: 160, top: 463, fontSize: 9,
      fontFamily: 'monospace', fill: '#999999',
      originX: 'center', originY: 'top',
      name: 'logo_var', selectable: true
    }));

    // ---- کد ----
    canvas.add(new fabric.IText('#{code}', {
      left: 560, top: 410, fontSize: 22,
      fontFamily: 'monospace', fontWeight: 'bold',
      fill: primary, originX: 'right', originY: 'top',
      name: 'code', selectable: true
    }));

    // ---- ردیف‌های جدول (قابل جابجایی و تغییر سایز جدا) ----
    var rows = [
      { name: 'row_stone',   y: 470, t: 'Stone: {stoneEn}' },
      { name: 'row_metal',   y: 495, t: 'Metal: {metalEn} ({carat})' },
      { name: 'row_size',    y: 520, t: 'Size: {length}*{width} mm' },
      { name: 'row_weight',  y: 545, t: 'Weight: {weight} gr' },
      { name: 'row_brill',   y: 570, t: 'Brilliant: {brilliant}' }
    ];
    rows.forEach(function (r) {
      canvas.add(new fabric.IText(r.t, {
        left: 560, top: r.y, fontSize: 13,
        fontFamily: 'Inter', fill: textCol,
        originX: 'right', originY: 'top',
        name: r.name, selectable: true
      }));
    });

    // خط زیر هر ردیف جدول (برای تغییر آسان)
    rows.forEach(function (r, i) {
      canvas.add(new fabric.Line([200, r.y + 20, 560, r.y + 20], {
        stroke: '#d0d0d0', strokeWidth: 1,
        name: 'table_line_' + i, selectable: true
      }));
    });

    canvas.renderAll();
  }

  function bind() {
    canvas.on('selection:created', updateProps);
    canvas.on('selection:updated', updateProps);
    canvas.on('selection:cleared', function () {
      var p = document.getElementById('designer-props');
      if (p) p.innerHTML = '<div style="color:#888;font-size:12px;text-align:center;padding:20px;">یک عنصر انتخاب کنید</div>';
    });
  }

  function updateProps() {
    var a = canvas.getActiveObject();
    var p = document.getElementById('designer-props');
    if (!a || !p) return;

    var isText = a.type === 'i-text' || a.type === 'text' || a.type === 'textbox';
    var isImg  = a.type === 'image';
    var isRect = a.type === 'rect';
    var isLine = a.type === 'line';

    var h = '<div style="font-size:11px;font-weight:700;color:#0d5c63;margin-bottom:10px;border-bottom:1px solid #ddd;padding-bottom:6px;">'
          + (a.name || a.type).toUpperCase() + '</div>';

    h += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">';
    h += '<label style="font-size:11px;">X<input type="number" id="prop-x" value="' + Math.round(a.left) + '" style="width:100%;padding:4px;border:1px solid #ccc;border-radius:4px;"></label>';
    h += '<label style="font-size:11px;">Y<input type="number" id="prop-y" value="' + Math.round(a.top) + '" style="width:100%;padding:4px;border:1px solid #ccc;border-radius:4px;"></label>';
    h += '</div>';

    if (isText) {
      var txt = (a.text || '').replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
      h += '<label style="font-size:11px;display:block;margin-top:6px;">متن<textarea id="prop-text" rows="2" style="width:100%;padding:4px;border:1px solid #ccc;border-radius:4px;font-family:monospace;">' + txt + '</textarea></label>';
      h += '<label style="font-size:11px;display:block;margin-top:6px;">اندازه فونت<input type="number" id="prop-fs" value="' + (a.fontSize || 12) + '" style="width:100%;padding:4px;border:1px solid #ccc;border-radius:4px;"></label>';
      h += '<label style="font-size:11px;display:block;margin-top:6px;">رنگ متن<input type="color" id="prop-fill" value="' + (a.fill || '#000000') + '" style="width:100%;height:30px;padding:2px;border:1px solid #ccc;border-radius:4px;"></label>';
      h += '<label style="font-size:11px;display:block;margin-top:6px;">فونت<input type="text" id="prop-ff" value="' + (a.fontFamily || 'Inter') + '" style="width:100%;padding:4px;border:1px solid #ccc;border-radius:4px;"></label>';
    }
    if (isRect || isImg) {
      h += '<label style="font-size:11px;display:block;margin-top:6px;">عرض<input type="number" id="prop-w" value="' + Math.round(a.width * (a.scaleX || 1)) + '" style="width:100%;padding:4px;border:1px solid #ccc;border-radius:4px;"></label>';
      h += '<label style="font-size:11px;display:block;margin-top:6px;">ارتفاع<input type="number" id="prop-h" value="' + Math.round(a.height * (a.scaleY || 1)) + '" style="width:100%;padding:4px;border:1px solid #ccc;border-radius:4px;"></label>';
    }
    if (isRect) {
      h += '<label style="font-size:11px;display:block;margin-top:6px;">رنگ خط<input type="color" id="prop-stroke" value="' + (a.stroke || '#000000') + '" style="width:100%;height:30px;padding:2px;border:1px solid #ccc;border-radius:4px;"></label>';
    }
    if (isLine) {
      h += '<label style="font-size:11px;display:block;margin-top:6px;">رنگ<input type="color" id="prop-stroke" value="' + (a.stroke || '#000000') + '" style="width:100%;height:30px;padding:2px;border:1px solid #ccc;border-radius:4px;"></label>';
    }

    h += '<button onclick="window.ShopGunDesigner.applyProps()" style="width:100%;margin-top:10px;padding:6px;background:#27ae60;color:#fff;border:none;border-radius:6px;cursor:pointer;font-weight:700;">اعمال</button>';
    h += '<button onclick="window.ShopGunDesigner.deleteActive()" style="width:100%;margin-top:6px;padding:6px;background:#e74c3c;color:#fff;border:none;border-radius:6px;cursor:pointer;font-weight:700;">حذف</button>';

    p.innerHTML = h;
  }

  function applyProps() {
    var a = canvas.getActiveObject(); if (!a) return;
    var x = parseFloat((document.getElementById('prop-x') || {}).value);
    var y = parseFloat((document.getElementById('prop-y') || {}).value);
    if (!isNaN(x)) a.set('left', x);
    if (!isNaN(y)) a.set('top', y);
    var t = document.getElementById('prop-text'); if (t) a.set('text', t.value);
    var fs = document.getElementById('prop-fs'); if (fs) a.set('fontSize', parseFloat(fs.value));
    var f = document.getElementById('prop-fill'); if (f) a.set('fill', f.value);
    var ff = document.getElementById('prop-ff'); if (ff) a.set('fontFamily', ff.value);
    var st = document.getElementById('prop-stroke'); if (st) a.set('stroke', st.value);
    var w = document.getElementById('prop-w'), h = document.getElementById('prop-h');
    if (w && h) {
      a.set('width',  parseFloat(w.value) / (a.scaleX || 1));
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
      left: 300, top: 300, fontSize: 14,
      fontFamily: 'Inter', fill: '#2c3e50', originX: 'center'
    });
    canvas.add(t); canvas.setActiveObject(t); canvas.renderAll();
  }

  function addRect() {
    if (!canvas) return;
    var r = new fabric.Rect({
      left: 250, top: 250, width: 100, height: 60,
      fill: 'transparent', stroke: '#b8860b', strokeWidth: 1.5, rx: 6, ry: 6
    });
    canvas.add(r); canvas.setActiveObject(r); canvas.renderAll();
  }

  function saveDesign() {
    if (!canvas) { alert('Canvas آماده نیست'); return; }

    var json = canvas.toJSON(['selectable', 'evented', 'name']);
    json.canvas_width  = CANVAS_W;
    json.canvas_height = CANVAS_H;
    var jsonStr = JSON.stringify(json);

    // ★ Global mode → ارسال به رویداد global-designer-save
    var eventName = isGlobal ? 'global-designer-save' : 'designer-save';

    if (window.Livewire && window.Livewire.dispatch) {
      try {
        window.Livewire.dispatch(eventName, { json: jsonStr });
        showSaveToast(isGlobal ? '✅ طرح پیش‌فرض برای همه ذخیره شد' : '✅ طراحی ذخیره شد');
        return;
      } catch (e) { console.warn('dispatch failed:', e); }
    }

    // Fallback
    var url = isGlobal ? '/api/certificates/design-global' : ('/certificates/' + currentCertId + '/design');
    fetch(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-TOKEN': (document.querySelector('meta[name="csrf-token"]') || {}).content || ''
      },
      body: JSON.stringify({ design_data: json })
    }).then(function (r) { return r.json(); })
      .then(function () { showSaveToast('✅ ذخیره شد'); })
      .catch(function (e) { alert('خطا در ذخیره: ' + e.message); });
  }

  function showSaveToast(msg) {
    var t = document.createElement('div');
    t.style.cssText = 'position:fixed;bottom:20px;right:20px;background:#27ae60;color:#fff;padding:12px 20px;border-radius:10px;font-weight:700;z-index:9999;box-shadow:0 4px 12px rgba(0,0,0,.3);';
    t.textContent = msg;
    document.body.appendChild(t);
    setTimeout(function () { t.remove(); }, 2000);
  }

  function resetToDefault() {
    if (!canvas) return;
    if (!confirm('طرح به حالت پیش‌فرض برگردد؟ (ذخیره نشده)')) return;
    canvas.clear();
    canvas.setBackgroundColor('#fffef9', function () {});
    buildDefaultDesign();
    canvas.renderAll();
  }

  window.ShopGunDesigner = {
    init: init,
    applyProps: applyProps,
    deleteActive: deleteActive,
    addText: addText,
    addRect: addRect,
    saveDesign: saveDesign,
    resetToDefault: resetToDefault,
    getCanvas: function () { return canvas; }
  };
})();
