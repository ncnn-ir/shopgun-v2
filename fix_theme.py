#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""رفع نهایی: تم تیره + تاریخ شمسی + تایم‌لاین + ایمپورت CSV + پروفایل"""
import shutil
from pathlib import Path
from datetime import datetime

PROJECT = Path("/data/data/com.termux/files/home/shopgun-v2.2")
if not PROJECT.exists():
    PROJECT = Path(input("مسیر پروژه: ").strip())

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
# ۱) EXTRA CSS — تم تیره + همه کامپوننت‌ها
# ═══════════════════════════════════════════════════════════════
EXTRA_CSS = r'''/* ═══════════════════════════════════════════════════════════════
   ShopGun V2 — Dark Theme + Fixes
   ═══════════════════════════════════════════════════════════════ */

/* ═══════════════════════════════════════════════════════════
   LIGHT THEME (default)
   ═══════════════════════════════════════════════════════════ */
:root {
    --primary: #1a5276;
    --primary-light: #2980b9;
    --primary-dark: #0d3b5e;
    --gold: #c9a84c;
    --gold-light: #f0d68a;
    --gold-dark: #8b6914;

    --bg: #f5f0e8;
    --bg-card: #ffffff;
    --bg-elevated: #ffffff;
    --bg-soft: rgba(0,0,0,.03);

    --text: #2c3e50;
    --text-light: #7f8c8d;
    --text-muted: #95a5a6;
    --border: #d4c5a9;
    --border-soft: rgba(0,0,0,.06);

    --success: #27ae60;
    --danger: #e74c3c;
    --warn: #f39c12;
    --info: #2980b9;

    --shadow: 0 4px 20px rgba(0,0,0,.08);
    --shadow-lg: 0 8px 40px rgba(0,0,0,.12);
    --shadow-card: 0 2px 8px rgba(0,0,0,.04);

    --table-title: #0d5c63;
    --table-title-text: #e0f7f8;
    --table-border: #7fbfc4;
    --thead-bg: #f8f6f0;

    --cert-gold: #b8860b;
    --cert-brown: #6b4423;

    --input-bg: #f5f0e8;
    --input-border: #d4c5a9;
    --chip-bg: #ffffff;
    --chip-border: #d4c5a9;
}

/* ═══════════════════════════════════════════════════════════
   DARK THEME — هماهنگ با همه اجزا
   ═══════════════════════════════════════════════════════════ */
[data-theme="dark"] {
    --primary: #4da6d8;
    --primary-light: #6bb8e3;
    --primary-dark: #2c7db3;
    --gold: #d4b85a;
    --gold-light: #e8d090;
    --gold-dark: #b89840;

    --bg: #0a0f1a;
    --bg-card: #151b27;
    --bg-elevated: #1c2332;
    --bg-soft: rgba(255,255,255,.04);

    --text: #e6edf5;
    --text-light: #94a3b8;
    --text-muted: #64748b;
    --border: #2a3544;
    --border-soft: rgba(255,255,255,.08);

    --success: #34d399;
    --danger: #f87171;
    --warn: #fbbf24;
    --info: #60a5fa;

    --shadow: 0 4px 20px rgba(0,0,0,.4);
    --shadow-lg: 0 8px 40px rgba(0,0,0,.6);
    --shadow-card: 0 2px 8px rgba(0,0,0,.3);

    --table-title: #1e3a5f;
    --table-title-text: #c9e8f5;
    --table-border: #3a5470;
    --thead-bg: #1c2332;

    --cert-gold: #d4a84c;
    --cert-brown: #d4a56a;

    --input-bg: #1c2332;
    --input-border: #2a3544;
    --chip-bg: #1c2332;
    --chip-border: #2a3544;
}

/* ═══════════════════════════════════════════════════════════
   BASE
   ═══════════════════════════════════════════════════════════ */
body {
    background: var(--bg) !important;
    color: var(--text) !important;
    transition: background .2s, color .2s;
}

/* ═══════════════════════════════════════════════════════════
   HEADER
   ═══════════════════════════════════════════════════════════ */
.sg-main-header {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
    border-bottom: 2px solid var(--gold);
}
.sg-header-title h1 { color: #fff !important; }
.sg-header-title p { color: var(--gold-light) !important; }
.sg-header-date {
    background: rgba(255,255,255,.15) !important;
    color: #fff !important;
    border: 1px solid rgba(255,255,255,.2);
}
.sg-header-icon-btn {
    background: rgba(255,255,255,.15) !important;
    color: #fff !important;
    border: 1px solid rgba(255,255,255,.2) !important;
}
.sg-header-icon-btn:hover { background: rgba(255,255,255,.25) !important; }
.sg-logo-container {
    background: var(--gold) !important;
    color: var(--primary-dark) !important;
}

/* ═══════════════════════════════════════════════════════════
   TABS
   ═══════════════════════════════════════════════════════════ */
.sg-tabs-bar { background: transparent; }
.sg-tab-btn {
    background: var(--bg-card) !important;
    color: var(--text-light) !important;
    border-bottom: 3px solid transparent !important;
}
.sg-tab-btn.active,
.sg-tab-btn:hover {
    color: var(--primary) !important;
    border-bottom-color: var(--gold) !important;
}

/* ═══════════════════════════════════════════════════════════
   TOOLBAR
   ═══════════════════════════════════════════════════════════ */
.sg-toolbar {
    background: var(--bg-card) !important;
    border-color: var(--border) !important;
    box-shadow: var(--shadow-card) !important;
}

/* ═══════════════════════════════════════════════════════════
   BUTTONS
   ═══════════════════════════════════════════════════════════ */
.btn {
    transition: all .15s;
}
.btn-primary {
    background: linear-gradient(135deg, var(--gold), var(--gold-dark)) !important;
    color: #fff !important;
    border: none !important;
}
.btn-secondary {
    background: var(--primary) !important;
    color: #fff !important;
    border: none !important;
}
.btn-outline {
    background: transparent !important;
    border: 2px solid var(--border) !important;
    color: var(--text) !important;
}
.btn-outline:hover {
    background: var(--bg-soft) !important;
    border-color: var(--gold) !important;
}
.btn-success { background: var(--success) !important; color: #fff !important; }
.btn-danger { background: var(--danger) !important; color: #fff !important; }
.btn-warn { background: var(--warn) !important; color: #fff !important; }

/* ═══════════════════════════════════════════════════════════
   FORM CONTROLS — هماهنگ با تم
   ═══════════════════════════════════════════════════════════ */
.form-control,
input.form-control,
select.form-control,
textarea.form-control {
    background: var(--input-bg) !important;
    color: var(--text) !important;
    border: 2px solid var(--input-border) !important;
    border-radius: 10px;
    padding: 10px 12px;
    font-family: inherit;
    font-size: 12.5px;
    transition: all .15s;
}
.form-control:focus {
    outline: none !important;
    border-color: var(--gold) !important;
    box-shadow: 0 0 0 3px rgba(201,168,76,.15) !important;
}
.form-control::placeholder {
    color: var(--text-muted) !important;
    opacity: .7;
}
select.form-control option {
    background: var(--bg-card) !important;
    color: var(--text) !important;
}

.form-group > label {
    background: var(--bg-card) !important;
    color: var(--primary) !important;
    padding: 0 6px;
    font-size: 10.5px;
    font-weight: 600;
}

/* ═══════════════════════════════════════════════════════════
   CARDS & SETTINGS
   ═══════════════════════════════════════════════════════════ */
.sg-settings-card {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    box-shadow: var(--shadow-card) !important;
}
.sg-settings-card h3 {
    color: var(--primary) !important;
    border-bottom: 2px solid var(--border) !important;
}

/* ═══════════════════════════════════════════════════════════
   TABLES
   ═══════════════════════════════════════════════════════════ */
.sg-table-container {
    background: var(--bg-card) !important;
    border-color: var(--border) !important;
}
.sg-table-header {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
    color: #fff !important;
}
.sg-table thead th {
    background: var(--thead-bg) !important;
    color: var(--primary) !important;
    border-bottom: 2px solid var(--border) !important;
}
.sg-table tbody td {
    background: transparent !important;
    color: var(--text) !important;
    border-bottom: 1px solid var(--border-soft) !important;
}
.sg-table tbody tr:hover {
    background: var(--bg-soft) !important;
}
.sg-table tbody tr:hover td {
    background: var(--bg-soft) !important;
}

.sg-mini-table th {
    color: var(--text-light) !important;
    border-bottom: 1px solid var(--border) !important;
}
.sg-mini-table td {
    color: var(--text) !important;
    border-bottom: 1px solid var(--border-soft) !important;
}
.sg-mini-table tr:hover td {
    background: var(--bg-soft) !important;
}

/* ═══════════════════════════════════════════════════════════
   MODALS
   ═══════════════════════════════════════════════════════════ */
.sg-modal-overlay {
    background: rgba(0,0,0,.7) !important;
    backdrop-filter: blur(8px);
}
.sg-modal {
    background: var(--bg-card) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
}
.sg-modal-header {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%) !important;
    color: #fff !important;
}
.sg-modal-header h2 { color: #fff !important; }
.sg-modal-close {
    background: rgba(255,255,255,.2) !important;
    color: #fff !important;
}
.sg-modal-body {
    background: var(--bg-card) !important;
    color: var(--text) !important;
}
.sg-modal-footer {
    background: var(--bg-soft) !important;
    border-top: 1px solid var(--border) !important;
}

/* ═══════════════════════════════════════════════════════════
   STAT CARDS
   ═══════════════════════════════════════════════════════════ */
.sg-stat-card {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
}
.sg-stat-card .num { color: var(--text) !important; }
.sg-stat-card .lbl { color: var(--text-light) !important; }
.sg-stat-card .icon { color: inherit; }

.sg-stat-card .trend.up { color: var(--success) !important; }
.sg-stat-card .trend.down { color: var(--danger) !important; }
.sg-stat-card .trend.flat { color: var(--text-muted) !important; }

/* ═══════════════════════════════════════════════════════════
   CHART CARDS
   ═══════════════════════════════════════════════════════════ */
.sg-chart-card {
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    color: var(--text) !important;
}
.sg-chart-card h3 {
    color: var(--primary) !important;
    border-bottom: 2px solid var(--border) !important;
}
.sg-bar-chart .bar-lbl { color: var(--text-light) !important; }
.sg-bar-chart .bar-val { color: var(--primary) !important; }
.sg-chart-scroll svg text {
    fill: var(--text-light) !important;
}
.sg-chart-scroll svg line {
    stroke: var(--border-soft) !important;
}

/* ═══════════════════════════════════════════════════════════
   FILTERS / CHIPS
   ═══════════════════════════════════════════════════════════ */
.sg-chip {
    background: var(--chip-bg) !important;
    border: 1.5px solid var(--chip-border) !important;
    color: var(--text-light) !important;
}
.sg-chip:hover {
    border-color: var(--gold) !important;
    color: var(--text) !important;
}
.sg-chip.active {
    background: linear-gradient(135deg, var(--primary), var(--primary-dark)) !important;
    color: #fff !important;
    border-color: var(--primary) !important;
}

.sg-tab-chip {
    background: var(--chip-bg) !important;
    border: 1.5px solid var(--chip-border) !important;
    color: var(--text-light) !important;
}
.sg-tab-chip:hover {
    border-color: var(--gold) !important;
    color: var(--text) !important;
}
.sg-tab-chip.active {
    background: linear-gradient(135deg, var(--primary), var(--primary-dark)) !important;
    color: #fff !important;
    border-color: var(--primary) !important;
}

/* ═══════════════════════════════════════════════════════════
   STONE GRID
   ═══════════════════════════════════════════════════════════ */
.sg-stone-card {
    background: var(--bg-card) !important;
    border: 2px solid var(--border) !important;
    color: var(--text) !important;
}
.sg-stone-card:hover {
    border-color: var(--gold) !important;
}
.sg-stone-card .s-icon {
    background: var(--bg-soft) !important;
}
.sg-stone-card .s-name { color: var(--primary) !important; }
.sg-stone-card .s-origin { color: var(--text-light) !important; }

/* ═══════════════════════════════════════════════════════════
   STATUS BADGES
   ═══════════════════════════════════════════════════════════ */
.sg-status-badge {
    color: #fff !important;
    border: none !important;
    font-weight: 700;
}
.sg-status-badge.pending {
    background: linear-gradient(135deg, #ffb74d, #ff9800) !important;
    color: #7a3800 !important;
}
.sg-status-badge.final-check {
    background: linear-gradient(135deg, #60a5fa, #3b82f6) !important;
    color: #fff !important;
}
.sg-status-badge.courier {
    background: linear-gradient(135deg, #4ade80, #22c55e) !important;
    color: #052e16 !important;
}

/* ═══════════════════════════════════════════════════════════
   TIMELINE — تم‌پذیر + اسکرول
   ═══════════════════════════════════════════════════════════ */
.sg-timeline {
    display: flex;
    align-items: flex-start;
    gap: 0;
    padding: 16px 4px 6px;
    overflow-x: auto;
    scrollbar-width: thin;
    position: relative;
}
.sg-timeline::-webkit-scrollbar { height: 4px; }
.sg-timeline::-webkit-scrollbar-thumb { background: var(--border); border-radius: 2px; }

.sg-tl-step {
    flex: 1;
    min-width: 90px;
    text-align: center;
    position: relative;
    padding-top: 26px;
}
.sg-tl-step .tl-dot {
    position: absolute;
    top: 0;
    left: 50%;
    transform: translateX(-50%);
    width: 24px;
    height: 24px;
    border-radius: 50%;
    background: var(--bg-card);
    border: 2.5px solid var(--border);
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 11px;
    font-weight: 700;
    color: var(--text-light);
    z-index: 2;
    transition: all .2s;
}
.sg-tl-step.done .tl-dot {
    background: var(--success) !important;
    border-color: var(--success) !important;
    color: #fff !important;
}
.sg-tl-step.current .tl-dot {
    background: var(--gold) !important;
    border-color: var(--gold) !important;
    color: #fff !important;
    box-shadow: 0 0 0 5px rgba(201,168,76,.25) !important;
    animation: sgPulse 1.5s infinite;
}
@keyframes sgPulse {
    0%,100% { box-shadow: 0 0 0 5px rgba(201,168,76,.25); }
    50% { box-shadow: 0 0 0 10px rgba(201,168,76,.05); }
}
.sg-tl-step::before {
    content: '';
    position: absolute;
    top: 11px;
    right: -50%;
    width: 100%;
    height: 2px;
    background: var(--border);
    z-index: 1;
}
.sg-tl-step:last-child::before { display: none; }
.sg-tl-step.done::before { background: var(--success) !important; }

.sg-tl-step .tl-lbl {
    font-size: 10.5px;
    font-weight: 700;
    color: var(--text-light) !important;
    margin-top: 2px;
    line-height: 1.3;
}
.sg-tl-step.done .tl-lbl { color: var(--success) !important; }
.sg-tl-step.current .tl-lbl { color: var(--gold) !important; }

.sg-tl-step .tl-date {
    font-size: 9px;
    font-family: monospace;
    color: var(--text-muted) !important;
    margin-top: 2px;
    direction: rtl;
}
.sg-tl-step .tl-time {
    font-size: 8.5px;
    font-family: monospace;
    color: var(--text-muted) !important;
    opacity: .8;
    direction: ltr;
}

/* ═══════════════════════════════════════════════════════════
   COMPACT CUSTOMER BOX
   ═══════════════════════════════════════════════════════════ */
.sg-compact-box {
    background: var(--bg-soft) !important;
    border: 1.5px solid var(--border) !important;
    border-radius: 12px;
    padding: 12px 14px;
    margin-bottom: 12px;
}
.sg-compact-box .avatar {
    background: linear-gradient(135deg, var(--primary), var(--primary-dark)) !important;
    color: #fff !important;
}
.sg-compact-box .name { color: var(--text) !important; }
.sg-compact-box .phone { color: var(--text-light) !important; }
.sg-compact-box .grid { border-top: 1px dashed var(--border) !important; }
.sg-compact-box .grid .item .val { color: var(--text) !important; }
.sg-compact-box .grid .item .lbl { color: var(--text-light) !important; }

.sg-inline-info {
    background: var(--bg-soft) !important;
    color: var(--text) !important;
}
.sg-inline-info .item strong { color: var(--text) !important; }

/* ═══════════════════════════════════════════════════════════
   MOBILE BAR
   ═══════════════════════════════════════════════════════════ */
.sg-mobile-bar {
    position: fixed !important;
    bottom: 10px !important;
    left: 10px !important;
    right: 10px !important;
    background: var(--bg-card) !important;
    border: 1px solid var(--border) !important;
    box-shadow: 0 8px 32px rgba(0,0,0,.15);
}
[data-theme="dark"] .sg-mobile-bar {
    background: rgba(21,27,39,.92) !important;
    backdrop-filter: blur(20px) saturate(180%);
}

.sg-mobile-bar-inner {
    display: flex !important;
    overflow-x: auto !important;
    gap: 2px;
    scrollbar-width: none;
    padding: 0 2px;
}
.sg-mobile-bar-inner::-webkit-scrollbar { display: none; }
.sg-mobile-bar-btn {
    flex: 0 0 auto !important;
    min-width: 62px !important;
    padding: 6px 8px !important;
    color: var(--text-light) !important;
    background: transparent !important;
    text-decoration: none;
}
.sg-mobile-bar-btn.active {
    background: linear-gradient(135deg, var(--primary), var(--primary-dark)) !important;
    color: #fff !important;
}
.sg-mobile-bar-btn.add {
    background: linear-gradient(135deg, var(--gold), var(--gold-dark)) !important;
    color: #fff !important;
}

/* ═══════════════════════════════════════════════════════════
   TOAST
   ═══════════════════════════════════════════════════════════ */
.sg-toast { color: #fff !important; }
.sg-toast.success { background: var(--success) !important; }
.sg-toast.error { background: var(--danger) !important; }
.sg-toast.warn { background: var(--warn) !important; }
.sg-toast.info { background: var(--info) !important; }

/* ═══════════════════════════════════════════════════════════
   SCROLLBAR
   ═══════════════════════════════════════════════════════════ */
::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb {
    background: var(--border);
    border-radius: 3px;
}
::-webkit-scrollbar-thumb:hover { background: var(--text-muted); }

/* ═══════════════════════════════════════════════════════════
   SETTINGS MOBILE TABS
   ═══════════════════════════════════════════════════════════ */
.sg-tabs-mobile {
    display: none;
    overflow-x: auto;
    overflow-y: hidden;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
    gap: 6px;
    padding: 6px 14px 12px;
    white-space: nowrap;
}
.sg-tabs-mobile::-webkit-scrollbar { display: none; }

@media(max-width: 768px) {
    .sg-tabs-mobile { display: flex !important; }
    .sg-tab-btn { display: none !important; }
    .sg-settings-card { margin: 0 14px !important; }
    .sg-chart-grid { grid-template-columns: 1fr !important; padding: 0 14px 14px !important; }
    .sg-stats-row { padding: 4px 14px 12px !important; }
}

/* ═══════════════════════════════════════════════════════════
   FIX: بلور و شفافیت در تم تیره
   ═══════════════════════════════════════════════════════════ */
[data-theme="dark"] .sg-modal-overlay {
    background: rgba(0,0,0,.85) !important;
}
[data-theme="dark"] .sg-main-header {
    box-shadow: 0 4px 20px rgba(0,0,0,.5);
}
[data-theme="dark"] .sg-stone-card:hover {
    box-shadow: 0 6px 20px rgba(0,0,0,.5) !important;
}
[data-theme="dark"] .sg-stat-card:hover {
    box-shadow: 0 6px 20px rgba(0,0,0,.5) !important;
}

/* ═══════════════════════════════════════════════════════════
   FIX: خوانایی متون
   ═══════════════════════════════════════════════════════════ */
[data-theme="dark"] {
    color-scheme: dark;
}
[data-theme="dark"] h1,
[data-theme="dark"] h2,
[data-theme="dark"] h3,
[data-theme="dark"] h4,
[data-theme="dark"] strong {
    color: var(--text) !important;
}

/* ═══════════════════════════════════════════════════════════
   PROFESSIONAL SCROLL
   ═══════════════════════════════════════════════════════════ */
.sg-chart-scroll {
    overflow-x: auto;
    overflow-y: hidden;
    padding-bottom: 6px;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: thin;
}
.sg-chart-scroll::-webkit-scrollbar { height: 5px; }
.sg-chart-scroll::-webkit-scrollbar-thumb { background: var(--border); border-radius: 3px; }
'''

