#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix ShopGun Cert — نمایش + PNG + چاپ + Designer"""
import shutil
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
# ۱) CertRenderer — نسخه جدید
# ═══════════════════════════════════════════════════════════════
CERT_RENDERER = r'''<?php

namespace App\Services;

use App\Models\Certificate;
use App\Support\CertConfig;
use App\Support\PersianNumber;

class CertRenderer
{
    /**
     * ★ HTML فقط کارت (بدون DOCTYPE/html/head) — برای نمایش مستقیم در صفحه
     */
    public static function renderCard(Certificate $cert): string
    {
        return self::buildCardInner($cert, false);
    }

    /**
     * ★ HTML کامل با DOCTYPE — برای iframe/چاپ
     */
    public static function renderHtml(Certificate $cert, array $opts = []): string
    {
        $card = self::buildCardInner($cert, true);
        $css  = self::inlineCss();

        return '<!DOCTYPE html><html lang="fa" dir="rtl"><head><meta charset="UTF-8">'
            . '<link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">'
            . '<link href="https://fonts.googleapis.com/css2?family=Great+Vibes&family=Playfair+Display:wght@400;700&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">'
            . '<style>' . $css . '</style></head><body style="margin:0;padding:0;background:transparent;">'
            . $card
            . '</body></html>';
    }

    /**
     * ★ فقط بدنه کارت (با یا بدون <style>)
     */
    protected static function buildCardInner(Certificate $cert, bool $includeStyle): string
    {
        $sizes = CertConfig::sizes();
        $assets = CertConfig::assets();
        $hide = CertConfig::hideDesc();

        $cw    = (float) ($sizes['width']  ?? 6.5);
        $ch    = (float) ($sizes['height'] ?? 6.5);
        $pxW   = (int) round($cw * 96 / 2.54);
        $pxH   = (int) round($ch * 96 / 2.54);
        $scale = $cw / 6.5;

        $imgW  = (int) round(($sizes['img_w']   ?? 120) * $scale);
        $imgH  = (int) round(($sizes['img_h']   ?? 120) * $scale);
        $qrS   = (int) round(($sizes['qr_size'] ?? 40)  * $scale);

        $code    = e($cert->code);
        $serial  = e($cert->serial ?? '');
        $stoneEn = e($cert->stone_en ?? '');
        $metalEn = e($cert->metal_en ?? $cert->metal ?? '');
        $carat   = e($cert->metal_carat ?? '');
        $origin  = e($cert->stone_origin ?? '');
        $flag    = $cert->stone_flag ?? '';
        $flagUrl = $flag ? 'https://flagcdn.com/w40/' . strtolower($flag) . '.png' : '';
        $length  = e($cert->length_clean ?? '0');
        $widthS  = e($cert->width_clean  ?? '0');
        $weight  = e($cert->weight_clean ?? '0');
        $brill   = PersianNumber::toFa($cert->brilliant_clean ?? '0');
        $qrUrl   = $cert->qr_url;

        // ★ تصویر محصول
        $imgSrc = '';
        if (!empty($cert->image_url))   $imgSrc = $cert->image_url;
        elseif (!empty($cert->image_path)) $imgSrc = asset('storage/' . $cert->image_path);

        $imgInner = $imgSrc
            ? '<img src="' . e($imgSrc) . '" alt="" crossorigin="anonymous">'
            : '<div style="display:flex;align-items:center;justify-content:center;width:100%;height:100%;font-size:32px;">💎</div>';

        // پس‌زمینه
        $bgStyle = !empty($assets['bg_image'])
            ? 'background-image:url(\'' . e($assets['bg_image']) . '\');'
            : '';

        // لوگو
        $logoHtml = !empty($assets['logo_image'])
            ? '<div class="ico"><img src="' . e($assets['logo_image']) . '" alt=""></div>'
            : '<div class="ico"><span>💎</span></div>';

        // توضیحات
        $descHtml = '';
        if (!$hide) {
            $descHtml = !empty($assets['desc_image'])
                ? '<img src="' . e($assets['desc_image']) . '" alt="">'
                : '<div class="cert-auth-text">This certificate is only for authenticity of purchased product.</div>';
        }

        $flagHtml = $flagUrl
            ? '<img src="' . e($flagUrl) . '" style="width:14px;vertical-align:middle;border-radius:2px;" alt="">'
            : '';

        // ★ کارت
        $card = <<<CARD
<div class="certificate" data-cert-code="{$code}" style="width:{$pxW}px;height:{$pxH}px;">
  <div class="cert-bg-layer" style="{$bgStyle}"></div>
  <div class="cert-main">
    <div class="cert-top-section">
      <div class="cert-right-text">
        <div class="cert-title-script">Certificate</div>
        <div class="cert-subtitle-script">Quality Guarantee</div>
        <div class="cert-desc-area">{$descHtml}</div>
        <div class="cert-sig-block">
          <div class="cert-sig-line">Quality Guarantee</div>
          <div class="cert-sig-label">تضمین کیفیت</div>
        </div>
      </div>
      <div class="cert-img-frame-wrap" style="width:{$imgW}px;height:{$imgH}px;">
        <div class="cert-img-frame">{$imgInner}</div>
        <div class="cert-serial-balloon">{$serial}</div>
      </div>
    </div>
    <div class="cert-qr-panel">
      <div class="cert-logo-mini">{$logoHtml}</div>
      <div class="cert-qr-wrap">
        <div class="cert-qr-url">mashahirid.ir/{$code}</div>
        <div class="cert-qr-inner">
          <div class="cert-qr-box" style="width:{$qrS}px;height:{$qrS}px;">
            <img src="{$qrUrl}" alt="QR">
          </div>
          <div class="cert-code-inline">
            <span class="lbl">CODE</span>
            <span class="val">{$code}</span>
          </div>
        </div>
      </div>
    </div>
    <div class="cert-table-wrap">
      <table class="cert-bottom-table">
        <colgroup><col style="width:25%"><col style="width:25%"><col style="width:25%"><col style="width:25%"></colgroup>
        <tr>
          <td class="tbl-label">Stone</td>
          <td class="tbl-value">{$stoneEn}</td>
          <td class="tbl-label">Metal</td>
          <td class="tbl-value">{$metalEn} <span class="unit">{$carat}</span></td>
        </tr>
        <tr>
          <td class="tbl-label">Originality</td>
          <td class="tbl-value">{$origin} {$flagHtml}</td>
          <td class="tbl-label">Stone S</td>
          <td class="tbl-value">{$length}*{$widthS} <span class="unit">mm</span></td>
        </tr>
        <tr>
          <td class="tbl-label">Brillant</td>
          <td class="tbl-value">{$brill}</td>
          <td class="tbl-label">Total W</td>
          <td class="tbl-value">{$weight} <span class="unit">gr</span></td>
        </tr>
      </table>
    </div>
  </div>
</div>
CARD;

        if ($includeStyle) {
            $css = self::inlineCss();
            return '<style>' . $css . '</style>' . $card;
        }
        return $card;
    }

    /**
     * ★ برای چاپ A4
     */
    public static function renderBatchHtml(array $certs, int $cols = 3): string
    {
        $sizes = CertConfig::sizes();
        $cw    = (float) ($sizes['width']  ?? 6.5);
        $ch    = (float) ($sizes['height'] ?? 6.5);
        $gap   = $cols === 1 ? 0 : round((210 - ($cols * $cw) - 6) / max(1, $cols - 1), 2);

        $cards = '';
        foreach ($certs as $cert) {
            $cards .= '<div class="batch-card">' . self::buildCardInner($cert, false) . '</div>';
        }

        $css = self::inlineCss();

        return '<!DOCTYPE html><html lang="fa" dir="rtl"><head><meta charset="UTF-8">'
            . '<link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">'
            . '<link href="https://fonts.googleapis.com/css2?family=Great+Vibes&family=Playfair+Display:wght@400;700&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">'
            . '<style>' . $css . '</style>'
            . '<style>'
            . '@page{size:A4 portrait;margin:3mm}'
            . '*{box-sizing:border-box;margin:0;padding:0;-webkit-print-color-adjust:exact;print-color-adjust:exact}'
            . 'html,body{background:#fff;margin:0!important;padding:0!important;width:210mm}'
            . '.cert-print-grid{display:grid;grid-template-columns:repeat(' . $cols . ',' . $cw . 'cm);'
            . 'column-gap:' . $gap . 'cm;row-gap:2mm;justify-content:center;align-content:start;padding:0;width:100%}'
            . '.batch-card .certificate{width:' . $cw . 'cm!important;height:' . $ch . 'cm!important;'
            . 'min-width:' . $cw . 'cm!important;min-height:' . $ch . 'cm!important;'
            . 'max-width:' . $cw . 'cm!important;max-height:' . $ch . 'cm!important;'
            . 'page-break-inside:avoid;break-inside:avoid;box-shadow:none!important;'
            . 'transform:none!important;margin:0!important;padding:0!important}'
            . '.batch-card .certificate .cert-main{overflow:hidden!important;height:100%!important;width:100%!important}'
            . '</style>'
            . '</head><body><div class="cert-print-grid">' . $cards . '</div></body></html>';
    }

    /**
     * ★ CSS داخلی — همه با .certificate scoped
     */
    protected static function inlineCss(): string
    {
        return <<<CSS
.certificate{background:#fffef9;color:#2c3e50;position:relative;overflow:hidden;font-family:'Inter','Vazirmatn',Tahoma,sans-serif;font-size:11px;border:1px solid #999;border-radius:10px;box-sizing:border-box;line-height:1.2}
.certificate *{box-sizing:border-box}
.certificate .cert-bg-layer{position:absolute;inset:0;background-size:cover;background-position:center;background-repeat:no-repeat;z-index:0;opacity:.12;border-radius:10px;pointer-events:none}
.certificate .cert-main{position:relative;z-index:3;width:100%;height:100%;padding:8px;display:flex;flex-direction:column;box-sizing:border-box;overflow:visible}
.certificate .cert-top-section{display:flex;gap:8px;margin-bottom:4px;overflow:hidden;flex:0 0 auto}
.certificate .cert-right-text{flex:1 1 auto;min-width:60px;display:flex;flex-direction:column;padding:2px 0 2px 4px;overflow:hidden;text-align:right}
.certificate .cert-title-script{font-family:'Great Vibes',cursive;color:#6b4423;line-height:1;text-align:right;font-size:20px}
.certificate .cert-subtitle-script{font-family:'Playfair Display',serif;font-size:8px;color:#6b4423;text-align:right;margin-bottom:6px;font-style:italic}
.certificate .cert-desc-area{flex:1 1 auto;text-align:right;overflow:hidden;display:flex;align-items:center;justify-content:flex-end;min-height:0}
.certificate .cert-desc-area img{max-width:100%;max-height:100%;object-fit:contain;margin:auto;display:block}
.certificate .cert-auth-text{font-family:'Playfair Display',serif;color:#6b4423;line-height:1.5;text-align:right;font-size:7px}
.certificate .cert-sig-block{text-align:right;margin-top:4px;flex-shrink:0}
.certificate .cert-sig-line{font-family:'Great Vibes',cursive;font-size:12px;color:#6b4423;border-bottom:1px solid #6b4423;display:inline-block;padding:0 6px 2px;min-width:70px}
.certificate .cert-sig-label{font-family:'Playfair Display',serif;font-size:6px;color:#999;margin-top:2px}
.certificate .cert-img-frame-wrap{flex:0 0 auto;position:relative;padding:4px;border:1px solid #b8860b;border-radius:8px;background:#fff;box-sizing:border-box;max-height:100%;overflow:hidden;align-self:flex-start}
.certificate .cert-img-frame-wrap::before{content:'';position:absolute;inset:2px;border:1px solid rgba(184,134,11,.4);border-radius:6px;pointer-events:none}
.certificate .cert-img-frame{width:100%;height:100%;border:1.5px solid #b8860b;border-radius:6px;overflow:hidden;background:#fff;position:relative}
.certificate .cert-img-frame img{width:100%;height:100%;object-fit:contain;display:block}
.certificate .cert-serial-balloon{position:absolute;bottom:6px;left:50%;transform:translateX(-50%);background:rgba(0,0,0,.55);color:#fff;font-family:monospace;font-size:5px;font-weight:700;padding:2px 6px;border-radius:8px;white-space:nowrap;border:1px solid rgba(255,255,255,.25);pointer-events:none;z-index:2}
.certificate .cert-qr-panel{display:flex;gap:6px;align-items:center;padding:4px 2px;margin-bottom:4px;justify-content:flex-end;flex-wrap:nowrap;overflow:visible;flex:0 0 auto}
.certificate .cert-qr-wrap{display:flex;flex-direction:column;align-items:center;background:#fff;border:1px solid #0d5c63;border-radius:6px;padding:3px 4px;min-width:30px;box-sizing:border-box;flex-shrink:0}
.certificate .cert-qr-url{color:#1a5276;font-weight:600;margin-bottom:2px;min-width:15px;font-size:6px;direction:ltr}
.certificate .cert-qr-inner{display:flex;gap:6px;align-items:center;overflow:hidden}
.certificate .cert-qr-box{background:#fff;border-radius:3px;overflow:hidden;flex-shrink:0;box-sizing:border-box}
.certificate .cert-qr-box img{width:100%;height:100%;object-fit:contain;display:block}
.certificate .cert-code-inline{display:flex;flex-direction:column;align-items:flex-start;gap:2px;min-width:30px}
.certificate .cert-code-inline .lbl{font-size:6px;color:#7f8c8d;text-transform:uppercase}
.certificate .cert-code-inline .val{font-family:monospace;font-weight:700;color:#1a5276;letter-spacing:.8px;font-size:11px}
.certificate .cert-logo-mini{display:flex;align-items:center;gap:4px;margin-right:auto;flex-wrap:nowrap;min-width:30px;max-width:50%;overflow:hidden}
.certificate .cert-logo-mini .ico{border:none;border-radius:4px;display:flex;align-items:center;justify-content:center;overflow:hidden;padding:0;background:transparent;flex-shrink:0;box-sizing:border-box;font-size:22px}
.certificate .cert-logo-mini .ico img{width:100%;height:100%;object-fit:contain;display:block}
.certificate .cert-table-wrap{width:100%;flex:0 0 auto;border-radius:8px;overflow:hidden;border:1.5px solid #0d5c63;background:#fff;box-sizing:border-box;max-width:100%}
.certificate .cert-bottom-table{width:100%;border-collapse:collapse;background:transparent;font-family:'Inter','Vazirmatn',sans-serif;table-layout:fixed;box-sizing:border-box}
.certificate .cert-bottom-table td{border:1px solid #7fbfc4;vertical-align:middle;line-height:1.2;word-break:break-word;padding:2px 3px;box-sizing:border-box;overflow:hidden;text-overflow:ellipsis}
.certificate .cert-bottom-table .tbl-label{background:#0d5c63;color:#e0f7f8;font-weight:700;text-align:right;font-size:8px}
.certificate .cert-bottom-table .tbl-value{background:#fff;color:#2c3e50;font-weight:600;text-align:right;font-size:8px}
.certificate .cert-bottom-table .unit{float:left;font-size:6px;color:#888;font-weight:400}
CSS;
    }
}
'''

