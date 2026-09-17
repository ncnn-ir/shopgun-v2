<div class="p-4 md:p-6 space-y-4">

    @if (session('success'))
        <div class="alert alert-success text-sm py-2"><span>{{ session('success') }}</span></div>
    @endif

    <div class="flex flex-wrap items-center justify-between gap-3">
        <h1 class="text-xl md:text-2xl font-bold">💎 مدیریت سنگ‌ها</h1>
        <button wire:click="openForm()" class="btn btn-primary btn-sm">➕ سنگ جدید</button>
    </div>

    <div class="bg-base-100 rounded-lg shadow border p-3">
        <input type="text" wire:model.live.debounce.400ms="search"
               placeholder="🔍 جستجوی سنگ..." class="input input-bordered input-sm w-full md:w-80" />
    </div>

    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
        @forelse($stones as $stone)
            <div wire:key="stone-{{ $stone->id }}"
                 class="card bg-base-100 shadow border {{ ! $stone->is_active ? 'opacity-50' : '' }} hover:shadow-lg transition">
                <div class="card-body p-3 items-center text-center relative">

                    <button wire:click="delete({{ $stone->id }})" wire:confirm="حذف شود؟"
                            class="absolute top-1 left-1 btn btn-error btn-xs btn-circle opacity-70 hover:opacity-100 z-10">✕</button>

                    <button wire:click="toggleActive({{ $stone->id }})"
                            class="absolute top-1 right-1 btn btn-xs btn-circle z-10 {{ $stone->is_active ? 'btn-success' : 'btn-ghost' }}">
                        {{ $stone->is_active ? '✓' : '—' }}
                    </button>

                    {{-- تصویر یا آیکون --}}
                    <div class="w-16 h-16 rounded-xl bg-base-200 flex items-center justify-center overflow-hidden">
                        @if($stone->png_path)
                            <img src="{{ asset('storage/' . $stone->png_path) }}"
                                 class="w-full h-full object-contain" alt="{{ $stone->name }}"
                                 onerror="this.replaceWith(document.createTextNode('{{ $stone->icon ?? '💎' }}'))" />
                        @else
                            <span class="text-3xl">{{ $stone->icon ?? '💎' }}</span>
                        @endif
                    </div>

                    <div class="font-bold text-xs mt-2 leading-tight">{{ $stone->name }}</div>
                    @if($stone->en)
                        <div class="text-[10px] text-base-content/50" dir="ltr">{{ $stone->en }}</div>
                    @endif
                    @if($stone->origin)
                        <div class="text-[10px] text-base-content/60 mt-1">{{ $stone->flag }} {{ $stone->origin }}</div>
                    @endif

                    <button wire:click="openForm({{ $stone->id }})" class="btn btn-ghost btn-xs mt-1 w-full">✏️ ویرایش</button>
                </div>
            </div>
        @empty
            <div class="col-span-full text-center py-12 text-base-content/50">
                <div class="text-4xl mb-2">💎</div>
                سنگی نیست
            </div>
        @endforelse
    </div>

    <div>{{ $stones->links() }}</div>

    @if($showForm)
    <div class="fixed inset-0 z-[90] flex items-start justify-center p-4 overflow-y-auto">
        <div class="fixed inset-0 bg-black/60 backdrop-blur-md" wire:click="closeForm"></div>

        <div class="relative bg-base-100 rounded-2xl shadow-2xl w-full max-w-lg my-8 md:my-16 border border-base-300">
            <div class="flex items-center justify-between p-4 border-b border-base-300 bg-gradient-to-l from-primary/10 to-transparent rounded-t-2xl">
                <div class="flex items-center gap-3">
                    <div class="w-9 h-9 rounded-lg bg-gradient-to-br from-cyan-500 to-teal-600 flex items-center justify-center text-white shadow">
                        {{ $editingId ? '✏️' : '💎' }}
                    </div>
                    <h2 class="font-bold text-base">{{ $editingId ? 'ویرایش سنگ' : 'سنگ جدید' }}</h2>
                </div>
                <button wire:click="closeForm" class="btn btn-ghost btn-sm btn-circle">✕</button>
            </div>

            <div class="p-5 space-y-3 max-h-[calc(100vh-14rem)] overflow-y-auto">
                <div class="grid grid-cols-2 gap-3">
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">نام فارسی *</span></label>
                        <input type="text" wire:model="name" class="input input-bordered input-sm w-full" />
                        @error('name') <span class="text-error text-xs">{{ $message }}</span> @enderror
                    </div>
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">نام انگلیسی</span></label>
                        <input type="text" wire:model="en" dir="ltr" class="input input-bordered input-sm w-full" />
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-3">
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">اصالت</span></label>
                        <input type="text" wire:model="origin" class="input input-bordered input-sm w-full" />
                    </div>
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">کشور</span></label>
                        <select wire:model="flag" class="select select-bordered select-sm w-full">
                            @foreach($countries as $k => $v)
                                <option value="{{ $k }}">{{ $v }}</option>
                            @endforeach
                        </select>
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-3">
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">برچسب</span></label>
                        <input type="text" wire:model="balloon" class="input input-bordered input-sm w-full" />
                    </div>
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">آیکون</span></label>
                        <input type="text" wire:model="icon" class="input input-bordered input-sm w-full text-center text-2xl" />
                    </div>
                </div>

                <div class="form-control">
                    <label class="label py-1"><span class="label-text text-xs font-bold">تصویر PNG (اختیاری)</span></label>
                    <input type="file" wire:model="png" accept="image/png,image/*"
                           class="file-input file-input-bordered file-input-sm w-full" />
                    @if($png)
                        <div class="mt-2"><img src="{{ $png->temporaryUrl() }}" class="w-20 h-20 object-contain border rounded" /></div>
                    @endif
                    @error('png') <span class="text-error text-xs">{{ $message }}</span> @enderror
                </div>
            </div>

            <div class="p-4 border-t border-base-300 flex justify-end gap-2 rounded-b-2xl bg-base-200/50">
                <button wire:click="closeForm" class="btn btn-ghost btn-sm">انصراف</button>
                <button wire:click="save" wire:loading.attr="disabled" class="btn btn-primary btn-sm">
                    <span wire:loading.remove wire:target="save">✅ ذخیره</span>
                    <span wire:loading wire:target="save">⏳...</span>
                </button>
            </div>
        </div>
    </div>
    @endif
</div>
