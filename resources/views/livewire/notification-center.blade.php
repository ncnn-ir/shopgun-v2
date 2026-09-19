<div wire:poll.8s="pollNew" style="position:relative" x-data="{ open: false }">
    <button type="button" @click="open = !open"
            style="position:relative;width:38px;height:38px;border-radius:50%;background:rgba(255,255,255,.15);border:1px solid rgba(255,255,255,.2);color:#fff;cursor:pointer;font-size:16px;display:flex;align-items:center;justify-content:center">
        🔔
        @if($unreadCount > 0)
            <span style="position:absolute;top:-4px;right:-4px;background:#ef4444;color:#fff;min-width:18px;height:18px;border-radius:9px;font-size:10px;font-weight:700;display:flex;align-items:center;justify-content:center;padding:0 4px">
                {{ $unreadCount > 99 ? '99+' : \App\Support\PersianNumber::toFa($unreadCount) }}
            </span>
        @endif
    </button>

    <div x-show="open" x-transition.opacity @click.outside="open = false"
         style="position:absolute;top:100%;left:0;margin-top:8px;width:340px;max-width:90vw;background:var(--sg-bg-elevated);border:1px solid var(--sg-border);border-radius:var(--sg-radius);box-shadow:var(--sg-shadow-lg);z-index:200;direction:rtl">

        <div style="padding:12px;border-bottom:1px solid var(--sg-divider);display:flex;justify-content:space-between;align-items:center">
            <span style="font-weight:700;font-size:13px">🔔 اعلان‌ها</span>
            @if($unreadCount > 0)
                <button wire:click="markAllAsRead" style="background:transparent;border:none;color:var(--sg-primary);font-size:11px;font-weight:700;cursor:pointer">✓ خواندن همه</button>
            @endif
        </div>

        <div style="max-height:400px;overflow-y:auto">
            @forelse($notifications as $n)
                <div wire:key="notif-{{ $n->id }}"
                     style="padding:10px 12px;border-bottom:1px solid var(--sg-divider);{{ !$n->is_read ? 'background:rgba(59,130,246,.04)' : '' }}">
                    <div style="display:flex;gap:8px">
                        <div style="font-size:18px">{{ $n->icon }}</div>
                        <div style="flex:1;min-width:0">
                            <div style="display:flex;justify-content:space-between;gap:6px">
                                <div style="font-weight:700;font-size:12px;color:var(--sg-text)">{{ $n->title }}</div>
                                <div style="font-size:10px;color:var(--sg-text-muted);white-space:nowrap">{{ $n->created_at?->diffForHumans() }}</div>
                            </div>
                            <div style="font-size:11px;color:var(--sg-text-secondary);margin-top:2px">{{ $n->message }}</div>
                            @if($n->url)
                                <a href="{{ $n->url }}" wire:click="markAsRead({{ $n->id }})" @click="open = false"
                                   style="display:inline-block;margin-top:6px;padding:4px 10px;background:var(--sg-primary);color:#fff;border-radius:6px;font-size:11px;font-weight:700;text-decoration:none">
                                    مشاهده
                                </a>
                            @endif
                        </div>
                    </div>
                </div>
            @empty
                <div style="padding:30px;text-align:center;color:var(--sg-text-muted);font-size:12px">اعلانی نیست</div>
            @endforelse
        </div>
    </div>
</div>
