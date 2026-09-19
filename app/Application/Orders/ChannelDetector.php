<?php

namespace App\Application\Orders;

use App\Models\Order;

/**
 * تشخیص خودکار کانال فروش از منابع مختلف سفارش
 */
class ChannelDetector
{
    /**
     * اولویت تشخیص:
     * 1) اگر sales_channel ست است و در لیست معتبر است → همان
     * 2) از meta_data (JSON)
     * 3) از payment_method / payment_title
     * 4) از customer_note / note
     * 5) از created_via
     * 6) از tracking_code / carrier
     * 7) پیش‌فرض: website
     */
    public function detect(Order $order): string
    {
        // 1) اگر قبلاً دستی ست شده و معتبر است
        $current = strtolower(trim((string) $order->sales_channel));
        if ($current && $current !== 'website' && $current !== 'unknown' && isset(\App\View\Components\ChannelBadge::MAP[$current])) {
            return $current;
        }

        // 2) متادیتا
        $fromMeta = $this->fromMeta($order->meta ?? null);
        if ($fromMeta) return $fromMeta;

        // 3) درگاه پرداخت
        $fromPay = $this->fromPayment($order->payment_method ?? '', $order->payment_title ?? '');
        if ($fromPay) return $fromPay;

        // 4) نوت مشتری / نوت سفارش
        $fromNote = $this->fromText(
            trim((string) ($order->customer_note ?? '') . ' ' . (string) ($order->note ?? ''))
        );
        if ($fromNote) return $fromNote;

        // 5) created_via
        $fromVia = $this->fromText((string) ($order->created_via ?? ''));
        if ($fromVia) return $fromVia;

        // 6) carrier
        $fromCarrier = $this->fromText((string) ($order->carrier ?? ''));
        if ($fromCarrier) return $fromCarrier;

        return 'website';
    }

    protected function fromMeta($meta): ?string
    {
        if (empty($meta)) return null;
        $json = is_string($meta) ? $meta : json_encode($meta, JSON_UNESCAPED_UNICODE);
        $json = strtolower($json);

        $map = [
            'basalam'   => ['basalam', 'باسلام', '_basalam_', 'bslm'],
            'digikala'  => ['digikala', 'دیجی‌کالا', 'digikala_', 'djk'],
            'torob'     => ['torob', 'ترب', 'torob_'],
            'divar'     => ['divar', 'دیوار', 'divar_'],
            'sheypoor'  => ['sheypoor', 'شیپور', 'sheypur'],
            'instagram' => ['instagram', 'اینستا', 'ig_'],
            'telegram'  => ['telegram', 'تلگرام', 'tg_'],
            'whatsapp'  => ['whatsapp', 'واتساپ', 'wa_'],
            'zibal'     => ['zibal', 'زیبال', '_zibal'],
            'sadad'     => ['sadad', 'سداد', '_sadad'],
            'zarinpal'  => ['zarinpal', 'زرین', '_zarinpal'],
            'asanpardakht' => ['asanpardakht', 'آسان پرداخت', '_asan'],
            'idpay'     => ['idpay', '_idpay'],
            'nextpay'   => ['nextpay', '_nextpay'],
            'payir'     => ['payir', '_payir'],
        ];

        foreach ($map as $channel => $hints) {
            foreach ($hints as $h) {
                if (str_contains($json, $h)) return $channel;
            }
        }
        return null;
    }

    protected function fromPayment(string $method, string $title): ?string
    {
        $hay = strtolower(trim($method . ' ' . $title));
        if ($hay === '') return null;

        // نگاشت درگاه‌ها و روش‌های پرداخت
        $map = [
            'zibal'        => ['zibal', 'زیبال'],
            'sadad'        => ['sadad', 'سداد', 'melli', 'bank_melli', 'mellat', 'ملت'],
            'zarinpal'     => ['zarinpal', 'zarin', 'زرین'],
            'asanpardakht' => ['asanpardakht', 'asan', 'آسان', 'pec'],
            'idpay'        => ['idpay', 'آی‌دی‌پی'],
            'nextpay'      => ['nextpay'],
            'payir'        => ['payir', 'pay.ir'],
            'mellat'       => ['mellat'],
            'saman'        => ['saman', 'سامان'],
            'parsian'      => ['parsian', 'پارسیان'],
            'pasargad'     => ['pasargad', 'پاسارگاد'],
            'basalam'      => ['basalam', 'باسلام'],
            'digikala'     => ['digikala', 'دیجی'],
            'torob'        => ['torob', 'ترب'],
            'in_person'    => ['cod', 'cash', 'in_person', 'حضوری', 'نقدی', 'درب'],
            'pos'          => ['pos', 'cardreader', 'کارتخوان', 'pax', 'pos_'],
        ];

        foreach ($map as $channel => $hints) {
            foreach ($hints as $h) {
                if (str_contains($hay, $h)) return $channel;
            }
        }
        return null;
    }

    protected function fromText(string $text): ?string
    {
        if (trim($text) === '') return null;
        $hay = strtolower($text);
        $map = [
            'basalam'   => ['basalam', 'باسلام', 'bslm'],
            'digikala'  => ['digikala', 'دیجی‌کالا', 'دیجی کالا'],
            'torob'     => ['torob', 'ترب', 'قیمت‌یاب'],
            'divar'     => ['divar', 'دیوار'],
            'sheypoor'  => ['sheypoor', 'شیپور'],
            'instagram' => ['instagram', 'اینستاگرام', 'اینستا', 'دایرکت'],
            'telegram'  => ['telegram', 'تلگرام'],
            'whatsapp'  => ['whatsapp', 'واتساپ', 'واتس'],
            'eitaa'     => ['eitaa', 'ایتا'],
            'zibal'     => ['zibal', 'زیبال'],
            'sadad'     => ['sadad', 'سداد'],
            'zarinpal'  => ['zarinpal', 'زرین‌پال', 'زرین پال'],
            'phone'     => ['phone', 'تلفن', 'تماس'],
            'in_person' => ['حضوری', 'مغازه', 'در محل'],
        ];
        foreach ($map as $channel => $hints) {
            foreach ($hints as $h) {
                if (str_contains($hay, $h)) return $channel;
            }
        }
        return null;
    }

    /**
     * برای استفاده در batch — روی همه سفارشات خالی اعمال می‌کند
     */
    public function backfill(bool $force = false): array
    {
        $stats = [];
        $q = Order::query();
        if (!$force) {
            $q->where(function ($x) {
                $x->whereNull('sales_channel')
                  ->orWhere('sales_channel', '')
                  ->orWhere('sales_channel', 'website');
            });
        }

        $q->chunkById(200, function ($orders) use (&$stats) {
            foreach ($orders as $o) {
                $ch = $this->detect($o);
                if ($ch && $ch !== $o->sales_channel) {
                    $o->sales_channel = $ch;
                    $o->saveQuietly();
                    $stats[$ch] = ($stats[$ch] ?? 0) + 1;
                }
            }
        });

        return $stats;
    }
}