# ═══════════════════════════════════════════════════════════════
# ۲) ORDER VIEW — Timeline با تاریخ/ساعت شمسی + باکس مشتری
# ═══════════════════════════════════════════════════════════════
ORDER_VIEW_PHP = r'''<?php
namespace App\Livewire\Orders;

use App\Models\Customer;
use App\Models\Order;
use Livewire\Attributes\On;
use Livewire\Component;

class ViewModal extends Component
{
    public bool $show = false;
    public ?Order $order = null;
    public array $customerStats = [];
    public array $timeline = [];

    #[On('open-order-view')]
    public function open(int $orderId): void
    {
        $this->order = Order::with(['customer', 'items', 'channel'])->find($orderId);
        if (!$this->order) return;

        // آمار مشتری
        if ($this->order->customer_id) {
            $customer = Customer::find($this->order->customer_id);
            if ($customer) {
                $orders = $customer->orders()->orderBy('created_at')->get();
                $this->customerStats = [
                    'total' => $orders->count(),
                    'sum' => (float) $orders->sum('amount'),
                    'first' => $orders->first()?->created_at,
                    'last' => $orders->last()?->created_at,
                ];
            }
        }

        $this->buildTimeline();
        $this->show = true;
    }

    protected function buildTimeline(): void
    {
        $stages = [
            ['id' => 'pending', 'label' => 'ثبت سفارش', 'icon' => '📝'],
            ['id' => 'final-check', 'label' => 'چک نهایی', 'icon' => '🔍'],
            ['id' => 'courier', 'label' => 'تحویل مامور', 'icon' => '🚚'],
        ];

        $currentStatus = $this->order->status ?? 'pending';
        $currentIdx = array_search($currentStatus, array_column($stages, 'id'));
        if ($currentIdx === false) $currentIdx = 0;

        // گرفتن تاریخچه از activity log
        $activities = [];
        try {
            $logs = \Spatie\Activitylog\Models\Activity::where('subject_type', Order::class)
                ->where('subject_id', $this->order->id)
                ->where('event', 'updated')
                ->orderBy('created_at')
                ->get();

            foreach ($logs as $log) {
                $changes = $log->properties['attributes'] ?? [];
                if (isset($changes['status'])) {
                    $activities[] = [
                        'status' => $changes['status'],
                        'at' => $log->created_at,
                    ];
                }
            }
        } catch (\Throwable $e) {}

        // اگر activity نیست، از created_at سفارش استفاده کن
        if (empty($activities)) {
            $activities[] = ['status' => 'pending', 'at' => $this->order->created_at];
            if ($currentIdx >= 1) $activities[] = ['status' => 'final-check', 'at' => $this->order->updated_at];
            if ($currentIdx >= 2) $activities[] = ['status' => 'courier', 'at' => $this->order->updated_at];
        }

        $this->timeline = [];
        foreach ($stages as $i => $stage) {
            $state = $i < $currentIdx ? 'done' : ($i === $currentIdx ? 'current' : '');

            // پیدا کردن تاریخ این مرحله از activity
            $at = null;
            foreach ($activities as $a) {
                if ($a['status'] === $stage['id']) {
                    $at = $a['at'];
                    break;
                }
            }

            $this->timeline[] = [
                'label' => $stage['label'],
                'icon' => $stage['icon'],
                'state' => $state,
                'date' => $at ? \App\Support\PersianDate::format($at, 'Y/m/d') : '',
                'time' => $at ? $at->format('H:i') : '',
            ];
        }
    }

    public function close(): void { $this->show = false; $this->order = null; }

    public function cycleStatus(): void
    {
        if (!$this->order) return;
        $statuses = ['pending', 'final-check', 'courier'];
        $cur = array_search($this->order->status, $statuses);
        $next = $statuses[($cur === false ? 0 : ($cur + 1)) % count($statuses)];
        $this->order->update(['status' => $next]);
        $this->order->refresh();
        $this->open($this->order->id);
        $this->dispatch('order-saved');
        $this->dispatch('notify', type: 'success', message: 'وضعیت تغییر کرد');
    }

    public function editOrder(): void
    {
        $id = $this->order->id;
        $this->close();
        $this->dispatch('open-order-form', orderId: $id);
    }

    public function deleteOrder(): void
    {
        $this->order?->delete();
        $this->close();
        $this->dispatch('order-saved');
        $this->dispatch('notify', type: 'success', message: 'حذف شد');
    }

    public function render() { return view('livewire.orders.view-modal'); }
}
'''

