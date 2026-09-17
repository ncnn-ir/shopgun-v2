# -*- coding: utf-8 -*-
"""
ShopGun V2 - Full UI Fix
"""
import os, sys
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).parent.resolve()

def write(rel, content):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        p.rename(p.with_suffix(p.suffix + '.bak-' + datetime.now().strftime('%H%M%S')))
    p.write_text(content, encoding='utf-8')
    print("OK: " + rel)

# ═══════════════════════════════════════════════════════════════
# 1. CERTIFICATE CREATE FORM (Wizard 3 step)
# ═══════════════════════════════════════════════════════════════

write('resources/views/livewire/certificates/create.blade.php', r'''<div style="padding:14px;max-width:900px;margin:0 auto" dir="rtl">

    <div style="display:flex;align-items:center;gap:10px;margin-bottom:20px">
        <a href="{{ route('certificates.index') }}" style="width:36px;height:36px;border-radius:50%;background:#f1f5f9;display:flex;align-items:center;justify-content:center;text-decoration:none;color:#1a5276;font-weight:700">→</a>
        <h1 style="margin:0;font-size:22px;font-weight:700">💎 شناسنامه جدید</h1>
    </div>

    {{-- Steps --}}
    <div style="display:flex;justify-content:space-between;margin-bottom:24px;position:relative;padding:0 20px">
        <div style="position:absolute;top:18px;left:60px;right:60px;height:2px;background:#e2e8f0;z-index:0"></div>
        @foreach([1 => 'سنگ و فلز', 2 => 'مشخصات', 3 => 'تصویر'] as $num => $label)
            <div style="position:relative;z-index:1;display:flex;flex-direction:column;align-items:center;flex:1">
                <div style="width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;
                    background:{{ $step >= $num ? 'linear-gradient(135deg,#1a5276,#0d3b5e)' : '#f1f5f9' }};
                    color:{{ $step >= $num ? '#fff' : '#64748b' }};
                    box-shadow:{{ $step === $num ? '0 0 0 4px rgba(26,82,118,.2)' : 'none' }};">
                    {{ $num }}
                </div>
                <div style="font-size:11px;font-weight:700;margin-top:6px;color:{{ $step >= $num ? '#1a5276' : '#94a3b8' }}">{{ $label }}</div>
            </div>
        @endforeach
    </div>

    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:20px;box-shadow:0 2px 8px rgba(0,0,0,.04)">

        @if($step === 1)
            <div style="margin-bottom:20px">
                <h3 style="font-size:14px;font-weight:700;color:#1a5276;margin:0 0 12px">💎 سنگ را انتخاب کن</h3>
                <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:8px">
                    @foreach($stoneOptions as $i => $s)
                        <button type="button" wire:click="selectStone({{ $i }})"
                                style="padding:10px 4px;border:2px solid {{ $stoneName === $s['name'] ? '#c9a84c' : '#e2e8f0' }};background:{{ $stoneName === $s['name'] ? '#fef3c7' : '#fff' }};border-radius:10px;cursor:pointer;transition:all .15s">
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
                    @error('length') <div style="color:#dc2626;font-size:10px;margin-top:3px">{{ $message }}</div> @enderror
                </div>
                <div>
                    <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">عرض (mm)</label>
                    <input type="number" step="0.01" wire:model="width" dir="ltr"
                           style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-family:monospace;font-size:13px;background:#f8fafc;box-sizing:border-box;text-align:center">
                    @error('width') <div style="color:#dc2626;font-size:10px;margin-top:3px">{{ $message }}</div> @enderror
                </div>
                <div>
                    <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">وزن (گرم)</label>
                    <input type="number" step="0.001" wire:model="weight" dir="ltr"
                           style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-family:monospace;font-size:13px;background:#f8fafc;box-sizing:border-box;text-align:center">
                    @error('weight') <div style="color:#dc2626;font-size:10px;margin-top:3px">{{ $message }}</div> @enderror
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
            <div style="background:linear-gradient(135deg,#fef3c7,#fde68a);padding:10px 14px;border-radius:10px;margin-bottom:16px;font-size:13px;font-weight:700;color:#78350f">
                💎 {{ $stoneName }} — 📐 {{ $length }}×{{ $width }} — ⚖️ {{ $weight }}g
            </div>

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

        <div style="display:flex;justify-content:space-between;gap:8px;margin-top:24px;padding-top:16px;border-top:1px solid #e2e8f0">
            <div>
                @if($step > 1)
                    <button type="button" wire:click="prevStep"
                            style="padding:9px 18px;background:#f1f5f9;color:#475569;border:1.5px solid #cbd5e1;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">
                        → مرحله قبل
                    </button>
                @endif
            </div>
            <div style="display:flex;gap:8px">
                <a href="{{ route('certificates.index') }}"
                   style="padding:9px 18px;background:#fff;color:#475569;border:1.5px solid #cbd5e1;border-radius:8px;font-weight:700;text-decoration:none;font-size:13px">
                    انصراف
                </a>
                @if($step < 3)
                    <button type="button" wire:click="nextStep"
                            style="padding:9px 22px;background:linear-gradient(135deg,#1a5276,#0d3b5e);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">
                        مرحله بعد ←
                    </button>
                @else
                    <button type="button" wire:click="save" wire:loading.attr="disabled"
                            style="padding:9px 22px;background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">
                        <span wire:loading.remove wire:target="save">✓ صدور شناسنامه</span>
                        <span wire:loading wire:target="save">⏳ در حال ثبت...</span>
                    </button>
                @endif
            </div>
        </div>
    </div>
</div>
''')

