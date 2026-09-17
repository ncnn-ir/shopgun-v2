#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""ShopGun V2 - Fix UI v4 (real changes)"""

import subprocess
from pathlib import Path
from datetime import datetime

ROOT = Path('/data/data/com.termux/files/home/shopgun-v2.2')

def log(m, k='info'):
    icons = {'info':'ℹ️','ok':'✅','warn':'⚠️','err':'❌'}
    colors = {'info':'\033[96m','ok':'\033[92m','warn':'\033[93m','err':'\033[91m'}
    print(f"{colors[k]} {icons[k]} {m}\033[0m")

def write(rel, content, backup=True):
    full = ROOT / rel
    full.parent.mkdir(parents=True, exist_ok=True)
    if full.exists() and backup:
        full.rename(full.with_suffix(full.suffix + f'.bak-{datetime.now().strftime("%H%M%S")}'))
    full.write_text(content, encoding='utf-8')
    log(f"ساخته شد: {rel}", 'ok')

# ═══════════════════════════════════════════════════════════════
# ۱. CSS جدید — فرم‌های ریسپانسیو + تب‌های درست
# ═══════════════════════════════════════════════════════════════

CSS_APPEND = r'''

/* ═══════════════════════════════════════════════════════════════
   FIX v4 — Responsive Forms, Tabs, Tables
   ═══════════════════════════════════════════════════════════════ */

/* ─── فرم‌های ریسپانسیو (mobile-first) ─── */
.form-grid {
    display: grid;
    gap: 12px;
    grid-template-columns: repeat(12, 1fr);
    margin-bottom: 14px;
}
.form-grid > .col-12 { grid-column: span 12; }
.form-grid > .col-8  { grid-column: span 12; }
.form-grid > .col-6  { grid-column: span 12; }
.form-grid > .col-4  { grid-column: span 12; }
.form-grid > .col-3  { grid-column: span 6;  }

@media (min-width: 640px) {
    .form-grid > .col-8  { grid-column: span 8;  }
    .form-grid > .col-6  { grid-column: span 6;  }
    .form-grid > .col-4  { grid-column: span 6;  }
    .form-grid > .col-3  { grid-column: span 4;  }
}

@media (min-width: 1024px) {
    .form-grid > .col-8  { grid-column: span 8;  }
    .form-grid > .col-6  { grid-column: span 6;  }
    .form-grid > .col-4  { grid-column: span 4;  }
    .form-grid > .col-3  { grid-column: span 3;  }
}

/* ─── فیلد تک‌خطی (label بالای input) ─── */
.field {
    display: flex;
    flex-direction: column;
    gap: 4px;
    min-width: 0;
}
.field > label {
    font-size: 11px;
    font-weight: 700;
    color: var(--primary);
    padding: 0 4px;
}
.field > label .req { color: var(--danger); }
.field > input,
.field > select,
.field > textarea {
    width: 100%;
    min-width: 0;
    background: var(--input-bg, #f5f0e8);
    color: var(--text);
    border: 1.5px solid var(--input-border, #d4c5a9);
    border-radius: 8px;
    padding: 8px 10px;
    font-size: 12.5px;
    font-family: inherit;
    transition: border-color .15s, box-shadow .15s;
    box-sizing: border-box;
}
.field > input:focus,
.field > select:focus,
.field > textarea:focus {
    outline: none;
    border-color: var(--gold);
    box-shadow: 0 0 0 3px rgba(201,168,76,.15);
}
.field > input[dir="ltr"] { font-family: monospace; text-align: left; }
.field textarea { resize: vertical; min-height: 60px; }
.field .hint { font-size: 10px; color: var(--text-light); padding: 0 4px; }
.field .err  { font-size: 10px; color: var(--danger); padding: 0 4px; }

/* ─── ردیف محصول در سفارش (responsive) ─── */
.order-item-row {
    display: grid;
    gap: 8px;
    grid-template-columns: 1fr;
    padding: 10px;
    border: 1.5px solid var(--border);
    border-radius: 10px;
    background: rgba(0,0,0,.02);
    margin-bottom: 10px;
    position: relative;
}
.order-item-row .remove-btn {
    position: absolute;
    top: 6px;
    left: 6px;
    width: 26px;
    height: 26px;
    border-radius: 50%;
    background: rgba(231,76,60,.15);
    color: var(--danger);
    border: none;
    cursor: pointer;
    font-size: 13px;
    display: flex;
    align-items: center;
    justify-content: center;
}
@media (min-width: 768px) {
    .order-item-row {
        grid-template-columns: 110px 2fr 110px 70px 44px 32px;
        align-items: start;
    }
}

/* ─── تب‌های تنظیمات (اسکرول افقی) ─── */
.sg-settings-tabs {
    display: flex !important;
    gap: 6px;
    overflow-x: auto;
    overflow-y: hidden;
    padding: 8px 14px 12px;
    margin-bottom: 14px;
    scrollbar-width: thin;
    -webkit-overflow-scrolling: touch;
    border-bottom: 2px solid var(--border);
    background: transparent;
}
.sg-settings-tabs::-webkit-scrollbar { height: 4px; }
.sg-settings-tabs::-webkit-scrollbar-thumb {
    background: var(--border);
    border-radius: 2px;
}
.sg-settings-tab {
    flex: 0 0 auto;
    padding: 8px 14px;
    border: 1.5px solid var(--border);
    border-radius: 10px;
    background: var(--bg-card);
    font-family: inherit;
    font-size: 12.5px;
    font-weight: 700;
    color: var(--text-light);
    cursor: pointer;
    transition: all .15s;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    white-space: nowrap;
}
.sg-settings-tab:hover {
    border-color: var(--gold);
    color: var(--text);
}
.sg-settings-tab.active {
    background: linear-gradient(135deg, var(--primary), #0d3b5e);
    color: #fff;
    border-color: var(--primary);
    box-shadow: 0 4px 12px rgba(26,82,118,.25);
}
.sg-settings-tab .badge-new {
    background: var(--gold);
    color: #fff;
    font-size: 8px;
    padding: 1px 5px;
    border-radius: 8px;
    font-weight: 800;
}

/* ─── موبایل ─── */
@media (max-width: 768px) {
    .sg-settings-tabs { padding: 6px 10px 10px; }
    .sg-settings-tab { padding: 7px 11px; font-size: 11.5px; }
    .field > input, .field > select, .field > textarea { font-size: 13px; }
}

/* ─── مخفی کردن تب‌های قدیمی ─── */
.sg-tabs-mobile, .sg-tabs-bar { display: none !important; }

/* ─── انتخابگر تاریخ شمسی ─── */
.jalali-picker-wrap {
    position: relative;
    display: flex;
    align-items: center;
}
.jalali-picker-wrap .calendar-icon {
    position: absolute;
    right: 10px;
    pointer-events: none;
    font-size: 14px;
    opacity: .5;
}
.jalali-picker-wrap input {
    padding-right: 34px !important;
    font-family: monospace;
    text-align: center;
    direction: ltr;
}

/* ─── جدول با مرتب‌سازی ─── */
.sg-table th.sortable {
    cursor: pointer;
    user-select: none;
    position: relative;
    padding-left: 20px;
}
.sg-table th.sortable::after {
    content: '⇅';
    position: absolute;
    left: 6px;
    opacity: .3;
    font-size: 10px;
}
.sg-table th.sorted-asc::after  { content: '▲'; opacity: 1; color: var(--gold); }
.sg-table th.sorted-desc::after { content: '▼'; opacity: 1; color: var(--gold); }

/* ─── ردیف فیلتر با تاریخ ─── */
.filter-bar {
    display: grid;
    grid-template-columns: 1fr;
    gap: 8px;
    padding: 10px 14px;
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    margin-bottom: 12px;
}
@media (min-width: 768px) {
    .filter-bar {
        grid-template-columns: 1.5fr 1fr 1fr 1fr auto;
        align-items: end;
    }
}
.filter-bar .field > label { font-size: 10px; }
'''

