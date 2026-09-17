# -*- coding: utf-8 -*-
"""ShopGun V2 - Final Fix: preview + modal buttons"""
from pathlib import Path
import time

ROOT = Path(r'D:\prodo\shopgun-v2.2')

def write(rel, content):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        p.rename(str(p) + '.bak-' + str(int(time.time())))
    p.write_text(content, encoding='utf-8')
    print("[OK] " + rel)


# ═══════════════════════════════════════════════════════════════
# 1. SETTINGS BLADE — بازنویسی کامل
# ═══════════════════════════════════════════════════════════════

SETTINGS = r'''<div style="padding:0 0 18px" dir="rtl">

    <div style="padding:0 14px 14px">
        <h1 style="font-size:20px;font-weight:700">⚙️ تنظیمات</h1>
    </div>

    {{-- تب‌ها --}}
    <div class="sg-settings-tabs">
        @foreach([
            'general'     => ['⚙️', 'عمومی', false],
            'appearance'  => ['🎨', 'ظاهر', false],
            'commerce'    => ['🔌', 'اتصالات', false],
            'certificate' => ['💎', 'شناسنامه', false],
            'labels'      => ['🎨', 'ویرایشگر برچسب', false],
            'assets'      => ['🖼️', 'تصاویر', false],
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

    <div style="padding:0 14px">

        {{-- عمومی --}}
        @if($tab === 'general')
            <div class="sg-settings-card">
                <h3>اطلاعات فروشگاه</h3>
                <div class="form-grid">
                    <div class="field col-6">
                        <label>🏪 نام فروشگاه</label>
                        <input type="text" wire:model="shop_name">
                    </div>
                    <div class="field col-6">
                        <label>📱 تلفن</label>
                        <input type="text" wire:model="shop_phone" dir="ltr">
                    </div>
                    <div class="field col-12">
                        <label>📍 آدرس</label>
                        <textarea wire:model="shop_address" rows="2"></textarea>
                    </div>
                    <div class="field col-4">
                        <label>📮 کدپستی</label>
                        <input type="text" wire:model="shop_postal" dir="ltr">
                    </div>
                    <div class="field col-4">
                        <label>📧 ایمیل</label>
                        <input type="email" wire:model="shop_email" dir="ltr">
                    </div>
                    <div class="field col-4">
                        <label>💵 واحد پول</label>
                        <input type="text" wire:model="currency">
                    </div>
                </div>
                <div style="display:flex;justify-content:flex-end;padding-top:14px;border-top:1px solid var(--border)">
                    <button wire:click="saveGeneral" class="btn btn-success">💾 ذخیره</button>
                </div>
            </div>
        @endif

        {{-- ظاهر --}}
        @if($tab === 'appearance')
            <div class="sg-settings-card">
                <h3>ظاهر برنامه</h3>
                <div class="form-grid">
                    <div class="field col-6">
                        <label>🌓 تم</label>
                        <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px">
                            @foreach(['light'=>'☀️ روشن','dark'=>'🌙 تیره'] as $k=>$v)
                                <button type="button" wire:click="$set('theme','{{ $k }}')"
                                        class="btn {{ $theme===$k ? 'btn-primary' : 'btn-outline' }} btn-sm">{{ $v }}</button>
                            @endforeach
                        </div>
                    </div>
                    <div class="field col-6">
                        <label>🎨 رنگ اصلی</label>
                        <input type="color" wire:model.live="primary_color" style="height:42px;padding:4px">
                    </div>
                    <div class="field col-6">
                        <label>✨ رنگ تاکیدی</label>
                        <input type="color" wire:model.live="accent_color" style="height:42px;padding:4px">
                    </div>
                </div>
                <div style="display:flex;justify-content:flex-end;padding-top:14px;border-top:1px solid var(--border)">
                    <button wire:click="saveAppearance" class="btn btn-success">💾 ذخیره</button>
                </div>
            </div>
        @endif

        {{-- کامرس --}}
        @if($tab === 'commerce')
            <div class="sg-settings-card">
                <h3>🔌 اتصال به WooCommerce</h3>
                <div class="form-grid">
                    <div class="field col-12">
                        <label>🌐 آدرس سایت</label>
                        <input type="text" wire:model="commerce_url" dir="ltr" placeholder="https://yoursite.com">
                    </div>
                    <div class="field col-6">
                        <label>🔑 Consumer Key</label>
                        <input type="text" wire:model="commerce_key" dir="ltr">
                    </div>
                    <div class="field col-6">
                        <label>🔐 Consumer Secret</label>
                        <input type="password" wire:model="commerce_secret" dir="ltr">
                    </div>
                </div>
                @if(!empty($commerce_test_result))
                    <div style="padding:10px;border-radius:8px;margin-top:10px;background:{{ $commerce_test_result['ok'] ? '#d1fae5' : '#fee2e2' }};color:{{ $commerce_test_result['ok'] ? '#065f46' : '#991b1b' }};font-weight:700;font-size:13px">
                        {{ $commerce_test_result['ok'] ? '✓' : '✗' }} {{ $commerce_test_result['message'] }}
                    </div>
                @endif
                <div style="display:flex;gap:6px;padding-top:14px;border-top:1px solid var(--border);margin-top:14px;flex-wrap:wrap">
                    <button wire:click="saveCommerce" class="btn btn-primary">💾 ذخیره</button>
                    <button wire:click="testCommerce" class="btn btn-secondary">🔌 تست</button>
                </div>
            </div>
        @endif

        {{-- ═══ شناسنامه ═══ --}}
        @if($tab === 'certificate')
            <div style="display:grid;grid-template-columns:1fr;gap:14px">

                {{-- پیش‌نمایش --}}
                <div class="sg-settings-card" style="position:sticky;top:0;z-index:5">
                    <h3>👁️ پیش‌نمایش زنده</h3>
                    <div style="background:repeating-conic-gradient(#f0f0f0 0% 25%, #fff 0% 50%) 50% / 20px 20px;border-radius:12px;padding:20px;display:flex;justify-content:center;overflow:auto;min-height:400px;align-items:center">
                        <div style="transform-origin:top center">
                            {!! $this->previewCard !!}
                        </div>
                    </div>
                    <div style="display:flex;justify-content:space-between;gap:8px;padding-top:14px;border-top:1px solid var(--border);margin-top:14px;flex-wrap:wrap">
                        <span style="font-size:11px;color:#64748b;align-self:center">
                            📐 {{ $cert_width }}×{{ $cert_height }} cm
                        </span>
                        <button wire:click="saveCertificate" class="btn btn-success">💾 ذخیره تنظیمات</button>
                    </div>
                </div>

                {{-- اهرم‌ها --}}
                <div class="sg-settings-card">
                    <h3>📏 ابعاد کارت</h3>
                    <div class="form-grid">
                        <div class="field col-6">
                            <label>📐 عرض (cm)</label>
                            <input type="number" step="0.1" min="3" max="15" wire:model.live.debounce.300ms="cert_width" dir="ltr">
                        </div>
                        <div class="field col-6">
                            <label>📐 ارتفاع (cm)</label>
                            <input type="number" step="0.1" min="3" max="15" wire:model.live.debounce.300ms="cert_height" dir="ltr">
                        </div>
                    </div>
                    <div style="display:flex;gap:6px;flex-wrap:wrap;margin-top:8px">
                        <button type="button" wire:click="setCertPreset(6.5,6.5)" class="btn btn-outline btn-xs">۶.۵×۶.۵</button>
                        <button type="button" wire:click="setCertPreset(7,7)" class="btn btn-outline btn-xs">۷×۷</button>
                        <button type="button" wire:click="setCertPreset(8,6)" class="btn btn-outline btn-xs">۸×۶</button>
                    </div>

                    <h3 style="margin-top:20px">🖼️ تصویر محصول</h3>
                    <div style="display:grid;grid-template-columns:100px 1fr 60px;gap:10px;align-items:center;margin-bottom:14px">
                        <label style="font-size:12px;font-weight:700;color:#1a5276">عرض</label>
                        <input type="range" min="40" max="300" step="5" wire:model.live.debounce.200ms="cert_img_w" class="range range-sm range-primary w-full">
                        <span style="font-family:monospace;font-size:11px;text-align:center;background:#fef3c7;padding:3px;border-radius:6px">{{ $cert_img_w }}px</span>
                    </div>
                    <div style="display:grid;grid-template-columns:100px 1fr 60px;gap:10px;align-items:center;margin-bottom:14px">
                        <label style="font-size:12px;font-weight:700;color:#1a5276">ارتفاع</label>
                        <input type="range" min="40" max="300" step="5" wire:model.live.debounce.200ms="cert_img_h" class="range range-sm range-primary w-full">
                        <span style="font-family:monospace;font-size:11px;text-align:center;background:#fef3c7;padding:3px;border-radius:6px">{{ $cert_img_h }}px</span>
                    </div>

                    <h3 style="margin-top:20px">📱 QR و لوگو</h3>
                    <div style="display:grid;grid-template-columns:100px 1fr 60px;gap:10px;align-items:center;margin-bottom:14px">
                        <label style="font-size:12px;font-weight:700;color:#1a5276">اندازه QR</label>
                        <input type="range" min="20" max="120" step="2" wire:model.live.debounce.200ms="cert_qr_size" class="range range-sm range-primary w-full">
                        <span style="font-family:monospace;font-size:11px;text-align:center;background:#fef3c7;padding:3px;border-radius:6px">{{ $cert_qr_size }}px</span>
                    </div>
                    <div style="display:grid;grid-template-columns:100px 1fr 60px;gap:10px;align-items:center;margin-bottom:14px">
                        <label style="font-size:12px;font-weight:700;color:#1a5276">عرض لوگو</label>
                        <input type="range" min="10" max="100" step="2" wire:model.live.debounce.200ms="cert_logo_w" class="range range-sm range-primary w-full">
                        <span style="font-family:monospace;font-size:11px;text-align:center;background:#fef3c7;padding:3px;border-radius:6px">{{ $cert_logo_w }}px</span>
                    </div>
                    <div style="display:grid;grid-template-columns:100px 1fr 60px;gap:10px;align-items:center;margin-bottom:14px">
                        <label style="font-size:12px;font-weight:700;color:#1a5276">ارتفاع لوگو</label>
                        <input type="range" min="10" max="100" step="2" wire:model.live.debounce.200ms="cert_logo_h" class="range range-sm range-primary w-full">
                        <span style="font-family:monospace;font-size:11px;text-align:center;background:#fef3c7;padding:3px;border-radius:6px">{{ $cert_logo_h }}px</span>
                    </div>

                    <h3 style="margin-top:20px">🔤 فونت‌ها</h3>
                    <div style="display:grid;grid-template-columns:100px 1fr 60px;gap:10px;align-items:center;margin-bottom:14px">
                        <label style="font-size:12px;font-weight:700;color:#1a5276">عنوان</label>
                        <input type="range" min="8" max="40" wire:model.live.debounce.200ms="cert_title_font" class="range range-sm range-primary w-full">
                        <span style="font-family:monospace;font-size:11px;text-align:center;background:#fef3c7;padding:3px;border-radius:6px">{{ $cert_title_font }}px</span>
                    </div>
                    <div style="display:grid;grid-template-columns:100px 1fr 60px;gap:10px;align-items:center;margin-bottom:14px">
                        <label style="font-size:12px;font-weight:700;color:#1a5276">کد</label>
                        <input type="range" min="6" max="30" wire:model.live.debounce.200ms="cert_code_font" class="range range-sm range-primary w-full">
                        <span style="font-family:monospace;font-size:11px;text-align:center;background:#fef3c7;padding:3px;border-radius:6px">{{ $cert_code_font }}px</span>
                    </div>
                    <div style="display:grid;grid-template-columns:100px 1fr 60px;gap:10px;align-items:center;margin-bottom:14px">
                        <label style="font-size:12px;font-weight:700;color:#1a5276">توضیحات</label>
                        <input type="range" min="5" max="20" wire:model.live.debounce.200ms="cert_desc_font" class="range range-sm range-primary w-full">
                        <span style="font-family:monospace;font-size:11px;text-align:center;background:#fef3c7;padding:3px;border-radius:6px">{{ $cert_desc_font }}px</span>
                    </div>

                    <h3 style="margin-top:20px">📊 عرض ستون‌های جدول</h3>
                    <div style="display:grid;grid-template-columns:100px 1fr 60px;gap:10px;align-items:center;margin-bottom:14px">
                        <label style="font-size:12px;font-weight:700;color:#1a5276">ستون ۱</label>
                        <input type="range" min="10" max="50" wire:model.live.debounce.100ms="cert_col1" class="range range-sm range-primary w-full">
                        <span style="font-family:monospace;font-size:11px;text-align:center;background:#fef3c7;padding:3px;border-radius:6px">{{ $cert_col1 }}%</span>
                    </div>
                    <div style="display:grid;grid-template-columns:100px 1fr 60px;gap:10px;align-items:center;margin-bottom:14px">
                        <label style="font-size:12px;font-weight:700;color:#1a5276">ستون ۲</label>
                        <input type="range" min="10" max="50" wire:model.live.debounce.100ms="cert_col2" class="range range-sm range-primary w-full">
                        <span style="font-family:monospace;font-size:11px;text-align:center;background:#fef3c7;padding:3px;border-radius:6px">{{ $cert_col2 }}%</span>
                    </div>
                    <div style="display:grid;grid-template-columns:100px 1fr 60px;gap:10px;align-items:center;margin-bottom:14px">
                        <label style="font-size:12px;font-weight:700;color:#1a5276">ستون ۳</label>
                        <input type="range" min="10" max="50" wire:model.live.debounce.100ms="cert_col3" class="range range-sm range-primary w-full">
                        <span style="font-family:monospace;font-size:11px;text-align:center;background:#fef3c7;padding:3px;border-radius:6px">{{ $cert_col3 }}%</span>
                    </div>
                    <div style="display:grid;grid-template-columns:100px 1fr 60px;gap:10px;align-items:center;margin-bottom:14px">
                        <label style="font-size:12px;font-weight:700;color:#1a5276">ستون ۴</label>
                        <input type="range" min="10" max="50" wire:model.live.debounce.100ms="cert_col4" class="range range-sm range-primary w-full">
                        <span style="font-family:monospace;font-size:11px;text-align:center;background:#fef3c7;padding:3px;border-radius:6px">{{ $cert_col4 }}%</span>
                    </div>

                    <label style="display:flex;align-items:center;gap:8px;padding:10px;background:rgba(0,0,0,.03);border-radius:8px;cursor:pointer;margin-top:14px">
                        <input type="checkbox" wire:model.live="cert_hide_desc" class="checkbox checkbox-primary checkbox-sm">
                        <span style="font-size:13px;font-weight:700">مخفی کردن توضیحات</span>
                    </label>
                </div>

                {{-- لوگوها --}}
                <div class="sg-settings-card">
                    <h3>🏷️ لوگوها (بالای کارت)</h3>
                    <p style="font-size:11px;color:#94a3b8;margin:0 0 10px">مثلاً نشان اعتبار، برند، لوگوی فروشگاه</p>

                    @if(count($logo_images))
                        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(80px,1fr));gap:8px;margin-bottom:12px">
                            @foreach($logo_images as $i => $logo)
                                <div style="position:relative;background:#fff;border:1.5px solid #e2e8f0;border-radius:8px;padding:6px">
                                    <img src="{{ asset('storage/' . $logo) }}" style="width:100%;height:50px;object-fit:contain">
                                    <button type="button" wire:click="removeLogo({{ $i }})" wire:confirm="حذف؟"
                                            style="position:absolute;top:-6px;right:-6px;width:20px;height:20px;background:#dc2626;color:#fff;border-radius:50%;border:2px solid #fff;font-size:10px;cursor:pointer;line-height:1">✕</button>
                                </div>
                            @endforeach
                        </div>
                    @endif

                    <input type="file" wire:model="logoUpload" accept="image/*"
                           style="width:100%;padding:8px;border:1.5px dashed #cbd5e1;border-radius:8px;font-size:12px">

                    <div style="display:grid;grid-template-columns:100px 1fr 60px;gap:10px;align-items:center;margin-top:12px">
                        <label style="font-size:12px;font-weight:700;color:#1a5276">اندازه</label>
                        <input type="range" min="20" max="120" step="4" wire:model.live.debounce.200ms="logo_size" class="range range-sm range-primary w-full">
                        <span style="font-family:monospace;font-size:11px;text-align:center;background:#fef3c7;padding:3px;border-radius:6px">{{ $logo_size }}px</span>
                    </div>

                    <button wire:click="saveLogos" class="btn btn-success btn-sm" style="margin-top:12px;width:100%">💾 ذخیره</button>
                </div>

                {{-- تصویر توضیحات --}}
                <div class="sg-settings-card">
                    <h3>📄 تصویر بخش Certificate</h3>
                    <p style="font-size:11px;color:#94a3b8;margin:0 0 10px">جایگزین متن "Certificate / Quality Guarantee"</p>

                    @if($desc_image)
                        <div style="margin-bottom:10px;padding:8px;background:#f8fafc;border-radius:8px;text-align:center">
                            <img src="{{ asset('storage/' . $desc_image) }}" style="max-width:100%;max-height:100px">
                            <button type="button" wire:click="$set('desc_image','')" class="btn btn-error btn-xs" style="margin-top:6px">🗑️ حذف</button>
                        </div>
                    @endif

                    <input type="file" wire:model="descUpload" accept="image/*"
                           style="width:100%;padding:8px;border:1.5px dashed #cbd5e1;border-radius:8px;font-size:12px">

                    <div style="display:grid;grid-template-columns:100px 1fr 60px;gap:10px;align-items:center;margin-top:12px">
                        <label style="font-size:12px;font-weight:700;color:#1a5276">عرض</label>
                        <input type="range" min="40" max="200" wire:model.live.debounce.200ms="desc_image_w" class="range range-sm range-primary w-full">
                        <span style="font-family:monospace;font-size:11px;text-align:center;background:#fef3c7;padding:3px;border-radius:6px">{{ $desc_image_w }}px</span>
                    </div>
                    <div style="display:grid;grid-template-columns:100px 1fr 60px;gap:10px;align-items:center;margin-top:8px">
                        <label style="font-size:12px;font-weight:700;color:#1a5276">ارتفاع</label>
                        <input type="range" min="30" max="150" wire:model.live.debounce.200ms="desc_image_h" class="range range-sm range-primary w-full">
                        <span style="font-family:monospace;font-size:11px;text-align:center;background:#fef3c7;padding:3px;border-radius:6px">{{ $desc_image_h }}px</span>
                    </div>

                    <button wire:click="saveLogos" class="btn btn-success btn-sm" style="margin-top:12px;width:100%">💾 ذخیره</button>
                </div>

                {{-- طرح‌های آماده --}}
                <div class="sg-settings-card">
                    <h3>💾 طرح‌های آماده</h3>
                    <p style="font-size:11px;color:#94a3b8;margin:0 0 10px">تنظیمات فعلی رو با یک نام ذخیره کن</p>

                    <div style="display:flex;gap:6px;margin-bottom:12px">
                        <input type="text" wire:model="new_template_name" placeholder="نام طرح..."
                               style="flex:1;padding:8px 10px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:12px">
                        <button wire:click="saveTemplate" class="btn btn-primary btn-sm">➕ ذخیره</button>
                    </div>

                    @if(count($templates))
                        <div style="display:flex;flex-direction:column;gap:6px">
                            @foreach($templates as $tpl)
                                <div style="display:flex;align-items:center;justify-content:space-between;padding:10px;background:#f8fafc;border:1px solid #e2e8f0;border-radius:8px">
                                    <div>
                                        <div style="font-weight:700;font-size:12px">{{ $tpl['name'] }}</div>
                                    </div>
                                    <div style="display:flex;gap:4px">
                                        <button wire:click="loadTemplate('{{ $tpl['id'] }}')"
                                                style="background:#1a5276;color:#fff;border:none;padding:5px 10px;border-radius:6px;font-size:11px;cursor:pointer;font-weight:700">
                                            بارگذاری
                                        </button>
                                        <button wire:click="deleteTemplate('{{ $tpl['id'] }}')" wire:confirm="حذف شود؟"
                                                style="background:#fee2e2;color:#dc2626;border:none;padding:5px 8px;border-radius:6px;font-size:11px;cursor:pointer">🗑️</button>
                                    </div>
                                </div>
                            @endforeach
                        </div>
                    @else
                        <div style="padding:16px;text-align:center;color:#94a3b8;font-size:11px">هنوز طرحی ذخیره نکردی</div>
                    @endif
                </div>
            </div>
        @endif

        {{-- ویرایشگر برچسب --}}
        @if($tab === 'labels')
            <livewire:settings.labels />
        @endif

        {{-- تصاویر --}}
        @if($tab === 'assets')
            <div class="sg-settings-card">
                <h3>🖼️ پس‌زمینه شناسنامه</h3>
                @if($bg_image)
                    <div style="margin-bottom:12px">
                        <img src="{{ $bg_image }}" style="max-width:120px;border-radius:10px;border:2px solid var(--gold)">
                    </div>
                @endif
                <input type="file" wire:model="bg_image" accept="image/*" class="form-control">
            </div>
        @endif

        {{-- سلامت --}}
        @if($tab === 'health')
            <livewire:settings.health />
        @endif
    </div>
</div>
'''

