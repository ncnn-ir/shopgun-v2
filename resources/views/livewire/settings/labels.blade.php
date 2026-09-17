<div class="p-4 md:p-6 space-y-4" dir="rtl">

    <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
            <h1 class="text-xl md:text-2xl font-bold">🏷️ ویرایشگر برچسب پستی</h1>
            <p class="text-xs text-base-content/60 mt-1">پیش‌نمایش زنده — تغییرات بلافاصله اعمال می‌شوند</p>
        </div>
        <div class="flex gap-2">
            <button wire:click="resetDefaults" class="btn btn-ghost btn-sm">↺ بازنشانی</button>
            <button wire:click="save" class="btn btn-primary btn-sm">💾 ذخیره</button>
        </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">

        {{-- ستون تنظیمات --}}
        <div class="lg:col-span-1 space-y-3">
            <div class="card bg-base-100 shadow border border-base-300">
                <div class="card-body p-4 space-y-3">
                    <h3 class="font-bold text-sm">📐 ابعاد</h3>
                    <div class="grid grid-cols-2 gap-2">
                        <label class="form-control">
                            <span class="label-text text-[10px] font-bold">عرض (mm)</span>
                            <input type="number" wire:model.live="width" dir="ltr"
                                   class="input input-bordered input-sm" />
                        </label>
                        <label class="form-control">
                            <span class="label-text text-[10px] font-bold">ارتفاع (mm)</span>
                            <input type="number" wire:model.live="height" dir="ltr"
                                   class="input input-bordered input-sm" />
                        </label>
                    </div>
                </div>
            </div>

            <div class="card bg-base-100 shadow border border-base-300">
                <div class="card-body p-4 space-y-3">
                    <h3 class="font-bold text-sm">🔤 اندازه فونت‌ها</h3>
                    @foreach([
                        'customer' => 'نام مشتری',
                        'insurance' => 'بیمه',
                        'address' => 'آدرس',
                        'contactLabel' => 'برچسب تلفن',
                        'contactValue' => 'مقدار تلفن',
                        'meta' => 'اطلاعات پایین',
                        'footer' => 'پاصفحه',
                    ] as $key => $label)
                        <label class="form-control">
                            <div class="flex justify-between">
                                <span class="text-xs">{{ $label }}</span>
                                <span class="font-mono text-xs">{{ $fonts[$key] ?? 0 }}px</span>
                            </div>
                            <input type="range" min="6" max="30" wire:model.live="fonts.{{ $key }}"
                                   class="range range-xs range-primary" />
                        </label>
                    @endforeach
                </div>
            </div>

            <div class="card bg-base-100 shadow border border-base-300">
                <div class="card-body p-4 space-y-2">
                    <h3 class="font-bold text-sm">👁️ نمایش المان‌ها</h3>
                    <label class="flex items-center gap-2 cursor-pointer">
                        <input type="checkbox" wire:model.live="showInsurance" class="checkbox checkbox-primary checkbox-sm" />
                        <span class="text-xs">بیمه</span>
                    </label>
                    <label class="flex items-center gap-2 cursor-pointer">
                        <input type="checkbox" wire:model.live="showPostal" class="checkbox checkbox-primary checkbox-sm" />
                        <span class="text-xs">کدپستی</span>
                    </label>
                    <label class="flex items-center gap-2 cursor-pointer">
                        <input type="checkbox" wire:model.live="showPhone" class="checkbox checkbox-primary checkbox-sm" />
                        <span class="text-xs">تلفن</span>
                    </label>
                </div>
            </div>

            <div class="card bg-base-100 shadow border border-base-300">
                <div class="card-body p-4 space-y-2">
                    <h3 class="font-bold text-sm">🧪 نمونه داده</h3>
                    <input type="text" wire:model.live="sampleName" placeholder="نام"
                           class="input input-bordered input-xs" />
                    <textarea wire:model.live="sampleAddress" rows="2" placeholder="آدرس"
                              class="textarea textarea-bordered textarea-xs"></textarea>
                    <div class="grid grid-cols-2 gap-2">
                        <input type="text" wire:model.live="samplePhone" placeholder="تلفن"
                               class="input input-bordered input-xs font-mono" dir="ltr" />
                        <input type="text" wire:model.live="samplePostal" placeholder="کدپستی"
                               class="input input-bordered input-xs font-mono" dir="ltr" />
                    </div>
                </div>
            </div>
        </div>

        {{-- پیش‌نمایش زنده --}}
        <div class="lg:col-span-2">
            <div class="card bg-base-100 shadow border-2 border-primary/30 sticky top-4">
                <div class="card-body p-4">
                    <h3 class="font-bold text-sm mb-3 flex items-center justify-between">
                        <span>👁️ پیش‌نمایش زنده</span>
                        <span class="badge badge-primary badge-sm font-mono">{{ $width }}×{{ $height }} mm</span>
                    </h3>

                    <div class="bg-base-200 rounded-lg p-4 flex items-center justify-center overflow-auto">
                        <div style="
                            width: {{ $width * 3.78 }}px;
                            height: {{ $height * 3.78 }}px;
                            background: #fff;
                            color: #000;
                            padding: 8px;
                            box-sizing: border-box;
                            border: 2px solid #000;
                            border-radius: 4px;
                            font-family: Vazirmatn, Tahoma, sans-serif;
                            display: flex;
                            flex-direction: column;
                            gap: 4px;
                            overflow: hidden;
                        ">
                            {{-- ردیف ۱: نام + بیمه --}}
                            <div style="display: flex; align-items: center; justify-content: space-between; gap: 8px; border-bottom: 2px solid #000; padding-bottom: 4px;">
                                <div style="font-size: {{ $fonts['customer'] ?? 16 }}px; font-weight: bold; flex: 1; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                                    {{ $sampleName ?: 'نام مشتری' }}
                                </div>
                                @if($showInsurance)
                                    <div style="font-size: {{ $fonts['insurance'] ?? 12 }}px; background: #000; color: #fff; padding: 2px 10px; border-radius: 20px; font-weight: bold; white-space: nowrap;">
                                        بیمه: {{ $sampleInsurance }}
                                    </div>
                                @endif
                            </div>

                            {{-- آدرس --}}
                            <div style="border: 2px solid #000; border-radius: 6px; padding: 6px; font-size: {{ $fonts['address'] ?? 14 }}px; line-height: 1.5; font-weight: 600; flex: 1; overflow: hidden;">
                                {{ $sampleAddress ?: 'آدرس گیرنده' }}
                            </div>

                            {{-- ردیف تلفن --}}
                            @if($showPhone || $showPostal)
                            <div style="display: flex; gap: 6px;">
                                @if($showPhone)
                                    <div style="flex: 1; display: flex; align-items: center; gap: 4px;">
                                        <span style="background: #000; color: #fff; padding: 2px 8px; border-radius: 5px; font-size: {{ $fonts['contactLabel'] ?? 11 }}px; font-weight: bold;">
                                            تلفن
                                        </span>
                                        <span style="flex: 1; border: 2px solid #000; border-radius: 5px; padding: 2px 8px; font-size: {{ $fonts['contactValue'] ?? 16 }}px; font-weight: bold; font-family: monospace; text-align: center;">
                                            {{ $samplePhone }}
                                        </span>
                                    </div>
                                @endif

                                @if($showPostal)
                                    <div style="flex: 1; display: flex; align-items: center; gap: 4px;">
                                        <span style="background: #000; color: #fff; padding: 2px 8px; border-radius: 5px; font-size: {{ $fonts['contactLabel'] ?? 11 }}px; font-weight: bold;">
                                            کدپستی
                                        </span>
                                        <span style="flex: 1; border: 2px solid #000; border-radius: 5px; padding: 2px 8px; font-size: {{ max(10, ($fonts['contactValue'] ?? 16) - 2) }}px; font-weight: bold; font-family: monospace; text-align: center;">
                                            {{ $samplePostal }}
                                        </span>
                                    </div>
                                @endif
                            </div>
                            @endif

                            {{-- پاصفحه --}}
                            <div style="display: flex; justify-content: space-between; font-size: {{ $fonts['meta'] ?? 11 }}px; margin-top: auto;">
                                <span style="background: #000; color: #fff; padding: 2px 10px; border-radius: 10px; font-weight: bold;">
                                    #{{ $sampleOrder }}
                                </span>
                                <span style="background: #000; color: #fff; padding: 2px 10px; border-radius: 10px; font-weight: bold; font-size: {{ $fonts['footer'] ?? 10 }}px;">
                                    جواهری مشاهیر
                                </span>
                            </div>
                        </div>
                    </div>

                    <div class="alert alert-info text-xs mt-3">
                        <span>💡 این پیش‌نمایش با ابعاد واقعی چاپ (mm) مقیاس شده. در چاپگر حرارتی مستقیم تست کن.</span>
                    </div>
                </div>
            </div>
        </div>
    </div>
</div>
