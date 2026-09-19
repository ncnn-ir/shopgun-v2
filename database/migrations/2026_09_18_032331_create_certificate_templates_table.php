<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        if (Schema::hasTable('certificate_templates')) return;

        Schema::create('certificate_templates', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->string('slug', 100)->unique()->index();
            $table->text('description')->nullable();
            $table->string('version', 20)->default('1.0');
            $table->string('status', 30)->default('draft')->index();
            // draft | published | archived

            $table->json('design_data')->nullable();        // Fabric.js JSON
            $table->json('sizes')->nullable();              // {width, height, img_w, ...}
            $table->json('logos')->nullable();              // [{path, position, size}]
            $table->json('colors')->nullable();             // palette

            $table->boolean('is_default')->default(false)->index();
            $table->boolean('is_global')->default(false)->index();

            $table->unsignedInteger('certificates_count')->default(0);
            $table->foreignId('created_by')->nullable();

            $table->timestamp('published_at')->nullable();
            $table->timestamp('archived_at')->nullable();
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('certificate_templates');
    }
};
