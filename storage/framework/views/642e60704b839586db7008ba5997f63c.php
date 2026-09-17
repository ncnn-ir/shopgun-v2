<?php $__bladeCompiler = app('blade.compiler'); ?><div dir="rtl" style="padding: 14px">

    
    <div style="background: var(--bg-card, #fff); border: 1px solid var(--border, #e2e8f0); border-radius: 12px; padding: 12px; margin-bottom: 14px;">
        <div style="display: grid; grid-template-columns: 1fr; gap: 10px;">

            <div style="display: grid; grid-template-columns: 2fr 1fr; gap: 10px;">
                <div>
                    <label style="font-size: 11px; font-weight: 700; color: var(--primary); display: block; margin-bottom: 4px;">🔍 جستجو</label>
                    <input type="text" wire:model.live.debounce.400ms="search"
                           placeholder="شماره سفارش، نام مشتری، تلفن..."
                           style="width: 100%; padding: 8px 12px; border: 1.5px solid var(--border); border-radius: 8px; background: var(--bg-soft, #f8fafc); font-family: inherit; font-size: 13px; box-sizing: border-box;">
                </div>
                <div>
                    <label style="font-size: 11px; font-weight: 700; color: var(--primary); display: block; margin-bottom: 4px;">📊 وضعیت</label>
                    <select wire:model.live="filterStatus"
                            style="width: 100%; padding: 8px 12px; border: 1.5px solid var(--border); border-radius: 8px; background: var(--bg-soft, #f8fafc); font-family: inherit; font-size: 13px; box-sizing: border-box;">
                        <option value="">همه</option>
                        <option value="pending">📝 ثبت سفارش</option>
                        <option value="final-check">🔍 چک نهایی</option>
                        <option value="courier">🚚 تحویل مامور</option>
                    </select>
                </div>
            </div>

            <div style="display: grid; grid-template-columns: 1fr 1fr auto; gap: 10px;">
                <div>
                    <label style="font-size: 11px; font-weight: 700; color: var(--primary); display: block; margin-bottom: 4px;">📅 از تاریخ (۱۴۰۳/۰۱/۰۱)</label>
                    <input type="text" wire:model.live="dateFrom" dir="ltr" placeholder="1403/01/01"
                           style="width: 100%; padding: 8px 12px; border: 1.5px solid var(--border); border-radius: 8px; background: var(--bg-soft); font-family: monospace; font-size: 13px; text-align: center; box-sizing: border-box;">
                </div>
                <div>
                    <label style="font-size: 11px; font-weight: 700; color: var(--primary); display: block; margin-bottom: 4px;">📅 تا تاریخ</label>
                    <input type="text" wire:model.live="dateTo" dir="ltr" placeholder="1403/12/29"
                           style="width: 100%; padding: 8px 12px; border: 1.5px solid var(--border); border-radius: 8px; background: var(--bg-soft); font-family: monospace; font-size: 13px; text-align: center; box-sizing: border-box;">
                </div>
                <div style="display: flex; align-items: flex-end; gap: 6px;">
                    <button wire:click="clearFilters" class="btn btn-outline btn-sm" title="پاک کردن">✕</button>
                    <button onclick="Livewire.dispatch('open-order-form')" class="btn btn-primary btn-sm">➕ جدید</button>
                </div>
            </div>
        </div>
    </div>

    
    <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if BLOCK]><![endif]--><?php endif; ?><?php if(count($selected) > 0): ?>
        <div style="background: linear-gradient(135deg, rgba(201,168,76,.15), rgba(201,168,76,.05)); border: 2px dashed var(--gold); border-radius: 12px; padding: 10px 14px; margin-bottom: 12px; display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 8px;">
            <span style="font-weight: 700; color: var(--gold-dark, #b45309);">
                <?php echo e($__bladeCompiler->applyEchoHandler(\App\Support\PersianNumber::toFa(count($selected)))); ?> مورد انتخاب شده
            </span>
            <div style="display: flex; gap: 6px; flex-wrap: wrap;">
                <button wire:click="bulkStatus('pending')" class="btn btn-outline btn-sm">📝 ثبت</button>
                <button wire:click="bulkStatus('final-check')" class="btn btn-outline btn-sm">🔍 چک</button>
                <button wire:click="bulkStatus('courier')" class="btn btn-outline btn-sm">🚚 مامور</button>
                <button wire:click="bulkDelete" wire:confirm="حذف شوند؟" class="btn btn-danger btn-sm">🗑️</button>
                <button wire:click="clearSelection" class="btn btn-ghost btn-sm">✕</button>
            </div>
        </div>
    <?php endif; ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if ENDBLOCK]><![endif]--><?php endif; ?>

    
    <div style="background: var(--bg-card); border: 1px solid var(--border); border-radius: 12px; overflow: hidden;">
        <div style="padding: 12px 16px; background: linear-gradient(135deg, var(--primary), #0d3b5e); color: #fff;">
            <h2 style="margin: 0; font-size: 14px; font-weight: 700;">
                📦 سفارشات
                <span style="background: var(--gold); color: var(--primary); padding: 2px 10px; border-radius: 20px; font-size: 11px; margin-right: 8px;">
                    <?php echo e($__bladeCompiler->applyEchoHandler(\App\Support\PersianNumber::toFa($orders->total()))); ?>

                </span>
            </h2>
        </div>

        <div style="overflow-x: auto;">
            <table style="width: 100%; border-collapse: collapse; font-size: 12px; min-width: 900px;">
                <thead>
                    <tr style="background: var(--bg-soft, #f8fafc);">
                        <th style="padding: 10px; text-align: right; font-weight: 700; color: var(--primary); border-bottom: 2px solid var(--border); font-size: 11px;">
                            <input type="checkbox" onclick="this.checked ? Livewire.dispatch('selectAll') : null" style="accent-color: var(--gold);">
                        </th>
                        <th wire:click="sortBy('order_number')" style="padding: 10px; text-align: right; font-weight: 700; color: var(--primary); border-bottom: 2px solid var(--border); font-size: 11px; cursor: pointer;">
                            # سفارش <?php echo e($__bladeCompiler->applyEchoHandler($sortField === 'order_number' ? ($sortDirection === 'asc' ? '▲' : '▼') : '⇅')); ?>

                        </th>
                        <th wire:click="sortBy('customer_name')" style="padding: 10px; text-align: right; font-weight: 700; color: var(--primary); border-bottom: 2px solid var(--border); font-size: 11px; cursor: pointer;">
                            مشتری <?php echo e($__bladeCompiler->applyEchoHandler($sortField === 'customer_name' ? ($sortDirection === 'asc' ? '▲' : '▼') : '⇅')); ?>

                        </th>
                        <th style="padding: 10px; text-align: right; font-weight: 700; color: var(--primary); border-bottom: 2px solid var(--border); font-size: 11px;">تلفن</th>
                        <th style="padding: 10px; text-align: right; font-weight: 700; color: var(--primary); border-bottom: 2px solid var(--border); font-size: 11px;">محصولات</th>
                        <th style="padding: 10px; text-align: right; font-weight: 700; color: var(--primary); border-bottom: 2px solid var(--border); font-size: 11px;">بیمه</th>
                        <th style="padding: 10px; text-align: right; font-weight: 700; color: var(--primary); border-bottom: 2px solid var(--border); font-size: 11px;">وضعیت</th>
                        <th wire:click="sortBy('created_at')" style="padding: 10px; text-align: right; font-weight: 700; color: var(--primary); border-bottom: 2px solid var(--border); font-size: 11px; cursor: pointer;">
                            تاریخ <?php echo e($__bladeCompiler->applyEchoHandler($sortField === 'created_at' ? ($sortDirection === 'asc' ? '▲' : '▼') : '⇅')); ?>

                        </th>
                        <th style="padding: 10px; text-align: right; font-weight: 700; color: var(--primary); border-bottom: 2px solid var(--border); font-size: 11px;">عملیات</th>
                    </tr>
                </thead>
                <tbody>
                    <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if BLOCK]><![endif]--><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::openLoop(); ?><?php endif; ?><?php $__empty_1 = true; $__currentLoopData = $orders; $__env->addLoop($__currentLoopData); foreach($__currentLoopData as $order): $__env->incrementLoopIndices(); $loop = $__env->getLastLoop(); $__empty_1 = false; ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::startLoopIteration(); ?><?php endif; ?>
                        <tr <?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::$currentLoop['key'] = 'ord-'.e($__bladeCompiler->applyEchoHandler($order->id)).''; ?>wire:key="ord-<?php echo e($__bladeCompiler->applyEchoHandler($order->id)); ?>" style="border-bottom: 1px solid var(--border);">
                            <td style="padding: 8px 10px;">
                                <input type="checkbox" wire:click="toggleSelect(<?php echo e($__bladeCompiler->applyEchoHandler($order->id)); ?>)"
                                       <?php if(in_array($order->id, $selected)): ?> checked <?php endif; ?>
                                       style="accent-color: var(--gold);">
                            </td>
                            <td style="padding: 8px 10px;"><strong>#<?php echo e($__bladeCompiler->applyEchoHandler($order->order_number)); ?></strong></td>
                            <td style="padding: 8px 10px;"><?php echo e($__bladeCompiler->applyEchoHandler($order->customer_name ?? '—')); ?></td>
                            <td style="padding: 8px 10px; font-family: monospace; font-size: 11px;" dir="ltr"><?php echo e($__bladeCompiler->applyEchoHandler($order->phone ?? '—')); ?></td>
                            <td style="padding: 8px 10px; max-width: 180px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                                <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if BLOCK]><![endif]--><?php endif; ?><?php if($order->items->count()): ?>
                                    <?php echo e($__bladeCompiler->applyEchoHandler($order->items->pluck('title')->take(2)->implode('، '))); ?>

                                <?php else: ?> — <?php endif; ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if ENDBLOCK]><![endif]--><?php endif; ?>
                            </td>
                            <td style="padding: 8px 10px;"><?php echo e($__bladeCompiler->applyEchoHandler(\App\Support\PersianNumber::toFa(number_format((float) $order->insurance)))); ?></td>
                            <td style="padding: 8px 10px;">
                                <?php
                                    $stMap = ['pending'=>['📝','ثبت','#f59e0b'], 'final-check'=>['🔍','چک','#3b82f6'], 'courier'=>['🚚','مامور','#10b981']];
                                    $st = $stMap[$order->status ?? 'pending'] ?? ['📝','ثبت','#f59e0b'];
                                ?>
                                <button wire:click="cycleStatus(<?php echo e($__bladeCompiler->applyEchoHandler($order->id)); ?>)"
                                        style="background: <?php echo e($__bladeCompiler->applyEchoHandler($st[2])); ?>; color: #fff; border: none; padding: 4px 10px; border-radius: 20px; font-size: 11px; font-weight: 700; cursor: pointer; font-family: inherit;">
                                    <?php echo e($__bladeCompiler->applyEchoHandler($st[0])); ?> <?php echo e($__bladeCompiler->applyEchoHandler($st[1])); ?>

                                </button>
                            </td>
                            <td style="padding: 8px 10px; font-family: monospace; font-size: 11px;">
                                <?php echo e($__bladeCompiler->applyEchoHandler(\App\Support\PersianDate::format($order->created_at, 'Y/m/d'))); ?>

                            </td>
                            <td style="padding: 8px 10px;">
                                <div style="display: flex; gap: 4px;">
                                    <button onclick="Livewire.dispatch('open-order-view', {orderId: <?php echo e($__bladeCompiler->applyEchoHandler($order->id)); ?>})"
                                            class="btn-icon" title="نمایش">👁️</button>
                                    <button onclick="Livewire.dispatch('open-order-form', {orderId: <?php echo e($__bladeCompiler->applyEchoHandler($order->id)); ?>})"
                                            class="btn-icon" title="ویرایش">✏️</button>
                                    <button wire:click="delete(<?php echo e($__bladeCompiler->applyEchoHandler($order->id)); ?>)" wire:confirm="حذف شود؟"
                                            class="btn-icon" title="حذف">🗑️</button>
                                </div>
                            </td>
                        </tr>
                    <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::endLoop(); ?><?php endif; ?><?php endforeach; $__env->popLoop(); $loop = $__env->getLastLoop(); if ($__empty_1): ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::closeLoop(); ?><?php endif; ?>
                        <tr>
                            <td colspan="9" style="text-align: center; padding: 40px; opacity: .5;">
                                <div style="font-size: 44px;">📦</div>
                                <p>سفارشی نیست</p>
                            </td>
                        </tr>
                    <?php endif; ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if ENDBLOCK]><![endif]--><?php endif; ?>
                </tbody>
            </table>
        </div>

        <div style="padding: 14px;"><?php echo e($__bladeCompiler->applyEchoHandler($orders->links())); ?></div>
    </div>
</div>

<style>
.btn-icon {
    width: 28px; height: 28px;
    border-radius: 8px; border: none;
    display: inline-flex; align-items: center; justify-content: center;
    background: rgba(0,0,0,.05); cursor: pointer; font-size: 13px;
    text-decoration: none;
}
.btn-icon:hover { background: rgba(201,168,76,.2); }
</style>
<?php /**PATH /data/data/com.termux/files/home/shopgun-v2.2/resources/views/livewire/orders/index.blade.php ENDPATH**/ ?>