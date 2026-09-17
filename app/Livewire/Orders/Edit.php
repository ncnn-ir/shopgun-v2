<?php

namespace App\Livewire\Orders;

use App\Models\Channel;
use App\Models\Order;
use Livewire\Component;

class Edit extends Component
{
    public Order $order;
    public string $phone = '';
    public string $customerName = '';
    public string $postalCode = '';
    public string $address = '';
    public string $insurance = '0';
    public string $status = 'pending';
    public ?int $channelId = null;
    public string $notes = '';

    public function mount(Order $order): void
    {
        $this->order        = $order;
        $this->phone        = $order->phone ?? '';
        $this->customerName = $order->customer?->name ?? '';
        $this->postalCode   = $order->postal_code ?? '';
        $this->address      = $order->address ?? '';
        $this->insurance    = (string) ($order->insurance ?? 0);
        $this->status       = $order->status ?? 'pending';
        $this->channelId    = $order->channel_id;
        $this->notes        = $order->notes ?? '';
    }

    public function save()
    {
        $this->validate([
            'phone'        => 'required|min:10',
            'customerName' => 'nullable|string|max:255',
            'postalCode'   => 'nullable|string|max:20',
            'address'      => 'nullable|string',
            'insurance'    => 'nullable|numeric',
            'status'       => 'required|in:pending,final-check,courier',
            'channelId'    => 'nullable|exists:channels,id',
        ]);

        if ($this->order->customer) {
            $this->order->customer->update([
                'name'        => $this->customerName ?: $this->order->customer->name,
                'postal_code' => $this->postalCode,
                'address'     => $this->address,
            ]);
        }

        $this->order->update([
            'phone'       => $this->phone,
            'postal_code' => $this->postalCode,
            'address'     => $this->address,
            'insurance'   => (float) ($this->insurance ?: 0),
            'status'      => $this->status,
            'channel_id'  => $this->channelId,
            'notes'       => $this->notes,
        ]);

        session()->flash('success', 'ویرایش شد.');
        return redirect()->route('orders.show', $this->order);
    }

    public function render()
    {
        return view('livewire.orders.edit', [
            'channels' => Channel::where('is_active', true)->orderBy('sort_order')->get(),
        ])->layout('components.layouts.app');
    }
}
