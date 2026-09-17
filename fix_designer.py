#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fix Designer + Renderer — طراحی پیش‌فرض و رفع خطاها"""
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
# ۱) CertRenderer — پشتیبانی از design_data
# ═══════════════════════════════════════════════════════════════
CERT_RENDERER = r'''<?php

namespace App\Services;

use App\Models\Certificate;
use App\Support\CertConfig;
use App\Support\PersianNumber;

class CertRenderer
{
    /**
     * ★ HTML فقط کارت (بدون DOCTYPE) — برای نمایش مستقیم
     */
    public static function renderCard(Certificate $cert): string
    {
        // اگر design_data دارد، از آن استفاده کن
        if (!empty($cert->design_data) && is_array($cert->design_data)) {
            return self::renderFromDesign($cert, $cert->design_data, false);
        }
        return self::buildCardInner($cert, false);
    }

    /**
     * ★ HTML کامل با DOCTYPE — برای iframe/چاپ
     */
    public static function renderHtml(Certificate $cert, array $opts = []): string
    {
        // اگر design_data دارد
        if (!empty($cert->design_data) && is_array($cert->design_data)) {
            $card = self::renderFromDesign($cert, $cert->design_data, true);
        } else {
            $card = self::buildCardInner($cert, true);
        }
        $css = self::inlineCss();
        return '<!DOCTYPE html><html lang="fa" dir="rtl"><head><meta charset="UTF-8">'
            . '<link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">'
            . '<link href="https://fonts.googleapis.com/css2?family=Great+Vibes&family=Playfair+Display:wght@400;700&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">'
            . '<style>' . $css . '</style></head><body style="margin:0;padding:0;background:transparent;">'
            . $card . '</body></html>';
    }

    /**
     * ★ رندر از design_data (Fabric.js JSON)
     */
    protected static function renderFromDesign(Certificate $cert, array $design, bool $includeStyle): string
    {
        $sizes = CertConfig::sizes();
        $cw = (float) ($sizes['width']  ?? 6.5);
        $ch = (float) ($sizes['height'] ?? 6.5);
        $pxW = (int) round($cw * 96 / 2.54);
        $pxH = (int) round($ch * 96 / 2.54);

        // ابعاد canvas اصلی در Designer
        $canvasW = (float) ($design['canvas_width']  ?? 600);
        $canvasH = (float) ($design['canvas_height'] ?? 600);

        $scaleX = $pxW / $canvasW;
        $scaleY = $pxH / $canvasH;
        $scale  = min($scaleX, $scaleY);

        // متغیرها
        $vars = [
            '{code}'       => $cert->code ?? '',
            '{serial}'     => $cert->serial ?? '',
            '{stoneName}'  => $cert->stone_name ?? '',
            '{stoneEn}'    => $cert->stone_en ?? '',
            '{origin}'     => $cert->stone_origin ?? '',
            '{metal}'      => $cert->metal ?? '',
            '{metalEn}'    => $cert->metal_en ?? $cert->metal ?? '',
            '{carat}'      => $cert->metal_carat ?? '',
            '{length}'     => $cert->length_clean ?? '0',
            '{width}'      => $cert->width_clean  ?? '0',
            '{weight}'     => $cert->weight_clean ?? '0',
            '{brilliant}'  => $cert->brilliant_clean ?? '0',
            '{image}'      => '',
            '{qr}'         => '',
            '{logo}'       => '',
            '{description}'=> 'This certificate is only for authenticity of purchased product.',
        ];

        // تصویر محصول
        $imgSrc = '';
        if (!empty($cert->image_url))    $imgSrc = $cert->image_url;
        elseif (!empty($cert->image_path)) $imgSrc = asset('storage/' . $cert->image_path);
        $qrUrl = $cert->qr_url;

        $objects = $design['objects'] ?? [];
        $inner = '';

        foreach ($objects as $o) {
            $type = $o['type'] ?? '';
            $name = $o['name'] ?? '';

            // موقعیت و اندازه
            $left   = ((float) ($o['left'] ?? 0)) * $scale;
            $top    = ((float) ($o['top']  ?? 0)) * $scale;
            $scX    = (float) ($o['scaleX'] ?? 1);
            $scY    = (float) ($o['scaleY'] ?? 1);
            $angle  = (float) ($o['angle'] ?? 0);
            $opacity = (float) ($o['opacity'] ?? 1);
            $originX = $o['originX'] ?? 'left';
            $originY = $o['originY'] ?? 'top';

            // style پایه
            $baseStyle = 'position:absolute;'
                . 'left:' . round($left, 2) . 'px;'
                . 'top:'  . round($top, 2)  . 'px;'
                . 'opacity:' . $opacity . ';';

            if ($angle != 0) $baseStyle .= 'transform:rotate(' . $angle . 'deg);';

            // اصلاح originX
            if ($originX === 'center') $baseStyle .= 'transform-origin:center top;';
            elseif ($originX === 'right') $baseStyle .= 'transform-origin:right top;';

            // ---- TEXT ----
            if ($type === 'i-text' || $type === 'text' || $type === 'textbox') {
                $rawText = $o['text'] ?? '';
                $text = strtr($rawText, $vars);

                $fs = ((float) ($o['fontSize'] ?? 14)) * $scale;
                $fontFamily = $o['fontFamily'] ?? 'Inter';
                $fontWeight = $o['fontWeight'] ?? 'normal';
                $fontStyle  = $o['fontStyle']  ?? 'normal';
                $fill = $o['fill'] ?? '#2c3e50';
                $underline = !empty($o['underline']) ? 'text-decoration:underline;' : '';
                $lineHeight = $o['lineHeight'] ?? 1.16;

                $tx = '';
                if ($originX === 'center') $tx = 'transform:translateX(-50%);';
                elseif ($originX === 'right') $tx = 'transform:translateX(-100%);';

                $ty = '';
                if ($originY === 'center') $ty = 'transform:translateY(-50%);';
                elseif ($originY === 'bottom') $ty = 'transform:translateY(-100%);';

                // ترکیب transform
                $tr = 'transform:';
                if ($originX === 'center') $tr .= 'translateX(-50%) ';
                elseif ($originX === 'right') $tr .= 'translateX(-100%) ';
                if ($originY === 'center') $tr .= 'translateY(-50%) ';
                elseif ($originY === 'bottom') $tr .= 'translateY(-100%) ';
                if ($angle != 0) $tr .= 'rotate(' . $angle . 'deg) ';

                $inner .= '<div style="' . $baseStyle
                    . $tr
                    . 'font-family:' . e($fontFamily) . ',sans-serif;'
                    . 'font-size:' . round($fs, 2) . 'px;'
                    . 'font-weight:' . e($fontWeight) . ';'
                    . 'font-style:' . e($fontStyle) . ';'
                    . 'color:' . e($fill) . ';'
                    . 'line-height:' . $lineHeight . ';'
                    . 'white-space:pre-wrap;'
                    . 'text-align:' . ($originX === 'right' ? 'right' : ($originX === 'center' ? 'center' : 'left')) . ';'
                    . $underline
                    . '">' . e($text) . '</div>';
            }
            // ---- RECT ----
            elseif ($type === 'rect') {
                $w = ((float) ($o['width'] ?? 0)) * $scX * $scale;
                $h = ((float) ($o['height'] ?? 0)) * $scY * $scale;
                $fill   = $o['fill'] ?? 'transparent';
                $stroke = $o['stroke'] ?? 'transparent';
                $sw     = ((float) ($o['strokeWidth'] ?? 0)) * $scale;
                $rx     = ((float) ($o['rx'] ?? 0)) * $scale;

                $isImage = strpos($name, 'image') !== false;
                $isQR    = strpos($name, 'qr')    !== false;
                $isLogo  = strpos($name, 'logo')  !== false;

                $content = '';
                if ($isImage && $imgSrc) {
                    $content = '<img src="' . e($imgSrc) . '" style="width:100%;height:100%;object-fit:contain;display:block;" crossorigin="anonymous">';
                } elseif ($isQR) {
                    $content = '<img src="' . e($qrUrl) . '" style="width:100%;height:100%;object-fit:contain;display:block;">';
                } elseif ($isLogo) {
                    $assets = CertConfig::assets();
                    if (!empty($assets['logo_image'])) {
                        $content = '<img src="' . e($assets['logo_image']) . '" style="width:100%;height:100%;object-fit:contain;display:block;">';
                    }
                }

                $inner .= '<div style="' . $baseStyle
                    . 'width:' . round($w, 2) . 'px;'
                    . 'height:' . round($h, 2) . 'px;'
                    . 'background:' . e($fill) . ';'
                    . 'border:' . round($sw, 2) . 'px solid ' . e($stroke) . ';'
                    . 'border-radius:' . round($rx, 2) . 'px;'
                    . 'overflow:hidden;'
                    . 'display:flex;align-items:center;justify-content:center;'
                    . 'box-sizing:border-box;'
                    . '">' . $content . '</div>';
            }
            // ---- LINE ----
            elseif ($type === 'line') {
                $x1 = ((float) ($o['x1'] ?? 0)) * $scale;
                $y1 = ((float) ($o['y1'] ?? 0)) * $scale;
                $x2 = ((float) ($o['x2'] ?? 0)) * $scale;
                $y2 = ((float) ($o['y2'] ?? 0)) * $scale;
                $stroke = $o['stroke'] ?? '#6b4423';
                $sw = ((float) ($o['strokeWidth'] ?? 1)) * $scale;

                $w = abs($x2 - $x1);
                $inner .= '<div style="position:absolute;left:' . round(min($x1, $x2), 2) . 'px;top:' . round(min($y1, $y2), 2) . 'px;'
                    . 'width:' . round($w, 2) . 'px;height:' . round($sw, 2) . 'px;'
                    . 'background:' . e($stroke) . ';"></div>';
            }
        }

        $styleTag = $includeStyle ? '<style>' . self::inlineCss() . '</style>' : '';

        return $styleTag
            . '<div class="certificate" data-cert-code="' . e($cert->code) . '" '
            . 'style="width:' . $pxW . 'px;height:' . $pxH . 'px;position:relative;background:#fffef9;border:1px solid #999;border-radius:10px;overflow:hidden;box-sizing:border-box;font-family:\'Inter\',\'Vazirmatn\',Tahoma,sans-serif;">'
            . $inner
            . '</div>';
    }

    /**
     * ★ روش HTML پیش‌فرض (وقتی design_data نداریم)
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

        $imgSrc = '';
        if (!empty($cert->image_url))    $imgSrc = $cert->image_url;
        elseif (!empty($cert->image_path)) $imgSrc = asset('storage/' . $cert->image_path);

        $imgInner = $imgSrc
            ? '<img src="' . e($imgSrc) . '" alt="" crossorigin="anonymous">'
            : '<div style="display:flex;align-items:center;justify-content:center;width:100%;height:100%;font-size:32px;">💎</div>';

        $bgStyle = !empty($assets['bg_image']) ? 'background-image:url(\'' . e($assets['bg_image']) . '\');' : '';
        $logoHtml = !empty($assets['logo_image'])
            ? '<div class="ico"><img src="' . e($assets['logo_image']) . '" alt=""></div>'
            : '<div class="ico"><span>💎</span></div>';

        $descHtml = '';
        if (!$hide) {
            $descHtml = !empty($assets['desc_image'])
                ? '<img src="' . e($assets['desc_image']) . '" alt="">'
                : '<div class="cert-auth-text">This certificate is only for authenticity of purchased product.</div>';
        }

        $flagHtml = $flagUrl
            ? '<img src="' . e($flagUrl) . '" style="width:14px;vertical-align:middle;border-radius:2px;" alt="">'
            : '';

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
          <td class="tbl-label">Stone</td><td class="tbl-value">{$stoneEn}</td>
          <td class="tbl-label">Metal</td><td class="tbl-value">{$metalEn} <span class="unit">{$carat}</span></td>
        </tr>
        <tr>
          <td class="tbl-label">Originality</td><td class="tbl-value">{$origin} {$flagHtml}</td>
          <td class="tbl-label">Stone S</td><td class="tbl-value">{$length}*{$widthS} <span class="unit">mm</span></td>
        </tr>
        <tr>
          <td class="tbl-label">Brillant</td><td class="tbl-value">{$brill}</td>
          <td class="tbl-label">Total W</td><td class="tbl-value">{$weight} <span class="unit">gr</span></td>
        </tr>
      </table>
    </div>
  </div>
</div>
CARD;

        if ($includeStyle) return '<style>' . self::inlineCss() . '</style>' . $card;
        return $card;
    }

    public static function renderBatchHtml(array $certs, int $cols = 3): string
    {
        $sizes = CertConfig::sizes();
        $cw    = (float) ($sizes['width']  ?? 6.5);
        $ch    = (float) ($sizes['height'] ?? 6.5);
        $gap   = $cols === 1 ? 0 : round((210 - ($cols * $cw) - 6) / max(1, $cols - 1), 2);

        $cards = '';
        foreach ($certs as $cert) {
            $cards .= '<div class="batch-card">' . self::renderCard($cert) . '</div>';
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
            . '</style>'
            . '</head><body><div class="cert-print-grid">' . $cards . '</div></body></html>';
    }

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
# ۲) cert-designer.js — با طرح پیش‌فرض کامل
# ═══════════════════════════════════════════════════════════════
CERT_DESIGNER_JS = r"""(function () {
  'use strict';

  // ★ suppress alphabetical warning از Fabric.js
  var _origWarn = console.warn;
  console.warn = function () {
    var m = arguments[0];
    if (typeof m === 'string' && m.indexOf('alphabetical') !== -1) return;
    _origWarn.apply(console, arguments);
  };

  var canvas = null;
  var currentCertId = null;
  var CANVAS_W = 600;
  var CANVAS_H = 600;

  function loadFabric(cb) {
    if (typeof fabric !== 'undefined') { cb(); return; }
    var s = document.createElement('script');
    s.src = 'https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.2.4/fabric.min.js';
    s.onload = cb;
    s.onerror = function () { console.error('fabric.js load failed'); };
    document.head.appendChild(s);
  }

  function init(certId, designData) {
    currentCertId = certId;
    loadFabric(function () {
      var el = document.getElementById('cert-fabric-canvas');
      if (!el) { setTimeout(function () { init(certId, designData); }, 200); return; }
      if (canvas) { canvas.dispose(); canvas = null; }

      canvas = new fabric.Canvas('cert-fabric-canvas', {
        width: CANVAS_W,
        height: CANVAS_H,
        backgroundColor: '#fffef9',
        preserveObjectStacking: true
      });

      var hasDesign = designData
        && designData.objects
        && designData.objects.length > 0;

      if (hasDesign) {
        canvas.loadFromJSON(designData, function () {
          canvas.renderAll();
          bind();
        });
      } else {
        buildDefaultDesign();
        bind();
      }
    });
  }

  /**
   * ★ طرح پیش‌فرض — منطبق با کارت HTML
   */
  function buildDefaultDesign() {
    var brown    = '#6b4423';
    var gold     = '#b8860b';
    var teal     = '#0d5c63';
    var primary  = '#1a5276';
    var textCol  = '#2c3e50';
    var grayCol  = '#999999';

    // ════════════ فریم تصویر (سمت چپ) ════════════
    canvas.add(new fabric.Rect({
      left: 40, top: 40, width: 180, height: 180,
      fill: '#ffffff', stroke: gold, strokeWidth: 3,
      rx: 8, ry: 8,
      name: 'image_frame',
      selectable: true
    }));

    canvas.add(new fabric.IText('{image}', {
      left: 130, top: 130,
      fontSize: 14, fontFamily: 'Inter',
      fill: grayCol, originX: 'center', originY: 'center',
      name: 'image_label', selectable: true
    }));

    // ════════════ عنوان (سمت راست) ════════════
    canvas.add(new fabric.IText('Certificate', {
      left: 560, top: 50,
      fontSize: 42, fontFamily: 'Great Vibes',
      fill: brown, originX: 'right',
      name: 'title', selectable: true
    }));

    canvas.add(new fabric.IText('Quality Guarantee', {
      left: 560, top: 105,
      fontSize: 14, fontFamily: 'Playfair Display',
      fontStyle: 'italic', fill: brown, originX: 'right',
      name: 'subtitle', selectable: true
    }));

    // ════════════ توضیحات ════════════
    canvas.add(new fabric.IText(
      'This certificate is only for\nauthenticity of purchased product.',
      {
        left: 560, top: 145,
        fontSize: 11, fontFamily: 'Playfair Display',
        fill: brown, originX: 'right',
        textAlign: 'right', lineHeight: 1.4,
        name: 'description', selectable: true
      }
    ));

    // ════════════ امضا ════════════
    canvas.add(new fabric.IText('Quality Guarantee', {
      left: 560, top: 200,
      fontSize: 22, fontFamily: 'Great Vibes',
      fill: brown, originX: 'right',
      name: 'signature', selectable: true
    }));

    canvas.add(new fabric.Line([420, 235, 560, 235], {
      stroke: brown, strokeWidth: 1,
      name: 'signature_line', selectable: true
    }));

    // ════════════ QR + لوگو (پایین چپ) ════════════
    canvas.add(new fabric.Rect({
      left: 40, top: 400, width: 70, height: 70,
      fill: '#ffffff', stroke: teal, strokeWidth: 2,
      rx: 4, ry: 4,
      name: 'qr_frame', selectable: true
    }));

    canvas.add(new fabric.IText('{qr}', {
      left: 75, top: 435,
      fontSize: 12, fontFamily: 'Inter',
      fill: grayCol, originX: 'center', originY: 'center',
      name: 'qr_label', selectable: true
    }));

    canvas.add(new fabric.Rect({
      left: 125, top: 400, width: 60, height: 60,
      fill: '#ffffff', stroke: gold, strokeWidth: 2,
      rx: 4, ry: 4,
      name: 'logo_frame', selectable: true
    }));

    canvas.add(new fabric.IText('{logo}', {
      left: 155, top: 430,
      fontSize: 12, fontFamily: 'Inter',
      fill: grayCol, originX: 'center', originY: 'center',
      name: 'logo_label', selectable: true
    }));

    // ════════════ کد (پایین راست) ════════════
    canvas.add(new fabric.IText('#{code}', {
      left: 560, top: 415,
      fontSize: 22, fontFamily: 'monospace',
      fontWeight: 'bold',
      fill: primary, originX: 'right',
      name: 'code', selectable: true
    }));

    // ════════════ جدول اطلاعات (پایین) ════════════
    var rows = [
      { t: 'Stone: {stoneEn}',            y: 480 },
      { t: 'Metal: {metalEn} ({carat})', y: 505 },
      { t: 'Size: {length}*{width} mm',  y: 530 },
      { t: 'Weight: {weight} gr',        y: 555 }
    ];
    rows.forEach(function (row, i) {
      canvas.add(new fabric.IText(row.t, {
        left: 560, top: row.y,
        fontSize: 14, fontFamily: 'Inter',
        fill: textCol, originX: 'right',
        name: 'table_row_' + i,
        selectable: true
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
      h += '<label style="font-size:11px;display:block;margin-top:6px;">متن<input type="text" id="prop-text" value="' + (a.text || '').replace(/"/g, '&quot;').replace(/\n/g, '\\n') + '" style="width:100%;padding:4px;border:1px solid #ccc;border-radius:4px;font-family:monospace;"></label>';
      h += '<label style="font-size:11px;display:block;margin-top:6px;">اندازه فونت<input type="number" id="prop-fs" value="' + (a.fontSize || 12) + '" style="width:100%;padding:4px;border:1px solid #ccc;border-radius:4px;"></label>';
      h += '<label style="font-size:11px;display:block;margin-top:6px;">رنگ<input type="color" id="prop-fill" value="' + (a.fill || '#000000') + '" style="width:100%;height:30px;padding:2px;border:1px solid #ccc;border-radius:4px;"></label>';
      h += '<label style="font-size:11px;display:block;margin-top:6px;">فونت<input type="text" id="prop-ff" value="' + (a.fontFamily || 'Inter') + '" style="width:100%;padding:4px;border:1px solid #ccc;border-radius:4px;"></label>';
    }
    if (isRect || isImg) {
      h += '<label style="font-size:11px;display:block;margin-top:6px;">عرض<input type="number" id="prop-w" value="' + Math.round(a.width * (a.scaleX || 1)) + '" style="width:100%;padding:4px;border:1px solid #ccc;border-radius:4px;"></label>';
      h += '<label style="font-size:11px;display:block;margin-top:6px;">ارتفاع<input type="number" id="prop-h" value="' + Math.round(a.height * (a.scaleY || 1)) + '" style="width:100%;padding:4px;border:1px solid #ccc;border-radius:4px;"></label>';
    }
    if (isRect) {
      h += '<label style="font-size:11px;display:block;margin-top:6px;">رنگ خط<input type="color" id="prop-stroke" value="' + (a.stroke || '#000000') + '" style="width:100%;height:30px;padding:2px;border:1px solid #ccc;border-radius:4px;"></label>';
      h += '<label style="font-size:11px;display:block;margin-top:6px;">رنگ پر<input type="color" id="prop-fill-r" value="' + (a.fill || '#ffffff') + '" style="width:100%;height:30px;padding:2px;border:1px solid #ccc;border-radius:4px;"></label>';
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
    var t = document.getElementById('prop-text'); if (t) a.set('text', t.value.replace(/\\n/g, '\n'));
    var fs = document.getElementById('prop-fs'); if (fs) a.set('fontSize', parseFloat(fs.value));
    var f = document.getElementById('prop-fill'); if (f) a.set('fill', f.value);
    var fr = document.getElementById('prop-fill-r'); if (fr) a.set('fill', fr.value);
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
    if (!canvas || !currentCertId) {
      alert('Canvas آماده نیست');
      return;
    }
    var json = canvas.toJSON(['selectable', 'evented', 'name', 'data']);
    // اضافه کردن ابعاد canvas
    json.canvas_width  = CANVAS_W;
    json.canvas_height = CANVAS_H;
    var jsonStr = JSON.stringify(json);

    if (window.Livewire && window.Livewire.dispatch) {
      try {
        window.Livewire.dispatch('designer-save', { json: jsonStr });
        showSaveToast();
        return;
      } catch (e) { console.warn('dispatch failed:', e); }
    }

    fetch('/certificates/' + currentCertId + '/design', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-TOKEN': (document.querySelector('meta[name="csrf-token"]') || {}).content || ''
      },
      body: JSON.stringify({ design_data: json })
    }).then(function (r) { return r.json(); })
      .then(function () { showSaveToast(); })
      .catch(function (e) { alert('خطا در ذخیره: ' + e.message); });
  }

  function showSaveToast() {
    var t = document.createElement('div');
    t.style.cssText = 'position:fixed;bottom:20px;right:20px;background:#27ae60;color:#fff;padding:12px 20px;border-radius:10px;font-weight:700;z-index:9999;box-shadow:0 4px 12px rgba(0,0,0,.3);';
    t.textContent = '✅ طراحی ذخیره شد';
    document.body.appendChild(t);
    setTimeout(function () { t.remove(); }, 2000);
  }

  function resetToDefault() {
    if (!canvas) return;
    if (!confirm('طرح به حالت پیش‌فرض برگردد؟')) return;
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
# ۳) Designer Blade — با wait for script
# ═══════════════════════════════════════════════════════════════
DESIGNER_BLADE = r'''<div class="p-6" dir="rtl"
     x-data="designerPage({
         certId: {{ $certificate?->id ?? 'null' }},
         designJson: {!! $designJson ?: 'null' !!}
     })"
     x-init="boot()">
    <div class="flex items-center justify-between mb-4 flex-wrap gap-2">
        <h1 class="text-2xl font-bold" style="color:#0d5c63;">
            🎨 ویرایشگر شناسنامه
            @if($certificate)
                <span class="text-sm font-normal text-gray-500">#{{ $certificate->code }}</span>
            @endif
        </h1>
        <div class="flex gap-2 flex-wrap">
            <button type="button" onclick="window.ShopGunDesigner.addText()"
                    class="px-3 py-2 bg-teal-600 text-white rounded-lg text-sm hover:bg-teal-700">
                ➕ متن
            </button>
            <button type="button" onclick="window.ShopGunDesigner.addRect()"
                    class="px-3 py-2 bg-teal-600 text-white rounded-lg text-sm hover:bg-teal-700">
                ▭ کادر
            </button>
            <button type="button" onclick="window.ShopGunDesigner.resetToDefault()"
                    class="px-3 py-2 bg-amber-500 text-white rounded-lg text-sm font-bold hover:bg-amber-600">
                ↺ ریست
            </button>
            <button type="button" onclick="window.ShopGunDesigner.saveDesign()"
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
                              title="کلیک = کپی">
                            {{ $v }}
                        </span>
                    @endforeach
                </div>
            </div>
        </div>
    </div>
