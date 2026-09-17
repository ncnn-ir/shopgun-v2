<?php

namespace App\Livewire\Orders;

use App\Models\Channel;
use App\Models\Customer;
use App\Models\Order;
use Livewire\Attributes\On;
use Livewire\Component;

class Create extends Component
{
    public string $phone = '';
    public string $customerName = '';
    public string $postalCode = '';
    public string $address = '';
    public string $insurance = '0';
    public string $status = 'pending';
    public ?int $channelId = null;
    public bool $invoiceNeeded = false;
    public string $notes = '';

    /** @var array<int, array{title:string,sku:string,price:string,qty:int,cert:bool}> */
    public array $items = [];

    public bool $customerFound = false;
    public ?int $existingCustomerId = null;

    public function mount(): void
    {
        $this->addItem();
    }

    public function addItem(): void
    {
        $this->items[] = [
            'title' => '',
            'sku'   => '',
            'price' => '',
            'qty'   => 1,
            'cert'  => true,
        ];
    }

    public function removeItem(int $index): void
    {
        if (isset($this->items[$index])) {
            unset($this->items[$index]);
            $this->items = array_values($this->items);
        }
        $this->recalcInsurance();
    }

    /** وقتی کاربر تلفن رو تایپ کرد، فقط شماره رو همگام کن */
    #[On('phone-typed')]
    public function onPhoneTyped(string $value): void
    {
        $this->phone = $value;
        $this->checkCustomer();
    }

    /** وقتی کاربر از لیست پیشنهادها انتخاب کرد، همه‌چیز رو پر کن */
    #[On('phone-selected')]
    public function onPhoneSelected(string $phone, string $name = '', string $address = '', string $postal = ''): void
    {
        $this->phone        = $phone;
        $this->customerName = $name;
        $this->address      = $address;
        $this->postalCode   = $postal;
        $this->checkCustomer();
    }

    /** انتخاب محصول از SkuSearch */
    #[On('sku-selected')]
    public function onSkuSelected(string $sku, string $title = '', float $price = 0): void
    {
        // دنبال ردیف خالی بگرد
        foreach (array_reverse(array_keys($this->items)) as $idx) {
            if (empty($this->items[$idx]['sku'])) {
                $this->items[$idx]['sku']   = $sku;
                $this->items[$idx]['title'] = $title;
                $this->items[$idx]['price'] = (string) $price;
                $this->recalcInsurance();
                return;
            }
        }

        $this->items[] = [
            'title' => $title,
            'sku'   => $sku,
            'price' => (string) $price,
            'qty'   => 1,
            'cert'  => true,
        ];
        $this->recalcInsurance();
    }

    public function checkCustomer(): void
    {
        $normalized = $this->normalizePhone($this->phone);

        if (strlen($normalized) < 10) {
            $this->customerFound = false;
            $this->existingCustomerId = null;
            return;
        }

        $customer = Customer::where('phone', $normalized)->first();

        if ($customer) {
            $this->customerFound = true;
            $this->existingCustomerId = $customer->id;
            if (! $this->customerName) $this->customerName = $customer->name ?? '';
            if (! $this->postalCode)   $this->postalCode   = $customer->postal_code ?? '';
            if (! $this->address)      $this->address      = $customer->address ?? '';
        } else {
            $this->customerFound = false;
            $this->existingCustomerId = null;
        }
    }

    public function updatedItems(): void
    {
        $this->recalcInsurance();
    }

    public function recalcInsurance(): void
    {
        $total = 0;
        foreach ($this->items as $it) {
            $total += ((float) ($it['price'] ?? 0)) * ((int) ($it['qty'] ?? 1));
        }
        $this->insurance = (string) round($total / 100000);
    }

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
            'phone'        => 'required|min:10',
            'customerName' => 'nullable|string|max:255',
            'postalCode'   => 'nullable|string|max:20',
            'address'      => 'nullable|string',
            'insurance'    => 'nullable|numeric',
            'status'       => 'required|in:pending,final-check,courier',
            'channelId'    => 'nullable|exists:channels,id',
        ], [
            'phone.required' => 'شماره تلفن الزامی است.',
            'phone.min'      => 'شماره تلفن حداقل ۱۰ رقم.',
        ]);

        $normalized = $this->normalizePhone($this->phone);

        $customer = Customer::where('phone', $normalized)->first();
        if ($customer) {
            $customer->update([
                'name'        => $this->customerName ?: $customer->name,
                'postal_code' => $this->postalCode ?: $customer->postal_code,
                'address'     => $this->address ?: $customer->address,
            ]);
        } else {
            $customer = Customer::create([
                'name'        => $this->customerName ?: 'بدون نام',
                'phone'       => $normalized,
                'postal_code' => $this->postalCode,
                'address'     => $this->address,
            ]);
        }

        $lastNumber = (int) Order::max('order_number');
        $newNumber  = max($lastNumber + 1, 317401);

        $amount = 0;
        foreach ($this->items as $it) {
            $amount += ((float) ($it['price'] ?? 0)) * ((int) ($it['qty'] ?? 1));
        }

        $order = Order::create([
            'order_number'   => (string) $newNumber,
            'customer_id'    => $customer->id,
            'channel_id'     => $this->channelId,
            'status'         => $this->status,
            'amount'         => $amount,
            'insurance'      => (float) ($this->insurance ?: 0),
            'phone'          => $normalized,
            'address'        => $this->address,
            'postal_code'    => $this->postalCode,
            'notes'          => $this->notes,
            'invoice_needed' => $this->invoiceNeeded,
        ]);

        foreach ($this->items as $i => $it) {
            if (empty($it['title']) && empty($it['sku'])) continue;
            $order->items()->create([
                'title'       => $it['title'] ?: 'محصول',
                'sku'         => $it['sku'] ?? '',
                'price'       => (float) ($it['price'] ?? 0),
                'quantity'    => (int) ($it['qty'] ?? 1),
                'cert_needed' => (bool) ($it['cert'] ?? true),
                'sort_order'  => $i,
            ]);
        }

        session()->flash('success', "سفارش #{$newNumber} با موفقیت ثبت شد.");

        return redirect()->route('orders.index');
    }

    public function render()
    {
        return view('livewire.orders.create', [
            'channels' => Channel::where('is_active', true)->orderBy('sort_order')->get(),
        ])->layout('components.layouts.app');
    }
}