css_path = ROOT / 'public/css/extra.css'
if css_path.exists():
    content = css_path.read_text(encoding='utf-8')
    if 'FIX v4' not in content:
        css_path.write_text(content + CSS_APPEND, encoding='utf-8')
        log("CSS به extra.css اضافه شد", 'ok')

# ═══════════════════════════════════════════════════════════════
# ۲. کامپوننت تاریخ شمسی (سبک، بدون نیاز به پکیج)
# ═══════════════════════════════════════════════════════════════

JALALI_COMPONENT = r'''@props([
    'model' => null,
    'label' => null,
    'placeholder' => '۱۴۰۳/۰۱/۰۱',
    'hint' => null,
])

@php
    $id = 'jp-' . uniqid();
    $modelAttr = $model ? "wire:model.live=$model" : '';
@endphp

<div class="field">
    @if($label)
        <label for="{{ $id }}">{{ $label }}</label>
    @endif
    <div class="jalali-picker-wrap" wire:ignore x-data="jalaliPicker(@entangle($model ?? 'null'))">
        <input
            id="{{ $id }}"
            type="text"
            x-ref="inp"
            :value="display"
            @click="open()"
            @input="onType($event)"
            @blur="setTimeout(() => close(), 200)"
            placeholder="{{ $placeholder }}"
            dir="ltr"
            autocomplete="off"
            inputmode="numeric"
        />
        <span class="calendar-icon">📅</span>

        <div x-show="isOpen" x-transition.opacity
             @click.outside="close()"
             class="absolute z-[100] mt-1 p-3 bg-base-100 border-2 border-primary rounded-xl shadow-2xl"
             style="top: 100%; right: 0; width: 290px; direction: rtl;">
            <div class="flex items-center justify-between mb-2">
                <button type="button" @click="prevMonth()" class="btn btn-ghost btn-xs">›</button>
                <div class="text-sm font-bold" x-text="monthNames[month-1] + ' ' + fa(year)"></div>
                <button type="button" @click="nextMonth()" class="btn btn-ghost btn-xs">‹</button>
            </div>
            <div class="grid grid-cols-7 gap-1 mb-1 text-[10px] text-center opacity-60">
                <div>ش</div><div>ی</div><div>د</div><div>س</div><div>چ</div><div>پ</div><div>ج</div>
            </div>
            <div class="grid grid-cols-7 gap-1">
                <template x-for="i in firstDay" :key="'b'+i"><div></div></template>
                <template x-for="d in daysInMonth" :key="d">
                    <button type="button" @click="pick(d)"
                            class="w-full aspect-square rounded text-xs font-bold transition"
                            :class="isSelected(d) ? 'bg-primary text-white' : 'hover:bg-base-200'"
                            x-text="fa(d)"></button>
                </template>
            </div>
            <div class="flex justify-between mt-3 pt-2 border-t border-base-300">
                <button type="button" @click="clear()" class="btn btn-ghost btn-xs">پاک</button>
                <button type="button" @click="today()" class="btn btn-primary btn-xs">امروز</button>
            </div>
        </div>
    </div>
    @if($hint)<div class="hint">{{ $hint }}</div>@endif
</div>

@once
@push('scripts')
<script>
document.addEventListener('alpine:init', () => {
    Alpine.data('jalaliPicker', (initial) => ({
        isOpen: false,
        value: initial || '',
        year: 1403,
        month: 1,
        monthNames: ['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور','مهر','آبان','آذر','دی','بهمن','اسفند'],
        monthDays: [31,31,31,31,31,31,30,30,30,30,30,29],
        get display() {
            if (!this.value) return '';
            const p = String(this.value).split('/');
            if (p.length !== 3) return this.value;
            return this.fa(p[0]) + '/' + this.fa(p[1]) + '/' + this.fa(p[2]);
        },
        get daysInMonth() { return this.monthDays[this.month - 1]; },
        get firstDay() { return (this.year + this.month) % 7; },
        init() {
            const t = new Date();
            const j = this.g2j(t.getFullYear(), t.getMonth() + 1, t.getDate());
            this.year = j[0]; this.month = j[1];
            this.$watch('value', v => {
                if (v) {
                    const p = String(v).split('/');
                    if (p.length === 3) { this.year = +p[0] || this.year; this.month = +p[1] || this.month; }
                }
            });
        },
        fa(n) { return String(n).replace(/\d/g, d => '۰۱۲۳۴۵۶۷۸۹'[d]); },
        en(n) { return String(n).replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d)); },
        open() { this.isOpen = true; },
        close() { this.isOpen = false; },
        prevMonth() { this.month--; if (this.month < 1) { this.month = 12; this.year--; } },
        nextMonth() { this.month++; if (this.month > 12) { this.month = 1; this.year++; } },
        isSelected(d) {
            if (!this.value) return false;
            const p = String(this.value).split('/');
            return +p[0] === this.year && +p[1] === this.month && +p[2] === d;
        },
        pick(d) {
            this.value = this.year + '/' + String(this.month).padStart(2, '0') + '/' + String(d).padStart(2, '0');
            this.isOpen = false;
        },
        clear() { this.value = ''; this.isOpen = false; },
        today() {
            const t = new Date();
            const j = this.g2j(t.getFullYear(), t.getMonth() + 1, t.getDate());
            this.value = j[0] + '/' + String(j[1]).padStart(2, '0') + '/' + String(j[2]).padStart(2, '0');
            this.isOpen = false;
        },
        onType(e) {
            const v = this.en(e.target.value).replace(/[^\d/]/g, '');
            e.target.value = this.fa(v);
        },
        g2j(gy, gm, gd) {
            const gdm = [0,31,59,90,120,151,181,212,243,273,304,334];
            let jy = (gy <= 1600) ? 0 : 979;
            gy -= (gy <= 1600) ? 621 : 1600;
            const gy2 = (gm > 2) ? (gy + 1) : gy;
            let days = (365*gy) + Math.floor((gy2+3)/4) - Math.floor((gy2+99)/100) + Math.floor((gy2+399)/400) - 80 + gd + gdm[gm-1];
            jy += 33 * Math.floor(days/12053); days %= 12053;
            jy += 4 * Math.floor(days/1461); days %= 1461;
            if (days > 365) { jy += Math.floor((days-1)/365); days = (days-1)%365; }
            const jm = (days < 186) ? 1 + Math.floor(days/31) : 7 + Math.floor((days-186)/30);
            const jd = 1 + ((days < 186) ? (days%31) : ((days-186)%30));
            return [jy, jm, jd];
        },
    }));
});
</script>
@endpush
@endonce
'''