# ═══════════════════════════════════════════════════════════════
# ۲) Show.php
# ═══════════════════════════════════════════════════════════════
SHOW_PHP = r'''<?php

namespace App\Livewire\Certificates;

use App\Models\Certificate;
use App\Services\CertRenderer;
use App\Support\CertConfig;
use Livewire\Component;

class Show extends Component
{
    public Certificate $certificate;
    public string $cardHtml = '';     // ★ فقط کارت (بدون iframe)
    public string $batchHtml = '';    // ★ برای چاپ

    public function mount(Certificate $certificate): void
    {
        $this->certificate = $certificate->load(['customer', 'order']);
        $this->cardHtml  = CertRenderer::renderCard($this->certificate);
        $this->batchHtml = CertRenderer::renderBatchHtml([$this->certificate]);
    }

    public function delete()
    {
        $code = $this->certificate->code;
        $this->certificate->delete();
        session()->flash('success', "شناسنامه #{$code} حذف شد.");
        return redirect()->route('certificates.index');
    }

    public function render()
    {
        return view('livewire.certificates.show', [
            'sizes' => CertConfig::sizes(),
        ])->layout('components.layouts.app');
    }
}
'''

# ═══════════════════════════════════════════════════════════════
# ۳) ViewModal.php
# ═══════════════════════════════════════════════════════════════
VIEW_MODAL_PHP = r'''<?php

namespace App\Livewire\Certificates;

use App\Models\Certificate;
use App\Services\CertRenderer;
use Livewire\Component;

class ViewModal extends Component
{
    public bool $show = false;
    public ?int $certId = null;
    public ?Certificate $certificate = null;
    public string $cardHtml = '';
    public string $batchHtml = '';

    protected $listeners = ['open-cert-view' => 'open'];

    public function open(int $certId): void
    {
        $this->certId = $certId;
        $this->certificate = Certificate::with(['customer', 'order'])->find($certId);

        if ($this->certificate) {
            $this->cardHtml  = CertRenderer::renderCard($this->certificate);
            $this->batchHtml = CertRenderer::renderBatchHtml([$this->certificate]);
        }
        $this->show = true;
    }

    public function close(): void
    {
        $this->show = false;
        $this->certId = null;
        $this->certificate = null;
        $this->cardHtml = '';
        $this->batchHtml = '';
    }

    public function render()
    {
        return view('livewire.certificates.view-modal');
    }
}
'''

