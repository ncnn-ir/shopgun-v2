<div class="p-4 md:p-6 space-y-4" dir="rtl">

    <div class="flex flex-wrap items-center justify-between gap-3">
        <div>
            <h1 class="text-xl md:text-2xl font-bold">🔐 نقش‌ها و مجوزها</h1>
            <p class="text-xs text-base-content/60 mt-1">
                {{ \App\Support\PersianNumber::toFa(count($roles)) }} نقش · {{ \App\Support\PersianNumber::toFa(count($permissions)) }} مجوز
            </p>
        </div>
        <button wire:click="saveAll" class="btn btn-primary btn-sm">💾 ذخیره همه</button>
    </div>

    <div class="bg-base-100 rounded-lg shadow border overflow-hidden">
        <div class="pro-table-wrap">
            <table class="pro-table">
                <thead>
                    <tr>
                        <th style="min-width:200px">مجوز ↓ / نقش →</th>
                        @foreach($roles as $role)
                            <th class="text-center">{{ $role }}</th>
                        @endforeach
                    </tr>
                </thead>
                <tbody>
                    @foreach($permissions as $perm)
                        <tr wire:key="perm-{{ $perm }}">
                            <td class="font-mono text-xs">{{ $perm }}</td>
                            @foreach($roles as $role)
                                <td class="text-center">
                                    <input type="checkbox"
                                           wire:click="toggle('{{ $role }}', '{{ $perm }}')"
                                           {{ ($matrix[$role][$perm] ?? false) ? 'checked' : '' }}
                                           class="checkbox checkbox-xs checkbox-primary">
                                </td>
                            @endforeach
                        </tr>
                    @endforeach
                </tbody>
            </table>
        </div>
    </div>

    <div class="alert alert-info text-xs">
        <span>💡 هر تغییر بلافاصله اعمال و در کش ذخیره می‌شود.</span>
    </div>
</div>
