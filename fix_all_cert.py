#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix ShopGun Cert — رفع کامل همه خطاها"""
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
    print(f"  ✓ {rel}  ({len(content.encode('utf-8')):,} bytes)")

def backup(rel):
    src = PROJECT / rel
    if not src.exists(): return
    bd = PROJECT / "storage/backups"; bd.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    name = src.name.replace('.php','').replace('.js','').replace('.blade','')
    shutil.copy2(src, bd / f"{name}_{ts}.bak")

# ═══════════════════════════════════════════════════════════════
# ۱) CertConfig.php — کامل با همه کلیدها
# ═══════════════════════════════════════════════════════════════
CERT_CONFIG = r'''<?php

namespace App\Support;

use App\Models\CertSetting;

class CertConfig
{
    public const DEFAULT_WIDTH  = 6.5;
    public const DEFAULT_HEIGHT = 6.5;

    public static function sizes($source = null): array
    {
        $d = [
            'width'  => self::DEFAULT_WIDTH,
            'height' => self::DEFAULT_HEIGHT,

            // snake_case (CertRenderer استفاده می‌کند)
            'img_w' => 120, 'img_h' => 120,
            'qr_size' => 40, 'logo_w' => 28, 'logo_h' => 22,
            'code_font' => 11, 'url_font' => 6, 'table_font' => 8,
            'title_font' => 20, 'desc_font' => 7,
            'table_label_font' => 8, 'table_value_font' => 8,

            // camelCase (Blade Component استفاده می‌کند)
            'imgW' => 120, 'imgH' => 120,
            'qrSize' => 40, 'logoW' => 28, 'logoH' => 22,
            'codeFont' => 11, 'urlFont' => 6, 'tableFont' => 8,
            'titleFont' => 20, 'descFont' => 7,
            'tableLabelFont' => 8, 'tableValueFont' => 8,
        ];

        $saved = null;
        if (is_array($source)) $saved = $source;
        elseif (is_object($source) && isset($source->sizes) && is_array($source->sizes)) $saved = $source->sizes;

        if ($saved === null) {
            try {
                $path = storage_path('app/cert-config.json');
                if (file_exists($path)) {
                    $data = json_decode(file_get_contents($path), true);
                    if (is_array($data)) $saved = $data['sizes'] ?? $data;
                }
            } catch (\Throwable $e) {}
        }

        return is_array($saved) ? array_merge($d, $saved) : $d;
    }

    public static function assets(): array
    {
        $bg = null; $logo = null; $desc = null;
        try {
            if (class_exists(CertSetting::class)) {
                $bg   = CertSetting::get('bg_image',   null);
                $logo = CertSetting::get('logo_image', null);
                $desc = CertSetting::get('desc_image', null);
            }
        } catch (\Throwable $e) {}

        return [
            'bg_image'   => self::resolveUrl($bg),
            'logo_image' => self::resolveUrl($logo),
            'desc_image' => self::resolveUrl($desc),
        ];
    }

    protected static function resolveUrl($v): ?string
    {
        if (!$v || !is_string($v)) return null;
        if (str_starts_with($v, 'http') || str_starts_with($v, 'data:')) return $v;
        $c = ltrim($v, '/');
        if (str_starts_with($c, 'storage/')) return asset($c);
        if (file_exists(public_path($c))) return asset($c);
        return asset('storage/' . $c);
    }

    public static function hideDesc(): bool
    {
        try {
            if (class_exists(CertSetting::class)) {
                return (bool) CertSetting::get('hide_desc', false);
            }
        } catch (\Throwable $e) {}
        return false;
    }

    public static function __callStatic($name, $args)
    {
        if (stripos($name, 'asset') !== false) return self::assets();
        if (stripos($name, 'hide')  !== false) return self::hideDesc();
        if (stripos($name, 'size')  !== false) return self::sizes();
        if (stripos($name, 'font')  !== false) return self::sizes();
        return self::sizes();
    }
}
'''

