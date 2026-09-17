<div class="p-4 md:p-6 space-y-4">

    @if (session('success'))
        <div class="alert alert-success text-sm py-2"><span>{{ session('success') }}</span></div>
    @endif

    <div class="flex flex-wrap items-center justify-between gap-3">
        <h1 class="text-xl md:text-2xl font-bold">⚙️ مدیریت فلزات</h1>
        <button wire:click="openForm()" class="btn btn-primary btn-sm">➕ فلز جدید</button>
    </div>

    <div class="bg-base-100 rounded-lg shadow border p-3">
        <input type="text" wire:model.live.debounce.400ms="search"
               placeholder="🔍 جستجو..." class="input input-bordered input-sm w-full md:w-80" />
    </div>

    <div class="bg-base-100 rounded-lg shadow border overflow-hidden">
        <div class="pro-table-wrap">
            <table class="pro-table">
                <thead>
                    <tr>
                        <th>آیکون</th>
                        <th>نام</th>
                        <th>English</th>
                        <th>عیار</th>
                        <th>وضعیت</th>
                        <th>عملیات</th>
                    </tr>
                </thead>
                <tbody>
                    @forelse($metals as $m)
                        <tr wire:key="metal-{{ $m->id }}" class="{{ ! $m->is_active ? 'opacity-50' : '' }}">
                            <td class="text-2xl">{{ $m->icon }}</td>
                            <td class="font-bold">{{ $m->name }}</td>
                            <td dir="ltr">{{ $m->en }}</td>
                            <td class="font-mono">{{ $m->carat }}</td>
                            <td>
                                <button wire:click="toggleActive({{ $m->id }})"
                                        class="badge badge-{{ $m->is_active ? 'success' : 'ghost' }} badge-sm cursor-pointer">
                                    {{ $m->is_active ? '✓ فعال' : 'غیرفعال' }}
                                </button>
                            </td>
                            <td>
                                <div class="flex gap-1">
                                    <button wire:click="openForm({{ $m->id }})" class="btn btn-ghost btn-xs">✏️</button>
                                    <button wire:click="delete({{ $m->id }})" wire:confirm="حذف شود؟"
                                            class="btn btn-ghost btn-xs text-error">🗑️</button>
                                </div>
                            </td>
                        </tr>
                    @empty
                        <tr><td colspan="6" class="text-center py-8 text-base-content/50">فلزی نیست</td></tr>
                    @endforelse
                </tbody>
            </table>
        </div>
    </div>

    <div>{{ $metals->links() }}</div>

    @if($showForm)
    <div class="fixed inset-0 z-[90] flex items-start justify-center p-4 overflow-y-auto">
        <div class="fixed inset-0 bg-black/60 backdrop-blur-md" wire:click="closeForm"></div>

        <div class="relative bg-base-100 rounded-2xl shadow-2xl w-full max-w-md my-8 md:my-16 border border-base-300">
            <div class="flex items-center justify-between p-4 border-b border-base-300 bg-gradient-to-l from-primary/10 to-transparent rounded-t-2xl">
                <div class="flex items-center gap-3">
                    <div class="w-9 h-9 rounded-lg bg-gradient-to-br from-cyan-500 to-teal-600 flex items-center justify-center text-white shadow">
                        {{ $editingId ? '✏️' : '⚙️' }}
                    </div>
                    <h2 class="font-bold text-base">{{ $editingId ? 'ویرایش فلز' : 'فلز جدید' }}</h2>
                </div>
                <button wire:click="closeForm" class="btn btn-ghost btn-sm btn-circle">✕</button>
            </div>

            <div class="p-5 space-y-3">
                <div class="form-control">
                    <label class="label py-1"><span class="label-text text-xs font-bold">نام *</span></label>
                    <input type="text" wire:model="name" class="input input-bordered input-sm w-full" />
                    @error('name') <span class="text-error text-xs">{{ $message }}</span> @enderror
                </div>
                <div class="form-control">
                    <label class="label py-1"><span class="label-text text-xs font-bold">English</span></label>
                    <input type="text" wire:model="en" dir="ltr" class="input input-bordered input-sm w-full" />
                </div>
                <div class="grid grid-cols-2 gap-3">
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">عیار</span></label>
                        <input type="text" wire:model="carat" dir="ltr" class="input input-bordered input-sm w-full font-mono" />
                    </div>
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">آیکون</span></label>
                        <input type="text" wire:model="icon" class="input input-bordered input-sm w-full text-center text-2xl" />
                    </div>
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
