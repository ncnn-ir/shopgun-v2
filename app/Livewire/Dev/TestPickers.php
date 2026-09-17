<?php

namespace App\Livewire\Dev;

use Livewire\Component;

class TestPickers extends Component
{
    public ?int $customerId = null;
    public array $customerData = [];
    public array $cart = [];

    protected $listeners = [
        'customer-selected' => 'onCustomerSelected',
        'customer-cleared'  => 'onCustomerCleared',
        'products-updated'  => 'onProductsUpdated',
    ];

    public function onCustomerSelected(int $customerId, array $data): void
    {
        $this->customerId = $customerId;
        $this->customerData = $data;
    }

    public function onCustomerCleared(): void
    {
        $this->customerId = null;
        $this->customerData = [];
    }

    public function onProductsUpdated(array $cart): void
    {
        $this->cart = $cart;
    }

    public function render()
    {
        $total = 0;
        foreach ($this->cart as $it) {
            $total += ((float) ($it['price'] ?? 0)) * ((int) ($it['qty'] ?? 1));
        }

        return view('livewire.dev.test-pickers', compact('total'))
            ->layout('components.layouts.app');
    }
}
