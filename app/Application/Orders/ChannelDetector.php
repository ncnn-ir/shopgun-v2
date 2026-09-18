<?php

namespace App\Application\Orders;

/**
 * ★ ChannelDetector — تشخیص خودکار کانال فروش از داده ووکامرس
 */
class ChannelDetector
{
    /**
     * تشخیص از payment_method + created_via + customer_note
     */
    public static function detect(array $wcOrder): array
    {
        $paymentMethod = strtolower((string) ($wcOrder['payment_method'] ?? ''));
        $paymentTitle = strtolower((string) ($wcOrder['payment_method_title'] ?? ''));
        $createdVia = strtolower((string) ($wcOrder['created_via'] ?? ''));
        $customerNote = strtolower((string) ($wcOrder['customer_note'] ?? ''));
        $metaData = $wcOrder['meta_data'] ?? [];

        // ۱. باسلام
        if (str_contains($paymentMethod, 'basalam')
            || str_contains($paymentTitle, 'basalam')
            || str_contains($paymentTitle, 'باسلام')
            || str_contains($customerNote, 'باسلام')) {
            return ['channel' => 'basalam', 'meta' => ['detected_from' => 'basalam_in_payment']];
        }

        // ۲. ترب
        if (str_contains($paymentMethod, 'terb')
            || str_contains($paymentTitle, 'ترب')
            || str_contains($paymentTitle, 'torob')
            || str_contains($customerNote, 'ترب')
            || str_contains($customerNote, 'torob')) {
            return ['channel' => 'terb', 'meta' => ['detected_from' => 'terb']];
        }

        // ۳. زیبال
        if (str_contains($paymentMethod, 'zibal') || str_contains($paymentTitle, 'زیبال')) {
            return ['channel' => 'zibal', 'meta' => ['detected_from' => 'zibal']];
        }

        // ۴. زرین‌پال
        if (str_contains($paymentMethod, 'zarinpal') || str_contains($paymentTitle, 'زرین')) {
            return ['channel' => 'zarinpal', 'meta' => ['detected_from' => 'zarinpal']];
        }

        // ۵. کارت‌به‌کارت / bacs
        if ($paymentMethod === 'bacs' || str_contains($paymentTitle, 'کارت')
            || str_contains($paymentTitle, 'واریز') || str_contains($paymentTitle, 'انتقال')) {
            return ['channel' => 'bank', 'meta' => ['detected_from' => 'bank_transfer']];
        }

        // ۶. پرداخت در محل
        if ($paymentMethod === 'cod' || str_contains($paymentTitle, 'در محل')) {
            return ['channel' => 'cod', 'meta' => ['detected_from' => 'cod']];
        }

        // ۷. اینستاگرام
        if (str_contains($createdVia, 'instagram') || str_contains($customerNote, 'اینستاگرام')) {
            return ['channel' => 'instagram', 'meta' => ['detected_from' => 'instagram']];
        }

        // ۸. تلگرام
        if (str_contains($createdVia, 'telegram') || str_contains($customerNote, 'تلگرام')) {
            return ['channel' => 'telegram', 'meta' => ['detected_from' => 'telegram']];
        }

        // ۹. بررسی meta_data برای کانال
        foreach ($metaData as $meta) {
            $key = strtolower((string) ($meta['key'] ?? ''));
            $val = strtolower((string) ($meta['value'] ?? ''));

            if (str_contains($key, 'basalam') || str_contains($val, 'basalam')) {
                return ['channel' => 'basalam', 'meta' => ['detected_from' => 'meta_' . $key]];
            }
            if (str_contains($key, 'terb') || str_contains($key, 'torob')) {
                return ['channel' => 'terb', 'meta' => ['detected_from' => 'meta_' . $key]];
            }
        }

        // ۱۰. از created_via checkout → website
        if (str_contains($createdVia, 'checkout') || str_contains($createdVia, 'api')) {
            return ['channel' => 'website', 'meta' => ['detected_from' => 'checkout']];
        }

        // پیش‌فرض
        return ['channel' => 'website', 'meta' => ['detected_from' => 'default']];
    }

    /**
     * استخراج اطلاعات متفرقه از سفارش (فقط موارد مفید)
     */
    public static function extractMeta(array $wcOrder): array
    {
        $meta = [];
        $metaData = $wcOrder['meta_data'] ?? [];

        foreach ($metaData as $m) {
            $key = (string) ($m['key'] ?? '');
            $val = $m['value'] ?? null;

            // فقط کلیدهای مفید
            if (in_array($key, [
                'billing_phone', 'shipping_phone',
                '_billing_national_code', 'کد ملی',
                '_shipping_city', '_shipping_state',
                'basalam_order_id', 'torob_order_id',
                '_payment_verification_status',
                '_transaction_id',
            ], true) || str_contains($key, 'basalam') || str_contains($key, 'torob')) {
                $meta[$key] = is_string($val) ? mb_substr($val, 0, 200) : $val;
            }
        }

        return $meta;
    }
}
