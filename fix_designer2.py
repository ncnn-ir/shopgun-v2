#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix Designer — JSON x-data + alphabetical + Global Designer"""
import shutil, json
from pathlib import Path
from datetime import datetime

PROJECT = Path(r"D:\prodo\shopgun-v2.1")
if not PROJECT.exists():
    PROJECT = Path(input("مسیر پروژه: ").strip().strip('"'))

def write(rel, content):
    full = PROJECT / rel
    full.parent.mkdir(parents=True, exist_ok=True)
    with open(full, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print(f"  ✓ {rel}")

def backup(rel):
    src = PROJECT / rel
    if not src.exists(): return
    bd = PROJECT / "storage/backups"; bd.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(src, bd / f"{src.stem}_{ts}.bak")

# ═══════════════════════════════════════════════════════════════
# ۱) cert-designer.js — نسخه نهایی با همه فیکس‌ها
# ═══════════════════════════════════════════════════════════════
CERT_DESIGNER_JS = r"""(function () {
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
"""

# ═══════════════════════════════════════════════════════════════
# ۲) Designer.php — پشتیبانی از global + per-cert
# ═══════════════════════════════════════════════════════════════
DESIGNER_PHP = r'''<?php

namespace App\Livewire\Certificates;

use App\Models\Certificate;
use App\Models\CertSetting;
use Livewire\Attributes\On;
use Livewire\Component;

class Designer extends Component
{
    public ?Certificate $certificate = null;
    public string $designJson = 'null';
    public string $statusMessage = '';
    public bool $isGlobal = false;

    public function mount(?Certificate $certificate = null): void
    {
        if ($certificate && $certificate->exists) {
            $this->certificate = $certificate;
            $this->isGlobal = false;
            $design = $certificate->design_data;
        } else {
            $this->isGlobal = true;
            $design = CertSetting::get('global_design', null);
        }

        if ($design) {
            $this->designJson = is_string($design) ? $design : json_encode($design, JSON_UNESCAPED_UNICODE);
        } else {
            $this->designJson = 'null';
        }
    }

    #[On('designer-save')]
    public function saveDesign($json = null): void
    {
        $design = $this->decodeJson($json);
        if ($design === null) {
            $this->statusMessage = '❌ JSON نامعتبر';
            return;
        }

        if (!$this->certificate) {
            $this->statusMessage = '❌ شناسنامه‌ای موجود نیست';
            return;
        }

        $this->certificate->update(['design_data' => $design]);
        $this->designJson = is_string($json) ? $json : json_encode($json, JSON_UNESCAPED_UNICODE);
        $this->statusMessage = '✅ طراحی ذخیره شد در ' . now()->format('H:i:s');
    }

    #[On('global-designer-save')]
    public function saveGlobalDesign($json = null): void
    {
        $design = $this->decodeJson($json);
        if ($design === null) {
            $this->statusMessage = '❌ JSON نامعتبر';
            return;
        }

        CertSetting::set('global_design', $design, 'cert');
        $this->designJson = is_string($json) ? $json : json_encode($json, JSON_UNESCAPED_UNICODE);
        $this->statusMessage = '✅ طرح پیش‌فرض برای همه شناسنامه‌ها ذخیره شد';
    }

    protected function decodeJson($json): ?array
    {
        if (is_string($json)) {
            $d = json_decode($json, true);
            return is_array($d) ? $d : null;
        }
        if (is_array($json)) return $json;
        return null;
    }

    public function resetDesign(): void
    {
        if ($this->isGlobal) {
            CertSetting::set('global_design', null, 'cert');
        } elseif ($this->certificate) {
            $this->certificate->update(['design_data' => null]);
        }
        $this->designJson = 'null';
        $this->statusMessage = '↺ طراحی ریست شد';
    }

    public function render()
    {
        return view('livewire.certificates.designer')
            ->layout('components.layouts.app');
    }
}
'''

# ═══════════════════════════════════════════════════════════════
# ۳) Designer Blade — با <script> برای JSON
# ═══════════════════════════════════════════════════════════════
DESIGNER_BLADE = r'''<div class="p-4 md:p-6" dir="rtl" x-data="designerPage()" x-init="boot()">
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
'''

# ═══════════════════════════════════════════════════════════════
# ۴) CertRenderer — پشتیبانی از global_design
# ═══════════════════════════════════════════════════════════════
def patch_cert_renderer():
    """فقط در CertRenderer متد renderCard رو آپدیت کن تا global_design رو هم چک کنه"""
    path = PROJECT / "app/Services/CertRenderer.php"
    if not path.exists():
        print("  ⚠️ CertRenderer پیدا نشد")
        return

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # در renderCard، اضافه کن global_design چک بشه
    old = """    public static function renderCard(Certificate $cert): string
    {
        // اگر design_data دارد، از آن استفاده کن
        if (!empty($cert->design_data) && is_array($cert->design_data)) {
            return self::renderFromDesign($cert, $cert->design_data, false);
        }
        return self::buildCardInner($cert, false);
    }"""

    new = """    public static function renderCard(Certificate $cert): string
    {
        // اول design_data شناسنامه
        if (!empty($cert->design_data) && is_array($cert->design_data)) {
            return self::renderFromDesign($cert, $cert->design_data, false);
        }
        // بعد global_design
        $global = self::getGlobalDesign();
        if (!empty($global) && is_array($global)) {
            return self::renderFromDesign($cert, $global, false);
        }
        // پیش‌فرض
        return self::buildCardInner($cert, false);
    }

    protected static function getGlobalDesign(): ?array
    {
        try {
            if (class_exists(\\App\\Models\\CertSetting::class)) {
                $d = \\App\\Models\\CertSetting::get('global_design', null);
                if (is_string($d)) return json_decode($d, true);
                if (is_array($d)) return $d;
            }
        } catch (\\Throwable $e) {}
        return null;
    }"""

    if old in content and 'getGlobalDesign' not in content:
        content = content.replace(old, new)
        with open(path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        print("  ✓ CertRenderer: global_design پشتیبانی شد")
    else:
        print("  ⏭ CertRenderer از قبل آپدیت شده یا الگو متفاوت است")

# ═══════════════════════════════════════════════════════════════
# ۵) Index blade — دکمه طراحی همه
# ═══════════════════════════════════════════════════════════════
def patch_index_blade():
    path = PROJECT / "resources/views/livewire/certificates/index.blade.php"
    if not path.exists():
        print("  ⚠️ index blade پیدا نشد")
        return

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # اگر دکمه طراحی پیش‌فرض نداره، اضافه کن
    if 'طراحی پیش‌فرض' not in content:
        old = '<a href="{{ route(\'certificates.create\') }}" class="btn btn-primary btn-sm">➕ شناسنامه جدید</a>'
        new = (
            '<a href="{{ route(\'certificates.designer\') }}" class="btn btn-outline btn-sm" '
            'title="طرح پیش‌فرض برای همه">🎨 طراحی پیش‌فرض</a>\n'
            '            <a href="{{ route(\'certificates.create\') }}" class="btn btn-primary btn-sm">➕ شناسنامه جدید</a>'
        )
        if old in content:
            content = content.replace(old, new)
            with open(path, 'w', encoding='utf-8', newline='\n') as f:
                f.write(content)
            print("  ✓ دکمه طراحی پیش‌فرض اضافه شد")
        else:
            print("  ⚠️ الگو پیدا نشد")
    else:
        print("  ⏭ دکمه از قبل موجود")

# ═══════════════════════════════════════════════════════════════
# اجرا
# ═══════════════════════════════════════════════════════════════
def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  Fix Designer — JSON + alphabetical + Global                 ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    print("📦 Backup...")
    for rel in [
        "app/Services/CertRenderer.php",
        "app/Livewire/Certificates/Designer.php",
        "resources/views/livewire/certificates/designer.blade.php",
        "resources/views/livewire/certificates/index.blade.php",
    ]:
        backup(rel)

    print("\n📄 نوشتن فایل‌ها...")
    write("app/Livewire/Certificates/Designer.php", DESIGNER_PHP)
    write("public/js/cert-designer.js", CERT_DESIGNER_JS)
    write("resources/views/livewire/certificates/designer.blade.php", DESIGNER_BLADE)

    print("\n🔧 patch CertRenderer...")
    patch_cert_renderer()

    print("\n🔧 patch Index blade...")
    patch_index_blade()

    print("\n" + "═" * 64)
    print("✅ تمام!")
    print("═" * 64)
    print(f"""
📋 اجرا کنید:

  cd {PROJECT}
  php artisan storage:link
  php artisan optimize:clear
  php artisan view:clear

  ⚠️ سرور رو ببند (Ctrl+C) و دوباره باز کن:
  php artisan serve

مرورگر: Ctrl+Shift+R

🎯 چه چیزی حل شد:
  ✓ JSON داخل x-data → منتقل شد به <script type="application/json">
  ✓ خطای Alpine Expression رفع شد
  ✓ خطای alphabetical → suppress + monkey-patch
  ✓ نمایش تصویر نمونه در canvas
  ✓ QR نمونه و لوگوی نمونه
  ✓ 5 ردیف جدول واقعی با خط جداکننده (قابل جابجایی)
  ✓ دکمه «طراحی پیش‌فرض» → ذخیره برای همه شناسنامه‌ها
  ✓ تصاویر 404 → با storage:link حل می‌شود

🎯 قابلیت‌های جدید:
  ✓ ویرایشگر روی همه elementها → click + drag + resize
  ✓ 5 ردیف جدول قابل جابجایی و تغییر اندازه
  ✓ طرح پیش‌فرض → در CertSetting با کلید global_design ذخیره
  ✓ هر شناسنامه می‌تونه design خودش رو داشته باشه یا از global استفاده کنه
""")

if __name__ == "__main__":
    main()