write('resources/views/components/ui/jalali-date.blade.php', JALALI_COMPONENT)

# ═══════════════════════════════════════════════════════════════
# ۳. بازنویسی View تنظیمات — تب‌ها + نمایش محتوا
# ═══════════════════════════════════════════════════════════════

SETTINGS_VIEW = r'''<div style="padding: 0 0 18px" dir="rtl">

    <div style="padding: 0 18px 14px">
        <h1 style="font-size:20px;font-weight:700">⚙️ تنظیمات</h1>
    </div>

    {{-- ═══ تب‌ها — یک خط، اسکرول افقی ═══ --}}
    <div class="sg-settings-tabs">
        @foreach([
            'general'     => ['⚙️', 'عمومی', false],
            'appearance'  => ['🎨', 'ظاهر', false],
            'commerce'    => ['🔌', 'اتصالات', false],
            'certificate' => ['💎', 'شناسنامه', false],
            'label'       => ['🏷️', 'برچسب', false],
            'labels'      => ['🎨', 'ویرایشگر برچسب', true],
            'assets'      => ['🖼️', 'تصاویر', false],
            'stones'      => ['💠', 'سنگ/فلز', false],
            'logs'        => ['📜', 'لاگ', false],
            'monitor'     => ['📊', 'رصد API', false],
            'backup'      => ['💾', 'پشتیبان', false],
            'health'      => ['🩺', 'سلامت', true],
        ] as $key => $meta)
            <button wire:click="setTab('{{ $key }}')"
                    class="sg-settings-tab {{ $tab === $key ? 'active' : '' }}">
                <span>{{ $meta[0] }}</span>
                <span>{{ $meta[1] }}</span>
                @if($meta[2])<span class="badge-new">🆕</span>@endif
            </button>
        @endforeach
    </div>

    {{-- ═══ محتوای تب‌ها ═══ --}}
    <div style="padding: 0 14px">

        {{-- ─────── عمومی ─────── --}}
        @if($tab === 'general')
            <div class="sg-settings-card">
                <h3>اطلاعات فروشگاه</h3>
                <div class="form-grid">
                    <div class="field col-6">
                        <label>🏪 نام فروشگاه</label>
                        <input type="text" wire:model="shop_name" />
                    </div>
                    <div class="field col-6">
                        <label>📱 تلفن</label>
                        <input type="text" wire:model="shop_phone" dir="ltr" />
                    </div>
                    <div class="field col-12">
                        <label>📍 آدرس</label>
                        <textarea wire:model="shop_address" rows="2"></textarea>
                    </div>
                    <div class="field col-4">
                        <label>📮 کدپستی</label>
                        <input type="text" wire:model="shop_postal" dir="ltr" />
                    </div>
                    <div class="field col-4">
                        <label>📧 ایمیل</label>
                        <input type="email" wire:model="shop_email" dir="ltr" />
                    </div>
                    <div class="field col-4">
                        <label>💵 واحد پول</label>
                        <input type="text" wire:model="currency" />
                    </div>
                </div>
                <div style="display:flex;justify-content:flex-end;padding-top:10px;border-top:1px solid var(--border)">
                    <button wire:click="saveGeneral" class="btn btn-success">💾 ذخیره</button>
                </div>
            </div>
        @endif

        {{-- ─────── ظاهر ─────── --}}
        @if($tab === 'appearance')
            <div class="sg-settings-card">
                <h3>ظاهر برنامه</h3>
                <div class="form-grid">
                    <div class="field col-6">
                        <label>🌓 تم</label>
                        <div class="grid grid-cols-2 gap-2">
                            @foreach(['light'=>'☀️ روشن','dark'=>'🌙 تیره'] as $k => $v)
                                <button type="button" wire:click="$set('theme','{{ $k }}')"
                                        class="btn {{ $theme === $k ? 'btn-primary' : 'btn-outline' }} btn-sm">{{ $v }}</button>
                            @endforeach
                        </div>
                    </div>
                    <div class="field col-6">
                        <label>📐 تراکم</label>
                        <div class="grid grid-cols-3 gap-2">
                            @foreach(['compact'=>'فشرده','normal'=>'معمولی','comfortable'=>'راحت'] as $k => $v)
                                <button type="button" wire:click="$set('density','{{ $k }}')"
                                        class="btn {{ $density === $k ? 'btn-primary' : 'btn-outline' }} btn-xs">{{ $v }}</button>
                            @endforeach
                        </div>
                    </div>
                    <div class="field col-6">
                        <label>🎨 رنگ اصلی</label>
                        <input type="color" wire:model.live="primary_color" style="height:42px;padding:4px;cursor:pointer" />
                    </div>
                    <div class="field col-6">
                        <label>✨ رنگ تاکیدی</label>
                        <input type="color" wire:model.live="accent_color" style="height:42px;padding:4px;cursor:pointer" />
                    </div>
                    <div class="field col-12">
                        <label>🔤 فونت</label>
                        <select wire:model.live="font_family">
                            <option value="Vazirmatn">وزیرمتن (پیش‌فرض)</option>
                            <option value="Tahoma">تاهوما</option>
                            <option value="system-ui">سیستم</option>
                            <option value="Arial">Arial</option>
                        </select>
                    </div>
                </div>
                <div style="display:flex;justify-content:flex-end;padding-top:10px;border-top:1px solid var(--border)">
                    <button wire:click="saveAppearance" class="btn btn-success">💾 ذخیره</button>
                </div>
            </div>
        @endif

        {{-- ─────── کامرس ─────── --}}
        @if($tab === 'commerce')
            <div class="sg-settings-card">
                <h3>🔌 اتصال به WooCommerce</h3>
                <div class="form-grid">
                    <div class="field col-12">
                        <label>🌐 آدرس سایت</label>
                        <input type="text" wire:model="commerce_url" dir="ltr" placeholder="https://yoursite.com" />
                    </div>
                    <div class="field col-6">
                        <label>🔑 Consumer Key</label>
                        <input type="text" wire:model="commerce_key" dir="ltr" />
                    </div>
                    <div class="field col-6">
                        <label>🔐 Consumer Secret</label>
                        <input type="password" wire:model="commerce_secret" dir="ltr" />
                    </div>
                </div>
                @if(!empty($commerce_test_result))
                    <div style="padding:12px;border-radius:10px;margin:12px 0;background:{{ $commerce_test_result['ok'] ? 'rgba(39,174,96,.1)' : 'rgba(231,76,60,.1)' }};color:{{ $commerce_test_result['ok'] ? 'var(--success)' : 'var(--danger)' }};font-weight:700">
                        {{ $commerce_test_result['ok'] ? '✅' : '❌' }} {{ $commerce_test_result['message'] }}
                    </div>
                @endif
                <div style="display:flex;gap:6px;flex-wrap:wrap;padding-top:10px;border-top:1px solid var(--border)">
                    <button wire:click="saveCommerce" class="btn btn-primary">💾 ذخیره</button>
                    <button wire:click="testCommerce" class="btn btn-secondary">🔌 تست اتصال</button>
                    <button wire:click="syncProducts" class="btn btn-success">📥 سینک محصولات</button>
                </div>
            </div>
        @endif

        {{-- ─────── شناسنامه ─────── --}}
        @if($tab === 'certificate')
            <div class="sg-settings-card">
                <h3>📏 اندازه شناسنامه</h3>
                <div class="form-grid">
                    <div class="field col-6">
                        <label>📐 عرض (cm)</label>
                        <input type="number" step="0.1" wire:model="cert_width" dir="ltr" />
                    </div>
                    <div class="field col-6">
                        <label>📐 ارتفاع (cm)</label>
                        <input type="number" step="0.1" wire:model="cert_height" dir="ltr" />
                    </div>
                </div>
                <div style="display:flex;gap:6px;margin-bottom:14px;flex-wrap:wrap">
                    <button wire:click="setCertPreset(6.5,6.5)" class="btn btn-outline btn-sm">۶.۵×۶.۵</button>
                    <button wire:click="setCertPreset(7,7)" class="btn btn-outline btn-sm">۷×۷</button>
                    <button wire:click="setCertPreset(8,6)" class="btn btn-outline btn-sm">۸×۶</button>
                </div>
                <div style="display:flex;justify-content:flex-end;padding-top:10px;border-top:1px solid var(--border)">
                    <button wire:click="saveCertificate" class="btn btn-success">💾 ذخیره</button>
                </div>
            </div>
        @endif

        {{-- ─────── برچسب ─────── --}}
        @if($tab === 'label')
            <div class="sg-settings-card">
                <h3>📐 اندازه برچسب</h3>
                <div class="form-grid">
                    <div class="field col-6">
                        <label>📐 عرض (mm)</label>
                        <input type="number" wire:model="label_width" dir="ltr" />
                    </div>
                    <div class="field col-6">
                        <label>📐 ارتفاع (mm)</label>
                        <input type="number" wire:model="label_height" dir="ltr" />
                    </div>
                </div>
                <div style="display:flex;justify-content:flex-end;padding-top:10px;border-top:1px solid var(--border)">
                    <button wire:click="saveLabel" class="btn btn-success">💾 ذخیره</button>
                </div>
            </div>
        @endif

        {{-- ─────── ویرایشگر برچسب ─────── --}}
        @if($tab === 'labels')
            <livewire:settings.labels />
        @endif

        {{-- ─────── تصاویر ─────── --}}
        @if($tab === 'assets')
            <div class="sg-settings-card">
                <h3>🖼️ پس‌زمینه شناسنامه</h3>
                @if($bg_image)
                    <div style="margin-bottom:12px;display:flex;gap:8px;align-items:center;flex-wrap:wrap">
                        <img src="{{ $bg_image }}" style="max-width:120px;border-radius:10px;border:2px solid var(--gold)">
                        <button wire:click="removeBg" class="btn btn-danger btn-sm">حذف</button>
                    </div>
                @endif
                <input type="file" wire:model="bg_image" accept="image/*" class="form-control">
            </div>
        @endif

        {{-- ─────── سنگ/فلز ─────── --}}
        @if($tab === 'stones')
            <div class="sg-settings-card">
                <h3>💎 سنگ‌های قیمتی ({{ \App\Support\PersianNumber::toFa(count($stones_list)) }})</h3>
                <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(90px,1fr));gap:8px;margin-bottom:14px">
                    @foreach($stones_list as $s)
                        <div style="background:var(--bg-card);border:2px solid var(--border);border-radius:10px;padding:8px 4px;text-align:center;position:relative">
                            <button wire:click="removeStone({{ $s['id'] }})" wire:confirm="حذف شود؟"
                                    style="position:absolute;top:-6px;left:-6px;width:20px;height:20px;border-radius:50%;background:var(--danger);color:#fff;border:none;cursor:pointer;font-size:11px">✕</button>
                            <div style="font-size:24px">{{ $s['icon'] ?? '💎' }}</div>
                            <div style="font-size:10px;font-weight:700;margin-top:4px">{{ $s['name'] }}</div>
                            <div style="font-size:9px;opacity:.6">{{ $s['origin'] ?? '' }}</div>
                        </div>
                    @endforeach
                </div>
                <h3 style="margin-top:20px">➕ افزودن سنگ</h3>
                <div class="form-grid">
                    <div class="field col-6">
                        <label>نام فارسی</label>
                        <input type="text" wire:model="new_stone_name" />
                    </div>
                    <div class="field col-6">
                        <label>نام انگلیسی</label>
                        <input type="text" wire:model="new_stone_en" dir="ltr" />
                    </div>
                </div>
                <button wire:click="addStone" class="btn btn-primary">➕ افزودن</button>

                <h3 style="margin-top:30px">⚙️ فلزات ({{ \App\Support\PersianNumber::toFa(count($metals_list)) }})</h3>
                @foreach($metals_list as $m)
                    <div style="padding:8px 12px;background:var(--bg-soft);border-radius:8px;margin-bottom:6px;display:flex;justify-content:space-between;align-items:center">
                        <span>⚙️ <strong>{{ $m['name'] }}</strong> — {{ $m['carat'] ?? '-' }}</span>
                        <button wire:click="removeMetal({{ $m['id'] }})" wire:confirm="حذف شود؟" class="btn btn-danger btn-sm">حذف</button>
                    </div>
                @endforeach
            </div>
        @endif

        {{-- ─────── لاگ ─────── --}}
        @if($tab === 'logs')
            <div class="sg-settings-card">
                <h3>📜 لاگ تغییرات</h3>
                <div style="display:flex;gap:8px;margin-bottom:14px;flex-wrap:wrap">
                    <input type="text" wire:model.live.debounce.400ms="log_search" placeholder="🔍 جستجو..." style="flex:1;min-width:200px" class="form-control">
                    <button wire:click="clearLogs" wire:confirm="پاک شوند؟" class="btn btn-danger btn-sm">🗑️</button>
                </div>
                <div style="max-height:500px;overflow-y:auto">
                    @forelse($logs as $log)
                        <div style="padding:10px 12px;border-bottom:1px solid var(--border);font-size:11.5px">
                            <strong>{{ $log['description'] }}</strong>
                            <span style="opacity:.6"> · {{ $log['event'] }}</span>
                            <div style="font-family:monospace;font-size:10px;opacity:.5;margin-top:2px">
                                {{ \App\Support\PersianDate::format($log['created_at'], 'Y/m/d H:i') }} · {{ $log['causer'] }}
                            </div>
                        </div>
                    @empty
                        <p style="text-align:center;padding:20px;opacity:.5">لاگی نیست</p>
                    @endforelse
                </div>
            </div>
        @endif

        {{-- ─────── رصد API ─────── --}}
        @if($tab === 'monitor')
            <div class="sg-settings-card">
                <h3>📊 رصد API</h3>
                <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:14px">
                    <div style="padding:12px;background:rgba(41,128,185,.1);border-radius:10px;text-align:center">
                        <div style="font-size:20px;font-weight:800;color:var(--primary)">{{ \App\Support\PersianNumber::toFa($monitor_stats['total'] ?? 0) }}</div>
                        <div style="font-size:11px;opacity:.7">کل</div>
                    </div>
                    <div style="padding:12px;background:rgba(39,174,96,.1);border-radius:10px;text-align:center">
                        <div style="font-size:20px;font-weight:800;color:var(--success)">{{ \App\Support\PersianNumber::toFa($monitor_stats['today'] ?? 0) }}</div>
                        <div style="font-size:11px;opacity:.7">امروز</div>
                    </div>
                    <div style="padding:12px;background:rgba(231,76,60,.1);border-radius:10px;text-align:center">
                        <div style="font-size:20px;font-weight:800;color:var(--danger)">{{ \App\Support\PersianNumber::toFa($monitor_stats['errors'] ?? 0) }}</div>
                        <div style="font-size:11px;opacity:.7">خطا</div>
                    </div>
                </div>
                <div style="display:flex;gap:8px;margin-bottom:14px">
                    <input type="text" wire:model.live.debounce.400ms="monitor_filter" placeholder="🔍 فیلتر..." style="flex:1" class="form-control">
                    <button wire:click="refreshMonitor" class="btn btn-outline btn-sm">🔄</button>
                    <button wire:click="clearMonitor" wire:confirm="پاک شوند؟" class="btn btn-danger btn-sm">🗑️</button>
                </div>
                <div style="max-height:500px;overflow-y:auto">
                    @forelse($monitor_logs as $log)
                        <div style="padding:8px 10px;border-bottom:1px solid var(--border);font-size:11px">
                            <div style="display:flex;gap:8px;align-items:center">
                                <span style="padding:2px 6px;border-radius:6px;background:{{ ($log['status_code'] ?? 0) >= 200 && ($log['status_code'] ?? 0) < 300 ? 'var(--success)' : 'var(--danger)' }};color:#fff;font-weight:700;font-size:10px;font-family:monospace">{{ $log['status_code'] ?? '—' }}</span>
                                <span style="font-family:monospace;font-weight:700">{{ $log['method'] }}</span>
                                <span style="margin-right:auto;font-family:monospace;opacity:.5;font-size:10px">{{ $log['created_at'] }}</span>
                            </div>
                            <div style="font-family:monospace;font-size:10px;opacity:.7;overflow:hidden;text-overflow:ellipsis" dir="ltr">{{ $log['url'] }}</div>
                        </div>
                    @empty
                        <p style="text-align:center;padding:20px;opacity:.5">لاگی نیست</p>
                    @endforelse
                </div>
            </div>
        @endif

        {{-- ─────── پشتیبان ─────── --}}
        @if($tab === 'backup')
            <div class="sg-settings-card">
                <h3>💾 پشتیبان‌گیری</h3>
                <div style="display:flex;gap:6px;flex-wrap:wrap">
                    <button wire:click="createBackup" class="btn btn-primary">➕ پشتیبان جدید</button>
                    <button wire:click="exportJson" class="btn btn-secondary">📥 خروجی JSON</button>
                </div>
                <h3 style="margin-top:20px">📊 اطلاعات سیستم</h3>
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
                    @foreach([
                        ['🖥️', 'PHP', $stats['php']],
                        ['⚡', 'Laravel', $stats['laravel']],
                        ['📦', 'سفارشات', \App\Support\PersianNumber::toFa($stats['orders'])],
                        ['👥', 'مشتریان', \App\Support\PersianNumber::toFa($stats['customers'])],
                        ['💎', 'شناسنامه‌ها', \App\Support\PersianNumber::toFa($stats['certificates'])],
                        ['🛍️', 'محصولات', \App\Support\PersianNumber::toFa($stats['products'])],
                    ] as $item)
                        <div style="padding:10px;background:var(--bg-soft);border-radius:8px;display:flex;justify-content:space-between;font-size:12px">
                            <span>{{ $item[0] }} {{ $item[1] }}</span>
                            <strong style="font-family:monospace">{{ $item[2] }}</strong>
                        </div>
                    @endforeach
                </div>
            </div>
        @endif

        {{-- ─────── سلامت ─────── --}}
        @if($tab === 'health')
            <livewire:settings.health />
        @endif
    </div>
</div>
'''

