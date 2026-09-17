<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('stones', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->string('en')->nullable();
            $table->string('origin')->nullable();
            $table->string('origin_en')->nullable();
            $table->string('flag', 4)->nullable();
            $table->string('balloon')->nullable();
            $table->string('icon')->default('💎');
            $table->string('png_path')->nullable();
            $table->boolean('is_active')->default(true);
            $table->integer('sort_order')->default(0);
            $table->timestamps();
        });
    }

    public function down(): void { Schema::dropIfExists('stones'); }
};
