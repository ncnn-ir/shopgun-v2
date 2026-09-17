<div class="p-4 md:p-6 max-w-3xl mx-auto">
    <div class="flex items-center gap-3 mb-6">
        <a href="{{ route('customers.show', $customer) }}" class="btn btn-ghost btn-sm">→</a>
        <h1 class="text-xl md:text-2xl font-bold">✏️ ویرایش مشتری</h1>
    </div>

    <div class="card bg-base-100 shadow">
        <div class="card-body gap-4">

            <div class="form-control">
                <label class="label py-1"><span class="label-text font-bold text-sm">📱 تلفن *</span></label>
                <input type="text" wire:model="phone" dir="ltr" class="input input-bordered w-full font-mono" />
                @error('phone') <span class="text-error text-xs mt-1">{{ $message }}</span> @enderror
            </div>

            <div class="form-control">
                <label class="label py-1"><span class="label-text font-bold text-sm">👤 نام</span></label>
                <input type="text" wire:model="name" class="input input-bordered w-full" />
            </div>

            <div class="form-control">
                <label class="label py-1"><span class="label-text font-bold text-sm">📮 کدپستی</span></label>
                <input type="text" wire:model="postalCode" dir="ltr" class="input input-bordered w-full font-mono" />
            </div>

            <div class="form-control">
                <label class="label py-1"><span class="label-text font-bold text-sm">📍 آدرس</span></label>
                <textarea wire:model="address" class="textarea textarea-bordered w-full" rows="3"></textarea>
            </div>

            <div class="form-control">
                <label class="label py-1"><span class="label-text font-bold text-sm">📝 یادداشت</span></label>
                <textarea wire:model="notes" class="textarea textarea-bordered w-full" rows="2"></textarea>
            </div>

            <div class="flex flex-col-reverse md:flex-row justify-end gap-2 mt-4">
                <a href="{{ route('customers.show', $customer) }}" class="btn btn-ghost w-full md:w-auto">انصراف</a>
                <button wire:click="save" wire:loading.attr="disabled" class="btn btn-primary w-full md:w-auto">
                    <span wire:loading.remove wire:target="save">✅ ذخیره</span>
                    <span wire:loading wire:target="save">⏳...</span>
                </button>
            </div>
        </div>
    </div>
</div>
