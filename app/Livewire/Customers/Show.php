<?php

namespace App\Livewire\Customers;

use App\Models\Customer;
use Livewire\Component;

class Show extends Component
{
    public Customer $customer;

    public function mount(Customer $customer): void
    {
        $this->customer = $customer->load([
            'phones', 'addresses',
            'orders' => fn($q) => $q->latest(),
        ]);
    }

    public function render()
    {
        return view('livewire.customers.show')
            ->layout('components.layouts.app');
    }
}
