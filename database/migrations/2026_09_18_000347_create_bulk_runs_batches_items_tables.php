<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        // ═══ bulk_runs ═══
        if (!Schema::hasTable('bulk_runs')) {
            Schema::create('bulk_runs', function (Blueprint $table) {
                $table->id();
                $table->foreignId('user_id')->nullable()->index();
                $table->string('source', 30)->default('manual'); // manual | csv | json
                $table->string('mode', 20)->default('create');   // create | update | upsert
                $table->string('status', 30)->default('draft')->index();
                // draft | validating | preview | queued | processing | completed | failed | cancelled
                $table->unsignedInteger('total_items')->default(0);
                $table->unsignedInteger('validated_items')->default(0);
                $table->unsignedInteger('queued_items')->default(0);
                $table->unsignedInteger('processing_items')->default(0);
                $table->unsignedInteger('success_items')->default(0);
                $table->unsignedInteger('failed_items')->default(0);
                $table->json('settings_snapshot')->nullable();
                $table->text('last_error')->nullable();
                $table->timestamp('started_at')->nullable();
                $table->timestamp('finished_at')->nullable();
                $table->timestamps();

                $table->index(['status', 'created_at']);
            });
        }

        // ═══ bulk_batches ═══
        if (!Schema::hasTable('bulk_batches')) {
            Schema::create('bulk_batches', function (Blueprint $table) {
                $table->id();
                $table->foreignId('run_id')->constrained('bulk_runs')->cascadeOnDelete();
                $table->unsignedInteger('sequence')->default(1);
                $table->string('status', 30)->default('pending')->index();
                // pending | processing | completed | failed
                $table->unsignedInteger('attempts')->default(0);
                $table->unsignedInteger('items_count')->default(0);
                $table->unsignedInteger('success_count')->default(0);
                $table->unsignedInteger('failed_count')->default(0);
                $table->timestamp('started_at')->nullable();
                $table->timestamp('finished_at')->nullable();
                $table->text('error')->nullable();
                $table->timestamps();

                $table->index(['run_id', 'sequence']);
            });
        }

        // ═══ bulk_items ═══
        if (!Schema::hasTable('bulk_items')) {
            Schema::create('bulk_items', function (Blueprint $table) {
                $table->id();
                $table->foreignId('run_id')->constrained('bulk_runs')->cascadeOnDelete();
                $table->foreignId('batch_id')->nullable()->constrained('bulk_batches')->nullOnDelete();
                $table->string('sku', 100)->index();
                $table->unsignedBigInteger('woo_product_id')->nullable()->index();
                $table->string('status', 30)->default('pending')->index();
                // pending | validating | valid | invalid | queued | processing
                // success | draft_created | failed | skipped
                $table->unsignedInteger('attempt')->default(0);
                $table->string('idempotency_key', 100)->nullable()->index();
                $table->string('payload_hash', 64)->nullable();
                $table->json('input_data')->nullable();
                $table->json('request_payload')->nullable();
                $table->json('response_payload')->nullable();
                $table->string('error_code', 50)->nullable();
                $table->text('error_message')->nullable();
                $table->json('validation_warnings')->nullable();
                $table->json('diff_data')->nullable();
                $table->timestamp('started_at')->nullable();
                $table->timestamp('finished_at')->nullable();
                $table->timestamps();

                $table->index(['run_id', 'status']);
                $table->unique(['run_id', 'sku'], 'bulk_items_run_sku_unique');
            });
        }
    }

    public function down(): void
    {
        Schema::dropIfExists('bulk_items');
        Schema::dropIfExists('bulk_batches');
        Schema::dropIfExists('bulk_runs');
    }
};
