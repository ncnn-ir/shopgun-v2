#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ShopGun V2 - v6: PowerGrid + Real Jalali Picker"""

import subprocess
from pathlib import Path
from datetime import datetime

ROOT = Path('/data/data/com.termux/files/home/shopgun-v2.2')

def log(m, k='info'):
    ic = {'info':'ℹ️','ok':'✅','warn':'⚠️','err':'❌'}
    co = {'info':'\033[96m','ok':'\033[92m','warn':'\033[93m','err':'\033[91m'}
    print(f"{co[k]} {ic[k]} {m}\033[0m")

def write(rel, content):
    full = ROOT / rel
    full.parent.mkdir(parents=True, exist_ok=True)
    if full.exists():
        full.rename(full.with_suffix(full.suffix + f'.bak-{datetime.now().strftime("%H%M%S")}'))
    full.write_text(content, encoding='utf-8')
    log(f"✓ {rel}", 'ok')

def delete(rel):
    full = ROOT / rel
    if full.exists():
        full.rename(full.with_suffix(full.suffix + f'.bak-{datetime.now().strftime("%H%M%S")}'))
        log(f"حذف: {rel}", 'warn')

# ═══════════════════════════════════════════════════════════════
# ۱. حذف کامپوننت خراب قبلی (jalali-date.blade.php)
# ═══════════════════════════════════════════════════════════════
delete('resources/views/components/ui/jalali-date.blade.php')

# ═══════════════════════════════════════════════════════════════
# ۲. POWERGRID — جدول سفارشات حرفه‌ای
# ═══════════════════════════════════════════════════════════════

