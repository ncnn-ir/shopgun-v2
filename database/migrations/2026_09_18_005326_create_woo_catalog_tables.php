<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        // ═══ woo_categories ═══
        if (!Schema::hasTable('woo_categories')) {
            Schema::create('woo_categories', function (Blueprint $table) {
                $table->id();
                $table->unsignedBigInteger('woo_id')->unique()->index();
                $table->unsignedBigInteger('parent_woo_id')->nullable()->index();
                $table->string('name');
                $table->string('slug')->index();
                $table->text('description')->nullable();
                $table->unsignedInteger('count')->default(0);
                $table->json('image')->nullable();
                $table->integer('menu_order')->default(0);
                $table->timestamp('synced_at')->nullable();
                $table->timestamps();
            });
        }

        // ═══ woo_attributes ═══
        if (!Schema::hasTable('woo_attributes')) {
            Schema::create('woo_attributes', function (Blueprint $table) {
                $table->id();
                $table->unsignedBigInteger('woo_id')->unique()->index();
                $table->string('name');
                $table->string('slug')->unique()->index();
                $table->string('type', 30)->default('select');
                $table->string('order_by', 30)->default('menu_order');
                $table->boolean('has_archives')->default(false);
                $table->timestamp('synced_at')->nullable();
                $table->timestamps();
            });
        }

        // ═══ woo_attribute_terms ═══
        if (!Schema::hasTable('woo_attribute_terms')) {
            Schema::create('woo_attribute_terms', function (Blueprint $table) {
                $table->id();
                $table->unsignedBigInteger('woo_id')->unique()->index();
                $table->unsignedBigInteger('attribute_woo_id')->index();
                $table->string('name');
                $table->string('slug')->index();
                $table->text('description')->nullable();
                $table->unsignedInteger('count')->default(0);
                $table->integer('menu_order')->default(0);
                $table->timestamp('synced_at')->nullable();
                $table->timestamps();

                $table->index(['attribute_woo_id', 'name']);
            });
        }

        // ═══ woo_users ═══
        if (!Schema::hasTable('woo_users')) {
            Schema::create('woo_users', function (Blueprint $table) {
                $table->id();
                $table->unsignedBigInteger('woo_id')->unique()->index();
                $table->string('name');
                $table->string('slug')->nullable();
                $table->string('email')->nullable();
                $table->json('roles')->nullable();
                $table->timestamp('synced_at')->nullable();
                $table->timestamps();
            });
        }

        // ═══ product_identity — نگاشت SKU مرکزی ═══
        if (!Schema::hasTable('product_identities')) {
            Schema::create('product_identities', function (Blueprint $table) {
                $table->id();
                $table->string('sku', 100)->unique()->index();
                $table->unsignedBigInteger('local_product_id')->nullable()->index();
                $table->unsignedBigInteger('woo_product_id')->nullable()->index();
                $table->string('canonical_name')->nullable();
                $table->string('canonical_slug')->nullable();
                $table->decimal('last_known_price', 15, 2)->nullable();
                $table->decimal('last_known_weight', 10, 3)->nullable();
                $table->json('last_known_woo_data')->nullable();
                $table->unsignedInteger('sync_count')->default(0);
                $table->timestamp('last_synced_at')->nullable();
                $table->timestamps();
            });
        }
    }

    public function down(): void
    {
        Schema::dropIfExists('product_identities');
        Schema::dropIfExists('woo_users');
        Schema::dropIfExists('woo_attribute_terms');
        Schema::dropIfExists('woo_attributes');
        Schema::dropIfExists('woo_categories');
    }
};
