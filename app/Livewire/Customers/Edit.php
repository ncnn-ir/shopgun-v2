<?php

namespace App\Livewire\Customers;

use App\Models\Customer;
use Livewire\Component;

class Edit extends Component
{
    public Customer $customer;
    public string $name = '';
    public string $phone = '';
    public string $postalCode = '';
    public string $address = '';
    public string $notes = '';

    public function mount(Customer $customer): void
    {
        $this->customer   = $customer;
        $this->name       = $customer->name ?? '';
        $this->phone      = $customer->phone ?? '';
        $this->postalCode = $customer->postal_code ?? '';
        $this->address    = $customer->address ?? '';
        $this->notes      = $customer->notes ?? '';
    }

    public function save()
    {
        $this->validate([
            'phone' => 'required|min:10|unique:customers,phone,' . $this->customer->id,
            'name'  => 'nullable|string|max:255',
        ], ['phone.unique' => 'این شماره قبلاً ثبت شده.']);

        $this->customer->update([
            'name'        => $this->name ?: 'بدون نام',
            'phone'       => $this->phone,
            'postal_code' => $this->postalCode,
            'address'     => $this->address,
            'notes'       => $this->notes,
        ]);

        session()->flash('success', 'ویرایش شد.');
        return redirect()->route('customers.show', $this->customer);
    }

    public function render()
    {
        return view('livewire.customers.edit')->layout('components.layouts.app');
    }
}
