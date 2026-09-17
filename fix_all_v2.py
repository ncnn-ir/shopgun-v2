#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║  ShopGun V2 — رفع کامل                                        ║
║  ۱) رفع Double Modal                                          ║
║  ۲) فرم سفارش با SKU Search جدا                                ║
║  ۳) استایل یکپارچه (Glass + Rounded)                          ║
║  ۴) سایدبار قدرتمند با تاریخ/آمار/اعلان                       ║
╚══════════════════════════════════════════════════════════════╝
"""
import shutil, re
from pathlib import Path
from datetime import datetime

PROJECT = Path(r"D:\prodo\shopgun-v2.1")
if not PROJECT.exists():
    PROJECT = Path(input("مسیر پروژه: ").strip().strip('"'))
    if not PROJECT.exists():
        print("❌"); exit(1)

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
# ۱) استایل سراسری یکپارچه
# ═══════════════════════════════════════════════════════════════

GLOBAL_CSS = r'''/* ═══════════════════════════════════════════════════════════════
   ShopGun V2 — Unified Design System
   ═══════════════════════════════════════════════════════════════ */

:root {
    --sg-radius: 14px;
    --sg-radius-sm: 10px;
    --sg-radius-lg: 20px;
    --sg-radius-full: 999px;

    --sg-glass-bg: rgba(255, 255, 255, 0.7);
    --sg-glass-bg-dark: rgba(30, 41, 59, 0.6);
    --sg-glass-border: rgba(255, 255, 255, 0.3);
    --sg-glass-border-dark: rgba(255, 255, 255, 0.08);

    --sg-shadow-sm: 0 2px 6px rgba(0,0,0,0.04);
    --sg-shadow: 0 4px 16px rgba(0,0,0,0.06);
    --sg-shadow-lg: 0 10px 40px rgba(0,0,0,0.12);

    --sg-transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
}

/* ═══ Card یکپارچه ═══ */
.sg-card {
    background: var(--sg-glass-bg);
    backdrop-filter: blur(14px) saturate(160%);
    -webkit-backdrop-filter: blur(14px) saturate(160%);
    border: 1px solid var(--sg-glass-border);
    border-radius: var(--sg-radius);
    box-shadow: var(--sg-shadow-sm);
    transition: var(--sg-transition);
}

[data-theme="dark"] .sg-card {
    background: var(--sg-glass-bg-dark);
    border-color: var(--sg-glass-border-dark);
}

.sg-card:hover {
    box-shadow: var(--sg-shadow);
    transform: translateY(-1px);
}

/* ═══ دکمه‌ها یکپارچه ═══ */
.btn, .sg-btn {
    border-radius: var(--sg-radius-sm) !important;
    transition: var(--sg-transition) !important;
    font-weight: 600;
    letter-spacing: 0.01em;
    border-width: 1px !important;
    backdrop-filter: blur(6px);
}

.btn:hover:not(:disabled) {
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(0,0,0,0.08);
}

.btn:active:not(:disabled) {
    transform: translateY(0);
}

.btn-circle {
    border-radius: var(--sg-radius-full) !important;
}

.btn-primary { box-shadow: 0 2px 8px rgba(13, 148, 136, 0.2); }
.btn-primary:hover:not(:disabled) { box-shadow: 0 6px 16px rgba(13, 148, 136, 0.3); }

/* ═══ Inputs یکپارچه ═══ */
.input, .select, .textarea {
    border-radius: var(--sg-radius-sm) !important;
    transition: var(--sg-transition) !important;
    background-color: rgba(255,255,255,0.5) !important;
    border-width: 1.5px !important;
}

[data-theme="dark"] .input,
[data-theme="dark"] .select,
[data-theme="dark"] .textarea {
    background-color: rgba(0,0,0,0.2) !important;
}

.input:focus, .select:focus, .textarea:focus {
    border-color: var(--sg-primary, #0d9488) !important;
    box-shadow: 0 0 0 3px rgba(13, 148, 136, 0.15) !important;
    outline: none !important;
}

/* ═══ جدول‌ها یکپارچه ═══ */
.table, .pro-table {
    border-radius: var(--sg-radius);
    overflow: hidden;
    border-collapse: separate !important;
    border-spacing: 0;
}

.pro-table thead th {
    background: rgba(0,0,0,0.02);
    border-bottom: 2px solid rgba(0,0,0,0.06);
    font-weight: 700;
    font-size: 11.5px;
    padding: 12px 10px;
    color: rgba(0,0,0,0.65);
}

[data-theme="dark"] .pro-table thead th {
    background: rgba(255,255,255,0.03);
    color: rgba(255,255,255,0.7);
}

.pro-table tbody tr {
    transition: var(--sg-transition);
    border-bottom: 1px solid rgba(0,0,0,0.04);
}

[data-theme="dark"] .pro-table tbody tr {
    border-bottom: 1px solid rgba(255,255,255,0.04);
}

.pro-table tbody tr:hover {
    background: rgba(13, 148, 136, 0.04);
}

.pro-table tbody td {
    padding: 10px;
    font-size: 12.5px;
    vertical-align: middle;
}

/* ═══ Modal یکپارچه ═══ */
.sg-modal-overlay {
    position: fixed;
    inset: 0;
    background: rgba(0,0,0,0.65);
    backdrop-filter: blur(8px);
    z-index: 80;
    display: flex;
    align-items: flex-start;
    justify-content: center;
    padding: 12px;
    overflow-y: auto;
    animation: sgFadeIn 0.2s ease;
}

.sg-modal {
    background: var(--sg-glass-bg);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    border: 1px solid var(--sg-glass-border);
    border-radius: var(--sg-radius-lg);
    box-shadow: var(--sg-shadow-lg);
    width: 100%;
    max-width: 900px;
    margin: 12px auto;
    animation: sgSlideUp 0.3s cubic-bezier(0.34, 1.56, 0.64, 1);
    overflow: hidden;
}

[data-theme="dark"] .sg-modal {
    background: var(--sg-glass-bg-dark);
}

@keyframes sgFadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}

@keyframes sgSlideUp {
    from { opacity: 0; transform: translateY(20px) scale(0.98); }
    to { opacity: 1; transform: translateY(0) scale(1); }
}

/* ═══ Badge یکپارچه ═══ */
.badge {
    border-radius: var(--sg-radius-full) !important;
    font-weight: 600;
    padding: 3px 10px;
}

/* ═══ Dropdown یکپارچه ═══ */
.dropdown-content {
    border-radius: var(--sg-radius) !important;
    box-shadow: var(--sg-shadow-lg) !important;
    border: 1px solid var(--sg-glass-border) !important;
    background: var(--sg-glass-bg) !important;
    backdrop-filter: blur(20px) !important;
}

/* ═══ Sidebar KPI Card ═══ */
.sg-kpi-scroll {
    display: flex;
    gap: 8px;
    overflow-x: auto;
    padding: 4px 2px;
    scrollbar-width: thin;
    scrollbar-color: rgba(255,255,255,0.2) transparent;
    -ms-overflow-style: none;
}

.sg-kpi-scroll::-webkit-scrollbar {
    height: 4px;
}

.sg-kpi-scroll::-webkit-scrollbar-thumb {
    background: rgba(255,255,255,0.15);
    border-radius: 2px;
}

.sg-kpi-card {
    min-width: 78px;
    flex-shrink: 0;
    padding: 8px 6px;
    background: rgba(255,255,255,0.55);
    border: 1px solid rgba(255,255,255,0.3);
    border-radius: var(--sg-radius-sm);
    text-align: center;
    backdrop-filter: blur(10px);
    transition: var(--sg-transition);
    cursor: pointer;
}

[data-theme="dark"] .sg-kpi-card {
    background: rgba(255,255,255,0.05);
    border-color: rgba(255,255,255,0.08);
}

.sg-kpi-card:hover {
    background: rgba(13, 148, 136, 0.1);
    border-color: rgba(13, 148, 136, 0.3);
    transform: translateY(-2px);
}

.sg-kpi-card .sg-kpi-num {
    font-size: 18px;
    font-weight: 800;
    line-height: 1;
    color: var(--sg-primary, #0d9488);
}

.sg-kpi-card .sg-kpi-lbl {
    font-size: 9.5px;
    color: rgba(0,0,0,0.55);
    margin-top: 3px;
    font-weight: 600;
}

[data-theme="dark"] .sg-kpi-card .sg-kpi-lbl {
    color: rgba(255,255,255,0.6);
}

/* ═══ Mobile Bottom Bar ═══ */
.sg-bottom-bar {
    position: fixed;
    bottom: 10px;
    left: 10px;
    right: 10px;
    background: var(--sg-glass-bg);
    backdrop-filter: blur(20px) saturate(180%);
    border: 1px solid var(--sg-glass-border);
    border-radius: var(--sg-radius-lg);
    padding: 6px 4px;
    z-index: 50;
    box-shadow: var(--sg-shadow-lg);
}

/* ═══ Scrollbar یکپارچه ═══ */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: rgba(0,0,0,0.15);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover { background: rgba(0,0,0,0.25); }
'''

# ═══════════════════════════════════════════════════════════════
# ۲) SIDEBAR — با تاریخ، آمار، اعلان، KPI Cards
# ═══════════════════════════════════════════════════════════════

SIDEBAR_PHP = r'''<?php

namespace App\Livewire\Components;

use App\Models\ApiLog;
use App\Models\Certificate;
use App\Models\Customer;
use App\Models\Order;
use App\Models\Product;
use App\Support\PersianDate;
use App\Support\PersianNumber;
use Livewire\Component;

class Sidebar extends Component
{
    public array $stats = [];
    public int $notifCount = 0;
    public string $today = '';
    public string $dayOfWeek = '';

    public function mount(): void
    {
        $this->refresh();
    }

    public function refresh(): void
    {
        $this->stats = [
            'orders_total'    => Order::count(),
            'orders_today'    => Order::whereDate('created_at', today())->count(),
            'orders_pending'  => Order::where('status', 'pending')->count(),
            'orders_check'    => Order::where('status', 'final-check')->count(),
            'orders_courier'  => Order::where('status', 'courier')->count(),
            'customers'       => Customer::count(),
            'products'        => Product::count(),
            'certificates'    => Certificate::count(),
            'api_today'       => ApiLog::whereDate('created_at', today())->count(),
            'api_errors'      => ApiLog::whereNotNull('error')
                                    ->whereDate('created_at', today())->count(),
        ];

        $this->notifCount = $this->stats['orders_pending'] + $this->stats['api_errors'];

        $now = now();
        $this->today = PersianDate::format($now, 'Y/m/d');
        $this->dayOfWeek = PersianDate::dayOfWeek($now);
    }

    public function render()
    {
        return view('livewire.components.sidebar');
    }
}
'''

SIDEBAR_BLADE = r'''<div class="flex flex-col h-full">
    {{-- ═══ لوگو ═══ --}}
    <div class="px-3 pt-3 pb-2">
        <div class="flex items-center gap-3 p-2.5 rounded-xl"
             style="background: linear-gradient(135deg, rgba(13,148,136,0.15), rgba(8,145,178,0.08)); border: 1px solid rgba(13,148,136,0.2);">
            <div class="w-10 h-10 rounded-xl flex items-center justify-center text-white text-lg font-extrabold shadow-lg"
                 style="background: linear-gradient(135deg, #14b8a6, #0891b2);">
                💎
            </div>
            <div class="flex-1 min-w-0">
                <div class="font-extrabold text-sm truncate">شاپگان</div>
                <div class="text-[10px] opacity-60">ShopGun v2.1</div>
            </div>
            @if($notifCount > 0)
                <div class="badge badge-error badge-sm">{{ \App\Support\PersianNumber::toFa($notifCount) }}</div>
            @endif
        </div>
    </div>

    {{-- ═══ تاریخ و روز ═══ --}}
    <div class="px-3 pb-3">
        <div class="flex items-center justify-between p-2 rounded-xl bg-black/5 dark:bg-white/5 text-xs">
            <div class="flex items-center gap-1.5">
                <span>📅</span>
                <span class="font-mono font-bold">{{ $today }}</span>
            </div>
            <span class="opacity-60 text-[10px]">{{ $dayOfWeek }}</span>
        </div>
    </div>

    {{-- ═══ KPI Cards — اسکرول افقی ═══ --}}
    <div class="px-3 pb-3">
        <div class="text-[10px] font-bold opacity-50 mb-1.5 px-1">📊 خلاصه امروز</div>
        <div class="sg-kpi-scroll">
            <a href="{{ route('orders.index') }}" wire:navigate class="sg-kpi-card">
                <div class="sg-kpi-num">{{ \App\Support\PersianNumber::toFa($stats['orders_today'] ?? 0) }}</div>
                <div class="sg-kpi-lbl">امروز</div>
            </a>
            <a href="{{ route('orders.index', ['status' => 'pending']) }}" wire:navigate class="sg-kpi-card">
                <div class="sg-kpi-num text-warning">{{ \App\Support\PersianNumber::toFa($stats['orders_pending'] ?? 0) }}</div>
                <div class="sg-kpi-lbl">در انتظار</div>
            </a>
            <a href="{{ route('orders.index', ['status' => 'final-check']) }}" wire:navigate class="sg-kpi-card">
                <div class="sg-kpi-num text-info">{{ \App\Support\PersianNumber::toFa($stats['orders_check'] ?? 0) }}</div>
                <div class="sg-kpi-lbl">چک نهایی</div>
            </a>
            <a href="{{ route('orders.index', ['status' => 'courier']) }}" wire:navigate class="sg-kpi-card">
                <div class="sg-kpi-num text-success">{{ \App\Support\PersianNumber::toFa($stats['orders_courier'] ?? 0) }}</div>
                <div class="sg-kpi-lbl">مامور</div>
            </a>
            <a href="{{ route('customers.index') }}" wire:navigate class="sg-kpi-card">
                <div class="sg-kpi-num">{{ \App\Support\PersianNumber::toFa($stats['customers'] ?? 0) }}</div>
                <div class="sg-kpi-lbl">مشتری</div>
            </a>
            <a href="{{ route('certificates.index') }}" wire:navigate class="sg-kpi-card">
                <div class="sg-kpi-num">{{ \App\Support\PersianNumber::toFa($stats['certificates'] ?? 0) }}</div>
                <div class="sg-kpi-lbl">شناسنامه</div>
            </a>
        </div>
    </div>

    {{-- ═══ منوی اصلی ═══ --}}
    <nav class="flex-1 overflow-y-auto px-3 pb-3">
        <div class="text-[10px] font-bold opacity-50 mb-1.5 px-1">📁 منو</div>
        <ul class="space-y-0.5">
            @php
                $menu = [
                    ['route' => 'dashboard',          'icon' => '🏠', 'label' => 'داشبورد'],
                    ['route' => 'orders.index',       'icon' => '📦', 'label' => 'سفارشات',   'badge' => $stats['orders_pending'] ?? 0],
                    ['route' => 'customers.index',    'icon' => '👥', 'label' => 'مشتریان'],
                    ['route' => 'certificates.index', 'icon' => '💎', 'label' => 'شناسنامه‌ها'],
                    ['route' => 'reports.index',      'icon' => '📊', 'label' => 'گزارش‌ها'],
                    ['route' => 'activity-log',       'icon' => '📜', 'label' => 'لاگ'],
                    ['route' => 'settings.index',     'icon' => '⚙️', 'label' => 'تنظیمات'],
                ];
            @endphp

            @foreach($menu as $m)
                @php
                    $isActive = request()->routeIs($m['route']) || request()->routeIs(explode('.', $m['route'])[0] . '.*');
                @endphp
                <li>
                    <a href="{{ route($m['route']) }}" wire:navigate
                       class="flex items-center gap-2.5 px-3 py-2 rounded-xl text-sm transition-all
                              {{ $isActive
                                  ? 'bg-primary/15 text-primary font-bold shadow-sm'
                                  : 'opacity-75 hover:opacity-100 hover:bg-black/5 dark:hover:bg-white/5' }}">
                        <span class="text-base">{{ $m['icon'] }}</span>
                        <span class="flex-1">{{ $m['label'] }}</span>
                        @if(!empty($m['badge']) && $m['badge'] > 0)
                            <span class="badge badge-warning badge-xs">{{ \App\Support\PersianNumber::toFa($m['badge']) }}</span>
                        @endif
                    </a>
                </li>
            @endforeach
        </ul>
    </nav>

    {{-- ═══ اعلان‌ها ═══ --}}
    @if($notifCount > 0)
        <div class="px-3 pb-3">
            <div class="rounded-xl p-2.5"
                 style="background: linear-gradient(135deg, rgba(251,146,60,0.12), rgba(248,113,113,0.08)); border: 1px solid rgba(251,146,60,0.25);">
                <div class="flex items-center gap-2 text-xs font-bold text-warning mb-1">
                    🔔 {{ \App\Support\PersianNumber::toFa($notifCount) }} اعلان
                </div>
                @if(($stats['orders_pending'] ?? 0) > 0)
                    <div class="text-[10px] opacity-70">• {{ \App\Support\PersianNumber::toFa($stats['orders_pending']) }} سفارش در انتظار</div>
                @endif
                @if(($stats['api_errors'] ?? 0) > 0)
                    <div class="text-[10px] opacity-70">• {{ \App\Support\PersianNumber::toFa($stats['api_errors']) }} خطای API امروز</div>
                @endif
            </div>
        </div>
    @endif

    {{-- ═══ فوتر ═══ --}}
    <div class="px-3 py-2 border-t border-black/5 dark:border-white/5 text-[9.5px] text-center opacity-50">
        گروه هنری اقاقیا · ۱۴۰۵
    </div>
</div>
'''

# ═══════════════════════════════════════════════════════════════
# ۳) LAYOUT جدید — Sidebar + Header + Theme
# ═══════════════════════════════════════════════════════════════

LAYOUT_BLADE = r'''<!DOCTYPE html>
<html lang="fa" dir="rtl" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, viewport-fit=cover">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <meta name="theme-color" content="#0d9488">
    <title>{{ \App\Models\AppSetting::get('shop_name', 'شاپگان') }} — ShopGun</title>

    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">

    <script>
        (function() {
            const t = localStorage.getItem('theme') || '{{ \App\Models\AppSetting::get("theme", "light") }}';
            document.documentElement.setAttribute('data-theme', t);
        })();
    </script>

    @vite(['resources/css/app.css', 'resources/js/app.js'])
    @livewireStyles

    {{-- ═══ Styling سراسری ═══ --}}
    <link rel="stylesheet" href="{{ asset('css/shopgun.css') }}?v=3">

    {{-- ═══ cert-card assets ═══ --}}
    <link rel="stylesheet" href="{{ asset('css/cert-card.css') }}?v=2">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
    <script src="{{ asset('js/cert-card.js') }}?v=2"></script>
    <script src="{{ asset('js/cert-designer.js') }}?v=3" defer></script>

    {{-- ═══ Theme از Settings ═══ --}}
    @php
        try {
            $__color = \App\Models\AppSetting::get('primary_color', '#0d9488');
            $__density = \App\Models\AppSetting::get('density', 'normal');
        } catch (\Throwable $e) {
            $__color = '#0d9488';
            $__density = 'normal';
        }
    @endphp
    <style>
        :root { --sg-primary: {{ $__color }}; }
        [data-theme="dark"] { --sg-primary: {{ $__color }}; }
        .btn-primary { background-color: var(--sg-primary) !important; border-color: var(--sg-primary) !important; color: #fff !important; }
        .text-primary { color: var(--sg-primary) !important; }
        .border-primary { border-color: var(--sg-primary) !important; }
        .bg-primary\/15 { background-color: color-mix(in srgb, var(--sg-primary) 15%, transparent) !important; }
        .bg-primary\/10 { background-color: color-mix(in srgb, var(--sg-primary) 10%, transparent) !important; }
        .bg-primary { background-color: var(--sg-primary) !important; }
        @if($__density === 'compact')
            .sg-card, .card-body { padding: 0.6rem !important; }
            table td, table th { padding: 0.35rem 0.5rem !important; font-size: 11.5px !important; }
        @elseif($__density === 'comfortable')
            .sg-card, .card-body { padding: 1.5rem !important; }
            table td, table th { padding: 0.9rem 1rem !important; }
        @endif
    </style>

    @stack('styles')
</head>
<body class="min-h-screen font-sans text-base-content" style="background: linear-gradient(135deg, #f5f7fa 0%, #e8eef3 100%);">

    @auth
        {{-- ═══ Global Components — فقط یکبار ═══ --}}
        <livewire:global-search />
        <livewire:components.shipment-timeline />
        <livewire:orders.form-modal :key="'global-form-modal'" />
        <livewire:orders.view-modal :key="'global-view-modal'" />
        <livewire:customers.profile-modal :key="'global-profile-modal'" />
        <livewire:certificates.view-modal :key="'global-cert-modal'" />
    @endauth

    <div class="flex min-h-screen">

        {{-- ═══ Sidebar (دسکتاپ) ═══ --}}
        <aside class="hidden lg:flex flex-col w-72 shrink-0 p-3 sticky top-0 h-screen">
            <div class="sg-card flex-1 flex flex-col overflow-hidden">
                <livewire:components.sidebar />
            </div>
        </aside>

        {{-- ═══ محتوای اصلی ═══ --}}
        <div class="flex-1 min-w-0 flex flex-col">

            {{-- ═══ Header ═══ --}}
            <header class="sticky top-0 z-30 p-3 md:p-4">
                <div class="sg-card px-3 md:px-4 py-2.5 flex items-center justify-between gap-3">
                    {{-- جستجو --}}
                    <div class="flex items-center gap-2 flex-1 min-w-0">
                        <div class="lg:hidden flex items-center gap-2">
                            <div class="w-8 h-8 rounded-lg flex items-center justify-center text-white text-sm font-extrabold shadow"
                                 style="background: linear-gradient(135deg, #14b8a6, #0891b2);">💎</div>
                        </div>

                        <button onclick="window.dispatchEvent(new KeyboardEvent('keydown', {key: 'k', ctrlKey: true}))"
                                class="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs opacity-60 hover:opacity-100 transition"
                                style="background: rgba(0,0,0,0.05);">
                            <span>🔍 جستجو</span>
                            <kbd class="px-1.5 py-0.5 rounded text-[10px] font-mono"
                                 style="background: rgba(0,0,0,0.08);">Ctrl+K</kbd>
                        </button>
                    </div>

                    {{-- اکشن‌ها --}}
                    <div class="flex items-center gap-1.5">
                        <button onclick="toggleTheme()" class="btn btn-ghost btn-sm btn-circle" title="تم">
                            <span id="themeIcon">🌙</span>
                        </button>

                        @auth
                            <livewire:notification-center />
                        @endauth

                        <div class="dropdown dropdown-end">
                            <div tabindex="0" role="button" class="btn btn-ghost btn-sm gap-2 px-2">
                                <div class="w-7 h-7 rounded-full flex items-center justify-center text-white text-xs font-bold"
                                     style="background: linear-gradient(135deg, #14b8a6, #0891b2);">
                                    {{ mb_substr(Auth::user()->name ?? '؟', 0, 1) }}
                                </div>
                                <span class="hidden sm:inline text-xs">{{ Auth::user()->name ?? 'کاربر' }}</span>
                            </div>
                            <ul tabindex="0" class="dropdown-content menu z-[1] w-52 p-2 mt-2">
                                <li><a href="{{ route('settings.index') }}" wire:navigate>⚙️ تنظیمات</a></li>
                                <li><a href="{{ route('activity-log') }}" wire:navigate>📜 لاگ</a></li>
                                <li>
                                    <form method="POST" action="{{ route('logout') }}">
                                        @csrf
                                        <button type="submit" class="w-full text-right">🚪 خروج</button>
                                    </form>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            </header>

            {{-- ═══ Main ═══ --}}
            <main class="flex-1 pb-24 lg:pb-6">
                {{ $slot }}
            </main>

            {{-- ═══ Bottom Bar (موبایل) ═══ --}}
            <nav class="lg:hidden sg-bottom-bar">
                <div class="flex gap-1">
                    @php
                        $bottomItems = [
                            ['route' => 'dashboard',          'icon' => '🏠', 'label' => 'خانه'],
                            ['route' => 'orders.index',       'icon' => '📦', 'label' => 'سفارش'],
                            ['route' => 'customers.index',    'icon' => '👥', 'label' => 'مشتری'],
                            ['route' => 'certificates.index', 'icon' => '💎', 'label' => 'کارت'],
                            ['route' => 'settings.index',     'icon' => '⚙️', 'label' => 'تنظیم'],
                        ];
                    @endphp

                    @foreach($bottomItems as $m)
                        @php $isActive = request()->routeIs($m['route']) || request()->routeIs(explode('.', $m['route'])[0] . '.*'); @endphp
                        <a href="{{ route($m['route']) }}" wire:navigate
                           class="flex-1 flex flex-col items-center justify-center gap-0.5 py-1.5 px-1 rounded-xl transition-all
                                  {{ $isActive ? 'bg-primary/15 text-primary' : 'opacity-60' }}">
                            <span class="text-lg leading-none">{{ $m['icon'] }}</span>
                            <span class="text-[9px] font-bold leading-none mt-0.5">{{ $m['label'] }}</span>
                        </a>
                    @endforeach
                </div>
            </nav>
        </div>
    </div>

    <script>
        function toggleTheme() {
            const html = document.documentElement;
            const cur = html.getAttribute('data-theme') || 'light';
            const next = cur === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', next);
            localStorage.setItem('theme', next);
            document.getElementById('themeIcon').textContent = next === 'dark' ? '☀️' : '🌙';
        }
        document.addEventListener('DOMContentLoaded', () => {
            const cur = document.documentElement.getAttribute('data-theme');
            const icon = document.getElementById('themeIcon');
            if (icon) icon.textContent = cur === 'dark' ? '☀️' : '🌙';
        });
    </script>

    @livewireScripts
    @stack('scripts')
</body>
</html>
'''

# ═══════════════════════════════════════════════════════════════
# ۴) Order FormModal — PHP نسخه اصلاح‌شده
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

    /* ─── مشتری ─── */
    public ?int $customerId = null;
    public string $customerName = '';
    public string $customerPhone = '';
    public string $customerAddress = '';
    public string $customerPostal = '';

    /* ─── سبد ─── */
    public array $cart = [];

    /* ─── ادیتور محصول درون فرم ─── */
    public string $draftSku = '';
    public string $draftTitle = '';
    public string $draftPrice = '0';
    public int    $draftQty = 1;
    public bool   $draftCert = false;
    public array  $draftSuggestions = [];

    /* ─── سایر ─── */
    public string $insurance = '0';
    public string $discount  = '0';
    public string $shipping  = '0';
    public string $status    = 'pending';
    public ?int   $channelId = null;
    public string $notes     = '';
    public bool   $invoiceNeeded = false;

    public array $statusOptions = [
        ['id' => 'pending',     'name' => 'ثبت سفارش',    'icon' => '📝'],
        ['id' => 'final-check', 'name' => 'چک نهایی',     'icon' => '🔍'],
        ['id' => 'courier',     'name' => 'تحویل مامور',  'icon' => '🚚'],
    ];

    #[On('open-order-form')]
    public function open(?int $orderId = null): void
    {
        // ★★★ جلوگیری از باز شدن دوباره ★★★
        if ($this->show && !$orderId && !$this->orderId) {
            return;
        }

        $this->resetForm();
        $this->orderId = $orderId;
        $this->mode = $orderId ? 'edit' : 'create';

        if ($orderId) {
            $this->loadOrder($orderId);
        }

        $this->show = true;

        // ارسال به پیکرها (بعد از رندر)
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

        $this->cart = [];
        foreach ($o->items as $item) {
            $this->cart[] = [
                'product_id' => $item->product_id,
                'sku'        => $item->sku ?? '',
                'title'      => $item->name ?? '',
                'price'      => (float) $item->price,
                'qty'        => (int) $item->quantity,
                'certNeeded' => (bool) $item->certificate_needed,
            ];
        }
    }

    /* ═══════════════════════════════════════════════════════════
       رویدادها از Pickers
       ═══════════════════════════════════════════════════════════ */
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
    }

    /* ═══════════════════════════════════════════════════════════
       جستجوی SKU در ادیتور
       ═══════════════════════════════════════════════════════════ */
    public function updatedDraftSku(): void
    {
        $q = trim($this->draftSku);
        if (mb_strlen($q) < 2) {
            $this->draftSuggestions = [];
            return;
        }

        // جستجوی محلی
        $this->draftSuggestions = Product::active()
            ->search($q)
            ->orderByRaw('CASE WHEN sku = ? THEN 0 WHEN sku LIKE ? THEN 1 ELSE 2 END', [$q, $q . '%'])
            ->limit(10)
            ->get()
            ->map(fn($p) => [
                'id'    => $p->id,
                'sku'   => $p->sku,
                'name'  => $p->name,
                'price' => (float) $p->price,
                'price_fmt' => $p->price_formatted,
                'image' => $p->image_src,
                'stock' => $p->stock_quantity,
            ])
            ->toArray();

        // تلاش برای تطبیق کامل
        $exact = Product::where('sku', $q)->first();
        if ($exact) {
            $this->fillDraftFromProduct($exact);
        }
    }

    public function pickDraftProduct(int $productId): void
    {
        $p = Product::find($productId);
        if (!$p) return;
        $this->fillDraftFromProduct($p);
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

        // بررسی تکراری
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
                'sku'        => trim($this->draftSku),
                'title'      => $title,
                'price'      => $price,
                'qty'        => max(1, $this->draftQty),
                'certNeeded' => $this->draftCert,
            ];
        }

        $this->dispatch('product-picker-set', cart: $this->cart);

        // ریست ادیتور
        $this->reset(['draftSku', 'draftTitle', 'draftPrice', 'draftQty', 'draftCert', 'draftSuggestions']);
        $this->draftPrice = '0';
        $this->draftQty = 1;
    }

    public function removeCartItem(int $idx): void
    {
        unset($this->cart[$idx]);
        $this->cart = array_values($this->cart);
        $this->dispatch('product-picker-set', cart: $this->cart);
    }

    public function updateCartQty(int $idx, $qty): void
    {
        if (!isset($this->cart[$idx])) return;
        $this->cart[$idx]['qty'] = max(1, (int) $qty);
        $this->dispatch('product-picker-set', cart: $this->cart);
    }

    public function updateCartPrice(int $idx, $price): void
    {
        if (!isset($this->cart[$idx])) return;
        $this->cart[$idx]['price'] = (float) preg_replace('/[^\d.]/', '', (string) $price);
        $this->dispatch('product-picker-set', cart: $this->cart);
    }

    /* ═══════════════════════════════════════════════════════════
       محاسبه
       ═══════════════════════════════════════════════════════════ */
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

    /* ═══════════════════════════════════════════════════════════
       ذخیره
       ═══════════════════════════════════════════════════════════ */
    public function save()
    {
        $this->validate([
            'customerPhone'  => 'required|string|max:20',
            'customerName'   => 'required|string|max:120',
            'status'         => 'required|in:pending,final-check,courier',
            'cart'           => 'required|array|min:1',
        ], [], [
            'customerPhone' => 'تلفن',
            'customerName'  => 'نام مشتری',
            'status'        => 'وضعیت',
            'cart'          => 'سبد محصولات',
        ]);

        // مشتری
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
                'name'               => $it['title'] ?? '—',
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
# ۵) Order FormModal Blade — چیدمان جدید
# ═══════════════════════════════════════════════════════════════

ORDER_FORM_BLADE = r'''<div>
    @if($show)
    <div class="sg-modal-overlay" wire:key="order-form-modal-{{ $orderId ?? 'new' }}"
         @keydown.escape.window="$wire.close()">

        <div class="sg-modal" style="max-width: 780px;">
            {{-- ═══ Header ═══ --}}
            <div class="flex items-center justify-between p-4 border-b border-black/5 dark:border-white/5"
                 style="background: linear-gradient(90deg, rgba(13,148,136,0.08), transparent);">
                <div class="flex items-center gap-3">
                    <div class="w-9 h-9 rounded-xl flex items-center justify-center text-white shadow"
                         style="background: linear-gradient(135deg, #14b8a6, #0891b2);">
                        {{ $mode === 'edit' ? '✏️' : '📦' }}
                    </div>
                    <div>
                        <h2 class="font-bold text-base">
                            {{ $mode === 'edit' ? 'ویرایش سفارش #'.$orderId : 'سفارش جدید' }}
                        </h2>
                    </div>
                </div>
                <button wire:click="close" class="btn btn-ghost btn-sm btn-circle">✕</button>
            </div>

            {{-- ═══ Body ═══ --}}
            <div class="p-4 space-y-5 max-h-[calc(100vh-14rem)] overflow-y-auto">

                {{-- ═══════════════════════════════════════════ --}}
                {{-- ۱) مشتری                                     --}}
                {{-- ═══════════════════════════════════════════ --}}
                <section>
                    <div class="flex items-center gap-2 mb-3">
                        <span class="w-6 h-6 rounded-full bg-primary text-white text-xs font-bold flex items-center justify-center">۱</span>
                        <h3 class="font-bold text-sm">👤 مشتری</h3>
                    </div>
                    <livewire:components.customer-picker
                        :customer-id="$customerId"
                        event-prefix="customer"
                        :key="'modal-cp-'.($orderId ?? 'new')" />
                </section>

                {{-- ═══════════════════════════════════════════ --}}
                {{-- ۲) افزودن محصول (SKU Search + فیلدهای دستی) --}}
                {{-- ═══════════════════════════════════════════ --}}
                <section>
                    <div class="flex items-center gap-2 mb-3">
                        <span class="w-6 h-6 rounded-full bg-primary text-white text-xs font-bold flex items-center justify-center">۲</span>
                        <h3 class="font-bold text-sm">🛍️ افزودن محصول</h3>
                    </div>

                    <div class="rounded-xl p-3 space-y-3"
                         style="background: rgba(13,148,136,0.04); border: 1.5px dashed rgba(13,148,136,0.25);">

                        {{-- ─── SKU Search ─── --}}
                        <div class="relative">
                            <label class="text-[10.5px] font-bold opacity-70 mb-1 block">
                                🔍 جستجوی SKU (اختیاری — اگر کد محصول داری)
                            </label>
                            <div class="relative">
                                <input type="text" wire:model.live.debounce.250ms="draftSku"
                                       placeholder="کد محصول (SKU) را وارد کن..."
                                       class="input input-bordered input-sm w-full font-mono pr-9"
                                       dir="ltr" autocomplete="off">
                                <span class="absolute left-2 top-1/2 -translate-y-1/2 opacity-40">🔍</span>
                            </div>

                            {{-- پیشنهادات --}}
                            @if(count($draftSuggestions) > 0)
                                <div class="absolute z-50 top-full left-0 right-0 mt-1 bg-base-100 rounded-xl shadow-2xl border border-base-300 max-h-72 overflow-y-auto">
                                    @foreach($draftSuggestions as $s)
                                        <button type="button" wire:click="pickDraftProduct({{ $s['id'] }})"
                                                wire:key="ds-{{ $s['id'] }}"
                                                class="w-full text-right p-2 hover:bg-base-200 border-b border-base-200 last:border-0 flex items-center gap-2">
                                            @if($s['image'])
                                                <img src="{{ $s['image'] }}" class="w-9 h-9 rounded object-cover shrink-0" alt="">
                                            @else
                                                <div class="w-9 h-9 rounded bg-base-200 flex items-center justify-center shrink-0">💎</div>
                                            @endif
                                            <div class="flex-1 min-w-0">
                                                <div class="text-xs font-bold truncate">{{ $s['name'] }}</div>
                                                <div class="text-[10px] font-mono opacity-60" dir="ltr">{{ $s['sku'] }}</div>
                                            </div>
                                            <div class="text-xs font-bold text-primary shrink-0">{{ $s['price_fmt'] }}</div>
                                        </button>
                                    @endforeach
                                </div>
                            @endif
                        </div>

                        {{-- ─── فیلدهای محصول ─── --}}
                        <div class="grid grid-cols-1 md:grid-cols-12 gap-2">
                            <div class="md:col-span-5">
                                <label class="text-[10.5px] font-bold opacity-70 mb-1 block">📝 عنوان محصول *</label>
                                <input type="text" wire:model="draftTitle"
                                       placeholder="مثال: انگشتر فیروزه"
                                       class="input input-bordered input-sm w-full">
                                @error('draftTitle') <span class="text-error text-[10px]">{{ $message }}</span> @enderror
                            </div>
                            <div class="md:col-span-3">
                                <label class="text-[10.5px] font-bold opacity-70 mb-1 block">💰 قیمت (تومان)</label>
                                <input type="text" wire:model="draftPrice"
                                       class="input input-bordered input-sm w-full font-mono text-left"
                                       dir="ltr" placeholder="0">
                            </div>
                            <div class="md:col-span-2">
                                <label class="text-[10.5px] font-bold opacity-70 mb-1 block">📦 تعداد</label>
                                <input type="number" wire:model="draftQty" min="1"
                                       class="input input-bordered input-sm w-full text-center" dir="ltr">
                            </div>
                            <div class="md:col-span-2 flex items-end">
                                <label class="flex items-center gap-1.5 cursor-pointer text-[10.5px] font-bold w-full p-2 rounded-lg bg-white/50"
                                       title="نیاز به شناسنامه دارد؟">
                                    <input type="checkbox" wire:model="draftCert"
                                           class="checkbox checkbox-sm checkbox-primary">
                                    <span>💎 شناسنامه</span>
                                </label>
                            </div>
                        </div>

                        {{-- ─── دکمه افزودن ─── --}}
                        <button type="button" wire:click="addDraftToCart"
                                class="btn btn-primary btn-sm w-full">
                            ➕ افزودن به سبد سفارش
                        </button>
                    </div>

                    {{-- ─── سبد فعلی ─── --}}
                    @if(count($cart) > 0)
                        <div class="mt-3 border border-base-300 rounded-xl overflow-hidden">
                            <div class="px-3 py-2 bg-black/5 dark:bg-white/5 flex items-center justify-between">
                                <span class="text-xs font-bold">🛒 سبد ({{ \App\Support\PersianNumber::toFa(count($cart)) }})</span>
                            </div>
                            <div class="divide-y divide-base-200">
                                @foreach($cart as $i => $item)
                                    <div class="p-2.5 flex items-center gap-3" wire:key="ci-{{ $i }}-{{ $item['sku'] ?? '' }}">
                                        <div class="flex-1 min-w-0">
                                            <div class="text-xs font-bold truncate">{{ $item['title'] ?? '—' }}</div>
                                            @if(!empty($item['sku']))
                                                <div class="text-[10px] font-mono opacity-50" dir="ltr">{{ $item['sku'] }}</div>
                                            @endif
                                        </div>
                                        <input type="number" min="1" value="{{ $item['qty'] ?? 1 }}"
                                               wire:change="updateCartQty({{ $i }}, $event.target.value)"
                                               class="input input-bordered input-xs w-16 text-center" dir="ltr">
                                        <input type="text" value="{{ number_format((float) ($item['price'] ?? 0)) }}"
                                               wire:change="updateCartPrice({{ $i }}, $event.target.value)"
                                               class="input input-bordered input-xs w-24 text-left font-mono" dir="ltr">
                                        <div class="text-xs font-bold text-primary w-20 text-left">
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

                {{-- ═══════════════════════════════════════════ --}}
                {{-- ۳) مالی + وضعیت                             --}}
                {{-- ═══════════════════════════════════════════ --}}
                <section>
                    <div class="flex items-center gap-2 mb-3">
                        <span class="w-6 h-6 rounded-full bg-primary text-white text-xs font-bold flex items-center justify-center">۳</span>
                        <h3 class="font-bold text-sm">💰 مالی و وضعیت</h3>
                    </div>

                    <div class="grid grid-cols-2 md:grid-cols-4 gap-2">
                        <div>
                            <label class="text-[10.5px] font-bold opacity-70 mb-1 block">💰 بیمه</label>
                            <input type="text" wire:model.live.debounce.400ms="insurance" dir="ltr"
                                   class="input input-bordered input-sm w-full font-mono text-center">
                        </div>
                        <div>
                            <label class="text-[10.5px] font-bold opacity-70 mb-1 block">📦 ارسال</label>
                            <input type="text" wire:model.live.debounce.400ms="shipping" dir="ltr"
                                   class="input input-bordered input-sm w-full font-mono text-center">
                        </div>
                        <div>
                            <label class="text-[10.5px] font-bold opacity-70 mb-1 block">🏷️ تخفیف</label>
                            <input type="text" wire:model.live.debounce.400ms="discount" dir="ltr"
                                   class="input input-bordered input-sm w-full font-mono text-center">
                        </div>
                        <div>
                            <label class="text-[10.5px] font-bold opacity-70 mb-1 block">🚦 وضعیت</label>
                            <select wire:model="status" class="select select-bordered select-sm w-full">
                                @foreach($statusOptions as $s)
                                    <option value="{{ $s['id'] }}">{{ $s['icon'] }} {{ $s['name'] }}</option>
                                @endforeach
                            </select>
                        </div>
                    </div>

                    <div class="grid grid-cols-1 md:grid-cols-2 gap-2 mt-2">
                        <div>
                            <label class="text-[10.5px] font-bold opacity-70 mb-1 block">🌐 کانال</label>
                            <select wire:model="channelId" class="select select-bordered select-sm w-full">
                                <option value="">— انتخاب —</option>
                                @foreach($channels as $ch)
                                    <option value="{{ $ch->id }}">{{ $ch->name }}</option>
                                @endforeach
                            </select>
                        </div>
                        <div class="flex items-end">
                            <label class="flex items-center gap-2 cursor-pointer p-2 rounded-lg bg-black/5 dark:bg-white/5 w-full">
                                <input type="checkbox" wire:model="invoiceNeeded"
                                       class="checkbox checkbox-sm checkbox-primary">
                                <span class="text-xs font-bold">📄 فاکتور</span>
                            </label>
                        </div>
                    </div>

                    <div class="mt-2">
                        <label class="text-[10.5px] font-bold opacity-70 mb-1 block">📝 یادداشت</label>
                        <textarea wire:model="notes" rows="2"
                                  class="textarea textarea-bordered textarea-sm w-full"
                                  placeholder="یادداشت داخلی..."></textarea>
                    </div>
                </section>

                {{-- ═══ جمع ═══ --}}
                <div class="rounded-xl p-3"
                     style="background: linear-gradient(135deg, rgba(13,148,136,0.08), rgba(8,145,178,0.04)); border: 1.5px solid rgba(13,148,136,0.2);">
                    <div class="space-y-1 text-sm">
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
                        <div class="flex justify-between border-t border-primary/20 pt-2 mt-2">
                            <span class="font-bold">💵 مبلغ نهایی:</span>
                            <span class="font-bold text-primary text-lg font-mono">{{ number_format($this->total) }} تومان</span>
                        </div>
                    </div>
                </div>
            </div>

            {{-- ═══ Footer ═══ --}}
            <div class="p-3 flex items-center justify-between gap-2 border-t border-black/5 dark:border-white/5 bg-black/5 dark:bg-white/5">
                <button wire:click="close" class="btn btn-ghost btn-sm">انصراف</button>
                <button wire:click="save" wire:loading.attr="disabled" class="btn btn-success btn-sm md:btn-md">
                    <span wire:loading.remove wire:target="save">✅ {{ $mode === 'edit' ? 'ویرایش' : 'ثبت سفارش' }}</span>
                    <span wire:loading wire:target="save">⏳...</span>
                </button>
            </div>
        </div>
    </div>
    @endif
</div>
'''

# ═══════════════════════════════════════════════════════════════
# اجرا
# ═══════════════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  ShopGun V2 — Fix All                                         ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    # Backup
    print("📦 Backup...")
    for rel in [
        "app/Livewire/Orders/FormModal.php",
        "resources/views/livewire/orders/form-modal.blade.php",
        "resources/views/components/layouts/app.blade.php",
    ]:
        backup(rel)

    # ۱) Global CSS
    print("\n📄 [۱] Global CSS...")
    write("public/css/shopgun.css", GLOBAL_CSS)

    # ۲) Sidebar
    print("\n📄 [۲] Sidebar Component...")
    write("app/Livewire/Components/Sidebar.php", SIDEBAR_PHP)
    write("resources/views/livewire/components/sidebar.blade.php", SIDEBAR_BLADE)

    # ۳) Layout جدید
    print("\n📄 [۳] Layout...")
    write("resources/views/components/layouts/app.blade.php", LAYOUT_BLADE)

    # ۴) Order Form PHP
    print("\n📄 [۴] Order Form PHP...")
    write("app/Livewire/Orders/FormModal.php", ORDER_FORM_PHP)

    # ۵) Order Form Blade
    print("\n📄 [۵] Order Form Blade...")
    write("resources/views/livewire/orders/form-modal.blade.php", ORDER_FORM_BLADE)

    # ─── حذف FormModal تکراری از سایر bladeها ───
    print("\n🔧 [۶] حذف مودال‌های تکراری از صفحات...")
    blades_dir = PROJECT / "resources/views/livewire"
    if blades_dir.exists():
        for blade in blades_dir.rglob("*.blade.php"):
            rel = blade.relative_to(PROJECT)
            # فایل layout رو skip کن
            if 'layouts' in str(rel): continue

            with open(blade, 'r', encoding='utf-8') as f:
                content = f.read()

            original = content

            # حذف تگ‌های مودال از صفحه‌های داخلی
            for pattern in [
                r'<livewire:orders\.form-modal[^/]*?/>',
                r'<livewire:orders\.view-modal[^/]*?/>',
                r'<livewire:customers\.profile-modal[^/]*?/>',
                r'<livewire:certificates\.view-modal[^/]*?/>',
            ]:
                content = re.sub(pattern, '', content)

            if content != original:
                with open(blade, 'w', encoding='utf-8', newline='\n') as f:
                    f.write(content)
                print(f"  ✓ {rel}")

    # ─── بررسی Orders/Index برای FormModal اضافی ───
    orders_index = PROJECT / "app/Livewire/Orders/Index.php"
    if orders_index.exists():
        with open(orders_index, 'r', encoding='utf-8') as f:
            c = f.read()
        # اگر listeners شامل open-order-form بود و داخل خودش open هم داره، مشکلی نیست
        # چون مودال توی layout هست. اما اگه این کامپوننت خودش open می‌کنه، درسته.

    # ─── بررسی Orders/Index blade برای دکمه سفارش جدید ───
    orders_index_blade = PROJECT / "resources/views/livewire/orders/index.blade.php"
    if orders_index_blade.exists():
        with open(orders_index_blade, 'r', encoding='utf-8') as f:
            content = f.read()

        # مطمئن شو دکمه با Livewire.dispatch صدا زده می‌شه
        if 'open-order-form' in content and 'Livewire.dispatch' not in content:
            print("  ⚠️ Orders/Index با dispatch صدا نمی‌زنه — بررسی کن")

    print("\n" + "═" * 64)
    print("✅ تمام!")
    print("═" * 64)
    print(f"""
