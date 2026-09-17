<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        if (Schema::hasTable('customer_phones')) return;

        Schema::create('customer_phones', function (Blueprint $table) {
            $table->id();
            $table->foreignId('customer_id')->constrained()->cascadeOnDelete();
            $table->string('phone', 20)->index();
            $table->string('label', 50)->nullable(); // موبایل اصلی، منزل، محل کار
            $table->boolean('is_primary')->default(false);
            $table->timestamp('verified_at')->nullable();
            $table->string('note', 255)->nullable();
            $table->timestamps();

            $table->unique(['customer_id', 'phone']);
            $table->index(['phone', 'is_primary']);
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('customer_phones');
    }
};
