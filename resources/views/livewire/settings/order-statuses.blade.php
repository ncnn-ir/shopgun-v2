<div style="padding:0" dir="rtl">

    @if(session()->has('message'))
        <div style="background:#d1fae5;color:#065f46;border:1px solid #6ee7b7;
                    border-radius:10px;padding:10px 14px;font-size:12.5px;font-weight:600;margin-bottom:12px">
            ✅ {{ session('message') }}
        </div>
    @endif

    <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:10px;margin-bottom:14px">
        <div>
            <h3 style="margin:0;font-size:15px;font-weight:700;color:#1e293b">
                📋 وضعیت‌های سفارش
            </h3>
            <p style="margin:4px 0 0;font-size:11.5px;color:#64748b">
                تعیین کن کدام وضعیت‌ها وارد سیستم شوند، نمایش داده شوند و در فروش شمرده شوند
            </p>
        </div>
        <button wire:click="save" wire:loading.attr="disabled"
            style="padding:9px 22px;background:linear-gradient(135deg,#16a34a,#15803d);
                   color:#fff;border:none;border-radius:9px;font-weight:700;cursor:pointer;font-size:12.5px;
                   box-shadow:0 2px 6px rgba(22,163,74,.25)">
            <span wire:loading.remove wire:target="save">💾 ذخیره</span>
            <span wire:loading wire:target="save">⏳...</span>
        </button>
    </div>

    <div style="overflow-x:auto;border:1px solid #e2e8f0;border-radius:12px;background:#fff">
        <table class="os-table">
            <thead>
                <tr>
                    <th style="width:130px">اسلاگ</th>
                    <th style="min-width:180px">عنوان (فارسی)</th>
                    <th style="width:100px;text-align:center">رنگ</th>
                    <th style="width:90px;text-align:center">نمایش</th>
                    <th style="width:110px;text-align:center">ایمپورت</th>
                    <th style="width:110px;text-align:center">شمارش فروش</th>
                    <th style="width:70px;text-align:center">ترتیب</th>
                </tr>
            </thead>
            <tbody>
                @foreach($statuses as $i => $s)
                    <tr wire:key="os-{{ $s['id'] }}">
                        <td>
                            <span class="os-slug">{{ $s['slug'] }}</span>
                        </td>
                        <td>
                            <input type="text" wire:model="statuses.{{ $i }}.title" class="os-input" />
                        </td>
                        <td style="text-align:center">
                            <select wire:model="statuses.{{ $i }}.color" class="os-input" style="text-align:center">
                                @foreach(\App\Models\OrderStatus::COLORS as $k => $v)
                                    <option value="{{ $k }}">{{ $v }}</option>
                                @endforeach
                            </select>
                        </td>
                        <td style="text-align:center">
                            <input type="checkbox" wire:model="statuses.{{ $i }}.is_active" class="os-checkbox" />
                        </td>
                        <td style="text-align:center">
                            <input type="checkbox" wire:model="statuses.{{ $i }}.should_import" class="os-checkbox" />
                        </td>
                        <td style="text-align:center">
                            <input type="checkbox" wire:model="statuses.{{ $i }}.should_count_sales" class="os-checkbox" />
                        </td>
                        <td style="text-align:center">
                            <input type="number" wire:model="statuses.{{ $i }}.sort_order" class="os-input"
                                style="text-align:center;padding:5px" />
                        </td>
                    </tr>
                @endforeach
            </tbody>
        </table>
    </div>

    <div style="margin-top:14px;padding:12px 14px;border-radius:10px;
                background:linear-gradient(135deg,#eff6ff,#dbeafe);
                border:1px solid #93c5fd;font-size:11.5px;color:#1e40af">
        <div style="font-weight:700;margin-bottom:6px">💡 راهنما</div>
        <div style="line-height:1.9">
            • <b>نمایش:</b> آیا این وضعیت در لیست سفارشات دیده شود<br>
            • <b>ایمپورت:</b> آیا سفارشات با این وضعیت از ووکامرس دریافت شوند<br>
            • <b>شمارش فروش:</b> آیا این وضعیت در گزارش‌ها و KPI حساب شود
        </div>
    </div>
</div>