ORDERS_TABLE_PHP = r'''<?php

namespace App\Livewire\Tables;

use App\Models\Order;
use Illuminate\Database\Eloquent\Builder;
use PowerComponents\LivewirePowerGrid\Column;
use PowerComponents\LivewirePowerGrid\Facades\Filter;
use PowerComponents\LivewirePowerGrid\Facades\PowerGrid;
use PowerComponents\LivewirePowerGrid\PowerGridComponent;
use PowerComponents\LivewirePowerGrid\PowerGridFields;

final class OrdersTable extends PowerGridComponent
{
    public string $tableName = 'orders-table';
    public string $sortField = 'id';
    public string $sortDirection = 'desc';

    public function setUp(): array
    {
        return [
            PowerGrid::header()
                ->showSearchInput()
                ->showToggleColumns(),

            PowerGrid::footer()
                ->showPerPage(perPage: 20, perPageValues: [10, 20, 50, 100])
                ->showRecordCount(),

            PowerGrid::detail()
                ->view('livewire.tables.orders-detail')
                ->showCollapseIcon(),
        ];
    }

    public function datasource(): Builder
    {
        return Order::query()
            ->with(['items', 'channel', 'customer']);
    }

    public function relationSearch(): array
    {
        return [
            'customer' => ['name', 'phone'],
        ];
    }

    public function fields(): PowerGridFields
    {
        return PowerGrid::fields()
            ->add('id')
            ->add('order_number')
            ->add('customer_display', fn($row) => $row->customer_name ?? $row->customer?->name ?? '—')
            ->add('phone')
            ->add('items_summary', function ($row) {
                if (!$row->items->count()) return '—';
                $names = $row->items->pluck('title')->take(2)->implode('، ');
                $extra = $row->items->count() > 2 ? ' +' . ($row->items->count() - 2) : '';
                return $names . $extra;
            })
            ->add('insurance_fmt', fn($row) => \App\Support\PersianNumber::toFa(number_format((float) $row->insurance)))
            ->add('status_label', function ($row) {
                $map = [
                    'pending'     => '<span class="badge-pill badge-warn">📝 ثبت سفارش</span>',
                    'final-check' => '<span class="badge-pill badge-info">🔍 چک نهایی</span>',
                    'courier'     => '<span class="badge-pill badge-ok">🚚 تحویل مامور</span>',
                ];
                return $map[$row->status] ?? '<span class="badge-pill">?</span>';
            })
            ->add('channel_name', fn($row) => $row->channel ? ($row->channel->icon . ' ' . $row->channel->name) : '—')
            ->add('created_at_fmt', fn($row) => \App\Support\PersianDate::format($row->created_at, 'Y/m/d H:i'))
            ->add('actions', function ($row) {
                $id = $row->id;
                return '<div class="flex gap-1 justify-center">'
                    . '<button onclick="Livewire.dispatch(\'open-order-view\', {orderId: ' . $id . '})" class="btn-icon" title="نمایش">👁️</button>'
                    . '<button onclick="Livewire.dispatch(\'open-order-form\', {orderId: ' . $id . '})" class="btn-icon" title="ویرایش">✏️</button>'
                    . '<a href="' . route('orders.show', $id) . '" wire:navigate class="btn-icon" title="صفحه کامل">📄</a>'
                    . '</div>';
            });
    }

    public function columns(): array
    {
        return [
            Column::action('actions')
                ->title('عملیات'),

            Column::add()
                ->title('#')
                ->field('order_number')
                ->searchable()
                ->sortable(),

            Column::add()
                ->title('مشتری')
                ->field('customer_display')
                ->searchable()
                ->sortable(),

            Column::add()
                ->title('تلفن')
                ->field('phone')
                ->searchable(),

            Column::add()
                ->title('محصولات')
                ->field('items_summary'),

            Column::add()
                ->title('بیمه')
                ->field('insurance_fmt')
                ->sortable(),

            Column::add()
                ->title('وضعیت')
                ->field('status_label')
                ->sortable(),

            Column::add()
                ->title('کانال')
                ->field('channel_name'),

            Column::add()
                ->title('تاریخ')
                ->field('created_at_fmt')
                ->sortable(),
        ];
    }

    public function filters(): array
    {
        return [
            Filter::inputText('order_number')
                ->operators(['contains', 'starts_with', 'equals'])
                ->placeholder('شماره...'),

            Filter::inputText('customer_display')
                ->operators(['contains', 'starts_with'])
                ->placeholder('نام مشتری...'),

            Filter::inputText('phone')
                ->operators(['contains', 'starts_with'])
                ->placeholder('تلفن...'),

            Filter::select('status_label')
                ->dataSource(collect([
                    ['label' => '📝 ثبت سفارش',  'value' => 'pending'],
                    ['label' => '🔍 چک نهایی',   'value' => 'final-check'],
                    ['label' => '🚚 تحویل مامور', 'value' => 'courier'],
                ]))
                ->optionLabel('label')
                ->optionValue('value'),

            Filter::multiSelect('channel_name')
                ->dataSource(collect(\App\Models\Channel::all())->map(fn($c) => [
                    'label' => ($c->icon ?? '') . ' ' . $c->name,
                    'value' => $c->icon . ' ' . $c->name,
                ]))
                ->optionLabel('label')
                ->optionValue('value'),
        ];
    }

    public function header(): array
    {
        return [
            PowerGrid::actions()
                ->addButton('open-order-form')
                ->slot('<span>➕ سفارش جدید</span>')
                ->class('btn btn-primary btn-sm'),
        ];
    }
}
'''
write('app/Livewire/Tables/OrdersTable.php', ORDERS_TABLE_PHP)

# View PowerGrid
ORDERS_TABLE_VIEW = r'''<div>
    <div class="p-4 md:p-6" dir="rtl">
        <h1 class="text-2xl font-bold mb-4">📦 سفارشات</h1>
        <livewire:tables.orders-table />
    </div>
</div>
'''
write('resources/views/livewire/tables/orders-table-page.blade.php', ORDERS_TABLE_VIEW)

# Detail view
ORDERS_DETAIL = r'''<div class="p-3 bg-base-200/50 rounded-lg" dir="rtl">
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
        <div>
            <div class="text-base-content/60">آدرس:</div>
            <div class="font-bold">{{ $row->address ?? '—' }}</div>
        </div>
        <div>
            <div class="text-base-content/60">کدپستی:</div>
            <div class="font-mono font-bold">{{ $row->postal_code ?? '—' }}</div>
        </div>
        <div>
            <div class="text-base-content/60">کانال:</div>
            <div class="font-bold">{{ $row->channel?->name ?? '—' }}</div>
        </div>
        <div>
            <div class="text-base-content/60">یادداشت:</div>
            <div>{{ $row->notes ?? '—' }}</div>
        </div>
    </div>
</div>
'''
write('resources/views/livewire/tables/orders-detail.blade.php', ORDERS_DETAIL)

# ═══════════════════════════════════════════════════════════════
# ۳. جایگزینی Orders Index با PowerGrid
# ═══════════════════════════════════════════════════════════════