# ═══════════════════════════════════════════════════════════════
# ۴) Designer.php — با #[On]
# ═══════════════════════════════════════════════════════════════
DESIGNER_PHP = r'''<?php

namespace App\Livewire\Certificates;

use App\Models\Certificate;
use Livewire\Attributes\On;
use Livewire\Component;

class Designer extends Component
{
    public ?Certificate $certificate = null;
    public string $designJson = '';
    public string $statusMessage = '';

    public function mount(?Certificate $certificate = null): void
    {
        if ($certificate && $certificate->exists) {
            $this->certificate = $certificate;
        } else {
            $this->certificate = Certificate::query()->latest()->first();
        }

        if ($this->certificate && !empty($this->certificate->design_data)) {
            $this->designJson = json_encode(
                $this->certificate->design_data,
                JSON_UNESCAPED_UNICODE
            );
        } else {
            $this->designJson = 'null';
        }
    }

    /**
     * ★ صدا زده می‌شود از JS با Livewire.dispatch
     */
    #[On('designer-save')]
    public function saveDesign($json = null): void
    {
        // اگر json به صورت رشته اومد
        if (is_string($json)) {
            $design = json_decode($json, true);
        } elseif (is_array($json)) {
            $design = $json;
        } else {
            $this->statusMessage = 'داده نامعتبر';
            $this->dispatch('notify', type: 'error', message: 'داده نامعتبر');
            return;
        }

        if (!is_array($design)) {
            $this->statusMessage = 'JSON نامعتبر';
            $this->dispatch('notify', type: 'error', message: 'JSON نامعتبر');
            return;
        }

        if ($this->certificate) {
            $this->certificate->update(['design_data' => $design]);
            $this->designJson = is_string($json) ? $json : json_encode($json, JSON_UNESCAPED_UNICODE);
            $this->statusMessage = 'ذخیره شد ✅';
            $this->dispatch('notify', type: 'success', message: 'طراحی ذخیره شد ✅');
        } else {
            $this->dispatch('notify', type: 'error', message: 'شناسنامه‌ای وجود ندارد');
        }
    }

    public function render()
    {
        return view('livewire.certificates.designer')
            ->layout('components.layouts.app');
    }
}
'''