write('resources/views/livewire/settings/index.blade.php', SETTINGS_VIEW)

# ═══════════════════════════════════════════════════════════════
# ۴. بازنویسی فرم Modal سفارش — موبایل-فرندلی
# ═══════════════════════════════════════════════════════════════

ORDER_FORM_MODAL = r'''<div>
@if($show)
<div class="sg-modal-overlay active" wire:key="ofm-{{ $orderId ?? 'new' }}" @keydown.escape.window="$wire.close()">
    <div class="sg-modal" style="max-width:900px">
        <div class="sg-modal-header">
            <h2>{{ $mode === 'edit' ? '✏️ ویرایش سفارش #'.$orderId : '📦 سفارش جدید' }}</h2>
            <button wire:click="close" class="sg-modal-close">✕</button>
        </div>

        <div class="sg-modal-body">

            {{-- ═══ اطلاعات مشتری ═══ --}}
            <div style="font-size:12px;font-weight:700;color:var(--primary);margin-bottom:10px;padding-bottom:6px;border-bottom:1px solid var(--border)">
                👤 اطلاعات مشتری
            </div>

            <div class="form-grid">
                <div class="field col-6" style="position:relative">
                    <label>📱 تلفن <span class="req">*</span></label>
                    <input type="text" wire:model.live.debounce.400ms="phone" dir="ltr" autocomplete="off" placeholder="09151234567" />
                    @if(!empty($phoneSuggestions))
                        <div style="position:absolute;top:100%;right:0;left:0;margin-top:4px;background:var(--bg-card);border:2px solid var(--gold);border-radius:10px;box-shadow:0 8px 24px rgba(0,0,0,.15);z-index:50;max-height:240px;overflow-y:auto">
                            @foreach($phoneSuggestions as $s)
                                <div wire:click="selectPhoneSuggestion({{ $s['id'] }})"
                                     style="padding:10px 12px;cursor:pointer;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;gap:8px;align-items:center">
                                    <div style="flex:1;min-width:0">
                                        <div style="font-weight:700;font-size:12px">{{ $s['name'] }}</div>
                                        <div style="font-family:monospace;font-size:10px;opacity:.6" dir="ltr">{{ $s['phone'] }}</div>
                                    </div>
                                    @if($s['orders_count'] > 0)
                                        <span style="background:rgba(201,168,76,.15);color:var(--gold-dark);padding:2px 8px;border-radius:8px;font-size:10px;font-weight:700">
                                            {{ \App\Support\PersianNumber::toFa($s['orders_count']) }}
                                        </span>
                                    @endif
                                </div>
                            @endforeach
                        </div>
                    @endif
                </div>

                <div class="field col-6">
                    <label>👤 نام مشتری <span class="req">*</span></label>
                    <input type="text" wire:model="customerName" />
                </div>

                <div class="field col-8">
                    <label>📍 آدرس</label>
                    <input type="text" wire:model="address" />
                </div>

                <div class="field col-4">
                    <label>📮 کدپستی</label>
                    <input type="text" wire:model="postalCode" dir="ltr" />
                </div>
            </div>

            {{-- ═══ محصولات ═══ --}}
            <div style="font-size:12px;font-weight:700;color:var(--primary);margin:14px 0 10px;padding-bottom:6px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center">
                <span>🛍️ محصولات</span>
                <button type="button" wire:click="addItem" class="btn btn-outline btn-sm">➕ افزودن</button>
            </div>

            @foreach($items as $i => $item)
                <div class="order-item-row" wire:key="item-{{ $i }}">
                    <button type="button" class="remove-btn" wire:click="removeItem({{ $i }})">✕</button>

                    {{-- SKU --}}
                    <div class="field" style="position:relative">
                        <label>SKU</label>
                        <input type="text" wire:model.live.debounce.400ms="items.{{ $i }}.sku" dir="ltr" autocomplete="off" placeholder="جستجو...">
                        @if($activeSkuIndex === $i && !empty($skuSuggestions))
                            <div style="position:absolute;top:100%;right:0;left:0;margin-top:4px;background:var(--bg-card);border:2px solid var(--gold);border-radius:10px;box-shadow:0 8px 24px rgba(0,0,0,.15);z-index:60;max-height:240px;overflow-y:auto">
                                @foreach($skuSuggestions as $p)
                                    <div wire:click="selectSkuProduct({{ $p['id'] }})"
                                         style="padding:8px 10px;cursor:pointer;border-bottom:1px solid var(--border);font-size:11px">
                                        <div style="font-weight:700">{{ $p['name'] }}</div>
                                        <div style="font-family:monospace;font-size:10px;opacity:.6" dir="ltr">{{ $p['sku'] }}</div>
                                    </div>
                                @endforeach
                            </div>
                        @endif
                    </div>

                    {{-- Title --}}
                    <div class="field">
                        <label>عنوان <span class="req">*</span></label>
                        <input type="text" wire:model="items.{{ $i }}.title">
                    </div>

                    {{-- Price --}}
                    <div class="field">
                        <label>قیمت</label>
                        <input type="number" wire:model.live="items.{{ $i }}.price" dir="ltr" min="0">
                    </div>

                    {{-- Qty --}}
                    <div class="field">
                        <label>تعداد</label>
                        <input type="number" wire:model.live="items.{{ $i }}.quantity" dir="ltr" min="1">
                    </div>

                    {{-- Cert --}}
                    <div class="field">
                        <label>شناسنامه</label>
                        <label style="display:flex;align-items:center;justify-content:center;height:36px;cursor:pointer;background:var(--bg-soft);border-radius:8px">
                            <input type="checkbox" wire:model="items.{{ $i }}.certificate_needed" style="width:20px;height:20px;accent-color:var(--gold)">
                        </label>
                    </div>

                    {{-- Spacer --}}
                    <div></div>
                </div>
            @endforeach

            {{-- جمع کل --}}
            <div style="display:flex;justify-content:space-between;padding:12px 16px;background:linear-gradient(135deg,rgba(201,168,76,.12),rgba(201,168,76,.05));border:2px solid var(--gold);border-radius:12px;margin-top:10px;font-weight:700">
                <span>💰 جمع کل:</span>
                <span style="font-family:monospace">{{ number_format($this->total) }} تومان</span>
            </div>

            {{-- ═══ مالی ═══ --}}
            <div style="font-size:12px;font-weight:700;color:var(--primary);margin:16px 0 10px;padding-bottom:6px;border-bottom:1px solid var(--border)">
                💰 اطلاعات مالی
            </div>

            <div class="form-grid">
                <div class="field col-3">
                    <label>💰 بیمه</label>
                    <input type="text" wire:model="insurance" dir="ltr">
                </div>
                <div class="field col-3">
                    <label>📦 ارسال</label>
                    <input type="text" wire:model="shipping" dir="ltr">
                </div>
                <div class="field col-3">
                    <label>🏷️ تخفیف</label>
                    <input type="text" wire:model="discount" dir="ltr">
                </div>
                <div class="field col-3">
                    <label>🚦 وضعیت</label>
                    <select wire:model="status">
                        <option value="pending">📝 ثبت سفارش</option>
                        <option value="final-check">🔍 چک نهایی</option>
                        <option value="courier">🚚 تحویل مامور</option>
                    </select>
                </div>
                <div class="field col-6">
                    <label>🌐 کانال</label>
                    <select wire:model="channelId">
                        <option value="">— انتخاب —</option>
                        @foreach($channels as $ch)
                            <option value="{{ $ch->id }}">{{ $ch->icon ?? '' }} {{ $ch->name }}</option>
                        @endforeach
                    </select>
                </div>
                <div class="field col-6">
                    <label>📝 یادداشت</label>
                    <input type="text" wire:model="notes">
                </div>
            </div>
        </div>

        <div class="sg-modal-footer">
            <button wire:click="close" class="btn btn-outline">انصراف</button>
            <button wire:click="save" wire:loading.attr="disabled" class="btn btn-success">
                <span wire:loading.remove wire:target="save">✅ {{ $mode === 'edit' ? 'ویرایش' : 'ثبت' }}</span>
                <span wire:loading wire:target="save">⏳...</span>
            </button>
        </div>
    </div>
</div>
@endif
</div>
'''

