<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        // ═══ sync_runs ═══
        if (!Schema::hasTable('sync_runs')) {
            Schema::create('sync_runs', function (Blueprint $table) {
                $table->id();
                $table->foreignId('user_id')->nullable()->index();
                $table->string('type', 40)->index(); // products | orders | customers | catalog | media | full
                $table->string('mode', 20)->default('full'); // full | incremental
                $table->string('status', 30)->default('pending')->index();
                // pending | running | completed | failed | cancelled

                $table->unsignedInteger('total_items')->default(0);
                $table->unsignedInteger('processed_items')->default(0);
                $table->unsignedInteger('created_items')->default(0);
                $table->unsignedInteger('updated_items')->default(0);
                $table->unsignedInteger('failed_items')->default(0);
                $table->unsignedInteger('skipped_items')->default(0);

                $table->json('options')->nullable();
                $table->text('last_error')->nullable();

                $table->timestamp('started_at')->nullable();
                $table->timestamp('finished_at')->nullable();
                $table->timestamps();

                $table->index(['type', 'status']);
            });
        }

        // ═══ sync_items ═══
        if (!Schema::hasTable('sync_items')) {
            Schema::create('sync_items', function (Blueprint $table) {
                $table->id();
                $table->foreignId('sync_run_id')->constrained('sync_runs')->cascadeOnDelete();
                $table->string('entity_type', 40)->index(); // product | order | customer | category | attribute | term | media
                $table->string('entity_id', 100)->index();  // شناسه خارجی (woo_id یا sku)
                $table->unsignedBigInteger('local_id')->nullable()->index();

                $table->string('status', 30)->default('pending')->index();
                // pending | processing | created | updated | skipped | failed

                $table->string('action', 30)->nullable(); // create | update | skip
                $table->text('error_message')->nullable();
                $table->json('diff_data')->nullable();
                $table->timestamp('started_at')->nullable();
                $table->timestamp('finished_at')->nullable();
                $table->timestamps();

                $table->index(['sync_run_id', 'status']);
            });
        }

        // ═══ woo_media ═══
        if (!Schema::hasTable('woo_media')) {
            Schema::create('woo_media', function (Blueprint $table) {
                $table->id();
                $table->unsignedBigInteger('woo_id')->unique()->index();
                $table->string('filename', 500)->index();
                $table->string('slug')->nullable()->index();
                $table->string('mime_type', 100)->nullable();
                $table->string('source_url', 1000);
                $table->unsignedBigInteger('file_size')->nullable();
                $table->unsignedInteger('width')->nullable();
                $table->unsignedInteger('height')->nullable();
                $table->string('title')->nullable();
                $table->string('alt_text')->nullable();
                $table->json('sizes')->nullable(); // responsive sizes
                $table->json('meta')->nullable();
                $table->timestamp('synced_at')->nullable();
                $table->timestamps();
            });
        }
    }

    public function down(): void
    {
        Schema::dropIfExists('woo_media');
        Schema::dropIfExists('sync_items');
        Schema::dropIfExists('sync_runs');
    }
};
