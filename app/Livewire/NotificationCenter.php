<?php

namespace App\Livewire;

use App\Models\AppNotification;
use Illuminate\Support\Facades\Auth;
use Livewire\Component;

class NotificationCenter extends Component
{
    public int $unreadCount = 0;

    public function mount(): void { $this->refreshCount(); }

    public function refreshCount(): void
    {
        $this->unreadCount = AppNotification::where('user_id', Auth::id())->where('is_read', false)->count();
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

    public function delete(int $id): void
    {
        AppNotification::where('id', $id)->where('user_id', Auth::id())->delete();
        $this->refreshCount();
    }

    public function clearAll(): void
    {
        AppNotification::where('user_id', Auth::id())->delete();
        $this->refreshCount();
    }

    public function render()
    {
        $notifications = AppNotification::where('user_id', Auth::id())->latest()->limit(20)->get();
        return view('livewire.notification-center', compact('notifications'));
    }
}