write('resources/views/livewire/orders/form-modal.blade.php', ORDER_FORM_MODAL)

# ═══════════════════════════════════════════════════════════════
# ۵. بازنویسی Create سفارش — موبایل-فرندلی
# ═══════════════════════════════════════════════════════════════

ORDER_CREATE = r'''<div class="p-4 md:p-6 max-w-4xl mx-auto" dir="rtl">
    <div class="flex items-center gap-3 mb-6">
        <a href="{{ route('orders.index') }}" class="btn btn-ghost btn-sm">→</a>
        <h1 class="text-xl md:text-2xl font-bold">➕ سفارش جدید</h1>
    </div>

    <div class="sg-settings-card">

        {{-- ═══ مشتری ═══ --}}
        <h3>👤 اطلاعات مشتری</h3>

        <div class="form-grid">
            <div class="field col-8">
                <label>📱 تلفن مشتری <span class="req">*</span></label>
                <livewire:components.phone-search wire:model="phone" wire:key="phone-{{ rand() }}" />
                @if($customerFound)
                    <div class="hint" style="color:var(--success)">✅ مشتری موجود — ID: {{ $existingCustomerId }}</div>
                @elseif(strlen(preg_replace('/\D/', '', $phone)) >= 10)
                    <div class="hint" style="color:var(--info)">🆕 مشتری جدید ساخته می‌شود</div>
                @endif
                @error('phone') <div class="err">{{ $message }}</div> @enderror
            </div>

            <div class="field col-4">
                <label>👤 نام</label>
                <input type="text" wire:model="customerName" />
            </div>

            <div class="field col-8">
                <label>📍 آدرس</label>
                <input type="text" wire:model="address" />
            </div>

            <div class="field col-4">
                <label>📮 کدپستی</label>
                <input type="text" wire:model="postalCode" dir="ltr" />
            </div>
        </div>

        {{-- ═══ وضعیت و کانال ═══ --}}
        <h3 style="margin-top:20px">🚦 وضعیت و کانال</h3>

        <div class="form-grid">
            <div class="field col-6">
                <label>📊 وضعیت</label>
                <div style="display:flex;gap:6px;flex-wrap:wrap">
                    @foreach(['pending' => '📝 ثبت', 'final-check' => '🔍 چک', 'courier' => '🚚 تحویل'] as $k => $v)
                        <button type="button" wire:click="$set('status', '{{ $k }}')"
                                class="btn btn-sm {{ $status === $k ? 'btn-primary' : 'btn-outline' }}">{{ $v }}</button>
                    @endforeach
                </div>
            </div>

            <div class="field col-6">
                <label>🌐 کانال</label>
                <div style="display:flex;gap:6px;flex-wrap:wrap">
                    @foreach($channels as $c)
                        <button type="button" wire:click="$set('channelId', {{ $c->id }})"
                                class="btn btn-sm {{ $channelId === $c->id ? 'btn-primary' : 'btn-outline' }}">{{ $c->icon }} {{ $c->name }}</button>
                    @endforeach
                </div>
            </div>

            <div class="field col-4">
                <label>💰 بیمه</label>
                <input type="text" wire:model="insurance" dir="ltr" />
            </div>

            <div class="field col-8">
                <label style="display:flex;align-items:center;gap:6px;cursor:pointer">
                    <input type="checkbox" wire:model="invoiceNeeded" style="width:18px;height:18px;accent-color:var(--gold)">
                    <span>📄 نیاز به فاکتور</span>
                </label>
            </div>
        </div>

        {{-- ═══ محصولات ═══ --}}
        <h3 style="margin-top:20px;display:flex;justify-content:space-between;align-items:center">
            <span>🛍️ محصولات</span>
            <button type="button" wire:click="addItem" class="btn btn-outline btn-sm">➕ افزودن</button>
        </h3>

        @foreach($items as $idx => $it)
            <div class="order-item-row" wire:key="item-{{ $idx }}">
                <button type="button" class="remove-btn"
                        wire:click="removeItem({{ $idx }})"
                        wire:confirm="این ردیف حذف شود؟">✕</button>

                <div class="field">
                    <label>SKU</label>
                    <input type="text" wire:model="items.{{ $idx }}.sku" dir="ltr" />
                </div>

                <div class="field">
                    <label>عنوان</label>
                    <input type="text" wire:model="items.{{ $idx }}.title" />
                </div>

                <div class="field">
                    <label>قیمت</label>
                    <input type="number" wire:model.live.debounce.500ms="items.{{ $idx }}.price" dir="ltr" min="0" />
                </div>

                <div class="field">
                    <label>تعداد</label>
                    <input type="number" wire:model.live="items.{{ $idx }}.qty" dir="ltr" min="1" />
                </div>

                <div class="field">
                    <label>شناسنامه</label>
                    <label style="display:flex;align-items:center;justify-content:center;height:36px;cursor:pointer;background:var(--bg-soft);border-radius:8px">
                        <input type="checkbox" wire:model="items.{{ $idx }}.cert" style="width:20px;height:20px;accent-color:var(--gold)">
                    </label>
                </div>
                <div></div>
            </div>
        @endforeach

        {{-- ═══ یادداشت ═══ --}}
        <div class="form-grid" style="margin-top:20px">
            <div class="field col-12">
                <label>📝 یادداشت</label>
                <textarea wire:model="notes" rows="2"></textarea>
            </div>
        </div>

        {{-- ═══ دکمه‌ها ═══ --}}
        <div style="display:flex;justify-content:flex-end;gap:8px;padding-top:14px;border-top:1px solid var(--border);margin-top:14px;flex-wrap:wrap">
            <a href="{{ route('orders.index') }}" class="btn btn-ghost">انصراف</a>
            <button wire:click="save" wire:loading.attr="disabled" class="btn btn-success">
                <span wire:loading.remove wire:target="save">✅ ثبت سفارش</span>
                <span wire:loading wire:target="save">⏳...</span>
            </button>
        </div>
    </div>
</div>
'''

