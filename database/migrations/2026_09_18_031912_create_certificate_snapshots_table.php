<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        // ★ certificate_snapshots — نگه‌داشتن تاریخچه تغییرات
        if (!Schema::hasTable('certificate_snapshots')) {
            Schema::create('certificate_snapshots', function (Blueprint $table) {
                $table->id();
                $table->foreignId('certificate_id')->constrained('certificates')->cascadeOnDelete();
                $table->string('event', 40); // issued | updated | reprinted | design_changed
                $table->string('sku', 100)->nullable()->index();
                $table->string('stone_name')->nullable();
                $table->string('stone_en')->nullable();
                $table->string('metal')->nullable();
                $table->string('metal_carat')->nullable();
                $table->decimal('length', 8, 2)->nullable();
                $table->decimal('width', 8, 2)->nullable();
                $table->decimal('weight', 10, 3)->nullable();
                $table->integer('brilliant')->nullable();
                $table->string('image_path')->nullable();
                $table->string('image_url')->nullable();
                $table->json('product_data')->nullable();
                $table->json('meta')->nullable();
                $table->foreignId('changed_by')->nullable();
                $table->timestamp('captured_at')->useCurrent();
                $table->timestamps();

                $table->index(['certificate_id', 'captured_at']);
            });
        }
    }

    public function down(): void
    {
        Schema::dropIfExists('certificate_snapshots');
    }
};