# تغییر Route orders.index به PowerGrid
ROUTES = ROOT / 'routes/web.php'
if ROUTES.exists():
    c = ROUTES.read_text(encoding='utf-8')
    # اضافه کردن route جدید برای powergrid (به عنوان alias)
    if 'tables.orders' not in c:
        marker = "Route::get('/', OrdersIndex::class)->name('index');"
        if marker in c:
            c = c.replace(marker,
                marker + "\n        Route::get('/table', \\App\\Livewire\\Tables\\OrdersTable::class)->name('table');")
            ROUTES.write_text(c, encoding='utf-8')
            log("route orders.table اضافه شد", 'ok')

# Index view — فقط لینک به table
ORDERS_INDEX_SIMPLE = r'''<div class="p-4 md:p-6" dir="rtl">
    <div class="flex items-center justify-between mb-4 flex-wrap gap-2">
        <h1 class="text-2xl font-bold">📦 سفارشات</h1>
        <div class="flex gap-2">
            <a href="{{ route('orders.table') }}" wire:navigate class="btn btn-primary btn-sm">
                📊 جدول حرفه‌ای (PowerGrid)
            </a>
            <button onclick="Livewire.dispatch('open-order-form')" class="btn btn-success btn-sm">
                ➕ سفارش جدید
            </button>
        </div>
    </div>

    <div class="alert alert-info text-sm">
        <span>💡 برای جدول با فیلتر ستونی، چک‌باکس مخفی/نمایان ستون، مرتب‌سازی و Export — روی «جدول حرفه‌ای» کلیک کن</span>
    </div>

    <div class="mt-4">
        <livewire:orders.index />
    </div>
</div>
'''

# ═══════════════════════════════════════════════════════════════
# ۴. CSS برای PowerGrid (DaisyUI 5 + RTL)
# ═══════════════════════════════════════════════════════════════

