<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::table('orders', function (Blueprint $table) {
            if (! Schema::hasColumn('orders', 'tracking_code')) {
                $table->string('tracking_code')->nullable()->index()->after('postal_code');
                $table->string('carrier')->nullable()->after('tracking_code');
                $table->string('shipping_status')->nullable()->after('carrier');
                $table->json('shipping_events')->nullable()->after('shipping_status');
                $table->timestamp('shipped_at')->nullable()->after('shipping_events');
                $table->timestamp('delivered_at')->nullable()->after('shipped_at');
            }
        });
    }

    public function down(): void
    {
        Schema::table('orders', function (Blueprint $table) {
            $table->dropColumn(['tracking_code','carrier','shipping_status','shipping_events','shipped_at','delivered_at']);
        });
    }
};
