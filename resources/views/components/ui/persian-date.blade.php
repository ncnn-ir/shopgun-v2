@props([
    'wire' => 'date',
    'label' => 'تاریخ',
    'placeholder' => '۱۴۰۳/۰۱/۰۱',
])

<div class="form-control">
    @if($label)
        <label class="label py-1"><span class="label-text text-xs font-bold">{{ $label }}</span></label>
    @endif

    <div class="persian-date-wrap relative" wire:ignore x-data="persianDatePicker(@entangle($wire))">
        <input
            type="text"
            x-ref="input"
            :value="displayValue"
            @focus="open()"
            @click="open()"
            dir="ltr"
            placeholder="{{ $placeholder }}"
            class="input input-bordered input-sm w-full font-mono text-center"
            readonly />

        {{-- پنل انتخابگر --}}
        <div x-show="isOpen"
             x-transition.opacity
             @click.outside="close()"
             class="absolute z-[100] mt-1 bg-base-100 border-2 border-primary rounded-lg shadow-xl p-3"
             style="width: 280px; top: 100%; right: 0;">

            {{-- هدر --}}
            <div class="flex justify-between items-center mb-2">
                <button type="button" @click="prevMonth()" class="btn btn-ghost btn-xs btn-circle">‹</button>
                <div class="text-sm font-bold" x-text="monthNames[month-1] + ' ' + toFa(year)"></div>
                <button type="button" @click="nextMonth()" class="btn btn-ghost btn-xs btn-circle">›</button>
            </div>

            {{-- روزهای هفته --}}
            <div class="grid grid-cols-7 gap-1 mb-1 text-[10px] text-base-content/60 text-center">
                <div>ش</div><div>ی</div><div>د</div><div>س</div><div>چ</div><div>پ</div><div>ج</div>
            </div>

            {{-- روزها --}}
            <div class="grid grid-cols-7 gap-1">
                <template x-for="blank in firstDayOffset" :key="'b' + blank">
                    <div></div>
                </template>
                <template x-for="day in daysInMonth" :key="day">
                    <button type="button"
                            @click="pick(day)"
                            class="w-full aspect-square rounded text-xs font-bold transition"
                            :class="{
                                'bg-primary text-primary-content': isSelected(day),
                                'hover:bg-base-300': !isSelected(day),
                            }"
                            x-text="toFa(day)"></button>
                </template>
            </div>

            {{-- دکمه‌ها --}}
            <div class="flex justify-between mt-3 pt-2 border-t border-base-300">
                <button type="button" @click="clear()" class="btn btn-ghost btn-xs">پاک کردن</button>
                <button type="button" @click="today()" class="btn btn-primary btn-xs">امروز</button>
            </div>
        </div>
    </div>
</div>

@once
@push('scripts')
<script>
function persianDatePicker(initialValue) {
    return {
        isOpen: false,
        year: 1403,
        month: 1,
        value: initialValue || '',

        monthNames: ['فروردین', 'اردیبهشت', 'خرداد', 'تیر', 'مرداد', 'شهریور', 'مهر', 'آبان', 'آذر', 'دی', 'بهمن', 'اسفند'],
        monthDays: [31, 31, 31, 31, 31, 31, 30, 30, 30, 30, 30, 29],

        get displayValue() {
            if (!this.value) return '';
            const parts = String(this.value).split('/');
            if (parts.length !== 3) return this.value;
            return this.toFa(parts[0]) + '/' + this.toFa(parts[1]) + '/' + this.toFa(parts[2]);
        },

        get daysInMonth() {
            return this.monthDays[this.month - 1];
        },

        get firstDayOffset() {
            // محاسبه‌ی ساده: روز هفته‌ی اول ماه
            // (کافیه برای نمایش)
            return (this.year * 365 + this.month * 30) % 7;
        },

        toFa(n) {
            return String(n).replace(/\d/g, d => '۰۱۲۳۴۵۶۷۸۹'[d]);
        },

        init() {
            // تاریخ امروز رو تنظیم کن
            const today = new Date();
            const jalali = this.gregorianToJalali(today.getFullYear(), today.getMonth() + 1, today.getDate());
            this.year = jalali[0];
            this.month = jalali[1];

            this.$watch('value', v => {
                if (v) {
                    const parts = String(v).split('/');
                    if (parts.length === 3) {
                        this.year = parseInt(parts[0]);
                        this.month = parseInt(parts[1]);
                    }
                }
            });
        },

        open() { this.isOpen = true; },
        close() { this.isOpen = false; },

        prevMonth() {
            this.month--;
            if (this.month < 1) { this.month = 12; this.year--; }
        },

        nextMonth() {
            this.month++;
            if (this.month > 12) { this.month = 1; this.year++; }
        },

        isSelected(day) {
            if (!this.value) return false;
            const parts = String(this.value).split('/');
            if (parts.length !== 3) return false;
            return parseInt(parts[0]) === this.year
                && parseInt(parts[1]) === this.month
                && parseInt(parts[2]) === day;
        },

        pick(day) {
            this.value = this.year + '/' + String(this.month).padStart(2, '0') + '/' + String(day).padStart(2, '0');
            this.close();
        },

        clear() {
            this.value = '';
            this.close();
        },

        today() {
            const now = new Date();
            const j = this.gregorianToJalali(now.getFullYear(), now.getMonth() + 1, now.getDate());
            this.value = j[0] + '/' + String(j[1]).padStart(2, '0') + '/' + String(j[2]).padStart(2, '0');
            this.close();
        },

        gregorianToJalali(gy, gm, gd) {
            const g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];
            let jy = (gy <= 1600) ? 0 : 979;
            gy -= (gy <= 1600) ? 621 : 1600;
            const gy2 = (gm > 2) ? (gy + 1) : gy;
            let days = (365 * gy) + Math.floor((gy2 + 3) / 4) - Math.floor((gy2 + 99) / 100)
                + Math.floor((gy2 + 399) / 400) - 80 + gd + g_d_m[gm - 1];
            jy += 33 * Math.floor(days / 12053); days %= 12053;
            jy += 4 * Math.floor(days / 1461); days %= 1461;
            if (days > 365) { jy += Math.floor((days - 1) / 365); days = (days - 1) % 365; }
            const jm = (days < 186) ? 1 + Math.floor(days / 31) : 7 + Math.floor((days - 186) / 30);
            const jd = 1 + ((days < 186) ? (days % 31) : ((days - 186) % 30));
            return [jy, jm, jd];
        },
    }
}
</script>
@endpush
@endonce