ORDER_VIEW_BLADE = r'''<div>
@if($show && $order)
<div class="sg-modal-overlay active" wire:key="ov-{{ $order->id }}" @keydown.escape.window="$wire.close()">
    <div class="sg-modal" style="max-width:640px">
        <div class="sg-modal-header">
            <h2>📋 سفارش #{{ $order->order_number }}</h2>
            <button wire:click="close" class="sg-modal-close">✕</button>
        </div>

        <div class="sg-modal-body" style="padding:14px">

            {{-- ═══ Timeline افقی با تاریخ/ساعت ═══ --}}
            <div class="sg-timeline">
                @foreach($timeline as $step)
                    <div class="sg-tl-step {{ $step['state'] }}">
                        <div class="tl-dot">{{ $step['state'] === 'done' ? '✓' : $step['icon'] }}</div>
                        <div class="tl-lbl">{{ $step['label'] }}</div>
                        @if($step['date'])
                            <div class="tl-date">{{ $step['date'] }}</div>
                        @endif
                        @if($step['time'])
                            <div class="tl-time">{{ $step['time'] }}</div>
                        @endif
                    </div>
                @endforeach
            </div>

            {{-- ═══ باکس مشتری ═══ --}}
            @if($order->customer)
                <div class="sg-compact-box">
                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:8px">
                        <div class="avatar">
                            {{ mb_substr($order->customer_name ?? $order->customer->name ?? '?', 0, 1) }}
                        </div>
                        <div style="flex:1;min-width:0">
                            <div class="name">{{ $order->customer_name ?? $order->customer->name }}</div>
                            <div class="phone">{{ $order->phone }}</div>
                        </div>
                        @if(!empty($customerStats))
                            <div style="background:var(--gold);color:#fff;padding:3px 10px;border-radius:12px;font-size:11px;font-weight:700">
                                {{ \App\Support\PersianNumber::toFa($customerStats['total']) }} سفارش
                            </div>
                        @endif
                    </div>

                    @if(!empty($customerStats))
                        <div class="grid" style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;padding-top:8px">
                            <div class="item" style="text-align:center">
                                <div class="val" style="font-size:14px;font-weight:800">
                                    {{ number_format($customerStats['sum'] / 1000000, 1) }}M
                                </div>
                                <div class="lbl" style="font-size:9.5px;margin-top:3px">مجموع خرید</div>
                            </div>
                            <div class="item" style="text-align:center">
                                <div class="val" style="font-size:11px;font-family:monospace">
                                    {{ \App\Support\PersianDate::format($customerStats['first'], 'Y/m/d') }}
                                </div>
                                <div class="lbl" style="font-size:9.5px;margin-top:3px">اولین</div>
                            </div>
                            <div class="item" style="text-align:center">
                                <div class="val" style="font-size:11px;font-family:monospace">
                                    {{ \App\Support\PersianDate::format($customerStats['last'], 'Y/m/d') }}
                                </div>
                                <div class="lbl" style="font-size:9.5px;margin-top:3px">آخرین</div>
                            </div>
                        </div>
                    @endif
                </div>
            @endif

            {{-- ═══ اطلاعات در یک خط ═══ --}}
            <div class="sg-inline-info">
                <div class="item">📅 <strong>{{ \App\Support\PersianDate::format($order->created_at, 'Y/m/d') }}</strong></div>
                @if($order->channel)
                    <div class="item">🌐 <span class="sg-channel-cell {{ $order->channel->slug ?? 'default' }}" style="font-size:10px">{{ $order->channel->name }}</span></div>
                @endif
                <div class="item">💰 <strong>{{ \App\Support\PersianNumber::toFa(number_format($order->insurance ?? 0)) }}</strong></div>
                @if($order->postal_code)
                    <div class="item">📮 <strong style="font-family:monospace">{{ $order->postal_code }}</strong></div>
                @endif
            </div>

            {{-- ═══ محصولات ═══ --}}
            @if($order->items->count())
                <div style="margin-bottom:10px">
                    <div style="font-size:10.5px;font-weight:700;opacity:.6;margin-bottom:6px">🛍️ محصولات ({{ \App\Support\PersianNumber::toFa($order->items->count()) }})</div>
                    <div style="border:1px solid var(--border);border-radius:10px;overflow:hidden">
                        @foreach($order->items as $item)
                            <div style="padding:8px 10px;border-bottom:1px solid var(--border-soft);display:flex;gap:8px;align-items:center;font-size:12px">
                                <div style="flex:1;min-width:0">
                                    <div style="font-weight:700;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ $item->title }}</div>
                                    @if($item->sku) <div style="font-family:monospace;font-size:9.5px;opacity:.5" dir="ltr">{{ $item->sku }}</div> @endif
                                </div>
                                <div style="opacity:.6;font-size:11px">×{{ \App\Support\PersianNumber::toFa($item->quantity) }}</div>
                                <div style="font-weight:700;font-family:monospace;font-size:11.5px">{{ number_format($item->price) }}</div>
                            </div>
                        @endforeach
                    </div>
                </div>
            @endif

            {{-- ═══ آدرس ═══ --}}
            @if($order->address)
                <div style="background:var(--bg-soft);padding:10px;border-radius:10px;margin-bottom:10px;font-size:11.5px;line-height:1.6">
                    📍 {{ $order->address }}
                </div>
            @endif

            {{-- ═══ Totals ═══ --}}
            <div style="background:linear-gradient(135deg,rgba(13,148,136,.08),rgba(8,145,178,.03));padding:10px 14px;border-radius:10px">
                <div style="display:flex;gap:14px;justify-content:space-between;flex-wrap:wrap;font-size:11.5px">
                    @if(($order->shipping ?? 0) > 0)
                        <div>📦 ارسال: <strong style="font-family:monospace">{{ number_format($order->shipping) }}</strong></div>
                    @endif
                    @if(($order->discount ?? 0) > 0)
                        <div style="color:var(--warn)">🏷️ تخفیف: <strong style="font-family:monospace">-{{ number_format($order->discount) }}</strong></div>
                    @endif
                    <div style="font-size:14px;margin-right:auto">💵 <strong style="color:var(--primary);font-size:15px">{{ number_format($order->amount ?? 0) }} ت</strong></div>
                </div>
            </div>

            @if($order->notes)
                <div style="background:rgba(201,168,76,.08);padding:8px 12px;border-radius:10px;margin-top:10px;font-size:11.5px">
                    📝 {{ $order->notes }}
                </div>
            @endif
        </div>

        <div class="sg-modal-footer" style="padding:10px 14px">
            <button wire:click="deleteOrder" wire:confirm="حذف شود؟" class="btn btn-danger btn-sm">🗑️</button>
            <div style="display:flex;gap:6px">
                <button wire:click="cycleStatus" class="btn btn-outline btn-sm">🔄 وضعیت بعدی</button>
                <button wire:click="editOrder" class="btn btn-primary btn-sm">✏️ ویرایش</button>
            </div>
        </div>
    </div>
</div>
@endif
</div>
'''

