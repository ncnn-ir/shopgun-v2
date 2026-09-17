<?php

namespace App\Support;

class PersianNumber
{
    protected static array $en = ['0','1','2','3','4','5','6','7','8','9'];
    protected static array $fa = ['۰','۱','۲','۳','۴','۵','۶','۷','۸','۹'];
    protected static array $ar = ['٠','١','٢','٣','٤','٥','٦','٧','٨','٩'];

    /**
     * تبدیل اعداد انگلیسی → فارسی
     */
    public static function toFa($value): string
    {
        if ($value === null || $value === '') return '';
        return str_replace(self::$en, self::$fa, (string) $value);
    }

    /**
     * تبدیل اعداد فارسی/عربی → انگلیسی
     */
    public static function toEn($value): string
    {
        if ($value === null || $value === '') return '';
        $value = str_replace(self::$fa, self::$en, (string) $value);
        $value = str_replace(self::$ar, self::$en, $value);
        return $value;
    }

    /**
     * عدد با جداکننده هزارگان فارسی
     */
    public static function money($value): string
    {
        return self::toFa(number_format((float) $value));
    }

    /**
     * فقط رقم‌های انگلیسی
     */
    public static function digitsOnly($value): string
    {
        return preg_replace('/[^0-9]/', '', self::toEn($value));
    }

    /**
     * عدد اعشاری با حذف صفر اضافه
     * مثال: 1.00 → 1 ، 1.50 → 1.5
     */
    public static function clean($value, int $decimals = 2): string
    {
        $n = (float) self::toEn($value);
        $s = number_format($n, $decimals, '.', '');
        $s = rtrim(rtrim($s, '0'), '.');
        return $s === '' ? '0' : $s;
    }
}
