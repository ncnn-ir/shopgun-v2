<?php

namespace App\Services;

use App\Models\Order;
use Illuminate\Support\Carbon;
use Illuminate\Support\Facades\Log;

class TipaxImportService
{
    /**
     * ایمپورت ردیف‌های Tipax
     * $rows = [['tracking_code' => '...', 'order_number' => '...', 'phone' => '...', 'status' => '...', 'date' => '...'], ...]
     */
    public function import(array $rows): array
    {
        $stats = ['matched' => 0, 'updated' => 0, 'created' => 0, 'unmatched' => 0, 'errors' => 0];

        foreach ($rows as $row) {
            try {
                $order = $this->findOrder($row);

                if (! $order) {
                    $stats['unmatched']++;
                    continue;
                }

                $stats['matched']++;
                $isNew = empty($order->tracking_code);

                $events   = $order->shipping_events ?? [];
                $newEvent = [
                    'status'      => $row['status'] ?? '',
                    'description' => $row['description'] ?? ($row['status'] ?? ''),
                    'date'        => $row['date'] ?? now()->format('Y/m/d H:i'),
                    'ts'          => now()->timestamp,
                ];

                // جلوگیری از تکرار
                $exists = false;
                foreach ($events as $e) {
                    if (($e['status'] ?? '') === $newEvent['status']
                        && ($e['date'] ?? '') === $newEvent['date']) {
                        $exists = true;
                        break;
                    }
                }
                if (! $exists) {
                    $events[] = $newEvent;
                }

                $order->update([
                    'tracking_code'   => $row['tracking_code'] ?? $order->tracking_code,
                    'carrier'         => 'tipax',
                    'shipping_status' => $row['status'] ?? $order->shipping_status,
                    'shipping_events' => $events,
                    'shipped_at'      => $order->shipped_at ?? now(),
                    'delivered_at'    => $this->isDelivered($row['status'] ?? '')
                        ? ($order->delivered_at ?? now())
                        : $order->delivered_at,
                ]);

                // اگه تحویل شد، وضعیت سفارش هم به «تحویل مامور» تغییر کن
                if ($this->isDelivered($row['status'] ?? '') && $order->status !== 'courier') {
                    $order->update(['status' => 'courier']);
                }

                $isNew ? $stats['created']++ : $stats['updated']++;

            } catch (\Throwable $e) {
                Log::error('TipaxImport: ' . $e->getMessage());
                $stats['errors']++;
            }
        }

        return $stats;
    }

    protected function findOrder(array $row): ?Order
    {
        // اولویت ۱: شماره سفارش
        if (! empty($row['order_number'])) {
            $o = Order::where('order_number', trim($row['order_number']))->first();
            if ($o) return $o;
        }

        // اولویت ۲: شماره تلفن
        if (! empty($row['phone'])) {
            $digits = preg_replace('/\D/', '', $row['phone']);
            if (str_starts_with($digits, '98') && strlen($digits) > 10) {
                $digits = substr($digits, 2);
            }
            if (str_starts_with($digits, '0') && strlen($digits) > 10) {
                $digits = substr($digits, 1);
            }

            if (strlen($digits) >= 10) {
                $o = Order::where('phone', 'like', "%{$digits}%")->latest('id')->first();
                if ($o) return $o;
            }
        }

        // اولویت ۳: کد رهگیری موجود
        if (! empty($row['tracking_code'])) {
            $o = Order::where('tracking_code', $row['tracking_code'])->first();
            if ($o) return $o;
        }

        return null;
    }

    protected function isDelivered(string $status): bool
    {
        $s = mb_strtolower($status);
        return str_contains($s, 'تحویل') && ! str_contains($s, 'نشد')
            || str_contains($s, 'deliver');
    }
}
