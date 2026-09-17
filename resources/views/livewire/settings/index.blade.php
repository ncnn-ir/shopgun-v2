<div style="padding:0 0 18px" dir="rtl">

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
            'stones'      => ['💠', 'سنگ/فلز', false],
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
                    <div wire:loading wire:target="logoUpload" style="font-size:11px;color:#0891b2;margin-top:4px">⏳ در حال آپلود...</div>

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
                    <div wire:loading wire:target="descUpload" style="font-size:11px;color:#0891b2;margin-top:4px">⏳ در حال آپلود...</div>

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


        
        
        {{-- ═══════════ ویژگی‌های ووکامرس ═══════════ --}}
        @if($tab === 'stones')
            <div class="sg-settings-card" style="margin-bottom:14px;background:linear-gradient(135deg,#eef2ff,#e0e7ff);border-color:#6366f1">
                <h3 style="color:#3730a3">🌐 اتصال به ویژگی‌های ووکامرس</h3>
                <p style="font-size:12px;color:#3730a3;margin:0 0 12px;opacity:.85">
                    لیست ویژگی‌ها (Attributes) و اصطلاحات (Terms) را از سایت می‌خواند. یک ویژگی را به عنوان «سنگ» و یکی را به عنوان «فلز» انتخاب کن.
                </p>

                <button type="button" wire:click="fetchWooAttributes"
                        wire:loading.attr="disabled"
                        style="padding:9px 22px;background:linear-gradient(135deg,#6366f1,#4338ca);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">
                    <span wire:loading.remove wire:target="fetchWooAttributes">🌐 دریافت لیست ویژگی‌ها</span>
                    <span wire:loading wire:target="fetchWooAttributes">⏳ در حال دریافت...</span>
                </button>

                @if($woo_attr_status)
                    <div style="margin-top:10px;padding:8px 12px;border-radius:6px;font-size:12px;font-weight:700;
                        background:{{ str_starts_with($woo_attr_status, '✅') ? '#d1fae5' : (str_starts_with($woo_attr_status, '⏳') ? '#dbeafe' : '#fee2e2') }};
                        color:{{ str_starts_with($woo_attr_status, '✅') ? '#065f46' : (str_starts_with($woo_attr_status, '⏳') ? '#1e40af' : '#991b1b') }}">
                        {{ $woo_attr_status }}
                    </div>
                @endif

                @if(count($woo_attributes) > 0)
                    <div style="margin-top:14px">
                        <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:8px;flex-wrap:wrap;gap:8px">
                            <div style="font-size:12px;font-weight:700;color:#3730a3">
                                ویژگی‌ها ({{ \App\Support\PersianNumber::toFa(count($woo_attributes)) }})
                            </div>
                            @if($woo_stone_attribute_id || $woo_metal_attribute_id)
                                <div style="font-size:11px;color:#3730a3;display:flex;gap:8px;flex-wrap:wrap">
                                    @if($woo_stone_attribute_id)
                                        <span style="background:#d1fae5;padding:3px 8px;border-radius:6px">💎 سنگ: <b>{{ $woo_stone_attribute_name }}</b></span>
                                    @endif
                                    @if($woo_metal_attribute_id)
                                        <span style="background:#d1fae5;padding:3px 8px;border-radius:6px">⚙️ فلز: <b>{{ $woo_metal_attribute_name }}</b></span>
                                    @endif
                                </div>
                            @endif
                        </div>

                        <div style="max-height:400px;overflow-y:auto;border:1px solid #c7d2fe;border-radius:8px;background:#fff">
                            <table style="width:100%;border-collapse:collapse;font-size:12px">
                                <thead style="position:sticky;top:0;background:#eef2ff;z-index:1">
                                    <tr>
                                        <th style="padding:8px;text-align:right;color:#3730a3">نام</th>
                                        <th style="padding:8px;text-align:right;color:#3730a3">slug</th>
                                        <th style="padding:8px;text-align:right;color:#3730a3">انتخاب</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    @foreach($woo_attributes as $a)
                                        <tr wire:key="woo-attr-{{ $a['id'] }}" style="border-bottom:1px solid #f1f5f9">
                                            <td style="padding:8px;font-weight:700;color:#1e293b">{{ $a['name'] }}</td>
                                            <td style="padding:8px;font-family:monospace;font-size:11px;color:#64748b" dir="ltr">{{ $a['slug'] }}</td>
                                            <td style="padding:8px">
                                                <div style="display:flex;gap:4px;flex-wrap:wrap">
                                                    <button type="button"
                                                            wire:click="pickStoneAttribute({{ $a['id'] }})"
                                                            wire:loading.attr="disabled"
                                                            style="padding:5px 10px;border:1.5px solid {{ $woo_stone_attribute_id === $a['id'] ? '#16a34a' : '#cbd5e1' }};background:{{ $woo_stone_attribute_id === $a['id'] ? '#d1fae5' : '#fff' }};color:{{ $woo_stone_attribute_id === $a['id'] ? '#065f46' : '#475569' }};border-radius:6px;font-size:11px;font-weight:700;cursor:pointer">
                                                        💎 سنگ
                                                    </button>
                                                    <button type="button"
                                                            wire:click="pickMetalAttribute({{ $a['id'] }})"
                                                            wire:loading.attr="disabled"
                                                            style="padding:5px 10px;border:1.5px solid {{ $woo_metal_attribute_id === $a['id'] ? '#16a34a' : '#cbd5e1' }};background:{{ $woo_metal_attribute_id === $a['id'] ? '#d1fae5' : '#fff' }};color:{{ $woo_metal_attribute_id === $a['id'] ? '#065f46' : '#475569' }};border-radius:6px;font-size:11px;font-weight:700;cursor:pointer">
                                                        ⚙️ فلز
                                                    </button>
                                                </div>
                                            </td>
                                        </tr>
                                    @endforeach
                                </tbody>
                            </table>
                        </div>
                    </div>
                @endif

                {{-- اصطلاحات سنگ --}}
                @if(count($woo_stone_terms) > 0)
                    <div style="margin-top:16px;padding:12px;background:#fff;border:1.5px solid #16a34a;border-radius:10px">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;flex-wrap:wrap;gap:8px">
                            <div style="font-weight:700;color:#15803d;font-size:13px">
                                💎 اصطلاحات «{{ $woo_stone_attribute_name }}» ({{ \App\Support\PersianNumber::toFa(count($woo_stone_terms)) }})
                            </div>
                            <button type="button" wire:click="applyWooTermsAsStones"
                                    wire:confirm="همه این اصطلاحات به سنگ‌های شما اضافه شوند؟"
                                    style="padding:7px 16px;background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">
                                ➕ افزودن همه به سنگ‌ها
                            </button>
                        </div>
                        <div style="max-height:250px;overflow-y:auto;display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:6px">
                            @foreach($woo_stone_terms as $t)
                                <div style="padding:6px 10px;background:#f0fdf4;border:1px solid #bbf7d0;border-radius:6px;font-size:11px;display:flex;justify-content:space-between;align-items:center;gap:4px">
                                    <span style="font-weight:700;color:#1e293b;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ $t['name'] }}</span>
                                    @if($t['count'] > 0)
                                        <span style="background:#16a34a;color:#fff;padding:1px 6px;border-radius:8px;font-size:9px;font-weight:700">{{ $t['count'] }}</span>
                                    @endif
                                </div>
                            @endforeach
                        </div>
                    </div>
                @endif

                {{-- اصطلاحات فلز --}}
                @if(count($woo_metal_terms) > 0)
                    <div style="margin-top:16px;padding:12px;background:#fff;border:1.5px solid #0891b2;border-radius:10px">
                        <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px;flex-wrap:wrap;gap:8px">
                            <div style="font-weight:700;color:#0e7490;font-size:13px">
                                ⚙️ اصطلاحات «{{ $woo_metal_attribute_name }}» ({{ \App\Support\PersianNumber::toFa(count($woo_metal_terms)) }})
                            </div>
                            <button type="button" wire:click="applyWooTermsAsMetals"
                                    wire:confirm="همه این اصطلاحات به فلزات شما اضافه شوند؟"
                                    style="padding:7px 16px;background:linear-gradient(135deg,#0891b2,#0e7490);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">
                                ➕ افزودن همه به فلزات
                            </button>
                        </div>
                        <div style="max-height:200px;overflow-y:auto;display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:6px">
                            @foreach($woo_metal_terms as $t)
                                <div style="padding:6px 10px;background:#ecfeff;border:1px solid #a5f3fc;border-radius:6px;font-size:11px;display:flex;justify-content:space-between;align-items:center;gap:4px">
                                    <span style="font-weight:700;color:#1e293b;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ $t['name'] }}</span>
                                    @if($t['count'] > 0)
                                        <span style="background:#0891b2;color:#fff;padding:1px 6px;border-radius:8px;font-size:9px;font-weight:700">{{ $t['count'] }}</span>
                                    @endif
                                </div>
                            @endforeach
                        </div>
                    </div>
                @endif
            </div>
        @endif

