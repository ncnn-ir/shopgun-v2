<?php
namespace App\Livewire\Orders;

use App\Models\Order;
use Illuminate\Support\Facades\Auth;
use Livewire\Component;
use Livewire\WithPagination;
use Livewire\Attributes\On;

class SupplyModal extends Component
{
    use WithPagination;

    public bool $open = false;
    public string $filter = 'pending';
    public string $statusFilter = '';
    public string $search = '';
    public int $perPage = 15;
    public array $selected = [];

    #[On('openSupplyModal')]
    public function triggerOpen(): void
    {
        $this->resetPage();
        $this->open = true;
    }

    public function close(): void { $this->open = false; $this->selected = []; }
    public function updatingSearch() { $this->resetPage(); }
    public function updatingFilter() { $this->resetPage(); }

    public function markFound(int $id) { $o = Order::find($id); if ($o) $o->markSupplyFound(Auth::id()); }
    public function deliverToShipping(int $id) { $o = Order::find($id); if ($o && $o->isSupplyFound()) $o->markDeliveredToShipping(Auth::id()); }
    public function unmarkFound(int $id) { $o = Order::find($id); if ($o) $o->update(['supply_status'=>'awaiting_supply','supply_found_at'=>null,'supply_found_by'=>null]); }
    public function bulkMarkFound() { foreach ($this->selected as $id) { $o = Order::find($id); if ($o && $o->isAwaitingSupply()) $o->markSupplyFound(Auth::id()); } $this->selected = []; }
    public function bulkDeliver() { foreach ($this->selected as $id) { $o = Order::find($id); if ($o && $o->isSupplyFound()) $o->markDeliveredToShipping(Auth::id()); } $this->selected = []; }

    protected function baseQ()
    {
        $q = Order::query()->with(['customer','items']);
        match ($this->filter) {
            'pending' => $q->where(fn($x) => $x->whereIn('supply_status',['awaiting_supply','pending','default'])->orWhereNull('supply_status')),
            'found' => $q->where('supply_status','found'),
            'delivered' => $q->where('supply_status','delivered_to_shipping'),
            default => null,
        };
        if ($this->statusFilter !== '') $q->where('status', $this->statusFilter);
        if ($this->search) {
            $s = '%'.$this->search.'%';
            $q->where(fn($x) => $x->where('order_number','like',$s)->orWhere('id','like',$s)
                ->orWhereHas('customer', fn($c) => $c->where('first_name','like',$s)->orWhere('last_name','like',$s)->orWhere('phone','like',$s)));
        }
        return $q->orderByDesc('created_at');
    }

    public function statusOptions(): array
    {
        return [
            'processing' => '🔄 در حال انجام',
            'completed' => '✅ تکمیل شده',
            'cancelled' => '❌ لغو شده',
            'on-hold' => '⏸ بررسی',
            'final-check' => '🔍 چک نهایی',
            'courier' => '🚚 مامور',
        ];
    }

    public function render()
    {
        $orders = $this->baseQ()->paginate($this->perPage);
        $stats = [
            'pending' => Order::where(fn($q) => $q->whereIn('supply_status',['awaiting_supply','pending','default'])->orWhereNull('supply_status'))->count(),
            'found' => Order::where('supply_status','found')->count(),
            'delivered' => Order::where('supply_status','delivered_to_shipping')->count(),
        ];
        return view('livewire.orders.supply-modal', ['orders' => $orders, 'stats' => $stats, 'statusOptions' => $this->statusOptions()]);
    }
}
