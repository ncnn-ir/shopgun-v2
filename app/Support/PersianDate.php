<?php

namespace App\Support;

use DateTimeInterface;

class PersianDate
{
    /**
     * تبدیل تاریخ میلادی به شمسی
     *
     * @param  \DateTimeInterface|string|int|null  $date
     * @param  string  $format  Y=سال، m=ماه، d=روز، H=ساعت، i=دقیقه، s=ثانیه
     * @return string
     */
    public static function format($date, string $format = 'Y/m/d H:i'): string
    {
        if ($date === null || $date === '') {
            return '';
        }

        if (is_string($date)) {
            $date = strtotime($date) ?: time();
        }
        if (is_int($date)) {
            $date = new \DateTime('@' . $date);
        }
        if ($date instanceof DateTimeInterface) {
            $gy = (int) $date->format('Y');
            $gm = (int) $date->format('n');
            $gd = (int) $date->format('j');
            $H  = (int) $date->format('G');
            $i  = (int) $date->format('i');
            $s  = (int) $date->format('s');
        } else {
            return '';
        }

        [$jy, $jm, $jd] = self::gregorianToJalali($gy, $gm, $gd);

        $out = '';
        $len = strlen($format);
        for ($k = 0; $k < $len; $k++) {
            $ch = $format[$k];
            $out .= match ($ch) {
                'Y' => (string) $jy,
                'y' => substr((string) $jy, -2),
                'm' => str_pad((string) $jm, 2, '0', STR_PAD_LEFT),
                'n' => (string) $jm,
                'd' => str_pad((string) $jd, 2, '0', STR_PAD_LEFT),
                'j' => (string) $jd,
                'H' => str_pad((string) $H, 2, '0', STR_PAD_LEFT),
                'i' => str_pad((string) $i, 2, '0', STR_PAD_LEFT),
                's' => str_pad((string) $s, 2, '0', STR_PAD_LEFT),
                default => $ch,
            };
        }
        return $out;
    }

    /**
     * تاریخ شمسی به‌صورت «۱۴۰۴/۰۱/۱۵»
     */
    public static function toJalaliString($date): string
    {
        return self::format($date, 'Y/m/d');
    }

    /**
     * تاریخ و ساعت
     */
    public static function toJalaliDateTime($date): string
    {
        return self::format($date, 'Y/m/d H:i');
    }

    /**
     * تبدیل میلادی → شمسی
     * الگوریتم: کد معروف jalaali-js (بدون خطای لپ‌یر)
     */
    public static function gregorianToJalali(int $gy, int $gm, int $gd): array
    {
        $g_d_m = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334];

        if ($gy <= 1600) {
            $jy = 0;
            $gy -= 621;
        } else {
            $jy = 979;
            $gy -= 1600;
        }

        $gy2 = ($gm > 2) ? ($gy + 1) : $gy;
        $days = (365 * $gy)
              + intdiv($gy2 + 3, 4)
              - intdiv($gy2 + 99, 100)
              + intdiv($gy2 + 399, 400)
              - 80
              + $gd
              + $g_d_m[$gm - 1];

        $jy += 33 * intdiv($days, 12053);
        $days %= 12053;
        $jy += 4 * intdiv($days, 1461);
        $days %= 1461;

        if ($days > 365) {
            $jy += intdiv($days - 1, 365);
            $days = ($days - 1) % 365;
        }

        if ($days < 186) {
            $jm = 1 + intdiv($days, 31);
            $jd = 1 + ($days % 31);
        } else {
            $jm = 7 + intdiv($days - 186, 30);
            $jd = 1 + (($days - 186) % 30);
        }

        return [$jy, $jm, $jd];
    }

    /**
     * تبدیل شمسی → میلادی
     */
    public static function jalaliToGregorian(int $jy, int $jm, int $jd): array
    {
        $jy += 1595;
        $days = -355668 + (365 * $jy) + (intdiv($jy, 33) * 8)
              + intdiv(($jy % 33) + 3, 4)
              + $jd
              + (($jm < 7) ? ($jm - 1) * 31 : (($jm - 7) * 30) + 186);

        $gy = 400 * intdiv($days, 146097);
        $days %= 146097;

        if ($days > 36524) {
            $gy += 100 * intdiv(--$days, 36524);
            $days %= 36524;
            if ($days >= 365) $days++;
        }

        $gy += 4 * intdiv($days, 1461);
        $days %= 1461;

        if ($days > 365) {
            $gy += intdiv($days - 1, 365);
            $days = ($days - 1) % 365;
        }

        $gd = $days + 1;
        $sal_a = [0, 31, ($gy % 4 === 0 && $gy % 100 !== 0) || ($gy % 400 === 0) ? 29 : 28,
                  31, 30, 31, 30, 31, 31, 30, 31, 30, 31];
        for ($gm = 0; $gm < 13 && $gd > $sal_a[$gm]; $gm++) {
            $gd -= $sal_a[$gm];
        }

        return [$gy, $gm, $gd];
    }

    /**
     * نام روز هفته
     */
    public static function dayOfWeek($date): string
    {
        $days = ['یکشنبه', 'دوشنبه', 'سه‌شنبه', 'چهارشنبه', 'پنجشنبه', 'جمعه', 'شنبه'];
        $d = is_int($date) ? new \DateTime('@' . $date) : new \DateTime((string) $date);
        return $days[(int) $d->format('w')];
    }

    /**
     * نام ماه شمسی
     */
    public static function monthName(int $jm): string
    {
        return [
            1 => 'فروردین', 2 => 'اردیبهشت', 3 => 'خرداد',
            4 => 'تیر', 5 => 'مرداد', 6 => 'شهریور',
            7 => 'مهر', 8 => 'آبان', 9 => 'آذر',
            10 => 'دی', 11 => 'بهمن', 12 => 'اسفند',
        ][$jm] ?? '';
    }
}