{{-- ═══════════ Fetch + Import سنگ‌ها ═══════════ --}}
        @if($tab === 'stones')

            {{-- Fetch از سایت --}}
            <div class="sg-settings-card" style="margin-bottom:14px;background:linear-gradient(135deg,#eff6ff,#dbeafe);border-color:#3b82f6">
                <h3 style="color:#1e40af">🌐 دریافت سنگ‌ها از سایت</h3>
                <p style="font-size:12px;color:#1e40af;margin:0 0 12px;opacity:.85">
                    محصولات را از ووکامرس می‌خواند و سنگ‌ها/فلزات موجود در نام و ویژگی‌های آن‌ها را استخراج می‌کند
                </p>

                <div style="display:flex;gap:10px;flex-wrap:wrap;align-items:center">
                    <label style="font-size:12px;font-weight:700;color:#1e40af">تعداد محصولات:</label>
                    <input type="number" wire:model="fetch_limit" min="50" max="1000" step="50"
                           style="width:100px;padding:7px 10px;border:1.5px solid #93c5fd;border-radius:6px;font-family:monospace;text-align:center">

                    <button type="button" wire:click="fetchStonesFromWoo"
                            wire:loading.attr="disabled"
                            style="padding:9px 22px;background:linear-gradient(135deg,#3b82f6,#1e40af);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">
                        <span wire:loading.remove wire:target="fetchStonesFromWoo">🌐 دریافت از سایت</span>
                        <span wire:loading wire:target="fetchStonesFromWoo">⏳ در حال دریافت...</span>
                    </button>
                </div>

                @if($fetch_status)
                    <div style="margin-top:10px;padding:8px 12px;border-radius:6px;font-size:12px;font-weight:700;
                        background:{{ str_starts_with($fetch_status, '✅') ? '#d1fae5' : (str_starts_with($fetch_status, '⏳') ? '#dbeafe' : '#fee2e2') }};
                        color:{{ str_starts_with($fetch_status, '✅') ? '#065f46' : (str_starts_with($fetch_status, '⏳') ? '#1e40af' : '#991b1b') }}">
                        {{ $fetch_status }}
                    </div>
                @endif
            </div>

            {{-- JSON Import --}}
            <div class="sg-settings-card" style="margin-bottom:14px;background:linear-gradient(135deg,#fef3c7,#fde68a);border-color:#d97706">
                <h3 style="color:#78350f">📥 ایمپورت سنگ‌ها از JSON</h3>

                <details style="margin-bottom:10px">
                    <summary style="cursor:pointer;font-size:12px;font-weight:700;color:#78350f;padding:6px 0">
                        📋 فرمت JSON مورد قبول (کلیک کن)
                    </summary>

                    <div style="background:#fff;border:1px solid #fbbf24;border-radius:8px;padding:12px;margin-top:8px;direction:ltr;font-family:monospace;font-size:11px;white-space:pre-wrap;overflow-x:auto;max-height:300px">
{
  "stones": [
    {
      "name": "فیروزه عجمی",
      "en": "Turquoise Ajami",
      "origin": "نیشابور",
      "flag": "ir",
      "icon": "💠"
    },
    {
      "name": "عقیق یمانی",
      "en": "Yemeni Agate",
      "origin": "یمن",
      "flag": "ye",
      "icon": "🔴"
    }
  ]
}
                    </div>

                    <div style="margin-top:10px;font-size:11px;color:#78350f;line-height:1.8">
                        <b>راهنما:</b><br>
                        • <code>stones</code> — آرایه‌ای از سنگ‌ها (اختیاری، می‌توانی مستقیم آرایه بفرستی)<br>
                        • <code>name</code> — نام فارسی سنگ (اجباری)<br>
                        • <code>en</code> — نام انگلیسی<br>
                        • <code>origin</code> — اصالت (مثلاً «نیشابور»)<br>
                        • <code>flag</code> — کد دو حرفی کشور (ir, ye, iq, af, za, mm, lk, co, br, au, it, eg, cn)<br>
                        • <code>icon</code> — ایموجی آیکون<br>
                        • اگر سنگی از قبل موجود باشد، <b>بروزرسانی</b> می‌شود<br>
                        • اگر جدید باشد، <b>اضافه</b> می‌شود
                    </div>
                </details>

                <textarea wire:model="json_input" rows="6" placeholder='{"stones": [{"name": "...", "en": "...", ...}]}'
                          style="width:100%;padding:10px;border:1.5px solid #fbbf24;border-radius:8px;font-family:monospace;font-size:12px;box-sizing:border-box;direction:ltr;background:#fff;resize:vertical"></textarea>

                <div style="display:flex;gap:6px;margin-top:10px;flex-wrap:wrap">
                    <button type="button" wire:click="importStonesJson"
                            wire:loading.attr="disabled"
                            style="padding:8px 18px;background:linear-gradient(135deg,#d97706,#92400e);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">
                        <span wire:loading.remove wire:target="importStonesJson">📥 ایمپورت</span>
                        <span wire:loading wire:target="importStonesJson">⏳...</span>
                    </button>

                    <button type="button" wire:click="$set('json_input','')"
                            style="padding:8px 18px;background:#fff;color:#475569;border:1.5px solid #cbd5e1;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">
                        پاک کردن
                    </button>
                </div>

                @if($json_status)
                    <div style="margin-top:10px;padding:8px 12px;border-radius:6px;font-size:12px;font-weight:700;
                        background:{{ str_starts_with($json_status, '✅') ? '#d1fae5' : '#fee2e2' }};
                        color:{{ str_starts_with($json_status, '✅') ? '#065f46' : '#991b1b' }}">
                        {{ $json_status }}
                    </div>
                @endif
            </div>

            {{-- ابزارها --}}
            <div class="sg-settings-card" style="margin-bottom:14px">
                <h3>🛠️ ابزارها</h3>
                <div style="display:flex;gap:6px;flex-wrap:wrap">
                    <button type="button" wire:click="resetStonesToDefault" wire:confirm="همه سنگ‌ها به پیش‌فرض برگردند؟"
                            style="padding:7px 14px;background:#f1f5f9;color:#475569;border:1.5px solid #cbd5e1;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">
                        ↺ بازگشت به پیش‌فرض
                    </button>
                    <button type="button" wire:click="clearAllStones" wire:confirm="همه سنگ‌ها پاک شوند؟"
                            style="padding:7px 14px;background:#fee2e2;color:#dc2626;border:1.5px solid #fca5a5;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">
                        🗑️ پاک کردن همه
                    </button>
                </div>
            </div>
        @endif

