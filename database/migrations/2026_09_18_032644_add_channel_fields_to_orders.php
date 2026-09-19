<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration
{
    public function up(): void
    {
        Schema::table('orders', function (Blueprint $table) {
            if (!Schema::hasColumn('orders', 'payment_method')) {
                $table->string('payment_method', 60)->nullable()->index()->after('channel_id');
            }
            if (!Schema::hasColumn('orders', 'payment_title')) {
                $table->string('payment_title')->nullable()->after('payment_method');
            }
            if (!Schema::hasColumn('orders', 'sales_channel')) {
                $table->string('sales_channel', 40)->nullable()->index()->after('payment_title');
            }
            if (!Schema::hasColumn('orders', 'channel_metadata')) {
                $table->json('channel_metadata')->nullable()->after('sales_channel');
            }
            if (!Schema::hasColumn('orders', 'customer_note')) {
                $table->text('customer_note')->nullable()->after('notes');
            }
            if (!Schema::hasColumn('orders', 'supply_status')) {
                $table->string('supply_status', 40)->default('default')->index()->after('status');
            }
            if (!Schema::hasColumn('orders', 'woo_status')) {
                $table->string('woo_status', 40)->nullable()->index()->after('status');
            }
        });
    }

    public function down(): void
    {
        Schema::table('orders', function (Blueprint $table) {
            foreach ([
                'payment_method', 'payment_title', 'sales_channel',
                'channel_metadata', 'customer_note', 'supply_status', 'woo_status',
            ] as $col) {
                if (Schema::hasColumn('orders', $col)) $table->dropColumn($col);
            }
        });
    }
};