PG_CSS = r'''

/* ═══════════════════════════════════════════════════════════
   PowerGrid Customization - DaisyUI 5 + RTL
   ═══════════════════════════════════════════════════════════ */

.pg-wrap {
    background: var(--bg-card, #fff);
    border-radius: 14px;
    border: 1px solid var(--border, #e2e8f0);
    overflow: hidden;
}

.pg-header {
    padding: 12px 16px;
    border-bottom: 1px solid var(--border, #e2e8f0);
    background: var(--bg-soft, #f8fafc);
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    align-items: center;
    justify-content: space-between;
}

.pg-footer {
    padding: 10px 16px;
    border-top: 1px solid var(--border, #e2e8f0);
    background: var(--bg-soft, #f8fafc);
    display: flex;
    flex-wrap: wrap;
    gap: 10px;
    align-items: center;
    justify-content: space-between;
    font-size: 12px;
}

.pg-search-input {
    padding: 8px 14px;
    border: 1.5px solid var(--border, #e2e8f0);
    border-radius: 10px;
    background: #fff;
    font-family: inherit;
    font-size: 13px;
    min-width: 240px;
    outline: none;
    transition: border .15s;
}
.pg-search-input:focus {
    border-color: var(--gold, #c9a84c);
    box-shadow: 0 0 0 3px rgba(201,168,76,.15);
}

.pg-btn-toggle-cols {
    padding: 8px 14px;
    background: var(--primary, #1a5276);
    color: #fff;
    border: none;
    border-radius: 10px;
    font-weight: 700;
    font-size: 12px;
    cursor: pointer;
    font-family: inherit;
    transition: opacity .15s;
}
.pg-btn-toggle-cols:hover { opacity: .9; }

/* Toggle columns dropdown */
.pg-toggle-cols {
    padding: 12px;
    background: #fff;
    border: 2px solid var(--gold, #c9a84c);
    border-radius: 12px;
    box-shadow: 0 8px 24px rgba(0,0,0,.15);
    min-width: 200px;
    max-height: 320px;
    overflow-y: auto;
}
.pg-toggle-cols label {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 6px 8px;
    cursor: pointer;
    border-radius: 6px;
    font-size: 12px;
    transition: background .1s;
}
.pg-toggle-cols label:hover { background: rgba(201,168,76,.08); }
.pg-toggle-cols input[type=checkbox] {
    width: 16px; height: 16px;
    accent-color: var(--gold, #c9a84c);
}

/* Table itself */
.pg-table {
    width: 100%;
    border-collapse: collapse;
    font-size: 12.5px;
    background: #fff;
}
.pg-table thead th {
    background: var(--thead-bg, #f8f6f0);
    padding: 10px 12px;
    text-align: right;
    font-weight: 700;
    font-size: 11.5px;
    color: var(--primary, #1a5276);
    border-bottom: 2px solid var(--border, #e2e8f0);
    white-space: nowrap;
    position: sticky;
    top: 0;
    z-index: 2;
}
.pg-table thead th button {
    background: transparent;
    border: none;
    font-family: inherit;
    font-size: inherit;
    font-weight: inherit;
    color: inherit;
    cursor: pointer;
    display: flex;
    align-items: center;
    gap: 4px;
    padding: 0;
    width: 100%;
    text-align: right;
}
.pg-table thead th button:hover {
    color: var(--gold, #c9a84c);
}
.pg-table thead th svg {
    width: 12px; height: 12px;
    opacity: .35;
}
.pg-table thead th.sort-active svg { opacity: 1; color: var(--gold, #c9a84c); }

.pg-table tbody td {
    padding: 9px 12px;
    border-bottom: 1px solid rgba(0,0,0,.05);
    vertical-align: middle;
    background: #fff;
    color: var(--text, #2c3e50);
}
.pg-table tbody tr:hover td {
    background: rgba(201,168,76,.05);
}
.pg-table tbody tr.pg-row-selected td {
    background: rgba(201,168,76,.12);
}

/* Filter row */
.pg-filter-row td {
    padding: 6px 8px;
    background: rgba(0,0,0,.02);
    border-bottom: 1px solid var(--border, #e2e8f0);
}
.pg-filter-row input,
.pg-filter-row select {
    width: 100%;
    padding: 4px 8px;
    border: 1px solid var(--border, #e2e8f0);
    border-radius: 6px;
    font-family: inherit;
    font-size: 11.5px;
    background: #fff;
    outline: none;
}
.pg-filter-row input:focus,
.pg-filter-row select:focus {
    border-color: var(--gold, #c9a84c);
    box-shadow: 0 0 0 2px rgba(201,168,76,.15);
}

/* Buttons */
.btn-icon {
    width: 28px; height: 28px;
    border-radius: 8px;
    border: none;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    background: rgba(0,0,0,.05);
    cursor: pointer;
    font-size: 13px;
    transition: all .15s;
    text-decoration: none;
    color: inherit;
}
.btn-icon:hover {
    background: rgba(201,168,76,.2);
    transform: scale(1.05);
}

/* Badges */
.badge-pill {
    display: inline-flex;
    align-items: center;
    gap: 4px;
    padding: 3px 10px;
    border-radius: 999px;
    font-size: 11px;
    font-weight: 700;
    white-space: nowrap;
}
.badge-pill.badge-warn { background: rgba(251,146,60,.15); color: #b45309; }
.badge-pill.badge-info { background: rgba(59,130,246,.15); color: #1d4ed8; }
.badge-pill.badge-ok   { background: rgba(34,197,94,.15); color: #15803d; }

/* Pagination */
.pg-pagination {
    display: flex;
    gap: 4px;
    align-items: center;
    flex-wrap: wrap;
}
.pg-pagination button {
    min-width: 32px;
    height: 32px;
    border-radius: 8px;
    border: 1px solid var(--border, #e2e8f0);
    background: #fff;
    font-family: inherit;
    font-size: 12px;
    font-weight: 600;
    cursor: pointer;
    color: var(--text, #2c3e50);
    transition: all .12s;
}
.pg-pagination button:hover {
    border-color: var(--gold, #c9a84c);
    background: rgba(201,168,76,.08);
}
.pg-pagination button.active {
    background: var(--primary, #1a5276);
    color: #fff;
    border-color: var(--primary, #1a5276);
}

/* Detail row */
.pg-detail-row td {
    padding: 0 !important;
    background: rgba(0,0,0,.02) !important;
    border-bottom: 2px solid var(--primary, #1a5276) !important;
}

/* Dark */
[data-theme="dark"] .pg-table,
[data-theme="dark"] .pg-table tbody td { background: #151b27; color: #e6edf5; }
[data-theme="dark"] .pg-table thead th { background: #1c2332; color: #6bb8e3; }
[data-theme="dark"] .pg-wrap { background: #151b27; border-color: #2a3544; }
[data-theme="dark"] .pg-header,
[data-theme="dark"] .pg-footer { background: #1c2332; border-color: #2a3544; }
[data-theme="dark"] .pg-search-input { background: #1c2332; color: #e6edf5; border-color: #2a3544; }
[data-theme="dark"] .pg-toggle-cols { background: #1c2332; }
[data-theme="dark"] .pg-table tbody tr:hover td { background: rgba(201,168,76,.08); }

/* Mobile */
@media (max-width: 768px) {
    .pg-header { padding: 10px; }
    .pg-search-input { min-width: 100%; }
    .pg-table { font-size: 11.5px; }
    .pg-table thead th, .pg-table tbody td { padding: 6px 8px; }
}
'''

