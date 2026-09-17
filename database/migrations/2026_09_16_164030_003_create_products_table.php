<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        if (Schema::hasTable('products')) return;

        Schema::create('products', function (Blueprint $table) {
            $table->id();

            // شناسه‌ها
            $table->string('sku', 100)->unique()->index();
            $table->unsignedBigInteger('wc_id')->nullable()->unique()->index();
            $table->string('barcode', 100)->nullable()->index();

            // اطلاعات اصلی
            $table->string('name', 255);
            $table->string('slug', 255)->nullable();
            $table->text('description')->nullable();
            $table->text('short_description')->nullable();

            // قیمت
            $table->decimal('price', 15, 2)->default(0);
            $table->decimal('regular_price', 15, 2)->nullable();
            $table->decimal('sale_price', 15, 2)->nullable();

            // موجودی
            $table->integer('stock_quantity')->nullable();
            $table->string('stock_status', 30)->default('instock');

            // ابعاد
            $table->decimal('weight', 10, 3)->nullable();
            $table->decimal('length', 10, 2)->nullable();
            $table->decimal('width', 10, 2)->nullable();
            $table->decimal('height', 10, 2)->nullable();

            // ارتباط با سنگ/فلز
            $table->foreignId('stone_id')->nullable()->constrained('stones')->nullOnDelete();
            $table->foreignId('metal_id')->nullable()->constrained('metals')->nullOnDelete();

            // تصاویر
            $table->string('image_path', 500)->nullable();
            $table->string('image_url', 500)->nullable();

            // JSON fields
            $table->json('gallery')->nullable();
            $table->json('categories')->nullable();
            $table->json('attributes')->nullable();
            $table->json('tags')->nullable();
            $table->json('wc_data')->nullable();       // خام از WooCommerce

            // وضعیت
            $table->boolean('is_active')->default(true);
            $table->timestamp('synced_at')->nullable();

            $table->timestamps();

            $table->index(['is_active', 'stock_status']);
            $table->index('name');
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('products');
    }
};
