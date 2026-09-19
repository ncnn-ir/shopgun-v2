<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::table('orders', function (Blueprint $table) {
            $cols = [
                'supply_status'             => fn($t) => $t->string('supply_status')->nullable()->index(),
                'supply_found_at'           => fn($t) => $t->timestamp('supply_found_at')->nullable(),
                'supply_found_by'           => fn($t) => $t->unsignedBigInteger('supply_found_by')->nullable(),
                'supply_notes'              => fn($t) => $t->text('supply_notes')->nullable(),
                'delivered_to_shipping_at'  => fn($t) => $t->timestamp('delivered_to_shipping_at')->nullable(),
                'delivered_to_shipping_by'  => fn($t) => $t->unsignedBigInteger('delivered_to_shipping_by')->nullable(),
                'paid_at'                   => fn($t) => $t->timestamp('paid_at')->nullable(),
                'shipped_at'                => fn($t) => $t->timestamp('shipped_at')->nullable(),
                'delivered_at'              => fn($t) => $t->timestamp('delivered_at')->nullable(),
                'shipping_lat'              => fn($t) => $t->decimal('shipping_lat', 10, 7)->nullable(),
                'shipping_lng'              => fn($t) => $t->decimal('shipping_lng', 10, 7)->nullable(),
                'shipping_city'             => fn($t) => $t->string('shipping_city')->nullable(),
                'shipping_province'         => fn($t) => $t->string('shipping_province')->nullable(),
                'shipping_address'          => fn($t) => $t->text('shipping_address')->nullable(),
            ];
            foreach ($cols as $name => $def) {
                if (!Schema::hasColumn('orders', $name)) {
                    $def($table);
                }
            }
        });
    }

    public function down(): void
    {
        $cols = [
            'supply_status','supply_found_at','supply_found_by','supply_notes',
            'delivered_to_shipping_at','delivered_to_shipping_by',
            'paid_at','shipped_at','delivered_at',
            'shipping_lat','shipping_lng','shipping_city','shipping_province','shipping_address',
        ];
        Schema::table('orders', function (Blueprint $table) use ($cols) {
            foreach ($cols as $c) {
                if (Schema::hasColumn('orders', $c)) {
                    $table->dropColumn($c);
                }
            }
        });
    }
};
