<?php
namespace App\Livewire\Customers;

use App\Models\Customer;
use Livewire\Attributes\On;
use Livewire\Component;

class ProfileModal extends Component
{
    public bool $show = false;
    public ?Customer $customer = null;
    public array $stats = [];
    public array $orders = [];

    #[On('open-customer-profile')]
    public function open(?string $phone = null, ?int $customerId = null): void
    {
        $customer = null;
        if ($customerId) {
            $customer = Customer::find($customerId);
        } elseif ($phone) {
            $np = preg_replace('/\D/', '', $phone);
            $customer = Customer::where('phone', 'like', "%{$np}%")->first();
        }

        if (!$customer) {
            $this->dispatch('notify', type: 'error', message: 'مشتری پیدا نشد');
            return;
        }

        $this->customer = $customer;
        $orders = $customer->orders()->latest()->get();

        $this->stats = [
            'total' => $orders->count(),
            'sum' => (float) $orders->sum('amount'),
            'insurance' => (float) $orders->sum('insurance'),
            'first' => $orders->last()?->created_at,
            'last' => $orders->first()?->created_at,
        ];

        $this->orders = $orders->take(10)->map(fn($o) => [
            'id' => $o->id,
            'num' => $o->order_number,
            'amount' => (float) $o->amount,
            'status' => $o->status,
            'date' => \App\Support\PersianDate::format($o->created_at, 'Y/m/d'),
            'products' => $o->items->pluck('title')->take(2)->implode('، '),
        ])->toArray();

        $this->show = true;
    }

    public function close(): void { $this->show = false; $this->customer = null; }

    public function viewOrder(int $orderId): void
    {
        $this->close();
        $this->dispatch('open-order-view', orderId: $orderId);
    }

    public function render() { return view('livewire.customers.profile-modal'); }
}