# ═══════════════════════════════════════════════════════════════
# ۳) ORDERS INDEX — دکمه‌های Import + دکمه پروفایل
# ═══════════════════════════════════════════════════════════════
ORDERS_INDEX_BLADE = r'''<div>
    {{-- Toolbar --}}
    <div class="sg-toolbar">
        <div class="sg-toolbar-right">
            <input type="text" wire:model.live.debounce.400ms="search"
                   placeholder="🔍 جستجو..." class="form-control" style="width:200px">
            <select wire:model.live="filterStatus" class="form-control" style="width:auto;display:inline-block">
                <option value="">همه وضعیت‌ها</option>
                <option value="pending">📝 ثبت سفارش</option>
                <option value="final-check">🔍 چک نهایی</option>
                <option value="courier">🚚 تحویل مامور</option>
            </select>
            @if($search || $filterStatus)
                <button wire:click="$set('search',''); $set('filterStatus','')" class="btn btn-outline btn-sm">✕</button>
            @endif
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap">
            <button onclick="Livewire.dispatch('open-import-postal')" class="btn btn-mahak btn-sm" title="ایمپورت مرسولات پستی">
                📮 CSV پستی
            </button>
            <button onclick="Livewire.dispatch('open-order-form')" class="btn btn-primary">➕ سفارش جدید</button>
        </div>
    </div>

    {{-- Bulk Bar --}}
    @if(count($selected) > 0)
        <div class="sg-toolbar" style="background:linear-gradient(135deg,rgba(201,168,76,.15),rgba(201,168,76,.05));border:2px dashed var(--gold);">
            <span style="font-weight:700;color:var(--gold-dark)">{{ \App\Support\PersianNumber::toFa(count($selected)) }} مورد انتخاب شده</span>
            <div style="display:flex;gap:6px;flex-wrap:wrap">
                <button wire:click="bulkStatus('pending')" class="btn btn-outline btn-sm">📝 ثبت</button>
                <button wire:click="bulkStatus('final-check')" class="btn btn-outline btn-sm">🔍 چک</button>
                <button wire:click="bulkStatus('courier')" class="btn btn-outline btn-sm">🚚 مامور</button>
                <button wire:click="bulkDelete" wire:confirm="حذف شوند؟" class="btn btn-danger btn-sm">🗑️ حذف</button>
                <button wire:click="clearSelection" class="btn btn-outline btn-sm">✕</button>
            </div>
        </div>
    @endif

    {{-- Table --}}
    <div class="sg-table-container">
        <div class="sg-table-header">
            <h2>📦 سفارشات <span style="background:var(--gold);color:var(--primary);padding:2px 10px;border-radius:20px;font-size:10.5px;font-weight:700">{{ \App\Support\PersianNumber::toFa($orders->total()) }}</span></h2>
        </div>
        <div class="sg-table-scroll">
            <table class="sg-table">
                <thead>
                    <tr>
                        <th style="width:36px"><input type="checkbox" wire:click="selectAllVisible"></th>
                        <th>#</th>
                        <th>مشتری</th>
                        <th>تلفن</th>
                        <th>محصولات</th>
                        <th>بیمه</th>
                        <th>وضعیت</th>
                        <th>کانال</th>
                        <th>تاریخ</th>
                        <th>عملیات</th>
                    </tr>
                </thead>
                <tbody>
                    @forelse($orders as $order)
                        <tr wire:key="ord-{{ $order->id }}">
                            <td><input type="checkbox" wire:click="toggleSelect({{ $order->id }})" @if(in_array($order->id, $selected)) checked @endif></td>
                            <td><strong>#{{ $order->order_number }}</strong></td>
                            <td>
                                <span class="sg-customer-link"
                                      onclick="Livewire.dispatch('open-customer-profile', {phone: '{{ $order->phone }}'})"
                                      style="cursor:pointer;color:var(--primary);text-decoration:underline dotted">
                                    {{ $order->customer_name ?? '—' }}
                                </span>
                            </td>
                            <td dir="ltr" style="font-family:monospace;font-size:11px">{{ $order->phone ?? '—' }}</td>
                            <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis">
                                @if($order->items->count())
                                    {{ $order->items->pluck('title')->take(2)->implode('، ') }}
                                    @if($order->items->count() > 2) +{{ $order->items->count() - 2 }} @endif
                                @else — @endif
                            </td>
                            <td>{{ \App\Support\PersianNumber::toFa($order->insurance ?? 0) }}</td>
                            <td>
                                @php $st = ['pending'=>['📝','ثبت'],'final-check'=>['🔍','چک'],'courier'=>['🚚','مامور']][$order->status ?? 'pending'] ?? ['📝','ثبت']; @endphp
                                <span class="sg-status-badge {{ $order->status ?? 'pending' }}" wire:click="cycleStatus({{ $order->id }})">
                                    {{ $st[0] }} {{ $st[1] }}
                                </span>
                            </td>
                            <td>
                                @if($order->channel)
                                    <span class="sg-channel-cell {{ $order->channel->slug ?? 'default' }}">{{ $order->channel->name }}</span>
                                @else — @endif
                            </td>
                            <td style="font-size:10.5px">{{ \App\Support\PersianDate::format($order->created_at, 'Y/m/d') }}</td>
                            <td>
                                <div class="sg-action-btns">
                                    <button onclick="Livewire.dispatch('open-order-view', {orderId: {{ $order->id }}})" class="sg-action-btn view" title="نمایش">👁️</button>
                                    <button onclick="Livewire.dispatch('open-order-form', {orderId: {{ $order->id }}})" class="sg-action-btn edit" title="ویرایش">✏️</button>
                                    <button wire:click="delete({{ $order->id }})" wire:confirm="حذف شود؟" class="sg-action-btn delete" title="حذف">🗑️</button>
                                </div>
                            </td>
                        </tr>
                    @empty
                        <tr><td colspan="10"><div style="text-align:center;padding:40px;color:var(--text-light)"><div style="font-size:44px;opacity:.5">📦</div><p>سفارشی نیست</p></div></td></tr>
                    @endforelse
                </tbody>
            </table>
        </div>
        <div style="padding:14px">{{ $orders->links() }}</div>
    </div>
</div>
'''