# ═══════════════════════════════════════════════════════════════
# ۵) cert-designer.js — با Livewire.dispatch
# ═══════════════════════════════════════════════════════════════
CERT_DESIGNER_JS = r"""(function () {
  'use strict';
  var canvas = null;
  var currentCertId = null;
  var SIZE = 600;

  function loadFabric(cb) {
    if (typeof fabric !== 'undefined') { cb(); return; }
    var s = document.createElement('script');
    s.src = 'https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.0/fabric.min.js';
    s.onload = cb;
    s.onerror = function () { console.error('fabric.js load failed'); };
    document.head.appendChild(s);
  }

  function init(certId, designData) {
    currentCertId = certId;
    loadFabric(function () {
      var el = document.getElementById('cert-fabric-canvas');
      if (!el) return;
      if (canvas) { canvas.dispose(); canvas = null; }

      canvas = new fabric.Canvas('cert-fabric-canvas', {
        width: SIZE, height: SIZE, backgroundColor: '#fffef9'
      });

      if (designData && designData.objects && designData.objects.length) {
        canvas.loadFromJSON(designData, function () { canvas.renderAll(); bind(); });
      } else {
        buildDefault();
        bind();
      }
    });
  }

  function buildDefault() {
    canvas.add(new fabric.IText('Certificate', {
      left: 300, top: 60, fontSize: 28,
      fontFamily: 'Great Vibes', fill: '#6b4423', originX: 'center'
    }));
    canvas.add(new fabric.IText('Quality Guarantee', {
      left: 300, top: 100, fontSize: 11,
      fontFamily: 'Playfair Display', fontStyle: 'italic',
      fill: '#6b4423', originX: 'center'
    }));

    [
      { t: '{code}',      y: 160, s: 14, c: '#1a5276', w: 'bold' },
      { t: '{stoneEn}',   y: 200, s: 12, c: '#2c3e50' },
      { t: '{metalEn}',   y: 225, s: 12, c: '#2c3e50' },
      { t: '{length}*{width}', y: 250, s: 12, c: '#2c3e50' },
      { t: '{weight} gr', y: 275, s: 12, c: '#2c3e50' }
    ].forEach(function (v) {
      canvas.add(new fabric.IText(v.t, {
        left: 300, top: v.y, fontSize: v.s, fontFamily: 'Inter',
        fill: v.c, fontWeight: v.w || 'normal', originX: 'center'
      }));
    });

    canvas.add(new fabric.Rect({
      left: 60, top: 440, width: 80, height: 80,
      fill: '#fff', stroke: '#0d5c63', strokeWidth: 1.5, rx: 6, ry: 6
    }));
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
    var isText = a.type === 'i-text' || a.type === 'text';
    var isImg = a.type === 'image';
    var isRect = a.type === 'rect';

    var h = '<div style="font-size:11px;font-weight:700;color:#0d5c63;margin-bottom:10px;border-bottom:1px solid #ddd;padding-bottom:6px;">' + a.type.toUpperCase() + '</div>';
    h += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">';
    h += '<label style="font-size:11px;">X <input type="number" id="prop-x" value="' + Math.round(a.left) + '" style="width:100%;padding:4px;border:1px solid #ccc;border-radius:4px;"></label>';
    h += '<label style="font-size:11px;">Y <input type="number" id="prop-y" value="' + Math.round(a.top) + '" style="width:100%;padding:4px;border:1px solid #ccc;border-radius:4px;"></label>';
    h += '</div>';

    if (isText) {
      h += '<label style="font-size:11px;display:block;margin-top:6px;">متن<input type="text" id="prop-text" value="' + (a.text || '').replace(/"/g, '&quot;') + '" style="width:100%;padding:4px;border:1px solid #ccc;border-radius:4px;font-family:monospace;"></label>';
      h += '<label style="font-size:11px;display:block;margin-top:6px;">فونت<input type="number" id="prop-fs" value="' + (a.fontSize || 12) + '" style="width:100%;padding:4px;border:1px solid #ccc;border-radius:4px;"></label>';
      h += '<label style="font-size:11px;display:block;margin-top:6px;">رنگ<input type="color" id="prop-fill" value="' + (a.fill || '#000000') + '" style="width:100%;height:30px;padding:2px;border:1px solid #ccc;border-radius:4px;"></label>';
    }
    if (isRect || isImg) {
      h += '<label style="font-size:11px;display:block;margin-top:6px;">عرض<input type="number" id="prop-w" value="' + Math.round(a.width * (a.scaleX || 1)) + '" style="width:100%;padding:4px;border:1px solid #ccc;border-radius:4px;"></label>';
      h += '<label style="font-size:11px;display:block;margin-top:6px;">ارتفاع<input type="number" id="prop-h" value="' + Math.round(a.height * (a.scaleY || 1)) + '" style="width:100%;padding:4px;border:1px solid #ccc;border-radius:4px;"></label>';
    }
    h += '<button onclick="window.ShopGunDesigner.applyProps()" style="width:100%;margin-top:10px;padding:6px;background:#27ae60;color:#fff;border:none;border-radius:6px;cursor:pointer;font-weight:700;">اعمال</button>';
    h += '<button onclick="window.ShopGunDesigner.deleteActive()" style="width:100%;margin-top:6px;padding:6px;background:#e74c3c;color:#fff;border:none;border-radius:6px;cursor:pointer;font-weight:700;">حذف</button>';
    p.innerHTML = h;
  }

  function applyProps() {
    var a = canvas.getActiveObject(); if (!a) return;
    var x = parseFloat(document.getElementById('prop-x').value);
    var y = parseFloat(document.getElementById('prop-y').value);
    if (!isNaN(x)) a.set('left', x);
    if (!isNaN(y)) a.set('top', y);
    var t = document.getElementById('prop-text'); if (t) a.set('text', t.value);
    var fs = document.getElementById('prop-fs'); if (fs) a.set('fontSize', parseFloat(fs.value));
    var f = document.getElementById('prop-fill'); if (f) a.set('fill', f.value);
    var w = document.getElementById('prop-w'), h = document.getElementById('prop-h');
    if (w && h) {
      a.set('width', parseFloat(w.value) / (a.scaleX || 1));
      a.set('height', parseFloat(h.value) / (a.scaleY || 1));
    }
    a.setCoords(); canvas.renderAll();
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

  /**
   * ★ ذخیره — از Livewire.dispatch استفاده می‌کند
   */
  function saveDesign() {
    if (!canvas || !currentCertId) {
      alert('Canvas آماده نیست');
      return;
    }
    var json = canvas.toJSON(['selectable', 'evented']);
    var jsonStr = JSON.stringify(json);

    if (window.Livewire && window.Livewire.dispatch) {
      try {
        window.Livewire.dispatch('designer-save', { json: jsonStr });
        showSaveToast();
        return;
      } catch (e) {
        console.warn('dispatch failed:', e);
      }
    }

    // fallback: fetch POST
    fetch('/certificates/' + currentCertId + '/design', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-TOKEN': (document.querySelector('meta[name="csrf-token"]') || {}).content || ''
      },
      body: JSON.stringify({ design_data: json })
    }).then(function (r) { return r.json(); })
      .then(function () { showSaveToast(); })
      .catch(function (e) {
        alert('خطا در ذخیره: ' + e.message);
      });
  }

  function showSaveToast() {
    var t = document.createElement('div');
    t.style.cssText = 'position:fixed;bottom:20px;right:20px;background:#27ae60;color:#fff;padding:12px 20px;border-radius:10px;font-weight:700;z-index:9999;box-shadow:0 4px 12px rgba(0,0,0,.3);';
    t.textContent = '✅ طراحی ذخیره شد';
    document.body.appendChild(t);
    setTimeout(function () { t.remove(); }, 2000);
  }

  window.ShopGunDesigner = {
    init: init, applyProps: applyProps, deleteActive: deleteActive,
    addText: addText, addRect: addRect, saveDesign: saveDesign,
    getCanvas: function () { return canvas; }
  };
})();
"""

