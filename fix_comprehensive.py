#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║  ShopGun V2 — Comprehensive Fix Pack                          ║
╚══════════════════════════════════════════════════════════════╝
"""
import shutil, re
from pathlib import Path
from datetime import datetime

PROJECT = Path(r"D:\prodo\shopgun-v2.1")
if not PROJECT.exists():
    PROJECT = Path(input("مسیر پروژه: ").strip().strip('"'))
    if not PROJECT.exists():
        print("❌ مسیر پیدا نشد"); exit(1)

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
# ۱) CSS سراسری — Blur، Sidebar باریک، Toggle، کارت‌ها
# ═══════════════════════════════════════════════════════════════

SHOPGUN_CSS = r'''/* ═══════════════════════════════════════════════════════════════
   ShopGun V2 — Comprehensive Style
   ═══════════════════════════════════════════════════════════════ */

:root {
    --sg-radius: 12px;
    --sg-radius-sm: 8px;
    --sg-radius-lg: 18px;
    --sg-primary: #0d9488;

    --sg-glass: rgba(255, 255, 255, 0.72);
    --sg-glass-heavy: rgba(255, 255, 255, 0.92);
    --sg-glass-border: rgba(255, 255, 255, 0.45);
    --sg-blur: blur(18px) saturate(180%);

    --sg-shadow-sm: 0 1px 4px rgba(0,0,0,0.04);
    --sg-shadow: 0 4px 16px rgba(0,0,0,0.06);
    --sg-shadow-lg: 0 12px 48px rgba(0,0,0,0.14);

    --sg-transition: 0.18s cubic-bezier(0.4, 0, 0.2, 1);
}

[data-theme="dark"] {
    --sg-glass: rgba(22, 30, 42, 0.72);
    --sg-glass-heavy: rgba(22, 30, 42, 0.94);
    --sg-glass-border: rgba(255, 255, 255, 0.08);
}

/* ═══════ Body Background ═══════ */
body {
    background:
        radial-gradient(ellipse at top right, rgba(13,148,136,0.06), transparent 60%),
        radial-gradient(ellipse at bottom left, rgba(8,145,178,0.05), transparent 60%),
        linear-gradient(135deg, #f5f7fa 0%, #e8eef3 100%);
    background-attachment: fixed;
}

[data-theme="dark"] body {
    background:
        radial-gradient(ellipse at top right, rgba(13,148,136,0.10), transparent 60%),
        radial-gradient(ellipse at bottom left, rgba(8,145,178,0.08), transparent 60%),
        linear-gradient(135deg, #0a0f1a 0%, #0f172a 100%);
}

/* ═══════ Sidebar — باریک ═══════ */
.sg-sidebar {
    width: 240px !important;
    transition: width var(--sg-transition);
}

@media (max-width: 1280px) {
    .sg-sidebar { width: 220px !important; }
}

.sg-sidebar .sg-card {
    padding: 0 !important;
    background: var(--sg-glass);
    backdrop-filter: var(--sg-blur);
    -webkit-backdrop-filter: var(--sg-blur);
    border: 1px solid var(--sg-glass-border);
    box-shadow: var(--sg-shadow);
}

/* ═══════ KPI Cards — اسکرول افقی ═══════ */
.sg-kpi-scroll {
    display: flex;
    gap: 6px;
    overflow-x: auto;
    overflow-y: hidden;
    padding: 3px 2px 6px 2px;
    scrollbar-width: none;
    -ms-overflow-style: none;
    scroll-behavior: smooth;
    -webkit-overflow-scrolling: touch;
}

.sg-kpi-scroll::-webkit-scrollbar { display: none; }

.sg-kpi-card {
    min-width: 68px;
    max-width: 78px;
    flex: 0 0 auto;
    padding: 7px 5px;
    background: var(--sg-glass-heavy);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255,255,255,0.4);
    border-radius: 10px;
    text-align: center;
    transition: var(--sg-transition);
    cursor: pointer;
    text-decoration: none;
    color: inherit;
}

[data-theme="dark"] .sg-kpi-card {
    background: rgba(255,255,255,0.05);
    border-color: rgba(255,255,255,0.08);
}

.sg-kpi-card:hover {
    background: rgba(13, 148, 136, 0.12);
    border-color: rgba(13, 148, 136, 0.4);
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(13,148,136,0.15);
}

.sg-kpi-card .num {
    font-size: 17px;
    font-weight: 800;
    line-height: 1;
    color: var(--sg-primary);
    font-variant-numeric: tabular-nums;
}

.sg-kpi-card .lbl {
    font-size: 9px;
    font-weight: 600;
    margin-top: 3px;
    opacity: 0.65;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

/* ═══════ Dropdown / Modal Blur ═══════ */
.dropdown-content,
.menu.dropdown-content {
    background: var(--sg-glass-heavy) !important;
    backdrop-filter: var(--sg-blur) !important;
    -webkit-backdrop-filter: var(--sg-blur) !important;
    border: 1px solid var(--sg-glass-border) !important;
    border-radius: var(--sg-radius) !important;
    box-shadow: var(--sg-shadow-lg) !important;
}

/* ═══════ Modal واحد ═══════ */
.sg-modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(15, 23, 42, 0.55);
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);
    z-index: 80;
    display: flex;
    align-items: flex-start;
    justify-content: center;
    padding: 12px;
    overflow-y: auto;
    animation: sgFadeIn 0.2s ease;
}

.sg-modal {
    background: var(--sg-glass-heavy);
    backdrop-filter: var(--sg-blur);
    -webkit-backdrop-filter: var(--sg-blur);
    border: 1px solid var(--sg-glass-border);
    border-radius: var(--sg-radius-lg);
    box-shadow: var(--sg-shadow-lg);
    width: 100%;
    max-width: 800px;
    margin: 12px auto;
    animation: sgSlideUp 0.28s cubic-bezier(0.34, 1.4, 0.64, 1);
    overflow: hidden;
}

@keyframes sgFadeIn { from { opacity: 0; } to { opacity: 1; } }
@keyframes sgSlideUp {
    from { opacity: 0; transform: translateY(16px) scale(0.98); }
    to { opacity: 1; transform: translateY(0) scale(1); }
}

/* ═══════ Cards ═══════ */
.sg-card {
    background: var(--sg-glass);
    backdrop-filter: var(--sg-blur);
    -webkit-backdrop-filter: var(--sg-blur);
    border: 1px solid var(--sg-glass-border);
    border-radius: var(--sg-radius);
    box-shadow: var(--sg-shadow-sm);
    transition: var(--sg-transition);
    overflow: hidden;
}

/* ═══════ Dashboard Cards — ردیف نشکنه ═══════ */
.sg-dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
    gap: 10px;
}

.sg-stat-card {
    padding: 14px 12px;
    background: var(--sg-glass);
    backdrop-filter: blur(14px);
    border: 1px solid var(--sg-glass-border);
    border-radius: var(--sg-radius);
    display: flex;
    align-items: center;
    gap: 12px;
    min-width: 0;
    transition: var(--sg-transition);
}

.sg-stat-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--sg-shadow);
}

.sg-stat-card .icon {
    width: 40px;
    height: 40px;
    min-width: 40px;
    border-radius: 10px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 20px;
    background: rgba(13,148,136,0.1);
    flex-shrink: 0;
}

.sg-stat-card .info { min-width: 0; flex: 1; }
.sg-stat-card .info .num { font-size: 20px; font-weight: 800; color: var(--sg-primary); line-height: 1.1; }
.sg-stat-card .info .lbl { font-size: 11px; opacity: 0.65; margin-top: 2px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; }

/* ═══════ Status Cell کوچک ═══════ */
.sg-status-cell {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 8px;
    border-radius: 999px;
    font-size: 10.5px;
    font-weight: 700;
    white-space: nowrap;
    cursor: pointer;
    transition: var(--sg-transition);
    border: 1px solid transparent;
}

.sg-status-cell.pending { background: rgba(251,146,60,0.15); color: #ea580c; border-color: rgba(251,146,60,0.3); }
.sg-status-cell.final-check { background: rgba(59,130,246,0.15); color: #2563eb; border-color: rgba(59,130,246,0.3); }
.sg-status-cell.courier { background: rgba(34,197,94,0.15); color: #16a34a; border-color: rgba(34,197,94,0.3); }

.sg-status-cell .icon { font-size: 11px; }
.sg-status-cell .count {
    background: rgba(0,0,0,0.12);
    padding: 0 5px;
    border-radius: 999px;
    font-size: 9px;
    margin-right: 2px;
    font-variant-numeric: tabular-nums;
}

.sg-status-cell:hover { transform: translateY(-1px); }

/* ═══════ Buttons ═══════ */
.btn, .sg-btn {
    border-radius: var(--sg-radius-sm) !important;
    transition: var(--sg-transition) !important;
    font-weight: 600;
    border-width: 1px !important;
}

.btn:hover:not(:disabled) { transform: translateY(-1px); box-shadow: 0 4px 12px rgba(0,0,0,0.08); }
.btn:active:not(:disabled) { transform: translateY(0); }
.btn-circle { border-radius: 999px !important; }

/* ═══════ Inputs ═══════ */
.input, .select, .textarea {
    border-radius: var(--sg-radius-sm) !important;
    transition: var(--sg-transition) !important;
    background-color: rgba(255,255,255,0.55) !important;
    border-width: 1.5px !important;
}

[data-theme="dark"] .input,
[data-theme="dark"] .select,
[data-theme="dark"] .textarea {
    background-color: rgba(0,0,0,0.25) !important;
}

.input:focus, .select:focus, .textarea:focus {
    border-color: var(--sg-primary) !important;
    box-shadow: 0 0 0 3px rgba(13,148,136,0.15) !important;
    outline: none !important;
}

/* ═══════ Table ═══════ */
.pro-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
}

.pro-table thead th {
    background: rgba(0,0,0,0.03);
    font-weight: 700;
    font-size: 11px;
    padding: 9px 10px;
    text-align: right;
    white-space: nowrap;
}

[data-theme="dark"] .pro-table thead th { background: rgba(255,255,255,0.03); }

.pro-table tbody td {
    padding: 8px 10px;
    font-size: 12px;
    border-top: 1px solid rgba(0,0,0,0.05);
}

[data-theme="dark"] .pro-table tbody td { border-top-color: rgba(255,255,255,0.05); }

.pro-table tbody tr { transition: background var(--sg-transition); }
.pro-table tbody tr:hover { background: rgba(13,148,136,0.05); }

/* ═══════ Scrollbar ═══════ */
::-webkit-scrollbar { width: 5px; height: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(0,0,0,0.15); border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: rgba(0,0,0,0.25); }

/* ═══════ Theme Toggle Buttons ═══════ */
.sg-choice {
    flex: 1;
    padding: 10px;
    border: 2px solid rgba(0,0,0,0.08);
    border-radius: 10px;
    text-align: center;
    font-size: 12px;
    font-weight: 700;
    cursor: pointer;
    transition: var(--sg-transition);
    user-select: none;
}

.sg-choice:hover { border-color: var(--sg-primary); background: rgba(13,148,136,0.04); }
.sg-choice.selected {
    border-color: var(--sg-primary);
    background: rgba(13,148,136,0.12);
    color: var(--sg-primary);
}

/* ═══════ Label Preview ═══════ */
.sg-label-preview {
    width: 100mm;
    height: 50mm;
    padding: 1.5mm;
    background: #fff;
    color: #000;
    box-sizing: border-box;
    border: 1px dashed #999;
    border-radius: 4px;
    font-family: Vazirmatn, sans-serif;
    overflow: hidden;
    display: flex;
    flex-direction: column;
    gap: 1mm;
    margin: 0 auto;
}

.sg-label-preview .row1 { display: flex; align-items: center; justify-content: space-between; gap: 2mm; }
.sg-label-preview .name { font-size: 14px; font-weight: bold; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
.sg-label-preview .ins { font-size: 11px; color: #fff; background: #000; padding: 2px 8px; border-radius: 10px; font-weight: bold; }
.sg-label-preview .addr { border: 1.5px solid #000; padding: 2mm; border-radius: 6px; font-size: 12px; flex: 1; }
.sg-label-preview .contacts { display: flex; gap: 2mm; }
.sg-label-preview .contact { flex: 1; display: flex; align-items: center; gap: 4px; }
.sg-label-preview .contact .lbl { font-size: 10px; color: #fff; background: #000; padding: 2px 6px; border-radius: 4px; font-weight: bold; }
.sg-label-preview .contact .val { font-size: 14px; border: 1.5px solid #000; padding: 2px 6px; border-radius: 4px; font-weight: bold; font-family: monospace; flex: 1; text-align: center; }
.sg-label-preview .footer { font-size: 9.5px; height: 4.5mm; background: #000; color: #fff; text-align: center; line-height: 4.5mm; border-radius: 6px; font-weight: 700; }

/* ═══════ Notification Popup ═══════ */
.sg-notif-popup {
    position: fixed;
    bottom: 20px;
    left: 20px;
    z-index: 9999;
    padding: 12px 18px;
    border-radius: 12px;
    font-size: 13px;
    font-weight: 700;
    box-shadow: 0 10px 32px rgba(0,0,0,0.25);
    backdrop-filter: blur(12px);
    display: flex;
    align-items: center;
    gap: 8px;
    animation: sgSlideIn 0.3s ease;
}

.sg-notif-popup.success { background: rgba(34,197,94,0.95); color: #fff; }
.sg-notif-popup.error   { background: rgba(239,68,68,0.95); color: #fff; }
.sg-notif-popup.info    { background: rgba(59,130,246,0.95); color: #fff; }
.sg-notif-popup.warning { background: rgba(245,158,11,0.95); color: #fff; }

@keyframes sgSlideIn {
    from { opacity: 0; transform: translateY(20px); }
    to { opacity: 1; transform: translateY(0); }
}
'''

# ═══════════════════════════════════════════════════════════════
# ۲) Sidebar — باریک با KPI افقی
# ═══════════════════════════════════════════════════════════════

SIDEBAR_BLADE = r'''<div class="flex flex-col h-full w-full overflow-hidden">

    {{-- ═══ لوگو ═══ --}}
    <div class="px-2.5 pt-2.5 pb-2">
        <a href="{{ route('dashboard') }}" wire:navigate
           class="flex items-center gap-2 p-2 rounded-xl"
           style="background: linear-gradient(135deg, rgba(13,148,136,0.15), rgba(8,145,178,0.08)); border: 1px solid rgba(13,148,136,0.2);">
            <div class="w-8 h-8 rounded-lg flex items-center justify-center text-white text-sm font-extrabold shadow"
                 style="background: linear-gradient(135deg, #14b8a6, #0891b2);">💎</div>
            <div class="flex-1 min-w-0">
                <div class="font-extrabold text-[12px] truncate">شاپگان</div>
                <div class="text-[9px] opacity-60">v2.1</div>
            </div>
        </a>
    </div>

    {{-- ═══ تاریخ ═══ --}}
    <div class="px-2.5 pb-2">
        <div class="flex items-center justify-between p-1.5 rounded-lg bg-black/5 dark:bg-white/5 text-[10.5px]">
            <div class="flex items-center gap-1">
                <span>📅</span>
                <span class="font-mono font-bold">{{ $today }}</span>
            </div>
            <span class="opacity-55 text-[9.5px]">{{ $dayOfWeek }}</span>
        </div>
    </div>

    {{-- ═══ KPI افقی ═══ --}}
    <div class="px-2 pb-2">
        <div class="text-[9.5px] font-bold opacity-45 mb-1 px-1">📊 امروز</div>
        <div class="sg-kpi-scroll">
            <a href="{{ route('orders.index') }}" wire:navigate class="sg-kpi-card">
                <div class="num">{{ \App\Support\PersianNumber::toFa($stats['orders_today'] ?? 0) }}</div>
                <div class="lbl">امروز</div>
            </a>
            <a href="{{ route('orders.index', ['status' => 'pending']) }}" wire:navigate class="sg-kpi-card">
                <div class="num" style="color:#ea580c">{{ \App\Support\PersianNumber::toFa($stats['orders_pending'] ?? 0) }}</div>
                <div class="lbl">در انتظار</div>
            </a>
            <a href="{{ route('orders.index', ['status' => 'final-check']) }}" wire:navigate class="sg-kpi-card">
                <div class="num" style="color:#2563eb">{{ \App\Support\PersianNumber::toFa($stats['orders_check'] ?? 0) }}</div>
                <div class="lbl">چک</div>
            </a>
            <a href="{{ route('orders.index', ['status' => 'courier']) }}" wire:navigate class="sg-kpi-card">
                <div class="num" style="color:#16a34a">{{ \App\Support\PersianNumber::toFa($stats['orders_courier'] ?? 0) }}</div>
                <div class="lbl">مامور</div>
            </a>
            <a href="{{ route('customers.index') }}" wire:navigate class="sg-kpi-card">
                <div class="num">{{ \App\Support\PersianNumber::toFa($stats['customers'] ?? 0) }}</div>
                <div class="lbl">مشتری</div>
            </a>
            <a href="{{ route('certificates.index') }}" wire:navigate class="sg-kpi-card">
                <div class="num">{{ \App\Support\PersianNumber::toFa($stats['certificates'] ?? 0) }}</div>
                <div class="lbl">کارت</div>
            </a>
            <a href="{{ route('settings.index') }}" wire:navigate class="sg-kpi-card">
                <div class="num">{{ \App\Support\PersianNumber::toFa($stats['products'] ?? 0) }}</div>
                <div class="lbl">محصول</div>
            </a>
        </div>
    </div>

    {{-- ═══ منو ═══ --}}
    <nav class="flex-1 overflow-y-auto px-2 pb-2">
        <ul class="space-y-0.5">
            @php
                $menu = [
                    ['route' => 'dashboard',          'icon' => '🏠', 'label' => 'داشبورد'],
                    ['route' => 'orders.index',       'icon' => '📦', 'label' => 'سفارشات',   'badge' => $stats['orders_pending'] ?? 0],
                    ['route' => 'customers.index',    'icon' => '👥', 'label' => 'مشتریان'],
                    ['route' => 'certificates.index', 'icon' => '💎', 'label' => 'شناسنامه'],
                    ['route' => 'reports.index',      'icon' => '📊', 'label' => 'گزارش‌ها'],
                    ['route' => 'activity-log',       'icon' => '📜', 'label' => 'لاگ'],
                    ['route' => 'settings.index',     'icon' => '⚙️', 'label' => 'تنظیمات'],
                ];
            @endphp
            @foreach($menu as $m)
                @php $isActive = request()->routeIs($m['route']) || request()->routeIs(explode('.', $m['route'])[0] . '.*'); @endphp
                <li>
                    <a href="{{ route($m['route']) }}" wire:navigate
                       class="flex items-center gap-2 px-2.5 py-1.5 rounded-lg text-[12px] transition-all
                              {{ $isActive
                                  ? 'bg-primary/15 text-primary font-bold'
                                  : 'opacity-75 hover:opacity-100 hover:bg-black/5 dark:hover:bg-white/5' }}">
                        <span class="text-[14px] leading-none">{{ $m['icon'] }}</span>
                        <span class="flex-1 truncate">{{ $m['label'] }}</span>
                        @if(!empty($m['badge']) && $m['badge'] > 0)
                            <span class="badge badge-warning badge-xs font-mono">{{ \App\Support\PersianNumber::toFa($m['badge']) }}</span>
                        @endif
                    </a>
                </li>
            @endforeach
        </ul>
    </nav>

    {{-- ═══ اعلان ═══ --}}
    @if($notifCount > 0)
        <div class="px-2 pb-2">
            <div class="rounded-lg p-2"
                 style="background: linear-gradient(135deg, rgba(251,146,60,0.12), rgba(248,113,113,0.08)); border: 1px solid rgba(251,146,60,0.25);">
                <div class="flex items-center gap-1.5 text-[10.5px] font-bold text-warning">
                    🔔 {{ \App\Support\PersianNumber::toFa($notifCount) }} اعلان
                </div>
            </div>
        </div>
    @endif

    {{-- ═══ فوتر ═══ --}}
    <div class="px-2 py-1.5 border-t border-black/5 dark:border-white/5 text-[9px] text-center opacity-45">
        اقاقیا · ۱۴۰۵
    </div>
</div>
'''

# ═══════════════════════════════════════════════════════════════
# ۳) Layout — باریک + CSS جدید + Popup
# ═══════════════════════════════════════════════════════════════

LAYOUT_BLADE = r'''<!DOCTYPE html>
<html lang="fa" dir="rtl" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>{{ \App\Models\AppSetting::get('shop_name', 'شاپگان') }}</title>

    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">

    <script>
        (function() {
            const t = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', t);

            // Density
            const d = localStorage.getItem('density') || '{{ \App\Models\AppSetting::get("density", "normal") }}';
            document.documentElement.setAttribute('data-density', d);

            // Primary color
            const c = localStorage.getItem('primary_color') || '{{ \App\Models\AppSetting::get("primary_color", "#0d9488") }}';
            document.documentElement.style.setProperty('--sg-primary', c);
        })();
    </script>

    @vite(['resources/css/app.css', 'resources/js/app.js'])
    @livewireStyles

    <link rel="stylesheet" href="{{ asset('css/shopgun.css') }}?v=10">
    <link rel="stylesheet" href="{{ asset('css/cert-card.css') }}?v=3">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <script src="{{ asset('js/cert-card.js') }}?v=3"></script>
    <script src="{{ asset('js/cert-designer.js') }}?v=4" defer></script>

    @stack('styles')

    <style>
        [data-density="compact"] .sg-card,
        [data-density="compact"] .card-body { padding: 0.6rem !important; }
        [data-density="compact"] table td,
        [data-density="compact"] table th { padding: 0.35rem 0.55rem !important; font-size: 11px !important; }
        [data-density="comfortable"] .sg-card,
        [data-density="comfortable"] .card-body { padding: 1.4rem !important; }
        [data-density="comfortable"] table td,
        [data-density="comfortable"] table th { padding: 0.85rem 0.9rem !important; }
    </style>
</head>
<body class="min-h-screen font-sans text-base-content">

    @auth
        <livewire:global-search />
        <livewire:components.shipment-timeline />
        {{-- ★ فقط یکبار در کل صفحه ★ --}}
        <livewire:orders.form-modal :key="'global-order-form'" />
        <livewire:orders.view-modal :key="'global-order-view'" />
        <livewire:customers.profile-modal :key="'global-customer-profile'" />
        <livewire:certificates.view-modal :key="'global-cert-view'" />
    @endauth

    <div class="flex min-h-screen">

        {{-- ═══ Sidebar ═══ --}}
        <aside class="sg-sidebar hidden lg:flex flex-col shrink-0 p-2.5 sticky top-0 h-screen">
            <div class="sg-card flex-1 flex flex-col overflow-hidden">
                <livewire:components.sidebar />
            </div>
        </aside>

        {{-- ═══ محتوا ═══ --}}
        <div class="flex-1 min-w-0 flex flex-col">

            {{-- Header --}}
            <header class="sticky top-0 z-30 p-2.5 md:p-3">
                <div class="sg-card px-3 py-2 flex items-center justify-between gap-2">
                    <div class="flex items-center gap-2 flex-1 min-w-0">
                        <div class="lg:hidden w-7 h-7 rounded-lg flex items-center justify-center text-white text-xs font-extrabold"
                             style="background: linear-gradient(135deg, #14b8a6, #0891b2);">💎</div>
                        <button onclick="window.dispatchEvent(new KeyboardEvent('keydown', {key: 'k', ctrlKey: true}))"
                                class="hidden md:flex items-center gap-1.5 px-2.5 py-1 rounded-lg text-[11px] opacity-60 hover:opacity-100 transition"
                                style="background: rgba(0,0,0,0.05);">
                            <span>🔍 جستجو</span>
                            <kbd class="px-1 py-0.5 rounded text-[9.5px] font-mono" style="background: rgba(0,0,0,0.08);">Ctrl+K</kbd>
                        </button>
                    </div>

                    <div class="flex items-center gap-1">
                        <button onclick="sgToggleTheme()" class="btn btn-ghost btn-sm btn-circle" title="تم">
                            <span id="themeIcon">🌙</span>
                        </button>

                        @auth
                            <livewire:notification-center />
                        @endauth

                        <div class="dropdown dropdown-end">
                            <div tabindex="0" role="button" class="btn btn-ghost btn-sm gap-1.5 px-1.5">
                                <div class="w-6 h-6 rounded-full flex items-center justify-center text-white text-[10px] font-bold"
                                     style="background: linear-gradient(135deg, #14b8a6, #0891b2);">
                                    {{ mb_substr(Auth::user()->name ?? '؟', 0, 1) }}
                                </div>
                                <span class="hidden sm:inline text-[11px]">{{ Auth::user()->name ?? 'کاربر' }}</span>
                            </div>
                            <ul tabindex="0" class="dropdown-content menu z-[1] w-48 p-1.5 mt-2">
                                <li><a href="{{ route('settings.index') }}" wire:navigate class="text-xs">⚙️ تنظیمات</a></li>
                                <li><a href="{{ route('activity-log') }}" wire:navigate class="text-xs">📜 لاگ</a></li>
                                <li>
                                    <form method="POST" action="{{ route('logout') }}">
                                        @csrf
                                        <button type="submit" class="w-full text-right text-xs">🚪 خروج</button>
                                    </form>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            </header>

            <main class="flex-1 pb-24 lg:pb-6">{{ $slot }}</main>

            {{-- Bottom Bar --}}
            <nav class="lg:hidden fixed bottom-2 left-2 right-2 z-40"
                 style="background: var(--sg-glass-heavy); backdrop-filter: var(--sg-blur); border: 1px solid var(--sg-glass-border); border-radius: 16px; box-shadow: var(--sg-shadow-lg); padding: 5px;">
                <div class="flex gap-0.5">
                    @php $items = [
                        ['dashboard','🏠','خانه'],
                        ['orders.index','📦','سفارش'],
                        ['customers.index','👥','مشتری'],
                        ['certificates.index','💎','کارت'],
                        ['settings.index','⚙️','تنظیم'],
                    ]; @endphp
                    @foreach($items as $it)
                        @php $isActive = request()->routeIs($it[0]) || request()->routeIs(explode('.', $it[0])[0] . '.*'); @endphp
                        <a href="{{ route($it[0]) }}" wire:navigate
                           class="flex-1 flex flex-col items-center justify-center gap-0.5 py-1.5 rounded-xl transition-all
                                  {{ $isActive ? 'bg-primary/15 text-primary' : 'opacity-55' }}">
                            <span class="text-base leading-none">{{ $it[1] }}</span>
                            <span class="text-[9px] font-bold leading-none">{{ $it[2] }}</span>
                        </a>
                    @endforeach
                </div>
            </nav>
        </div>
    </div>

    <script>
        function sgToggleTheme() {
            const html = document.documentElement;
            const cur = html.getAttribute('data-theme') || 'light';
            const next = cur === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', next);
            localStorage.setItem('theme', next);
            document.getElementById('themeIcon').textContent = next === 'dark' ? '☀️' : '🌙';
            // اطلاع به Livewire برای ذخیره
            if (window.Livewire) {
                Livewire.dispatch('theme-changed', { theme: next });
            }
        }

        // Global notification popup
        window.sgNotify = function(type, message) {
            const icons = { success: '✅', error: '❌', info: 'ℹ️', warning: '⚠️' };
            const popup = document.createElement('div');
            popup.className = 'sg-notif-popup ' + type;
            popup.innerHTML = '<span>' + (icons[type] || 'ℹ️') + '</span><span>' + message + '</span>';
            document.body.appendChild(popup);
            setTimeout(() => {
                popup.style.transition = 'all 0.3s ease';
                popup.style.opacity = '0';
                popup.style.transform = 'translateY(20px)';
                setTimeout(() => popup.remove(), 300);
            }, 3000);
        };

        // Livewire notify event
        document.addEventListener('livewire:init', () => {
            Livewire.on('notify', (data) => {
                const payload = Array.isArray(data) ? data[0] : data;
                window.sgNotify(payload.type || 'info', payload.message || '');
            });
        });

        // Apply settings from server
        document.addEventListener('DOMContentLoaded', () => {
            const cur = document.documentElement.getAttribute('data-theme');
            const icon = document.getElementById('themeIcon');
            if (icon) icon.textContent = cur === 'dark' ? '☀️' : '🌙';
        });

        // Theme change event from Livewire
        document.addEventListener('livewire:init', () => {
            Livewire.on('apply-theme', (data) => {
                const payload = Array.isArray(data) ? data[0] : data;
                if (payload.theme) {
                    document.documentElement.setAttribute('data-theme', payload.theme);
                    localStorage.setItem('theme', payload.theme);
                }
                if (payload.density) {
                    document.documentElement.setAttribute('data-density', payload.density);
                    localStorage.setItem('density', payload.density);
                }
                if (payload.primary_color) {
                    document.documentElement.style.setProperty('--sg-primary', payload.primary_color);
                    localStorage.setItem('primary_color', payload.primary_color);
                }
            });
        });
    </script>

    @livewireScripts
    @stack('scripts')
</body>
</html>
'''

# ═══════════════════════════════════════════════════════════════
# ۴) Order Form PHP — بیمه خودکار + fixed title
# ═══════════════════════════════════════════════════════════════

ORDER_FORM_PHP = r'''<?php

namespace App\Livewire\Orders;

use App\Models\Channel;
use App\Models\Customer;
use App\Models\Order;
use App\Models\Product;
use Livewire\Attributes\On;
use Livewire\Component;

class FormModal extends Component
{
    public bool $show = false;
    public ?int $orderId = null;
    public string $mode = 'create';

    public ?int $customerId = null;
    public string $customerName = '';
    public string $customerPhone = '';
    public string $customerAddress = '';
    public string $customerPostal = '';

    public array $cart = [];

    /* ادیتور محصول */
    public string $draftSku = '';
    public string $draftTitle = '';
    public string $draftPrice = '0';
    public int    $draftQty = 1;
    public bool   $draftCert = false;
    public array  $draftSuggestions = [];

    /* مالی */
    public string $insurance = '0';
    public string $discount  = '0';
    public string $shipping  = '0';
    public string $status    = 'pending';
    public ?int   $channelId = null;
    public string $notes     = '';
    public bool   $invoiceNeeded = false;
    public bool   $insuranceManual = false; // اگر کاربر دستی تغییر داد

    public array $statusOptions = [
        ['id' => 'pending',     'name' => 'ثبت سفارش',   'icon' => '📝'],
        ['id' => 'final-check', 'name' => 'چک نهایی',    'icon' => '🔍'],
        ['id' => 'courier',     'name' => 'تحویل مامور', 'icon' => '🚚'],
    ];

    #[On('open-order-form')]
    public function open(?int $orderId = null): void
    {
        if ($this->show && !$orderId && !$this->orderId) return;

        $this->resetForm();
        $this->orderId = $orderId;
        $this->mode = $orderId ? 'edit' : 'create';

        if ($orderId) $this->loadOrder($orderId);

        $this->show = true;
        $this->dispatch('customer-picker-set', id: $this->customerId);
        $this->dispatch('product-picker-set', cart: $this->cart);
    }

    public function close(): void
    {
        $this->show = false;
        $this->resetForm();
    }

    protected function resetForm(): void
    {
        $this->orderId = null;
        $this->customerId = null;
        $this->customerName = '';
        $this->customerPhone = '';
        $this->customerAddress = '';
        $this->customerPostal = '';
        $this->cart = [];
        $this->draftSku = '';
        $this->draftTitle = '';
        $this->draftPrice = '0';
        $this->draftQty = 1;
        $this->draftCert = false;
        $this->draftSuggestions = [];
        $this->insurance = '0';
        $this->discount = '0';
        $this->shipping = '0';
        $this->status = 'pending';
        $this->channelId = null;
        $this->notes = '';
        $this->invoiceNeeded = false;
        $this->insuranceManual = false;
    }

    protected function loadOrder(int $orderId): void
    {
        $o = Order::with(['items', 'customer'])->find($orderId);
        if (!$o) return;

        $this->customerId = $o->customer_id;
        $this->customerName = $o->customer_name ?? $o->customer?->name ?? '';
        $this->customerPhone = $o->phone ?? '';
        $this->customerAddress = $o->address ?? '';
        $this->customerPostal = $o->postal_code ?? '';
        $this->insurance = (string) ($o->insurance ?? 0);
        $this->discount  = (string) ($o->discount ?? 0);
        $this->shipping  = (string) ($o->shipping ?? 0);
        $this->status    = $o->status ?? 'pending';
        $this->channelId = $o->channel_id;
        $this->notes     = $o->notes ?? '';
        $this->invoiceNeeded = (bool) $o->invoice_needed;
        $this->insuranceManual = true;

        $this->cart = [];
        foreach ($o->items as $item) {
            $this->cart[] = [
                'product_id' => $item->product_id,
                'sku'        => $item->sku ?? '',
                'title'      => $item->title ?? $item->name ?? '—',
                'price'      => (float) $item->price,
                'qty'        => (int) $item->quantity,
                'certNeeded' => (bool) ($item->certificate_needed ?? false),
            ];
        }
    }

    #[On('customer-selected')]
    public function onCustomerSelected(int $customerId, array $data): void
    {
        $this->customerId = $customerId;
        $this->customerName = $data['name'] ?? '';
        $this->customerPhone = $data['phone'] ?? '';
        $this->customerAddress = $data['address'] ?? '';
        $this->customerPostal = $data['postal_code'] ?? '';
    }

    #[On('customer-cleared')]
    public function onCustomerCleared(): void
    {
        $this->customerId = null;
        $this->customerName = '';
        $this->customerPhone = '';
        $this->customerAddress = '';
        $this->customerPostal = '';
    }

    #[On('products-updated')]
    public function onProductsUpdated(array $cart): void
    {
        $this->cart = $cart;
        $this->autoCalcInsurance();
    }

    /* ═══ SKU Search ═══ */
    public function updatedDraftSku(): void
    {
        $q = trim($this->draftSku);
        if (mb_strlen($q) < 2) {
            $this->draftSuggestions = [];
            return;
        }

        $this->draftSuggestions = Product::active()
            ->search($q)
            ->orderByRaw('CASE WHEN sku = ? THEN 0 WHEN sku LIKE ? THEN 1 ELSE 2 END', [$q, $q . '%'])
            ->limit(10)
            ->get()
            ->map(fn($p) => [
                'id' => $p->id, 'sku' => $p->sku, 'name' => $p->name,
                'price' => (float) $p->price, 'price_fmt' => $p->price_formatted,
                'image' => $p->image_src, 'stock' => $p->stock_quantity,
            ])
            ->toArray();

        $exact = Product::where('sku', $q)->first();
        if ($exact) $this->fillDraftFromProduct($exact);
    }

    public function pickDraftProduct(int $productId): void
    {
        $p = Product::find($productId);
        if ($p) $this->fillDraftFromProduct($p);
    }

    protected function fillDraftFromProduct(Product $p): void
    {
        $this->draftSku = $p->sku;
        $this->draftTitle = $p->name;
        $this->draftPrice = number_format((float) $p->price, 0, '.', '');
        $this->draftSuggestions = [];
    }

    public function addDraftToCart(): void
    {
        $title = trim($this->draftTitle);
        $price = (float) preg_replace('/[^\d.]/', '', $this->draftPrice ?: '0');

        if ($title === '') {
            $this->addError('draftTitle', 'عنوان محصول الزامی است');
            return;
        }

        $found = false;
        foreach ($this->cart as $i => $item) {
            if (!empty($this->draftSku) && ($item['sku'] ?? '') === $this->draftSku) {
                $this->cart[$i]['qty'] = ((int) ($item['qty'] ?? 1)) + $this->draftQty;
                $this->cart[$i]['price'] = $price;
                $found = true;
                break;
            }
        }

        if (!$found) {
            $this->cart[] = [
                'product_id' => null,
                'sku' => trim($this->draftSku),
                'title' => $title,
                'price' => $price,
                'qty' => max(1, $this->draftQty),
                'certNeeded' => $this->draftCert,
            ];
        }

        $this->dispatch('product-picker-set', cart: $this->cart);
        $this->autoCalcInsurance();

        $this->reset(['draftSku', 'draftTitle', 'draftPrice', 'draftQty', 'draftCert', 'draftSuggestions']);
        $this->draftPrice = '0';
        $this->draftQty = 1;
    }

    public function removeCartItem(int $idx): void
    {
        unset($this->cart[$idx]);
        $this->cart = array_values($this->cart);
        $this->dispatch('product-picker-set', cart: $this->cart);
        $this->autoCalcInsurance();
    }

    public function updateCartQty(int $idx, $qty): void
    {
        if (!isset($this->cart[$idx])) return;
        $this->cart[$idx]['qty'] = max(1, (int) $qty);
        $this->dispatch('product-picker-set', cart: $this->cart);
        $this->autoCalcInsurance();
    }

    public function updateCartPrice(int $idx, $price): void
    {
        if (!isset($this->cart[$idx])) return;
        $this->cart[$idx]['price'] = (float) preg_replace('/[^\d.]/', '', (string) $price);
        $this->dispatch('product-picker-set', cart: $this->cart);
        $this->autoCalcInsurance();
    }

    /* ═══ محاسبه‌ها ═══ */
    public function getSubtotalProperty(): float
    {
        $s = 0;
        foreach ($this->cart as $it) {
            $s += ((float) ($it['price'] ?? 0)) * ((int) ($it['qty'] ?? 1));
        }
        return $s;
    }

    public function getInsuranceAmountProperty(): float
    {
        return (float) preg_replace('/[^\d.]/', '', $this->insurance ?: '0');
    }

    public function getDiscountAmountProperty(): float
    {
        return (float) preg_replace('/[^\d.]/', '', $this->discount ?: '0');
    }

    public function getShippingAmountProperty(): float
    {
        return (float) preg_replace('/[^\d.]/', '', $this->shipping ?: '0');
    }

    public function getTotalProperty(): float
    {
        return max(0, $this->subtotal + $this->insurance_amount + $this->shipping_amount - $this->discount_amount);
    }

    /**
     * ★ محاسبه خودکار بیمه — حذف ۶ رقم از مبلغ کل
     * 25,000,000 → 25
     * 10,000,000 → 10
     */
    protected function autoCalcInsurance(): void
    {
        if ($this->insuranceManual) return;

        $total = $this->subtotal;
        if ($total <= 0) {
            $this->insurance = '0';
            return;
        }

        // تقسیم بر 1,000,000 و گرد کردن به پایین
        $ins = (int) floor($total / 1000000);
        $this->insurance = (string) $ins;
    }

    /**
     * اگر کاربر دستی بیمه رو تغییر داد، دیگه خودکار حساب نکن
     */
    public function updatedInsurance(): void
    {
        // اگر مقدار فعلی با محاسبه خودکار یکی نیست، یعنی دستی تغییر داد
        $auto = (int) floor($this->subtotal / 1000000);
        $cur = (int) preg_replace('/[^\d.]/', '', $this->insurance ?: '0');
        $this->insuranceManual = ($cur !== $auto && $cur > 0);
    }

    public function recalcInsurance(): void
    {
        $this->insuranceManual = false;
        $this->autoCalcInsurance();
    }

    /* ═══ ذخیره ═══ */
    public function save()
    {
        $this->validate([
            'customerPhone' => 'required|string|max:20',
            'customerName'  => 'required|string|max:120',
            'status'        => 'required|in:pending,final-check,courier',
            'cart'          => 'required|array|min:1',
        ], [], [
            'customerPhone' => 'تلفن',
            'customerName'  => 'نام',
            'status'        => 'وضعیت',
            'cart'          => 'سبد',
        ]);

        $customer = $this->customerId ? Customer::find($this->customerId) : null;
        if (!$customer) $customer = Customer::findByPhone($this->customerPhone);
        if (!$customer) {
            $customer = Customer::create([
                'name'        => $this->customerName,
                'phone'       => Customer::normalizePhone($this->customerPhone),
                'address'     => $this->customerAddress,
                'postal_code' => $this->customerPostal,
            ]);
            $customer->addPhone($this->customerPhone, 'اصلی', true);
            if ($this->customerAddress || $this->customerPostal) {
                $customer->addAddress([
                    'address'     => $this->customerAddress,
                    'postal_code' => $this->customerPostal,
                ], true);
            }
        }

        $orderData = [
            'customer_id'    => $customer->id,
            'customer_name'  => $this->customerName,
            'phone'          => Customer::normalizePhone($this->customerPhone),
            'address'        => $this->customerAddress,
            'postal_code'    => $this->customerPostal,
            'status'         => $this->status,
            'channel_id'     => $this->channelId,
            'insurance'      => $this->insurance_amount,
            'discount'       => $this->discount_amount,
            'shipping'       => $this->shipping_amount,
            'amount'         => $this->total,
            'notes'          => $this->notes,
            'invoice_needed' => $this->invoiceNeeded,
        ];

        if ($this->orderId) {
            $order = Order::find($this->orderId);
            $order->update($orderData);
            $order->items()->delete();
        } else {
            $orderData['order_number'] = Order::generateNumber();
            $order = Order::create($orderData);
        }

        foreach ($this->cart as $it) {
            $order->items()->create([
                'product_id'         => $it['product_id'] ?? null,
                'sku'                => $it['sku'] ?? null,
                'title'              => $it['title'] ?? '—',    // ★ اصلاح شد
                'price'              => (float) ($it['price'] ?? 0),
                'quantity'           => (int) ($it['qty'] ?? 1),
                'certificate_needed' => !empty($it['certNeeded']),
            ]);
        }

        $this->dispatch('order-saved', orderId: $order->id);
        $this->dispatch('notify', type: 'success',
            message: $this->orderId ? 'سفارش ویرایش شد ✅' : 'سفارش ثبت شد ✅');

        $this->close();
    }

    public function render()
    {
        return view('livewire.orders.form-modal', [
            'channels' => Channel::orderBy('id')->get(),
        ]);
    }
}
'''

# ═══════════════════════════════════════════════════════════════
# ۵) Order Form Blade — با دکمه بازمحاسبه بیمه
# ═══════════════════════════════════════════════════════════════

ORDER_FORM_BLADE = r'''<div>
    @if($show)
    <div class="sg-modal-overlay" wire:key="ofm-{{ $orderId ?? 'new' }}"
         @keydown.escape.window="$wire.close()">
        <div class="sg-modal" style="max-width: 780px;">

            {{-- Header --}}
            <div class="flex items-center justify-between p-3 border-b border-black/5 dark:border-white/5"
                 style="background: linear-gradient(90deg, rgba(13,148,136,0.08), transparent);">
                <div class="flex items-center gap-2.5">
                    <div class="w-8 h-8 rounded-lg flex items-center justify-center text-white shadow text-sm"
                         style="background: linear-gradient(135deg, #14b8a6, #0891b2);">
                        {{ $mode === 'edit' ? '✏️' : '📦' }}
                    </div>
                    <h2 class="font-bold text-sm">
                        {{ $mode === 'edit' ? 'ویرایش سفارش #'.$orderId : 'سفارش جدید' }}
                    </h2>
                </div>
                <button wire:click="close" class="btn btn-ghost btn-sm btn-circle">✕</button>
            </div>

            {{-- Body --}}
            <div class="p-3 space-y-4 max-h-[calc(100vh-13rem)] overflow-y-auto">

                {{-- ═══ مشتری ═══ --}}
                <section>
                    <div class="flex items-center gap-2 mb-2">
                        <span class="w-5 h-5 rounded-full bg-primary text-white text-[10px] font-bold flex items-center justify-center">۱</span>
                        <h3 class="font-bold text-xs">👤 مشتری</h3>
                    </div>
                    <livewire:components.customer-picker
                        :customer-id="$customerId"
                        event-prefix="customer"
                        :key="'mf-cp-'.($orderId ?? 'new')" />
                </section>

                {{-- ═══ افزودن محصول ═══ --}}
                <section>
                    <div class="flex items-center gap-2 mb-2">
                        <span class="w-5 h-5 rounded-full bg-primary text-white text-[10px] font-bold flex items-center justify-center">۲</span>
                        <h3 class="font-bold text-xs">🛍️ محصولات</h3>
                    </div>

                    <div class="rounded-lg p-2.5 space-y-2.5"
                         style="background: rgba(13,148,136,0.04); border: 1.5px dashed rgba(13,148,136,0.25);">

                        {{-- SKU Search --}}
                        <div class="relative">
                            <label class="text-[10px] font-bold opacity-70 mb-1 block">🔍 SKU (اختیاری)</label>
                            <div class="relative">
                                <input type="text" wire:model.live.debounce.250ms="draftSku"
                                       placeholder="کد محصول..." class="input input-bordered input-sm w-full font-mono pr-8"
                                       dir="ltr" autocomplete="off">
                                <span class="absolute left-2 top-1/2 -translate-y-1/2 opacity-40 text-sm">🔍</span>
                            </div>

                            @if(count($draftSuggestions) > 0)
                                <div class="absolute z-50 top-full left-0 right-0 mt-1 rounded-lg shadow-2xl max-h-72 overflow-y-auto"
                                     style="background: var(--sg-glass-heavy); backdrop-filter: var(--sg-blur); border: 1px solid var(--sg-glass-border);">
                                    @foreach($draftSuggestions as $s)
                                        <button type="button" wire:click="pickDraftProduct({{ $s['id'] }})"
                                                class="w-full text-right p-2 hover:bg-black/5 dark:hover:bg-white/5 border-b border-black/5 last:border-0 flex items-center gap-2">
                                            @if($s['image'])
                                                <img src="{{ $s['image'] }}" class="w-8 h-8 rounded object-cover shrink-0" alt="">
                                            @else
                                                <div class="w-8 h-8 rounded bg-black/5 flex items-center justify-center shrink-0 text-xs">💎</div>
                                            @endif
                                            <div class="flex-1 min-w-0">
                                                <div class="text-[11px] font-bold truncate">{{ $s['name'] }}</div>
                                                <div class="text-[9.5px] font-mono opacity-50" dir="ltr">{{ $s['sku'] }}</div>
                                            </div>
                                            <div class="text-[11px] font-bold text-primary shrink-0">{{ $s['price_fmt'] }}</div>
                                        </button>
                                    @endforeach
                                </div>
                            @endif
                        </div>

                        {{-- عنوان / قیمت / تعداد --}}
                        <div class="grid grid-cols-1 md:grid-cols-12 gap-2">
                            <div class="md:col-span-5">
                                <label class="text-[10px] font-bold opacity-70 mb-1 block">📝 عنوان *</label>
                                <input type="text" wire:model="draftTitle" placeholder="مثال: انگشتر فیروزه"
                                       class="input input-bordered input-sm w-full">
                                @error('draftTitle') <span class="text-error text-[10px]">{{ $message }}</span> @enderror
                            </div>
                            <div class="md:col-span-3">
                                <label class="text-[10px] font-bold opacity-70 mb-1 block">💰 قیمت</label>
                                <input type="text" wire:model="draftPrice" dir="ltr"
                                       class="input input-bordered input-sm w-full font-mono text-left" placeholder="0">
                            </div>
                            <div class="md:col-span-2">
                                <label class="text-[10px] font-bold opacity-70 mb-1 block">📦 تعداد</label>
                                <input type="number" wire:model="draftQty" min="1"
                                       class="input input-bordered input-sm w-full text-center" dir="ltr">
                            </div>
                            <div class="md:col-span-2 flex items-end">
                                <label class="flex items-center gap-1.5 cursor-pointer text-[10px] font-bold w-full p-1.5 rounded-lg bg-white/40 dark:bg-black/20">
                                    <input type="checkbox" wire:model="draftCert" class="checkbox checkbox-xs checkbox-primary">
                                    <span>💎 شناسنامه</span>
                                </label>
                            </div>
                        </div>

                        <button type="button" wire:click="addDraftToCart" class="btn btn-primary btn-sm w-full">
                            ➕ افزودن به سبد
                        </button>
                    </div>

                    @if(count($cart) > 0)
                        <div class="mt-2 rounded-lg overflow-hidden"
                             style="background: var(--sg-glass-heavy); border: 1px solid var(--sg-glass-border);">
                            <div class="px-2.5 py-1.5 bg-black/5 dark:bg-white/5 flex items-center justify-between">
                                <span class="text-[11px] font-bold">🛒 سبد ({{ \App\Support\PersianNumber::toFa(count($cart)) }})</span>
                            </div>
                            <div class="divide-y divide-black/5 dark:divide-white/5">
                                @foreach($cart as $i => $item)
                                    <div class="p-2 flex items-center gap-2" wire:key="ci-{{ $i }}">
                                        <div class="flex-1 min-w-0">
                                            <div class="text-[11px] font-bold truncate">{{ $item['title'] ?? '—' }}</div>
                                            @if(!empty($item['sku']))
                                                <div class="text-[9.5px] font-mono opacity-50" dir="ltr">{{ $item['sku'] }}</div>
                                            @endif
                                        </div>
                                        <input type="number" min="1" value="{{ $item['qty'] ?? 1 }}"
                                               wire:change="updateCartQty({{ $i }}, $event.target.value)"
                                               class="input input-bordered input-xs w-14 text-center" dir="ltr">
                                        <input type="text" value="{{ number_format((float) ($item['price'] ?? 0)) }}"
                                               wire:change="updateCartPrice({{ $i }}, $event.target.value)"
                                               class="input input-bordered input-xs w-24 text-left font-mono" dir="ltr">
                                        <div class="text-[11px] font-bold text-primary w-20 text-left font-mono">
                                            {{ number_format(((float) ($item['price'] ?? 0)) * ((int) ($item['qty'] ?? 1))) }}
                                        </div>
                                        <button type="button" wire:click="removeCartItem({{ $i }})"
                                                class="btn btn-ghost btn-xs text-error">🗑️</button>
                                    </div>
                                @endforeach
                            </div>
                        </div>
                    @endif
                </section>

                {{-- ═══ مالی ═══ --}}
                <section>
                    <div class="flex items-center gap-2 mb-2">
                        <span class="w-5 h-5 rounded-full bg-primary text-white text-[10px] font-bold flex items-center justify-center">۳</span>
                        <h3 class="font-bold text-xs">💰 مالی</h3>
                    </div>

                    <div class="grid grid-cols-2 md:grid-cols-4 gap-2">
                        <div>
                            <label class="text-[10px] font-bold opacity-70 mb-1 flex items-center justify-between">
                                <span>💰 بیمه</span>
                                @if($insuranceManual)
                                    <button type="button" wire:click="recalcInsurance" class="text-[9px] text-primary hover:underline">↺ خودکار</button>
                                @endif
                            </label>
                            <input type="text" wire:model.live.debounce.500ms="insurance" dir="ltr"
                                   class="input input-bordered input-sm w-full font-mono text-center">
                        </div>
                        <div>
                            <label class="text-[10px] font-bold opacity-70 mb-1 block">📦 ارسال</label>
                            <input type="text" wire:model.live.debounce.400ms="shipping" dir="ltr"
                                   class="input input-bordered input-sm w-full font-mono text-center">
                        </div>
                        <div>
                            <label class="text-[10px] font-bold opacity-70 mb-1 block">🏷️ تخفیف</label>
                            <input type="text" wire:model.live.debounce.400ms="discount" dir="ltr"
                                   class="input input-bordered input-sm w-full font-mono text-center">
                        </div>
                        <div>
                            <label class="text-[10px] font-bold opacity-70 mb-1 block">🚦 وضعیت</label>
                            <select wire:model="status" class="select select-bordered select-sm w-full">
                                @foreach($statusOptions as $s)
                                    <option value="{{ $s['id'] }}">{{ $s['icon'] }} {{ $s['name'] }}</option>
                                @endforeach
                            </select>
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2">
                        <div>
                            <label class="text-[10px] font-bold opacity-70 mb-1 block">🌐 کانال</label>
                            <select wire:model="channelId" class="select select-bordered select-sm w-full">
                                <option value="">— انتخاب —</option>
                                @foreach($channels as $ch)
                                    <option value="{{ $ch->id }}">{{ $ch->name }}</option>
                                @endforeach
                            </select>
                        </div>
                        <div class="flex items-end">
                            <label class="flex items-center gap-2 cursor-pointer p-1.5 rounded-lg bg-black/5 dark:bg-white/5 w-full">
                                <input type="checkbox" wire:model="invoiceNeeded" class="checkbox checkbox-sm checkbox-primary">
                                <span class="text-[11px] font-bold">📄 فاکتور</span>
                            </label>
                        </div>
                    </div>

                    <div class="mt-2">
                        <label class="text-[10px] font-bold opacity-70 mb-1 block">📝 یادداشت</label>
                        <textarea wire:model="notes" rows="2" class="textarea textarea-bordered textarea-sm w-full" placeholder="..."></textarea>
                    </div>
                </section>

                {{-- ═══ جمع ═══ --}}
                <div class="rounded-lg p-2.5"
                     style="background: linear-gradient(135deg, rgba(13,148,136,0.08), rgba(8,145,178,0.04)); border: 1.5px solid rgba(13,148,136,0.2);">
                    <div class="space-y-1 text-xs">
                        <div class="flex justify-between opacity-70">
                            <span>جمع محصولات:</span>
                            <span class="font-mono">{{ number_format($this->subtotal) }}</span>
                        </div>
                        @if($this->insurance_amount > 0)
                            <div class="flex justify-between opacity-70">
                                <span>💰 بیمه:</span>
                                <span class="font-mono">{{ number_format($this->insurance_amount) }}</span>
                            </div>
                        @endif
                        @if($this->shipping_amount > 0)
                            <div class="flex justify-between opacity-70">
                                <span>📦 ارسال:</span>
                                <span class="font-mono">{{ number_format($this->shipping_amount) }}</span>
                            </div>
                        @endif
                        @if($this->discount_amount > 0)
                            <div class="flex justify-between text-warning">
                                <span>🏷️ تخفیف:</span>
                                <span class="font-mono">- {{ number_format($this->discount_amount) }}</span>
                            </div>
                        @endif
                        <div class="flex justify-between border-t border-primary/20 pt-1.5 mt-1.5">
                            <span class="font-bold text-sm">💵 نهایی:</span>
                            <span class="font-bold text-primary text-base font-mono">{{ number_format($this->total) }} تومان</span>
                        </div>
                    </div>
                </div>
            </div>

            {{-- Footer --}}
            <div class="p-2.5 flex items-center justify-between gap-2 border-t border-black/5 dark:border-white/5 bg-black/5 dark:bg-white/5">
                <button wire:click="close" class="btn btn-ghost btn-sm">انصراف</button>
                <button wire:click="save" wire:loading.attr="disabled" class="btn btn-success btn-sm">
                    <span wire:loading.remove wire:target="save">✅ {{ $mode === 'edit' ? 'ویرایش' : 'ثبت' }}</span>
                    <span wire:loading wire:target="save">⏳</span>
                </button>
            </div>
        </div>
    </div>
    @endif
</div>
'''

# ═══════════════════════════════════════════════════════════════
# ۶) Status Cell Click → Popup (نه صفحه)
# ═══════════════════════════════════════════════════════════════

ORDER_VIEW_PHP = r'''<?php

namespace App\Livewire\Orders;

use App\Models\Order;
use Livewire\Attributes\On;
use Livewire\Component;

class ViewModal extends Component
{
    public bool $show = false;
    public ?int $orderId = null;
    public ?Order $order = null;

    #[On('open-order-view')]
    public function open(int $orderId): void
    {
        $this->orderId = $orderId;
        $this->order = Order::with(['customer', 'items', 'channel'])->find($orderId);
        $this->show = true;
    }

    public function close(): void
    {
        $this->show = false;
        $this->orderId = null;
        $this->order = null;
    }

    public function editOrder(): void
    {
        $id = $this->orderId;
        $this->close();
        $this->dispatch('open-order-form', orderId: $id);
    }

    public function cycleStatus(): void
    {
        if (!$this->order) return;
        $statuses = ['pending', 'final-check', 'courier'];
        $cur = array_search($this->order->status ?? 'pending', $statuses);
        $next = $statuses[($cur === false ? 0 : ($cur + 1)) % count($statuses)];
        $this->order->update(['status' => $next]);
        $this->order->refresh();
        $this->dispatch('notify', type: 'success', message: 'وضعیت: ' . $next);
        $this->dispatch('order-updated');
    }

    public function deleteOrder(): void
    {
        if (!$this->order) return;
        $this->order->delete();
        $this->dispatch('notify', type: 'success', message: 'حذف شد');
        $this->close();
        $this->dispatch('order-updated');
    }

    public function render()
    {
        return view('livewire.orders.view-modal');
    }
}
'''

ORDER_VIEW_BLADE = r'''<div>
    @if($show && $order)
    <div class="sg-modal-overlay" wire:key="ovm-{{ $orderId }}"
         @keydown.escape.window="$wire.close()">
        <div class="sg-modal" style="max-width: 620px;">

            <div class="flex items-center justify-between p-3 border-b border-black/5 dark:border-white/5"
                 style="background: linear-gradient(90deg, rgba(13,148,136,0.08), transparent);">
                <div>
                    <div class="font-bold text-sm">📋 سفارش #{{ $order->order_number ?? $order->id }}</div>
                    <div class="text-[10px] opacity-60 mt-0.5">{{ \App\Support\PersianDate::format($order->created_at, 'Y/m/d H:i') }}</div>
                </div>
                <button wire:click="close" class="btn btn-ghost btn-sm btn-circle">✕</button>
            </div>

            <div class="p-3 space-y-3 max-h-[calc(100vh-13rem)] overflow-y-auto">

                {{-- وضعیت + کانال --}}
                <div class="flex flex-wrap gap-1.5">
                    @php
                        $statusMap = ['pending' => ['📝', 'ثبت سفارش', 'pending'], 'final-check' => ['🔍', 'چک نهایی', 'final-check'], 'courier' => ['🚚', 'تحویل مامور', 'courier']];
                        $s = $statusMap[$order->status] ?? ['📝', 'ثبت', 'pending'];
                    @endphp
                    <button wire:click="cycleStatus" class="sg-status-cell {{ $s[2] }} py-1.5 px-3 text-xs">
                        <span class="icon">{{ $s[0] }}</span>
                        <span>{{ $s[1] }}</span>
                        <span class="text-[9px] opacity-60">↻</span>
                    </button>
                    @if($order->channel)
                        <span class="badge badge-sm">{{ $order->channel->name }}</span>
                    @endif
                    @if($order->invoice_needed)
                        <span class="badge badge-info badge-sm">📄 فاکتور</span>
                    @endif
                </div>

                {{-- مشتری --}}
                <div class="rounded-lg p-2.5" style="background: rgba(13,148,136,0.05);">
                    <div class="text-[10px] font-bold opacity-60 mb-1">👤 مشتری</div>
                    <div class="font-bold text-sm">{{ $order->customer_name ?? $order->customer?->name ?? '—' }}</div>
                    <div class="font-mono text-xs opacity-70 mt-0.5" dir="ltr">{{ $order->phone ?? '—' }}</div>
                </div>

                {{-- آدرس --}}
                @if($order->address)
                    <div class="rounded-lg p-2.5" style="background: rgba(0,0,0,0.03);">
                        <div class="text-[10px] font-bold opacity-60 mb-1">📍 آدرس</div>
                        <div class="text-xs leading-relaxed">{{ $order->address }}</div>
                        @if($order->postal_code)
                            <div class="text-[10px] font-mono opacity-60 mt-1" dir="ltr">📮 {{ $order->postal_code }}</div>
                        @endif
                    </div>
                @endif

                {{-- محصولات --}}
                @if($order->items->count() > 0)
                    <div>
                        <div class="text-[10px] font-bold opacity-60 mb-1.5">🛍️ محصولات ({{ \App\Support\PersianNumber::toFa($order->items->count()) }})</div>
                        <div class="rounded-lg overflow-hidden" style="border: 1px solid var(--sg-glass-border);">
                            @foreach($order->items as $item)
                                <div class="p-2 flex items-center gap-2 border-b border-black/5 dark:border-white/5 last:border-0">
                                    <div class="flex-1 min-w-0">
                                        <div class="text-xs font-bold truncate">{{ $item->title ?? $item->name ?? '—' }}</div>
                                        @if($item->sku)
                                            <div class="text-[9.5px] font-mono opacity-50" dir="ltr">{{ $item->sku }}</div>
                                        @endif
                                    </div>
                                    <div class="text-[10px] opacity-60">×{{ \App\Support\PersianNumber::toFa($item->quantity) }}</div>
                                    <div class="text-xs font-bold font-mono">{{ number_format((float) $item->price) }}</div>
                                </div>
                            @endforeach
                        </div>
                    </div>
                @endif

                {{-- مالی --}}
                <div class="rounded-lg p-2.5" style="background: rgba(13,148,136,0.05);">
                    <div class="space-y-1 text-xs">
                        <div class="flex justify-between opacity-70">
                            <span>💰 بیمه:</span>
                            <span class="font-mono">{{ number_format((float) ($order->insurance ?? 0)) }}</span>
                        </div>
                        @if(($order->discount ?? 0) > 0)
                            <div class="flex justify-between text-warning">
                                <span>🏷️ تخفیف:</span>
                                <span class="font-mono">- {{ number_format((float) $order->discount) }}</span>
                            </div>
                        @endif
                        <div class="flex justify-between border-t border-primary/20 pt-1.5 mt-1.5">
                            <span class="font-bold text-sm">💵 نهایی:</span>
                            <span class="font-bold text-primary font-mono">{{ number_format((float) ($order->amount ?? 0)) }} ت</span>
                        </div>
                    </div>
                </div>

                @if($order->notes)
                    <div class="rounded-lg p-2.5" style="background: rgba(0,0,0,0.03);">
                        <div class="text-[10px] font-bold opacity-60 mb-1">📝 یادداشت</div>
                        <div class="text-xs">{{ $order->notes }}</div>
                    </div>
                @endif
            </div>

            <div class="p-2.5 flex items-center justify-between gap-2 border-t border-black/5 dark:border-white/5 bg-black/5 dark:bg-white/5">
                <button wire:click="deleteOrder" wire:confirm="حذف شود؟" class="btn btn-error btn-xs">🗑️</button>
                <div class="flex gap-1.5">
                    <button wire:click="close" class="btn btn-ghost btn-sm">بستن</button>
                    <button wire:click="editOrder" class="btn btn-primary btn-sm">✏️ ویرایش</button>
                </div>
            </div>
        </div>
    </div>
    @endif
</div>
'''

# ═══════════════════════════════════════════════════════════════
# ۷) Reports — بازسازی کامل
# ═══════════════════════════════════════════════════════════════

REPORTS_PHP = r'''<?php

namespace App\Livewire\Reports;

use App\Models\Certificate;
use App\Models\Customer;
use App\Models\Order;
use App\Models\Product;
use Livewire\Component;

class Index extends Component
{
    public string $range = 'today';

    public function setRange(string $range): void
    {
        $this->range = $range;
    }

    public function getStartDateProperty()
    {
        return match($this->range) {
            'today'   => now()->startOfDay(),
            'week'    => now()->subDays(7)->startOfDay(),
            'month'   => now()->subDays(30)->startOfDay(),
            'year'    => now()->startOfYear(),
            default   => now()->startOfDay(),
        };
    }

    public function render()
    {
        $start = $this->start_date;

        $orders = Order::where('created_at', '>=', $start);
        $total = (clone $orders)->count();
        $amount = (float) (clone $orders)->sum('amount');
        $avgAmount = $total > 0 ? $amount / $total : 0;

        // آمار به تفکیک وضعیت
        $byStatus = [
            'pending'     => (clone $orders)->where('status', 'pending')->count(),
            'final-check' => (clone $orders)->where('status', 'final-check')->count(),
            'courier'     => (clone $orders)->where('status', 'courier')->count(),
        ];

        // روند روزانه (۷ روز اخیر)
        $daily = [];
        for ($i = 6; $i >= 0; $i--) {
            $d = now()->subDays($i);
            $daily[] = [
                'date'   => \App\Support\PersianDate::format($d, 'm/d'),
                'count'  => Order::whereDate('created_at', $d)->count(),
                'amount' => (float) Order::whereDate('created_at', $d)->sum('amount'),
            ];
        }

        // بهترین مشتریان
        $topCustomers = Customer::withCount('orders')
            ->having('orders_count', '>', 0)
            ->orderByDesc('orders_count')
            ->limit(5)
            ->get();

        // آمار کلی
        $stats = [
            'customers'    => Customer::count(),
            'orders_total' => Order::count(),
            'products'     => Product::count(),
            'certificates' => Certificate::count(),
        ];

        return view('livewire.reports.index', [
            'total'        => $total,
            'amount'       => $amount,
            'avgAmount'    => $avgAmount,
            'byStatus'     => $byStatus,
            'daily'        => $daily,
            'topCustomers' => $topCustomers,
            'stats'        => $stats,
        ])->layout('components.layouts.app');
    }
}
'''

REPORTS_BLADE = r'''<div class="p-3 md:p-5 max-w-6xl mx-auto space-y-4">
    <h1 class="text-lg md:text-xl font-bold mb-2">📊 گزارش‌ها</h1>

    {{-- فیلتر بازه --}}
    <div class="sg-card p-3 flex flex-wrap items-center gap-2">
        <span class="text-xs font-bold opacity-60">بازه:</span>
        @foreach(['today' => 'امروز', 'week' => '۷ روز', 'month' => '۳۰ روز', 'year' => 'سال'] as $k => $v)
            <button wire:click="setRange('{{ $k }}')"
                    class="px-3 py-1.5 rounded-lg text-xs font-bold transition {{ $range === $k ? 'bg-primary text-white' : 'bg-black/5 dark:bg-white/5' }}">
                {{ $v }}
            </button>
        @endforeach

        <div class="flex-1"></div>

        <a href="{{ route('reports.export.excel', ['range' => $range]) }}"
           class="btn btn-outline btn-sm">📥 CSV</a>
    </div>

    {{-- کارت‌های اصلی --}}
    <div class="sg-dashboard-grid">
        <div class="sg-stat-card">
            <div class="icon">📦</div>
            <div class="info">
                <div class="num">{{ \App\Support\PersianNumber::toFa($total) }}</div>
                <div class="lbl">سفارش</div>
            </div>
        </div>
        <div class="sg-stat-card">
            <div class="icon">💰</div>
            <div class="info">
                <div class="num">{{ number_format($amount / 1000000, 1) }}M</div>
                <div class="lbl">فروش</div>
            </div>
        </div>
        <div class="sg-stat-card">
            <div class="icon">📊</div>
            <div class="info">
                <div class="num">{{ number_format($avgAmount / 1000, 0) }}K</div>
                <div class="lbl">میانگین</div>
            </div>
        </div>
        <div class="sg-stat-card">
            <div class="icon">👥</div>
            <div class="info">
                <div class="num">{{ \App\Support\PersianNumber::toFa($stats['customers']) }}</div>
                <div class="lbl">مشتری</div>
            </div>
        </div>
    </div>

    {{-- وضعیت‌ها --}}
    <div class="grid grid-cols-1 md:grid-cols-3 gap-3">
        <div class="sg-card p-3">
            <div class="flex items-center gap-2 mb-2">
                <div class="w-8 h-8 rounded-lg flex items-center justify-center bg-orange-500/15 text-orange-600">📝</div>
                <div>
                    <div class="text-xs font-bold">در انتظار</div>
                    <div class="text-lg font-bold text-orange-600">{{ \App\Support\PersianNumber::toFa($byStatus['pending']) }}</div>
                </div>
            </div>
            <div class="h-1.5 rounded-full bg-orange-500/20 overflow-hidden">
                <div class="h-full bg-orange-500" style="width: {{ $total > 0 ? ($byStatus['pending'] / $total * 100) : 0 }}%"></div>
            </div>
        </div>
        <div class="sg-card p-3">
            <div class="flex items-center gap-2 mb-2">
                <div class="w-8 h-8 rounded-lg flex items-center justify-center bg-blue-500/15 text-blue-600">🔍</div>
                <div>
                    <div class="text-xs font-bold">چک نهایی</div>
                    <div class="text-lg font-bold text-blue-600">{{ \App\Support\PersianNumber::toFa($byStatus['final-check']) }}</div>
                </div>
            </div>
            <div class="h-1.5 rounded-full bg-blue-500/20 overflow-hidden">
                <div class="h-full bg-blue-500" style="width: {{ $total > 0 ? ($byStatus['final-check'] / $total * 100) : 0 }}%"></div>
            </div>
        </div>
        <div class="sg-card p-3">
            <div class="flex items-center gap-2 mb-2">
                <div class="w-8 h-8 rounded-lg flex items-center justify-center bg-green-500/15 text-green-600">🚚</div>
                <div>
                    <div class="text-xs font-bold">تحویل مامور</div>
                    <div class="text-lg font-bold text-green-600">{{ \App\Support\PersianNumber::toFa($byStatus['courier']) }}</div>
                </div>
            </div>
            <div class="h-1.5 rounded-full bg-green-500/20 overflow-hidden">
                <div class="h-full bg-green-500" style="width: {{ $total > 0 ? ($byStatus['courier'] / $total * 100) : 0 }}%"></div>
            </div>
        </div>
    </div>

    {{-- روند روزانه --}}
    <div class="sg-card p-4">
        <h2 class="text-sm font-bold mb-3">📈 روند ۷ روز اخیر</h2>
        @php $max = collect($daily)->max('count') ?: 1; @endphp
        <div class="flex items-end gap-1.5 h-40">
            @foreach($daily as $d)
                <div class="flex-1 flex flex-col items-center gap-1">
                    <div class="text-[10px] font-bold opacity-70">{{ $d['count'] > 0 ? \App\Support\PersianNumber::toFa($d['count']) : '' }}</div>
                    <div class="w-full rounded-t-lg bg-gradient-to-t from-teal-500 to-cyan-400 transition-all"
                         style="height: {{ max(4, $d['count'] / $max * 100) }}%"
                         title="{{ number_format($d['amount']) }}"></div>
                    <div class="text-[9px] font-mono opacity-55">{{ $d['date'] }}</div>
                </div>
            @endforeach
        </div>
    </div>

    {{-- بهترین مشتریان --}}
    @if($topCustomers->count() > 0)
        <div class="sg-card p-4">
            <h2 class="text-sm font-bold mb-3">⭐ بهترین مشتریان</h2>
            <div class="space-y-1">
                @foreach($topCustomers as $i => $c)
                    <a href="{{ route('customers.show', $c) }}" wire:navigate
                       class="flex items-center gap-3 p-2 rounded-lg hover:bg-black/5 dark:hover:bg-white/5 transition">
                        <div class="w-7 h-7 rounded-full flex items-center justify-center text-white text-xs font-bold"
                             style="background: linear-gradient(135deg, #14b8a6, #0891b2);">
                            {{ \App\Support\PersianNumber::toFa($i + 1) }}
                        </div>
                        <div class="flex-1 min-w-0">
                            <div class="text-xs font-bold truncate">{{ $c->name }}</div>
                            <div class="text-[10px] font-mono opacity-55" dir="ltr">{{ $c->phone }}</div>
                        </div>
                        <div class="badge badge-primary badge-sm">{{ \App\Support\PersianNumber::toFa($c->orders_count) }} سفارش</div>
                    </a>
                @endforeach
            </div>
        </div>
    @endif

    {{-- آمار کلی --}}
    <div class="sg-dashboard-grid">
        <div class="sg-stat-card">
            <div class="icon">🛍️</div>
            <div class="info">
                <div class="num">{{ \App\Support\PersianNumber::toFa($stats['products']) }}</div>
                <div class="lbl">محصول</div>
            </div>
        </div>
        <div class="sg-stat-card">
            <div class="icon">💎</div>
            <div class="info">
                <div class="num">{{ \App\Support\PersianNumber::toFa($stats['certificates']) }}</div>
                <div class="lbl">شناسنامه</div>
            </div>
        </div>
        <div class="sg-stat-card">
            <div class="icon">📊</div>
            <div class="info">
                <div class="num">{{ \App\Support\PersianNumber::toFa($stats['orders_total']) }}</div>
                <div class="lbl">کل سفارش</div>
            </div>
        </div>
    </div>
</div>
'''

# ═══════════════════════════════════════════════════════════════
# ۸) ProductSync Command
# ═══════════════════════════════════════════════════════════════

SYNC_COMMAND = r'''<?php

namespace App\Console\Commands;

use App\Models\AppSetting;
use App\Models\Product;
use Illuminate\Console\Command;
use Illuminate\Support\Facades\Http;

class SyncProducts extends Command
{
    protected $signature = 'shopgun:sync-products {--force : بدون تأیید}';
    protected $description = 'سینک محصولات از WooCommerce';

    public function handle(): int
    {
        $url = AppSetting::get('commerce_url', '');
        $key = AppSetting::get('commerce_key', '');
        $secret = AppSetting::get('commerce_secret', '');

        if (!$url || !$key || !$secret) {
            $this->error('اطلاعات کامرس تنظیم نشده. ابتدا /settings → کامرس');
            return 1;
        }

        // پاکسازی URL
        $base = rtrim($url, '/');
        if (!str_contains($base, '/wp-json')) {
            $base .= '/wp-json/wc/v3';
        }

        $this->info("سینک از: {$base}");

        $page = 1;
        $created = 0;
        $updated = 0;
        $errors = 0;
        $total = 0;

        $bar = $this->output->createProgressBar();
        $bar->start();

        while ($page <= 100) {
            try {
                $response = Http::withBasicAuth($key, $secret)
                    ->timeout(60)
                    ->get("{$base}/products", [
                        'per_page' => 100,
                        'page' => $page,
                        'status' => 'publish',
                    ]);

                if (!$response->successful()) {
                    $this->newLine();
                    $this->error("HTTP {$response->status()}: " . substr($response->body(), 0, 200));
                    break;
                }

                $products = $response->json();
                if (!is_array($products) || empty($products)) break;

                foreach ($products as $wc) {
                    try {
                        $sku = $wc['sku'] ?? null;
                        if (!$sku) $sku = 'WC-' . $wc['id'];

                        $exists = Product::where('sku', $sku)->exists();

                        Product::updateOrCreate(['sku' => $sku], [
                            'sku'               => $sku,
                            'wc_id'             => $wc['id'] ?? null,
                            'name'              => $wc['name'] ?? '',
                            'price'             => (float) ($wc['price'] ?? 0),
                            'regular_price'     => (float) ($wc['regular_price'] ?? 0),
                            'stock_quantity'    => $wc['stock_quantity'] ?? null,
                            'stock_status'      => $wc['stock_status'] ?? 'instock',
                            'image_url'         => $wc['images'][0]['src'] ?? null,
                            'weight'            => !empty($wc['weight']) ? (float) $wc['weight'] : null,
                            'categories'        => array_map(fn($c) => ['id' => $c['id'] ?? null, 'name' => $c['name'] ?? ''], $wc['categories'] ?? []),
                            'attributes'        => array_map(fn($a) => ['name' => $a['name'] ?? '', 'options' => $a['options'] ?? []], $wc['attributes'] ?? []),
                            'wc_data'           => $wc,
                            'is_active'         => true,
                            'synced_at'         => now(),
                        ]);

                        if ($exists) $updated++;
                        else         $created++;
                        $total++;
                        $bar->advance();
                    } catch (\Throwable $e) {
                        $errors++;
                    }
                }

                if (count($products) < 100) break;
                $page++;
            } catch (\Throwable $e) {
                $this->newLine();
                $this->error('خطا: ' . $e->getMessage());
                break;
            }
        }

        $bar->finish();
        $this->newLine(2);

        $this->table(
            ['مورد', 'تعداد'],
            [
                ['کل', $total],
                ['جدید', $created],
                ['بروز شده', $updated],
                ['خطا', $errors],
            ]
        );

        return 0;
    }
}
'''

# ═══════════════════════════════════════════════════════════════
# ۹) Settings Index — با پیش‌نمایش برچسب + اعلان
# ═══════════════════════════════════════════════════════════════

def patch_settings_index():
    path = PROJECT / "app/Livewire/Settings/Index.php"
    if not path.exists():
        print("  ⚠️ Settings Index پیدا نشد")
        return

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # اضافه کردن متد test connection بهتر + notify در همه‌ی save
    if "'dispatch(\'notify'" not in content:
        print("  ⚠️ Settings Index بدون notify — دستی چک کن")
        return

    print("  ✓ Settings Index از قبل notify دارد")

# ═══════════════════════════════════════════════════════════════
# اجرا
# ═══════════════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  ShopGun V2 — Comprehensive Fix Pack                          ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    for rel in [
        "resources/views/components/layouts/app.blade.php",
        "resources/views/livewire/components/sidebar.blade.php",
        "resources/views/livewire/orders/form-modal.blade.php",
        "resources/views/livewire/orders/view-modal.blade.php",
        "resources/views/livewire/reports/index.blade.php",
        "app/Livewire/Orders/FormModal.php",
        "app/Livewire/Orders/ViewModal.php",
        "app/Livewire/Reports/Index.php",
    ]:
        backup(rel)

    print("📄 نوشتن فایل‌ها...")
    write("public/css/shopgun.css", SHOPGUN_CSS)
    write("resources/views/components/layouts/app.blade.php", LAYOUT_BLADE)
    write("resources/views/livewire/components/sidebar.blade.php", SIDEBAR_BLADE)
    write("app/Livewire/Orders/FormModal.php", ORDER_FORM_PHP)
    write("resources/views/livewire/orders/form-modal.blade.php", ORDER_FORM_BLADE)
    write("app/Livewire/Orders/ViewModal.php", ORDER_VIEW_PHP)
    write("resources/views/livewire/orders/view-modal.blade.php", ORDER_VIEW_BLADE)
    write("app/Livewire/Reports/Index.php", REPORTS_PHP)
    write("resources/views/livewire/reports/index.blade.php", REPORTS_BLADE)
    write("app/Console/Commands/SyncProducts.php", SYNC_COMMAND)

    print("\n" + "═" * 64)
    print("✅ تمام!")
    print("═" * 64)
    print(f"""
