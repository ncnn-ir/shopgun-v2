#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""رفع باگ اسکریپت قبلی — ۳ چیز مشخص"""
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

def read(rel):
    full = PROJECT / rel
    if not full.exists(): return None
    with open(full, 'r', encoding='utf-8') as f:
        return f.read()

def backup(rel):
    src = PROJECT / rel
    if not src.exists(): return
    bd = PROJECT / "storage/backups"; bd.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(src, bd / f"{src.stem}_{ts}.bak")

# ═══════════════════════════════════════════════════════════════
# FIX 1: Settings Blade — تب‌های موبایل
# ═══════════════════════════════════════════════════════════════
SETTINGS_BLADE = r'''<div style="padding:0 0 18px">
    <div style="padding:0 18px 14px">
        <h1 style="font-size:20px;font-weight:700">⚙️ تنظیمات</h1>
    </div>

    {{-- ═══ Desktop Tabs ═══ --}}
    <div class="sg-tabs-bar" style="padding:0 18px;margin-bottom:14px;overflow-x:auto;flex-wrap:nowrap;display:none">
        @foreach([
            'general' => ['⚙️', 'عمومی'],
            'appearance' => ['🎨', 'ظاهر'],
            'commerce' => ['🔌', 'کامرس'],
            'certificate' => ['💎', 'شناسنامه'],
            'label' => ['🏷️', 'برچسب'],
            'assets' => ['🖼️', 'تصاویر'],
            'backup' => ['💾', 'پشتیبان'],
            'logs' => ['📜', 'لاگ'],
            'stones' => ['💠', 'سنگ/فلز'],
            'monitor' => ['📊', 'رصد API'],
        ] as $key => $meta)
            <button wire:click="setTab('{{ $key }}')"
                    class="sg-tab-btn {{ $tab === $key ? 'active' : '' }}"
                    style="white-space:nowrap">
                <span>{{ $meta[0] }}</span><span>{{ $meta[1] }}</span>
            </button>
        @endforeach
    </div>

    {{-- ═══ Mobile Tabs — Horizontal Scroll ═══ --}}
    <div class="sg-tabs-mobile">
        @foreach([
            'general' => ['⚙️', 'عمومی'],
            'appearance' => ['🎨', 'ظاهر'],
            'commerce' => ['🔌', 'کامرس'],
            'certificate' => ['💎', 'کارت'],
            'label' => ['🏷️', 'برچسب'],
            'assets' => ['🖼️', 'تصاویر'],
            'backup' => ['💾', 'پشتیبان'],
            'logs' => ['📜', 'لاگ'],
            'stones' => ['💠', 'سنگ'],
            'monitor' => ['📊', 'API'],
        ] as $key => $meta)
            <button wire:click="setTab('{{ $key }}')"
                    class="sg-tab-chip {{ $tab === $key ? 'active' : '' }}">
                <span>{{ $meta[0] }}</span><span>{{ $meta[1] }}</span>
            </button>
        @endforeach
    </div>

    {{-- ═══════════════════════════════════════════════════════ --}}
    {{-- Tab: General                                             --}}
    {{-- ═══════════════════════════════════════════════════════ --}}
    @if($tab === 'general')
        <div class="sg-settings-card" style="margin:0 18px">
            <h3>اطلاعات فروشگاه</h3>
            <div class="form-row cols-2">
                <div class="form-group"><label>🏪 نام فروشگاه</label><input type="text" wire:model="shop_name" class="form-control"></div>
                <div class="form-group"><label>📱 تلفن</label><input type="text" wire:model="shop_phone" class="form-control" dir="ltr"></div>
            </div>
            <div class="form-group"><label>📍 آدرس</label><textarea wire:model="shop_address" class="form-control" rows="2"></textarea></div>
            <div class="form-row cols-3">
                <div class="form-group"><label>📮 کدپستی</label><input type="text" wire:model="shop_postal" class="form-control" dir="ltr"></div>
                <div class="form-group"><label>📧 ایمیل</label><input type="email" wire:model="shop_email" class="form-control" dir="ltr"></div>
                <div class="form-group"><label>💵 واحد پول</label><input type="text" wire:model="currency" class="form-control"></div>
            </div>
            <div style="display:flex;justify-content:flex-end;padding-top:10px;border-top:1px solid var(--border)">
                <button wire:click="saveGeneral" class="btn btn-success">💾 ذخیره</button>
            </div>
        </div>
    @endif

    {{-- Tab: Appearance --}}
    @if($tab === 'appearance')
        <div class="sg-settings-card" style="margin:0 18px">
            <h3>ظاهر برنامه</h3>
            <div class="form-row cols-2">
                <div class="form-group"><label>🌓 تم</label>
                    <div style="display:flex;gap:6px">
                        @foreach(['light'=>'☀️ روشن','dark'=>'🌙 تیره'] as $k => $v)
                            <label style="flex:1;cursor:pointer">
                                <input type="radio" wire:model.live="theme" value="{{ $k }}" style="display:none">
                                <div style="padding:10px;border:2px solid {{ $theme === $k ? 'var(--gold)' : 'var(--border)' }};border-radius:10px;text-align:center;font-size:12px;font-weight:700;background:{{ $theme === $k ? 'rgba(201,168,76,.15)' : 'transparent' }}">{{ $v }}</div>
                            </label>
                        @endforeach
                    </div>
                </div>
                <div class="form-group"><label>📐 تراکم</label>
                    <div style="display:flex;gap:6px">
                        @foreach(['compact'=>'فشرده','normal'=>'معمولی','comfortable'=>'راحت'] as $k => $v)
                            <label style="flex:1;cursor:pointer">
                                <input type="radio" wire:model.live="density" value="{{ $k }}" style="display:none">
                                <div style="padding:10px;border:2px solid {{ $density === $k ? 'var(--gold)' : 'var(--border)' }};border-radius:10px;text-align:center;font-size:12px;font-weight:700;background:{{ $density === $k ? 'rgba(201,168,76,.15)' : 'transparent' }}">{{ $v }}</div>
                            </label>
                        @endforeach
                    </div>
                </div>
            </div>
            <div class="form-row cols-2">
                <div class="form-group"><label>🎨 رنگ اصلی</label>
                    <input type="color" wire:model.live="primary_color" style="width:100%;height:42px;border:2px solid var(--border);border-radius:10px;cursor:pointer">
                </div>
                <div class="form-group"><label>✨ رنگ تاکیدی</label>
                    <input type="color" wire:model.live="accent_color" style="width:100%;height:42px;border:2px solid var(--border);border-radius:10px;cursor:pointer">
                </div>
            </div>
            <div class="form-group"><label>🔤 فونت</label>
                <select wire:model.live="font_family" class="form-control">
                    <option value="Vazirmatn">وزیرمتن (پیش‌فرض)</option>
                    <option value="Tahoma">تاهوما</option>
                    <option value="system-ui">سیستم</option>
                    <option value="Arial">Arial</option>
                </select>
            </div>
            <div style="padding:10px;background:var(--bg);border-radius:8px;font-size:11px;margin-bottom:10px">
                💡 تغییرات به صورت زنده روی همین صفحه اعمال می‌شود.
            </div>
            <div style="display:flex;justify-content:flex-end;padding-top:10px;border-top:1px solid var(--border)">
                <button wire:click="saveAppearance" class="btn btn-success">💾 ذخیره دائمی</button>
            </div>
        </div>
    @endif

    {{-- Tab: Commerce --}}
    @if($tab === 'commerce')
        <div class="sg-settings-card" style="margin:0 18px">
            <h3>🔌 اتصال به WooCommerce</h3>
            <div style="padding:10px;background:rgba(41,128,185,.08);border-radius:10px;font-size:11.5px;margin-bottom:12px">
                💡 وردپرس → WooCommerce → Settings → Advanced → REST API → Add key
            </div>
            <div class="form-group"><label>🌐 آدرس سایت</label>
                <input type="text" wire:model="commerce_url" class="form-control" dir="ltr" placeholder="https://yoursite.com">
            </div>
            <div class="form-row cols-2">
                <div class="form-group"><label>🔑 Consumer Key</label><input type="text" wire:model="commerce_key" class="form-control" dir="ltr"></div>
                <div class="form-group"><label>🔐 Consumer Secret</label><input type="password" wire:model="commerce_secret" class="form-control" dir="ltr"></div>
            </div>

            @if(!empty($commerce_test_result))
                <div style="padding:12px;border-radius:10px;margin-bottom:12px;background:{{ $commerce_test_result['ok'] ? 'rgba(39,174,96,.1)' : 'rgba(231,76,60,.1)' }};color:{{ $commerce_test_result['ok'] ? 'var(--success)' : 'var(--danger)' }};font-weight:700;font-size:13px">
                    {{ $commerce_test_result['ok'] ? '✅' : '❌' }} {{ $commerce_test_result['message'] }}
                </div>
            @endif

            <div style="display:flex;gap:6px;flex-wrap:wrap;padding-top:10px;border-top:1px solid var(--border)">
                <button wire:click="saveCommerce" class="btn btn-primary">💾 ذخیره</button>
                <button wire:click="testCommerce" class="btn btn-secondary">🔌 تست</button>
                <button wire:click="syncProducts" class="btn btn-success">📥 سینک محصولات</button>
            </div>
        </div>
    @endif

    {{-- Tab: Certificate --}}
    @if($tab === 'certificate')
        <div class="sg-settings-card" style="margin:0 18px">
            <h3>📏 اندازه شناسنامه</h3>
            <div class="form-row cols-2">
                <div class="form-group"><label>📐 عرض (cm)</label><input type="number" step="0.1" wire:model="cert_width" class="form-control" dir="ltr"></div>
                <div class="form-group"><label>📐 ارتفاع (cm)</label><input type="number" step="0.1" wire:model="cert_height" class="form-control" dir="ltr"></div>
            </div>
            <div style="display:flex;gap:6px;margin-bottom:14px">
                <button wire:click="setCertPreset(6.5,6.5)" class="btn btn-outline btn-sm">۶.۵×۶.۵</button>
                <button wire:click="setCertPreset(7,7)" class="btn btn-outline btn-sm">۷×۷</button>
                <button wire:click="setCertPreset(8,6)" class="btn btn-outline btn-sm">۸×۶</button>
            </div>
            <div style="display:flex;justify-content:flex-end;padding-top:10px;border-top:1px solid var(--border)">
                <button wire:click="saveCertificate" class="btn btn-success">💾 ذخیره</button>
            </div>
        </div>
    @endif

    {{-- Tab: Label --}}
    @if($tab === 'label')
        <div class="sg-settings-card" style="margin:0 18px">
            <h3>📐 اندازه برچسب</h3>
            <div class="form-row cols-2">
                <div class="form-group"><label>📐 عرض (mm)</label><input type="number" wire:model="label_width" class="form-control" dir="ltr"></div>
                <div class="form-group"><label>📐 ارتفاع (mm)</label><input type="number" wire:model="label_height" class="form-control" dir="ltr"></div>
            </div>
            <div style="display:flex;justify-content:flex-end;padding-top:10px;border-top:1px solid var(--border)">
                <button wire:click="saveLabel" class="btn btn-success">💾 ذخیره</button>
            </div>
        </div>
    @endif

    {{-- Tab: Assets --}}
    @if($tab === 'assets')
        <div class="sg-settings-card" style="margin:0 18px">
            <h3>🖼️ پس‌زمینه شناسنامه</h3>
            @if($bg_image)
                <div style="margin-bottom:12px">
                    <img src="{{ $bg_image }}" style="max-width:200px;border-radius:10px;border:2px solid var(--gold)">
                    <button wire:click="removeBg" class="btn btn-danger btn-sm" style="margin-right:8px">حذف</button>
                </div>
            @endif
            <input type="file" wire:model="bg_image" accept="image/*" class="form-control">
        </div>
    @endif

    {{-- Tab: Backup --}}
    @if($tab === 'backup')
        <div class="sg-settings-card" style="margin:0 18px">
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
                    <div style="padding:10px;background:var(--bg);border-radius:8px;display:flex;justify-content:space-between;font-size:12px">
                        <span>{{ $item[0] }} {{ $item[1] }}</span>
                        <strong style="font-family:monospace">{{ $item[2] }}</strong>
                    </div>
                @endforeach
            </div>
        </div>
    @endif

    {{-- Tab: Logs --}}
    @if($tab === 'logs')
        <div class="sg-settings-card" style="margin:0 18px">
            <h3>📜 لاگ تغییرات</h3>
            <div style="display:flex;gap:8px;margin-bottom:14px">
                <input type="text" wire:model.live.debounce.400ms="log_search" placeholder="🔍 جستجو..." class="form-control" style="flex:1">
                <button wire:click="clearLogs" wire:confirm="پاک شوند؟" class="btn btn-danger btn-sm">🗑️</button>
            </div>
            <div style="max-height:500px;overflow-y:auto">
                @forelse($logs as $log)
                    <div style="padding:10px 12px;border-bottom:1px solid var(--border);font-size:11.5px">
                        <strong>{{ $log['description'] }}</strong>
                        <span style="opacity:.6"> · {{ $log['event'] }}</span>
                        <div style="font-family:monospace;font-size:10px;opacity:.5;margin-top:2px">{{ $log['created_at'] }} · {{ $log['causer'] }}</div>
                    </div>
                @empty
                    <p style="text-align:center;padding:20px;opacity:.5">لاگی نیست</p>
                @endforelse
            </div>
        </div>
    @endif

    {{-- Tab: Stones --}}
    @if($tab === 'stones')
        <div class="sg-settings-card" style="margin:0 18px">
            <h3>💎 سنگ‌های قیمتی ({{ \App\Support\PersianNumber::toFa(count($stones_list)) }})</h3>
            <div class="sg-stones-grid">
                @foreach($stones_list as $s)
                    <div class="sg-stone-card">
                        <button wire:click="removeStone({{ $s['id'] }})" wire:confirm="حذف شود؟"
                                style="position:absolute;top:-6px;left:-6px;width:20px;height:20px;border-radius:50%;background:var(--danger);color:#fff;border:none;cursor:pointer;font-size:11px">✕</button>
                        <div class="s-icon">{{ $s['icon'] ?? '💎' }}</div>
                        <div class="s-name">{{ $s['name'] }}</div>
                        <div class="s-origin">{{ $s['origin'] ?? '' }}</div>
                    </div>
                @endforeach
            </div>

            <h3 style="margin-top:20px">➕ افزودن سنگ</h3>
            <div class="form-row cols-2">
                <div class="form-group"><label>نام فارسی</label><input type="text" wire:model="new_stone_name" class="form-control"></div>
                <div class="form-group"><label>نام انگلیسی</label><input type="text" wire:model="new_stone_en" class="form-control" dir="ltr"></div>
            </div>
            <button wire:click="addStone" class="btn btn-primary">➕ افزودن سنگ</button>

            <h3 style="margin-top:30px">⚙️ فلزات ({{ \App\Support\PersianNumber::toFa(count($metals_list)) }})</h3>
            @foreach($metals_list as $m)
                <div style="padding:8px 12px;background:var(--bg);border-radius:8px;margin-bottom:6px;display:flex;justify-content:space-between;align-items:center">
                    <span>⚙️ <strong>{{ $m['name'] }}</strong> — {{ $m['carat'] ?? '-' }}</span>
                    <button wire:click="removeMetal({{ $m['id'] }})" wire:confirm="حذف شود؟" class="btn btn-danger btn-sm">حذف</button>
                </div>
            @endforeach
        </div>
    @endif

    {{-- Tab: Monitor --}}
    @if($tab === 'monitor')
        <div class="sg-settings-card" style="margin:0 18px">
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
                <input type="text" wire:model.live.debounce.400ms="monitor_filter" placeholder="🔍 فیلتر..." class="form-control" style="flex:1">
                <button wire:click="refreshMonitor" class="btn btn-outline btn-sm">🔄</button>
                <button wire:click="clearMonitor" wire:confirm="پاک شوند؟" class="btn btn-danger btn-sm">🗑️</button>
            </div>
            <div style="max-height:500px;overflow-y:auto">
                @forelse($monitor_logs as $log)
                    <div style="padding:8px 10px;border-bottom:1px solid var(--border);font-size:11px">
                        <div style="display:flex;gap:8px;align-items:center;margin-bottom:4px">
                            <span style="padding:2px 6px;border-radius:6px;background:{{ ($log['status_code'] ?? 0) >= 200 && ($log['status_code'] ?? 0) < 300 ? 'var(--success)' : 'var(--danger)' }};color:#fff;font-weight:700;font-size:10px;font-family:monospace">{{ $log['status_code'] ?? '—' }}</span>
                            <span style="font-family:monospace;font-weight:700">{{ $log['method'] }}</span>
                            <span style="margin-right:auto;font-family:monospace;opacity:.5">{{ $log['created_at'] }}</span>
                        </div>
                        <div style="font-family:monospace;font-size:10px;opacity:.7;overflow:hidden;text-overflow:ellipsis" dir="ltr">{{ $log['url'] }}</div>
                    </div>
                @empty
                    <p style="text-align:center;padding:20px;opacity:.5">لاگی نیست</p>
                @endforelse
            </div>
        </div>
    @endif
</div>
'''