# ═══════════════════════════════════════════════════════════════
# ۶) Show Blade — نمایش مستقیم کارت (نه iframe)
# ═══════════════════════════════════════════════════════════════
SHOW_BLADE = r'''<div class="p-4 md:p-6 max-w-5xl mx-auto">

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
            <button onclick="printCurrentCert()" class="btn btn-info btn-sm">🖨️ چاپ</button>
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
<script type="text/template" id="cert-batch-template">{!! $batchHtml !!}</script>

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
    window.printCurrentCert = function () {
        var tmpl = document.getElementById('cert-batch-template');
        if (!tmpl) { alert('کارت پیدا نشد'); return; }
        var html = tmpl.innerHTML;

        var iframe = document.createElement('iframe');
        iframe.style.cssText = 'position:fixed;left:-99999px;top:0;width:0;height:0;border:0;';
        document.body.appendChild(iframe);
        var doc = iframe.contentDocument || iframe.contentWindow.document;
        doc.open();
        doc.write(html);
        doc.close();
        setTimeout(function () {
            try {
                iframe.contentWindow.focus();
                iframe.contentWindow.print();
            } catch (e) { console.error(e); }
            setTimeout(function () {
                if (iframe.parentNode) document.body.removeChild(iframe);
            }, 3000);
        }, 800);
    };

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
'''