write('resources/views/livewire/orders/create.blade.php', ORDER_CREATE)

# ═══════════════════════════════════════════════════════════════
# ۶. فیلتر تاریخ شمسی در Orders Index
# ═══════════════════════════════════════════════════════════════

ORDERS_INDEX = r'''<div dir="rtl">

    {{-- ═══ فیلترها ═══ --}}
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

            <x-ui.jalali-date model="dateFrom" label="📅 از تاریخ" />
            <x-ui.jalali-date model="dateTo"   label="📅 تا تاریخ" />

            <div class="field">
                <label style="opacity:0">عملیات</label>
                <div style="display:flex;gap:6px">
                    <button wire:click="clearFilters" class="btn btn-outline btn-sm" title="پاک کردن">✕</button>
                    <button onclick="Livewire.dispatch('open-order-form')" class="btn btn-primary btn-sm">➕ جدید</button>
                </div>
            </div>
        </div>

        {{-- ═══ نوار انتخاب گروهی ═══ --}}
        @if(count($selected) > 0)
            <div style="background:linear-gradient(135deg,rgba(201,168,76,.15),rgba(201,168,76,.05));border:2px dashed var(--gold);border-radius:12px;padding:10px 14px;margin-bottom:12px;display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:8px">
                <span style="font-weight:700;color:var(--gold-dark)">
                    {{ \App\Support\PersianNumber::toFa(count($selected)) }} مورد انتخاب شده
                </span>
                <div style="display:flex;gap:6px;flex-wrap:wrap">
                    <button wire:click="bulkStatus('pending')" class="btn btn-outline btn-sm">📝 ثبت</button>
                    <button wire:click="bulkStatus('final-check')" class="btn btn-outline btn-sm">🔍 چک</button>
                    <button wire:click="bulkStatus('courier')" class="btn btn-outline btn-sm">🚚 مامور</button>
                    <button wire:click="bulkDelete" wire:confirm="حذف شوند؟" class="btn btn-danger btn-sm">🗑️ حذف</button>
                    <button wire:click="clearSelection" class="btn btn-ghost btn-sm">✕</button>
                </div>
            </div>
        @endif
    </div>

    {{-- ═══ جدول ═══ --}}
    <div class="sg-table-container">
        <div class="sg-table-header">
            <h2>📦 سفارشات
                <span style="background:var(--gold);color:var(--primary);padding:2px 10px;border-radius:20px;font-size:10.5px;font-weight:700;margin-right:6px">
                    {{ \App\Support\PersianNumber::toFa($orders->total()) }}
                </span>
            </h2>
            <div style="display:flex;gap:4px">
                <button wire:click="sortBy('id')" class="btn btn-ghost btn-xs">مرتب: {{ $sortField === 'id' ? ($sortDirection === 'asc' ? '↑' : '↓') : '⇅' }}</button>
            </div>
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
                                <span class="sg-status-badge {{ $order->status ?? 'pending' }}" wire:click="cycleStatus({{ $order->id }})">
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
</div>
'''

