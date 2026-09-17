<div class="p-6 max-w-3xl mx-auto">
    <div class="flex items-center gap-3 mb-6">
        <a href="{{ route('orders.show', $order) }}" class="btn btn-ghost btn-sm">→</a>
        <h1 class="text-2xl font-bold">✏️ ویرایش سفارش #{{ $order->order_number }}</h1>
    </div>

    <div class="card bg-base-100 shadow">
        <div class="card-body space-y-4">
            <div class="form-control">
                <label class="label"><span class="label-text font-bold">📱 تلفن *</span></label>
                <input type="text" wire:model="phone" dir="ltr" class="input input-bordered font-mono" />
                @error('phone') <label class="label"><span class="label-text-alt text-error">{{ $message }}</span></label> @enderror
            </div>

            <div class="form-control">
                <label class="label"><span class="label-text font-bold">👤 نام</span></label>
                <input type="text" wire:model="customerName" class="input input-bordered" />
            </div>

            <div class="form-control">
                <label class="label"><span class="label-text font-bold">📮 کدپستی</span></label>
                <input type="text" wire:model="postalCode" dir="ltr" class="input input-bordered font-mono" />
            </div>

            <div class="form-control">
                <label class="label"><span class="label-text font-bold">📍 آدرس</span></label>
                <textarea wire:model="address" class="textarea textarea-bordered" rows="3"></textarea>
            </div>

            <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div class="form-control">
                    <label class="label"><span class="label-text font-bold">💰 بیمه</span></label>
                    <input type="number" wire:model="insurance" dir="ltr" class="input input-bordered" />
                </div>
                <div class="form-control">
                    <label class="label"><span class="label-text font-bold">📊 وضعیت</span></label>
                    <select wire:model="status" class="select select-bordered">
                        <option value="pending">📝 ثبت سفارش</option>
                        <option value="final-check">🔍 چک نهایی</option>
                        <option value="courier">🚚 تحویل مامور</option>
                    </select>
                </div>
                <div class="form-control">
                    <label class="label"><span class="label-text font-bold">🌐 کانال</span></label>
                    <select wire:model="channelId" class="select select-bordered">
                        <option value="">— انتخاب —</option>
                        @foreach($channels as $channel)
                            <option value="{{ $channel->id }}">{{ $channel->icon }} {{ $channel->name }}</option>
                        @endforeach
                    </select>
                </div>
            </div>

            <div class="form-control">
                <label class="label"><span class="label-text font-bold">📝 یادداشت</span></label>
                <textarea wire:model="notes" class="textarea textarea-bordered" rows="2"></textarea>
            </div>

            <div class="card-actions justify-end mt-6">
                <a href="{{ route('orders.show', $order) }}" class="btn btn-ghost">انصراف</a>
                <button wire:click="save" class="btn btn-primary">✅ ذخیره</button>
            </div>
        </div>
    </div>
</div>
