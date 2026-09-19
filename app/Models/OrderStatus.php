<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class OrderStatus extends Model
{
    protected $fillable = [
        'slug', 'title', 'color', 'is_active',
        'should_import', 'should_count_sales', 'sort_order',
    ];

    protected $casts = [
        'is_active'          => 'bool',
        'should_import'      => 'bool',
        'should_count_sales' => 'bool',
        'sort_order'         => 'int',
    ];

    public const COLORS = [
        'gray'    => 'خاکستری',
        'amber'   => 'کهربایی',
        'blue'    => 'آبی',
        'green'   => 'سبز',
        'red'     => 'قرمز',
        'purple'  => 'بنفش',
        'orange'  => 'نارنجی',
        'cyan'    => 'فیروزه‌ای',
    ];

    /** مقادیر پیش‌فرض ووکامرس */
    public static function defaults(): array
    {
        return [
            ['pending',    'در انتظار پرداخت', 'amber',  1,  1,  0, 10],
            ['processing', 'در حال انجام',     'blue',   1,  1,  1, 20],
            ['on-hold',    'در انتظار بررسی',  'gray',   1,  1,  0, 30],
            ['completed',  'تکمیل شده',        'green',  1,  1,  1, 40],
            ['cancelled',  'لغو شده',          'red',    1,  1,  0, 50],
            ['refunded',   'مرجوع شده',        'purple', 1,  1,  0, 60],
            ['failed',     'ناموفق',           'red',    0,  0,  0, 70],
            ['trash',      'زباله‌دان',         'gray',   0,  0,  0, 80],
        ];
    }
}
