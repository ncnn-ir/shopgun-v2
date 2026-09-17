# -*- coding: utf-8 -*-
"""ShopGun V2 - Fix designer + Ziggy + storage + Create.php"""
from pathlib import Path
import re
import time
import subprocess
import os

ROOT = Path(r'D:\prodo\shopgun-v2.2')

def write(rel, content):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        # بکاپ با timestamp یکتا
        bak = str(p) + '.bak-' + str(int(time.time()))
        try:
            p.rename(bak)
        except Exception as e:
            print("[WARN] cannot backup: " + str(e))
    p.write_text(content, encoding='utf-8')
    print("[OK] " + rel)


# ═══════════════════════════════════════════════════════════════
# 1. DESIGNER BLADE
# ═══════════════════════════════════════════════════════════════

DESIGNER = r'''<div style="padding:14px" dir="rtl">

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
'''

write('resources/views/livewire/certificates/designer.blade.php', DESIGNER)


# ═══════════════════════════════════════════════════════════════
# 2. PATCH CREATE.PHP — کامل با openModal و resetForm
# ═══════════════════════════════════════════════════════════════

create_path = ROOT / 'app' / 'Livewire' / 'Certificates' / 'Create.php'

if create_path.exists():
    txt = create_path.read_text(encoding='utf-8')

    has_open = 'public function openModal' in txt
    has_listener = "open-cert-form" in txt

    if not has_open or not has_listener:
        # بکاپ
        bak = str(create_path) + '.bak-' + str(int(time.time()))
        create_path.rename(bak)

        # بازنویسی کامل با نسخه کامل
        NEW_CREATE = r'''<?php

namespace App\Livewire\Certificates;

use App\Models\Certificate;
use App\Models\Customer;
use App\Models\Order;
use Livewire\Attributes\On;
use Livewire\Component;
use Livewire\WithFileUploads;

class Create extends Component
{
    use WithFileUploads;

    public int $step = 1;
    public bool $show = false;
    public ?int $editingId = null;

    public string $stoneName   = '';
    public string $stoneEn     = '';
    public string $stoneOrigin = 'نیشابور';
    public string $stoneFlag   = 'ir';
    public string $stoneIcon   = '💠';
    public string $metal       = 'نقره 925';
    public string $metalEn     = 'Silver 925';
    public string $metalCarat  = '925';

    public string $length    = '';
    public string $width     = '';
    public string $weight    = '';
    public string $brilliant = '0';

    public ?int $customerId = null;
    public ?int $orderId    = null;

    public $image = null;

    public array $stoneOptions = [
        ['name' => 'فیروزه عجمی',   'en' => 'Turquoise Ajami',   'origin' => 'نیشابور',   'flag' => 'ir', 'icon' => '💠'],
        ['name' => 'فیروزه شجری',   'en' => 'Turquoise Shajari', 'origin' => 'نیشابور',   'flag' => 'ir', 'icon' => '💠'],
        ['name' => 'عقیق یمانی',    'en' => 'Yemeni Agate',      'origin' => 'یمن',        'flag' => 'ye', 'icon' => '🔴'],
        ['name' => 'عقیق سلیمانی',  'en' => 'Solomoni Agate',    'origin' => 'یمن',        'flag' => 'ye', 'icon' => '❤️'],
        ['name' => 'عقیق شجر',      'en' => 'Dendritic Agate',   'origin' => 'یمن',        'flag' => 'ye', 'icon' => '🌿'],
        ['name' => 'در نجف',        'en' => 'Najaf Pearl',       'origin' => 'عراق',       'flag' => 'iq', 'icon' => '⚪'],
        ['name' => 'الماس',         'en' => 'Diamond',           'origin' => 'آفریقا',     'flag' => 'za', 'icon' => '💎'],
        ['name' => 'یاقوت سرخ',     'en' => 'Ruby',              'origin' => 'میانمار',    'flag' => 'mm', 'icon' => '❤️'],
        ['name' => 'یاقوت کبود',    'en' => 'Blue Sapphire',     'origin' => 'سری‌لانکا',  'flag' => 'lk', 'icon' => '🔵'],
        ['name' => 'زمرد',          'en' => 'Emerald',           'origin' => 'کلمبیا',     'flag' => 'co', 'icon' => '🟢'],
        ['name' => 'توپاز',         'en' => 'Topaz',             'origin' => 'برزیل',      'flag' => 'br', 'icon' => '💛'],
        ['name' => 'آمیتیست',       'en' => 'Amethyst',          'origin' => 'برزیل',      'flag' => 'br', 'icon' => '🟣'],
    ];

    public array $metalOptions = [
        ['name' => 'نقره 925',      'en' => 'Silver 925',      'carat' => '925'],
        ['name' => 'نقره 999',      'en' => 'Fine Silver',     'carat' => '999'],
        ['name' => 'طلا 18K',       'en' => 'Gold 18K',        'carat' => '750'],
        ['name' => 'طلا 21K',       'en' => 'Gold 21K',        'carat' => '875'],
        ['name' => 'طلا 22K',       'en' => 'Gold 22K',        'carat' => '916'],
        ['name' => 'طلا 24K',       'en' => 'Gold 24K',        'carat' => '999'],
        ['name' => 'پلاتین 950',    'en' => 'Platinum 950',    'carat' => '950'],
        ['name' => 'استیل',         'en' => 'Stainless Steel', 'carat' => '-'],
    ];

    #[On('open-cert-form')]
    public function openModal(?int $certId = null): void
    {
        $this->resetForm();
        $this->editingId = $certId;

        if ($certId) {
            $c = Certificate::find($certId);
            if ($c) {
                $this->stoneName   = (string) $c->stone_name;
                $this->stoneEn     = (string) $c->stone_en;
                $this->stoneOrigin = (string) $c->stone_origin;
                $this->stoneFlag   = (string) $c->stone_flag;
                $this->metal       = (string) $c->metal;
                $this->metalEn     = (string) $c->metal_en;
                $this->metalCarat  = (string) $c->metal_carat;
                $this->length      = (string) $c->length;
                $this->width       = (string) $c->width;
                $this->weight      = (string) $c->weight;
                $this->brilliant   = (string) $c->brilliant;
                $this->customerId  = $c->customer_id;
                $this->orderId     = $c->order_id;
            }
        }

        $this->show = true;
        $this->step = 1;
    }

    public function closeModal(): void
    {
        $this->show = false;
        $this->resetForm();
    }

    protected function resetForm(): void
    {
        $this->step = 1;
        $this->stoneName = '';
        $this->stoneEn = '';
        $this->stoneOrigin = 'نیشابور';
        $this->stoneFlag = 'ir';
        $this->stoneIcon = '💠';
        $this->metal = 'نقره 925';
        $this->metalEn = 'Silver 925';
        $this->metalCarat = '925';
        $this->length = '';
        $this->width = '';
        $this->weight = '';
        $this->brilliant = '0';
        $this->customerId = null;
        $this->orderId = null;
        $this->image = null;
        $this->editingId = null;
    }

    public function selectStone(int $index): void
    {
        $s = $this->stoneOptions[$index] ?? null;
        if (!$s) return;
        $this->stoneName   = $s['name'];
        $this->stoneEn     = $s['en'];
        $this->stoneOrigin = $s['origin'];
        $this->stoneFlag   = $s['flag'];
        $this->stoneIcon   = $s['icon'];
    }

    public function selectMetal(int $index): void
    {
        $m = $this->metalOptions[$index] ?? null;
        if (!$m) return;
        $this->metal      = $m['name'];
        $this->metalEn    = $m['en'];
        $this->metalCarat = $m['carat'];
    }

    public function nextStep(): void
    {
        if ($this->step === 1) {
            $this->validate([
                'stoneName' => 'required|string',
                'metal'     => 'required|string',
            ], [
                'stoneName.required' => 'سنگ را انتخاب کن',
                'metal.required'     => 'فلز را انتخاب کن',
            ]);
        }
        if ($this->step === 2) {
            $this->validate([
                'length' => 'required|numeric|min:0',
                'width'  => 'required|numeric|min:0',
                'weight' => 'required|numeric|min:0',
            ], [
                'length.required' => 'طول الزامی است',
                'width.required'  => 'عرض الزامی است',
                'weight.required' => 'وزن الزامی است',
            ]);
        }
        $this->step = min(3, $this->step + 1);
    }

    public function prevStep(): void
    {
        $this->step = max(1, $this->step - 1);
    }

    public function save()
    {
        $this->validate([
            'stoneName' => 'required|string|max:255',
            'metal'     => 'required|string|max:255',
            'length'    => 'nullable|numeric|min:0',
            'width'     => 'nullable|numeric|min:0',
            'weight'    => 'nullable|numeric|min:0',
            'image'     => 'nullable|image|max:5120',
        ]);

        $imagePath = null;
        if ($this->image) {
            $imagePath = $this->image->store('certificates', 'public');
        }

        if ($this->editingId) {
            $cert = Certificate::find($this->editingId);
            $data = [
                'stone_name'   => $this->stoneName,
                'stone_en'     => $this->stoneEn,
                'stone_origin' => $this->stoneOrigin,
                'stone_flag'   => $this->stoneFlag,
                'metal'        => $this->metal,
                'metal_en'     => $this->metalEn,
                'metal_carat'  => $this->metalCarat,
                'length'       => (float) ($this->length ?: 0),
                'width'        => (float) ($this->width ?: 0),
                'weight'       => (float) ($this->weight ?: 0),
                'brilliant'    => (int) ($this->brilliant ?: 0),
                'customer_id'  => $this->customerId,
                'order_id'     => $this->orderId,
            ];
            if ($imagePath) $data['image_path'] = $imagePath;
            $cert->update($data);
            session()->flash('success', "شناسنامه #{$cert->code} ویرایش شد.");
        } else {
            $code = Certificate::generateCode();
            $serial = Certificate::generateSerial($code, $this->stoneEn ?: $this->stoneName);

            $cert = Certificate::create([
                'code'         => $code,
                'serial'       => $serial,
                'stone_name'   => $this->stoneName,
                'stone_en'     => $this->stoneEn,
                'stone_origin' => $this->stoneOrigin,
                'stone_flag'   => $this->stoneFlag,
                'metal'        => $this->metal,
                'metal_en'     => $this->metalEn,
                'metal_carat'  => $this->metalCarat,
                'length'       => (float) ($this->length ?: 0),
                'width'        => (float) ($this->width ?: 0),
                'weight'       => (float) ($this->weight ?: 0),
                'brilliant'    => (int) ($this->brilliant ?: 0),
                'image_path'   => $imagePath,
                'customer_id'  => $this->customerId,
                'order_id'     => $this->orderId,
                'issued_at'    => now(),
            ]);
            session()->flash('success', "شناسنامه #{$code} صادر شد.");
        }

        $this->closeModal();
        $this->dispatch('notify', type: 'success', message: 'شناسنامه ذخیره شد');
        $this->dispatch('cert-saved');
    }

    public function render()
    {
        return view('livewire.certificates.create', [
            'customers' => Customer::orderBy('name')->limit(200)->get(),
            'orders'    => Order::latest('id')->limit(100)->get(),
        ]);
    }
}
'''
        create_path.write_text(NEW_CREATE, encoding='utf-8')
        print("[OK] Create.php بازنویسی شد با openModal + resetForm")
    else:
        print("[SKIP] Create.php قبلاً patch شده")