# ═══════════════════════════════════════════════════════════════
# ۲) CertRenderer.php — بازنویسی کامل با طراحی Legacy
# ═══════════════════════════════════════════════════════════════
CERT_RENDERER = r'''<?php

namespace App\Services;

use App\Models\Certificate;
use App\Support\CertConfig;
use App\Support\PersianNumber;

class CertRenderer
{
    public static function renderHtml(Certificate $cert, array $opts = []): string
    {
        $sizes  = CertConfig::sizes();
        $assets = CertConfig::assets();
        $hide   = CertConfig::hideDesc();

        // ★★★ نکته مهم: با ?? مقادیر پیش‌فرض ایمن ★★★
        $cw     = (float) ($sizes['width']  ?? 6.5);
        $ch     = (float) ($sizes['height'] ?? 6.5);
        $pxW    = (int) round($cw * 96 / 2.54);
        $pxH    = (int) round($ch * 96 / 2.54);
        $scale  = $cw / 6.5;

        $imgW   = (int) round(($sizes['img_w']   ?? 120) * $scale);
        $imgH   = (int) round(($sizes['img_h']   ?? 120) * $scale);
        $qrS    = (int) round(($sizes['qr_size'] ?? 40)  * $scale);
        $logoW  = (int) round(($sizes['logo_w']  ?? 28)  * $scale);
        $logoH  = (int) round(($sizes['logo_h']  ?? 22)  * $scale);

        // اطلاعات
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

        // تصویر محصول
        $imgSrc = '';
        if (!empty($cert->image_url)) $imgSrc = $cert->image_url;
        elseif (!empty($cert->image_path)) $imgSrc = asset('storage/' . $cert->image_path);

        $imgInner = $imgSrc
            ? "<img src='{$imgSrc}' alt='' crossorigin='anonymous'>"
            : "<div style='display:flex;align-items:center;justify-content:center;width:100%;height:100%;font-size:32px;'>💎</div>";

        // پس‌زمینه
        $bgStyle = !empty($assets['bg_image']) ? "background-image:url('{$assets['bg_image']}');" : '';

        // لوگو
        $logoHtml = !empty($assets['logo_image'])
            ? "<div class='ico'><img src='{$assets['logo_image']}' alt=''></div>"
            : "<div class='ico'><span>💎</span></div>";

        // توضیحات
        $descHtml = '';
        if (!$hide) {
            $descHtml = !empty($assets['desc_image'])
                ? "<img src='{$assets['desc_image']}' alt=''>"
                : '<div class="cert-auth-text">This certificate is only for authenticity of purchased product.</div>';
        }

        $flagHtml = $flagUrl
            ? "<img src='{$flagUrl}' style='width:14px;vertical-align:middle;border-radius:2px;' alt=''>"
            : '';

        // ★ طراحی کارت (بر اساس Legacy v6.14)
        $cardHtml = <<<CARD
<div class="certificate" style="width:{$pxW}px;height:{$pxH}px;">
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

        // ★ CSS (کپی از cert-card.css به inline تا iframe مستقل باشد)
        $css = self::inlineCss();

        return <<<HTML
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<title>Certificate {$code}</title>
<link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Great+Vibes&family=Playfair+Display:wght@400;700&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>{$css}</style>
</head>
<body style="margin:0;padding:0;background:transparent;">
{$cardHtml}
</body>
</html>
HTML;
    }

    public static function renderBatchHtml(array $certs, int $cols = 3): string
    {
        $sizes = CertConfig::sizes();
        $cw    = (float) ($sizes['width']  ?? 6.5);
        $ch    = (float) ($sizes['height'] ?? 6.5);
        $gap   = $cols === 1 ? 0 : round((210 - ($cols * $cw) - 6) / max(1, $cols - 1), 2);

        $cards = '';
        foreach ($certs as $cert) {
            $html = self::renderHtml($cert);
            if (preg_match('/<body[^>]*>(.*)<\/body>/s', $html, $m)) {
                $cards .= "<div class='batch-card'>{$m[1]}</div>";
            }
        }

        $css = self::inlineCss();

        return <<<HTML
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">
<link href="https://fonts.googleapis.com/css2?family=Great+Vibes&family=Playfair+Display:wght@400;700&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>
{$css}
@page{size:A4 portrait;margin:3mm}
*{box-sizing:border-box;margin:0;padding:0;-webkit-print-color-adjust:exact;print-color-adjust:exact}
html,body{background:#fff}
.grid{display:grid;grid-template-columns:repeat({$cols},{$cw}cm);column-gap:{$gap}cm;row-gap:2mm;justify-content:center;padding:0;width:100%}
.batch-card .certificate{width:{$cw}cm!important;height:{$ch}cm!important;min-width:{$cw}cm!important;min-height:{$ch}cm!important;max-width:{$cw}cm!important;max-height:{$ch}cm!important;page-break-inside:avoid;break-inside:avoid;box-shadow:none!important}
</style>
</head>
<body>
<div class="grid">{$cards}</div>
</body>
</html>
HTML;
    }

    protected static function inlineCss(): string
    {
        return <<<CSS
*{box-sizing:border-box}
html,body{margin:0;padding:0;background:transparent}
.certificate{background:#fffef9;color:#2c3e50;position:relative;overflow:hidden;font-family:'Inter','Vazirmatn',Tahoma,sans-serif;font-size:11px;border:1px solid #999;border-radius:10px;box-sizing:border-box;line-height:1.2}
.cert-bg-layer{position:absolute;inset:0;background-size:cover;background-position:center;background-repeat:no-repeat;z-index:0;opacity:.12;border-radius:10px;pointer-events:none}
.cert-main{position:relative;z-index:3;width:100%;height:100%;padding:8px;display:flex;flex-direction:column;box-sizing:border-box;overflow:visible}
.cert-top-section{display:flex;gap:8px;margin-bottom:4px;overflow:hidden;flex:0 0 auto}
.cert-right-text{flex:1 1 auto;min-width:60px;display:flex;flex-direction:column;padding:2px 0 2px 4px;overflow:hidden;text-align:right}
.cert-title-script{font-family:'Great Vibes',cursive;color:#6b4423;line-height:1;text-align:right;font-size:20px}
.cert-subtitle-script{font-family:'Playfair Display',serif;font-size:8px;color:#6b4423;text-align:right;margin-bottom:6px;font-style:italic}
.cert-desc-area{flex:1 1 auto;text-align:right;overflow:hidden;display:flex;align-items:center;justify-content:flex-end;min-height:0}
.cert-desc-area img{max-width:100%;max-height:100%;object-fit:contain;margin:auto;display:block}
.cert-auth-text{font-family:'Playfair Display',serif;color:#6b4423;line-height:1.5;text-align:right;font-size:7px}
.cert-sig-block{text-align:right;margin-top:4px;flex-shrink:0}
.cert-sig-line{font-family:'Great Vibes',cursive;font-size:12px;color:#6b4423;border-bottom:1px solid #6b4423;display:inline-block;padding:0 6px 2px;min-width:70px}
.cert-sig-label{font-family:'Playfair Display',serif;font-size:6px;color:#999;margin-top:2px}
.cert-img-frame-wrap{flex:0 0 auto;position:relative;padding:4px;border:1px solid #b8860b;border-radius:8px;background:#fff;box-sizing:border-box;max-height:100%;overflow:hidden;align-self:flex-start}
.cert-img-frame-wrap::before{content:'';position:absolute;inset:2px;border:1px solid rgba(184,134,11,.4);border-radius:6px;pointer-events:none}
.cert-img-frame{width:100%;height:100%;border:1.5px solid #b8860b;border-radius:6px;overflow:hidden;background:#fff;position:relative}
.cert-img-frame img{width:100%;height:100%;object-fit:contain;display:block}
.cert-serial-balloon{position:absolute;bottom:6px;left:50%;transform:translateX(-50%);background:rgba(0,0,0,.55);color:#fff;font-family:monospace;font-size:5px;font-weight:700;padding:2px 6px;border-radius:8px;white-space:nowrap;border:1px solid rgba(255,255,255,.25);pointer-events:none;z-index:2}
.cert-qr-panel{display:flex;gap:6px;align-items:center;padding:4px 2px;margin-bottom:4px;justify-content:flex-end;flex-wrap:nowrap;overflow:visible;flex:0 0 auto}
.cert-qr-wrap{display:flex;flex-direction:column;align-items:center;background:#fff;border:1px solid #0d5c63;border-radius:6px;padding:3px 4px;min-width:30px;box-sizing:border-box;flex-shrink:0}
.cert-qr-url{color:#1a5276;font-weight:600;margin-bottom:2px;min-width:15px;font-size:6px;direction:ltr}
.cert-qr-inner{display:flex;gap:6px;align-items:center;overflow:hidden}
.cert-qr-box{background:#fff;border-radius:3px;overflow:hidden;flex-shrink:0;box-sizing:border-box}
.cert-qr-box img{width:100%;height:100%;object-fit:contain;display:block}
.cert-code-inline{display:flex;flex-direction:column;align-items:flex-start;gap:2px;min-width:30px}
.cert-code-inline .lbl{font-size:6px;color:#7f8c8d;text-transform:uppercase}
.cert-code-inline .val{font-family:monospace;font-weight:700;color:#1a5276;letter-spacing:.8px;font-size:11px}
.cert-logo-mini{display:flex;align-items:center;gap:4px;margin-right:auto;flex-wrap:nowrap;min-width:30px;max-width:50%;overflow:hidden}
.cert-logo-mini .ico{border:none;border-radius:4px;display:flex;align-items:center;justify-content:center;overflow:hidden;padding:0;background:transparent;flex-shrink:0;box-sizing:border-box;font-size:22px}
.cert-logo-mini .ico img{width:100%;height:100%;object-fit:contain;display:block}
.cert-table-wrap{width:100%;flex:0 0 auto;border-radius:8px;overflow:hidden;border:1.5px solid #0d5c63;background:#fff;box-sizing:border-box;max-width:100%}
.cert-bottom-table{width:100%;border-collapse:collapse;background:transparent;font-family:'Inter','Vazirmatn',sans-serif;table-layout:fixed;box-sizing:border-box}
.cert-bottom-table td{border:1px solid #7fbfc4;vertical-align:middle;line-height:1.2;word-break:break-word;padding:2px 3px;box-sizing:border-box;overflow:hidden;text-overflow:ellipsis}
.cert-bottom-table .tbl-label{background:#0d5c63;color:#e0f7f8;font-weight:700;text-align:right;font-size:8px}
.cert-bottom-table .tbl-value{background:#fff;color:#2c3e50;font-weight:600;text-align:right;font-size:8px}
.cert-bottom-table .unit{float:left;font-size:6px;color:#888;font-weight:400}
CSS;
    }
}
'''

