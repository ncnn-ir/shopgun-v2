<div style="padding:14px 14px 20px;direction:rtl">

    {{-- ═══ Header ═══ --}}
    <div style="margin-bottom:16px">
        <h1 style="margin:0;font-size:22px;font-weight:700">⚙️ تنظیمات</h1>
        <p style="margin:4px 0 0;font-size:12px;color:#64748b">تنظیمات سیستم به ۴ گروه اصلی تقسیم شده</p>
    </div>

    {{-- ═══ Group Cards (Level 1) ═══ --}}
    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:10px;margin-bottom:16px">
        @foreach($groups as $key => $g)
            @php $isActive = $group === $key; @endphp
            <button type="button" wire:click="setGroup('{{ $key }}')"
                    style="padding:14px 12px;border-radius:12px;cursor:pointer;text-align:right;transition:all .18s;
                        border:2px solid {{ $isActive ? '#c9a84c' : '#e2e8f0' }};
                        background:{{ $isActive ? 'linear-gradient(135deg,#fef3c7,#fde68a)' : '#fff' }};
                        box-shadow:{{ $isActive ? '0 4px 12px rgba(201,168,76,.25)' : '0 1px 3px rgba(0,0,0,.04)' }}">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:6px">
                    <span style="font-size:22px">{{ $g['icon'] }}</span>
                    <span style="font-size:14px;font-weight:700;color:{{ $isActive ? '#78350f' : '#1e293b' }}">{{ $g['label'] }}</span>
                </div>
                <div style="font-size:10.5px;color:{{ $isActive ? '#92400e' : '#94a3b8' }}">{{ $g['desc'] }}</div>
                <div style="font-size:10px;color:#94a3b8;margin-top:4px">{{ \App\Support\PersianNumber::toFa(count($g['tabs'])) }} تب</div>
            </button>
        @endforeach
    </div>

    {{-- ═══ Sub-tabs (Level 2) ═══ --}}
    <div style="display:flex;gap:6px;overflow-x:auto;padding:6px 2px 12px;border-bottom:2px solid #e2e8f0;margin-bottom:14px">
        @foreach($groups[$group]['tabs'] as $k => $meta)
            @php $isTab = $tab === $k; @endphp
            <button type="button" wire:click="setTab('{{ $k }}')"
                    style="flex:0 0 auto;padding:8px 14px;border-radius:10px;font-size:12px;font-weight:700;white-space:nowrap;cursor:pointer;transition:all .12s;
                        border:1.5px solid {{ $isTab ? '#1a5276' : '#e2e8f0' }};
                        background:{{ $isTab ? 'linear-gradient(135deg,#1a5276,#0d3b5e)' : '#fff' }};
                        color:{{ $isTab ? '#fff' : '#64748b' }}">
                {{ $meta[0] }} {{ $meta[1] }}
            </button>
        @endforeach
    </div>

    {{-- ═══ Content ═══ --}}

    {{-- ═══ SYSTEM > GENERAL ═══ --}}
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
            <div style="display:flex;justify-content:flex-end;padding-top:14px;border-top:1px solid #e2e8f0">
                <button wire:click="saveGeneral" style="padding:9px 22px;background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">💾 ذخیره</button>
            </div>
        </div>
    @endif

    {{-- ═══ SYSTEM > APPEARANCE ═══ --}}
    @if($tab === 'appearance')
        <div class="sg-settings-card">
            <h3>ظاهر برنامه</h3>
            <div class="form-grid">
                <div class="field col-6">
                    <label>🌓 تم</label>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:6px">
                        @foreach(['light'=>'☀️ روشن','dark'=>'🌙 تیره'] as $k=>$v)
                            <button type="button" wire:click="$set('theme','{{ $k }}')"
                                    style="padding:9px;border-radius:8px;font-weight:700;font-size:12px;cursor:pointer;border:2px solid {{ $theme===$k ? '#c9a84c' : '#e2e8f0' }};background:{{ $theme===$k ? '#fef3c7' : '#fff' }}">{{ $v }}</button>
                        @endforeach
                    </div>
                </div>
                <div class="field col-6">
                    <label>📐 تراکم</label>
                    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:6px">
                        @foreach(['compact'=>'فشرده','normal'=>'معمولی','comfortable'=>'راحت'] as $k=>$v)
                            <button type="button" wire:click="$set('density','{{ $k }}')"
                                    style="padding:9px;border-radius:8px;font-weight:700;font-size:11px;cursor:pointer;border:2px solid {{ $density===$k ? '#c9a84c' : '#e2e8f0' }};background:{{ $density===$k ? '#fef3c7' : '#fff' }}">{{ $v }}</button>
                        @endforeach
                    </div>
                </div>
                <div class="field col-6">
                    <label>🎨 رنگ اصلی</label>
                    <input type="color" wire:model.live="primary_color" style="height:42px;padding:4px;cursor:pointer">
                </div>
                <div class="field col-6">
                    <label>✨ رنگ تاکیدی</label>
                    <input type="color" wire:model.live="accent_color" style="height:42px;padding:4px;cursor:pointer">
                </div>
                <div class="field col-12">
                    <label>🔤 فونت</label>
                    <select wire:model.live="font_family" style="width:100%;padding:9px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:13px">
                        <option value="Vazirmatn">وزیرمتن</option>
                        <option value="Tahoma">تاهوما</option>
                        <option value="system-ui">سیستم</option>
                        <option value="Arial">Arial</option>
                    </select>
                </div>
            </div>
            <div style="display:flex;justify-content:flex-end;padding-top:14px;border-top:1px solid #e2e8f0">
                <button wire:click="saveAppearance" style="padding:9px 22px;background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">💾 ذخیره</button>
            </div>
        </div>
    @endif

    {{-- ═══ SYSTEM > NOTIFICATIONS ═══ --}}
    @if($tab === 'notifications')
        <div class="sg-settings-card">
            <h3>اعلان‌ها</h3>
            <p style="font-size:11.5px;color:#94a3b8;margin:0 0 12px">کدام رویدادها اعلان ایجاد کنند</p>
            <div style="display:flex;flex-direction:column;gap:8px">
                <label style="display:flex;align-items:center;gap:8px;padding:10px;background:#f8fafc;border-radius:8px;cursor:pointer">
                    <input type="checkbox" wire:model="notif_order_created" style="width:18px;height:18px;accent-color:#c9a84c">
                    <div>
                        <div style="font-weight:700;font-size:12.5px">📦 سفارش جدید</div>
                        <div style="font-size:10.5px;color:#94a3b8">هنگام ایجاد سفارش جدید</div>
                    </div>
                </label>
                <label style="display:flex;align-items:center;gap:8px;padding:10px;background:#f8fafc;border-radius:8px;cursor:pointer">
                    <input type="checkbox" wire:model="notif_order_status" style="width:18px;height:18px;accent-color:#c9a84c">
                    <div>
                        <div style="font-weight:700;font-size:12.5px">🔄 تغییر وضعیت سفارش</div>
                        <div style="font-size:10.5px;color:#94a3b8">هنگام تغییر وضعیت</div>
                    </div>
                </label>
                <label style="display:flex;align-items:center;gap:8px;padding:10px;background:#f8fafc;border-radius:8px;cursor:pointer">
                    <input type="checkbox" wire:model="notif_certificate_issued" style="width:18px;height:18px;accent-color:#c9a84c">
                    <div>
                        <div style="font-weight:700;font-size:12.5px">💎 صدور شناسنامه</div>
                        <div style="font-size:10.5px;color:#94a3b8">هنگام صدور شناسنامه جدید</div>
                    </div>
                </label>
                <label style="display:flex;align-items:center;gap:8px;padding:10px;background:#f8fafc;border-radius:8px;cursor:pointer">
                    <input type="checkbox" wire:model="notif_api_error" style="width:18px;height:18px;accent-color:#c9a84c">
                    <div>
                        <div style="font-weight:700;font-size:12.5px">⚠️ خطای API</div>
                        <div style="font-size:10.5px;color:#94a3b8">هنگام بروز خطا در ووکامرس</div>
                    </div>
                </label>
            </div>
            <div style="display:flex;justify-content:flex-end;padding-top:14px;border-top:1px solid #e2e8f0;margin-top:14px">
                <button wire:click="saveNotifications" style="padding:9px 22px;background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">💾 ذخیره</button>
            </div>
        </div>
    @endif

    {{-- ═══ SYSTEM > MAINTENANCE ═══ --}}
    @if($tab === 'maintenance')
        <div class="sg-settings-card">
            <h3>🔧 نگهداری</h3>

            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-bottom:14px">
                <div style="padding:12px;background:#f8fafc;border-radius:8px;text-align:center">
                    <div style="font-size:24px;font-weight:800;color:#1a5276">{{ \App\Support\PersianNumber::toFa($stats['php']) }}</div>
                    <div style="font-size:10.5px;color:#64748b">PHP</div>
                </div>
                <div style="padding:12px;background:#f8fafc;border-radius:8px;text-align:center">
                    <div style="font-size:14px;font-weight:800;color:#1a5276">v{{ $stats['laravel'] }}</div>
                    <div style="font-size:10.5px;color:#64748b">Laravel</div>
                </div>
                <div style="padding:12px;background:#f8fafc;border-radius:8px;text-align:center">
                    <div style="font-size:20px;font-weight:800;color:#16a34a">{{ \App\Support\PersianNumber::toFa($stats['orders']) }}</div>
                    <div style="font-size:10.5px;color:#64748b">سفارش</div>
                </div>
                <div style="padding:12px;background:#f8fafc;border-radius:8px;text-align:center">
                    <div style="font-size:20px;font-weight:800;color:#16a34a">{{ \App\Support\PersianNumber::toFa($stats['certificates']) }}</div>
                    <div style="font-size:10.5px;color:#64748b">شناسنامه</div>
                </div>
            </div>

            <h3 style="margin-top:14px">🛠️ ابزارها</h3>
            <div style="display:flex;flex-direction:column;gap:6px">
                <button type="button" onclick="fetch('/artisan-clear', {method:'POST', headers:{'X-CSRF-TOKEN':document.querySelector('meta[name=csrf-token]').content}}).then(()=>alert('کش پاک شد'))"
                        style="padding:10px 14px;background:#fff;color:#475569;border:1.5px solid #cbd5e1;border-radius:8px;font-weight:700;cursor:pointer;text-align:right;font-size:12.5px">
                    🧹 پاک‌سازی کش (optimize:clear)
                </button>
            </div>
        </div>
    @endif

    {{-- ═══ COMMERCE > WOO ═══ --}}
    @if($tab === 'woo')
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
                <div style="padding:10px;border-radius:8px;margin-top:10px;background:{{ $commerce_test_result['ok'] ? '#d1fae5' : '#fee2e2' }};color:{{ $commerce_test_result['ok'] ? '#065f46' : '#991b1b' }};font-weight:700;font-size:12.5px">
                    {{ $commerce_test_result['message'] }}
                </div>
            @endif

            <div style="display:flex;gap:6px;padding-top:14px;border-top:1px solid #e2e8f0;margin-top:14px;flex-wrap:wrap">
                <button wire:click="saveCommerce" style="padding:8px 18px;background:#1a5276;color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:12.5px">💾 ذخیره</button>
                <button wire:click="testCommerce" wire:loading.attr="disabled" style="padding:8px 18px;background:linear-gradient(135deg,#0891b2,#0e7490);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:12.5px">
                    <span wire:loading.remove wire:target="testCommerce">🔌 تست اتصال</span>
                    <span wire:loading wire:target="testCommerce">⏳...</span>
                </button>
            </div>
        </div>
    @endif

    {{-- ═══ COMMERCE > SYNC ═══ --}}
    @if($tab === 'sync')
        <div class="sg-settings-card">
            <h3>🔄 سینک و ایمپورت</h3>

            <div style="display:grid;grid-template-columns:1fr;gap:12px;margin-bottom:14px">
                <div style="padding:12px;background:linear-gradient(135deg,#f0fdf4,#dcfce7);border:1.5px solid #16a34a;border-radius:10px">
                    <div style="font-size:13px;font-weight:700;color:#15803d;margin-bottom:8px">📥 دریافت سفارشات</div>
                    <div style="font-size:11px;color:#166534;margin-bottom:8px">
                        آخرین سینک: {{ $woo_last_orders_sync ? \App\Support\PersianDate::format($woo_last_orders_sync, 'Y/m/d H:i') : 'هرگز' }}
                    </div>
                    <div style="display:flex;gap:6px;flex-wrap:wrap">
                        <input type="number" wire:model="sync_limit" min="10" max="500"
                               style="width:100px;padding:6px 10px;border:1.5px solid #16a34a;border-radius:6px;font-family:monospace;text-align:center">
                        <button wire:click="syncOrdersFromWoo" wire:loading.attr="disabled"
                                style="padding:7px 16px;background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">
                            <span wire:loading.remove wire:target="syncOrdersFromWoo">📥 دریافت سفارشات</span>
                            <span wire:loading wire:target="syncOrdersFromWoo">⏳...</span>
                        </button>
                        <button wire:click="syncCustomersFromWoo" wire:loading.attr="disabled"
                                style="padding:7px 16px;background:linear-gradient(135deg,#0891b2,#0e7490);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">
                            <span wire:loading.remove wire:target="syncCustomersFromWoo">👥 دریافت مشتریان</span>
                            <span wire:loading wire:target="syncCustomersFromWoo">⏳...</span>
                        </button>
                        <button wire:click="syncWooCatalog" wire:loading.attr="disabled"
                                style="padding:7px 16px;background:linear-gradient(135deg,#7c3aed,#5b21b6);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">
                            <span wire:loading.remove wire:target="syncWooCatalog">🔄 سینک کاتالوگ</span>
                            <span wire:loading wire:target="syncWooCatalog">⏳...</span>
                        </button>
                        <button wire:click="syncProductsFromWoo" wire:loading.attr="disabled"
                                style="padding:7px 16px;background:linear-gradient(135deg,#f59e0b,#d97706);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">
                            <span wire:loading.remove wire:target="syncProductsFromWoo">📦 سینک محصولات</span>
                            <span wire:loading wire:target="syncProductsFromWoo">⏳...</span>
                        </button>
                    </div>
                </div>

                <div style="padding:12px;background:#eff6ff;border:1.5px solid #3b82f6;border-radius:10px">
                    <div style="font-size:13px;font-weight:700;color:#1e40af;margin-bottom:8px">📋 وضعیت‌هایی که از سایت دریافت شوند</div>
                    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:6px">
                        @foreach([
                            'pending' => '📝 در انتظار',
                            'processing' => '⚙️ پردازش',
                            'on-hold' => '⏸️ تعلیق',
                            'completed' => '✅ تکمیل',
                            'cancelled' => '❌ لغو',
                            'refunded' => '↩️ مرجوع',
                            'failed' => '⚠️ ناموفق',
                        ] as $k => $label)
                            <label style="display:flex;align-items:center;gap:6px;padding:6px 10px;background:#fff;border:1.5px solid {{ in_array($k, $wc_status_filter, true) ? '#16a34a' : '#e2e8f0' }};border-radius:8px;cursor:pointer;font-size:11.5px;font-weight:700;color:{{ in_array($k, $wc_status_filter, true) ? '#15803d' : '#475569' }}">
                                <input type="checkbox" wire:model="wc_status_filter" value="{{ $k }}" style="accent-color:#16a34a">
                                <span>{{ $label }}</span>
                            </label>
                        @endforeach
                    </div>
                    <button wire:click="saveWcStatusFilter" style="margin-top:10px;padding:6px 14px;background:#1e40af;color:#fff;border:none;border-radius:6px;font-weight:700;cursor:pointer;font-size:11.5px">💾 ذخیره فیلتر</button>
                </div>

                @if($woo_sync_status)
                    <div style="padding:10px;border-radius:8px;font-size:12px;font-weight:700;background:{{ str_starts_with($woo_sync_status, '✅') ? '#d1fae5' : (str_starts_with($woo_sync_status, '⏳') ? '#dbeafe' : '#fee2e2') }};color:{{ str_starts_with($woo_sync_status, '✅') ? '#065f46' : (str_starts_with($woo_sync_status, '⏳') ? '#1e40af' : '#991b1b') }}">
                        {{ $woo_sync_status }}
                    </div>
                @endif
            </div>
        </div>
    @endif

    {{-- ═══ COMMERCE > API MONITOR ═══ --}}
    @if($tab === 'api-monitor')
        @php $this->loadApiMonitor(); @endphp
        <div class="sg-settings-card">
            <h3>📊 رصد API ووکامرس</h3>

            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:8px;margin-bottom:14px">
                <div style="padding:10px;background:#f8fafc;border-radius:8px;text-align:center">
                    <div style="font-size:20px;font-weight:800;color:#1a5276">{{ \App\Support\PersianNumber::toFa($api_stats['total'] ?? 0) }}</div>
                    <div style="font-size:10.5px;color:#64748b">کل درخواست‌ها</div>
                </div>
                <div style="padding:10px;background:#d1fae5;border-radius:8px;text-align:center">
                    <div style="font-size:20px;font-weight:800;color:#065f46">{{ \App\Support\PersianNumber::toFa($api_stats['today'] ?? 0) }}</div>
                    <div style="font-size:10.5px;color:#065f46">امروز</div>
                </div>
                <div style="padding:10px;background:#fee2e2;border-radius:8px;text-align:center">
                    <div style="font-size:20px;font-weight:800;color:#991b1b">{{ \App\Support\PersianNumber::toFa($api_stats['errors'] ?? 0) }}</div>
                    <div style="font-size:10.5px;color:#991b1b">کل خطاها</div>
                </div>
                <div style="padding:10px;background:#fef3c7;border-radius:8px;text-align:center">
                    <div style="font-size:20px;font-weight:800;color:#92400e">{{ \App\Support\PersianNumber::toFa($api_stats['avg_ms'] ?? 0) }}ms</div>
                    <div style="font-size:10.5px;color:#92400e">میانگین زمان</div>
                </div>
            </div>

            <div style="display:flex;justify-content:space-between;margin-bottom:8px;align-items:center">
                <h3 style="margin:0">📜 آخرین درخواست‌ها</h3>
                <button wire:click="clearApiLogs" wire:confirm="همه پاک شوند؟"
                        style="padding:6px 14px;background:#fee2e2;color:#dc2626;border:1.5px solid #fca5a5;border-radius:6px;font-weight:700;cursor:pointer;font-size:11px">🗑️ پاک کردن</button>
            </div>

            <div style="max-height:400px;overflow-y:auto;background:#0f172a;border-radius:8px;padding:10px;font-family:monospace;font-size:11px;direction:ltr">
                @forelse($api_logs_list as $l)
                    <div style="padding:4px 0;border-bottom:1px solid #1e293b">
                        <div style="display:flex;gap:8px;align-items:center">
                            <span style="background:{{ ($l['status_code'] ?? 0) >= 200 && ($l['status_code'] ?? 0) < 300 ? '#16a34a' : '#dc2626' }};color:#fff;padding:1px 6px;border-radius:4px;font-size:10px;font-weight:700">{{ $l['status_code'] ?? '—' }}</span>
                            <span style="color:#60a5fa;font-weight:700">{{ $l['method'] }}</span>
                            <span style="color:#94a3b8;margin-right:auto;font-size:10px">{{ $l['time'] }}</span>
                        </div>
                        <div style="color:#cbd5e1;margin-top:2px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;font-size:10px">{{ $l['url'] }}</div>
                        @if($l['error'])
                            <div style="color:#f87171;font-size:10px">{{ $l['error'] }}</div>
                        @endif
                    </div>
                @empty
                    <div style="color:#475569;text-align:center;padding:15px">درخواستی نیست</div>
                @endforelse
            </div>
        </div>
    @endif

    {{-- ═══ CERTIFICATES > TEMPLATES ═══ --}}
    @if($tab === 'cert-templates')
        <livewire:settings.templates />
    @endif

    {{-- ═══ CERTIFICATES > SIZES ═══ --}}
    @if($tab === 'cert-sizes')
        <div style="display:grid;grid-template-columns:1fr;gap:14px">

            <div class="sg-settings-card" style="position:sticky;top:0;z-index:5">
                <h3>👁️ پیش‌نمایش زنده</h3>
                <div style="background:repeating-conic-gradient(#f0f0f0 0% 25%, #fff 0% 50%) 50% / 20px 20px;border-radius:12px;padding:16px;display:flex;justify-content:center;overflow:auto;min-height:340px;align-items:center">
                    <div style="transform-origin:top center">{!! $this->previewCard !!}</div>
                </div>
                <div style="display:flex;justify-content:space-between;padding-top:14px;border-top:1px solid #e2e8f0;margin-top:14px;flex-wrap:wrap;gap:6px">
                    <span style="font-size:11px;color:#64748b;align-self:center">📐 {{ $cert_width }}×{{ $cert_height }} cm</span>
                    <button wire:click="saveCertificate" style="padding:8px 20px;background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:12.5px">💾 ذخیره</button>
                </div>
            </div>

            <div class="sg-settings-card">
                <h3>📏 ابعاد کارت</h3>
                <div class="form-grid">
                    <div class="field col-6">
                        <label>📐 عرض (cm)</label>
                        <input type="number" step="0.1" min="3" max="15" wire:model.live="cert_width" dir="ltr">
                    </div>
                    <div class="field col-6">
                        <label>📐 ارتفاع (cm)</label>
                        <input type="number" step="0.1" min="3" max="15" wire:model.live="cert_height" dir="ltr">
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
                    <input type="range" min="40" max="300" step="5" wire:model.live="cert_img_w" class="range range-sm range-primary w-full">
                    <span style="font-family:monospace;font-size:11px;text-align:center;background:#fef3c7;padding:3px;border-radius:6px">{{ $cert_img_w }}px</span>
                </div>
                <div style="display:grid;grid-template-columns:100px 1fr 60px;gap:10px;align-items:center;margin-bottom:14px">
                    <label style="font-size:12px;font-weight:700;color:#1a5276">ارتفاع</label>
                    <input type="range" min="40" max="300" step="5" wire:model.live="cert_img_h" class="range range-sm range-primary w-full">
                    <span style="font-family:monospace;font-size:11px;text-align:center;background:#fef3c7;padding:3px;border-radius:6px">{{ $cert_img_h }}px</span>
                </div>

                <h3 style="margin-top:20px">📱 QR و لوگو</h3>
                <div style="display:grid;grid-template-columns:100px 1fr 60px;gap:10px;align-items:center;margin-bottom:14px">
                    <label style="font-size:12px;font-weight:700;color:#1a5276">QR</label>
                    <input type="range" min="20" max="120" step="2" wire:model.live="cert_qr_size" class="range range-sm range-primary w-full">
                    <span style="font-family:monospace;font-size:11px;text-align:center;background:#fef3c7;padding:3px;border-radius:6px">{{ $cert_qr_size }}px</span>
                </div>

                <h3 style="margin-top:20px">🔤 فونت‌ها</h3>
                <div style="display:grid;grid-template-columns:100px 1fr 60px;gap:10px;align-items:center;margin-bottom:14px">
                    <label style="font-size:12px;font-weight:700;color:#1a5276">عنوان</label>
                    <input type="range" min="8" max="40" wire:model.live="cert_title_font" class="range range-sm range-primary w-full">
                    <span style="font-family:monospace;font-size:11px;text-align:center;background:#fef3c7;padding:3px;border-radius:6px">{{ $cert_title_font }}px</span>
                </div>
                <div style="display:grid;grid-template-columns:100px 1fr 60px;gap:10px;align-items:center;margin-bottom:14px">
                    <label style="font-size:12px;font-weight:700;color:#1a5276">کد</label>
                    <input type="range" min="6" max="30" wire:model.live="cert_code_font" class="range range-sm range-primary w-full">
                    <span style="font-family:monospace;font-size:11px;text-align:center;background:#fef3c7;padding:3px;border-radius:6px">{{ $cert_code_font }}px</span>
                </div>

                <h3 style="margin-top:20px">📊 عرض ستون‌های جدول</h3>
                <div style="display:grid;grid-template-columns:100px 1fr 60px;gap:10px;align-items:center;margin-bottom:14px">
                    <label style="font-size:12px;font-weight:700;color:#1a5276">ستون ۱</label>
                    <input type="range" min="10" max="50" wire:model.live="cert_col1" class="range range-sm range-primary w-full">
                    <span style="font-family:monospace;font-size:11px;text-align:center;background:#fef3c7;padding:3px;border-radius:6px">{{ $cert_col1 }}%</span>
                </div>
                <div style="display:grid;grid-template-columns:100px 1fr 60px;gap:10px;align-items:center;margin-bottom:14px">
                    <label style="font-size:12px;font-weight:700;color:#1a5276">ستون ۲</label>
                    <input type="range" min="10" max="50" wire:model.live="cert_col2" class="range range-sm range-primary w-full">
                    <span style="font-family:monospace;font-size:11px;text-align:center;background:#fef3c7;padding:3px;border-radius:6px">{{ $cert_col2 }}%</span>
                </div>
                <div style="display:grid;grid-template-columns:100px 1fr 60px;gap:10px;align-items:center;margin-bottom:14px">
                    <label style="font-size:12px;font-weight:700;color:#1a5276">ستون ۳</label>
                    <input type="range" min="10" max="50" wire:model.live="cert_col3" class="range range-sm range-primary w-full">
                    <span style="font-family:monospace;font-size:11px;text-align:center;background:#fef3c7;padding:3px;border-radius:6px">{{ $cert_col3 }}%</span>
                </div>
                <div style="display:grid;grid-template-columns:100px 1fr 60px;gap:10px;align-items:center;margin-bottom:14px">
                    <label style="font-size:12px;font-weight:700;color:#1a5276">ستون ۴</label>
                    <input type="range" min="10" max="50" wire:model.live="cert_col4" class="range range-sm range-primary w-full">
                    <span style="font-family:monospace;font-size:11px;text-align:center;background:#fef3c7;padding:3px;border-radius:6px">{{ $cert_col4 }}%</span>
                </div>

                <label style="display:flex;align-items:center;gap:8px;padding:10px;background:#f8fafc;border-radius:8px;cursor:pointer">
                    <input type="checkbox" wire:model.live="cert_hide_desc" style="width:18px;height:18px;accent-color:#c9a84c">
                    <span style="font-size:13px;font-weight:700">مخفی کردن توضیحات</span>
                </label>
            </div>
        </div>
    @endif

    {{-- ═══ CERTIFICATES > CATALOG (Stones/Metals) ═══ --}}
    @if($tab === 'catalog')
        <div class="sg-settings-card">
            <h3>💎 سنگ‌ها ({{ \App\Support\PersianNumber::toFa(count($cert_stones)) }})</h3>

            <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:8px;margin-bottom:16px">
                @foreach($cert_stones as $i => $s)
                    <div style="position:relative;background:#fff;border:2px solid #e2e8f0;border-radius:10px;padding:8px;text-align:center">
                        <div style="font-size:22px;margin-bottom:4px">{{ $s['icon'] ?? '💎' }}</div>
                        <div style="font-size:10.5px;font-weight:700;color:#1e293b">{{ $s['name'] }}</div>
                        <div style="font-size:9px;color:#94a3b8">{{ $s['origin'] ?? '' }}</div>
                        <div style="display:flex;gap:3px;margin-top:6px;justify-content:center">
                            <button type="button" wire:click="editStone({{ $i }})"
                                    style="background:#e0e7ff;color:#3730a3;border:none;width:22px;height:22px;border-radius:5px;font-size:10px;cursor:pointer">✏️</button>
                            <button type="button" wire:click="removeStone({{ $i }})" wire:confirm="حذف شود؟"
                                    style="background:#fee2e2;color:#dc2626;border:none;width:22px;height:22px;border-radius:5px;font-size:10px;cursor:pointer">🗑️</button>
                        </div>
                    </div>
                @endforeach
            </div>

            <h3 style="margin-top:14px">{{ $editing_stone_idx !== null ? '✏️ ویرایش سنگ' : '➕ سنگ جدید' }}</h3>
            <div class="form-grid">
                <div class="field col-6">
                    <label>نام فارسی</label>
                    <input type="text" wire:model="new_stone_name" placeholder="فیروزه عجمی">
                </div>
                <div class="field col-6">
                    <label>نام انگلیسی</label>
                    <input type="text" wire:model="new_stone_en" dir="ltr" placeholder="Turquoise Ajami">
                </div>
                <div class="field col-6">
                    <label>اصالت</label>
                    <input type="text" wire:model="new_stone_origin" placeholder="نیشابور">
                </div>
                <div class="field col-3">
                    <label>آیکون</label>
                    <input type="text" wire:model="new_stone_icon" style="text-align:center;font-size:18px">
                </div>
                <div class="field col-3">
                    <label>پرچم</label>
                    <select wire:model="new_stone_flag" style="width:100%;padding:9px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:12px">
                        <option value="ir">🇮🇷 ایران</option>
                        <option value="ye">🇾🇪 یمن</option>
                        <option value="iq">🇮🇶 عراق</option>
                        <option value="af">🇦🇫 افغانستان</option>
                        <option value="za">🇿🇦 آفریقا</option>
                        <option value="mm">🇲🇲 میانمار</option>
                        <option value="co">🇨🇴 کلمبیا</option>
                        <option value="lk">🇱🇰 سری‌لانکا</option>
                        <option value="br">🇧🇷 برزیل</option>
                    </select>
                </div>
            </div>
            <div style="display:flex;gap:6px;margin-top:10px">
                <button wire:click="addStone" style="padding:8px 18px;background:#1a5276;color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:12.5px">{{ $editing_stone_idx !== null ? '✏️ ویرایش' : '➕ افزودن' }}</button>
                @if($editing_stone_idx !== null)
                    <button wire:click="cancelStoneEdit" style="padding:8px 18px;background:#fff;color:#475569;border:1.5px solid #cbd5e1;border-radius:8px;font-weight:700;cursor:pointer;font-size:12.5px">انصراف</button>
                @endif
            </div>

            <h3 style="margin-top:24px">⚙️ فلزات ({{ \App\Support\PersianNumber::toFa(count($cert_metals)) }})</h3>
            <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(140px,1fr));gap:8px;margin-bottom:16px">
                @foreach($cert_metals as $i => $m)
                    <div style="background:#f8fafc;border:1.5px solid #e2e8f0;border-radius:8px;padding:8px;display:flex;justify-content:space-between;align-items:center">
                        <div>
                            <div style="font-weight:700;font-size:11.5px">{{ $m['name'] }}</div>
                            <div style="font-size:10px;color:#94a3b8" dir="ltr">{{ $m['carat'] ?? '' }}</div>
                        </div>
                        <div style="display:flex;gap:3px">
                            <button wire:click="editMetal({{ $i }})" style="background:#e0e7ff;color:#3730a3;border:none;width:20px;height:20px;border-radius:4px;font-size:9px;cursor:pointer">✏️</button>
                            <button wire:click="removeMetal({{ $i }})" wire:confirm="حذف؟" style="background:#fee2e2;color:#dc2626;border:none;width:20px;height:20px;border-radius:4px;font-size:9px;cursor:pointer">🗑️</button>
                        </div>
                    </div>
                @endforeach
            </div>

            <h3 style="margin-top:14px">{{ $editing_metal_idx !== null ? '✏️ ویرایش فلز' : '➕ فلز جدید' }}</h3>
            <div class="form-grid">
                <div class="field col-4"><label>نام</label><input type="text" wire:model="new_metal_name" placeholder="نقره 925"></div>
                <div class="field col-4"><label>English</label><input type="text" wire:model="new_metal_en" dir="ltr" placeholder="Silver 925"></div>
                <div class="field col-4"><label>عیار</label><input type="text" wire:model="new_metal_carat" dir="ltr" placeholder="925"></div>
            </div>
            <button wire:click="addMetal" style="margin-top:10px;padding:8px 18px;background:#1a5276;color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:12.5px">{{ $editing_metal_idx !== null ? '✏️ ویرایش' : '➕ افزودن' }}</button>
        </div>
    @endif

    {{-- ═══ CERTIFICATES > LABELS ═══ --}}
    @if($tab === 'labels')
        <div class="sg-settings-card">
            <h3>🏷️ اندازه برچسب پستی</h3>
            <div class="form-grid">
                <div class="field col-6"><label>عرض (mm)</label><input type="number" wire:model="label_width" dir="ltr"></div>
                <div class="field col-6"><label>ارتفاع (mm)</label><input type="number" wire:model="label_height" dir="ltr"></div>
            </div>
            <div style="display:flex;justify-content:flex-end;padding-top:14px;border-top:1px solid #e2e8f0;margin-top:14px">
                <button wire:click="saveLabel" style="padding:9px 22px;background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">💾 ذخیره</button>
            </div>
        </div>
    @endif

    {{-- ═══ CERTIFICATES > ASSETS ═══ --}}
    @if($tab === 'assets')
        <div class="sg-settings-card">
            <h3>🖼️ لوگوها ({{ \App\Support\PersianNumber::toFa(count($logo_images)) }})</h3>

            @if(count($logo_images))
                <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(80px,1fr));gap:8px;margin-bottom:12px">
                    @foreach($logo_images as $i => $logo)
                        <div style="position:relative;background:#fff;border:1.5px solid #e2e8f0;border-radius:8px;padding:6px">
                            <img src="{{ asset('storage/' . $logo) }}" style="width:100%;height:50px;object-fit:contain">
                            <button wire:click="removeLogo({{ $i }})" wire:confirm="حذف؟"
                                    style="position:absolute;top:-6px;right:-6px;width:20px;height:20px;background:#dc2626;color:#fff;border-radius:50%;border:2px solid #fff;font-size:10px;cursor:pointer">✕</button>
                        </div>
                    @endforeach
                </div>
            @endif

            <input type="file" wire:model="logoUpload" accept="image/*" style="width:100%;padding:8px;border:1.5px dashed #cbd5e1;border-radius:8px;font-size:12px">
            <div wire:loading wire:target="logoUpload" style="font-size:11px;color:#0891b2;margin-top:4px">⏳...</div>

            <div style="display:grid;grid-template-columns:100px 1fr 60px;gap:10px;align-items:center;margin-top:12px">
                <label style="font-size:12px;font-weight:700;color:#1a5276">اندازه</label>
                <input type="range" min="20" max="120" step="4" wire:model.live="logo_size" class="range range-sm range-primary w-full">
                <span style="font-family:monospace;font-size:11px;text-align:center;background:#fef3c7;padding:3px;border-radius:6px">{{ $logo_size }}px</span>
            </div>

            <h3 style="margin-top:24px">📄 تصویر توضیحات</h3>
            @if($desc_image)
                <div style="margin-bottom:12px;padding:8px;background:#f8fafc;border-radius:8px;text-align:center">
                    <img src="{{ asset('storage/' . $desc_image) }}" style="max-width:100%;max-height:100px">
                    <button wire:click="$set('desc_image','')" style="margin-top:6px;padding:4px 12px;background:#dc2626;color:#fff;border:none;border-radius:6px;font-size:11px;cursor:pointer">🗑️ حذف</button>
                </div>
            @endif
            <input type="file" wire:model="descUpload" accept="image/*" style="width:100%;padding:8px;border:1.5px dashed #cbd5e1;border-radius:8px;font-size:12px">

            <h3 style="margin-top:24px">🎨 پس‌زمینه</h3>
            @if($bg_image)
                <div style="margin-bottom:12px"><img src="{{ $bg_image }}" style="max-width:140px;border-radius:8px;border:1.5px solid #c9a84c"></div>
            @endif
            <input type="file" wire:model="bgUpload" accept="image/*" style="width:100%;padding:8px;border:1.5px dashed #cbd5e1;border-radius:8px;font-size:12px">

            <div style="display:flex;justify-content:flex-end;padding-top:14px;border-top:1px solid #e2e8f0;margin-top:14px">
                <button wire:click="saveLogos" style="padding:9px 22px;background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">💾 ذخیره</button>
            </div>
        </div>
    @endif

    {{-- ═══ HEALTH > HEALTH ═══ --}}
    @if($tab === 'health')
        <livewire:settings.health />
    @endif

    {{-- ═══ HEALTH > LOGS ═══ --}}
    @if($tab === 'logs')
        <div class="sg-settings-card">
            <h3>📜 لاگ فعالیت‌ها</h3>
            <a href="{{ route('activity-log') }}" wire:navigate
               style="display:inline-block;padding:9px 18px;background:#1a5276;color:#fff;border-radius:8px;font-weight:700;text-decoration:none;font-size:12.5px">
                🔍 مشاهده لاگ کامل
            </a>
        </div>
    @endif

    {{-- ═══ HEALTH > BACKUP ═══ --}}
    @if($tab === 'backup')
        <div class="sg-settings-card">
            <h3>💾 پشتیبان‌گیری</h3>
            <div style="display:flex;gap:6px;flex-wrap:wrap">
                <button onclick="fetch('/api/backup/create',{method:'POST',headers:{'X-CSRF-TOKEN':document.querySelector('meta[name=csrf-token]').content}}).then(()=>alert('در حال ساخت...'))"
                        style="padding:9px 18px;background:#1a5276;color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:12.5px">
                    ➕ پشتیبان جدید
                </button>
            </div>
            <h3 style="margin-top:20px">📊 اطلاعات سیستم</h3>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px">
                @foreach([
                    ['🖥️', 'PHP', $stats['php']],
                    ['⚡', 'Laravel', $stats['laravel']],
                    ['📦', 'سفارشات', \App\Support\PersianNumber::toFa($stats['orders'])],
                    ['👥', 'مشتریان', \App\Support\PersianNumber::toFa($stats['customers'])],
                    ['💎', 'شناسنامه', \App\Support\PersianNumber::toFa($stats['certificates'])],
                    ['🛍️', 'محصولات', \App\Support\PersianNumber::toFa($stats['products'])],
                ] as $item)
                    <div style="padding:10px;background:#f8fafc;border-radius:8px;display:flex;justify-content:space-between;font-size:12px">
                        <span>{{ $item[0] }} {{ $item[1] }}</span>
                        <strong style="font-family:monospace">{{ $item[2] }}</strong>
                    </div>
                @endforeach
            </div>
        </div>
    @endif
</div>