📋 اجرا کن:

  cd {PROJECT}
  php artisan optimize:clear
  php artisan view:clear
  php artisan route:clear
  php artisan migrate

  ⚠️ سرور رو ببند (Ctrl+C) و دوباره باز کن:
  php artisan serve

مرورگر: Ctrl+Shift+R

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 چه چیزی حل شد:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✅ Double Modal — فقط یک FormModal در layout، سایر حذف شدند
  ✅ فرم سفارش — SKU Search بالای فیلدهای عنوان/قیمت
  ✅ بخش افزودن محصول — Title + Price + Qty + Cert + Add
  ✅ سبد جدید — ویرایش Qty/Price داخل سبد
  ✅ Sidebar قدرتمند — تاریخ، KPI Cards افقی، اعلان
  ✅ استایل یکپارچه — Glass + Rounded + Transitions
  ✅ Modal یکپارچه — sg-modal + sg-modal-overlay
  ✅ جلوگیری از باز شدن دوباره modal

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 نکته مهم دربارهٔ سرچ:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  اگر سرچ هنوز کار نمی‌کنه، احتمالاً:
  
  ۱) جدول products خالیه → تنظیمات → کامرس → سینک محصولات
  ۲) مشتری‌ای در جدول customers نیست → باید اول چند مشتری داشته باشی
  
  برای تست، در tinker بزن:
  
    php artisan tinker
    >>> App\\Models\\Product::count();
    >>> App\\Models\\Customer::count();
    >>> App\\Models\\CustomerPhone::count();
  
  اگه صفر بود، اول سینک محصولات رو بزن.
""")

if __name__ == "__main__":
    main()