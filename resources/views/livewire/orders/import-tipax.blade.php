<div class="p-4 md:p-6 max-w-5xl mx-auto">

    <div class="flex items-center gap-3 mb-6">
        <a href="{{ route('orders.index') }}" class="btn btn-ghost btn-sm">→</a>
        <h1 class="text-xl md:text-2xl font-bold">📮 ایمپورت مرسولات تیپاکس</h1>
    </div>

    @if (session('error'))
        <div class="alert alert-error mb-4 text-sm"><span>{{ session('error') }}</span></div>
    @endif

    @if($result)
        <div class="alert alert-success mb-4">
            <div class="text-sm space-y-1">
                <div>✅ تطبیق: <strong>{{ $result['matched'] }}</strong></div>
                <div>🔁 بروزرسانی: <strong>{{ $result['updated'] }}</strong></div>
                <div>✨ جدید: <strong>{{ $result['created'] }}</strong></div>
                <div>⚠️ بدون تطبیق: <strong>{{ $result['unmatched'] }}</strong></div>
                @if($result['errors'])
                    <div>❌ خطا: <strong>{{ $result['errors'] }}</strong></div>
                @endif
            </div>
        </div>
        <div class="flex gap-2 mb-4">
            <a href="{{ route('orders.index') }}" class="btn btn-primary btn-sm">مشاهده سفارشات</a>
            <button wire:click="reset_" class="btn btn-ghost btn-sm">ایمپورت جدید</button>
        </div>
    @endif

    @if(! $result)
        <div class="card bg-base-100 shadow">
            <div class="card-body gap-4">

                <div class="form-control">
                    <label class="label py-1">
                        <span class="label-text font-bold text-sm">📁 فایل CSV / TSV تیپاکس</span>
                    </label>
                    <input type="file" wire:model="file" accept=".csv,.tsv,.txt"
                           class="file-input file-input-bordered file-input-sm w-full" />
                </div>

                <div wire:loading wire:target="file" class="text-xs text-info">⏳ در حال بارگذاری...</div>

                @if(! empty($headers))
                    <div class="divider my-1">نگاشت ستون‌ها</div>

                    <div class="overflow-x-auto">
                        <table class="table table-sm table-zebra">
                            <thead>
                                <tr>
                                    <th>ستون فایل</th>
                                    <th>نمونه</th>
                                    <th>فیلد مقصد</th>
                                </tr>
                            </thead>
                            <tbody>
                                @foreach($headers as $i => $h)
                                    <tr>
                                        <td class="font-bold text-xs">{{ $h }}</td>
                                        <td class="text-xs text-base-content/60">{{ $rows[0][$i] ?? '—' }}</td>
                                        <td>
                                            <select wire:model="mapping.{{ $i }}" class="select select-bordered select-xs w-full">
                                                @foreach($fields as $k => $l)
                                                    <option value="{{ $k }}">{{ $l }}</option>
                                                @endforeach
                                            </select>
                                        </td>
                                    </tr>
                                @endforeach
                            </tbody>
                        </table>
                    </div>

                    <div class="alert alert-info text-xs py-2">
                        💡 {{ count($rows) }} ردیف آماده ایمپورت — تطبیق با <strong>شماره سفارش</strong> یا <strong>تلفن</strong> انجام می‌شود
                    </div>

                    <div class="card-actions justify-end">
                        <button wire:click="import" wire:loading.attr="disabled" class="btn btn-primary btn-sm">
                            <span wire:loading.remove wire:target="import">✅ ایمپورت</span>
                            <span wire:loading wire:target="import">⏳...</span>
                        </button>
                    </div>
                @endif
            </div>
        </div>
    @endif
</div>