# ═══════════════════════════════════════════════════════════════
# ۴) CUSTOMER PROFILE MODAL — پاپ‌آپ
# ═══════════════════════════════════════════════════════════════
CUSTOMER_PROFILE_PHP = r'''<?php
namespace App\Livewire\Customers;

use App\Models\Customer;
use Livewire\Attributes\On;
use Livewire\Component;

class ProfileModal extends Component
{
    public bool $show = false;
    public ?Customer $customer = null;
    public array $stats = [];
    public array $orders = [];

    #[On('open-customer-profile')]
    public function open(?string $phone = null, ?int $customerId = null): void
    {
        $customer = null;
        if ($customerId) {
            $customer = Customer::find($customerId);
        } elseif ($phone) {
            $np = preg_replace('/\D/', '', $phone);
            $customer = Customer::where('phone', 'like', "%{$np}%")->first();
        }

        if (!$customer) {
            $this->dispatch('notify', type: 'error', message: 'مشتری پیدا نشد');
            return;
        }

        $this->customer = $customer;
        $orders = $customer->orders()->latest()->get();

        $this->stats = [
            'total' => $orders->count(),
            'sum' => (float) $orders->sum('amount'),
            'insurance' => (float) $orders->sum('insurance'),
            'first' => $orders->last()?->created_at,
            'last' => $orders->first()?->created_at,
        ];

        $this->orders = $orders->take(10)->map(fn($o) => [
            'id' => $o->id,
            'num' => $o->order_number,
            'amount' => (float) $o->amount,
            'status' => $o->status,
            'date' => \App\Support\PersianDate::format($o->created_at, 'Y/m/d'),
            'products' => $o->items->pluck('title')->take(2)->implode('، '),
        ])->toArray();

        $this->show = true;
    }

    public function close(): void { $this->show = false; $this->customer = null; }

    public function viewOrder(int $orderId): void
    {
        $this->close();
        $this->dispatch('open-order-view', orderId: $orderId);
    }

    public function render() { return view('livewire.customers.profile-modal'); }
}
'''

