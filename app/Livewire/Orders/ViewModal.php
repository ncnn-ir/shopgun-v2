<?php
namespace App\Livewire\Orders;

use App\Models\Order;
use Livewire\Component;
use Livewire\Attributes\On;

class ViewModal extends Component
{
    public bool $open = false;
    public ?int $orderId = null;
    public ?array $order = null;

    #[On('open-order-view')]
    public function openView($orderId = null): void
    {
        if (!$orderId) return;
        $this->orderId = (int) $orderId;
        $o = Order::with(['customer', 'items'])->find($this->orderId);
        if (!$o) return;
        $this->order = $this->buildData($o);
        $this->open = true;
    }

    public function close(): void
    {
        $this->open = false;
        $this->orderId = null;
        $this->order = null;
    }

    public function changeStatus(string $newStatus): void
    {
        if (!$this->orderId) return;
        $o = Order::find($this->orderId);
        if (!$o) return;
        $o->update(['status' => $newStatus]);
        $this->order = $this->buildData($o->fresh(['customer', 'items']));
        $this->dispatch('$refresh');
    }

    protected function buildData(Order $o): array
    {
        // محاسبه مجموع
        $itemsTotal = 0;
        $itemsList = [];
        foreach ($o->items as $item) {
            $line = ($item->price ?? 0) * ($item->quantity ?? 1);
            $itemsTotal += $line;
            $itemsList[] = [
                'title' => $item->title ?? $item->name ?? '—',
                'sku'   => $item->sku ?? null,
                'qty'   => $item->quantity ?? 1,
                'price' => (float) ($item->price ?? 0),
                'line'  => (float) $line,
            ];
        }

        // تایم‌لاین
        $timeline = [];
        if ($o->created_at) {
            $timeline[] = [
                'label' => 'ثبت سفارش',
                'icon'  => '📝',
                'date'  => $o->created_at,
                'state' => 'done',
            ];
        }
        if ($o->paid_at || $o->status === 'processing' || $o->status === 'completed') {
            $timeline[] = [
                'label' => 'پرداخت',
                'icon'  => '💳',
                'date'  => $o->paid_at ?? $o->created_at,
                'state' => 'done',
            ];
        }
        if ($o->supply_found_at) {
            $timeline[] = [
                'label' => 'پیدا شد',
                'icon'  => '📦',
                'date'  => $o->supply_found_at,
                'state' => 'done',
            ];
        }
        if ($o->delivered_to_shipping_at) {
            $timeline[] = [
                'label' => 'تحویل ارسال',
                'icon'  => '🚚',
                'date'  => $o->delivered_to_shipping_at,
                'state' => 'done',
            ];
        }
        if ($o->shipped_at) {
            $timeline[] = [
                'label' => 'ارسال',
                'icon'  => '✈️',
                'date'  => $o->shipped_at,
                'state' => 'done',
            ];
        }
        if ($o->delivered_at || $o->status === 'completed') {
            $timeline[] = [
                'label' => 'تحویل مشتری',
                'icon'  => '🏠',
                'date'  => $o->delivered_at ?? $o->updated_at,
                'state' => 'done',
            ];
        }

        // وضعیت بعدی (current)
        $nextState = match ($o->status) {
            'pending'     => 'پرداخت',
            'final-check' => 'چک نهایی',
            'courier'     => 'تحویل مامور',
            'completed'   => null,
            default       => null,
        };

        // وضعیت برچسب
        $statusMap = [
            'pending'     => ['📝', 'ثبت سفارش',      '#f59e0b', '#fef3c7'],
            'final-check' => ['🔍', 'چک نهایی',       '#3b82f6', '#dbeafe'],
            'courier'     => ['🚚', 'تحویل مامور',    '#10b981', '#d1fae5'],
            'completed'   => ['✅', 'تکمیل شده',      '#059669', '#d1fae5'],
            'cancelled'   => ['❌', 'لغو شده',        '#dc2626', '#fee2e2'],
            'processing'  => ['🔄', 'در حال انجام',   '#6366f1', '#eef2ff'],
        ];
        $st = $statusMap[$o->status ?? 'pending'] ?? $statusMap['pending'];

        return [
            'id'           => $o->id,
            'number'       => $o->order_number ?? $o->id,
            'status'       => $o->status,
            'status_icon'  => $st[0],
            'status_label' => $st[1],
            'status_color' => $st[2],
            'status_bg'    => $st[3],
            'amount'       => (float) ($o->amount ?? 0),
            'insurance'    => (float) ($o->insurance ?? 0),
            'created'      => $o->created_at,
            'updated'      => $o->updated_at,
            'customer' => [
                'name'  => trim(($o->customer->first_name ?? '') . ' ' . ($o->customer->last_name ?? '')) ?: 'مهمان',
                'phone' => $o->phone ?? $o->customer->phone ?? '',
                'email' => $o->customer->email ?? '',
            ],
            'address'      => $o->address ?? '',
            'postal'       => $o->postal_code ?? '',
            'channel'      => $o->sales_channel,
            'note'         => $o->notes ?? '',
            'customer_note'=> $o->customer_note ?? '',
            'tracking'     => $o->tracking_code ?? '',
            'carrier'      => $o->carrier ?? '',
            'items'        => $itemsList,
            'items_total'  => $itemsTotal,
            'timeline'     => $timeline,
            'next_state'   => $nextState,
        ];
    }

    public function render()
    {
        return view('livewire.orders.view-modal');
    }
}
