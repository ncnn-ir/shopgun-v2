<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('certificates', function (Blueprint $table) {
            if (!Schema::hasColumn('certificates', 'design_data')) {
                $table->json('design_data')->nullable()->after('image_url');
            }
            if (!Schema::hasColumn('certificates', 'image_url')) {
                $table->string('image_url', 500)->nullable()->after('image');
            }
        });
    }

    public function down(): void
    {
        Schema::table('certificates', function (Blueprint $table) {
            if (Schema::hasColumn('certificates', 'design_data')) {
                $table->dropColumn('design_data');
            }
            if (Schema::hasColumn('certificates', 'image_url')) {
                $table->dropColumn('image_url');
            }
        });
    }
};
