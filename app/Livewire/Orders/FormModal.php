<?php
namespace App\Livewire\Orders;

use App\Models\Channel;
use App\Models\Customer;
use App\Models\Order;
use App\Models\Product;
use Livewire\Attributes\On;
use Livewire\Component;

class FormModal extends Component
{
    public bool $show = false;
    public ?int $orderId = null;
    public string $mode = 'create';

    public string $customerName = '';
    public string $phone = '';
    public string $postalCode = '';
    public string $address = '';
    public ?int $customerId = null;

    public array $items = [];
    public array $phoneSuggestions = [];
    public array $skuSuggestions = [];

    public string $insurance = '0';
    public string $discount = '0';
    public string $shipping = '0';
    public string $status = 'pending';
    public ?int $channelId = null;
    public string $notes = '';

    public int $activeSkuIndex = -1;

    #[On('open-order-form')]
    public function open(?int $orderId = null): void
    {
        $this->resetForm();
        $this->orderId = $orderId;
        $this->mode = $orderId ? 'edit' : 'create';

        if ($orderId) {
            $o = Order::with('items')->find($orderId);
            if ($o) {
                $this->customerId = $o->customer_id;
                $this->customerName = $o->customer_name ?? '';
                $this->phone = $o->phone ?? '';
                $this->postalCode = $o->postal_code ?? '';
                $this->address = $o->address ?? '';
                $this->insurance = (string)($o->insurance ?? 0);
                $this->discount = (string)($o->discount ?? 0);
                $this->shipping = (string)($o->shipping ?? 0);
                $this->status = $o->status ?? 'pending';
                $this->channelId = $o->channel_id;
                $this->notes = $o->notes ?? '';
                $this->items = $o->items->map(fn($i) => [
                    'title' => $i->title,
                    'sku' => $i->sku ?? '',
                    'price' => (float)$i->price,
                    'quantity' => (int)$i->quantity,
                    'certificate_needed' => (bool)$i->certificate_needed,
                ])->toArray();
            }
        }

        if (empty($this->items)) $this->addItem();

        $this->show = true;
    }

    public function close(): void { $this->show = false; $this->resetForm(); }

    public function resetForm(): void
    {
        $this->orderId = null;
        $this->customerId = null;
        $this->customerName = '';
        $this->phone = '';
        $this->postalCode = '';
        $this->address = '';
        $this->items = [];
        $this->insurance = '0';
        $this->discount = '0';
        $this->shipping = '0';
        $this->status = 'pending';
        $this->channelId = null;
        $this->notes = '';
        $this->activeSkuIndex = -1;
        $this->skuSuggestions = [];
        $this->phoneSuggestions = [];
    }

    /* ═══ Items ═══ */
    public function addItem(): void
    {
        $this->items[] = ['title'=>'', 'sku'=>'', 'price'=>0, 'quantity'=>1, 'certificate_needed'=>false];
    }

    public function removeItem(int $idx): void
    {
        unset($this->items[$idx]);
        $this->items = array_values($this->items);
        if (empty($this->items)) $this->addItem();
        $this->autoInsurance();
    }

    public function updatedItems(): void { $this->autoInsurance(); }

    /* ═══ Insurance auto = total / 1,000,000 ═══ */
    public function autoInsurance(): void
    {
        $total = collect($this->items)->sum(fn($i) => (float)($i['price'] ?? 0) * (int)($i['quantity'] ?? 1));
        if ($total > 0) {
            $this->insurance = (string) floor($total / 1000000);
        }
    }

    /* ═══ Phone Search ═══ */
    public function updatedPhone(): void
    {
        $q = preg_replace('/\D/', '', $this->phone);
        if (strlen($q) < 3) { $this->phoneSuggestions = []; return; }

        $this->phoneSuggestions = Customer::where('phone', 'like', "%{$q}%")
            ->orWhere('name', 'like', "%{$this->phone}%")
            ->limit(8)->get()
            ->map(fn($c) => [
                'id' => $c->id,
                'name' => $c->name,
                'phone' => $c->phone,
                'address' => $c->address ?? '',
                'postal_code' => $c->postal_code ?? '',
                'orders_count' => $c->orders()->count(),
            ])->toArray();
    }