# ═══════════════════════════════════════════════════════════════
# FIX 2: Extra CSS — با تب‌های موبایل
# ═══════════════════════════════════════════════════════════════
EXTRA_CSS = r'''/* ═══ Chart Scroll ═══ */
.sg-chart-scroll {
    overflow-x: auto;
    overflow-y: hidden;
    padding-bottom: 6px;
    -webkit-overflow-scrolling: touch;
}
.sg-chart-scroll::-webkit-scrollbar { height: 4px; }
.sg-chart-scroll::-webkit-scrollbar-thumb { background: rgba(0,0,0,.15); border-radius: 2px; }

/* ═══ Settings Mobile Tabs — Horizontal Scroll ═══ */
.sg-tabs-mobile {
    display: none;
    overflow-x: auto;
    overflow-y: hidden;
    -webkit-overflow-scrolling: touch;
    scrollbar-width: none;
    -ms-overflow-style: none;
    gap: 6px;
    padding: 6px 14px 12px;
    white-space: nowrap;
    align-items: center;
}
.sg-tabs-mobile::-webkit-scrollbar { display: none; }

.sg-tab-chip {
    display: inline-flex;
    align-items: center;
    gap: 5px;
    padding: 8px 14px;
    background: var(--bg-card);
    border: 1.5px solid var(--border);
    border-radius: 20px;
    font-family: inherit;
    font-size: 12px;
    font-weight: 700;
    color: var(--text-light);
    cursor: pointer;
    flex-shrink: 0;
    transition: all .2s;
    white-space: nowrap;
}
.sg-tab-chip:hover {
    border-color: var(--gold);
    color: var(--text);
}
.sg-tab-chip.active {
    background: linear-gradient(135deg, var(--primary), #0d3b5e);
    color: #fff;
    border-color: var(--primary);
    box-shadow: 0 4px 12px rgba(13,148,136,.3);
}

/* ═══ Timeline with Time ═══ */
.sg-tl-step .tl-time {
    font-size: 8px;
    font-family: monospace;
    color: var(--text-light);
    margin-top: 2px;
    opacity: .8;
}

/* ═══ Mobile Bar sticky fix ═══ */
.sg-mobile-bar {
    position: fixed !important;
    bottom: 10px !important;
    left: 10px !important;
    right: 10px !important;
}

/* ═══ Mobile: Settings show mobile tabs, hide desktop ═══ */
@media(max-width: 768px) {
    .sg-tabs-mobile { display: flex !important; }
    .sg-settings-card { margin: 0 14px !important; }
    .sg-chart-grid { grid-template-columns: 1fr; padding: 0 14px 14px; }
    .sg-stats-row { padding: 4px 14px 12px; }
}
'''

