<div style="padding:12px;direction:rtl" wire:poll.5s="refresh">

    @if(!$run)
        <div style="text-align:center;padding:40px;color:#94a3b8">Run پیدا نشد</div>
    @else

    {{-- Header --}}
    <div style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:8px;margin-bottom:14px">
        <div>
            <h1 style="margin:0;font-size:19px;font-weight:700">📊 جزئیات اجرای #{{ $run->id }}</h1>
            <p style="margin:4px 0 0;font-size:11.5px;color:#64748b">
                شروع: {{ $run->started_at ? \App\Support\PersianDate::format($run->started_at, 'Y/m/d H:i') : '—' }}
                @if($run->finished_at)
                    · پایان: {{ \App\Support\PersianDate::format($run->finished_at, 'Y/m/d H:i') }}
                @endif
            </p>
        </div>
        <div style="display:flex;gap:6px;flex-wrap:wrap">
            @if(in_array($run->status, ['processing', 'queued']))
                <button wire:click="cancel" wire:confirm="لغو شود؟"
                        style="padding:7px 14px;background:#fee2e2;color:#dc2626;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">
                    🛑 لغو
                </button>
            @endif
            @if($run->failed_items > 0)
                <button wire:click="retryFailed" wire:confirm="آیتم‌های ناموفق مجدداً ارسال شوند؟"
                        style="padding:7px 14px;background:linear-gradient(135deg,#f59e0b,#d97706);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">
                    🔄 Retry ناموفق‌ها ({{ \App\Support\PersianNumber::toFa($run->failed_items) }})
                </button>
            @endif
            <a href="{{ route('products.bulk') }}" wire:navigate
               style="padding:7px 14px;background:#f1f5f9;color:#475569;border:1.5px solid #cbd5e1;border-radius:8px;font-weight:700;text-decoration:none;font-size:12px">
                ← بازگشت
            </a>
        </div>
    </div>

    {{-- Progress --}}
    @php $pct = $run->progress_percent; @endphp
    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:14px;margin-bottom:12px">
        <div style="display:flex;justify-content:space-between;font-size:12px;font-weight:700;margin-bottom:6px">
            <span>📤 پیشرفت</span>
            <span>{{ \App\Support\PersianNumber::toFa($pct) }}%</span>
        </div>
        <div style="height:12px;background:#e2e8f0;border-radius:6px;overflow:hidden;margin-bottom:12px">
            <div style="height:100%;width:{{ $pct }}%;background:linear-gradient(90deg,#16a34a,#10b981);transition:width .4s"></div>
        </div>

        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(100px,1fr));gap:8px">
            <div style="padding:10px;background:#f8fafc;border-radius:8px;text-align:center">
                <div style="font-size:18px;font-weight:800;color:#1a5276">{{ \App\Support\PersianNumber::toFa($run->total_items) }}</div>
                <div style="font-size:10px;color:#64748b;font-weight:700">کل</div>
            </div>
            <div style="padding:10px;background:#dbeafe;border-radius:8px;text-align:center">
                <div style="font-size:18px;font-weight:800;color:#1e40af">{{ \App\Support\PersianNumber::toFa($run->queued_items) }}</div>
                <div style="font-size:10px;color:#1e40af;font-weight:700">در صف</div>
            </div>
            <div style="padding:10px;background:#fef3c7;border-radius:8px;text-align:center">
                <div style="font-size:18px;font-weight:800;color:#92400e">{{ \App\Support\PersianNumber::toFa($run->processing_items) }}</div>
                <div style="font-size:10px;color:#92400e;font-weight:700">پردازش</div>
            </div>
            <div style="padding:10px;background:#d1fae5;border-radius:8px;text-align:center">
                <div style="font-size:18px;font-weight:800;color:#065f46">{{ \App\Support\PersianNumber::toFa($run->success_items) }}</div>
                <div style="font-size:10px;color:#065f46;font-weight:700">موفق</div>
            </div>
            <div style="padding:10px;background:#fee2e2;border-radius:8px;text-align:center">
                <div style="font-size:18px;font-weight:800;color:#991b1b">{{ \App\Support\PersianNumber::toFa($run->failed_items) }}</div>
                <div style="font-size:10px;color:#991b1b;font-weight:700">ناموفق</div>
            </div>
        </div>
    </div>

    {{-- Filters --}}
    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;padding:8px;margin-bottom:10px;display:grid;grid-template-columns:1fr 1fr;gap:6px">
        <input type="text" wire:model.live.debounce.400ms="search" placeholder="🔍 جستجوی SKU..."
               style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:12px;background:#f8fafc;box-sizing:border-box">
        <select wire:model.live="filterStatus" style="width:100%;padding:7px 10px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:12px;background:#f8fafc">
            <option value="">همه وضعیت‌ها ({{ array_sum($statusCounts) }})</option>
            @foreach(['pending'=>'⏸️ در انتظار','valid'=>'✓ معتبر','invalid'=>'⚠️ نامعتبر','queued'=>'🕐 در صف','processing'=>'⏳ پردازش','success'=>'✅ موفق','draft_created'=>'📝 پیش‌نویس','failed'=>'❌ ناموفق'] as $k => $lbl)
                @if(isset($statusCounts[$k]))
                    <option value="{{ $k }}">{{ $lbl }} ({{ $statusCounts[$k] }})</option>
                @endif
            @endforeach
        </select>
    </div>

    {{-- Items Table --}}
    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;overflow:hidden">
        <div style="overflow-x:auto">
            <table style="width:100%;border-collapse:collapse;font-size:11.5px;min-width:700px">
                <thead style="background:#f8fafc;position:sticky;top:0;z-index:2">
                    <tr>
                        <th wire:click="$set('sortBy','id')" style="padding:7px;text-align:right;color:#1a5276;cursor:pointer">#</th>
                        <th wire:click="$set('sortBy','sku')" style="padding:7px;text-align:right;color:#1a5276;cursor:pointer">SKU</th>
                        <th style="padding:7px;text-align:right;color:#1a5276">عنوان</th>
                        <th style="padding:7px;text-align:right;color:#1a5276">قیمت</th>
                        <th style="padding:7px;text-align:right;color:#1a5276">وضعیت</th>
                        <th style="padding:7px;text-align:right;color:#1a5276">جزئیات</th>
                    </tr>
                </thead>
                <tbody>
                    @forelse($items as $it)
                        @php
                            $stMap = [
                                'pending' => ['⏸️', 'در انتظار', '#f1f5f9', '#475569'],
                                'valid' => ['✓', 'معتبر', '#d1fae5', '#065f46'],
                                'invalid' => ['⚠️', 'نامعتبر', '#fef3c7', '#92400e'],
                                'queued' => ['🕐', 'در صف', '#dbeafe', '#1e40af'],
                                'processing' => ['⏳', 'پردازش', '#fef3c7', '#92400e'],
                                'success' => ['✅', 'موفق', '#d1fae5', '#065f46'],
                                'draft_created' => ['📝', 'پیش‌نویس', '#fef3c7', '#92400e'],
                                'failed' => ['❌', 'ناموفق', '#fee2e2', '#991b1b'],
                            ];
                            $st = $stMap[$it->status] ?? ['—', $it->status, '#f1f5f9', '#475569'];
                        @endphp
                        <tr wire:key="item-{{ $it->id }}" style="border-bottom:1px solid #f1f5f9;cursor:pointer"
                            wire:click="showItem({{ $it->id }})">
                            <td style="padding:6px;font-family:monospace;font-size:10.5px">{{ \App\Support\PersianNumber::toFa($it->id) }}</td>
                            <td style="padding:6px;font-family:monospace;font-weight:700;font-size:11px">{{ $it->sku }}</td>
                            <td style="padding:6px;font-size:11px;max-width:180px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">
                                {{ $it->input_data['title_fa'] ?? '—' }}
                            </td>
                            <td style="padding:6px;font-family:monospace;font-size:10.5px">
                                @if(!empty($it->input_data['regular_price']))
                                    {{ number_format((float) $it->input_data['regular_price']) }}
                                @else — @endif
                            </td>
                            <td style="padding:6px">
                                <span style="background:{{ $st[2] }};color:{{ $st[3] }};padding:2px 8px;border-radius:10px;font-size:10px;font-weight:700;white-space:nowrap">
                                    {{ $st[0] }} {{ $st[1] }}
                                </span>
                            </td>
                            <td style="padding:6px;font-size:10.5px">
                                @if($it->error_message)
                                    <span style="color:#991b1b">{{ \Illuminate\Support\Str::limit($it->error_message, 40) }}</span>
                                @elseif($it->woo_product_id)
                                    <a href="{{ $it->woo_edit_url }}" target="_blank" style="color:#1e40af;text-decoration:none" onclick="event.stopPropagation()">✏️ ID {{ $it->woo_product_id }}</a>
                                @else
                                    <span style="color:#94a3b8">—</span>
                                @endif
                            </td>
                        </tr>
                    @empty
                        <tr>
                            <td colspan="6" style="text-align:center;padding:30px;color:#94a3b8">آیتمی با این فیلتر نیست</td>
                        </tr>
                    @endforelse
                </tbody>
            </table>
        </div>
        <div style="padding:10px">{{ $items->links() }}</div>
    </div>

    @endif

    {{-- ══════ Item Detail Modal ══════ --}}
    @if($showItemDetail && $itemDetail)
        <div style="position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:95;display:flex;align-items:flex-start;justify-content:center;padding:8px;overflow-y:auto"
             @keydown.escape.window="$wire.closeItem()">

            <div style="background:#fff;width:100%;max-width:640px;margin:8px auto;border-radius:14px;overflow:hidden;direction:rtl">

                <div style="background:linear-gradient(135deg,#1a5276,#0d3b5e);color:#fff;padding:12px 16px;display:flex;justify-content:space-between;align-items:center">
                    <h2 style="margin:0;font-size:14px;font-weight:700">🔍 SKU {{ $itemDetail['sku'] }}</h2>
                    <button wire:click="closeItem" style="width:30px;height:30px;border-radius:50%;background:rgba(255,255,255,.2);color:#fff;border:none;cursor:pointer;font-size:14px">✕</button>
                </div>

                <div style="padding:14px;max-height:calc(100vh - 140px);overflow-y:auto">

                    {{-- Warnings --}}
                    @if(!empty($itemDetail['warnings']))
                        <div style="padding:10px;background:#fef3c7;border-radius:8px;margin-bottom:12px">
                            <div style="font-size:11.5px;font-weight:700;color:#92400e;margin-bottom:6px">⚠️ هشدارها</div>
                            @foreach($itemDetail['warnings'] as $w)
                                <div style="font-size:11px;color:#92400e">• {{ $w }}</div>
                            @endforeach
                        </div>
                    @endif

                    {{-- Error --}}
                    @if($itemDetail['error_message'])
                        <div style="padding:10px;background:#fee2e2;border-radius:8px;margin-bottom:12px">
                            <div style="font-size:11.5px;font-weight:700;color:#991b1b;margin-bottom:4px">❌ خطا ({{ $itemDetail['error_code'] ?? 'unknown' }})</div>
                            <div style="font-size:11px;color:#991b1b;font-family:monospace">{{ $itemDetail['error_message'] }}</div>
                        </div>
                    @endif

                    {{-- Success links --}}
                    @if($itemDetail['woo_product_id'])
                        <div style="padding:10px;background:#d1fae5;border-radius:8px;margin-bottom:12px;display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:6px">
                            <span style="font-size:11.5px;font-weight:700;color:#065f46">✅ Woo ID: {{ $itemDetail['woo_product_id'] }}</span>
                            <div style="display:flex;gap:6px">
                                @if($itemDetail['edit_url'])
                                    <a href="{{ $itemDetail['edit_url'] }}" target="_blank"
                                       style="padding:4px 12px;background:#065f46;color:#fff;border-radius:6px;font-size:11px;font-weight:700;text-decoration:none">✏️ ویرایش</a>
                                @endif
                                @if($itemDetail['view_url'])
                                    <a href="{{ $itemDetail['view_url'] }}" target="_blank"
                                       style="padding:4px 12px;background:#16a34a;color:#fff;border-radius:6px;font-size:11px;font-weight:700;text-decoration:none">🌐 مشاهده</a>
                                @endif
                            </div>
                        </div>
                    @endif

                    {{-- Input data --}}
                    <div style="font-size:11px;font-weight:700;color:#1a5276;margin-bottom:6px">📥 داده ورودی</div>
                    <div style="background:#f8fafc;border-radius:8px;padding:10px;margin-bottom:12px;font-size:11px;font-family:monospace;direction:ltr;white-space:pre-wrap;overflow-x:auto;max-height:200px">
{{ json_encode($itemDetail['input'], JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT) }}
                    </div>

                    {{-- Request --}}
                    @if($itemDetail['request'])
                        <div style="font-size:11px;font-weight:700;color:#1a5276;margin-bottom:6px">📤 درخواست</div>
                        <div style="background:#f8fafc;border-radius:8px;padding:10px;margin-bottom:12px;font-size:10px;font-family:monospace;direction:ltr;white-space:pre-wrap;overflow-x:auto;max-height:200px">
{{ json_encode($itemDetail['request'], JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT) }}
                        </div>
                    @endif

                    {{-- Response --}}
                    @if($itemDetail['response'])
                        <div style="font-size:11px;font-weight:700;color:#1a5276;margin-bottom:6px">📥 پاسخ</div>
                        <div style="background:#f8fafc;border-radius:8px;padding:10px;font-size:10px;font-family:monospace;direction:ltr;white-space:pre-wrap;overflow-x:auto;max-height:200px">
{{ json_encode($itemDetail['response'], JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT) }}
                        </div>
                    @endif

                    {{-- Timing --}}
                    <div style="margin-top:12px;padding-top:12px;border-top:1px solid #e2e8f0;font-size:10.5px;color:#64748b;display:flex;justify-content:space-between;flex-wrap:wrap;gap:4px">
                        <span>شروع: {{ $itemDetail['started_at'] ?? '—' }}</span>
                        <span>پایان: {{ $itemDetail['finished_at'] ?? '—' }}</span>
                        <span>تلاش: {{ $itemDetail['attempt'] }}</span>
                    </div>
                </div>
            </div>
        </div>
    @endif
</div>