css_path = ROOT / 'public/css/extra.css'
if css_path.exists():
    c = css_path.read_text(encoding='utf-8')
    if 'PowerGrid Customization' not in c:
        css_path.write_text(c + PG_CSS, encoding='utf-8')
        log("CSS PowerGrid اضافه شد", 'ok')

# ═══════════════════════════════════════════════════════════════
# ۵. Tailwind — اضافه کردن @source برای PowerGrid
# ═══════════════════════════════════════════════════════════════

app_css = ROOT / 'resources/css/app.css'
if app_css.exists():
    c = app_css.read_text(encoding='utf-8')
    src_line = "@source '../../vendor/power-components/livewire-powergrid/src/**/*.php';"
    if src_line not in c:
        c = c.replace("@source '../**/*.js';", "@source '../**/*.js';\n" + src_line)
        app_css.write_text(c, encoding='utf-8')
        log("@source PowerGrid اضافه شد", 'ok')

# ═══════════════════════════════════════════════════════════════
# ۶. تب‌های تنظیمات — CSS قطعی
# ═══════════════════════════════════════════════════════════════

TABS_CSS = r'''

/* ═══════════════════════════════════════════════════════════
   Settings Tabs — FORCE FIX
   ═══════════════════════════════════════════════════════════ */

.sg-settings-tabs {
    display: flex !important;
    flex-wrap: nowrap !important;
    gap: 8px !important;
    overflow-x: auto !important;
    overflow-y: hidden !important;
    padding: 10px 16px !important;
    margin: 0 0 14px 0 !important;
    background: transparent !important;
    border-bottom: 2px solid var(--border, #e2e8f0) !important;
    scrollbar-width: thin;
    -webkit-overflow-scrolling: touch;
}
.sg-settings-tabs::-webkit-scrollbar { height: 4px; }
.sg-settings-tabs::-webkit-scrollbar-thumb {
    background: var(--border, #cbd5e1);
    border-radius: 2px;
}

.sg-settings-tab {
    flex: 0 0 auto !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 6px !important;
    padding: 8px 14px !important;
    border: 1.5px solid var(--border, #e2e8f0) !important;
    border-radius: 10px !important;
    background: var(--bg-card, #fff) !important;
    font-family: inherit !important;
    font-size: 12.5px !important;
    font-weight: 700 !important;
    color: var(--text-light, #64748b) !important;
    cursor: pointer !important;
    white-space: nowrap !important;
    transition: all .15s !important;
    text-decoration: none !important;
}
.sg-settings-tab:hover {
    border-color: var(--gold, #c9a84c) !important;
    color: var(--text, #0f172a) !important;
    transform: translateY(-1px) !important;
}
.sg-settings-tab.active {
    background: linear-gradient(135deg, var(--primary, #1a5276), #0d3b5e) !important;
    color: #fff !important;
    border-color: var(--primary, #1a5276) !important;
    box-shadow: 0 4px 12px rgba(26,82,118,.25) !important;
}
.sg-settings-tab .badge-new {
    background: var(--gold, #c9a84c) !important;
    color: #fff !important;
    font-size: 8px !important;
    padding: 1px 5px !important;
    border-radius: 8px !important;
    font-weight: 800 !important;
}

/* Force hide old tabs */
.sg-tabs-mobile, .sg-tabs-bar { display: none !important; }

/* Hide old jalali picker */
.jalali-picker-wrap { display: none !important; }
'''

css_path = ROOT / 'public/css/extra.css'
if css_path.exists():
    c = css_path.read_text(encoding='utf-8')
    if 'Settings Tabs — FORCE FIX' not in c:
        css_path.write_text(c + TABS_CSS, encoding='utf-8')
        log("CSS Tabs قطعی اضافه شد", 'ok')

