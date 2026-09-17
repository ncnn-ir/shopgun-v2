<?php
namespace App\Livewire\Orders;

use App\Models\Customer;
use App\Models\Order;
use Livewire\Attributes\On;
use Livewire\Component;

class ViewModal extends Component
{
    public bool $show = false;
    public ?Order $order = null;
    public array $customerStats = [];
    public array $timeline = [];

    #[On('open-order-view')]
    public function open(int $orderId): void
    {
        $this->order = Order::with(['customer', 'items', 'channel'])->find($orderId);
        if (!$this->order) return;

        // آمار مشتری
        if ($this->order->customer_id) {
            $customer = Customer::find($this->order->customer_id);
            if ($customer) {
                $orders = $customer->orders()->orderBy('created_at')->get();
                $this->customerStats = [
                    'total' => $orders->count(),
                    'sum' => (float) $orders->sum('amount'),
                    'first' => $orders->first()?->created_at,
                    'last' => $orders->last()?->created_at,
                ];
            }
        }

        $this->buildTimeline();
        $this->show = true;
    }

    protected function buildTimeline(): void
    {
        $stages = [
            ['id' => 'pending', 'label' => 'ثبت سفارش', 'icon' => '📝'],
            ['id' => 'final-check', 'label' => 'چک نهایی', 'icon' => '🔍'],
            ['id' => 'courier', 'label' => 'تحویل مامور', 'icon' => '🚚'],
        ];

        $currentStatus = $this->order->status ?? 'pending';
        $currentIdx = array_search($currentStatus, array_column($stages, 'id'));
        if ($currentIdx === false) $currentIdx = 0;

        // گرفتن تاریخچه از activity log
        $activities = [];
        try {
            $logs = \Spatie\Activitylog\Models\Activity::where('subject_type', Order::class)
                ->where('subject_id', $this->order->id)
                ->where('event', 'updated')
                ->orderBy('created_at')
                ->get();

            foreach ($logs as $log) {
                $changes = $log->properties['attributes'] ?? [];
                if (isset($changes['status'])) {
                    $activities[] = [
                        'status' => $changes['status'],
                        'at' => $log->created_at,
                    ];
                }
            }
        } catch (\Throwable $e) {}

        // اگر activity نیست، از created_at سفارش استفاده کن
        if (empty($activities)) {
            $activities[] = ['status' => 'pending', 'at' => $this->order->created_at];
            if ($currentIdx >= 1) $activities[] = ['status' => 'final-check', 'at' => $this->order->updated_at];
            if ($currentIdx >= 2) $activities[] = ['status' => 'courier', 'at' => $this->order->updated_at];
        }

        $this->timeline = [];
        foreach ($stages as $i => $stage) {
            $state = $i < $currentIdx ? 'done' : ($i === $currentIdx ? 'current' : '');

            // پیدا کردن تاریخ این مرحله از activity
            $at = null;
            foreach ($activities as $a) {
                if ($a['status'] === $stage['id']) {
                    $at = $a['at'];
                    break;
                }
            }

            $this->timeline[] = [
                'label' => $stage['label'],
                'icon' => $stage['icon'],
                'state' => $state,
                'date' => $at ? \App\Support\PersianDate::format($at, 'Y/m/d') : '',
                'time' => $at ? $at->format('H:i') : '',
            ];
        }
    }

    public function close(): void { $this->show = false; $this->order = null; }

    public function cycleStatus(): void
    {
        if (!$this->order) return;
        $statuses = ['pending', 'final-check', 'courier'];
        $cur = array_search($this->order->status, $statuses);
        $next = $statuses[($cur === false ? 0 : ($cur + 1)) % count($statuses)];
        $this->order->update(['status' => $next]);
        $this->order->refresh();
        $this->open($this->order->id);
        $this->dispatch('order-saved');
        $this->dispatch('notify', type: 'success', message: 'وضعیت تغییر کرد');
    }

    public function editOrder(): void
    {
        $id = $this->order->id;
        $this->close();
        $this->dispatch('open-order-form', orderId: $id);
    }

    public function deleteOrder(): void
    {
        $this->order?->delete();
        $this->close();
        $this->dispatch('order-saved');
        $this->dispatch('notify', type: 'success', message: 'حذف شد');
    }

    public function render() { return view('livewire.orders.view-modal'); }
}
