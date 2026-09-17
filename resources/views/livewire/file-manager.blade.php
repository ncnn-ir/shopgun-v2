<div class="p-4 md:p-6 space-y-4" dir="rtl">

    <div class="flex flex-wrap items-center justify-between gap-3">
        <h1 class="text-xl md:text-2xl font-bold">📁 مدیریت فایل‌ها</h1>
        <div class="flex gap-2">
            <input type="text" wire:model.live.debounce.400ms="search"
                   placeholder="🔍 جستجو..."
                   class="input input-bordered input-sm w-40 md:w-56" />
            <button wire:click="refresh" class="btn btn-outline btn-sm">🔄</button>
        </div>
    </div>

    <div class="bg-base-100 rounded-lg shadow border border-base-300 p-4">
        <label class="label py-1">
            <span class="label-text font-bold text-sm">📤 آپلود فایل جدید (max 20 MB)</span>
        </label>
        <input type="file" wire:model="upload"
               class="file-input file-input-bordered w-full" />
        <div wire:loading wire:target="upload" class="text-xs text-info mt-2">
            ⏳ در حال آپلود...
        </div>
        @error('upload') <span class="text-error text-xs">{{ $message }}</span> @enderror
    </div>

    <div class="bg-base-100 rounded-lg shadow border border-base-300 overflow-hidden">
        <div class="p-3 border-b border-base-300 bg-base-200/50 flex items-center justify-between">
            <span class="font-bold text-sm">
                📂 فایل‌ها ({{ \App\Support\PersianNumber::toFa(count($files)) }})
            </span>
        </div>

        <div class="p-3 grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
            @forelse($files as $f)
                <div class="card bg-base-100 border border-base-300 hover:shadow-lg transition"
                     wire:key="file-{{ md5($f['path']) }}">
                    <div class="aspect-square bg-base-200 rounded-t-lg flex items-center justify-center overflow-hidden">
                        @if($f['is_image'])
                            <img src="{{ $f['url'] }}" alt="" class="w-full h-full object-cover" loading="lazy">
                        @else
                            <span class="text-4xl">
                                @if(preg_match('/\.pdf$/i', $f['name'])) 📄
                                @elseif(preg_match('/\.(zip|rar|7z)$/i', $f['name'])) 📦
                                @elseif(preg_match('/\.(mp4|avi|mov)$/i', $f['name'])) 🎬
                                @elseif(preg_match('/\.(mp3|wav)$/i', $f['name'])) 🎵
                                @else 📎
                                @endif
                            </span>
                        @endif
                    </div>
                    <div class="p-2">
                        <div class="text-[10px] truncate font-bold" title="{{ $f['name'] }}">
                            {{ $f['name'] }}
                        </div>
                        <div class="text-[10px] text-base-content/50">
                            {{ number_format($f['size'] / 1024, 1) }} KB
                        </div>
                        <div class="flex gap-1 mt-1">
                            <a href="{{ $f['url'] }}" target="_blank"
                               class="btn btn-ghost btn-xs flex-1" title="دانلود">⬇️</a>
                            <button wire:click="delete('{{ $f['path'] }}')"
                                    wire:confirm="حذف شود؟"
                                    class="btn btn-ghost btn-xs text-error" title="حذف">🗑️</button>
                        </div>
                    </div>
                </div>
            @empty
                <div class="col-span-full text-center py-12 text-base-content/50">
                    <div class="text-5xl mb-3">📁</div>
                    <div class="text-sm">فایلی نیست</div>
                    <div class="text-xs mt-1 opacity-70">یک فایل آپلود کن تا اینجا نمایش داده شود</div>
                </div>
            @endforelse
        </div>
    </div>

    <div class="alert alert-info text-xs">
        <span>💡 فایل‌ها در <code>storage/app/public/uploads/</code> ذخیره می‌شوند.</span>
    </div>
</div>