📋 دستورات — دقیقاً به ترتیب:

  cd {PROJECT}

  # ⚠️ مهم‌ترین
  php artisan storage:link

  # پاک‌سازی
  php artisan optimize:clear
  php artisan view:clear
  php artisan route:clear

  # ★★ سینک محصولات از WooCommerce ★★
  php artisan shopgun:sync-products

  # سرور
  php artisan serve

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 چه چیزی حل شد:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✅ NOT NULL constraint order_items.title
       → ستون title پر می‌شه (قبلاً name می‌فرستاد)
  ✅ Products = 0
       → دستور `php artisan shopgun:sync-products`
  ✅ بیمه خودکار
       → مبلغ کل / 1,000,000 (25M → 25)
       → دکمه "↺ خودکار" برای بازمحاسبه
  ✅ Sidebar باریک 240px + KPI افقی اسکرول
  ✅ Dropdown/Modal با Blur
  ✅ نمایش سفارش → Popup (نه صفحه)
  ✅ Status cell کوچک با آیکون و عدد
  ✅ گزارشات کامل با نمودار
  ✅ Storage:link → تصاویر 404 حل
  ✅ Layout با theme/density toggle واقعی

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 نکته مهم:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  اگر storage:link خطا داد، این رو دستی بزن:
  
    cd public
    rmdir storage 2>nul
    mklink /J storage ..\\storage\\app\\public
    cd ..

  و برای تست سینک:
  
    php artisan shopgun:sync-products --force
""")

if __name__ == "__main__":
    main()