else:
    print("[WARN] Create.php پیدا نشد")


# ═══════════════════════════════════════════════════════════════
# 3. CERT-CREATE BLADE — فرم داخل modal
# ═══════════════════════════════════════════════════════════════

CREATE_VIEW = r'''<div>
@if($show)
<div style="position:fixed;inset:0;background:rgba(0,0,0,.7);z-index:95;display:flex;align-items:flex-start;justify-content:center;padding:10px;overflow-y:auto"
     wire:key="cert-form-{{ $editingId ?? 'new' }}"
     @keydown.escape.window="$wire.closeModal()">

    <div style="background:#fff;width:100%;max-width:880px;margin:10px auto;border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,.35);overflow:hidden;direction:rtl;font-family:Vazirmatn,Tahoma,sans-serif">

        <div style="background:linear-gradient(135deg,#1a5276,#0d3b5e);color:#fff;padding:14px 18px;display:flex;align-items:center;justify-content:space-between">
            <h2 style="margin:0;font-size:16px;font-weight:700">{{ $editingId ? '✏️ ویرایش شناسنامه' : '💎 شناسنامه جدید' }}</h2>
            <button type="button" wire:click="closeModal" style="width:32px;height:32px;border-radius:50%;background:rgba(255,255,255,.2);color:#fff;border:none;cursor:pointer;font-size:15px">X</button>
        </div>

        <div style="padding:16px;max-height:calc(100vh - 180px);overflow-y:auto">

            {{-- Steps --}}
            <div style="display:flex;justify-content:space-between;margin-bottom:24px;position:relative;padding:0 20px">
                <div style="position:absolute;top:18px;left:60px;right:60px;height:2px;background:#e2e8f0;z-index:0"></div>
                @foreach([1 => 'سنگ و فلز', 2 => 'مشخصات', 3 => 'تصویر'] as $num => $label)
                    <div style="position:relative;z-index:1;display:flex;flex-direction:column;align-items:center;flex:1">
                        <div style="width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;
                            background:{{ $step >= $num ? 'linear-gradient(135deg,#1a5276,#0d3b5e)' : '#f1f5f9' }};
                            color:{{ $step >= $num ? '#fff' : '#64748b' }};">
                            {{ $num }}
                        </div>
                        <div style="font-size:11px;font-weight:700;margin-top:6px;color:{{ $step >= $num ? '#1a5276' : '#94a3b8' }}">{{ $label }}</div>
                    </div>
                @endforeach
            </div>

            @if($step === 1)
                <div style="margin-bottom:20px">
                    <h3 style="font-size:14px;font-weight:700;color:#1a5276;margin:0 0 12px">💎 سنگ را انتخاب کن</h3>
                    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:8px">
                        @foreach($stoneOptions as $i => $s)
                            <button type="button" wire:click="selectStone({{ $i }})"
                                    style="padding:10px 4px;border:2px solid {{ $stoneName === $s['name'] ? '#c9a84c' : '#e2e8f0' }};background:{{ $stoneName === $s['name'] ? '#fef3c7' : '#fff' }};border-radius:10px;cursor:pointer">
                                <div style="font-size:26px;margin-bottom:4px">{{ $s['icon'] }}</div>
                                <div style="font-size:11px;font-weight:700;color:#1e293b">{{ $s['name'] }}</div>
                            </button>
                        @endforeach
                    </div>
                </div>

                <div>
                    <h3 style="font-size:14px;font-weight:700;color:#1a5276;margin:0 0 12px">⚙️ فلز را انتخاب کن</h3>
                    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(100px,1fr));gap:8px">
                        @foreach($metalOptions as $i => $m)
                            <button type="button" wire:click="selectMetal({{ $i }})"
                                    style="padding:12px 6px;border:2px solid {{ $metal === $m['name'] ? '#c9a84c' : '#e2e8f0' }};background:{{ $metal === $m['name'] ? '#fef3c7' : '#fff' }};border-radius:10px;cursor:pointer;font-weight:700;font-size:12px;color:#1e293b">
                                {{ $m['name'] }}
                            </button>
                        @endforeach
                    </div>
                </div>
            @endif

            @if($step === 2)
                <div style="background:linear-gradient(135deg,#fef3c7,#fde68a);padding:10px 14px;border-radius:10px;margin-bottom:16px;font-size:13px;font-weight:700;color:#78350f">
                    💎 {{ $stoneName }} — ⚙️ {{ $metal }}
                </div>

                <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:14px">
                    <div>
                        <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">طول (mm)</label>
                        <input type="number" step="0.01" wire:model="length" dir="ltr"
                               style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-family:monospace;font-size:13px;background:#f8fafc;box-sizing:border-box;text-align:center">
                    </div>
                    <div>
                        <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">عرض (mm)</label>
                        <input type="number" step="0.01" wire:model="width" dir="ltr"
                               style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-family:monospace;font-size:13px;background:#f8fafc;box-sizing:border-box;text-align:center">
                    </div>
                    <div>
                        <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">وزن (گرم)</label>
                        <input type="number" step="0.001" wire:model="weight" dir="ltr"
                               style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-family:monospace;font-size:13px;background:#f8fafc;box-sizing:border-box;text-align:center">
                    </div>
                    <div>
                        <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">عیار</label>
                        <input type="text" value="{{ $metalCarat }}" readonly dir="ltr"
                               style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-family:monospace;font-size:13px;background:#e2e8f0;box-sizing:border-box;text-align:center">
                    </div>
                    <div>
                        <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">برلیان</label>
                        <input type="number" wire:model="brilliant" dir="ltr"
                               style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-family:monospace;font-size:13px;background:#f8fafc;box-sizing:border-box;text-align:center">
                    </div>
                </div>
            @endif

            @if($step === 3)
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:16px">
                    <div>
                        <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">👤 مشتری (اختیاری)</label>
                        <select wire:model="customerId" style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:13px;background:#f8fafc;box-sizing:border-box">
                            <option value="">— بدون مشتری —</option>
                            @foreach($customers as $c)
                                <option value="{{ $c->id }}">{{ $c->name }} — {{ $c->phone }}</option>
                            @endforeach
                        </select>
                    </div>
                    <div>
                        <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">📦 سفارش (اختیاری)</label>
                        <select wire:model="orderId" style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:13px;background:#f8fafc;box-sizing:border-box">
                            <option value="">— بدون سفارش —</option>
                            @foreach($orders as $o)
                                <option value="{{ $o->id }}">#{{ $o->order_number }}</option>
                            @endforeach
                        </select>
                    </div>
                </div>

                <div>
                    <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">📸 تصویر محصول</label>
                    <input type="file" wire:model="image" accept="image/*"
                           style="width:100%;padding:8px;border:1.5px dashed #cbd5e1;border-radius:8px;background:#f8fafc;box-sizing:border-box">
                    @if($image)
                        <div style="margin-top:10px"><img src="{{ $image->temporaryUrl() }}" style="max-width:120px;border-radius:10px;border:2px solid #c9a84c"></div>
                    @endif
                </div>
            @endif
        </div>

        <div style="padding:12px 18px;background:#f8fafc;border-top:1px solid #e2e8f0;display:flex;justify-content:space-between;gap:8px">
            <div>
                @if($step > 1)
                    <button type="button" wire:click="prevStep"
                            style="padding:9px 18px;background:#f1f5f9;color:#475569;border:1.5px solid #cbd5e1;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">→ قبل</button>
                @endif
            </div>
            <div style="display:flex;gap:8px">
                <button type="button" wire:click="closeModal"
                        style="padding:9px 18px;background:#fff;color:#475569;border:1.5px solid #cbd5e1;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">انصراف</button>
                @if($step < 3)
                    <button type="button" wire:click="nextStep"
                            style="padding:9px 22px;background:linear-gradient(135deg,#1a5276,#0d3b5e);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">بعد ←</button>
                @else
                    <button type="button" wire:click="save" wire:loading.attr="disabled"
                            style="padding:9px 22px;background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">
                        <span wire:loading.remove wire:target="save">✓ ذخیره</span>
                        <span wire:loading wire:target="save">⏳...</span>
                    </button>
                @endif
            </div>
        </div>
    </div>
</div>
@endif
</div>
'''