{{-- ═══════════ سنگ و فلز ═══════════ --}}
        @if($tab === 'stones')
            <div style="display:grid;grid-template-columns:1fr;gap:14px">

                {{-- سنگ‌ها --}}
                <div class="sg-settings-card">
                    <h3>💎 سنگ‌ها ({{ \App\Support\PersianNumber::toFa(count($cert_stones)) }})</h3>

                    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:8px;margin-bottom:16px">
                        @foreach($cert_stones as $i => $s)
                            <div style="position:relative;background:#fff;border:2px solid #e2e8f0;border-radius:10px;padding:8px;text-align:center">
                                <div style="font-size:24px;margin-bottom:4px">{{ $s['icon'] ?? '💎' }}</div>
                                <div style="font-size:11px;font-weight:700;color:#1e293b">{{ $s['name'] }}</div>
                                <div style="font-size:9px;color:#94a3b8">{{ $s['origin'] ?? '' }}</div>
                                <div style="display:flex;gap:3px;margin-top:6px;justify-content:center">
                                    <button type="button" wire:click="editStone({{ $i }})"
                                            style="background:#e0e7ff;color:#3730a3;border:none;width:24px;height:24px;border-radius:6px;font-size:11px;cursor:pointer;font-weight:700">✏️</button>
                                    <button type="button" wire:click="removeStone({{ $i }})" wire:confirm="حذف شود؟"
                                            style="background:#fee2e2;color:#dc2626;border:none;width:24px;height:24px;border-radius:6px;font-size:11px;cursor:pointer">🗑️</button>
                                </div>
                            </div>
                        @endforeach
                    </div>

                    <h3 style="margin-top:16px">{{ $editing_stone_idx !== null ? '✏️ ویرایش سنگ' : '➕ افزودن سنگ جدید' }}</h3>
                    <div class="form-grid">
                        <div class="field col-6">
                            <label>نام فارسی</label>
                            <input type="text" wire:model="new_stone_name" placeholder="مثلاً: فیروزه عجمی">
                        </div>
                        <div class="field col-6">
                            <label>نام انگلیسی</label>
                            <input type="text" wire:model="new_stone_en" dir="ltr" placeholder="Turquoise Ajami">
                        </div>
                        <div class="field col-4">
                            <label>اصالت</label>
                            <input type="text" wire:model="new_stone_origin" placeholder="نیشابور">
                        </div>
                        <div class="field col-4">
                            <label>پرچم</label>
                            <select wire:model="new_stone_flag" style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px">
                                <option value="ir">🇮🇷 ایران</option>
                                <option value="ye">🇾🇪 یمن</option>
                                <option value="iq">🇮🇶 عراق</option>
                                <option value="af">🇦🇫 افغانستان</option>
                                <option value="za">🇿🇦 آفریقا</option>
                                <option value="mm">🇲🇲 میانمار</option>
                                <option value="co">🇨🇴 کلمبیا</option>
                                <option value="lk">🇱🇰 سری‌لانکا</option>
                                <option value="br">🇧🇷 برزیل</option>
                                <option value="au">🇦🇺 استرالیا</option>
                                <option value="it">🇮🇹 ایتالیا</option>
                                <option value="eg">🇪🇬 مصر</option>
                            </select>
                        </div>
                        <div class="field col-4">
                            <label>آیکون</label>
                            <input type="text" wire:model="new_stone_icon" style="text-align:center;font-size:20px">
                        </div>
                    </div>

                    <div style="display:flex;gap:6px;margin-top:10px">
                        <button type="button" wire:click="addStone" class="btn btn-primary">
                            {{ $editing_stone_idx !== null ? '✏️ ویرایش' : '➕ افزودن' }}
                        </button>
                        @if($editing_stone_idx !== null)
                            <button type="button" wire:click="cancelStoneEdit" class="btn btn-ghost">انصراف</button>
                        @endif
                    </div>
                </div>

                {{-- فلزات --}}
                <div class="sg-settings-card">
                    <h3>⚙️ فلزات ({{ \App\Support\PersianNumber::toFa(count($cert_metals)) }})</h3>

                    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:8px;margin-bottom:16px">
                        @foreach($cert_metals as $i => $m)
                            <div style="background:#f8fafc;border:1.5px solid #e2e8f0;border-radius:8px;padding:10px;display:flex;align-items:center;justify-content:space-between">
                                <div>
                                    <div style="font-weight:700;font-size:12px;color:#1e293b">{{ $m['name'] }}</div>
                                    <div style="font-size:10px;color:#94a3b8" dir="ltr">{{ $m['carat'] ?? '' }}</div>
                                </div>
                                <div style="display:flex;gap:3px">
                                    <button type="button" wire:click="editMetal({{ $i }})"
                                            style="background:#e0e7ff;color:#3730a3;border:none;width:22px;height:22px;border-radius:5px;font-size:10px;cursor:pointer">✏️</button>
                                    <button type="button" wire:click="removeMetal({{ $i }})" wire:confirm="حذف شود؟"
                                            style="background:#fee2e2;color:#dc2626;border:none;width:22px;height:22px;border-radius:5px;font-size:10px;cursor:pointer">🗑️</button>
                                </div>
                            </div>
                        @endforeach
                    </div>

                    <h3 style="margin-top:16px">{{ $editing_metal_idx !== null ? '✏️ ویرایش فلز' : '➕ افزودن فلز' }}</h3>
                    <div class="form-grid">
                        <div class="field col-4">
                            <label>نام فارسی</label>
                            <input type="text" wire:model="new_metal_name" placeholder="نقره 925">
                        </div>
                        <div class="field col-4">
                            <label>نام انگلیسی</label>
                            <input type="text" wire:model="new_metal_en" dir="ltr" placeholder="Silver 925">
                        </div>
                        <div class="field col-4">
                            <label>عیار</label>
                            <input type="text" wire:model="new_metal_carat" dir="ltr" placeholder="925">
                        </div>
                    </div>
                    <button type="button" wire:click="addMetal" class="btn btn-primary" style="margin-top:10px">
                        {{ $editing_metal_idx !== null ? '✏️ ویرایش' : '➕ افزودن' }}
                    </button>
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
