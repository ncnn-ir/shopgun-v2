<div wire:poll.15s="refreshCount" class="dropdown dropdown-end">
    <div tabindex="0" role="button" class="btn btn-ghost btn-sm">
        <div class="indicator">
            🔔
            @if($unreadCount > 0)
                <span class="badge badge-error badge-xs indicator-item">{{ $unreadCount > 99 ? '99+' : $unreadCount }}</span>
            @endif
        </div>
    </div>
    <div tabindex="0" class="dropdown-content z-[100] card card-compact w-80 bg-base-100 shadow-2xl border border-base-300">
        <div class="card-body p-0">
            <div class="flex items-center justify-between p-3 border-b border-base-300">
                <h3 class="font-bold text-sm">🔔 اعلان‌ها @if($unreadCount > 0)<span class="badge badge-error badge-sm">{{ $unreadCount }}</span>@endif</h3>
                @if($unreadCount > 0)
                    <button wire:click="markAllAsRead" class="btn btn-ghost btn-xs">✓ خواندن همه</button>
                @endif
            </div>
            <div class="max-h-96 overflow-y-auto">
                @forelse($notifications as $notif)
                    <div wire:key="notif-{{ $notif->id }}" class="p-3 border-b border-base-200 hover:bg-base-200 {{ !$notif->is_read ? 'bg-primary/5' : '' }}">
                        <div class="flex gap-3">
                            <div class="text-2xl">{{ $notif->icon }}</div>
                            <div class="flex-1">
                                <div class="flex justify-between items-start gap-2">
                                    <div class="font-bold text-sm">{{ $notif->title }}</div>
                                    <div class="text-[10px] text-base-content/50">{{ $notif->created_at->diffForHumans() }}</div>
                                </div>
                                <div class="text-xs text-base-content/70 mt-1">{{ $notif->message }}</div>
                                <div class="flex gap-2 mt-2">
                                    @if($notif->url)
                                        <a href="{{ $notif->url }}" wire:click="markAsRead({{ $notif->id }})" class="btn btn-primary btn-xs">مشاهده</a>
                                    @endif
                                    <button wire:click="delete({{ $notif->id }})" class="btn btn-ghost btn-xs text-error mr-auto">🗑️</button>
                                </div>
                            </div>
                        </div>
                    </div>
                @empty
                    <div class="text-center py-8 text-base-content/50 text-sm">اعلانی نیست</div>
                @endforelse
            </div>
            @if($notifications->isNotEmpty())
                <div class="p-3 border-t border-base-300">
                    <button wire:click="clearAll" class="btn btn-ghost btn-sm w-full">🗑️ پاک کردن همه</button>
                </div>
            @endif
        </div>
    </div>
</div>
