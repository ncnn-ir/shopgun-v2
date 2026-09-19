<div style="padding:12px;direction:rtl">

    {{-- Header --}}
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:14px">
        <div>
            <h1 style="margin:0;font-size:19px;font-weight:700">📦 ثبت گروهی محصولات</h1>
            <p style="margin:4px 0 0;font-size:11.5px;color:#64748b">ارسال دسته‌ای به ووکامرس + تاریخچه + ماشین‌حساب قیمت</p>
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap">
            <button type="button" wire:click="testConnection" wire:loading.attr="disabled"
                    style="padding:7px 14px;background:linear-gradient(135deg,#0891b2,#0e7490);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px;height:36px">
                <span wire:loading.remove wire:target="testConnection">🔌 تست اتصال</span>
                <span wire:loading wire:target="testConnection">⏳...</span>
            </button>
            @if($tab === 'form')
                <button type="button" wire:click="buildPreview" wire:loading.attr="disabled"
                        style="padding:7px 20px;background:linear-gradient(135deg,#7c3aed,#5b21b6);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px;height:36px">
                    <span wire:loading.remove wire:target="buildPreview">👁️ پیش‌نمایش</span>
                    <span wire:loading wire:target="buildPreview">⏳...</span>
                </button>
            @endif
        </div>
    </div>

    @if(!empty($test_result))
        <div style="padding:10px 12px;border-radius:8px;margin-bottom:12px;font-size:12px;font-weight:700;
            background:{{ !empty($test_result['ok']) ? '#d1fae5' : '#fee2e2' }};
            color:{{ !empty($test_result['ok']) ? '#065f46' : '#991b1b' }}">
            {{ $test_result['msg'] }}
        </div>
    @endif

    {{-- Tabs --}}
    <div style="display:flex;gap:4px;margin-bottom:12px;border-bottom:2px solid #e2e8f0;overflow-x:auto">
        @foreach(['form'=>['📝','فرم'], 'history'=>['📚','تاریخچه'], 'queue'=>['📊','گزارش']] as $k => $meta)
            <button wire:click="$set('tab','{{ $k }}')"
                    style="padding:8px 16px;border:none;white-space:nowrap;background:{{ $tab === $k ? 'linear-gradient(135deg,#1a5276,#0d3b5e)' : 'transparent' }};color:{{ $tab === $k ? '#fff' : '#64748b' }};border-radius:10px 10px 0 0;font-weight:700;cursor:pointer;font-size:12.5px">
                {{ $meta[0] }} {{ $meta[1] }}
            </button>
        @endforeach
    </div>

    {{-- ══════════════ FORM TAB ══════════════ --}}
    @if($tab === 'form')

        {{-- Settings summary --}}
        <div class="sg-settings-card" style="margin-bottom:12px">
            <h3>⚙️ تنظیمات گروهی</h3>

            <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(200px,1fr));gap:10px">
                <div>
                    <label style="font-size:11px;font-weight:700;color:#1a5276;display:block;margin-bottom:3px">📁 دسته‌بندی‌ها</label>
                    <div style="max-height:130px;overflow-y:auto;border:1.5px solid #cbd5e1;border-radius:6px;padding:6px;background:#f8fafc">
                        @forelse($woo_categories as $c)
                            <label style="display:flex;align-items:center;gap:4px;padding:2px 4px;font-size:11px;cursor:pointer">
                                <input type="checkbox" wire:model.live="selected_categories" value="{{ $c['id'] }}" style="accent-color:#c9a84c">
                                <span>{{ $c['name'] }}</span>
                            </label>
                        @empty
                            <div style="padding:10px;text-align:center;color:#94a3b8;font-size:10px">اول «تست اتصال»</div>
                        @endforelse
                    </div>
                </div>

                <div>
                    <label style="font-size:11px;font-weight:700;color:#1a5276;display:block;margin-bottom:3px">🚦 وضعیت</label>
                    <select wire:model="status" style="width:100%;padding:8px;border:1.5px solid #cbd5e1;border-radius:6px;font-size:12px">
                        <option value="draft">📝 پیش‌نویس</option>
                        <option value="publish">✅ منتشر</option>
                        <option value="private">🔒 خصوصی</option>
                    </select>

                    <label style="font-size:11px;font-weight:700;color:#1a5276;display:block;margin-top:8px;margin-bottom:3px">👤 نویسنده</label>
                    <select wire:model="author_id" style="width:100%;padding:8px;border:1.5px solid #cbd5e1;border-radius:6px;font-size:12px">
                        <option value="">پیش‌فرض</option>
                        @foreach($wp_users as $u)
                            <option value="{{ $u['id'] }}">{{ $u['name'] }}</option>
                        @endforeach
                    </select>
                </div>

                <div>
                    <label style="font-size:11px;font-weight:700;color:#1a5276;display:block;margin-bottom:3px">📅 تاریخ انتشار</label>
                    <input type="text" wire:model="date_created" dir="ltr" placeholder="YYYY-MM-DD HH:MM:SS"
                           style="width:100%;padding:8px;border:1.5px solid #cbd5e1;border-radius:6px;font-family:monospace;font-size:11px">

                    <label style="font-size:11px;font-weight:700;color:#1a5276;display:block;margin-top:8px;margin-bottom:3px">🖼️ پسوند</label>
                    <select wire:model="image_ext" style="width:100%;padding:8px;border:1.5px solid #cbd5e1;border-radius:6px;font-size:12px">
                        <option value="jpg">.jpg</option>
                        <option value="jpeg">.jpeg</option>
                        <option value="png">.png</option>
                        <option value="webp">.webp</option>
                    </select>
                </div>

                <div>
                    <label style="font-size:11px;font-weight:700;color:#1a5276;display:block;margin-bottom:3px">📊 موجودی</label>
                    <label style="display:flex;align-items:center;gap:4px;font-size:11px;margin-bottom:4px">
                        <input type="checkbox" wire:model="manage_stock" style="accent-color:#c9a84c">
                        <span>مدیریت موجودی</span>
                    </label>
                    <label style="display:flex;align-items:center;gap:4px;font-size:11px">
                        <input type="checkbox" wire:model="sold_individually" style="accent-color:#c9a84c">
                        <span>فقط تکی</span>
                    </label>
                </div>
            </div>

            {{-- ★ Price calculator --}}
            <div style="margin-top:12px;padding:10px;background:linear-gradient(135deg,#fef3c7,#fde68a);border-radius:10px">
                <div style="font-size:12px;font-weight:700;color:#78350f;margin-bottom:8px">🧮 ماشین‌حساب قیمت بر مبنای گرم</div>
                <div style="display:flex;gap:8px;flex-wrap:wrap;align-items:center">
                    <input type="number" wire:model="price_per_gram" dir="ltr" placeholder="قیمت هر گرم (تومان)"
                           style="flex:1;min-width:160px;padding:8px 10px;border:1.5px solid #d97706;border-radius:6px;font-family:monospace;font-size:12px">

                    <button type="button" wire:click="applyPricePerGram"
                            style="padding:8px 16px;background:linear-gradient(135deg,#d97706,#92400e);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">
                        🧮 محاسبه برای همه
                    </button>
                </div>
                <div style="font-size:10.5px;color:#78350f;margin-top:6px;opacity:.85">قیمت = وزن × قیمت هر گرم — روی همه ردیف‌هایی که وزن دارن اعمال می‌شه</div>
            </div>
        </div>

        {{-- ★ Attributes selector (as columns) --}}
        @if(!empty($woo_attributes))
            <div class="sg-settings-card" style="margin-bottom:12px">
                <h3>💎 ویژگی‌ها (به عنوان ستون جدول)</h3>
                <p style="font-size:11px;color:#94a3b8;margin:0 0 8px">هر ویژگی که اینجا تیک بزنی، یک ستون در جدول زیر اضافه می‌شه</p>
                <div style="display:flex;flex-wrap:wrap;gap:6px">
                    @foreach($woo_attributes as $a)
                        @php $isOn = !empty($visible_attributes[(string) $a['id']]); @endphp
                        <button type="button"
                                wire:click="toggleVisibleAttribute({{ $a['id'] }})"
                                style="padding:6px 12px;border-radius:20px;font-size:11.5px;font-weight:700;cursor:pointer;
                                    border:1.5px solid {{ $isOn ? '#16a34a' : '#cbd5e1' }};
                                    background:{{ $isOn ? '#d1fae5' : '#fff' }};
                                    color:{{ $isOn ? '#065f46' : '#475569' }}">
                            {{ $isOn ? '✓' : '+' }} {{ $a['name'] }}
                        </button>
                    @endforeach
                </div>
            </div>
        @endif

        
        {{-- ══════ Preview Section ══════ --}}
        @if($showing_preview)
            <div class="sg-settings-card" style="margin-bottom:14px;border:2px solid #7c3aed;background:linear-gradient(135deg,#faf5ff,#f3e8ff)">
                <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:12px">
                    <h3 style="margin:0;color:#5b21b6">👁️ پیش‌نمایش ارسال</h3>
                    <button wire:click="$set('showing_preview', false)"
                            style="background:#fff;color:#7c3aed;border:1.5px solid #c4b5fd;border-radius:8px;padding:5px 12px;font-weight:700;cursor:pointer;font-size:11px">✕ بستن</button>
                </div>

                @if(($run_summary['status'] ?? '') === 'processing')
                    <div style="text-align:center;padding:20px;color:#7c3aed;font-size:13px">{{ $run_summary['msg'] }}</div>
                @elseif(($run_summary['status'] ?? '') === 'error')
                    <div style="padding:10px;background:#fee2e2;color:#991b1b;border-radius:8px;font-size:12px">{{ $run_summary['msg'] }}</div>
                @else
                    <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin-bottom:12px">
                        <div style="padding:10px;background:#fff;border-radius:8px;text-align:center">
                            <div style="font-size:22px;font-weight:800;color:#1a5276">{{ \App\Support\PersianNumber::toFa($run_summary['total'] ?? 0) }}</div>
                            <div style="font-size:10.5px;color:#64748b;font-weight:700">کل</div>
                        </div>
                        <div style="padding:10px;background:#d1fae5;border-radius:8px;text-align:center">
                            <div style="font-size:22px;font-weight:800;color:#065f46">{{ \App\Support\PersianNumber::toFa($run_summary['valid'] ?? 0) }}</div>
                            <div style="font-size:10.5px;color:#065f46;font-weight:700">معتبر</div>
                        </div>
                        <div style="padding:10px;background:#fef3c7;border-radius:8px;text-align:center">
                            <div style="font-size:22px;font-weight:800;color:#92400e">{{ \App\Support\PersianNumber::toFa($run_summary['warnings'] ?? 0) }}</div>
                            <div style="font-size:10.5px;color:#92400e;font-weight:700">هشدار</div>
                        </div>
                    </div>

                    <div style="max-height:300px;overflow-y:auto;border:1px solid #ddd6fe;border-radius:8px;background:#fff">
                        <table style="width:100%;border-collapse:collapse;font-size:11px">
                            <thead style="background:#f3e8ff;position:sticky;top:0">
                                <tr>
                                    <th style="padding:5px;text-align:right;color:#5b21b6">SKU</th>
                                    <th style="padding:5px;text-align:right;color:#5b21b6">عنوان</th>
                                    <th style="padding:5px;text-align:right;color:#5b21b6">وضعیت</th>
                                    <th style="padding:5px;text-align:right;color:#5b21b6">هشدارها</th>
                                </tr>
                            </thead>
                            <tbody>
                                @foreach($preview_data as $pv)
                                    <tr style="border-bottom:1px solid #f3e8ff">
                                        <td style="padding:5px;font-family:monospace;font-weight:700">{{ $pv['sku'] }}</td>
                                        <td style="padding:5px;font-size:10.5px">{{ \Illuminate\Support\Str::limit($pv['title_fa'], 30) }}</td>
                                        <td style="padding:5px">
                                            @if($pv['exists_in_woo'])
                                                <span style="background:#fef3c7;color:#92400e;padding:1px 6px;border-radius:8px;font-size:9.5px;font-weight:700">🔄 موجود</span>
                                            @else
                                                <span style="background:#d1fae5;color:#065f46;padding:1px 6px;border-radius:8px;font-size:9.5px;font-weight:700">✨ جدید</span>
                                            @endif
                                        </td>
                                        <td style="padding:5px;font-size:10px;color:#92400e">
                                            @foreach($pv['warnings'] as $w)
                                                <div>⚠️ {{ $w }}</div>
                                            @endforeach
                                        </td>
                                    </tr>
                                @endforeach
                            </tbody>
                        </table>
                    </div>

                    <div style="display:flex;gap:8px;margin-top:14px;justify-content:flex-end;flex-wrap:wrap">
                        <button wire:click="$set('showing_preview', false)"
                                style="padding:9px 18px;background:#fff;color:#475569;border:1.5px solid #cbd5e1;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">انصراف</button>
                        <button wire:click="confirmSend" wire:loading.attr="disabled"
                                wire:confirm="ارسال {{ $run_summary['valid'] ?? 0 }} محصول به صف؟"
                                style="padding:9px 22px;background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">
                            <span wire:loading.remove wire:target="confirmSend">🚀 ارسال به صف ({{ \App\Support\PersianNumber::toFa($run_summary['valid'] ?? 0) }} آیتم)</span>
                            <span wire:loading wire:target="confirmSend">⏳...</span>
                        </button>
                    </div>
                @endif
            </div>
        @endif

