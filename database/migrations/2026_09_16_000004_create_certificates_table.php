<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('certificates', function (Blueprint $table) {
            $table->id();
            $table->string('code')->unique()->index();
            $table->string('serial')->unique()->index();
            $table->string('sku')->nullable()->index();
            $table->string('stone_name');
            $table->string('stone_en')->nullable();
            $table->string('stone_origin')->nullable();
            $table->string('stone_flag', 4)->nullable();
            $table->string('metal');
            $table->string('metal_en')->nullable();
            $table->string('metal_carat')->nullable();
            $table->decimal('length', 8, 2)->default(0);
            $table->decimal('width', 8, 2)->default(0);
            $table->decimal('weight', 10, 3)->default(0);
            $table->integer('brilliant')->default(0);
            $table->string('image_path')->nullable();
            $table->foreignId('order_id')->nullable()->constrained('orders')->nullOnDelete();
            $table->foreignId('customer_id')->nullable()->constrained('customers')->nullOnDelete();
            $table->timestamp('issued_at')->nullable();
            $table->json('design_data')->nullable();
            $table->json('meta')->nullable();
            $table->timestamps();
            $table->index('issued_at');
        });
    }

    public function down(): void { Schema::dropIfExists('certificates'); }
};