</div>

<script>
    // ★ تعریف Alpine data برای wait-for-script
    document.addEventListener('alpine:init', function () {
        Alpine.data('designerPage', function (cfg) {
            return {
                ready: false,
                initCount: 0,
                certId: cfg.certId,
                designJson: cfg.designJson,

                boot() {
                    var self = this;
                    var check = function () {
                        if (window.ShopGunDesigner) {
                            self.ready = true;
                            // بعد از ظاهر شدن canvas
                            self.$nextTick(function () {
                                window.ShopGunDesigner.init(self.certId, self.designJson);
                            });
                        } else {
                            self.initCount++;
                            if (self.initCount > 50) {
                                console.error('ShopGunDesigner بارگذاری نشد');
                                return;
                            }
                            setTimeout(check, 150);
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
# ۴) Layout — از defer استفاده نکن برای cert-designer
# ═══════════════════════════════════════════════════════════════
def update_layout():
    layout = PROJECT / "resources/views/components/layouts/app.blade.php"
    if not layout.exists():
        print("  ⚠️ Layout پیدا نشد")
        return

    with open(layout, 'r', encoding='utf-8') as f:
        content = f.read()

    # حذف نسخه قدیمی با defer
    content = content.replace(
        '<script src="{{ asset(\'js/cert-designer.js\') }}?v=1" defer></script>',
        ''
    )
    content = content.replace(
        '<script src="{{ asset(\'js/cert-designer.js\') }}" defer></script>',
        ''
    )

    # اضافه کردن بدون defer قبل از @stack
    if 'cert-designer.js' not in content:
        new_tags = (
            '<script src="{{ asset(\'js/cert-card.js\') }}?v=2"></script>\n'
            '    <script src="{{ asset(\'js/cert-designer.js\') }}?v=2"></script>\n'
            '    @stack(\'scripts\')'
        )
        # حذف cert-card.js قدیمی
        content = content.replace(
            '<script src="{{ asset(\'js/cert-card.js\') }}?v=1" defer></script>',
            ''
        )
        content = content.replace(
            '@stack(\'scripts\')',
            new_tags,
            1
        )
        with open(layout, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        print("  ✓ Layout آپدیت شد (cert-designer بدون defer)")
    else:
        # فقط defer رو بردار
        if 'cert-designer.js" defer' in content or "cert-designer.js' defer" in content:
            content = content.replace(
                '<script src="{{ asset(\'js/cert-designer.js\') }}?v=1" defer></script>',
                '<script src="{{ asset(\'js/cert-designer.js\') }}?v=2"></script>'
            )
            with open(layout, 'w', encoding='utf-8', newline='\n') as f:
                f.write(content)
            print("  ✓ defer حذف شد")

# ═══════════════════════════════════════════════════════════════
# ۵) Designer.php — با ذخیره‌ی صحیح
# ═══════════════════════════════════════════════════════════════
DESIGNER_PHP = r'''<?php

namespace App\Livewire\Certificates;

use App\Models\Certificate;
use Livewire\Attributes\On;
use Livewire\Component;

class Designer extends Component
{
    public ?Certificate $certificate = null;
    public string $designJson = 'null';
    public string $statusMessage = '';

    public function mount(?Certificate $certificate = null): void
    {
        if ($certificate && $certificate->exists) {
            $this->certificate = $certificate;
        } else {
            $this->certificate = Certificate::query()->latest()->first();
        }

        if ($this->certificate && !empty($this->certificate->design_data)) {
            $design = $this->certificate->design_data;
            if (is_array($design)) {
                $this->designJson = json_encode($design, JSON_UNESCAPED_UNICODE);
            }
        }
    }

    #[On('designer-save')]
    public function saveDesign($json = null): void
    {
        if (is_string($json)) {
            $design = json_decode($json, true);
        } elseif (is_array($json)) {
            $design = $json;
        } else {
            $this->statusMessage = 'داده نامعتبر';
            return;
        }

        if (!is_array($design)) {
            $this->statusMessage = 'JSON نامعتبر';
            return;
        }

        if (!$this->certificate) {
            $this->statusMessage = 'شناسنامه‌ای موجود نیست';
            return;
        }

        $this->certificate->update(['design_data' => $design]);
        $this->designJson = is_string($json) ? $json : json_encode($json, JSON_UNESCAPED_UNICODE);
        $this->statusMessage = '✅ طراحی ذخیره شد در ' . now()->format('H:i:s');
        $this->dispatch('notify', type: 'success', message: 'طراحی ذخیره شد');
    }

    public function resetDesign(): void
    {
        if ($this->certificate) {
            $this->certificate->update(['design_data' => null]);
            $this->designJson = 'null';
            $this->statusMessage = '↺ طراحی ریست شد';
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
# اجرا
# ═══════════════════════════════════════════════════════════════
def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  Fix Designer + Renderer                                      ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    print("📦 Backup...")
    for rel in [
        "app/Services/CertRenderer.php",
        "app/Livewire/Certificates/Designer.php",
        "resources/views/livewire/certificates/designer.blade.php",
        "resources/views/components/layouts/app.blade.php",
    ]:
        backup(rel)

    print("\n📄 نوشتن فایل‌ها...")
    write("app/Services/CertRenderer.php", CERT_RENDERER)
    write("app/Livewire/Certificates/Designer.php", DESIGNER_PHP)
    write("public/js/cert-designer.js", CERT_DESIGNER_JS)
    write("resources/views/livewire/certificates/designer.blade.php", DESIGNER_BLADE)

    print("\n🔗 بروزرسانی Layout...")
    update_layout()

    print("\n" + "═" * 64)
    print("✅ تمام!")
    print("═" * 64)
    print(f"""
📋 اجرا کنید:

  cd {PROJECT}
  php artisan optimize:clear
  php artisan view:clear

  ⚠️ سرور رو ببند (Ctrl+C) و دوباره باز کن:
  php artisan serve

مرورگر: Ctrl+Shift+R

🎯 چه چیزی حل شد:
  ✓ Designer با طرح پیش‌فرض کامل باز می‌شه (همه ۱۲ عنصر)
  ✓ خطای alphabetical suppress شد
  ✓ cert-designer.js با ترتیب درست لود می‌شه
  ✓ CertRenderer از design_data پشتیبانی می‌کنه
  ✓ دکمه ریست اضافه شد
  ✓ متغیرها با کلیک کپی می‌شن
""")

if __name__ == "__main__":
    main()