# ═══════════════════════════════════════════════════════════════
# ۳) cert-designer.js — فایل JS ویرایشگر
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
    var title = new fabric.IText('Certificate', {
      left: 300, top: 60, fontSize: 28,
      fontFamily: 'Great Vibes', fill: '#6b4423', originX: 'center'
    });
    canvas.add(title);

    var sub = new fabric.IText('Quality Guarantee', {
      left: 300, top: 100, fontSize: 11,
      fontFamily: 'Playfair Display', fontStyle: 'italic',
      fill: '#6b4423', originX: 'center'
    });
    canvas.add(sub);

    var vars = [
      { t: '{code}',      y: 160, s: 14, c: '#1a5276', w: 'bold' },
      { t: '{stoneEn}',   y: 200, s: 12, c: '#2c3e50' },
      { t: '{metalEn}',   y: 225, s: 12, c: '#2c3e50' },
      { t: '{length}*{width}', y: 250, s: 12, c: '#2c3e50' },
      { t: '{weight} gr', y: 275, s: 12, c: '#2c3e50' }
    ];
    vars.forEach(function (v) {
      canvas.add(new fabric.IText(v.t, {
        left: 300, top: v.y, fontSize: v.s,
        fontFamily: 'Inter', fill: v.c,
        fontWeight: v.w || 'normal', originX: 'center'
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
    var isImg  = a.type === 'image';
    var isRect = a.type === 'rect';

    var h = '<div style="font-size:11px;font-weight:700;color:#0d5c63;margin-bottom:10px;border-bottom:1px solid #ddd;padding-bottom:6px;">' + a.type.toUpperCase() + '</div>';
    h += '<div style="display:grid;grid-template-columns:1fr 1fr;gap:6px;">';
    h += '<label style="font-size:11px;">X <input type="number" id="prop-x" value="' + Math.round(a.left) + '" style="width:100%;padding:4px;border:1px solid #ccc;border-radius:4px;"></label>';
    h += '<label style="font-size:11px;">Y <input type="number" id="prop-y" value="' + Math.round(a.top) + '" style="width:100%;padding:4px;border:1px solid #ccc;border-radius:4px;"></label>';
    h += '</div>';

    if (isText) {
      h += '<label style="font-size:11px;display:block;margin-top:6px;">متن<input type="text" id="prop-text" value="' + (a.text || '').replace(/"/g, '&quot;') + '" style="width:100%;padding:4px;border:1px solid #ccc;border-radius:4px;font-family:monospace;"></label>';
      h += '<label style="font-size:11px;display:block;margin-top:6px;">اندازه فونت<input type="number" id="prop-fs" value="' + (a.fontSize || 12) + '" style="width:100%;padding:4px;border:1px solid #ccc;border-radius:4px;"></label>';
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
    var a = canvas.getActiveObject();
    if (!a) return;
    var x = parseFloat(document.getElementById('prop-x').value);
    var y = parseFloat(document.getElementById('prop-y').value);
    if (!isNaN(x)) a.set('left', x);
    if (!isNaN(y)) a.set('top', y);
    var t = document.getElementById('prop-text'); if (t) a.set('text', t.value);
    var fs = document.getElementById('prop-fs'); if (fs) a.set('fontSize', parseFloat(fs.value));
    var f = document.getElementById('prop-fill'); if (f) a.set('fill', f.value);
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
    if (!canvas || !currentCertId) { alert('Canvas آماده نیست'); return; }
    var json = canvas.toJSON(['selectable', 'evented']);
    var jsonStr = JSON.stringify(json);

    // Try Livewire
    var rootEl = document.querySelector('[wire\\:id]');
    if (window.Livewire && rootEl) {
      var compId = rootEl.getAttribute('wire:id');
      var comp = window.Livewire.find(compId);
      if (comp) {
        comp.call('saveDesign', jsonStr);
        return;
      }
    }
    // Fallback
    fetch('/certificates/' + currentCertId + '/design', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-TOKEN': (document.querySelector('meta[name="csrf-token"]') || {}).content || ''
      },
      body: JSON.stringify({ design_data: json })
    }).then(function (r) { return r.json(); })
      .then(function () { alert('ذخیره شد ✅'); })
      .catch(function () { alert('خطا در ذخیره'); });
  }

  window.ShopGunDesigner = {
    init: init, applyProps: applyProps, deleteActive: deleteActive,
    addText: addText, addRect: addRect, saveDesign: saveDesign,
    getCanvas: function () { return canvas; }
  };
})();
"""

# ═══════════════════════════════════════════════════════════════
# اجرا
# ═══════════════════════════════════════════════════════════════
def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  Fix ShopGun Cert — همه خطاها                                 ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    print("📦 Backup...")
    backup("app/Support/CertConfig.php")
    backup("app/Services/CertRenderer.php")
    backup("resources/views/components/layouts/app.blade.php")

    print("\n📄 نوشتن فایل‌ها...")
    write("app/Support/CertConfig.php", CERT_CONFIG)
    write("app/Services/CertRenderer.php", CERT_RENDERER)
    write("public/js/cert-designer.js", CERT_DESIGNER_JS)

    # ═══ بررسی layout — اضافه کردن cert-designer.js ═══
    print("\n🔗 بررسی Layout...")
    layout = PROJECT / "resources/views/components/layouts/app.blade.php"
    if layout.exists():
        with open(layout, 'r', encoding='utf-8') as f:
            content = f.read()

        changed = False
        # اضافه کردن cert-designer.js اگر نیست
        if 'cert-designer.js' not in content:
            old_tag = '<script src="{{ asset(\'js/cert-card.js\') }}?v=1" defer></script>'
            new_tag = old_tag + '\n    <script src="{{ asset(\'js/cert-designer.js\') }}?v=1" defer></script>'
            if old_tag in content:
                content = content.replace(old_tag, new_tag, 1)
                changed = True
                print("  ✓ cert-designer.js به layout اضافه شد")
            else:
                # fallback — قبل از @stack
                if '@stack(\'scripts\')' in content:
                    content = content.replace(
                        "@stack('scripts')",
                        '<script src="{{ asset(\'js/cert-designer.js\') }}?v=1" defer></script>\n    @stack(\'scripts\')',
                        1
                    )
                    changed = True
                    print("  ✓ cert-designer.js قبل از @stack اضافه شد")
        else:
            print("  ⏭ cert-designer.js از قبل موجود است")

        if changed:
            with open(layout, 'w', encoding='utf-8', newline='\n') as f:
                f.write(content)
    else:
        print("  ⚠️ Layout پیدا نشد!")

    print("\n" + "═" * 64)
    print("✅ تمام!")
    print("═" * 64)
    print(f"""
📋 حالا اجرا کنید:

  cd {PROJECT}
  php artisan optimize:clear
  php artisan route:clear
  php artisan view:clear

  ⚠️ مهم: سرور رو ببند (Ctrl+C) و دوباره اجرا کن:
  php artisan serve

سپس مرورگر رو کامل رفرش کن (Ctrl+Shift+R).

🎯 چه چیزی درست شد:
  ✓ CertConfig حالا width و height داره
  ✓ CertRenderer طراحی زیبای Legacy رو برمی‌گردونه
  ✓ cert-designer.js لود می‌شه → Designer کار می‌کنه
""")

if __name__ == "__main__":
    main()