write('resources/views/livewire/certificates/create.blade.php', CREATE_VIEW)


# ═══════════════════════════════════════════════════════════════
# 4. CERT INDEX — دکمه popup
# ═══════════════════════════════════════════════════════════════

cert_index = ROOT / 'resources' / 'views' / 'livewire' / 'certificates' / 'index.blade.php'
if cert_index.exists():
    txt = cert_index.read_text(encoding='utf-8')
    txt = txt.replace(
        '<a href="{{ route(\'certificates.create\') }}" wire:navigate class="btn btn-primary">',
        '<button onclick="Livewire.dispatch(\'open-cert-form\')" class="btn btn-primary">'
    )
    txt = txt.replace(
        '➕ شناسنامه جدید</a>',
        '➕ شناسنامه جدید</button>'
    )
    cert_index.write_text(txt, encoding='utf-8')
    print("[OK] certificates/index.blade.php - دکمه popup")


# ═══════════════════════════════════════════════════════════════
# 5. LAYOUT — حذف cert-designer.js، حذف @routes، اضافه modal
# ═══════════════════════════════════════════════════════════════

layout = ROOT / 'resources' / 'views' / 'components' / 'layouts' / 'app.blade.php'
if layout.exists():
    txt = layout.read_text(encoding='utf-8')

    # حذف cert-designer.js
    txt = re.sub(
        r'<script[^>]*cert-designer\.js[^>]*></script>\s*',
        '',
        txt
    )

    # حذف @routes duplicate
    txt = re.sub(r'@routes\s*', '', txt)

    # اضافه کردن cert modal به layout اگه نبود
    if 'certificates.create' not in txt and '<livewire:certificates.create' not in txt:
        if '<livewire:orders.form-modal' in txt:
            txt = txt.replace(
                '<livewire:orders.form-modal',
                '<livewire:certificates.create :key="\'cfm\'" />\n    <livewire:orders.form-modal',
                1
            )
            print("[OK] layout: cert modal اضافه شد")

    layout.write_text(txt, encoding='utf-8')
    print("[OK] layout: clean")


# ═══════════════════════════════════════════════════════════════
# 6. STORAGE LINK
# ═══════════════════════════════════════════════════════════════

os.chdir(str(ROOT))

# چک کن public/storage وجود داره یا نه
link = ROOT / 'public' / 'storage'

if link.exists() and not link.is_symlink():
    print("[INFO] public/storage از قبل وجود دارد (فایل/فولدر عادی)")
elif link.exists() and link.is_symlink():
    try:
        link.unlink()
        print("[OK] storage link قدیمی حذف شد")
    except Exception as e:
        print("[WARN] " + str(e))

try:
    r = subprocess.run(['php', 'artisan', 'storage:link'], capture_output=True, text=True, shell=False)
    if r.returncode == 0:
        print("[OK] storage:link اجرا شد")
    else:
        print("[WARN] " + (r.stderr or r.stdout or 'unknown'))
except Exception as e:
    print("[WARN] " + str(e))


# ═══════════════════════════════════════════════════════════════
# DONE
# ═══════════════════════════════════════════════════════════════

print()
print("=" * 60)
print("DONE")
print("=" * 60)
print()
print("Run:")
print("  php artisan view:clear")
print("  php artisan optimize:clear")
print("  php artisan serve")