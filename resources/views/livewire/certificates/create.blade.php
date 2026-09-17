<div class="p-4 md:p-6 max-w-3xl mx-auto">
    <div class="flex items-center gap-3 mb-6">
        <a href="{{ route('certificates.index') }}" class="btn btn-ghost btn-sm">→</a>
        <h1 class="text-xl md:text-2xl font-bold">💎 شناسنامه جدید</h1>
    </div>

    {{-- Step indicator --}}
    <ul class="steps steps-horizontal w-full mb-6 text-xs">
        <li class="step {{ $step >= 1 ? 'step-primary' : '' }}">سنگ/فلز</li>
        <li class="step {{ $step >= 2 ? 'step-primary' : '' }}">مشخصات</li>
        <li class="step {{ $step >= 3 ? 'step-primary' : '' }}">تصویر</li>
    </ul>

    <div class="card bg-base-100 shadow">
        <div class="card-body gap-5">

            {{-- ========== STEP 1 ========== --}}
            @if($step === 1)
                <div>
                    <h3 class="font-bold text-sm mb-3 text-base-content/70">💎 انتخاب سنگ</h3>
                    <div class="grid grid-cols-3 md:grid-cols-4 gap-2">
                        @foreach($stoneOptions as $i => $s)
                            <button type="button"
                                    wire:click="selectStone({{ $i }})"
                                    class="border-2 rounded-lg p-2 text-center transition
                                        {{ $stoneName === $s['name'] ? 'border-primary bg-primary/10' : 'border-base-300 hover:border-primary/50' }}">
                                <div class="text-2xl mb-1">{{ $s['icon'] }}</div>
                                <div class="text-[11px] font-bold leading-tight">{{ $s['name'] }}</div>
                            </button>
                        @endforeach
                    </div>
                </div>

                <div class="divider my-1"></div>

                <div>
                    <h3 class="font-bold text-sm mb-3 text-base-content/70">⚙️ انتخاب فلز</h3>
                    <div class="grid grid-cols-2 md:grid-cols-4 gap-2">
                        @foreach($metalOptions as $i => $m)
                            <button type="button"
                                    wire:click="selectMetal({{ $i }})"
                                    class="border-2 rounded-lg p-2 text-center text-xs font-bold transition
                                        {{ $metal === $m['name'] ? 'border-primary bg-primary/10' : 'border-base-300 hover:border-primary/50' }}">
                                {{ $m['name'] }}
                            </button>
                        @endforeach
                    </div>
                </div>
            @endif

            {{-- ========== STEP 2 ========== --}}
            @if($step === 2)
                <div class="alert alert-info py-2 text-xs">
                    <span>💎 <strong>{{ $stoneName }}</strong> — ⚙️ <strong>{{ $metal }}</strong></span>
                </div>

                <div class="grid grid-cols-2 md:grid-cols-5 gap-3">
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">طول (mm)</span></label>
                        <input type="number" wire:model="length" step="0.01" dir="ltr"
                               class="input input-bordered input-sm w-full text-center" />
                        @error('length') <span class="text-error text-[10px]">{{ $message }}</span> @enderror
                    </div>
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">عرض (mm)</span></label>
                        <input type="number" wire:model="width" step="0.01" dir="ltr"
                               class="input input-bordered input-sm w-full text-center" />
                        @error('width') <span class="text-error text-[10px]">{{ $message }}</span> @enderror
                    </div>
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">وزن (gr)</span></label>
                        <input type="number" wire:model="weight" step="0.001" dir="ltr"
                               class="input input-bordered input-sm w-full text-center" />
                        @error('weight') <span class="text-error text-[10px]">{{ $message }}</span> @enderror
                    </div>
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">عیار</span></label>
                        <input type="text" value="{{ $metalCarat }}" readonly
                               class="input input-bordered input-sm w-full text-center bg-base-200" />
                    </div>
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">برلیان</span></label>
                        <input type="number" wire:model="brilliant" dir="ltr"
                               class="input input-bordered input-sm w-full text-center" />
                    </div>
                </div>
            @endif

            {{-- ========== STEP 3 ========== --}}
            @if($step === 3)
                <div class="alert alert-info py-2 text-xs">
                    <span>💎 {{ $stoneName }} — ⚙️ {{ $metal }} — 📐 {{ $length }}×{{ $width }} — ⚖️ {{ $weight }}g</span>
                </div>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">👤 مشتری (اختیاری)</span></label>
                        <select wire:model="customerId" class="select select-bordered select-sm w-full">
                            <option value="">— بدون مشتری —</option>
                            @foreach($customers as $c)
                                <option value="{{ $c->id }}">{{ $c->name }} — {{ $c->phone }}</option>
                            @endforeach
                        </select>
                    </div>
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">📦 سفارش (اختیاری)</span></label>
                        <select wire:model="orderId" class="select select-bordered select-sm w-full">
                            <option value="">— بدون سفارش —</option>
                            @foreach($orders as $o)
                                <option value="{{ $o->id }}">#{{ $o->order_number }} — {{ $o->customer?->name }}</option>
                            @endforeach
                        </select>
                    </div>
                </div>

                <div class="form-control">
                    <label class="label py-1"><span class="label-text text-xs font-bold">📸 تصویر محصول</span></label>
                    <input type="file" wire:model="image" accept="image/*"
                           class="file-input file-input-bordered file-input-sm w-full" />
                    @if($image)
                        <div class="mt-2">
                            <img src="{{ $image->temporaryUrl() }}" class="w-24 h-24 object-contain border rounded" />
                        </div>
                    @endif
                    @error('image') <span class="text-error text-[10px]">{{ $message }}</span> @enderror
                </div>
            @endif

            {{-- دکمه‌ها --}}
            <div class="flex justify-between gap-2 mt-4 pt-3 border-t">
                <div>
                    @if($step > 1)
                        <button wire:click="prevStep" class="btn btn-ghost btn-sm">→ قبلی</button>
                    @endif
                </div>
                <div class="flex gap-2">
                    <a href="{{ route('certificates.index') }}" class="btn btn-ghost btn-sm">انصراف</a>
                    @if($step < 3)
                        <button wire:click="nextStep" class="btn btn-primary btn-sm">بعدی ←</button>
                    @else
                        <button wire:click="save" wire:loading.attr="disabled" class="btn btn-success btn-sm">
                            <span wire:loading.remove wire:target="save">✅ صدور شناسنامه</span>
                            <span wire:loading wire:target="save">⏳...</span>
                        </button>
                    @endif
                </div>
            </div>
        </div>
    </div>
</div>
