<div style="padding:14px;direction:rtl" @if($activeTab === 'progress') wire:poll.3s="refreshProgress" @endif>

    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px;flex-wrap:wrap;gap:8px">
        <div>
            <h1 style="margin:0;font-size:20px;font-weight:700">🔄 سینک ووکامرس</h1>
            <p style="margin:4px 0 0;font-size:12px;color:#64748b">دریافت سفارشات، محصولات، کاتالوگ و مدیا از سایت</p>
        </div>
    </div>

    {{-- Tabs --}}
    <div style="display:flex;gap:6px;border-bottom:2px solid #e2e8f0;margin-bottom:14px;overflow-x:auto">
        @foreach([
            'overview' => ['📋','شروع سینک'],
            'progress' => ['⏳','در حال اجرا'],
            'items' => ['📦','جزئیات آیتم‌ها'],
            'history' => ['📜','تاریخچه'],
        ] as $k => $meta)
            <button wire:click="$set('activeTab','{{ $k }}')"
                    style="padding:9px 16px;border:none;background:{{ $activeTab === $k ? 'linear-gradient(135deg,#1a5276,#0d3b5e)' : 'transparent' }};color:{{ $activeTab === $k ? '#fff' : '#64748b' }};border-radius:10px 10px 0 0;font-weight:700;cursor:pointer;font-size:12.5px;white-space:nowrap">
                {{ $meta[0] }} {{ $meta[1] }}
            </button>
        @endforeach
    </div>

    {{-- ═══ Overview ═══ --}}
    @if($activeTab === 'overview')
        <div class="sg-settings-card">
            <h3>▶️ شروع سینک جدید</h3>

            <div class="form-grid">
                <div class="field col-6">
                    <label>نوع سینک</label>
                    <select wire:model="syncType" style="width:100%;padding:10px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:13px">
                        <option value="full">🌟 کامل (Catalog + Products)</option>
                        <option value="catalog">📚 فقط کاتالوگ (دسته/ویژگی/اصطلاحات)</option>
                        <option value="products">📦 فقط محصولات</option>
                        <option value="media">🖼️ فقط رسانه (تصاویر)</option>
                    </select>
                </div>
                <div class="field col-6">
                    <label>حالت</label>
                    <select wire:model="syncMode" style="width:100%;padding:10px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:13px">
                        <option value="full">همه چیز</option>
                        <option value="incremental">فقط تغییرات ۳۰ روز اخیر</option>
                    </select>
                </div>
            </div>

            <label style="display:flex;align-items:center;gap:8px;padding:10px;background:#fef3c7;border-radius:8px;cursor:pointer;margin-top:10px">
                <input type="checkbox" wire:model="syncMedia" style="width:18px;height:18px;accent-color:#c9a84c">
                <div>
                    <div style="font-weight:700;font-size:12.5px">شامل سینک Media</div>
                    <div style="font-size:10.5px;color:#78350f">ممکنه زمان‌بر باشد (بالای ۵۰۰۰ تصویر)</div>
                </div>
            </label>

            <div style="display:flex;gap:8px;margin-top:16px;justify-content:flex-end">
                <button wire:click="startSync" wire:loading.attr="disabled"
                        style="padding:11px 28px;background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;border:none;border-radius:10px;font-weight:700;cursor:pointer;font-size:13px">
                    <span wire:loading.remove wire:target="startSync">🚀 شروع سینک</span>
                    <span wire:loading wire:target="startSync">⏳ در حال اجرا...</span>
                </button>
            </div>

            <div style="margin-top:16px;padding:12px;background:#eff6ff;border-radius:10px;font-size:11.5px;line-height:1.7;color:#1e40af">
                💡 <b>راهنما:</b><br>
                • <b>Catalog</b> — دسته‌ها، ویژگی‌ها، اصطلاحات (سریع — ۱-۲ دقیقه)<br>
                • <b>Products</b> — همه محصولات با تصاویر (بسته به تعداد)<br>
                • <b>Media</b> — تصاویر کتابخانه (کندتر)<br>
                • <b>Full</b> — همه موارد بالا
            </div>
        </div>
    @endif

    {{-- ═══ Progress ═══ --}}
    @if($activeTab === 'progress')
        @if(empty($progressData))
            <div style="text-align:center;padding:40px;color:#94a3b8">سینکی در حال اجرا نیست</div>
        @else
            <div class="sg-settings-card">
                <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
                    <h3 style="margin:0">⏳ Run #{{ $progressData['id'] }} — {{ $progressData['type'] }}</h3>
                    <span style="padding:4px 12px;border-radius:10px;font-size:11.5px;font-weight:700;
                        @if($progressData['status'] === 'completed') background:#d1fae5;color:#065f46
                        @elseif($progressData['status'] === 'running') background:#dbeafe;color:#1e40af
                        @elseif($progressData['status'] === 'failed') background:#fee2e2;color:#991b1b
                        @else background:#f1f5f9;color:#475569 @endif">
                        {{ $progressData['status'] }}
                    </span>
                </div>

                <div style="height:14px;background:#e2e8f0;border-radius:7px;overflow:hidden;margin-bottom:14px">
                    <div style="height:100%;width:{{ $progressData['percent'] }}%;background:linear-gradient(90deg,#16a34a,#10b981);transition:width .4s"></div>
                </div>

                <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(90px,1fr));gap:8px;margin-bottom:14px">
                    <div style="padding:10px;background:#f8fafc;border-radius:8px;text-align:center">
                        <div style="font-size:18px;font-weight:800;color:#1a5276">{{ \App\Support\PersianNumber::toFa($progressData['total']) }}</div>
                        <div style="font-size:10px;color:#64748b">کل</div>
                    </div>
                    <div style="padding:10px;background:#d1fae5;border-radius:8px;text-align:center">
                        <div style="font-size:18px;font-weight:800;color:#065f46">{{ \App\Support\PersianNumber::toFa($progressData['created']) }}</div>
                        <div style="font-size:10px;color:#065f46">جدید</div>
                    </div>
                    <div style="padding:10px;background:#dbeafe;border-radius:8px;text-align:center">
                        <div style="font-size:18px;font-weight:800;color:#1e40af">{{ \App\Support\PersianNumber::toFa($progressData['updated']) }}</div>
                        <div style="font-size:10px;color:#1e40af">بروزرسانی</div>
                    </div>
                    <div style="padding:10px;background:#fef3c7;border-radius:8px;text-align:center">
                        <div style="font-size:18px;font-weight:800;color:#92400e">{{ \App\Support\PersianNumber::toFa($progressData['skipped']) }}</div>
                        <div style="font-size:10px;color:#92400e">رد</div>
                    </div>
                    <div style="padding:10px;background:#fee2e2;border-radius:8px;text-align:center">
                        <div style="font-size:18px;font-weight:800;color:#991b1b">{{ \App\Support\PersianNumber::toFa($progressData['failed']) }}</div>
                        <div style="font-size:10px;color:#991b1b">خطا</div>
                    </div>
                </div>

                @if($progressData['duration'])
                    <div style="font-size:11.5px;color:#64748b;margin-bottom:10px">
                        ⏱️ مدت: {{ \App\Support\PersianNumber::toFa($progressData['duration']) }} ثانیه
                    </div>
                @endif

                <h3 style="margin-top:14px">📜 لاگ زنده</h3>
                <div style="max-height:280px;overflow-y:auto;background:#0f172a;border-radius:8px;padding:10px;font-family:monospace;font-size:11px;direction:ltr">
                    @forelse($syncLog as $l)
                        <div style="padding:2px 0;color:{{ $l['type'] === 'success' ? '#4ade80' : ($l['type'] === 'error' ? '#f87171' : ($l['type'] === 'warn' ? '#fbbf24' : '#94a3b8')) }}">
                            [{{ $l['time'] }}] {{ $l['msg'] }}
                        </div>
                    @empty
                        <div style="color:#475569;text-align:center;padding:15px">هنوز لاگی نیست</div>
                    @endforelse
                </div>
            </div>
        @endif
    @endif

    {{-- ═══ Items ═══ --}}
    @if($activeTab === 'items')
        @if(!$currentRunId)
            <div style="text-align:center;padding:40px;color:#94a3b8">یک Run انتخاب کن</div>
        @else
            <div class="sg-settings-card">
                <div style="display:flex;gap:6px;margin-bottom:12px;flex-wrap:wrap">
                    <input type="text" wire:model.live.debounce.400ms="filterEntity" placeholder="entity_type (product/order/...)"
                           style="padding:8px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:12px">
                    <select wire:model.live="filterStatus" style="padding:8px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:12px">
                        <option value="">همه وضعیت‌ها</option>
                        <option value="created">جدید</option>
                        <option value="updated">بروزرسانی</option>
                        <option value="failed">خطا</option>
                        <option value="skipped">رد شده</option>
                    </select>
                </div>

                <div style="overflow-x:auto">
                    <table style="width:100%;border-collapse:collapse;font-size:11.5px">
                        <thead style="background:#f8fafc">
                            <tr>
                                <th style="padding:6px;text-align:right">#</th>
                                <th style="padding:6px;text-align:right">نوع</th>
                                <th style="padding:6px;text-align:right">شناسه</th>
                                <th style="padding:6px;text-align:right">وضعیت</th>
                                <th style="padding:6px;text-align:right">خطا</th>
                            </tr>
                        </thead>
                        <tbody>
                            @forelse($items as $it)
                                <tr style="border-bottom:1px solid #f1f5f9">
                                    <td style="padding:5px;font-family:monospace">{{ $it->id }}</td>
                                    <td style="padding:5px;font-size:10.5px">{{ $it->entity_type }}</td>
                                    <td style="padding:5px;font-family:monospace;font-size:10.5px">{{ $it->entity_id }}</td>
                                    <td style="padding:5px">
                                        <span style="padding:2px 8px;border-radius:8px;font-size:10px;font-weight:700;
                                            @if($it->status === 'created') background:#d1fae5;color:#065f46
                                            @elseif($it->status === 'updated') background:#dbeafe;color:#1e40af
                                            @elseif($it->status === 'failed') background:#fee2e2;color:#991b1b
                                            @else background:#f1f5f9;color:#475569 @endif">
                                            {{ $it->status }}
                                        </span>
                                    </td>
                                    <td style="padding:5px;font-size:10.5px;color:#991b1b;max-width:200px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">
                                        {{ $it->error_message ? mb_substr($it->error_message, 0, 60) : '—' }}
                                    </td>
                                </tr>
                            @empty
                                <tr><td colspan="5" style="text-align:center;padding:20px;color:#94a3b8">آیتمی نیست</td></tr>
                            @endforelse
                        </tbody>
                    </table>
                </div>

                @if(method_exists($items, 'links'))
                    <div style="padding:10px">{{ $items->links() }}</div>
                @endif
            </div>
        @endif
    @endif

    {{-- ═══ History ═══ --}}
    @if($activeTab === 'history')
        <div class="sg-settings-card">
            <h3>📜 تاریخچه سینک‌ها</h3>

            <div style="overflow-x:auto">
                <table style="width:100%;border-collapse:collapse;font-size:11.5px">
                    <thead style="background:#f8fafc">
                        <tr>
                            <th style="padding:7px;text-align:right">#</th>
                            <th style="padding:7px;text-align:right">نوع</th>
                            <th style="padding:7px;text-align:right">وضعیت</th>
                            <th style="padding:7px;text-align:right">کل</th>
                            <th style="padding:7px;text-align:right">جدید</th>
                            <th style="padding:7px;text-align:right">بروزرسانی</th>
                            <th style="padding:7px;text-align:right">خطا</th>
                            <th style="padding:7px;text-align:right">زمان</th>
                            <th></th>
                        </tr>
                    </thead>
                    <tbody>
                        @forelse($runs as $r)
                            <tr style="border-bottom:1px solid #f1f5f9">
                                <td style="padding:6px;font-family:monospace;font-weight:700">#{{ $r->id }}</td>
                                <td style="padding:6px">
                                    <span style="padding:2px 8px;border-radius:8px;background:#eff6ff;color:#1e40af;font-size:10px;font-weight:700">{{ $r->type }}</span>
                                </td>
                                <td style="padding:6px">
                                    <span style="padding:2px 8px;border-radius:8px;font-size:10px;font-weight:700;
                                        @if($r->status === 'completed') background:#d1fae5;color:#065f46
                                        @elseif($r->status === 'running') background:#dbeafe;color:#1e40af
                                        @elseif($r->status === 'failed') background:#fee2e2;color:#991b1b
                                        @else background:#f1f5f9;color:#475569 @endif">
                                        {{ $r->status }}
                                    </span>
                                </td>
                                <td style="padding:6px;font-family:monospace">{{ \App\Support\PersianNumber::toFa($r->total_items) }}</td>
                                <td style="padding:6px;font-family:monospace;color:#065f46">{{ \App\Support\PersianNumber::toFa($r->created_items) }}</td>
                                <td style="padding:6px;font-family:monospace;color:#1e40af">{{ \App\Support\PersianNumber::toFa($r->updated_items) }}</td>
                                <td style="padding:6px;font-family:monospace;color:#991b1b">{{ \App\Support\PersianNumber::toFa($r->failed_items) }}</td>
                                <td style="padding:6px;font-size:10px;font-family:monospace">
                                    {{ $r->started_at ? \App\Support\PersianDate::format($r->started_at, 'Y/m/d H:i') : '—' }}
                                </td>
                                <td style="padding:6px">
                                    <div style="display:flex;gap:3px">
                                        <button wire:click="viewRun({{ $r->id }})"
                                                style="padding:3px 8px;background:#dbeafe;color:#1e40af;border:none;border-radius:5px;font-size:10px;cursor:pointer;font-weight:700">👁️</button>
                                        <button wire:click="deleteRun({{ $r->id }})" wire:confirm="حذف؟"
                                                style="padding:3px 8px;background:#fee2e2;color:#dc2626;border:none;border-radius:5px;font-size:10px;cursor:pointer">🗑️</button>
                                    </div>
                                </td>
                            </tr>
                        @empty
                            <tr><td colspan="9" style="text-align:center;padding:20px;color:#94a3b8">سینکی انجام نشده</td></tr>
                        @endforelse
                    </tbody>
                </table>
            </div>
            <div style="padding:10px">{{ $runs->links() }}</div>
        </div>
    @endif
</div>
