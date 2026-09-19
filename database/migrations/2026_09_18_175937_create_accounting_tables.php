<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void {
        if (!Schema::hasTable('accounting_parties')) {
            Schema::create('accounting_parties', function (Blueprint $table) {
                $table->id();
                $table->string('type', 32)->default('other')->index();
                $table->string('name');
                $table->string('company')->nullable();
                $table->string('phone', 32)->nullable()->index();
                $table->string('national_code', 32)->nullable();
                $table->string('card_number', 32)->nullable();
                $table->string('iban', 64)->nullable();
                $table->text('notes')->nullable();
                $table->boolean('is_active')->default(true);
                $table->timestamps();
            });
        }
        if (!Schema::hasTable('accounting_transactions')) {
            Schema::create('accounting_transactions', function (Blueprint $table) {
                $table->id();
                $table->unsignedBigInteger('party_id')->nullable()->index();
                $table->string('type', 16)->index();
                $table->decimal('amount', 18, 0);
                $table->string('description')->nullable();
                $table->string('reference', 128)->nullable();
                $table->dateTime('occurred_at')->index();
                $table->string('source', 32)->default('manual');
                $table->text('raw_sms')->nullable();
                $table->json('meta')->nullable();
                $table->unsignedBigInteger('user_id')->nullable();
                $table->timestamps();
            });
        }
        if (!Schema::hasTable('accounting_sms_inbox')) {
            Schema::create('accounting_sms_inbox', function (Blueprint $table) {
                $table->id();
                $table->text('raw_text');
                $table->json('parsed_data')->nullable();
                $table->string('status', 32)->default('pending')->index();
                $table->unsignedBigInteger('transaction_id')->nullable();
                $table->unsignedBigInteger('party_id')->nullable();
                $table->timestamps();
            });
        }
    }
    public function down(): void {
        Schema::dropIfExists('accounting_sms_inbox');
        Schema::dropIfExists('accounting_transactions');
        Schema::dropIfExists('accounting_parties');
    }
};