# ═══════════════════════════════════════════════════════════════
# ۷) ViewModal Blade
# ═══════════════════════════════════════════════════════════════
VIEW_MODAL_BLADE = r'''<div>
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
'''

# ═══════════════════════════════════════════════════════════════
# ۸) Designer Blade — با wire:click و تغییرات
# ═══════════════════════════════════════════════════════════════
DESIGNER_BLADE = r'''<div class="p-6" dir="rtl" x-data x-init="
    window.ShopGunDesigner.init(
        {{ $certificate?->id ?? 'null' }},
        {!! $designJson ?: 'null' !!}
    )
">
    <div class="flex items-center justify-between mb-4 flex-wrap gap-2">
        <h1 class="text-2xl font-bold" style="color:#0d5c63;">
            🎨 ویرایشگر شناسنامه
            @if($certificate)
                <span class="text-sm font-normal text-gray-500">#{{ $certificate->code }}</span>
            @endif
        </h1>
        <div class="flex gap-2">
            <button type="button" onclick="window.ShopGunDesigner.addText()"
                    class="px-3 py-2 bg-teal-600 text-white rounded-lg text-sm hover:bg-teal-700">
                ➕ متن
            </button>
            <button type="button" onclick="window.ShopGunDesigner.addRect()"
                    class="px-3 py-2 bg-teal-600 text-white rounded-lg text-sm hover:bg-teal-700">
                ▭ کادر
            </button>
            {{-- ★ دکمه ذخیره Livewire --}}
            <button type="button"
                    onclick="window.ShopGunDesigner.saveDesign()"
                    class="px-4 py-2 bg-green-600 text-white rounded-lg text-sm font-bold hover:bg-green-700">
                💾 ذخیره
            </button>
        </div>
    </div>

    @if($statusMessage)
        <div class="mb-3 p-3 rounded-lg text-sm font-bold" style="background:#d1fae5;color:#065f46;">
            {{ $statusMessage }}
        </div>
    @endif

    <div class="grid grid-cols-1 lg:grid-cols-4 gap-4">
        <div class="lg:col-span-3 bg-white rounded-xl shadow p-4 flex justify-center"
             style="background: repeating-conic-gradient(#f0f0f0 0% 25%, #ffffff 0% 50%) 50% / 20px 20px;">
            <canvas id="cert-fabric-canvas" width="600" height="600"
                    style="border: 2px solid #b8860b; border-radius: 8px; box-shadow: 0 8px 24px rgba(0,0,0,.15);"></canvas>
        </div>

        <div class="lg:col-span-1 bg-white rounded-xl shadow p-4">
            <h2 class="text-sm font-bold mb-3 pb-2 border-b" style="color:#0d5c63;">✏️ خواص عنصر</h2>
            <div id="designer-props" class="text-gray-400 text-xs text-center py-6">
                یک عنصر انتخاب کنید
            </div>

            <div class="mt-4 pt-4 border-t">
                <h3 class="text-xs font-bold text-gray-600 mb-2">🔤 متغیرها:</h3>
                <div class="flex flex-wrap gap-1">
                    @foreach(['{code}', '{stoneEn}', '{stoneName}', '{metalEn}', '{metal}', '{carat}', '{length}', '{width}', '{weight}', '{brilliant}', '{serial}', '{origin}', '{qr}'] as $v)
                        <span class="px-2 py-1 bg-amber-100 text-amber-800 rounded text-xs font-mono cursor-pointer hover:bg-amber-200"
                              onclick="navigator.clipboard.writeText('{{ $v }}')"
                              title="کلیک = کپی">
                            {{ $v }}
                        </span>
                    @endforeach
                </div>
            </div>
        </div>
    </div>
</div>
'''