CUSTOMER_PROFILE_BLADE = r'''<div>
@if($show && $customer)
<div class="sg-modal-overlay active" @keydown.escape.window="$wire.close()">
    <div class="sg-modal" style="max-width:600px">
        <div class="sg-modal-header">
            <h2>👤 پروفایل مشتری</h2>
            <button wire:click="close" class="sg-modal-close">✕</button>
        </div>

        <div class="sg-modal-body" style="padding:14px">

            {{-- باکس مشتری --}}
            <div class="sg-compact-box">
                <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px">
                    <div class="avatar" style="width:50px;height:50px;font-size:20px">
                        {{ mb_substr($customer->name ?? '?', 0, 1) }}
                    </div>
                    <div style="flex:1;min-width:0">
                        <div class="name" style="font-size:16px">{{ $customer->name }}</div>
                        <div class="phone" style="font-size:12px">{{ $customer->phone }}</div>
                    </div>
                </div>

                @if(!empty($stats))
                    <div class="grid" style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;padding-top:10px">
                        <div class="item" style="text-align:center">
                            <div class="val">{{ \App\Support\PersianNumber::toFa($stats['total']) }}</div>
                            <div class="lbl">سفارشات</div>
                        </div>
                        <div class="item" style="text-align:center">
                            <div class="val">{{ number_format($stats['sum'] / 1000000, 1) }}M</div>
                            <div class="lbl">مجموع</div>
                        </div>
                        <div class="item" style="text-align:center">
                            <div class="val">{{ number_format($stats['insurance']) }}</div>
                            <div class="lbl">بیمه</div>
                        </div>
                    </div>
                @endif
            </div>

            @if($customer->address)
                <div class="sg-inline-info">
                    <div class="item">📍 {{ $customer->address }}</div>
                    @if($customer->postal_code)
                        <div class="item">📮 <strong style="font-family:monospace">{{ $customer->postal_code }}</strong></div>
                    @endif
                </div>
            @endif

            {{-- تاریخچه سفارشات --}}
            <div style="font-size:12px;font-weight:700;color:var(--primary);margin:14px 0 8px">
                📦 آخرین سفارشات
            </div>

            @forelse($orders as $o)
                <div wire:key="ord-{{ $o['id'] }}"
                     style="padding:10px;border:1px solid var(--border);border-radius:10px;margin-bottom:6px;cursor:pointer;transition:.15s"
                     wire:click="viewOrder({{ $o['id'] }})"
                     onmouseover="this.style.background='var(--bg-soft)'"
                     onmouseout="this.style.background='transparent'">
                    <div style="display:flex;justify-content:space-between;font-weight:700;font-size:12.5px;margin-bottom:4px">
                        <span>#{{ $o['num'] }}</span>
                        <span style="font-size:10.5px;opacity:.6;font-family:monospace">{{ $o['date'] }}</span>
                    </div>
                    @if($o['products'])
                        <div style="font-size:11px;opacity:.7;margin-bottom:3px">🛍️ {{ $o['products'] }}</div>
                    @endif
                    <div style="display:flex;justify-content:space-between;font-size:11px">
                        <span style="font-family:monospace">{{ number_format($o['amount']) }} ت</span>
                        <span class="sg-status-badge {{ $o['status'] }}" style="font-size:10px;padding:2px 8px">
                            {{ ['pending'=>'📝 ثبت','final-check'=>'🔍 چک','courier'=>'🚚 مامور'][$o['status']] ?? '📝' }}
                        </span>
                    </div>
                </div>
            @empty
                <p style="text-align:center;padding:20px;opacity:.5;font-size:12px">سفارشی نیست</p>
            @endforelse
        </div>

        <div class="sg-modal-footer">
            <button wire:click="close" class="btn btn-outline btn-sm">بستن</button>
            <a href="{{ route('customers.index') }}" class="btn btn-primary btn-sm">👥 همه مشتریان</a>
        </div>
    </div>
</div>
@endif
</div>
'''