write('resources/views/livewire/settings/index.blade.php', SETTINGS)


# ═══════════════════════════════════════════════════════════════
# 2. VIEW MODAL — بدون ویرایشگر + با دانلود
# ═══════════════════════════════════════════════════════════════

VM = r'''<div>
@if($show && $certificate)
<div style="position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:96;display:flex;align-items:flex-start;justify-content:center;padding:10px;overflow-y:auto"
     @keydown.escape.window="$wire.close()">

    <div style="background:#fff;width:100%;max-width:820px;margin:10px auto;border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,.4);overflow:hidden;direction:rtl;font-family:Vazirmatn,Tahoma,sans-serif">

        <div style="background:linear-gradient(135deg,#1a5276,#0d3b5e);color:#fff;padding:14px 18px;display:flex;align-items:center;justify-content:space-between">
            <div>
                <h2 style="margin:0;font-size:16px;font-weight:700">شناسنامه #{{ $certificate->code }}</h2>
                <div style="font-size:11px;opacity:.8;font-family:monospace;margin-top:2px" dir="ltr">{{ $certificate->serial }}</div>
            </div>
            <button type="button" wire:click="close" style="width:32px;height:32px;border-radius:50%;background:rgba(255,255,255,.2);color:#fff;border:none;cursor:pointer;font-size:15px">X</button>
        </div>

        <div style="padding:16px;max-height:calc(100vh - 180px);overflow-y:auto">

            <div id="cert-card-area" style="background:repeating-conic-gradient(#f0f0f0 0% 25%, #fff 0% 50%) 50% / 20px 20px;border-radius:12px;padding:16px;display:flex;justify-content:center;overflow:auto;margin-bottom:16px">
                <div style="transform-origin:top center;max-width:100%">
                    {!! $cardHtml !!}
                </div>
            </div>

            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px">
                <div style="padding:10px;background:#f8fafc;border-radius:8px">
                    <div style="font-size:10px;color:#94a3b8">💎 سنگ</div>
                    <div style="font-size:13px;font-weight:700">{{ $certificate->stone_name }}</div>
                </div>
                <div style="padding:10px;background:#f8fafc;border-radius:8px">
                    <div style="font-size:10px;color:#94a3b8">⚙️ فلز</div>
                    <div style="font-size:13px">{{ $certificate->metal }} ({{ $certificate->metal_carat }})</div>
                </div>
                <div style="padding:10px;background:#f8fafc;border-radius:8px">
                    <div style="font-size:10px;color:#94a3b8">📐 ابعاد</div>
                    <div style="font-size:13px">{{ $certificate->length }}×{{ $certificate->width }} mm</div>
                </div>
                <div style="padding:10px;background:#f8fafc;border-radius:8px">
                    <div style="font-size:10px;color:#94a3b8">⚖️ وزن</div>
                    <div style="font-size:13px">{{ $certificate->weight }} gr</div>
                </div>
            </div>
        </div>

        <div style="padding:12px 18px;background:#f8fafc;border-top:1px solid #e2e8f0;display:flex;justify-content:space-between;gap:8px;flex-wrap:wrap">
            <button type="button" wire:click="delete" wire:confirm="حذف شود؟"
                    style="padding:9px 16px;background:#fee2e2;color:#dc2626;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">
                🗑️ حذف
            </button>

            <div style="display:flex;gap:6px;flex-wrap:wrap">
                <button type="button" onclick="downloadCertModal()"
                        style="padding:9px 16px;background:#0891b2;color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">
                    📥 دانلود PNG
                </button>
                <button type="button" onclick="window.open('{{ route('certificates.print', ['ids' => $certificate->id, 'auto' => 1]) }}', '_blank')"
                        style="padding:9px 16px;background:#1a5276;color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">
                    🖨️ چاپ
                </button>
                <button type="button" wire:click="edit"
                        style="padding:9px 16px;background:#16a34a;color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">
                    ✏️ ویرایش
                </button>
            </div>
        </div>
    </div>
</div>
@endif
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script>
function downloadCertModal() {
    var el = document.querySelector('#cert-card-area .certificate');
    if (!el) { alert('کارت پیدا نشد'); return; }

    var clone = el.cloneNode(true);
    var w = el.offsetWidth || 600;
    var h = el.offsetHeight || 600;

    clone.style.transform = 'none';
    clone.style.boxShadow = 'none';

    var wrap = document.createElement('div');
    wrap.style.cssText = 'position:fixed;left:-99999px;top:0;background:#fffef9;width:' + w + 'px;height:' + h + 'px';
    wrap.appendChild(clone);
    document.body.appendChild(wrap);

    html2canvas(clone, {
        scale: 3,
        backgroundColor: '#fffef9',
        useCORS: true,
        logging: false,
        width: w,
        height: h
    }).then(function(canvas) {
        wrap.remove();
        var a = document.createElement('a');
        a.download = 'certificate-{{ $certificate->code ?? "card" }}.png';
        a.href = canvas.toDataURL('image/png');
        a.click();
    }).catch(function(e) {
        wrap.remove();
        alert('خطا: ' + e.message);
    });
}
</script>
'''

