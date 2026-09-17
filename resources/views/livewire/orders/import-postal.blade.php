<div>
@if($show)
<div class="sg-modal-overlay active" @keydown.escape.window="$wire.close()">
    <div class="sg-modal" style="max-width:820px">
        <div class="sg-modal-header" style="background:linear-gradient(135deg,#3498db,#1a5276)">
            <h2>📮 ایمپورت مرسولات پستی</h2>
            <button wire:click="close" class="sg-modal-close">✕</button>
        </div>

        <div class="sg-modal-body">
            @if(empty($columns))
                {{-- Step 1: Upload --}}
                <div class="form-group">
                    <label>فایل CSV/TSV (خروجی از شرکت پستی)</label>
                    <input type="file" wire:model="file" accept=".csv,.tsv,.txt" class="form-control">
                    <div wire:loading wire:target="file" style="text-align:center;padding:10px;color:var(--primary)">⏳ در حال بارگذاری...</div>
                </div>
                <div style="padding:10px 12px;background:rgba(52,152,219,.08);border-radius:10px;font-size:11.5px;line-height:1.7">
                    💡 تطبیق با سفارشات بر اساس <strong>شماره تلفن گیرنده</strong>.<br>
                    🔖 از Excel: File → Save As → CSV UTF-8
                </div>
            @else
                {{-- Stats --}}
                <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px">
                    <div style="padding:8px 14px;background:var(--bg);border-radius:10px;font-size:12px">📋 <strong>{{ \App\Support\PersianNumber::toFa(count($rows)) }}</strong> ردیف</div>
                    <div style="padding:8px 14px;background:rgba(39,174,96,.1);border-radius:10px;font-size:12px;color:var(--success)">🎯 <strong>{{ \App\Support\PersianNumber::toFa($matched) }}</strong> تطبیق</div>
                    <div style="padding:8px 14px;background:rgba(231,76,60,.1);border-radius:10px;font-size:12px;color:var(--danger)">⚠️ <strong>{{ \App\Support\PersianNumber::toFa($unmatched) }}</strong> بدون تطبیق</div>
                </div>

                {{-- Column Mapping --}}
                <div style="font-weight:700;font-size:12.5px;color:var(--primary);margin-bottom:8px">🗺️ نگاشت ستون‌ها</div>
                <div style="max-height:280px;overflow:auto;border-radius:10px;border:1px solid var(--border);margin-bottom:14px">
                    <table style="width:100%;border-collapse:collapse;font-size:12px">
                        <thead style="position:sticky;top:0;background:var(--thead-bg)">
                            <tr>
                                <th style="padding:8px;text-align:right">ستون فایل</th>
                                <th style="padding:8px;text-align:right">نمونه</th>
                                <th style="padding:8px;text-align:right">فیلد مقصد</th>
                            </tr>
                        </thead>
                        <tbody>
                            @foreach($columns as $i => $col)
                                <tr style="border-top:1px solid var(--border)">
                                    <td style="padding:8px;font-weight:700">{{ $col }}</td>
                                    <td style="padding:8px;font-size:10.5px;opacity:.7;max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ $rows[0][$i] ?? '—' }}</td>
                                    <td style="padding:8px">
                                        <select wire:model.live="mapping.{{ $i }}" class="form-control" style="padding:4px 8px;font-size:11px">
                                            @foreach($availableFields as $k => $v)
                                                <option value="{{ $k }}">{{ $v }}</option>
                                            @endforeach
                                        </select>
                                    </td>
                                </tr>
                            @endforeach
                        </tbody>
                    </table>
                </div>

                {{-- Preview --}}
                <details style="margin-bottom:14px">
                    <summary style="cursor:pointer;font-weight:700;font-size:12px;color:var(--primary);padding:8px;background:var(--bg);border-radius:8px">👁️ پیش‌نمایش ۵ ردیف</summary>
                    <div style="max-height:240px;overflow:auto;margin-top:8px;border:1px solid var(--border);border-radius:8px">
                        <table style="width:100%;border-collapse:collapse;font-size:10.5px">
                            <thead style="background:var(--thead-bg);position:sticky;top:0">
                                <tr>
                                    @foreach($columns as $col)<th style="padding:6px;text-align:right;white-space:nowrap">{{ $col }}</th>@endforeach
                                </tr>
                            </thead>
                            <tbody>
                                @foreach($preview as $row)
                                    <tr style="border-top:1px solid var(--border)">
                                        @foreach($row as $cell)
                                            <td style="padding:6px;max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ $cell }}</td>
                                        @endforeach
                                    </tr>
                                @endforeach
                            </tbody>
                        </table>
                    </div>
                </details>
            @endif
        </div>

        <div class="sg-modal-footer">
            <button wire:click="close" class="btn btn-outline">انصراف</button>
            @if(!empty($columns))
                <button wire:click="save" wire:loading.attr="disabled" class="btn btn-success">
                    <span wire:loading.remove wire:target="save">✅ اعمال و بروزرسانی</span>
                    <span wire:loading wire:target="save">⏳ در حال اعمال...</span>
                </button>
            @endif
        </div>
    </div>
</div>
@endif
</div>
