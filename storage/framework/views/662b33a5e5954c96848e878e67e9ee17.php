<?php $__bladeCompiler = app('blade.compiler'); ?><div x-data="{ open: <?php if ((object) ('open') instanceof \Livewire\WireDirective) : ?>window.Livewire.find('<?php echo e($__bladeCompiler->applyEchoHandler($__livewire->getId())); ?>').entangle('<?php echo e($__bladeCompiler->applyEchoHandler('open'->value())); ?>')<?php echo e($__bladeCompiler->applyEchoHandler('open'->hasModifier('live') ? '.live' : '')); ?><?php else : ?>window.Livewire.find('<?php echo e($__bladeCompiler->applyEchoHandler($__livewire->getId())); ?>').entangle('<?php echo e($__bladeCompiler->applyEchoHandler('open')); ?>')<?php endif; ?> }"
     @keydown.window.prevent.ctrl.k="open = true; $wire.openSearch(); $nextTick(() => $refs.searchInput?.focus())"
     @keydown.window.escape="open = false; $wire.close()">

    <div x-show="open" x-transition.opacity
         class="fixed inset-0 bg-black/60 backdrop-blur-sm z-[100]"
         @click="open = false; $wire.close()"></div>

    <div x-show="open" x-transition
         class="fixed inset-x-0 top-20 mx-auto max-w-2xl z-[101] px-4">
        <div class="card bg-base-100 shadow-2xl">
            <div class="card-body p-0">
                <div class="flex items-center gap-3 p-4 border-b border-base-300">
                    <span class="text-2xl">🔍</span>
                    <input x-ref="searchInput" type="text"
                           wire:model.live.debounce.300ms="query"
                           placeholder="جستجو..."
                           class="input input-ghost w-full text-lg" autofocus />
                    <kbd class="kbd kbd-sm">ESC</kbd>
                </div>

                <div class="max-h-96 overflow-y-auto p-2">
                    <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if BLOCK]><![endif]--><?php endif; ?><?php if(strlen(trim($query)) < 2): ?>
                        <div class="text-center py-8 text-base-content/50 text-sm">حداقل ۲ کاراکتر وارد کن</div>
                    <?php else: ?>
                        <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if BLOCK]><![endif]--><?php endif; ?><?php if($orders->isNotEmpty()): ?>
                            <div class="text-xs text-base-content/60 px-3 pt-3 pb-1 font-bold">📦 سفارشات</div>
                            <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if BLOCK]><![endif]--><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::openLoop(); ?><?php endif; ?><?php $__currentLoopData = $orders; $__env->addLoop($__currentLoopData); foreach($__currentLoopData as $order): $__env->incrementLoopIndices(); $loop = $__env->getLastLoop(); ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::startLoopIteration(); ?><?php endif; ?>
                                <a href="<?php echo e($__bladeCompiler->applyEchoHandler(route('orders.show', $order))); ?>" wire:navigate @click="open = false"
                                   class="flex items-center gap-3 p-3 rounded-lg hover:bg-base-200">
                                    <span class="text-xl">📦</span>
                                    <div class="flex-1">
                                        <div class="font-bold text-sm">#<?php echo e($__bladeCompiler->applyEchoHandler($order->order_number)); ?> — <?php echo e($__bladeCompiler->applyEchoHandler($order->customer?->name ?? 'بدون نام')); ?></div>
                                        <div class="text-xs text-base-content/60 font-mono" dir="ltr"><?php echo e($__bladeCompiler->applyEchoHandler($order->phone)); ?></div>
                                    </div>
                                </a>
                            <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::endLoop(); ?><?php endif; ?><?php endforeach; $__env->popLoop(); $loop = $__env->getLastLoop(); ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if ENDBLOCK]><![endif]--><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::closeLoop(); ?><?php endif; ?>
                        <?php endif; ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if ENDBLOCK]><![endif]--><?php endif; ?>

                        <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if BLOCK]><![endif]--><?php endif; ?><?php if($customers->isNotEmpty()): ?>
                            <div class="text-xs text-base-content/60 px-3 pt-3 pb-1 font-bold">👥 مشتریان</div>
                            <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if BLOCK]><![endif]--><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::openLoop(); ?><?php endif; ?><?php $__currentLoopData = $customers; $__env->addLoop($__currentLoopData); foreach($__currentLoopData as $customer): $__env->incrementLoopIndices(); $loop = $__env->getLastLoop(); ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::startLoopIteration(); ?><?php endif; ?>
                                <a href="<?php echo e($__bladeCompiler->applyEchoHandler(route('customers.show', $customer))); ?>" wire:navigate @click="open = false"
                                   class="flex items-center gap-3 p-3 rounded-lg hover:bg-base-200">
                                    <span class="text-xl">👤</span>
                                    <div class="flex-1">
                                        <div class="font-bold text-sm"><?php echo e($__bladeCompiler->applyEchoHandler($customer->name ?? 'بدون نام')); ?></div>
                                        <div class="text-xs text-base-content/60 font-mono" dir="ltr"><?php echo e($__bladeCompiler->applyEchoHandler($customer->phone)); ?></div>
                                    </div>
                                </a>
                            <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::endLoop(); ?><?php endif; ?><?php endforeach; $__env->popLoop(); $loop = $__env->getLastLoop(); ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if ENDBLOCK]><![endif]--><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::closeLoop(); ?><?php endif; ?>
                        <?php endif; ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if ENDBLOCK]><![endif]--><?php endif; ?>

                        <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if BLOCK]><![endif]--><?php endif; ?><?php if($orders->isEmpty() && $customers->isEmpty()): ?>
                            <div class="text-center py-8 text-base-content/50 text-sm">نتیجه‌ای یافت نشد</div>
                        <?php endif; ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if ENDBLOCK]><![endif]--><?php endif; ?>
                    <?php endif; ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if ENDBLOCK]><![endif]--><?php endif; ?>
                </div>
            </div>
        </div>
    </div>
</div>
<?php /**PATH /data/data/com.termux/files/home/shopgun-v2.2/resources/views/livewire/global-search.blade.php ENDPATH**/ ?>