# ═══════════════════════════════════════════════════════════════
# 2. CUSTOMER FORM AS MODAL
# ═══════════════════════════════════════════════════════════════

write('resources/views/livewire/customers/create.blade.php', r'''<div style="padding:14px;max-width:700px;margin:0 auto" dir="rtl">
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:20px">
        <a href="{{ route('customers.index') }}" style="width:36px;height:36px;border-radius:50%;background:#f1f5f9;display:flex;align-items:center;justify-content:center;text-decoration:none;color:#1a5276;font-weight:700">→</a>
        <h1 style="margin:0;font-size:22px;font-weight:700">👤 مشتری جدید</h1>
    </div>

    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:20px">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:14px">
            <div>
                <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">📱 تلفن *</label>
                <input type="text" wire:model="phone" dir="ltr"
                       style="width:100%;padding:10px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-family:monospace;font-size:14px;background:#f8fafc;box-sizing:border-box">
                @error('phone') <div style="color:#dc2626;font-size:10px;margin-top:3px">{{ $message }}</div> @enderror
            </div>
            <div>
                <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">👤 نام</label>
                <input type="text" wire:model="name"
                       style="width:100%;padding:10px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:14px;background:#f8fafc;box-sizing:border-box">
            </div>
        </div>

        <div style="margin-bottom:14px">
            <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">📮 کدپستی</label>
            <input type="text" wire:model="postalCode" dir="ltr"
                   style="width:100%;padding:10px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-family:monospace;font-size:14px;background:#f8fafc;box-sizing:border-box">
        </div>

        <div style="margin-bottom:14px">
            <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">📍 آدرس</label>
            <textarea wire:model="address" rows="3"
                      style="width:100%;padding:10px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:14px;background:#f8fafc;box-sizing:border-box"></textarea>
        </div>

        <div style="margin-bottom:14px">
            <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">📝 یادداشت</label>
            <textarea wire:model="notes" rows="2"
                      style="width:100%;padding:10px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:14px;background:#f8fafc;box-sizing:border-box"></textarea>
        </div>

        <div style="display:flex;justify-content:flex-end;gap:8px;padding-top:14px;border-top:1px solid #e2e8f0">
            <a href="{{ route('customers.index') }}"
               style="padding:10px 20px;background:#fff;color:#475569;border:1.5px solid #cbd5e1;border-radius:8px;font-weight:700;text-decoration:none">انصراف</a>
            <button type="button" wire:click="save" wire:loading.attr="disabled"
                    style="padding:10px 24px;background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer">
                <span wire:loading.remove wire:target="save">✓ ذخیره مشتری</span>
                <span wire:loading wire:target="save">⏳...</span>
            </button>
        </div>
    </div>
</div>
''')

# ═══════════════════════════════════════════════════════════════
# 3. CUSTOMER EDIT (same style)
# ═══════════════════════════════════════════════════════════════

