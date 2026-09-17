<?php

namespace App\Livewire\Customers;

use App\Models\Customer;
use Livewire\Component;

class Create extends Component
{
    public string $name = '';
    public string $phone = '';
    public string $postalCode = '';
    public string $address = '';
    public string $notes = '';

    protected function normalizePhone(string $phone): string
    {
        $digits = preg_replace('/\D/', '', $phone);
        if (str_starts_with($digits, '0098')) $digits = substr($digits, 4);
        elseif (str_starts_with($digits, '98') && strlen($digits) > 10) $digits = substr($digits, 2);
        if (str_starts_with($digits, '0') && strlen($digits) > 10) $digits = substr($digits, 1);
        return $digits;
    }

    public function save()
    {
        $this->validate([
            'phone' => 'required|min:10|unique:customers,phone',
            'name'  => 'nullable|string|max:255',
        ], ['phone.unique' => 'این شماره قبلاً ثبت شده.']);

        Customer::create([
            'name'        => $this->name ?: 'بدون نام',
            'phone'       => $this->normalizePhone($this->phone),
            'postal_code' => $this->postalCode,
            'address'     => $this->address,
            'notes'       => $this->notes,
        ]);

        session()->flash('success', 'مشتری ثبت شد.');
        return redirect()->route('customers.index');
    }

    public function render()
    {
        return view('livewire.customers.create')->layout('components.layouts.app');
    }
}
