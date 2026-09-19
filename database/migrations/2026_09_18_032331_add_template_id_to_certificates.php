<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        if (!Schema::hasColumn('certificates', 'template_id')) {
            Schema::table('certificates', function (Blueprint $table) {
                $table->foreignId('template_id')->nullable()->after('id')->constrained('certificate_templates')->nullOnDelete();
            });
        }
    }

    public function down(): void
    {
        if (Schema::hasColumn('certificates', 'template_id')) {
            Schema::table('certificates', function (Blueprint $table) {
                $table->dropForeign(['template_id']);
                $table->dropColumn('template_id');
            });
        }
    }
};
