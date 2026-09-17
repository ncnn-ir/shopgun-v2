<div style="padding:14px;direction:rtl" x-data>

    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px;margin-bottom:16px">
        <div>
            <h1 style="margin:0;font-size:20px;font-weight:700">📦 ثبت گروهی محصولات ووکامرس</h1>
            <p style="margin:4px 0 0;font-size:12px;color:#64748b">ارسال دسته‌ای محصولات به سایت — با تصاویر خودکار و گزارش زنده</p>
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap">
            <button type="button" wire:click="testConnection" wire:loading.attr="disabled"
                    style="padding:8px 18px;background:linear-gradient(135deg,#0891b2,#0e7490);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px;height:38px">
                <span wire:loading.remove wire:target="testConnection">🔌 تست اتصال + دریافت لیست‌ها</span>
                <span wire:loading wire:target="testConnection">⏳...</span>
            </button>

            @if($tab === 'form')
                <button type="button" wire:click="sendBatch" wire:loading.attr="disabled"
                        wire:confirm="آیا مطمئنی می‌خواهی {{ count(array_filter($products, fn($p) => $p['checked'] ?? false)) }} محصول ارسال شوند؟"
                        style="padding:8px 22px;background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px;height:38px">
                    <span wire:loading.remove wire:target="sendBatch">🚀 ارسال به سایت</span>
                    <span wire:loading wire:target="sendBatch">⏳ در حال ارسال...</span>
                </button>
            @endif
        </div>
    </div>

    {{-- Test result --}}
    @if(!empty($test_result))
        <div style="padding:12px;border-radius:10px;margin-bottom:14px;font-size:13px;font-weight:700;
            background:{{ !empty($test_result['ok']) ? '#d1fae5' : '#fee2e2' }};
            color:{{ !empty($test_result['ok']) ? '#065f46' : '#991b1b' }}">
            {{ $test_result['msg'] }}
        </div>
    @endif

    {{-- Tabs --}}
    <div style="display:flex;gap:6px;margin-bottom:14px;border-bottom:2px solid #e2e8f0">
        <button wire:click="$set('tab','form')"
                style="padding:8px 18px;border:none;background:{{ $tab === 'form' ? 'linear-gradient(135deg,#1a5276,#0d3b5e)' : 'transparent' }};color:{{ $tab === 'form' ? '#fff' : '#64748b' }};border-radius:10px 10px 0 0;font-weight:700;cursor:pointer;font-size:13px">
            📝 فرم
        </button>
        <button wire:click="$set('tab','queue')"
                style="padding:8px 18px;border:none;background:{{ $tab === 'queue' ? 'linear-gradient(135deg,#7c3aed,#5b21b6)' : 'transparent' }};color:{{ $tab === 'queue' ? '#fff' : '#64748b' }};border-radius:10px 10px 0 0;font-weight:700;cursor:pointer;font-size:13px">
            📊 گزارش و صف ({{ \App\Support\PersianNumber::toFa($progress_sent) }}/{{ \App\Support\PersianNumber::toFa($progress_total) }})
        </button>
    </div>

    {{-- ═══════════════ FORM TAB ═══════════════ --}}
    @if($tab === 'form')

        {{-- Group fields --}}
        <div class="sg-settings-card" style="margin-bottom:14px">
            <h3>🎛️ فیلدهای گروهی (برای همه محصولات)</h3>

            <div class="form-grid">
                <div class="field col-6">
                    <label>📁 دسته‌بندی‌ها (چندگانه)</label>
                    <div style="max-height:180px;overflow-y:auto;border:1.5px solid #cbd5e1;border-radius:8px;padding:8px;background:#f8fafc">
                        @forelse($woo_categories as $c)
                            <label style="display:flex;align-items:center;gap:6px;padding:4px 6px;border-radius:6px;cursor:pointer;font-size:12px">
                                <input type="checkbox" wire:model.live="selected_categories" value="{{ $c['id'] }}"
                                       style="accent-color:#c9a84c">
                                <span>{{ $c['name'] }}</span>
                            </label>
                        @empty
                            <div style="padding:14px;text-align:center;color:#94a3b8;font-size:11px">اول «تست اتصال» را بزن</div>
                        @endforelse
                    </div>
                </div>

                <div class="field col-6">
                    <label>👤 نویسنده</label>
                    <select wire:model="author_id" style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:13px;background:#f8fafc">
                        <option value="">— پیش‌فرض (کاربر متصل) —</option>
                        @foreach($wp_users as $u)
                            <option value="{{ $u['id'] }}">{{ $u['name'] }}</option>
                        @endforeach
                    </select>
                </div>

                <div class="field col-4">
                    <label>🚦 وضعیت انتشار</label>
                    <select wire:model="status" style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:13px;background:#f8fafc">
                        <option value="draft">📝 پیش‌نویس</option>
                        <option value="publish">✅ منتشر شده</option>
                        <option value="private">🔒 خصوصی</option>
                        <option value="pending">⏳ در انتظار بررسی</option>
                    </select>
                </div>

                <div class="field col-4">
                    <label>🖼️ پسوند تصویر</label>
                    <select wire:model="image_ext" style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:13px;background:#f8fafc">
                        <option value="jpg">.jpg</option>
                        <option value="jpeg">.jpeg</option>
                        <option value="png">.png</option>
                        <option value="webp">.webp</option>
                    </select>
                </div>

                <div class="field col-4">
                    <label>🔢 تعداد تصاویر هر محصول</label>
                    <input type="number" min="1" max="10" wire:model="max_images"
                           style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-family:monospace;text-align:center">
                </div>

                <div class="field col-12">
                    <label>📅 تاریخ انتشار (اختیاری — ISO 8601 یا YYYY-MM-DD HH:MM:SS)</label>
                    <input type="text" wire:model="date_created" dir="ltr" placeholder="2026-09-17 14:30:00"
                           style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-family:monospace;font-size:12px">
                </div>

                <div class="field col-12">
                    <label>📝 توضیحات کوتاه پیش‌فرض (اگر برای محصولی پر نشده باشد)</label>
                    <textarea wire:model="default_short_description" rows="2"
                              style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:12px;box-sizing:border-box"></textarea>
                </div>
            </div>

            <h3 style="margin-top:16px">⚙️ موجودی و خرید</h3>
            <div class="form-grid">
                <div class="field col-3">
                    <label style="display:flex;align-items:center;gap:6px;cursor:pointer">
                        <input type="checkbox" wire:model="manage_stock" style="width:16px;height:16px;accent-color:#c9a84c">
                        <span>مدیریت موجودی</span>
                    </label>
                </div>
                <div class="field col-3">
                    <label>وضعیت پیش‌فرض</label>
                    <select wire:model="stock_status" style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:6px;font-size:12px;background:#f8fafc">
                        <option value="instock">موجود</option>
                        <option value="outofstock">ناموجود</option>
                        <option value="onbackorder">پیش‌سفارش</option>
                    </select>
                </div>
                <div class="field col-3">
                    <label>سفارش مجدد</label>
                    <select wire:model="backorders" style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:6px;font-size:12px;background:#f8fafc">
                        <option value="no">غیرفعال</option>
                        <option value="notify">با اطلاع</option>
                        <option value="yes">فعال</option>
                    </select>
                </div>
                <div class="field col-3">
                    <label style="display:flex;align-items:center;gap:6px;cursor:pointer">
                        <input type="checkbox" wire:model="sold_individually" style="width:16px;height:16px;accent-color:#c9a84c">
                        <span>فقط تکی</span>
                    </label>
                </div>
            </div>
        </div>

        {{-- Attributes --}}
        @if(!empty($woo_attributes))
            <div class="sg-settings-card" style="margin-bottom:14px">
                <h3>💎 ویژگی‌های گروهی</h3>
                <p style="font-size:11px;color:#94a3b8;margin:0 0 10px">یک یا چند ویژگی انتخاب کن. هر ویژگی به همه محصولات اضافه می‌شود.</p>

                <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:10px">
                    @foreach($woo_attributes as $a)
                        <div style="border:1.5px solid #e2e8f0;border-radius:10px;padding:10px;background:#f8fafc">
                            <div style="font-weight:700;font-size:12px;color:#1a5276;margin-bottom:6px">{{ $a['name'] }}</div>

                            @php $this->loadAttrTerms($a['id']); @endphp

                            @if(!empty($attr_terms[$a['id']] ?? []))
                                <div style="max-height:120px;overflow-y:auto;display:flex;flex-wrap:wrap;gap:3px">
                                    @foreach($attr_terms[$a['id']] as $t)
                                        @php $sel = in_array($t['id'], $selected_attributes[$a['id']] ?? [], true); @endphp
                                        <button type="button"
                                                wire:click="toggleAttrTerm({{ $a['id'] }}, {{ $t['id'] }})"
                                                style="padding:3px 8px;border-radius:12px;font-size:10.5px;font-weight:700;cursor:pointer;border:1.5px solid {{ $sel ? '#16a34a' : '#cbd5e1' }};background:{{ $sel ? '#d1fae5' : '#fff' }};color:{{ $sel ? '#065f46' : '#475569' }}">
                                            {{ $t['name'] }}
                                        </button>
                                    @endforeach
                                </div>
                            @else
                                <div style="font-size:11px;color:#94a3b8">اصطلاحی ندارد</div>
                            @endif
                        </div>
                    @endforeach
                </div>
            </div>
        @endif

        {{-- Bulk add --}}
        <div class="sg-settings-card" style="margin-bottom:14px;background:linear-gradient(135deg,#eff6ff,#dbeafe);border-color:#3b82f6">
            <h3 style="color:#1e40af">⚡ افزودن سریع بر اساس لیست SKU</h3>
            <div class="form-grid">
                <div class="field col-12">
                    <label>لیست SKU (با فاصله، کاما، یا خط جدید)</label>
                    <textarea wire:model="bulk_skus" rows="3" dir="ltr" placeholder="200 201 202 203"
                              style="width:100%;padding:8px 12px;border:1.5px solid #93c5fd;border-radius:8px;font-family:monospace;font-size:12px;background:#fff;box-sizing:border-box"></textarea>
                </div>
                <div class="field col-6">
                    <label>عنوان فارسی (بدون SKU)</label>
                    <input type="text" wire:model="bulk_title_fa" placeholder="مثلاً: انگشتر فیروزه مردانه">
                </div>
                <div class="field col-6">
                    <label>نامک لاتین</label>
                    <input type="text" wire:model="bulk_slug_en" dir="ltr" placeholder="men-turquoise-ring">
                </div>
                <div class="field col-3">
                    <label>قیمت اصلی</label>
                    <input type="text" wire:model="bulk_regular_price" dir="ltr" placeholder="1500000">
                </div>
                <div class="field col-3">
                    <label>قیمت حراج</label>
                    <input type="text" wire:model="bulk_sale_price" dir="ltr" placeholder="1200000">
                </div>
                <div class="field col-2">
                    <label>وزن</label>
                    <input type="text" wire:model="bulk_weight" dir="ltr" placeholder="5.5">
                </div>
                <div class="field col-2">
                    <label>طول</label>
                    <input type="text" wire:model="bulk_length" dir="ltr" placeholder="15">
                </div>
                <div class="field col-1">
                    <label>عرض</label>
                    <input type="text" wire:model="bulk_width" dir="ltr" placeholder="12">
                </div>
                <div class="field col-1">
                    <label>ارتفاع</label>
                    <input type="text" wire:model="bulk_height" dir="ltr" placeholder="3">
                </div>
                <div class="field col-6">
                    <label>موجودی</label>
                    <input type="text" wire:model="bulk_stock" dir="ltr" placeholder="10">
                </div>
            </div>
            <div style="display:flex;gap:6px;margin-top:10px">
                <button type="button" wire:click="addBulkSkus"
                        style="padding:9px 20px;background:linear-gradient(135deg,#3b82f6,#1e40af);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">
                    ⚡ افزودن همه
                </button>
                <button type="button" wire:click="clearAll" wire:confirm="همه ردیف‌ها پاک شوند؟"
                        style="padding:9px 16px;background:#fff;color:#dc2626;border:1.5px solid #fca5a5;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">
                    🗑️ پاک کردن همه
                </button>
            </div>
        </div>

        {{-- Products table --}}
        <div class="sg-settings-card">
            <h3>📋 محصولات ({{ \App\Support\PersianNumber::toFa(count($products)) }})</h3>

            <div style="overflow-x:auto;margin-top:8px">
                <table style="width:100%;border-collapse:collapse;font-size:11.5px;min-width:900px">
                    <thead style="background:#f8fafc">
                        <tr>
                            <th style="padding:8px;text-align:right;color:#1a5276">✓</th>
                            <th style="padding:8px;text-align:right;color:#1a5276">SKU</th>
                            <th style="padding:8px;text-align:right;color:#1a5276">عنوان</th>
                            <th style="padding:8px;text-align:right;color:#1a5276">نامک</th>
                            <th style="padding:8px;text-align:right;color:#1a5276">قیمت</th>
                            <th style="padding:8px;text-align:right;color:#1a5276">حراج</th>
                            <th style="padding:8px;text-align:right;color:#1a5276">موجودی</th>
                            <th style="padding:8px;text-align:right;color:#1a5276">وزن</th>
                            <th style="padding:8px;text-align:right;color:#1a5276">ابعاد</th>
                            <th style="padding:8px;text-align:right;color:#1a5276">تصاویر</th>
                            <th style="padding:8px;text-align:right;color:#1a5276"></th>
                        </tr>
                    </thead>
                    <tbody>
                        @foreach($products as $i => $p)
                            <tr wire:key="row-{{ $i }}" style="border-bottom:1px solid #f1f5f9">
                                <td style="padding:6px;text-align:center">
                                    <input type="checkbox" wire:model="products.{{ $i }}.checked" style="accent-color:#16a34a">
                                </td>
                                <td style="padding:4px">
                                    <input type="text" wire:model.live.debounce.400ms="products.{{ $i }}.sku" dir="ltr"
                                           style="width:80px;padding:5px;border:1.5px solid #cbd5e1;border-radius:5px;font-family:monospace;font-size:11px;text-align:center">
                                </td>
                                <td style="padding:4px">
                                    <input type="text" wire:model="products.{{ $i }}.title_fa"
                                           style="width:180px;padding:5px;border:1.5px solid #cbd5e1;border-radius:5px;font-size:11px">
                                </td>
                                <td style="padding:4px">
                                    <input type="text" wire:model="products.{{ $i }}.slug_en" dir="ltr"
                                           style="width:130px;padding:5px;border:1.5px solid #cbd5e1;border-radius:5px;font-family:monospace;font-size:11px">
                                </td>
                                <td style="padding:4px">
                                    <input type="text" wire:model="products.{{ $i }}.regular_price" dir="ltr"
                                           style="width:90px;padding:5px;border:1.5px solid #cbd5e1;border-radius:5px;font-family:monospace;font-size:11px;text-align:center">
                                </td>
                                <td style="padding:4px">
                                    <input type="text" wire:model="products.{{ $i }}.sale_price" dir="ltr"
                                           style="width:90px;padding:5px;border:1.5px solid #cbd5e1;border-radius:5px;font-family:monospace;font-size:11px;text-align:center">
                                </td>
                                <td style="padding:4px">
                                    <input type="text" wire:model="products.{{ $i }}.stock_quantity" dir="ltr"
                                           style="width:60px;padding:5px;border:1.5px solid #cbd5e1;border-radius:5px;font-family:monospace;font-size:11px;text-align:center">
                                </td>
                                <td style="padding:4px">
                                    <input type="text" wire:model="products.{{ $i }}.weight" dir="ltr"
                                           style="width:55px;padding:5px;border:1.5px solid #cbd5e1;border-radius:5px;font-family:monospace;font-size:11px;text-align:center">
                                </td>
                                <td style="padding:4px">
                                    <div style="display:flex;gap:2px">
                                        <input type="text" wire:model="products.{{ $i }}.length" dir="ltr" placeholder="L"
                                               style="width:42px;padding:5px;border:1.5px solid #cbd5e1;border-radius:5px;font-family:monospace;font-size:10px;text-align:center">
                                        <input type="text" wire:model="products.{{ $i }}.width" dir="ltr" placeholder="W"
                                               style="width:42px;padding:5px;border:1.5px solid #cbd5e1;border-radius:5px;font-family:monospace;font-size:10px;text-align:center">
                                        <input type="text" wire:model="products.{{ $i }}.height" dir="ltr" placeholder="H"
                                               style="width:42px;padding:5px;border:1.5px solid #cbd5e1;border-radius:5px;font-family:monospace;font-size:10px;text-align:center">
                                    </div>
                                </td>
                                <td style="padding:4px;text-align:center">
                                    @if(!empty($p['sku']))
                                        <button type="button" wire:click="showDetail({{ $i }})"
                                                style="background:#e0e7ff;color:#3730a3;border:none;padding:4px 8px;border-radius:6px;font-size:10.5px;font-weight:700;cursor:pointer;white-space:nowrap">
                                            🖼️ پیش‌نمایش
                                        </button>
                                    @else
                                        <span style="color:#94a3b8;font-size:10px">—</span>
                                    @endif
                                </td>
                                <td style="padding:4px">
                                    <button type="button" wire:click="removeRow({{ $i }})"
                                            wire:confirm="حذف شود؟"
                                            style="background:#fee2e2;color:#dc2626;border:none;width:26px;height:26px;border-radius:5px;cursor:pointer;font-size:12px">✕</button>
                                </td>
                            </tr>
                        @endforeach
                    </tbody>
                </table>
            </div>

            <button type="button" wire:click="addRow"
                    style="margin-top:10px;padding:8px 16px;background:#f1f5f9;color:#475569;border:1.5px solid #cbd5e1;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">
                ➕ افزودن ردیف
            </button>
        </div>
    @endif

    {{-- ═══════════════ QUEUE TAB ═══════════════ --}}
    @if($tab === 'queue')
        <div class="sg-settings-card">
            <h3>📊 گزارش پیشرفت</h3>

            @php
                $pct = $progress_total > 0 ? round(($progress_sent / $progress_total) * 100) : 0;
            @endphp

            <div style="margin-bottom:14px">
                <div style="display:flex;justify-content:space-between;font-size:12px;font-weight:700;margin-bottom:6px">
                    <span>📤 ارسال شده: {{ \App\Support\PersianNumber::toFa($progress_sent) }} از {{ \App\Support\PersianNumber::toFa($progress_total) }} ({{ \App\Support\PersianNumber::toFa($pct) }}%)</span>
                </div>
                <div style="height:14px;background:#e2e8f0;border-radius:7px;overflow:hidden">
                    <div style="height:100%;width:{{ $pct }}%;background:linear-gradient(90deg,#16a34a,#10b981);transition:width .3s"></div>
                </div>
            </div>

            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:14px">
                <div style="padding:10px;background:#d1fae5;border-radius:8px;text-align:center">
                    <div style="font-size:22px;font-weight:800;color:#065f46">{{ \App\Support\PersianNumber::toFa($progress_ok) }}</div>
                    <div style="font-size:11px;color:#065f46;font-weight:700">موفق</div>
                </div>
                <div style="padding:10px;background:#fee2e2;border-radius:8px;text-align:center">
                    <div style="font-size:22px;font-weight:800;color:#991b1b">{{ \App\Support\PersianNumber::toFa($progress_fail) }}</div>
                    <div style="font-size:11px;color:#991b1b;font-weight:700">ناموفق</div>
                </div>
            </div>

            <h3>📜 لاگ زنده</h3>
            <div style="max-height:400px;overflow-y:auto;background:#0f172a;border-radius:8px;padding:12px;font-family:monospace;font-size:11.5px;direction:ltr">
                @forelse($log as $l)
                    <div style="padding:3px 0;color:{{ $l['type'] === 'success' ? '#4ade80' : ($l['type'] === 'error' ? '#f87171' : '#94a3b8') }}">
                        [{{ $l['time'] }}] {{ $l['msg'] }}
                    </div>
                @empty
                    <div style="color:#475569;text-align:center;padding:20px">هنوز ارسالی انجام نشده</div>
                @endforelse
            </div>
        </div>
    @endif

    {{-- ═══════════════ DETAIL MODAL ═══════════════ --}}
    @if($show_detail && $detail)
        <div style="position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:95;display:flex;align-items:flex-start;justify-content:center;padding:10px;overflow-y:auto"
             @keydown.escape.window="$wire.closeDetail()">

            <div style="background:#fff;width:100%;max-width:800px;margin:10px auto;border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,.4);overflow:hidden;direction:rtl">

                <div style="background:linear-gradient(135deg,#7c3aed,#5b21b6);color:#fff;padding:14px 18px;display:flex;justify-content:space-between;align-items:center">
                    <h2 style="margin:0;font-size:16px;font-weight:700">🖼️ پیش‌نمایش محصول SKU {{ $detail['product']['sku'] }}</h2>
                    <button wire:click="closeDetail" style="width:32px;height:32px;border-radius:50%;background:rgba(255,255,255,.2);color:#fff;border:none;cursor:pointer;font-size:15px">X</button>
                </div>

                <div style="padding:16px;max-height:calc(100vh - 160px);overflow-y:auto">

                    <h3>📸 تصاویر پیش‌بینی شده</h3>
                    <p style="font-size:11px;color:#94a3b8;margin:0 0 10px">
                        الگو: <code>{{ $detail['site'] }}/wp-content/uploads/[سال]/[ماه]/[index]-{{ $detail['product']['sku'] }}.{{ $image_ext }}</code>
                    </p>

                    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(120px,1fr));gap:8px;margin-bottom:14px">
                        @foreach($detail['images'] as $idx => $url)
                            <div style="position:relative;background:#f8fafc;border:1.5px solid #e2e8f0;border-radius:10px;padding:6px">
                                <div style="font-size:10px;font-weight:700;color:{{ $idx === 0 ? '#16a34a' : '#64748b' }};margin-bottom:4px">
                                    {{ $idx === 0 ? '🌟 شاخص' : '🖼️ گالری #' . $idx }}
                                </div>
                                <div style="width:100%;aspect-ratio:1;border-radius:6px;background:#fff;overflow:hidden;display:flex;align-items:center;justify-content:center">
                                    <img src="{{ $url }}" style="width:100%;height:100%;object-fit:cover"
                                         onerror="this.replaceWith(document.createTextNode('❌'))">
                                </div>
                                <div style="font-family:monospace;font-size:9px;color:#94a3b8;margin-top:4px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" dir="ltr">{{ $idx }}-{{ $detail['product']['sku'] }}.{{ $image_ext }}</div>
                            </div>
                        @endforeach
                    </div>

                    <h3>📝 اطلاعات</h3>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:12px">
                        <div style="padding:8px;background:#f8fafc;border-radius:8px">
                            <div style="font-size:10px;color:#94a3b8">عنوان نهایی</div>
                            <div style="font-weight:700">{{ $detail['product']['title_fa'] }} {{ $detail['product']['sku'] }}</div>
                        </div>
                        <div style="padding:8px;background:#f8fafc;border-radius:8px">
                            <div style="font-size:10px;color:#94a3b8">نامک نهایی</div>
                            <div style="font-family:monospace;font-size:11px" dir="ltr">{{ $detail['product']['slug_en'] }}-{{ $detail['product']['sku'] }}</div>
                        </div>
                        <div style="padding:8px;background:#f8fafc;border-radius:8px">
                            <div style="font-size:10px;color:#94a3b8">قیمت</div>
                            <div style="font-family:monospace">{{ $detail['product']['regular_price'] ?: '—' }}</div>
                        </div>
                        <div style="padding:8px;background:#f8fafc;border-radius:8px">
                            <div style="font-size:10px;color:#94a3b8">حراج</div>
                            <div style="font-family:monospace">{{ $detail['product']['sale_price'] ?: '—' }}</div>
                        </div>
                        <div style="padding:8px;background:#f8fafc;border-radius:8px">
                            <div style="font-size:10px;color:#94a3b8">ابعاد</div>
                            <div style="font-family:monospace">{{ $detail['product']['length'] ?: '—' }} × {{ $detail['product']['width'] ?: '—' }} × {{ $detail['product']['height'] ?: '—' }}</div>
                        </div>
                        <div style="padding:8px;background:#f8fafc;border-radius:8px">
                            <div style="font-size:10px;color:#94a3b8">وزن</div>
                            <div style="font-family:monospace">{{ $detail['product']['weight'] ?: '—' }}</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    @endif
</div>
