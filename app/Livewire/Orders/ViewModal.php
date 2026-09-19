<?php
namespace App\Livewire\Orders;

use App\Models\Customer;
use App\Models\Order;
use Livewire\Attributes\On;
use Livewire\Component;

class ViewModal extends Component
{
    public bool $show = false;
    public ?Order $order = null;
    public array $customerStats = [];
    public array $timeline = [];

    #[On('open-order-view')]
    public function open(int $orderId): void
    {
        $this->order = Order::with(['customer', 'items', 'channel'])->find($orderId);
        if (!$this->order) return;

        // آمار مشتری
        if ($this->order->customer_id) {
            $customer = Customer::find($this->order->customer_id);
            if ($customer) {
                $orders = $customer->orders()->orderBy('created_at')->get();
                $this->customerStats = [
                    'total' => $orders->count(),
                    'sum' => (float) $orders->sum('amount'),
                    'first' => $orders->first()?->created_at,
                    'last' => $orders->last()?->created_at,
                ];
            }
        }

        $this->buildTimeline();
        $this->show = true;
    }

    protected function buildTimeline(): void
    {
        $stages = [
            ['id' => 'pending', 'label' => 'ثبت سفارش', 'icon' => '📝'],
            ['id' => 'final-check', 'label' => 'چک نهایی', 'icon' => '🔍'],
            ['id' => 'courier', 'label' => 'تحویل مامور', 'icon' => '🚚'],
        ];

        $currentStatus = $this->order->status ?? 'pending';
        $currentIdx = array_search($currentStatus, array_column($stages, 'id'));
        if ($currentIdx === false) $currentIdx = 0;

        // گرفتن تاریخچه از activity log
        $activities = [];
        try {
            $logs = \Spatie\Activitylog\Models\Activity::where('subject_type', Order::class)
                ->where('subject_id', $this->order->id)
                ->where('event', 'updated')
                ->orderBy('created_at')
                ->get();

            foreach ($logs as $log) {
                $changes = $log->properties['attributes'] ?? [];
                if (isset($changes['status'])) {
                    $activities[] = [
                        'status' => $changes['status'],
                        'at' => $log->created_at,
                    ];
                }
            }
        } catch (\Throwable $e) {}

        // اگر activity نیست، از created_at سفارش استفاده کن
        if (empty($activities)) {
            $activities[] = ['status' => 'pending', 'at' => $this->order->created_at];
            if ($currentIdx >= 1) $activities[] = ['status' => 'final-check', 'at' => $this->order->updated_at];
            if ($currentIdx >= 2) $activities[] = ['status' => 'courier', 'at' => $this->order->updated_at];
        }

        $this->timeline = [];
        foreach ($stages as $i => $stage) {
            $state = $i < $currentIdx ? 'done' : ($i === $currentIdx ? 'current' : '');

            // پیدا کردن تاریخ این مرحله از activity
            $at = null;
            foreach ($activities as $a) {
                if ($a['status'] === $stage['id']) {
                    $at = $a['at'];
                    break;
                }
            }

            $this->timeline[] = [
                'label' => $stage['label'],
                'icon' => $stage['icon'],
                'state' => $state,
                'date' => $at ? \App\Support\PersianDate::format($at, 'Y/m/d') : '',
                'time' => $at ? $at->format('H:i') : '',
            ];
        }
    }

    public function close(): void { $this->show = false; $this->order = null; }

    public function cycleStatus(): void
    {
        if (!$this->order) return;
        $statuses = ['pending', 'final-check', 'courier'];
        $cur = array_search($this->order->status, $statuses);
        $next = $statuses[($cur === false ? 0 : ($cur + 1)) % count($statuses)];
        $this->order->update(['status' => $next]);
        $this->order->refresh();
        $this->open($this->order->id);
        $this->dispatch('order-saved');
        $this->dispatch('notify', type: 'success', message: 'وضعیت تغییر کرد');
    }

    public function editOrder(): void
    {
        $id = $this->order->id;
        $this->close();
        $this->dispatch('open-order-form', orderId: $id);
    }

    public function deleteOrder(): void
    {
        $this->order?->delete();
        $this->close();
        $this->dispatch('order-saved');
        $this->dispatch('notify', type: 'success', message: 'حذف شد');
    }


    public function openCustomerProfile(int $customerId): void
    {
        $this->close();
        $this->dispatch('open-customer-profile', customerId: $customerId);
    }

    public bool $showProductInfo = false;
    public ?array $productInfo = null;

    public function openProductInfo(string $sku): void
    {
        $sku = trim($sku);
        if ($sku === '') return;

        $info = ['sku' => $sku, 'title' => '', 'price' => 0, 'weight' => null, 'dimensions' => null, 'stock' => null, 'stock_status' => 'unknown', 'image' => null, 'view_url' => null];

        // از ProductIdentity
        $id = \App\Models\ProductIdentity::where('sku', $sku)->first();
        if ($id) {
            $info['title'] = $id->canonical_name ?? '';
            $info['price'] = (float) ($id->last_known_price ?? 0);
            $info['weight'] = $id->last_known_weight;
            $woo = $id->last_known_woo_data;
            if (is_array($woo)) {
                $info['image'] = $woo['images'][0]['src'] ?? null;
                $info['dimensions'] = $woo['dimensions'] ?? null;
                $info['stock'] = $woo['stock_quantity'] ?? null;
                $info['stock_status'] = $woo['stock_status'] ?? 'unknown';
                if (!empty($id->woo_product_id)) {
                    $site = rtrim((string) \App\Models\AppSetting::get('commerce_url', ''), '/');
                    $info['view_url'] = $site . '/?p=' . $id->woo_product_id;
                }
            }
        }

        // از Product محلی
        if (empty($info['title'])) {
            $local = \App\Models\Product::where('sku', $sku)->first();
            if ($local) {
                $info['title'] = $local->name;
                $info['price'] = (float) $local->price;
                $info['weight'] = $local->weight;
                $info['image'] = $local->image_src;
                $info['stock'] = $local->stock_quantity;
                $info['stock_status'] = $local->stock_status;
                $info['dimensions'] = ['length'=>$local->length, 'width'=>$local->width, 'height'=>$local->height];
            }
        }

        // از آیتم سفارش
        if (empty($info['title'])) {
            $item = \App\Models\OrderItem::where('sku', $sku)->latest('id')->first();
            if ($item) {
                $info['title'] = $item->title;
                $info['price'] = (float) $item->price;
            }
        }

        $this->productInfo = $info;
        $this->showProductInfo = true;
    }

    public function closeProductInfo(): void
    {
        $this->showProductInfo = false;
        $this->productInfo = null;
    }

    public function render() { return view('livewire.orders.view-modal'); }
}
