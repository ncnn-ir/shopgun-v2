<?php

namespace App\Exports;

use App\Models\Order;
use Maatwebsite\Excel\Concerns\FromCollection;
use Maatwebsite\Excel\Concerns\WithHeadings;
use Maatwebsite\Excel\Concerns\WithMapping;
use Maatwebsite\Excel\Concerns\ShouldAutoSize;

class OrdersExport implements FromCollection, WithHeadings, WithMapping, ShouldAutoSize
{
    public function __construct(
        protected string $search = '',
        protected string $statusFilter = '',
        protected string $channelFilter = ''
    ) {}

    public function collection()
    {
        return Order::with(['customer', 'channel'])
            ->when($this->search, function ($q) {
                $q->where(function ($qq) {
                    $qq->where('order_number', 'like', "%{$this->search}%")
                       ->orWhere('phone', 'like', "%{$this->search}%")
                       ->orWhereHas('customer', fn ($cq) => $cq->where('name', 'like', "%{$this->search}%"));
                });
            })
            ->when($this->statusFilter, fn ($q) => $q->where('status', $this->statusFilter))
            ->when($this->channelFilter, fn ($q) => $q->where('channel_id', $this->channelFilter))
            ->latest('id')
            ->get();
    }

    public function headings(): array
    {
        return ['شماره سفارش', 'مشتری', 'تلفن', 'کدپستی', 'آدرس', 'وضعیت', 'کانال', 'بیمه', 'مبلغ', 'تاریخ'];
    }

    public function map($order): array
    {
        return [
            $order->order_number,
            $order->customer?->name ?? '',
            $order->phone,
            $order->postal_code,
            $order->address,
            $order->status_label,
            $order->channel?->name ?? '',
            $order->insurance,
            $order->amount,
            $order->created_at?->format('Y/m/d H:i'),
        ];
    }
}
