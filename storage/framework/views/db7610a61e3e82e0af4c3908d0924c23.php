<?php $__bladeCompiler = app('blade.compiler'); ?><div>
    <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if BLOCK]><![endif]--><?php endif; ?><?php if($show && $order): ?>
    <div class="fixed inset-0 z-[100] flex items-start justify-center p-4 overflow-y-auto"
         x-data="{ show: true }"
         x-init="$nextTick(() => show = true)">

        <div class="fixed inset-0 bg-black/70 backdrop-blur-md transition-opacity duration-300"
             x-show="show"
             x-transition:enter="ease-out duration-300"
             x-transition:enter-start="opacity-0"
             x-transition:enter-end="opacity-100"
             wire:click="close"></div>

        <div class="relative bg-base-100 rounded-2xl shadow-2xl w-full max-w-3xl my-8 md:my-16
                    border border-primary/20 transition-all duration-300"
             x-show="show"
             x-transition:enter="ease-out duration-300"
             x-transition:enter-start="opacity-0 translate-y-8 scale-95"
             x-transition:enter-end="opacity-100 translate-y-0 scale-100">

            <div class="flex items-center justify-between p-4 border-b border-base-300 bg-gradient-to-l from-primary/10 to-transparent rounded-t-2xl">
                <div class="flex items-center gap-3">
                    <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-500 to-teal-600 flex items-center justify-center text-white text-lg shadow-lg">
                        📮
                    </div>
                    <div>
                        <div class="font-bold text-sm">مرسوله تیپاکس</div>
                        <div class="text-xs text-base-content/60">سفارش #<?php echo e($__bladeCompiler->applyEchoHandler($order->order_number)); ?></div>
                    </div>
                </div>
                <button wire:click="close" class="btn btn-ghost btn-sm btn-circle">✕</button>
            </div>

            <div class="p-5 space-y-5">

                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                    <div class="bg-gradient-to-br from-cyan-500 to-teal-600 text-white rounded-xl p-4 shadow-lg">
                        <div class="text-[10px] opacity-80 mb-1">📮 کد رهگیری</div>
                        <div class="font-mono font-bold text-lg tracking-wider" dir="ltr">
                            <?php echo e($__bladeCompiler->applyEchoHandler($order->tracking_code ?: '—')); ?>

                        </div>
                        <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if BLOCK]><![endif]--><?php endif; ?><?php if($order->shipping_status): ?>
                            <div class="inline-block mt-2 px-2 py-0.5 bg-white/20 rounded-full text-[10px] font-bold">
                                <?php echo e($__bladeCompiler->applyEchoHandler($order->shipping_status)); ?>

                            </div>
                        <?php endif; ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if ENDBLOCK]><![endif]--><?php endif; ?>
                    </div>

                    <div class="bg-base-200 rounded-xl p-4">
                        <div class="text-[10px] text-base-content/60 mb-1">👤 گیرنده</div>
                        <div class="font-bold text-sm"><?php echo e($__bladeCompiler->applyEchoHandler($order->customer?->name ?? '—')); ?></div>
                        <div class="text-xs text-base-content/60 font-mono mt-1" dir="ltr"><?php echo e($__bladeCompiler->applyEchoHandler($order->phone)); ?></div>
                        <div class="text-xs text-base-content/60 mt-1 truncate"><?php echo e($__bladeCompiler->applyEchoHandler($order->address)); ?></div>
                    </div>
                </div>

                <div>
                    <h3 class="font-bold text-sm mb-4 flex items-center gap-2">
                        <span class="w-2 h-2 rounded-full bg-cyan-500 animate-pulse"></span>
                        مراحل ارسال
                    </h3>

                    <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if BLOCK]><![endif]--><?php endif; ?><?php if(empty($events)): ?>
                        <div class="text-center py-8 text-base-content/40 text-sm">
                            هنوز رویدادی ثبت نشده
                        </div>
                    <?php else: ?>
                        <div class="overflow-x-auto pb-4 -mx-5 px-5">
                            <div class="flex items-start gap-0 min-w-max">
                                <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if BLOCK]><![endif]--><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::openLoop(); ?><?php endif; ?><?php $__currentLoopData = array_reverse($events); $__env->addLoop($__currentLoopData); foreach($__currentLoopData as $i => $e): $__env->incrementLoopIndices(); $loop = $__env->getLastLoop(); ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::startLoopIteration(); ?><?php endif; ?>
                                    <?php
                                        $isLast = $i === count($events) - 1;
                                        $s = mb_strtolower($e['status'] ?? '');
                                        $color = str_contains($s, 'تحویل') && ! str_contains($s, 'نشد')
                                            ? 'from-emerald-500 to-green-600'
                                            : (str_contains($s, 'مسیر') || str_contains($s, 'ارسال')
                                                ? 'from-cyan-500 to-blue-600'
                                                : 'from-amber-500 to-orange-500');
                                    ?>

                                    <div class="flex items-start">
                                        <div class="flex flex-col items-center w-40" <?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::$currentLoop['key'] = 'event-'.e($__bladeCompiler->applyEchoHandler($i)).''; ?>wire:key="event-<?php echo e($__bladeCompiler->applyEchoHandler($i)); ?>">
                                            <div class="relative">
                                                <div class="w-12 h-12 rounded-full bg-gradient-to-br <?php echo e($__bladeCompiler->applyEchoHandler($color)); ?> 
                                                            flex items-center justify-center text-white text-xl shadow-lg
                                                            <?php echo e($__bladeCompiler->applyEchoHandler($isLast ? 'ring-4 ring-cyan-500/30 animate-pulse' : '')); ?>">
                                                    <?php echo e($__bladeCompiler->applyEchoHandler($isLast ? '🚚' : ($i === 0 ? '📦' : '📍'))); ?>

                                                </div>
                                                <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if BLOCK]><![endif]--><?php endif; ?><?php if(! $isLast): ?>
                                                    <div class="absolute top-1/2 -right-14 w-14 h-0.5 bg-gradient-to-l from-cyan-500 to-transparent"></div>
                                                <?php endif; ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if ENDBLOCK]><![endif]--><?php endif; ?>
                                            </div>
                                            <div class="mt-3 text-center w-36">
                                                <div class="text-xs font-bold text-base-content/80 leading-tight">
                                                    <?php echo e($__bladeCompiler->applyEchoHandler(\Illuminate\Support\Str::limit($e['status'] ?? '—', 30))); ?>

                                                </div>
                                                <div class="text-[10px] text-base-content/50 mt-1 font-mono" dir="ltr">
                                                    <?php echo e($__bladeCompiler->applyEchoHandler($e['date'] ?? '')); ?>

                                                </div>
                                                <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if BLOCK]><![endif]--><?php endif; ?><?php if(! empty($e['description']) && $e['description'] !== ($e['status'] ?? '')): ?>
                                                    <div class="text-[10px] text-base-content/40 mt-1 leading-tight">
                                                        <?php echo e($__bladeCompiler->applyEchoHandler(\Illuminate\Support\Str::limit($e['description'], 60))); ?>

                                                    </div>
                                                <?php endif; ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if ENDBLOCK]><![endif]--><?php endif; ?>
                                            </div>
                                        </div>
                                    </div>
                                <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::endLoop(); ?><?php endif; ?><?php endforeach; $__env->popLoop(); $loop = $__env->getLastLoop(); ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if ENDBLOCK]><![endif]--><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::closeLoop(); ?><?php endif; ?>
                            </div>
                        </div>
                    <?php endif; ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if ENDBLOCK]><![endif]--><?php endif; ?>
                </div>

                <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if BLOCK]><![endif]--><?php endif; ?><?php if($order->tracking_code): ?>
                    <a href="https://tipaxco.com/tracking?code=<?php echo e($__bladeCompiler->applyEchoHandler($order->tracking_code)); ?>"
                       target="_blank"
                       class="inline-flex items-center gap-2 px-4 py-2 rounded-lg bg-gradient-to-l from-cyan-500 to-teal-600 text-white text-xs font-bold hover:opacity-90 transition">
                        🔗 پیگیری در سایت تیپاکس
                    </a>
                <?php endif; ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if ENDBLOCK]><![endif]--><?php endif; ?>
            </div>
        </div>
    </div>
    <?php endif; ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if ENDBLOCK]><![endif]--><?php endif; ?>
</div>
<?php /**PATH /data/data/com.termux/files/home/shopgun-v2.2/resources/views/livewire/components/shipment-timeline.blade.php ENDPATH**/ ?>