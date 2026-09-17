<div class="p-4 md:p-6 space-y-4">
    <div class="flex flex-wrap items-center justify-between gap-3">
        <h1 class="text-xl md:text-2xl font-bold">📜 لاگ فعالیت‌ها</h1>
        <div class="flex flex-wrap gap-2">
            <input type="text" wire:model.live.debounce.400ms="search" placeholder="🔍 جستجو..."
                   class="input input-bordered input-sm w-52" />
            <select wire:model.live="logNameFilter" class="select select-bordered select-sm">
                <option value="">همه لاگ‌ها</option>
                @foreach($logNames as $name)
                    <option value="{{ $name }}">{{ $name }}</option>
                @endforeach
            </select>
        </div>
    </div>

    <div class="bg-base-100 rounded-lg shadow border overflow-hidden">
        <div class="pro-table-wrap">
            <table class="pro-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>تاریخ</th>
                        <th>کاربر</th>
                        <th>لاگ</th>
                        <th>رویداد</th>
                        <th>توضیح</th>
                    </tr>
                </thead>
                <tbody>
                    @forelse($activities as $a)
                        <tr>
                            <td class="text-xs">{{ $a->id }}</td>
                            <td class="text-xs whitespace-nowrap">{{ $a->created_at?->format('Y/m/d H:i:s') }}</td>
                            <td class="text-xs">{{ $a->causer?->name ?? 'سیستم' }}</td>
                            <td><span class="badge badge-outline badge-sm">{{ $a->log_name }}</span></td>
                            <td><span class="badge badge-primary badge-sm">{{ $a->event }}</span></td>
                            <td class="text-xs">{{ $a->description }}</td>
                        </tr>
                    @empty
                        <tr><td colspan="6" class="text-center py-8 text-base-content/50">لاگی نیست</td></tr>
                    @endforelse
                </tbody>
            </table>
        </div>
    </div>

    <div>{{ $activities->links() }}</div>
</div>
