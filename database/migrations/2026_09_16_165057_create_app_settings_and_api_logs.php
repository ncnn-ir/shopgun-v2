<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        if (!Schema::hasTable('app_settings')) {
            Schema::create('app_settings', function (Blueprint $table) {
                $table->id();
                $table->string('key', 100)->unique();
                $table->text('value')->nullable();
                $table->string('group', 50)->default('general');
                $table->string('type', 30)->default('string'); // string|int|bool|json
                $table->timestamps();
                $table->index('group');
            });
        }

        if (!Schema::hasTable('api_logs')) {
            Schema::create('api_logs', function (Blueprint $table) {
                $table->id();
                $table->string('service', 50)->index();      // woocommerce | server | ...
                $table->string('method', 10);                 // GET|POST|...
                $table->text('url');
                $table->integer('status_code')->nullable();
                $table->integer('duration_ms')->nullable();
                $table->text('request_body')->nullable();
                $table->longText('response_body')->nullable();
                $table->text('error')->nullable();
                $table->integer('items_count')->nullable();
                $table->foreignId('user_id')->nullable();
                $table->timestamp('created_at')->useCurrent();
                $table->index(['service', 'created_at']);
            });
        }
    }

    public function down(): void
    {
        Schema::dropIfExists('api_logs');
        Schema::dropIfExists('app_settings');
    }
};