write('resources/views/livewire/certificates/view-modal.blade.php', VM)


# ═══════════════════════════════════════════════════════════════
# 3. LAYOUT — اطمینان از اینکه همه modal ها لود می‌شن
# ═══════════════════════════════════════════════════════════════

layout = ROOT / 'resources' / 'views' / 'components' / 'layouts' / 'app.blade.php'
if layout.exists():
    txt = layout.read_text(encoding='utf-8')

    # حذف نسخه‌های قدیمی
    txt = txt.replace('<livewire:certificates.view-modal :key="\'cvm\'" />', '')
    txt = txt.replace('<livewire:certificates.create :key="\'cfm\'" />', '')

    # پیدا کردن @auth
    marker = '@auth'
    if marker in txt:
        modals = '''@auth
    <livewire:global-search />
    <livewire:components.shipment-timeline />
    <livewire:orders.import-postal :key="'imp'" />
    <livewire:orders.form-modal :key="'ofm'" />
    <livewire:orders.view-modal :key="'ovm'" />
    <livewire:customers.profile-modal :key="'cpm'" />
    <livewire:certificates.view-modal :key="'cvm'" />
    <livewire:certificates.create :key="'cfm'" />
@endauth'''
        # جایگزینی کامل @auth...@endauth
        import re
        txt = re.sub(r'@auth.*?@endauth', modals, txt, count=1, flags=re.DOTALL)

    layout.write_text(txt, encoding='utf-8')
    print("[OK] layout")


print()
print("=" * 60)
print("DONE")
print("=" * 60)
print()
print("Run:")
print("  php artisan view:clear")
print("  php artisan optimize:clear")
print("  php artisan serve")