# ═══════════════════════════════════════════════════════════════
# اجرا
# ═══════════════════════════════════════════════════════════════
def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  Fix Cert — نمایش + PNG + چاپ + Designer                     ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    print("📦 Backup...")
    for rel in [
        "app/Services/CertRenderer.php",
        "app/Livewire/Certificates/Show.php",
        "app/Livewire/Certificates/ViewModal.php",
        "app/Livewire/Certificates/Designer.php",
        "resources/views/livewire/certificates/show.blade.php",
        "resources/views/livewire/certificates/view-modal.blade.php",
        "resources/views/livewire/certificates/designer.blade.php",
    ]:
        backup(rel)

    print("\n📄 نوشتن فایل‌ها...")
    write("app/Services/CertRenderer.php", CERT_RENDERER)
    write("app/Livewire/Certificates/Show.php", SHOW_PHP)
    write("app/Livewire/Certificates/ViewModal.php", VIEW_MODAL_PHP)
    write("app/Livewire/Certificates/Designer.php", DESIGNER_PHP)
    write("public/js/cert-designer.js", CERT_DESIGNER_JS)
    write("resources/views/livewire/certificates/show.blade.php", SHOW_BLADE)
    write("resources/views/livewire/certificates/view-modal.blade.php", VIEW_MODAL_BLADE)
    write("resources/views/livewire/certificates/designer.blade.php", DESIGNER_BLADE)

    print("\n" + "═" * 64)
    print("✅ تمام!")
    print("═" * 64)
    print(f"""
📋 دستورات:

  cd {PROJECT}
  php artisan optimize:clear
  php artisan view:clear

  ⚠️ مهم: سرور رو ببند (Ctrl+C) و دوباره:
  php artisan serve

  سپس در مرورگر: Ctrl+Shift+R (هارد رفرش)

🎯 چه چیزی حل شد:
  ✓ نمایش شناسنامه — دیگه iframe نیست، مستقیم render می‌شه
  ✓ PNG — selector .certificate درست شده
  ✓ چاپ — از renderBatchHtml با iframe داینامیک
  ✓ Designer — با Livewire.dispatch ذخیره می‌شه
""")

if __name__ == "__main__":
    main()