write('resources/views/livewire/customers/edit.blade.php', r'''<div style="padding:14px;max-width:700px;margin:0 auto" dir="rtl">
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:20px">
        <a href="{{ route('customers.show', $customer) }}" style="width:36px;height:36px;border-radius:50%;background:#f1f5f9;display:flex;align-items:center;justify-content:center;text-decoration:none;color:#1a5276;font-weight:700">→</a>
        <h1 style="margin:0;font-size:22px;font-weight:700">✏️ ویرایش مشتری</h1>
    </div>

    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:20px">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:14px">
            <div>
                <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">📱 تلفن *</label>
                <input type="text" wire:model="phone" dir="ltr"
                       style="width:100%;padding:10px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-family:monospace;font-size:14px;background:#f8fafc;box-sizing:border-box">
                @error('phone') <div style="color:#dc2626;font-size:10px;margin-top:3px">{{ $message }}</div> @enderror
            </div>
            <div>
                <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">👤 نام</label>
                <input type="text" wire:model="name"
                       style="width:100%;padding:10px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:14px;background:#f8fafc;box-sizing:border-box">
            </div>
        </div>

        <div style="margin-bottom:14px">
            <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">📮 کدپستی</label>
            <input type="text" wire:model="postalCode" dir="ltr"
                   style="width:100%;padding:10px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-family:monospace;font-size:14px;background:#f8fafc;box-sizing:border-box">
        </div>

        <div style="margin-bottom:14px">
            <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">📍 آدرس</label>
            <textarea wire:model="address" rows="3"
                      style="width:100%;padding:10px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:14px;background:#f8fafc;box-sizing:border-box"></textarea>
        </div>

        <div style="margin-bottom:14px">
            <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">📝 یادداشت</label>
            <textarea wire:model="notes" rows="2"
                      style="width:100%;padding:10px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:14px;background:#f8fafc;box-sizing:border-box"></textarea>
        </div>

        <div style="display:flex;justify-content:flex-end;gap:8px;padding-top:14px;border-top:1px solid #e2e8f0">
            <a href="{{ route('customers.show', $customer) }}"
               style="padding:10px 20px;background:#fff;color:#475569;border:1.5px solid #cbd5e1;border-radius:8px;font-weight:700;text-decoration:none">انصراف</a>
            <button type="button" wire:click="save" wire:loading.attr="disabled"
                    style="padding:10px 24px;background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer">
                <span wire:loading.remove wire:target="save">✓ ذخیره</span>
                <span wire:loading wire:target="save">⏳...</span>
            </button>
        </div>
    </div>
</div>
''')

# ═══════════════════════════════════════════════════════════════
# 4. CSS FINAL - محافظت از تنظیمات
# ═══════════════════════════════════════════════════════════════

css_path = ROOT / 'public/css/settings-tabs-fix.css'
css_path.write_text(r'''/* Settings Tabs - FORCE */
.sg-settings-tabs {
    display: flex !important;
    flex-wrap: nowrap !important;
    gap: 8px !important;
    overflow-x: auto !important;
    padding: 10px 16px !important;
    margin: 0 0 14px 0 !important;
    border-bottom: 2px solid #e2e8f0 !important;
    background: transparent !important;
    scrollbar-width: thin;
}
.sg-settings-tabs::-webkit-scrollbar { height: 4px; }
.sg-settings-tabs::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 2px; }

.sg-settings-tab {
    flex: 0 0 auto !important;
    display: inline-flex !important;
    align-items: center !important;
    gap: 6px !important;
    padding: 8px 14px !important;
    border: 1.5px solid #e2e8f0 !important;
    border-radius: 10px !important;
    background: #fff !important;
    font-family: inherit !important;
    font-size: 12.5px !important;
    font-weight: 700 !important;
    color: #64748b !important;
    cursor: pointer !important;
    white-space: nowrap !important;
    text-decoration: none !important;
    transition: all .15s !important;
}
.sg-settings-tab:hover {
    border-color: #c9a84c !important;
    color: #1e293b !important;
    transform: translateY(-1px) !important;
}
.sg-settings-tab.active {
    background: linear-gradient(135deg, #1a5276, #0d3b5e) !important;
    color: #fff !important;
    border-color: #1a5276 !important;
    box-shadow: 0 4px 12px rgba(26,82,118,.25) !important;
}
.sg-settings-tab .badge-new {
    background: #c9a84c !important;
    color: #fff !important;
    font-size: 8px !important;
    padding: 1px 5px !important;
    border-radius: 8px !important;
    font-weight: 800 !important;
}

.sg-tabs-mobile, .sg-tabs-bar { display: none !important; }

[data-theme="dark"] .sg-settings-tabs { border-bottom-color: #2a3544 !important; }
[data-theme="dark"] .sg-settings-tab { background: #1c2332 !important; color: #94a3b8 !important; border-color: #2a3544 !important; }
[data-theme="dark"] .sg-settings-tab.active { background: linear-gradient(135deg, #4da6d8, #2c7db3) !important; color: #fff !important; }
''', encoding='utf-8')
print("OK: public/css/settings-tabs-fix.css")

# ═══════════════════════════════════════════════════════════════
# 5. LAYOUT - مطمئن شو لینک‌ها سالم هستن
# ═══════════════════════════════════════════════════════════════

layout = ROOT / 'resources/views/components/layouts/app.blade.php'
if layout.exists():
    txt = layout.read_text(encoding='utf-8')
    # حذف @routes تکراری
    txt = txt.replace('@routes', '')
    # اضافه کردن یک بار
    if '@livewireScripts' in txt and '\n@routes' not in txt:
        txt = txt.replace('@livewireScripts', '@livewireScripts\n@routes')
    layout.write_text(txt, encoding='utf-8')
    print("OK: layout fixed (routes @once)")

print("\n=== DONE ===")
print("Now run:")
print("  php artisan view:clear")
print("  php artisan optimize:clear")
print("  php artisan serve")