    public function selectPhoneSuggestion(int $customerId): void
    {
        $c = Customer::find($customerId);
        if (!$c) return;
        $this->customerId = $c->id;
        $this->customerName = $c->name;
        $this->phone = $c->phone;
        $this->address = $c->address ?? '';
        $this->postalCode = $c->postal_code ?? '';
        $this->phoneSuggestions = [];
    }

    /* ═══ SKU Search ═══ */
    public function updatedItemsSku($value, $key): void
    {
        $parts = explode('.', $key);
        $idx = (int)($parts[0] ?? -1);
        if ($idx < 0) return;

        $q = trim($value);
        if (strlen($q) < 2) { $this->skuSuggestions = []; $this->activeSkuIndex = -1; return; }

        $this->activeSkuIndex = $idx;
        $this->skuSuggestions = Product::where('is_active', true)
            ->where(function($qq) use ($q) {
                $qq->where('sku', 'like', "%{$q}%")
                   ->orWhere('name', 'like', "%{$q}%");
            })
            ->limit(10)->get()
            ->map(fn($p) => [
                'id' => $p->id, 'sku' => $p->sku, 'name' => $p->name,
                'price' => (float)$p->price, 'stock' => $p->stock_quantity,
                'image' => $p->image_src,
            ])->toArray();
    }

    public function selectSkuProduct(int $productId): void
    {
        $p = Product::find($productId);
        if (!$p || $this->activeSkuIndex < 0) return;
        $this->items[$this->activeSkuIndex]['sku'] = $p->sku;
        $this->items[$this->activeSkuIndex]['title'] = $p->name;
        $this->items[$this->activeSkuIndex]['price'] = (float)$p->price;
        $this->skuSuggestions = [];
        $this->activeSkuIndex = -1;
        $this->autoInsurance();
    }

    /* ═══ Computed ═══ */
    public function getSubtotalProperty(): float {
        return collect($this->items)->sum(fn($i) => (float)($i['price'] ?? 0) * (int)($i['quantity'] ?? 1));
    }
    public function getTotalProperty(): float {
        return max(0, $this->subtotal + (float)$this->insurance + (float)$this->shipping - (float)$this->discount);
    }

    /* ═══ Save ═══ */
    public function save(): void
    {
        $this->validate([
            'phone' => 'required|string|max:20',
            'customerName' => 'required|string|max:120',
            'items' => 'required|array|min:1',
            'items.*.title' => 'required|string|max:255',
        ]);

        // مشتری
        $customer = $this->customerId ? Customer::find($this->customerId) : null;
        if (!$customer) {
            $customer = Customer::firstOrCreate(
                ['phone' => preg_replace('/\D/', '', $this->phone)],
                ['name' => $this->customerName, 'address' => $this->address, 'postal_code' => $this->postalCode]
            );
        }
        $customer->update([
            'name' => $this->customerName,
            'address' => $this->address,
            'postal_code' => $this->postalCode,
        ]);

        // سفارش
        $data = [
            'customer_id' => $customer->id,
            'customer_name' => $this->customerName,
            'phone' => $this->phone,
            'address' => $this->address,
            'postal_code' => $this->postalCode,
            'status' => $this->status,
            'channel_id' => $this->channelId,
            'insurance' => (float)$this->insurance,
            'discount' => (float)$this->discount,
            'shipping' => (float)$this->shipping,
            'amount' => $this->total,
            'notes' => $this->notes,
        ];

        if ($this->orderId) {
            $order = Order::find($this->orderId);
            $order->update($data);
            $order->items()->delete();
        } else {
            $data['order_number'] = Order::generateNumber();
            $order = Order::create($data);
        }

        foreach ($this->items as $it) {
            $order->items()->create([
                'product_id' => null,
                'sku' => $it['sku'] ?? null,
                'title' => $it['title'],
                'price' => (float)$it['price'],
                'quantity' => (int)$it['quantity'],
                'certificate_needed' => !empty($it['certificate_needed']),
            ]);
        }

        $this->dispatch('order-saved', orderId: $order->id);
        $this->dispatch('notify', type: 'success', message: $this->orderId ? 'ویرایش شد ✅' : 'ثبت شد ✅');
        $this->close();
    }

    public function render() {
        return view('livewire.orders.form-modal', [
            'channels' => Channel::all(),
        ]);
    }
}
