<?php

namespace App\Livewire;

use App\Models\AppNotification;
use Illuminate\Support\Facades\Auth;
use Livewire\Attributes\On;
use Livewire\Component;

class NotificationCenter extends Component
{
    public int $unreadCount = 0;
    public int $lastSeenId = 0;
    public array $newToasts = [];

    public function mount(): void
    {
        $this->lastSeenId = (int) AppNotification::where('user_id', Auth::id())->max('id');
        $this->refreshCount();
    }

    /**
     * چک دورهای برای اعلان‌های جدید
     */
    public function pollNew(): void
    {
        $new = AppNotification::where('user_id', Auth::id())
            ->where('id', '>', $this->lastSeenId)
            ->where('is_read', false)
            ->latest('id')
            ->limit(5)
            ->get();

        foreach ($new as $n) {
            $this->dispatch('sg-toast', [
                'type' => $n->type === 'order_created' ? 'success' : 'info',
                'message' => $n->icon . ' ' . $n->title,
                'url' => $n->url,
            ]);
            $this->lastSeenId = max($this->lastSeenId, $n->id);
        }

        $this->refreshCount();
    }

    public function refreshCount(): void
    {
        $this->unreadCount = AppNotification::where('user_id', Auth::id())
            ->where('is_read', false)
            ->count();
    }

    public function markAsRead(int $id): void
    {
        AppNotification::where('id', $id)->where('user_id', Auth::id())->update(['is_read' => true]);
        $this->refreshCount();
    }

    public function markAllAsRead(): void
    {
        AppNotification::where('user_id', Auth::id())->update(['is_read' => true]);
        $this->refreshCount();
    }

    #[On('notif-open')]
    public function openNotification(int $id): void
    {
        $this->markAsRead($id);
    }

    public function render()
    {
        $notifications = AppNotification::where('user_id', Auth::id())
            ->latest('id')->limit(30)->get();

        return view('livewire.notification-center', compact('notifications'));
    }
}
