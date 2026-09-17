#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Port کامل Legacy → Laravel
همه‌ی امکانات + استایل از جواهری مشاهیر v6.14
"""
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
# ۱) CSS کامل — Legacy Style
# ═══════════════════════════════════════════════════════════════
FULL_CSS = r'''/* ═══════════════════════════════════════════════════════════════
   ShopGun V2 — Legacy Style Port
   ═══════════════════════════════════════════════════════════════ */

:root{
  --primary:#1a5276;--primary-light:#2980b9;--gold:#c9a84c;--gold-light:#f0d68a;--gold-dark:#8b6914;
  --bg:#f5f0e8;--bg-card:#fff;--text:#2c3e50;--text-light:#7f8c8d;--border:#d4c5a9;
  --success:#27ae60;--danger:#e74c3c;--warn:#f39c12;
  --shadow:0 4px 20px rgba(0,0,0,.08);--shadow-lg:0 8px 40px rgba(0,0,0,.12);
  --cert-gold:#b8860b;--cert-brown:#6b4423;
  --table-title:#0d5c63;--table-title-text:#e0f7f8;--table-border:#7fbfc4;--thead-bg:#f8f6f0;
  --label-w:100mm;--label-h:50mm;
  --velvet:#6b0f1a;--velvet-dark:#4a0511;--velvet-light:#8b1a2b;
  --basalam:#00b894;--basalam-dark:#00806a;
}

[data-theme="dark"]{
  --primary:#4a90c2;--primary-light:#66a8d8;--gold:#d4b85a;--gold-light:#e8d090;--gold-dark:#b89840;
  --bg:#0f1419;--bg-card:#1a2029;--text:#e0e6ed;--text-light:#8b97a8;--border:#2a3441;
  --success:#2ecc71;--table-title:#0d4a52;--table-border:#3d6b70;--thead-bg:#232b36;
}

*{margin:0;padding:0;box-sizing:border-box}
body{font-family:'Vazirmatn',Tahoma,sans-serif;background:var(--bg);color:var(--text);min-height:100vh}

/* ═══════ Header ═══════ */
.sg-main-header{background:linear-gradient(135deg,var(--primary) 0%,#0d3b5e 100%);padding:10px 18px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;position:relative}
.sg-header-right{display:flex;align-items:center;gap:10px}
.sg-logo-container{width:44px;height:44px;background:var(--gold);border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:20px;overflow:hidden;cursor:pointer;flex-shrink:0}
.sg-logo-container img{width:100%;height:100%;object-fit:cover}
.sg-header-title h1{color:#fff;font-size:16px;font-weight:700}
.sg-header-title p{color:var(--gold-light);font-size:10.5px;margin-top:2px}
.sg-header-date{background:rgba(255,255,255,.12);color:#fff;padding:6px 14px;border-radius:20px;font-size:12px;font-weight:600;border:1px solid rgba(255,255,255,.15)}
.sg-header-actions{display:flex;gap:6px;align-items:center;flex-wrap:wrap}
.sg-header-icon-btn{width:34px;height:34px;border-radius:50%;background:rgba(255,255,255,.15);color:#fff;border:1px solid rgba(255,255,255,.2);cursor:pointer;font-size:15px;display:flex;align-items:center;justify-content:center;position:relative;text-decoration:none;transition:.2s}
.sg-header-icon-btn:hover{background:rgba(255,255,255,.25)}

/* ═══════ Tabs Bar ═══════ */
.sg-tabs-bar{display:flex;gap:6px;padding:10px 18px 0;flex-wrap:wrap;align-items:center}
.sg-tab-btn{padding:9px 18px;border:none;background:var(--bg-card);border-radius:12px 12px 0 0;font-family:inherit;font-size:12.5px;font-weight:700;cursor:pointer;color:var(--text-light);border-bottom:3px solid transparent;position:relative;text-decoration:none;display:inline-flex;align-items:center;gap:6px}
.sg-tab-btn.active,.sg-tab-btn:hover{color:var(--primary);border-bottom-color:var(--gold)}

/* ═══════ Toolbar ═══════ */
.sg-toolbar{background:var(--bg-card);margin:0 18px 14px;padding:11px 16px;border-radius:0 0 16px 16px;box-shadow:var(--shadow);display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;border:1px solid var(--border);border-top:none}
.sg-toolbar-right{display:flex;align-items:center;gap:6px;flex-wrap:wrap}

/* ═══════ Buttons ═══════ */
.btn{padding:8px 16px;border:none;border-radius:10px;font-family:inherit;font-size:12.5px;font-weight:600;cursor:pointer;display:inline-flex;align-items:center;gap:5px;transition:.15s;text-decoration:none}
.btn:hover{transform:translateY(-1px)}
.btn-primary{background:linear-gradient(135deg,var(--gold),var(--gold-dark));color:#fff}
.btn-secondary{background:var(--primary);color:#fff}
.btn-outline{background:transparent;border:2px solid var(--border);color:var(--text)}
.btn-success{background:var(--success);color:#fff}
.btn-danger{background:var(--danger);color:#fff}
.btn-warn{background:var(--warn);color:#fff}
.btn-velvet{background:linear-gradient(135deg,var(--velvet-light),var(--velvet-dark));color:#fff}
.btn-basalam{background:linear-gradient(135deg,var(--basalam),var(--basalam-dark));color:#fff}
.btn-mahak{background:linear-gradient(135deg,#3498db,#1a5276);color:#fff}
.btn-sm{padding:5px 10px;font-size:11px}

/* ═══════ Table ═══════ */
.sg-table-container{margin:0 18px 18px;background:var(--bg-card);border-radius:16px;box-shadow:var(--shadow);overflow:hidden;border:1px solid var(--border)}
.sg-table-header{padding:12px 18px;background:linear-gradient(135deg,var(--primary) 0%,#0d3b5e 100%);color:#fff;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px}
.sg-table-header h2{font-size:13.5px;display:flex;align-items:center;gap:8px}
.sg-table-scroll{overflow-x:auto;max-height:70vh}
.sg-table{width:100%;border-collapse:collapse}
.sg-table thead th{background:var(--thead-bg);padding:10px 12px;text-align:right;font-size:11.5px;font-weight:700;color:var(--primary);border-bottom:2px solid var(--border);white-space:nowrap;position:sticky;top:0;z-index:2}
.sg-table tbody td{padding:8px 12px;border-bottom:1px solid var(--border);font-size:12px;vertical-align:middle;white-space:nowrap}
.sg-table tbody tr:hover{background:rgba(201,168,76,.05)}

/* ═══════ Status Badges ═══════ */
.sg-status-badge{display:inline-flex;align-items:center;gap:5px;padding:4px 12px;border-radius:20px;font-size:11px;font-weight:700;white-space:nowrap;color:#fff;cursor:pointer}
.sg-status-badge.pending{background:linear-gradient(135deg,#ffb74d,#ff9800)}
.sg-status-badge.final-check{background:linear-gradient(135deg,#42a5f5,#2980b9)}
.sg-status-badge.courier{background:linear-gradient(135deg,#4caf50,#27ae60)}

.sg-channel-cell{display:inline-flex;align-items:center;gap:4px;padding:3px 10px;border-radius:20px;font-size:11px;font-weight:700;color:#fff}
.sg-channel-cell.telegram{background:linear-gradient(135deg,#29b6f6,#0288d1)}
.sg-channel-cell.instagram{background:linear-gradient(135deg,#e91e63,#c2185b)}
.sg-channel-cell.website{background:linear-gradient(135deg,var(--velvet-light),var(--velvet-dark))}
.sg-channel-cell.phone{background:linear-gradient(135deg,#66bb6a,#388e3c)}
.sg-channel-cell.direct{background:linear-gradient(135deg,#ffb74d,#f57c00)}
.sg-channel-cell.basalam{background:linear-gradient(135deg,var(--basalam),var(--basalam-dark))}

.sg-row-num{display:inline-flex;align-items:center;justify-content:center;min-width:26px;height:26px;padding:0 6px;background:var(--bg);border:1px solid var(--border);border-radius:50%;font-size:11px;font-weight:700;color:var(--primary)}

.sg-action-btns{display:flex;gap:4px}
.sg-action-btn{width:28px;height:28px;border:none;border-radius:8px;cursor:pointer;display:flex;align-items:center;justify-content:center;font-size:12px;text-decoration:none}
.sg-action-btn.view{background:rgba(41,128,185,.15);color:#2980b9}
.sg-action-btn.print{background:rgba(39,174,96,.15);color:#27ae60}
.sg-action-btn.edit{background:rgba(155,89,182,.15);color:#9b59b6}
.sg-action-btn.delete{background:rgba(231,76,60,.15);color:#e74c3c}

/* ═══════ Modal ═══════ */
.sg-modal-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.65);backdrop-filter:blur(8px);z-index:1000;align-items:flex-start;justify-content:center;padding:14px;overflow-y:auto}
.sg-modal-overlay.active{display:flex}
.sg-modal{background:var(--bg-card);border-radius:20px;width:100%;max-width:880px;max-height:92vh;overflow-y:auto;box-shadow:var(--shadow-lg);margin:auto}
.sg-modal-header{padding:14px 20px;background:linear-gradient(135deg,var(--primary) 0%,#0d3b5e 100%);color:#fff;border-radius:20px 20px 0 0;display:flex;align-items:center;justify-content:space-between;position:sticky;top:0;z-index:5}
.sg-modal-header h2{font-size:15px;display:flex;align-items:center;gap:8px}
.sg-modal-close{width:30px;height:30px;border:none;background:rgba(255,255,255,.2);color:#fff;border-radius:50%;cursor:pointer;font-size:14px}
.sg-modal-body{padding:18px}
.sg-modal-footer{padding:12px 20px;border-top:1px solid var(--border);display:flex;justify-content:space-between;background:var(--bg);border-radius:0 0 20px 20px;gap:8px;flex-wrap:wrap}

/* ═══════ Form ═══════ */
.form-group{position:relative;margin-bottom:14px;padding-top:6px}
.form-control{width:100%;padding:11px 12px;border:2px solid var(--border);border-radius:10px;font-family:inherit;font-size:12.5px;background:var(--bg);color:var(--text);box-sizing:border-box}
.form-control:focus{outline:none;border-color:var(--gold);box-shadow:0 0 0 3px rgba(201,168,76,.15)}
.form-group>label{position:absolute;top:0;right:12px;background:var(--bg-card);padding:0 6px;font-size:10.5px;font-weight:600;color:var(--primary);z-index:1;border-radius:4px;line-height:1}

.form-row{display:grid;gap:14px;margin-bottom:14px}
.form-row.cols-5{grid-template-columns:repeat(5,1fr)}
.form-row.cols-3{grid-template-columns:repeat(3,1fr)}
.form-row.cols-2{grid-template-columns:1fr 1fr}

/* ═══════ Order Product Row ═══════ */
.sg-product-row{display:grid;grid-template-columns:1.2fr 1.8fr 1.2fr 70px 42px;gap:10px;margin-bottom:14px;align-items:start;position:relative}
.sg-sku-wrap{position:relative;margin-bottom:0;padding-top:6px}
.sg-sku-wrap>label{position:absolute;top:0;right:12px;background:var(--bg-card);padding:0 6px;font-size:10.5px;font-weight:600;color:var(--primary);z-index:1;border-radius:4px;line-height:1}
.sg-sku-wrap .form-control{padding-right:34px}
.sg-sku-wrap::before{content:'🔍';position:absolute;right:12px;top:50%;transform:translateY(-50%);font-size:12px;color:var(--text-light);pointer-events:none;z-index:2}

.sg-sku-suggestions{position:absolute;top:100%;right:0;left:0;background:var(--bg-card);border:2px solid var(--gold);border-radius:10px;margin-top:4px;box-shadow:var(--shadow-lg);z-index:200;max-height:280px;overflow-y:auto;display:none}
.sg-sku-suggestions.show{display:block}
.sg-sku-suggestion{padding:10px 14px;cursor:pointer;font-size:12.5px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;gap:8px;align-items:center}
.sg-sku-suggestion:hover{background:rgba(201,168,76,.1)}
.sg-sku-suggestion .info{flex:1;min-width:0}
.sg-sku-suggestion .title{font-weight:700;color:var(--primary);font-size:12px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.sg-sku-suggestion .sku-txt{font-family:monospace;font-size:11px;color:var(--text-light);direction:ltr;margin-top:2px}
.sg-sku-suggestion .price{font-size:11.5px;color:var(--gold-dark);font-weight:700}

.sg-phone-suggestions{position:absolute;top:100%;right:0;left:0;background:var(--bg-card);border:2px solid var(--gold);border-radius:10px;margin-top:6px;box-shadow:var(--shadow-lg);z-index:100;max-height:240px;overflow-y:auto;display:none}
.sg-phone-suggestions.show{display:block}
.sg-phone-suggestion{padding:10px 14px;cursor:pointer;font-size:12.5px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;gap:8px;align-items:center}
.sg-phone-suggestion:hover{background:rgba(201,168,76,.1)}
.sg-phone-suggestion .name{font-weight:700;color:var(--primary);font-size:12.5px}
.sg-phone-suggestion .phone{font-family:monospace;font-size:11.5px;color:var(--text-light);direction:ltr}

/* ═══════ Certificate Card ═══════ */
.certificate{background:#fffef9;color:#2c3e50;position:relative;overflow:hidden;box-shadow:0 10px 40px rgba(0,0,0,.3);font-family:'Inter','Vazirmatn',sans-serif;font-size:11px;border:1px solid #999;border-radius:10px;box-sizing:border-box}
.cert-bg-layer{position:absolute;inset:0;background-size:cover;background-position:center;background-repeat:no-repeat;z-index:0;opacity:.12;border-radius:10px;pointer-events:none}
.cert-main{position:relative;z-index:3;width:100%;height:100%;padding:8px;display:flex;flex-direction:column;box-sizing:border-box}
.cert-top-section{display:flex;gap:8px;margin-bottom:4px;overflow:hidden;flex:0 0 auto}
.cert-right-text{flex:1 1 auto;min-width:60px;display:flex;flex-direction:column;padding:2px 0 2px 4px;overflow:hidden}
.cert-title-script{font-family:'Great Vibes',cursive;color:var(--cert-brown);line-height:1;text-align:right;font-size:20px}
.cert-subtitle-script{font-family:'Playfair Display',serif;font-size:8px;color:var(--cert-brown);text-align:right;margin-bottom:6px;font-style:italic}
.cert-desc-area{flex:1 1 auto;text-align:right;overflow:hidden;display:flex;align-items:center;justify-content:flex-end;min-height:0}
.cert-desc-area img{max-width:100%;max-height:100%;object-fit:contain;margin:auto;display:block}
.cert-auth-text{font-family:'Playfair Display',serif;color:var(--cert-brown);line-height:1.5;text-align:right;font-size:7px}
.cert-img-frame-wrap{flex:0 0 auto;position:relative;padding:4px;border:1px solid var(--cert-gold);border-radius:8px;background:#fff;box-sizing:border-box;overflow:hidden;align-self:flex-start}
.cert-img-frame{width:100%;height:100%;border:1.5px solid var(--cert-gold);border-radius:6px;overflow:hidden;background:#fff;position:relative}
.cert-img-frame img{width:100%;height:100%;object-fit:contain;display:block}
.cert-serial-balloon{position:absolute;bottom:6px;left:50%;transform:translateX(-50%);background:rgba(0,0,0,.55);color:#fff;font-family:monospace;font-size:5px;font-weight:700;padding:2px 6px;border-radius:8px;white-space:nowrap;border:1px solid rgba(255,255,255,.25);pointer-events:none;z-index:2}
.cert-qr-panel{display:flex;gap:6px;align-items:center;padding:4px 2px;margin-bottom:4px;justify-content:flex-end;flex-wrap:nowrap}
.cert-qr-url{color:var(--primary);font-weight:600;margin-bottom:2px;min-width:15px;font-size:6px}
.cert-qr-wrap{display:flex;flex-direction:column;align-items:center;background:#fff;border:1px solid var(--table-title);border-radius:6px;padding:3px 4px;min-width:30px;box-sizing:border-box;flex-shrink:0}
.cert-qr-inner{display:flex;gap:6px;align-items:center;overflow:hidden}
.cert-qr-box{background:#fff;border-radius:3px;overflow:hidden;flex-shrink:0;box-sizing:border-box}
.cert-qr-box img{width:100%;height:100%;object-fit:contain;display:block}
.cert-code-inline{display:flex;flex-direction:column;align-items:flex-start;gap:2px;min-width:30px}
.cert-code-inline .lbl{font-size:6px;color:var(--text-light);text-transform:uppercase}
.cert-code-inline .val{font-family:monospace;font-weight:700;color:var(--primary);letter-spacing:.8px;font-size:11px}
.cert-logo-mini{display:flex;align-items:center;gap:4px;margin-right:auto;flex-wrap:nowrap;min-width:30px;max-width:50%;overflow:hidden}
.cert-logo-mini .ico{border:none;border-radius:4px;display:flex;align-items:center;justify-content:center;overflow:hidden;padding:0;background:transparent;flex-shrink:0}
.cert-logo-mini .ico img{width:100%;height:100%;object-fit:contain;display:block}
.cert-table-wrap{width:100%;flex:0 0 auto;border-radius:8px;overflow:hidden;border:1.5px solid var(--table-title);background:#fff;box-sizing:border-box}
.cert-bottom-table{width:100%;border-collapse:collapse;background:transparent;font-family:'Inter','Vazirmatn',sans-serif;table-layout:fixed;box-sizing:border-box}
.cert-bottom-table td{border:1px solid var(--table-border);vertical-align:middle;line-height:1.2;word-break:break-word;padding:2px 3px;box-sizing:border-box;overflow:hidden;text-overflow:ellipsis}
.cert-bottom-table .tbl-label{background:var(--table-title);color:var(--table-title-text);font-weight:700;text-align:right;font-size:8px}
.cert-bottom-table .tbl-value{background:#fff;color:#2c3e50;font-weight:600;text-align:right;font-size:8px}
.cert-bottom-table .unit{float:left;font-size:6px;color:#888;font-weight:400}

/* ═══════ Certificate Preview ═══════ */
.sg-cert-preview-overlay{display:none;position:fixed;inset:0;background:rgba(0,0,0,.9);backdrop-filter:blur(8px);z-index:2000;align-items:flex-start;justify-content:center;padding:14px;overflow-y:auto}
.sg-cert-preview-overlay.active{display:flex}
.sg-cert-preview-stage{display:flex;flex-direction:column;align-items:center;justify-content:center;width:100%;padding:14px;border-radius:16px;overflow:auto;min-height:220px}
.sg-cert-preview-actions{display:flex;justify-content:center;gap:8px;flex-wrap:wrap;padding:10px 14px;background:rgba(255,255,255,.12);backdrop-filter:blur(10px);border:1px solid rgba(255,255,255,.2);border-radius:14px}

/* ═══════ Settings Panels ═══════ */
.sg-settings-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:14px;padding:20px 18px}
.sg-settings-card{background:var(--bg-card);border-radius:16px;padding:16px;box-shadow:var(--shadow);border:1px solid var(--border)}
.sg-settings-card h3{font-size:13px;color:var(--primary);margin-bottom:10px;display:flex;align-items:center;gap:8px;padding-bottom:8px;border-bottom:2px solid var(--border)}

/* ═══════ Stones Grid ═══════ */
.sg-stones-grid{display:grid;grid-template-columns:repeat(8,1fr);gap:8px;max-height:600px;overflow-y:auto;padding:8px;background:var(--bg);border-radius:12px}
.sg-stone-card{position:relative;background:var(--bg-card);border:2px solid var(--border);border-radius:10px;padding:8px 4px;display:flex;flex-direction:column;align-items:center;gap:4px;min-height:90px;text-align:center;transition:all .2s}
.sg-stone-card:hover{border-color:var(--gold);transform:translateY(-2px);box-shadow:var(--shadow)}
.sg-stone-card .s-icon{width:44px;height:44px;display:flex;align-items:center;justify-content:center;font-size:24px;background:var(--bg);border-radius:8px;overflow:hidden}
.sg-stone-card .s-icon img{width:100%;height:100%;object-fit:contain}
.sg-stone-card .s-name{font-size:10.5px;font-weight:700;color:var(--primary)}
.sg-stone-card .s-origin{font-size:9px;color:var(--text-light)}

/* ═══════ Toast ═══════ */
.sg-toast-container{position:fixed;top:20px;left:20px;z-index:3000;display:flex;flex-direction:column;gap:10px;pointer-events:none}
.sg-toast{padding:11px 16px;border-radius:10px;color:#fff;font-size:12.5px;font-weight:600;box-shadow:0 4px 20px rgba(0,0,0,.25);display:flex;align-items:center;gap:8px;max-width:340px;pointer-events:auto;animation:sgToastIn .3s ease}
.sg-toast.success{background:var(--success)}
.sg-toast.error{background:var(--danger)}
.sg-toast.info{background:var(--primary-light)}
.sg-toast.warn{background:var(--warn)}
@keyframes sgToastIn{from{transform:translateX(-100%);opacity:0}to{transform:translateX(0);opacity:1}}

/* ═══════ Mobile Bar ═══════ */
.sg-mobile-bar{display:none;position:fixed;bottom:10px;left:10px;right:10px;background:rgba(255,255,255,.82);backdrop-filter:blur(18px);border:1px solid rgba(255,255,255,.5);border-radius:22px;padding:6px 4px;z-index:500;box-shadow:0 8px 32px rgba(0,0,0,.22)}
[data-theme="dark"] .sg-mobile-bar{background:rgba(26,32,41,.85);border-color:rgba(255,255,255,.1)}
.sg-mobile-bar-inner{display:flex;justify-content:space-around;gap:2px}
.sg-mobile-bar-btn{flex:1;padding:5px 2px;border:none;background:transparent;border-radius:14px;cursor:pointer;display:flex;flex-direction:column;align-items:center;gap:1px;font-family:inherit;font-size:9px;font-weight:600;color:var(--text-light);text-decoration:none}
.sg-mobile-bar-btn.active{background:linear-gradient(135deg,rgba(201,168,76,.25),rgba(201,168,76,.1));color:var(--gold-dark);font-weight:700}
.sg-mobile-bar-btn .ico{font-size:18px}
.sg-mobile-bar-btn.add{background:linear-gradient(135deg,var(--gold),var(--gold-dark));color:#fff}

/* ═══════ Responsive ═══════ */
@media(max-width:900px){
  .sg-stones-grid{grid-template-columns:repeat(4,1fr)}
  .form-row.cols-5{grid-template-columns:repeat(2,1fr)}
  .sg-toolbar,.sg-table-container,.sg-settings-grid{margin-left:10px;margin-right:10px}
}
@media(max-width:768px){
  .sg-mobile-bar{display:block}
  body{padding-bottom:75px}
  .sg-tabs-bar{display:none!important}
  .form-row.cols-3,.form-row.cols-2{grid-template-columns:1fr}
  .sg-product-row{grid-template-columns:1fr}
  .sg-toolbar{flex-direction:column;align-items:stretch}
  .sg-toolbar-right{width:100%}
  .sg-settings-grid{grid-template-columns:1fr}
}
@media(max-width:600px){.sg-stones-grid{grid-template-columns:repeat(3,1fr)}}

::-webkit-scrollbar{width:6px;height:6px}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px}
'''

# ═══════════════════════════════════════════════════════════════
# ۲) Layout کامل
# ═══════════════════════════════════════════════════════════════
LAYOUT_BLADE = r'''<!DOCTYPE html>
<html lang="fa" dir="rtl" data-theme="{{ \App\Models\AppSetting::get('theme', 'light') }}">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width,initial-scale=1.0,viewport-fit=cover">
    <meta name="theme-color" content="#1a5276">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>جواهری مشاهیر</title>

    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Great+Vibes&family=Playfair+Display:wght@400;700&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">

    <script>
        (function(){
            var t = localStorage.getItem('theme') || '{{ \App\Models\AppSetting::get("theme", "light") }}';
            document.documentElement.setAttribute('data-theme', t);
        })();
    </script>

    @vite(['resources/css/app.css', 'resources/js/app.js'])
    @livewireStyles

    <link rel="stylesheet" href="{{ asset('css/legacy.css') }}?v=1">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>

    @stack('styles')
</head>
<body>

@auth
    <livewire:global-search />
    <livewire:components.shipment-timeline />
    <livewire:orders.form-modal :key="'ofm'" />
    <livewire:orders.view-modal :key="'ovm'" />
    <livewire:customers.profile-modal :key="'cpm'" />
    <livewire:certificates.view-modal :key="'cvm'" />
@endauth

{{-- ═══ Header ═══ --}}
<header class="sg-main-header">
    <div class="sg-header-right">
        <div class="sg-logo-container" id="headerLogo" onclick="document.getElementById('headerLogoInput').click()">
            @if(\App\Models\AppSetting::get('header_logo'))
                <img src="{{ \App\Models\AppSetting::get('header_logo') }}">
            @else
                💎
            @endif
        </div>
        <input type="file" id="headerLogoInput" accept="image/*" style="display:none" onchange="sgHandleHeaderLogo(event)">
        <div class="sg-header-title">
            <h1>{{ \App\Models\AppSetting::get('shop_name', 'جواهری مشاهیر') }}</h1>
            <p>مدیریت سفارشات و شناسنامه</p>
        </div>
    </div>

    <div class="sg-header-date" id="headerDate">📅 در حال بارگذاری...</div>

    <div class="sg-header-actions">
        <button class="sg-header-icon-btn" onclick="sgToggleTheme()" id="themeIconBtn">🌙</button>
        <a href="{{ route('activity-log') }}" wire:navigate class="sg-header-icon-btn" title="لاگ">📜</a>
        <a href="{{ route('settings.index') }}" wire:navigate class="sg-header-icon-btn" title="تنظیمات">⚙️</a>
    </div>
</header>

{{-- ═══ Tabs (Desktop) ═══ --}}
<div class="sg-tabs-bar">
    @php
        $tabs = [
            ['route' => 'orders.index',       'icon' => '📦', 'label' => 'سفارشات'],
            ['route' => 'customers.index',    'icon' => '👥', 'label' => 'مشتریان'],
            ['route' => 'certificates.index', 'icon' => '💎', 'label' => 'شناسنامه‌ها'],
            ['route' => 'reports.index',      'icon' => '📊', 'label' => 'گزارش‌ها'],
            ['route' => 'settings.index',     'icon' => '⚙️', 'label' => 'تنظیمات'],
        ];
    @endphp
    @foreach($tabs as $tab)
        @php $isActive = request()->routeIs($tab['route']) || request()->routeIs(explode('.', $tab['route'])[0].'.*'); @endphp
        <a href="{{ route($tab['route']) }}" wire:navigate class="sg-tab-btn {{ $isActive ? 'active' : '' }}">
            <span>{{ $tab['icon'] }}</span>
            <span>{{ $tab['label'] }}</span>
        </a>
    @endforeach
</div>

{{-- ═══ Main Content ═══ --}}
<main>
    {{ $slot }}
</main>

{{-- ═══ Mobile Bar ═══ --}}
<nav class="sg-mobile-bar">
    <div class="sg-mobile-bar-inner">
        @php
            $mobileItems = [
                ['route' => 'dashboard',          'icon' => '🏠', 'label' => 'خانه'],
                ['route' => 'orders.index',       'icon' => '📦', 'label' => 'سفارش'],
                ['route' => 'orders.create',      'icon' => '➕', 'label' => 'جدید',  'is_add' => true],
                ['route' => 'certificates.index', 'icon' => '💎', 'label' => 'کارت'],
                ['route' => 'settings.index',     'icon' => '⚙️', 'label' => 'تنظیم'],
            ];
        @endphp
        @foreach($mobileItems as $item)
            @php
                $isActive = request()->routeIs($item['route']) || request()->routeIs(explode('.', $item['route'])[0].'.*');
                $cls = 'sg-mobile-bar-btn';
                if (!empty($item['is_add'])) $cls .= ' add';
                elseif ($isActive) $cls .= ' active';
            @endphp
            <a href="{{ route($item['route']) }}" wire:navigate class="{{ $cls }}">
                <span class="ico">{{ $item['icon'] }}</span>
                <span>{{ $item['label'] }}</span>
            </a>
        @endforeach
    </div>
</nav>

{{-- ═══ Toast Container ═══ --}}
<div class="sg-toast-container" id="toastContainer"></div>

<script>
    // ═══ Theme Toggle ═══
    function sgToggleTheme() {
        var html = document.documentElement;
        var cur = html.getAttribute('data-theme') || 'light';
        var next = cur === 'dark' ? 'light' : 'dark';
        html.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
        document.getElementById('themeIconBtn').textContent = next === 'dark' ? '☀️' : '🌙';

        // ذخیره در سرور
        fetch('{{ route("settings.update-theme") }}', {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-CSRF-TOKEN': '{{ csrf_token() }}'},
            body: JSON.stringify({theme: next})
        }).catch(function(){});
    }

    // ═══ Toast ═══
    window.sgToast = function(msg, type) {
        type = type || 'info';
        var c = document.getElementById('toastContainer');
        if (!c) return;
        var icons = {success: '✅', error: '❌', info: 'ℹ️', warn: '⚠️'};
        var t = document.createElement('div');
        t.className = 'sg-toast ' + type;
        t.innerHTML = (icons[type] || 'ℹ️') + ' ' + msg;
        c.appendChild(t);
        setTimeout(function() { if (t.parentNode) t.remove(); }, 3200);
    };

    // ═══ Header Logo Upload ═══
    function sgHandleHeaderLogo(e) {
        var f = e.target.files[0]; if (!f) return;
        if (f.size > 2 * 1024 * 1024) { sgToast('حجم زیاد (max 2MB)', 'error'); return; }
        var r = new FileReader();
        r.onload = function(ev) {
            var data = ev.target.result;
            document.getElementById('headerLogo').innerHTML = '<img src="' + data + '">';
            // ذخیره به سرور
            fetch('{{ route("settings.update-header-logo") }}', {
                method: 'POST',
                headers: {'Content-Type': 'application/json', 'X-CSRF-TOKEN': '{{ csrf_token() }}'},
                body: JSON.stringify({logo: data})
            }).then(function() { sgToast('لوگو ذخیره شد ✅', 'success'); });
        };
        r.readAsDataURL(f);
    }

    // ═══ Header Date ═══
    function sgUpdateHeaderDate() {
        var el = document.getElementById('headerDate');
        if (!el) return;
        var d = new Date();
        var p = toPersianDate(d);
        var months = ['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور','مهر','آبان','آذر','دی','بهمن','اسفند'];
        el.innerHTML = '📅 ' + p.day + ' ' + months[p.month-1] + ' ' + p.year + ' · ' + String(d.getHours()).padStart(2,'0') + ':' + String(d.getMinutes()).padStart(2,'0');
    }
    function toPersianDate(d) {
        var gy=d.getFullYear(),gm=d.getMonth()+1,gd=d.getDate();
        var g_d_m=[0,31,59,90,120,151,181,212,243,273,304,334];
        var jy=(gy<=1600)?0:979;gy-=(gy<=1600)?621:1600;
        var gy2=(gm>2)?(gy+1):gy;
        var days=365*gy+Math.floor((gy2+3)/4)-Math.floor((gy2+99)/100)+Math.floor((gy2+399)/400)-80+gd+g_d_m[gm-1];
        jy+=33*Math.floor(days/12053);days%=12053;jy+=4*Math.floor(days/1461);days%=1461;
        if(days>365){jy+=Math.floor((days-1)/365);days=(days-1)%365}
        var jm=(days<186)?1+Math.floor(days/31):7+Math.floor((days-186)/30);
        var jd=1+((days<186)?(days%31):((days-186)%30));
        return {year:jy,month:jm,day:jd};
    }
    sgUpdateHeaderDate();
    setInterval(sgUpdateHeaderDate, 60000);

    // ═══ Init ═══
    document.addEventListener('DOMContentLoaded', function() {
        var cur = document.documentElement.getAttribute('data-theme');
        var icon = document.getElementById('themeIconBtn');
        if (icon) icon.textContent = cur === 'dark' ? '☀️' : '🌙';
    });

    // ═══ Livewire Notify Event ═══
    document.addEventListener('livewire:init', function() {
        Livewire.on('notify', function(data) {
            var p = Array.isArray(data) ? data[0] : data;
            sgToast(p.message || '', p.type || 'info');
        });
    });
</script>

@livewireScripts
@stack('scripts')
</body>
</html>
'''

# ═══════════════════════════════════════════════════════════════
# ۳) Routes کامل
# ═══════════════════════════════════════════════════════════════
ROUTES_WEB = r'''<?php

use Illuminate\Support\Facades\Route;
use Illuminate\Support\Facades\Auth;
use App\Livewire\Auth\Login;
use App\Livewire\Dashboard;
use App\Livewire\ActivityLog;
use App\Livewire\Orders\Index as OrdersIndex;
use App\Livewire\Orders\Create as OrdersCreate;
use App\Livewire\Orders\Show as OrdersShow;
use App\Livewire\Orders\Edit as OrdersEdit;
use App\Livewire\Orders\PrintLabel as OrdersPrintLabel;
use App\Livewire\Orders\BulkPrintLabels as OrdersBulkPrintLabels;
use App\Livewire\Orders\CourierList as OrdersCourierList;
use App\Livewire\Orders\ImportTipax;
use App\Livewire\Customers\Index as CustomersIndex;
use App\Livewire\Customers\Create as CustomersCreate;
use App\Livewire\Customers\Show as CustomersShow;
use App\Livewire\Customers\Edit as CustomersEdit;
use App\Livewire\Certificates\Index as CertificatesIndex;
use App\Livewire\Certificates\Create as CertificatesCreate;
use App\Livewire\Certificates\Show as CertificatesShow;
use App\Livewire\Certificates\Designer as CertificatesDesigner;
use App\Livewire\Reports\Index as ReportsIndex;
use App\Livewire\Settings\Index as SettingsIndex;
use App\Livewire\Settings\Stones as SettingsStones;
use App\Livewire\Settings\Metals as SettingsMetals;

Route::get('/', fn () => redirect('/dashboard'));

Route::middleware('guest')->group(function () {
    Route::get('/login', Login::class)->name('login');
});

Route::middleware('auth')->group(function () {
    Route::post('/logout', function () {
        Auth::logout();
        request()->session()->invalidate();
        request()->session()->regenerateToken();
        return redirect('/login');
    })->name('logout');

    Route::get('/dashboard', Dashboard::class)->name('dashboard');
    Route::get('/activity-log', ActivityLog::class)->name('activity-log');

    Route::prefix('orders')->name('orders.')->group(function () {
        Route::get('/', OrdersIndex::class)->name('index');
        Route::get('/create', OrdersCreate::class)->name('create');
        Route::get('/import-tipax', ImportTipax::class)->name('import-tipax');
        Route::get('/courier-list', OrdersCourierList::class)->name('courier-list');
        Route::get('/bulk-print-labels', OrdersBulkPrintLabels::class)->name('bulk-print-labels');
        Route::get('/{order}/print-label', OrdersPrintLabel::class)->name('print-label');
        Route::get('/{order}/edit', OrdersEdit::class)->name('edit');
        Route::get('/{order}', OrdersShow::class)->name('show');
    });

    Route::prefix('customers')->name('customers.')->group(function () {
        Route::get('/', CustomersIndex::class)->name('index');
        Route::get('/create', CustomersCreate::class)->name('create');
        Route::get('/{customer}/edit', CustomersEdit::class)->name('edit');
        Route::get('/{customer}', CustomersShow::class)->name('show');
    });

    Route::prefix('certificates')->name('certificates.')->group(function () {
        Route::get('/', CertificatesIndex::class)->name('index');
        Route::get('/create', CertificatesCreate::class)->name('create');
        Route::get('/designer/{certificate?}', CertificatesDesigner::class)->name('designer');
        Route::get('/{certificate}', CertificatesShow::class)->name('show');
    });

    Route::get('/reports', ReportsIndex::class)->name('reports.index');

    Route::prefix('settings')->name('settings.')->group(function () {
        Route::get('/', SettingsIndex::class)->name('index');
        Route::get('/stones', SettingsStones::class)->name('stones');
        Route::get('/metals', SettingsMetals::class)->name('metals');

        // ★ Theme + Logo APIs
        Route::post('/theme', function() {
            \App\Models\AppSetting::put('theme', request('theme'), 'appearance');
            return response()->json(['ok' => true]);
        })->name('update-theme');

        Route::post('/header-logo', function() {
            \App\Models\AppSetting::put('header_logo', request('logo'), 'appearance');
            return response()->json(['ok' => true]);
        })->name('update-header-logo');
    });
});
'''

# ═══════════════════════════════════════════════════════════════
# اجرا
# ═══════════════════════════════════════════════════════════════
def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  Port کامل Legacy → Laravel                                   ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    print("📦 Backup...")
    backup("resources/views/components/layouts/app.blade.php")
    backup("routes/web.php")

    print("\n📄 نوشتن فایل‌ها...")
    write("public/css/legacy.css", FULL_CSS)
    write("resources/views/components/layouts/app.blade.php", LAYOUT_BLADE)
    write("routes/web.php", ROUTES_WEB)

    print("\n" + "═" * 64)
    print("✅ تمام!")
    print("═" * 64)
    print(f"""
