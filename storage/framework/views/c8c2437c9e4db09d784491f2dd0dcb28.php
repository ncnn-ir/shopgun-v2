<?php $__bladeCompiler = app('blade.compiler'); ?><div>
<?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if BLOCK]><![endif]--><?php endif; ?><?php if($show && $customer): ?>
<div class="sg-modal-overlay active" @keydown.escape.window="$wire.close()">
    <div class="sg-modal" style="max-width:600px">
        <div class="sg-modal-header">
            <h2>👤 پروفایل مشتری</h2>
            <button wire:click="close" class="sg-modal-close">✕</button>
        </div>

        <div class="sg-modal-body" style="padding:14px">

            
            <div class="sg-compact-box">
                <div style="display:flex;align-items:center;gap:12px;margin-bottom:10px">
                    <div class="avatar" style="width:50px;height:50px;font-size:20px">
                        <?php echo e($__bladeCompiler->applyEchoHandler(mb_substr($customer->name ?? '?', 0, 1))); ?>

                    </div>
                    <div style="flex:1;min-width:0">
                        <div class="name" style="font-size:16px"><?php echo e($__bladeCompiler->applyEchoHandler($customer->name)); ?></div>
                        <div class="phone" style="font-size:12px"><?php echo e($__bladeCompiler->applyEchoHandler($customer->phone)); ?></div>
                    </div>
                </div>

                <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if BLOCK]><![endif]--><?php endif; ?><?php if(!empty($stats)): ?>
                    <div class="grid" style="display:grid;grid-template-columns:repeat(3,1fr);gap:8px;padding-top:10px">
                        <div class="item" style="text-align:center">
                            <div class="val"><?php echo e($__bladeCompiler->applyEchoHandler(\App\Support\PersianNumber::toFa($stats['total']))); ?></div>
                            <div class="lbl">سفارشات</div>
                        </div>
                        <div class="item" style="text-align:center">
                            <div class="val"><?php echo e($__bladeCompiler->applyEchoHandler(number_format($stats['sum'] / 1000000, 1))); ?>M</div>
                            <div class="lbl">مجموع</div>
                        </div>
                        <div class="item" style="text-align:center">
                            <div class="val"><?php echo e($__bladeCompiler->applyEchoHandler(number_format($stats['insurance']))); ?></div>
                            <div class="lbl">بیمه</div>
                        </div>
                    </div>
                <?php endif; ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if ENDBLOCK]><![endif]--><?php endif; ?>
            </div>

            <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if BLOCK]><![endif]--><?php endif; ?><?php if($customer->address): ?>
                <div class="sg-inline-info">
                    <div class="item">📍 <?php echo e($__bladeCompiler->applyEchoHandler($customer->address)); ?></div>
                    <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if BLOCK]><![endif]--><?php endif; ?><?php if($customer->postal_code): ?>
                        <div class="item">📮 <strong style="font-family:monospace"><?php echo e($__bladeCompiler->applyEchoHandler($customer->postal_code)); ?></strong></div>
                    <?php endif; ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if ENDBLOCK]><![endif]--><?php endif; ?>
                </div>
            <?php endif; ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if ENDBLOCK]><![endif]--><?php endif; ?>

            
            <div style="font-size:12px;font-weight:700;color:var(--primary);margin:14px 0 8px">
                📦 آخرین سفارشات
            </div>

            <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if BLOCK]><![endif]--><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::openLoop(); ?><?php endif; ?><?php $__empty_1 = true; $__currentLoopData = $orders; $__env->addLoop($__currentLoopData); foreach($__currentLoopData as $o): $__env->incrementLoopIndices(); $loop = $__env->getLastLoop(); $__empty_1 = false; ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::startLoopIteration(); ?><?php endif; ?>
                <div <?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::$currentLoop['key'] = 'ord-'.e($__bladeCompiler->applyEchoHandler($o['id'])).''; ?>wire:key="ord-<?php echo e($__bladeCompiler->applyEchoHandler($o['id'])); ?>"
                     style="padding:10px;border:1px solid var(--border);border-radius:10px;margin-bottom:6px;cursor:pointer;transition:.15s"
                     wire:click="viewOrder(<?php echo e($__bladeCompiler->applyEchoHandler($o['id'])); ?>)"
                     onmouseover="this.style.background='var(--bg-soft)'"
                     onmouseout="this.style.background='transparent'">
                    <div style="display:flex;justify-content:space-between;font-weight:700;font-size:12.5px;margin-bottom:4px">
                        <span>#<?php echo e($__bladeCompiler->applyEchoHandler($o['num'])); ?></span>
                        <span style="font-size:10.5px;opacity:.6;font-family:monospace"><?php echo e($__bladeCompiler->applyEchoHandler($o['date'])); ?></span>
                    </div>
                    <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if BLOCK]><![endif]--><?php endif; ?><?php if($o['products']): ?>
                        <div style="font-size:11px;opacity:.7;margin-bottom:3px">🛍️ <?php echo e($__bladeCompiler->applyEchoHandler($o['products'])); ?></div>
                    <?php endif; ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if ENDBLOCK]><![endif]--><?php endif; ?>
                    <div style="display:flex;justify-content:space-between;font-size:11px">
                        <span style="font-family:monospace"><?php echo e($__bladeCompiler->applyEchoHandler(number_format($o['amount']))); ?> ت</span>
                        <span class="sg-status-badge <?php echo e($__bladeCompiler->applyEchoHandler($o['status'])); ?>" style="font-size:10px;padding:2px 8px">
                            <?php echo e($__bladeCompiler->applyEchoHandler(['pending'=>'📝 ثبت','final-check'=>'🔍 چک','courier'=>'🚚 مامور'][$o['status']] ?? '📝')); ?>

                        </span>
                    </div>
                </div>
            <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::endLoop(); ?><?php endif; ?><?php endforeach; $__env->popLoop(); $loop = $__env->getLastLoop(); if ($__empty_1): ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::closeLoop(); ?><?php endif; ?>
                <p style="text-align:center;padding:20px;opacity:.5;font-size:12px">سفارشی نیست</p>
            <?php endif; ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if ENDBLOCK]><![endif]--><?php endif; ?>
        </div>

        <div class="sg-modal-footer">
            <button wire:click="close" class="btn btn-outline btn-sm">بستن</button>
            <a href="<?php echo e($__bladeCompiler->applyEchoHandler(route('customers.index'))); ?>" class="btn btn-primary btn-sm">👥 همه مشتریان</a>
        </div>
    </div>
</div>
<?php endif; ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if ENDBLOCK]><![endif]--><?php endif; ?>
</div>
<?php /**PATH /data/data/com.termux/files/home/shopgun-v2.2/resources/views/livewire/customers/profile-modal.blade.php ENDPATH**/ ?>