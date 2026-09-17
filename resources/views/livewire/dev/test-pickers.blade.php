<div class="p-4 md:p-6 max-w-4xl mx-auto space-y-6">
    <div class="flex items-center gap-3 mb-2">
        <h1 class="text-xl md:text-2xl font-bold">🧪 تست Pickerها</h1>
        <span class="badge badge-warning">فاز ۱</span>
    </div>

    <div class="alert alert-info py-2 text-sm">
        <span>این صفحه برای تست کامپوننت‌های جدید است. بعد از تأیید، این پیکرها در فرم سفارش جایگزین می‌شوند.</span>
    </div>

    {{-- ═══ Customer Picker ═══ --}}
    <div class="card bg-base-100 shadow border">
        <div class="card-body">
            <h2 class="font-bold text-base mb-3">👤 انتخاب مشتری</h2>
            <livewire:components.customer-picker
                :customer-id="$customerId"
                event-prefix="customer" />

            @if($customerId)
                <div class="mt-4 p-3 bg-success/5 border border-success/30 rounded-lg">
                    <div class="text-xs font-bold mb-2 text-success">✓ مشتری انتخاب شده (ID: {{ $customerId }})</div>
                    <pre class="text-[10px] bg-base-200 p-2 rounded overflow-x-auto" dir="ltr">{{ json_encode($customerData, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT) }}</pre>
                </div>
            @endif
        </div>
    </div>

    {{-- ═══ Product Picker ═══ --}}
    <div class="card bg-base-100 shadow border">
        <div class="card-body">
            <h2 class="font-bold text-base mb-3">🛍️ انتخاب محصولات</h2>
            <livewire:components.product-picker event-prefix="products" />

            @if(count($cart) > 0)
                <div class="mt-4 p-3 bg-primary/5 border border-primary/30 rounded-lg">
                    <div class="text-xs font-bold mb-2 text-primary">🛒 سبد ({{ count($cart) }} آیتم)</div>
                    <pre class="text-[10px] bg-base-200 p-2 rounded overflow-x-auto" dir="ltr">{{ json_encode($cart, JSON_UNESCAPED_UNICODE | JSON_PRETTY_PRINT) }}</pre>
                    <div class="text-sm font-bold mt-2 text-primary">
                        جمع: {{ number_format($total) }} تومان
                    </div>
                </div>
            @endif
        </div>
    </div>
</div>