write('resources/views/livewire/orders/index.blade.php', ORDERS_INDEX)

# ═══════════════════════════════════════════════════════════════
# ۷. اضافه کردن sortBy و clearFilters به Orders Index.php
# ═══════════════════════════════════════════════════════════════

orders_php = ROOT / 'app/Livewire/Orders/Index.php'
if orders_php.exists():
    content = orders_php.read_text(encoding='utf-8')

    if 'sortBy' not in content:
        # اضافه کردن پراپرتی sort
        content = content.replace(
            "public string \$dateFrom = '';",
            "public string \$dateFrom = '';\n    public string \$sortField = 'id';\n    public string \$sortDirection = 'desc';"
        )

        # اضافه کردن متدها
        methods = '''
    public function sortBy(string $field): void
    {
        if ($this->sortField === $field) {
            $this->sortDirection = $this->sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            $this->sortField = $field;
            $this->sortDirection = 'asc';
        }
    }

    public function clearFilters(): void
    {
        $this->search = '';
        $this->filterStatus = '';
        $this->filterChannel = null;
        $this->dateFrom = '';
        $this->dateTo = '';
        $this->resetPage();
    }
'''
        content = content.replace('    public function render()', methods + '\n    public function render()')

        # اضافه کردن sort به query
        content = content.replace(
            '->latest(\'id\')',
            '->orderBy($this->sortField, $this->sortDirection)'
        )

        orders_php.write_text(content, encoding='utf-8')
        log("Orders/Index.php بروزرسانی شد", 'ok')

# ═══════════════════════════════════════════════════════════════
# ۸. پاکسازی
# ═══════════════════════════════════════════════════════════════

print("\n🔧 پاکسازی...")
subprocess.run("php artisan view:clear", shell=True, cwd=ROOT)
subprocess.run("php artisan optimize:clear", shell=True, cwd=ROOT)

print(f"""
╔══════════════════════════════════════════════════╗
║  ✅ UI واقعی اعمال شد                             ║
╚══════════════════════════════════════════════════╝

🎯 تغییرات قابل مشاهده:

   ✅ فرم سفارش: input‌ها کنار هم (چند ستونه) در موبایل
   ✅ فرم Create سفارش: بازنویسی کامل موبایل-فرندلی
   ✅ تب‌های تنظیمات: یک خط با اسکرول افقی، تب فعال مشخص
   ✅ فیلتر تاریخ شمسی در لیست سفارشات
   ✅ ستون‌های جدول قابل مرتب‌سازی (کلیک روی هدر)
   ✅ لاگ‌ها با تاریخ شمسی
   ✅ دکمه پاک کردن فیلترها

🚀 اجرا:
   php artisan serve
   http://127.0.0.1:8000/orders
   http://127.0.0.1:8000/settings
""")