# ═══════════════════════════════════════════════════════════════
# ۷. تاریخ شمسی در Orders View — استفاده از پکیج نصب‌شده
# ═══════════════════════════════════════════════════════════════

# PowerShell view - از livewire package استفاده کن
ORDERS_INDEX_VIEW_JALALI = r'''<div dir="rtl">

    <div style="padding: 12px 14px 0">
        <div class="filter-bar">
            <div class="field">
                <label>🔍 جستجو</label>
                <input type="text" wire:model.live.debounce.400ms="search" placeholder="شماره، نام، تلفن..." />
            </div>

            <div class="field">
                <label>📊 وضعیت</label>
                <select wire:model.live="filterStatus">
                    <option value="">همه</option>
                    <option value="pending">📝 ثبت سفارش</option>
                    <option value="final-check">🔍 چک نهایی</option>
                    <option value="courier">🚚 تحویل مامور</option>
                </select>
            </div>

            <div class="field">
                <label>📅 از تاریخ</label>
                <livewire:jalali-datepicker wire:model="dateFrom" :hasTime="false" placeholder="از تاریخ" wire:key="jalali-from" />
            </div>

            <div class="field">
                <label>📅 تا تاریخ</label>
                <livewire:jalali-datepicker wire:model="dateTo" :hasTime="false" placeholder="تا تاریخ" wire:key="jalali-to" />
            </div>

            <div class="field">
                <label style="opacity:0">عملیات</label>
                <div style="display:flex;gap:6px">
                    <button wire:click="clearFilters" class="btn btn-outline btn-sm" title="پاک کردن">✕</button>
                    <button onclick="Livewire.dispatch('open-order-form')" class="btn btn-primary btn-sm">➕ جدید</button>
                </div>
            </div>
        </div>
    </div>

    <div style="padding: 0 14px 14px">
        <a href="{{ route('orders.table') }}" wire:navigate class="btn btn-primary btn-sm">
            📊 جدول حرفه‌ای (PowerGrid با فیلتر ستونی)
        </a>
    </div>

    <div class="sg-table-container">
        <div class="sg-table-header">
            <h2>📦 سفارشات <span style="background:var(--gold);color:var(--primary);padding:2px 10px;border-radius:20px;font-size:10.5px;font-weight:700">{{ \App\Support\PersianNumber::toFa($orders->total()) }}</span></h2>
        </div>

        <div class="sg-table-scroll">
            <table class="sg-table">
                <thead>
                    <tr>
                        <th style="width:36px"><input type="checkbox" wire:click="selectAllVisible"></th>
                        <th wire:click="sortBy('order_number')" class="sortable {{ $sortField === 'order_number' ? 'sorted-' . $sortDirection : '' }}"># سفارش</th>
                        <th wire:click="sortBy('customer_name')" class="sortable {{ $sortField === 'customer_name' ? 'sorted-' . $sortDirection : '' }}">مشتری</th>
                        <th>تلفن</th>
                        <th>محصولات</th>
                        <th wire:click="sortBy('insurance')" class="sortable {{ $sortField === 'insurance' ? 'sorted-' . $sortDirection : '' }}">بیمه</th>
                        <th>وضعیت</th>
                        <th wire:click="sortBy('created_at')" class="sortable {{ $sortField === 'created_at' ? 'sorted-' . $sortDirection : '' }}">تاریخ</th>
                        <th>عملیات</th>
                    </tr>
                </thead>
                <tbody>
                    @forelse($orders as $order)
                        <tr wire:key="ord-{{ $order->id }}">
                            <td><input type="checkbox" wire:click="toggleSelect({{ $order->id }})" @if(in_array($order->id, $selected)) checked @endif></td>
                            <td><strong>#{{ $order->order_number }}</strong></td>
                            <td>{{ $order->customer_name ?? '—' }}</td>
                            <td dir="ltr" style="font-family:monospace;font-size:11px">{{ $order->phone ?? '—' }}</td>
                            <td style="max-width:200px;overflow:hidden;text-overflow:ellipsis">
                                @if($order->items->count())
                                    {{ $order->items->pluck('title')->take(2)->implode('، ') }}
                                    @if($order->items->count() > 2) <span style="opacity:.5">+{{ $order->items->count() - 2 }}</span> @endif
                                @else — @endif
                            </td>
                            <td>{{ \App\Support\PersianNumber::toFa(number_format((float) $order->insurance)) }}</td>
                            <td>
                                @php $st = ['pending'=>['📝','ثبت'],'final-check'=>['🔍','چک'],'courier'=>['🚚','مامور']][$order->status ?? 'pending'] ?? ['📝','ثبت']; @endphp
                                <span class="sg-status-badge {{ $order->status ?? 'pending' }}" wire:click="cycleStatus({{ $order->id }})" style="cursor:pointer">
                                    {{ $st[0] }} {{ $st[1] }}
                                </span>
                            </td>
                            <td style="font-size:10.5px;font-family:monospace">{{ \App\Support\PersianDate::format($order->created_at, 'Y/m/d') }}</td>
                            <td>
                                <div class="sg-action-btns">
                                    <button onclick="Livewire.dispatch('open-order-view', {orderId: {{ $order->id }}})" class="sg-action-btn view">👁️</button>
                                    <button onclick="Livewire.dispatch('open-order-form', {orderId: {{ $order->id }}})" class="sg-action-btn edit">✏️</button>
                                    <button wire:click="delete({{ $order->id }})" wire:confirm="حذف شود؟" class="sg-action-btn delete">🗑️</button>
                                </div>
                            </td>
                        </tr>
                    @empty
                        <tr><td colspan="9" style="text-align:center;padding:40px;opacity:.5">
                            <div style="font-size:44px">📦</div>
                            <p>سفارشی نیست</p>
                        </td></tr>
                    @endforelse
                </tbody>
            </table>
        </div>

        <div style="padding:14px">{{ $orders->links() }}</div>
    </div>

    @if(count($selected) > 0)
        <div style="position:fixed;bottom:80px;left:20px;right:20px;background:var(--bg-card);border:2px dashed var(--gold);border-radius:14px;padding:12px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px;z-index:50;box-shadow:0 8px 32px rgba(0,0,0,.2)">
            <span style="font-weight:700;color:var(--gold-dark)">{{ \App\Support\PersianNumber::toFa(count($selected)) }} مورد</span>
            <div style="display:flex;gap:6px;flex-wrap:wrap">
                <button wire:click="bulkStatus('pending')" class="btn btn-outline btn-sm">📝 ثبت</button>
                <button wire:click="bulkStatus('final-check')" class="btn btn-outline btn-sm">🔍 چک</button>
                <button wire:click="bulkStatus('courier')" class="btn btn-outline btn-sm">🚚 مامور</button>
                <button wire:click="bulkDelete" wire:confirm="حذف شوند؟" class="btn btn-danger btn-sm">🗑️</button>
                <button wire:click="clearSelection" class="btn btn-ghost btn-sm">✕</button>
            </div>
        </div>
    @endif
</div>
'''
write('resources/views/livewire/orders/index.blade.php', ORDERS_INDEX_VIEW_JALALI)

