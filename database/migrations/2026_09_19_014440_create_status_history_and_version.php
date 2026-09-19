<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        if (!Schema::hasTable('order_status_history')) {
            Schema::create('order_status_history', function (Blueprint $table) {
                $table->id();
                $table->foreignId('order_id')->constrained('orders')->cascadeOnDelete();
                $table->string('from_status', 40)->nullable();
                $table->string('to_status', 40)->index();
                $table->text('note')->nullable();
                $table->foreignId('changed_by')->nullable();
                $table->timestamp('changed_at')->useCurrent();
                $table->timestamps();
                $table->index(['order_id', 'changed_at']);
            });
        }

        if (!Schema::hasTable('app_version_info')) {
            Schema::create('app_version_info', function (Blueprint $table) {
                $table->id();
                $table->string('version', 30);
                $table->string('title')->nullable();
                $table->text('changelog')->nullable();
                $table->timestamp('released_at')->nullable();
                $table->timestamps();
            });
        }
    }

    public function down(): void
    {
        Schema::dropIfExists('app_version_info');
        Schema::dropIfExists('order_status_history');
    }
};