{{-- Bulk SKU add --}}
        <div class="sg-settings-card" style="margin-bottom:12px;background:linear-gradient(135deg,#eff6ff,#dbeafe);border-color:#3b82f6">
            <h3 style="color:#1e40af">⚡ افزودن سریع SKU</h3>
            <textarea wire:model="bulk_skus" rows="2" dir="ltr" placeholder="200 201 202 203 (با فاصله یا خط جدید)"
                      style="width:100%;padding:8px;border:1.5px solid #93c5fd;border-radius:6px;font-family:monospace;font-size:12px;box-sizing:border-box"></textarea>
            <button type="button" wire:click="addBulkSkus"
                    style="margin-top:6px;padding:7px 18px;background:linear-gradient(135deg,#3b82f6,#1e40af);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">
                ⚡ افزودن
            </button>
        </div>

        {{-- Products table --}}
        @php
            $visibleAttrs = [];
            foreach ($visible_attributes as $aid => $on) {
                if (!$on) continue;
                foreach ($woo_attributes as $a) {
                    if ((int) $a['id'] === (int) $aid) {
                        $visibleAttrs[] = $a;
                        $this->loadAttrTerms((int) $aid);
                        break;
                    }
                }
            }
        @endphp

        <div class="sg-settings-card">
            <h3>📋 محصولات ({{ \App\Support\PersianNumber::toFa(count($products)) }})</h3>

            <div style="overflow-x:auto;margin-top:8px">
                <table style="width:100%;border-collapse:collapse;font-size:11px;min-width:1000px">
                    <thead style="background:#f8fafc;position:sticky;top:0;z-index:2">
                        <tr>
                            <th style="padding:6px;color:#1a5276">✓</th>
                            <th style="padding:6px;color:#1a5276">SKU</th>
                            <th style="padding:6px;color:#1a5276">عنوان</th>
                            <th style="padding:6px;color:#1a5276">وزن</th>
                            <th style="padding:6px;color:#1a5276">قیمت</th>
                            @foreach($visibleAttrs as $a)
                                <th style="padding:6px;color:#7c3aed;background:#f3e8ff">{{ $a['name'] }}</th>
                            @endforeach
                            <th style="padding:6px;color:#1a5276">تصاویر</th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody>
                        @foreach($products as $i => $p)
                            <tr wire:key="row-{{ $i }}" style="border-bottom:1px solid #f1f5f9">
                                <td style="padding:3px;text-align:center">
                                    <input type="checkbox" wire:model="products.{{ $i }}.checked" style="accent-color:#16a34a">
                                </td>
                                <td style="padding:3px">
                                    <input type="text" wire:model.live.debounce.400ms="products.{{ $i }}.sku" dir="ltr"
                                           style="width:75px;padding:5px;border:1.5px solid #cbd5e1;border-radius:5px;font-family:monospace;font-size:11px;text-align:center">
                                </td>
                                <td style="padding:3px">
                                    <input type="text" wire:model="products.{{ $i }}.title_fa"
                                           style="width:170px;padding:5px;border:1.5px solid #cbd5e1;border-radius:5px;font-size:11px">
                                </td>
                                <td style="padding:3px">
                                    <input type="text" wire:model.live.debounce.400ms="products.{{ $i }}.weight" dir="ltr"
                                           style="width:55px;padding:5px;border:1.5px solid #cbd5e1;border-radius:5px;font-family:monospace;font-size:11px;text-align:center">
                                </td>
                                <td style="padding:3px">
                                    <input type="text" wire:model="products.{{ $i }}.regular_price" dir="ltr"
                                           style="width:85px;padding:5px;border:1.5px solid #cbd5e1;border-radius:5px;font-family:monospace;font-size:11px;text-align:center">
                                </td>
                                @foreach($visibleAttrs as $a)
                                    @php
                                        $aid = (int) $a['id'];
                                        $currentIds = $p['attr_values'][$aid] ?? [];
                                    @endphp
                                    <td style="padding:3px;background:#faf5ff">
                                        <select wire:model="products.{{ $i }}.attr_values.{{ $aid }}" multiple
                                                style="width:130px;padding:4px;border:1.5px solid #c4b5fd;border-radius:5px;font-size:10.5px;background:#fff;height:50px">
                                            @foreach($attr_terms[$aid] ?? [] as $t)
                                                <option value="{{ $t['id'] }}">{{ $t['name'] }}</option>
                                            @endforeach
                                        </select>
                                    </td>
                                @endforeach
                                <td style="padding:3px;text-align:center">
                                    @if(!empty($p['sku']))
                                        <button type="button" wire:click="showDetail({{ $i }})"
                                                style="background:#e0e7ff;color:#3730a3;border:none;padding:3px 8px;border-radius:5px;font-size:10px;font-weight:700;cursor:pointer">
                                            🖼️
                                        </button>
                                    @endif
                                </td>
                                <td style="padding:3px">
                                    <button type="button" wire:click="removeRow({{ $i }})" wire:confirm="حذف؟"
                                            style="background:#fee2e2;color:#dc2626;border:none;width:24px;height:24px;border-radius:5px;cursor:pointer;font-size:11px">✕</button>
                                </td>
                            </tr>
                        @endforeach
                    </tbody>
                </table>
            </div>

            <div style="display:flex;gap:6px;margin-top:10px;flex-wrap:wrap">
                <button type="button" wire:click="addRow"
                        style="padding:7px 14px;background:#f1f5f9;color:#475569;border:1.5px solid #cbd5e1;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">
                    ➕ ردیف
                </button>
                <button type="button" wire:click="clearAll" wire:confirm="پاک شوند؟"
                        style="padding:7px 14px;background:#fee2e2;color:#dc2626;border:1.5px solid #fca5a5;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">
                    🗑️ پاک کردن
                </button>
            </div>
        </div>
    @endif

    {{-- ══════════════ HISTORY TAB ══════════════ --}}
    @if($tab === 'history')
        <div class="sg-settings-card">
            <h3>📚 تاریخچه محصولات ارسال‌شده</h3>

            <div style="display:flex;gap:6px;margin-bottom:10px;flex-wrap:wrap">
                <input type="text" wire:model.live.debounce.400ms="history_search" placeholder="🔍 SKU یا نام..."
                       style="flex:1;min-width:150px;padding:8px;border:1.5px solid #cbd5e1;border-radius:6px;font-size:12px">
                <select wire:model.live="history_filter" style="padding:8px;border:1.5px solid #cbd5e1;border-radius:6px;font-size:12px">
                    <option value="">همه</option>
                    <option value="publish">✅ منتشر</option>
                    <option value="draft">📝 پیش‌نویس</option>
                    <option value="failed">❌ ناموفق</option>
                </select>
                <button type="button" wire:click="clearHistory" wire:confirm="همه حذف شوند؟"
                        style="padding:8px 14px;background:#fee2e2;color:#dc2626;border:1.5px solid #fca5a5;border-radius:6px;font-weight:700;cursor:pointer;font-size:11.5px">
                    🗑️ پاک کردن همه
                </button>
            </div>

            @if($history->isEmpty())
                <div style="text-align:center;padding:30px;color:#94a3b8;font-size:12px">هنوز محصولی ارسال نشده</div>
            @else
                <div style="overflow-x:auto">
                    <table style="width:100%;border-collapse:collapse;font-size:11.5px;min-width:800px">
                        <thead style="background:#f8fafc">
                            <tr>
                                <th style="padding:6px;text-align:right">SKU</th>
                                <th style="padding:6px;text-align:right">نام</th>
                                <th style="padding:6px;text-align:right">قیمت</th>
                                <th style="padding:6px;text-align:right">وزن</th>
                                <th style="padding:6px;text-align:right">وضعیت</th>
                                <th style="padding:6px;text-align:right">تاریخ</th>
                                <th style="padding:6px;text-align:right">لینک‌ها</th>
                                <th></th>
                            </tr>
                        </thead>
                        <tbody>
                            @foreach($history as $h)
                                <tr style="border-bottom:1px solid #f1f5f9">
                                    <td style="padding:6px;font-family:monospace;font-weight:700">{{ $h->sku }}</td>
                                    <td style="padding:6px;font-size:11px">{{ \Illuminate\Support\Str::limit($h->name, 40) }}</td>
                                    <td style="padding:6px;font-family:monospace">{{ number_format((float) $h->regular_price) }}</td>
                                    <td style="padding:6px;font-family:monospace">{{ $h->weight }}</td>
                                    <td style="padding:6px">
                                        @if($h->status === 'failed')
                                            <span style="background:#fee2e2;color:#991b1b;padding:2px 8px;border-radius:10px;font-size:10px;font-weight:700">❌ ناموفق</span>
                                            @if($h->error_message)
                                                <div style="font-size:9.5px;color:#991b1b;margin-top:2px">{{ \Illuminate\Support\Str::limit($h->error_message, 50) }}</div>
                                            @endif
                                        @elseif($h->status === 'publish')
                                            <span style="background:#d1fae5;color:#065f46;padding:2px 8px;border-radius:10px;font-size:10px;font-weight:700">✅ منتشر</span>
                                        @else
                                            <span style="background:#fef3c7;color:#92400e;padding:2px 8px;border-radius:10px;font-size:10px;font-weight:700">📝 پیش‌نویس</span>
                                        @endif
                                    </td>
                                    <td style="padding:6px;font-size:10px;font-family:monospace">{{ $h->sent_at?->format('Y/m/d H:i') }}</td>
                                    <td style="padding:6px">
                                        <div style="display:flex;gap:3px">
                                            @if($h->woo_edit_url)
                                                <a href="{{ $h->woo_edit_url }}" target="_blank"
                                                   style="background:#dbeafe;color:#1e40af;padding:3px 7px;border-radius:5px;font-size:10px;font-weight:700;text-decoration:none">✏️</a>
                                            @endif
                                            @if($h->woo_view_url)
                                                <a href="{{ $h->woo_view_url }}" target="_blank"
                                                   style="background:#d1fae5;color:#065f46;padding:3px 7px;border-radius:5px;font-size:10px;font-weight:700;text-decoration:none">🌐</a>
                                            @endif
                                        </div>
                                    </td>
                                    <td style="padding:6px">
                                        <div style="display:flex;gap:3px">
                                            @if($h->payload)
                                                <button type="button" wire:click="resendFromHistory({{ $h->id }})"
                                                        style="background:#e0e7ff;color:#3730a3;border:none;padding:3px 7px;border-radius:5px;font-size:10px;font-weight:700;cursor:pointer">🔄</button>
                                            @endif
                                            <button type="button" wire:click="deleteHistory({{ $h->id }})" wire:confirm="حذف؟"
                                                    style="background:#fee2e2;color:#dc2626;border:none;width:24px;height:22px;border-radius:5px;font-size:10px;cursor:pointer">✕</button>
                                        </div>
                                    </td>
                                </tr>
                            @endforeach
                        </tbody>
                    </table>
                </div>
            @endif
        </div>
    @endif

    {{-- ══════════════ QUEUE TAB ══════════════ --}}
    @if($tab === 'queue')
        <div class="sg-settings-card" wire:poll.3s="refreshProgress">
            <h3 style="display:flex;justify-content:space-between;align-items:center">
                <span>📊 گزارش پیشرفت (auto-refresh)</span>
                @if($current_run_id)
                    <a href="{{ route('products.bulk.run', $current_run_id) }}" wire:navigate
                       style="padding:5px 12px;background:#7c3aed;color:#fff;border-radius:8px;font-size:11px;font-weight:700;text-decoration:none">
                        🔍 مشاهده جزئیات Run
                    </a>
                @endif
            </h3>

            @php $pct = $progress_total > 0 ? round(($progress_sent / $progress_total) * 100) : 0; @endphp

            <div style="margin-bottom:12px">
                <div style="display:flex;justify-content:space-between;font-size:11.5px;font-weight:700;margin-bottom:4px">
                    <span>📤 {{ \App\Support\PersianNumber::toFa($progress_sent) }}/{{ \App\Support\PersianNumber::toFa($progress_total) }} ({{ \App\Support\PersianNumber::toFa($pct) }}%)</span>
                </div>
                <div style="height:12px;background:#e2e8f0;border-radius:6px;overflow:hidden">
                    <div style="height:100%;width:{{ $pct }}%;background:linear-gradient(90deg,#16a34a,#10b981);transition:width .3s"></div>
                </div>
            </div>

            <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-bottom:12px">
                <div style="padding:10px;background:#d1fae5;border-radius:8px;text-align:center">
                    <div style="font-size:20px;font-weight:800;color:#065f46">{{ \App\Support\PersianNumber::toFa($progress_ok) }}</div>
                    <div style="font-size:10.5px;color:#065f46;font-weight:700">موفق</div>
                </div>
                <div style="padding:10px;background:#fee2e2;border-radius:8px;text-align:center">
                    <div style="font-size:20px;font-weight:800;color:#991b1b">{{ \App\Support\PersianNumber::toFa($progress_fail) }}</div>
                    <div style="font-size:10.5px;color:#991b1b;font-weight:700">ناموفق</div>
                </div>
            </div>

            <h3>📜 لاگ زنده</h3>
            <div style="max-height:400px;overflow-y:auto;background:#0f172a;border-radius:8px;padding:10px;font-family:monospace;font-size:11px;direction:ltr">
                @forelse($log as $l)
                    <div style="padding:2px 0;color:{{ $l['type'] === 'success' ? '#4ade80' : ($l['type'] === 'error' ? '#f87171' : '#94a3b8') }}">
                        [{{ $l['time'] }}] {{ $l['msg'] }}
                    </div>
                @empty
                    <div style="color:#475569;text-align:center;padding:15px">هنوز ارسالی نشده</div>
                @endforelse
            </div>
        </div>
    @endif

    {{-- ══════════════ DETAIL MODAL ══════════════ --}}
    @if($show_detail && $detail)
        <div style="position:fixed;inset:0;background:rgba(0,0,0,.8);z-index:95;display:flex;align-items:flex-start;justify-content:center;padding:8px;overflow-y:auto"
             @keydown.escape.window="$wire.closeDetail()">
            <div style="background:#fff;width:100%;max-width:760px;margin:8px auto;border-radius:14px;overflow:hidden;direction:rtl">
                <div style="background:linear-gradient(135deg,#7c3aed,#5b21b6);color:#fff;padding:12px 16px;display:flex;justify-content:space-between;align-items:center">
                    <h2 style="margin:0;font-size:14px;font-weight:700">🖼️ SKU {{ $detail['product']['sku'] }}</h2>
                    <button wire:click="closeDetail" style="width:30px;height:30px;border-radius:50%;background:rgba(255,255,255,.2);color:#fff;border:none;cursor:pointer;font-size:14px">X</button>
                </div>
                <div style="padding:14px;max-height:calc(100vh - 140px);overflow-y:auto">
                    <h3 style="font-size:13px;margin:0 0 8px">📸 تصاویر پیش‌بینی</h3>
                    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(100px,1fr));gap:6px">
                        @foreach($detail['images'] as $idx => $url)
                            <div style="background:#f8fafc;border:1.5px solid #e2e8f0;border-radius:8px;padding:5px">
                                <div style="font-size:9.5px;font-weight:700;color:{{ $idx === 0 ? '#16a34a' : '#64748b' }};margin-bottom:3px">
                                    {{ $idx === 0 ? '🌟 شاخص' : '#' . $idx }}
                                </div>
                                <div style="aspect-ratio:1;background:#fff;border-radius:5px;overflow:hidden;display:flex;align-items:center;justify-content:center">
                                    <img src="{{ $url }}" style="width:100%;height:100%;object-fit:cover" onerror="this.replaceWith(document.createTextNode('❌'))">
                                </div>
                                <div style="font-family:monospace;font-size:8.5px;color:#94a3b8;margin-top:3px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap" dir="ltr">{{ $idx }}-{{ $detail['product']['sku'] }}.{{ $image_ext }}</div>
                            </div>
                        @endforeach
                    </div>
                </div>
            </div>
        </div>
    @endif
</div>
