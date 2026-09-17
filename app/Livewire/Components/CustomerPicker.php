<?php

namespace App\Livewire\Components;

use App\Models\Customer;
use Livewire\Attributes\On;
use Livewire\Component;

class CustomerPicker extends Component
{
    /** شناسه مشتری انتخاب‌شده */
    public ?int $customerId = null;

    /** متن جستجو */
    public string $query = '';

    /** نتیجه‌ها */
    public array $results = [];

    /** حالت: search | selected | new */
    public string $mode = 'search';

    /** اطلاعات مشتری انتخاب‌شده برای نمایش */
    public array $selectedData = [];

    /** فرم مشتری جدید */
    public string $newName = '';
    public string $newPhone = '';
    public string $newAddress = '';
    public string $newPostal = '';

    /** پیشوند کانتینر برای رویداد */
    public string $eventPrefix = 'customer';

    /** نمایش inline */
    public bool $compact = false;

    public function mount(?int $customerId = null, string $eventPrefix = 'customer', bool $compact = false): void
    {
        $this->eventPrefix = $eventPrefix;
        $this->compact = $compact;

        if ($customerId) {
            $this->loadCustomer($customerId);
        }
    }

    public function updatedQuery(): void
    {
        $q = trim($this->query);
        if (mb_strlen($q) < 2) {
            $this->results = [];
            return;
        }

        $normalized = Customer::normalizePhone($q);

        // جستجو در تلفن‌های جدید + فیلد قدیمی + نام
        $this->results = Customer::query()
            ->withCount('orders')
            ->with(['phones', 'addresses'])
            ->where(function ($qq) use ($q, $normalized) {
                if ($normalized !== '') {
                    $qq->whereHas('phones', fn($p) => $p->where('phone', 'like', "%{$normalized}%"))
                       ->orWhere('phone', 'like', "%{$normalized}%");
                }
                $qq->orWhere('name', 'like', "%{$q}%");
            })
            ->orderByDesc('id')
            ->limit(15)
            ->get()
            ->map(fn($c) => [
                'id'         => $c->id,
                'name'       => $c->name ?: '—',
                'phone'      => $c->primaryPhone()?->formatted
                                ?? $c->phone
                                ?? '—',
                'phone_raw'  => $c->primaryPhone()?->phone ?? $c->phone,
                'address'    => $c->primaryAddress()?->short ?? $c->address ?? '',
                'postal'     => $c->primaryAddress()?->postal_code ?? $c->postal_code ?? '',
                'orders'     => $c->orders_count ?? 0,
                'last_at'    => $c->updated_at?->toIso8601String(),
            ])
            ->toArray();
    }

    public function selectCustomer(int $id): void
    {
        $this->loadCustomer($id);
        $this->dispatch("{$this->eventPrefix}-selected", customerId: $id, data: $this->selectedData);
    }

    public function loadCustomer(int $id): void
    {
        $c = Customer::with(['phones', 'addresses'])->find($id);
        if (!$c) return;

        $primaryPhone = $c->primaryPhone();
        $primaryAddr  = $c->primaryAddress();

        $this->customerId = $c->id;
        $this->selectedData = [
            'id'          => $c->id,
            'name'        => $c->name,
            'phone'       => $primaryPhone?->phone ?? $c->phone,
            'phone_fmt'   => $primaryPhone?->formatted ?? $c->phone,
            'phone_label' => $primaryPhone?->label,
            'address'     => $primaryAddr?->address ?? $c->address,
            'city'        => $primaryAddr?->city,
            'province'    => $primaryAddr?->province,
            'postal_code' => $primaryAddr?->postal_code ?? $c->postal_code,
            'extra_phones'    => $c->phones->pluck('phone')->toArray(),
            'extra_addresses' => $c->addresses->pluck('short')->toArray(),
        ];
        $this->mode = 'selected';
        $this->query = '';
        $this->results = [];
    }

    public function clearSelection(): void
    {
        $this->customerId = null;
        $this->selectedData = [];
        $this->mode = 'search';
        $this->query = '';
        $this->results = [];
        $this->dispatch("{$this->eventPrefix}-cleared");
    }

    public function startNew(): void
    {
        $this->mode = 'new';
        $this->newName = '';
        $this->newPhone = $this->query; // پیش‌پر کردن
        $this->newAddress = '';
        $this->newPostal = '';
    }

    public function cancelNew(): void
    {
        $this->mode = 'search';
    }

    public function createCustomer(): void
    {
        $this->validate([
            'newName'    => 'required|string|max:120',
            'newPhone'   => 'required|string|max:20',
            'newAddress' => 'nullable|string|max:500',
            'newPostal'  => 'nullable|string|max:20',
        ], [], [
            'newName'    => 'نام',
            'newPhone'   => 'تلفن',
            'newAddress' => 'آدرس',
            'newPostal'  => 'کدپستی',
        ]);

        $normalized = Customer::normalizePhone($this->newPhone);
        if ($normalized === '') {
            $this->addError('newPhone', 'شماره تلفن نامعتبر');
            return;
        }

        // بررسی تکراری
        $existing = Customer::findByPhone($normalized);
        if ($existing) {
            $this->selectCustomer($existing->id);
            return;
        }

        $customer = Customer::create([
            'name'        => $this->newName,
            'phone'       => $normalized,
            'address'     => $this->newAddress,
            'postal_code' => $this->newPostal,
        ]);

        $customer->addPhone($normalized, 'اصلی', true);
        if ($this->newAddress || $this->newPostal) {
            $customer->addAddress([
                'address'     => $this->newAddress,
                'postal_code' => $this->newPostal,
            ], true);
        }

        $this->loadCustomer($customer->id);
        $this->dispatch("{$this->eventPrefix}-selected", customerId: $customer->id, data: $this->selectedData);
    }

    #[On('customer-picker-set')]
    public function setCustomer(?int $id = null): void
    {
        if ($id) $this->loadCustomer($id);
    }

    public function render()
    {
        return view('livewire.components.customer-picker');
    }
}
