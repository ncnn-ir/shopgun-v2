<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        if (Schema::hasTable('bulk_product_logs')) return;

        Schema::create('bulk_product_logs', function (Blueprint $table) {
            $table->id();
            $table->string('sku', 100)->index();
            $table->unsignedBigInteger('woo_id')->nullable()->index();
            $table->string('name')->nullable();
            $table->string('slug')->nullable();
            $table->decimal('regular_price', 15, 2)->nullable();
            $table->decimal('sale_price', 15, 2)->nullable();
            $table->decimal('weight', 10, 3)->nullable();
            $table->integer('stock_quantity')->nullable();
            $table->string('status', 30)->default('draft')->index();
            $table->text('error_message')->nullable();
            $table->json('payload')->nullable();
            $table->json('response')->nullable();
            $table->string('batch_id', 50)->nullable()->index();
            $table->timestamp('sent_at')->nullable();
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('bulk_product_logs');
    }
};