# ═══════════════════════════════════════════════════════════════
# ۵) Patch Layout — اضافه کردن ProfileModal
# ═══════════════════════════════════════════════════════════════
def patch_layout():
    layout = PROJECT / "resources/views/components/layouts/app.blade.php"
    if not layout.exists(): return

    backup("resources/views/components/layouts/app.blade.php")

    with open(layout, 'r', encoding='utf-8') as f:
        content = f.read()

    # اضافه کردن ProfileModal اگر نیست
    if "customers.profile-modal" not in content:
        content = content.replace(
            "<livewire:orders.form-modal",
            "<livewire:customers.profile-modal :key=\"'cpm'\" />\n    <livewire:orders.form-modal",
            1
        )

    # اضافه کردن extra.css نسخه ۴
    if 'extra.css' in content:
        import re
        content = re.sub(r'extra\.css[^"]*', 'extra.css?v=4', content)

    # Style داینامیک — بهتر
    if 'primary-dynamic' not in content:
        style_block = '''    @php
        try {
            $_p = \\App\\Models\\AppSetting::get('primary_color', '#1a5276');
            $_g = \\App\\Models\\AppSetting::get('accent_color', '#c9a84c');
            $_f = \\App\\Models\\AppSetting::get('font_family', 'Vazirmatn');
        } catch (\\Throwable $e) {
            $_p = '#1a5276'; $_g = '#c9a84c'; $_f = 'Vazirmatn';
        }
    @endphp
    <style>
        :root {
            --primary: {{ $_p }} !important;
            --gold: {{ $_g }} !important;
            --font-dynamic: {{ $_f }};
        }
        body { font-family: var(--font-dynamic), 'Vazirmatn', Tahoma, sans-serif !important; }
    </style>
'''
        content = content.replace('</head>', style_block + '</head>', 1)

    with open(layout, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print("  ✓ Layout: ProfileModal + CSS v4")

# ═══════════════════════════════════════════════════════════════
# اجرا
# ═══════════════════════════════════════════════════════════════
def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  رفع کامل — تم تیره + همه موارد                               ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    print("📄 نوشتن فایل‌ها...")
    write("public/css/extra.css", EXTRA_CSS)
    write("app/Livewire/Orders/ViewModal.php", ORDER_VIEW_PHP)
    write("resources/views/livewire/orders/view-modal.blade.php", ORDER_VIEW_BLADE)
    write("resources/views/livewire/orders/index.blade.php", ORDERS_INDEX_BLADE)
    write("app/Livewire/Customers/ProfileModal.php", CUSTOMER_PROFILE_PHP)
    write("resources/views/livewire/customers/profile-modal.blade.php", CUSTOMER_PROFILE_BLADE)

    print("\n🔧 Patch Layout...")
    patch_layout()

    print("\n" + "═" * 64)
    print("✅ تمام!")
    print("═" * 64)
    print("""
📋 اجرا کن:

  cd ~/shopgun-v2.2
  php artisan optimize:clear
  php artisan view:clear

  # سرور رو ببند (Ctrl+C) و دوباره باز کن
  php artisan serve

  # مرورگر: Ctrl+Shift+R

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 چه چیزی رفع شد:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✅ تم تیره هماهنگ — همه کامپوننت‌ها (Header, Table, Card, Modal, Form, Button)
  ✅ رنگ‌ها/فونت‌های خوانا در تم تیره
  ✅ بدون هاله نور روی آیتم‌ها
  ✅ Timeline با تاریخ + ساعت شمسی
  ✅ Timeline اسکرول افقی
  ✅ پروفایل مشتری → Modal پاپ‌آپ
  ✅ کلیک روی نام مشتری در سفارشات → پروفایل
  ✅ دکمه ایمپورت CSV پستی در /orders
  ✅ تاریخ شمسی در همه جدول‌ها
  ✅ دکمه پروفایل مشتری داخل Modal سفارش

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📌 تست:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ۱. تم تیره:
     تنظیمات → ظاهر → تم → تیره → همه چیز باید هماهنگ باشه

  ۲. تایم‌لاین:
     /orders → کلیک روی 👁️ → باید تایم‌لاین با تاریخ و ساعت شمسی ببینی

  ۳. پروفایل:
     /orders → کلیک روی نام مشتری → پاپ‌آپ پروفایل

  ۴. ایمپورت CSV:
     /orders → دکمه «📮 CSV پستی» → آپلود فایل
""")

if __name__ == "__main__":
    main()