# ═══════════════════════════════════════════════════════════════
# FIX 3: Layout — Appearance Listener + Reports CSS
# ═══════════════════════════════════════════════════════════════
def patch_layout():
    layout = PROJECT / "resources/views/components/layouts/app.blade.php"
    if not layout.exists():
        print("  ⚠️ Layout پیدا نشد")
        return

    backup("resources/views/components/layouts/app.blade.php")

    with open(layout, 'r', encoding='utf-8') as f:
        content = f.read()

    # ۱) اضافه کردن extra.css
    if 'extra.css' not in content:
        content = content.replace('</head>', '    <link rel="stylesheet" href="{{ asset(\'css/extra.css\') }}?v=3">\n</head>', 1)
        print("  ✓ extra.css link اضافه شد")

    # ۲) Style برای رنگ/فونت داینامیک
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
        .btn-primary { background: linear-gradient(135deg, {{ $_g }}, {{ $_g }}dd) !important; }
        .sg-tab-btn.active, .sg-tab-chip.active { color: {{ $_p }} !important; border-bottom-color: {{ $_g }} !important; }
        .sg-tab-chip.active { color: #fff !important; background: linear-gradient(135deg, {{ $_p }}, {{ $_p }}cc) !important; }
    </style>
'''
        content = content.replace('</head>', style_block + '</head>', 1)
        print("  ✓ Style داینامیک اضافه شد")

    # ۳) Listener apply-appearance
    if 'apply-appearance' not in content:
        listener = '''
    Livewire.on('apply-appearance', function(data) {
        var p = Array.isArray(data) ? data[0] : data;
        var root = document.documentElement;
        if (p.primary_color) {
            root.style.setProperty('--primary', p.primary_color);
            document.querySelectorAll('style').forEach(function(s) {
                if (s.textContent.includes('--primary:')) {
                    // no-op
                }
            });
        }
        if (p.accent_color) root.style.setProperty('--gold', p.accent_color);
        if (p.font_family) {
            root.style.setProperty('--font-dynamic', p.font_family);
            document.body.style.fontFamily = p.font_family + ", 'Vazirmatn', Tahoma, sans-serif";
        }
        if (p.theme) {
            root.setAttribute('data-theme', p.theme);
            localStorage.setItem('theme', p.theme);
        }
        if (window.sgToast) sgToast('ظاهر اعمال شد ✅', 'success');
    });
'''
        # جایگزینی داخل livewire:init
        content = content.replace(
            "document.addEventListener('livewire:init', function() {",
            "document.addEventListener('livewire:init', function() {" + listener,
            1
        )
        print("  ✓ Listener apply-appearance اضافه شد")

    with open(layout, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)

# ═══════════════════════════════════════════════════════════════
# FIX 4: Settings PHP — Live update methods
# ═══════════════════════════════════════════════════════════════
def patch_settings_php():
    php_path = PROJECT / "app/Livewire/Settings/Index.php"
    if not php_path.exists():
        print("  ⚠️ Settings Index پیدا نشد")
        return

    backup("app/Livewire/Settings/Index.php")

    with open(php_path, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'updatedPrimaryColor' in content:
        print("  ⏭ از قبل هست")
        return

    # اضافه کردن متدهای live update
    extra = '''
    /* ═══ Live Appearance ═══ */
    protected function dispatchAppearance(): void
    {
        $this->dispatch('apply-appearance', [
            'theme' => $this->theme,
            'density' => $this->density,
            'primary_color' => $this->primary_color,
            'accent_color' => $this->accent_color,
            'font_family' => $this->font_family,
        ]);
    }

    public function updatedPrimaryColor(): void { $this->dispatchAppearance(); }
    public function updatedAccentColor(): void { $this->dispatchAppearance(); }
    public function updatedTheme(): void { $this->dispatchAppearance(); }
    public function updatedFontFamily(): void { $this->dispatchAppearance(); }
    public function updatedDensity(): void { $this->dispatchAppearance(); }

    public function resetAppearance(): void
    {
        $this->primary_color = '#1a5276';
        $this->accent_color = '#c9a84c';
        $this->font_family = 'Vazirmatn';
        $this->theme = 'light';
        $this->density = 'normal';
        $this->dispatchAppearance();
        $this->dispatch('notify', type: 'success', message: 'بازنشانی شد');
    }
'''

    # درست قبل از render اضافه کن
    idx = content.rfind('public function render()')
    if idx > 0:
        content = content[:idx] + extra + "\n    " + content[idx:]
        with open(php_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        print("  ✓ متدهای live update اضافه شد")

    # saveAppearance هم dispatch کنه
    if "dispatch('apply-appearance'" not in content:
        content = content.replace(
            "$this->dispatch('apply-theme', [",
            "$this->dispatch('apply-appearance', ["
        )
        with open(php_path, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        print("  ✓ saveAppearance اصلاح شد")

# ═══════════════════════════════════════════════════════════════
# اجرا
# ═══════════════════════════════════════════════════════════════
def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  رفع باگ — ۳ چیز مشخص قابل تست                               ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    print("📄 نوشتن Settings Blade (با تب‌های موبایل)...")
    backup("resources/views/livewire/settings/index.blade.php")
    write("resources/views/livewire/settings/index.blade.php", SETTINGS_BLADE)

    print("\n📄 نوشتن CSS...")
    write("public/css/extra.css", EXTRA_CSS)

    print("\n🔧 Patch Layout...")
    patch_layout()

    print("\n🔧 Patch Settings PHP...")
    patch_settings_php()

    print("\n" + "═" * 64)
    print("✅ تمام!")
    print("═" * 64)
    print("""
📋 اجرا کن:

  cd ~/shopgun-v2.2
  php artisan optimize:clear
  php artisan view:clear

  # ⚠️ حتماً سرور رو ببند (Ctrl+C) و دوباره باز کن
  php artisan serve

  # مرورگر: Ctrl+Shift+R

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 این بار چی تست کن:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ۱. برو /settings
     → در موبایل باید ۱۰ تب افقی با اسکرول ببینی
     → تب فعال رنگی (آبی/سبز) باشه

  ۲. تب «🎨 ظاهر»
     → رنگ اصلی رو تغییر بده
     → **فوراً** رنگ صفحه عوض بشه
     → فونت رو تغییر بده → فونت فوری عوض بشه

  ۳. تب «🎨 ظاهر»
     → تم تیره/روشن
     → فوری اعمال بشه

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ اگه باز هم تغییر نکرد، این رو تو Console مرورگر بزن:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  // ۱. چک کن Livewire لود شده
  typeof Livewire

  // ۲. چک کن ایونت listener ثبت شده
  console.log('listeners active')

  // ۳. متن خطا اگه هست رو بگیر

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
""")

if __name__ == "__main__":
    main()