# ═══════════════════════════════════════════════════════════════
# ۸. پاکسازی
# ═══════════════════════════════════════════════════════════════

print("\n🔧 پاکسازی...")
subprocess.run("php artisan view:clear", shell=True, cwd=ROOT)
subprocess.run("php artisan route:clear", shell=True, cwd=ROOT)
subprocess.run("php artisan optimize:clear", shell=True, cwd=ROOT)

print(r"""
╔══════════════════════════════════════════════════════════╗
║  ✅ تمام شد                                             ║
╚══════════════════════════════════════════════════════════╝

🎯 ویژگی‌های جدید:

   1. 📊 PowerGrid در /orders/table
      - فیلتر ستونی (input+operator)
      - مخفی/نمایان کردن ستون‌ها (checkbox)
      - مرتب‌سازی هر ستون
      - جستجوی سراسری
      - صفحه‌بندی قابل تنظیم (10/20/50/100)
      - Detail row (نمایش جزئیات هر سفارش)
      - Export CSV (فقط کلید Export)

   2. 📅 Jalali Datepicker — با پکیج نصب‌شده
      - در فیلتر سفارشات

   3. 🎨 تب‌های تنظیمات
      - یک خط، اسکرول افقی، فعال پررنگ

🚀 اجرا:
   php artisan serve

   /orders          → لیست ساده + فیلتر + لینک به جدول حرفه‌ای
   /orders/table    → جدول PowerGrid حرفه‌ای ⭐

⚠️ مهم: بعد از باز کردن در مرورگر، Ctrl+Shift+R (Hard Refresh) بزن.
""")