📋 اجرا کن:

  cd {PROJECT}
  php artisan optimize:clear
  php artisan view:clear
  php artisan route:clear

  ⚠️ سرور رو ببند (Ctrl+C) و دوباره:
  php artisan serve

سپس مرورگر: Ctrl+Shift+R

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 چه چیزی اضافه شد:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✅ Header کامل: لوگو + نام فروشگاه + تاریخ شمسی + تم + لاگ + تنظیمات
  ✅ Tabs Bar دسکتاپ (سفارشات، مشتریان، شناسنامه، گزارش، تنظیمات)
  ✅ Mobile Bar با ۵ دکمه (خانه، سفارش، ➕، کارت، تنظیم)
  ✅ استایل Certificate Card کامل (Legacy design)
  ✅ استایل جدول‌ها با status/channel badge
  ✅ Modal overlay با blur
  ✅ فرم‌ها با label شناور (floating label)
  ✅ SKU Suggestions + Phone Suggestions
  ✅ Toast notifications
  ✅ Theme toggle + ذخیره در سرور
  ✅ Header logo upload + ذخیره در سرور
  ✅ Responsive کامل (desktop + tablet + mobile)
  ✅ Stones Grid برای تنظیمات
  ✅ تمام CSS های Legacy

📌 این patch CSS و Layout رو با Legacy جایگزین کرد.
   برای تکمیل ویژگی‌های باقی‌مانده (Print Labels, Bulk Actions, CSV Import, Mahak),
   اگه کار کردن این‌ها رو تست کردی و ok بود، اسکریپت بعدی رو بفرستم.
""")

if __name__ == "__main__":
    main()
