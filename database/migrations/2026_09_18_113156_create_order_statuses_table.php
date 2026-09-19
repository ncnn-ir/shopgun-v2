<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        if (Schema::hasTable('order_statuses')) return;

        Schema::create('order_statuses', function (Blueprint $table) {
            $table->id();
            $table->string('slug')->unique();          // pending, processing, completed, ...
            $table->string('title');                    // نام فارسی
            $table->string('color')->default('gray');   // رنگ برچسب
            $table->boolean('is_active')->default(true);        // نمایش داده شود
            $table->boolean('should_import')->default(true);    // در ایمپورت وارد شود
            $table->boolean('should_count_sales')->default(true); // در گزارش فروش
            $table->integer('sort_order')->default(0);
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('order_statuses');
    }
};
