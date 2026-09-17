<?php $__bladeCompiler = app('blade.compiler'); ?><div>
<?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if BLOCK]><![endif]--><?php endif; ?><?php if($show): ?>
<div class="sg-modal-overlay active" @keydown.escape.window="$wire.close()">
    <div class="sg-modal" style="max-width:820px">
        <div class="sg-modal-header" style="background:linear-gradient(135deg,#3498db,#1a5276)">
            <h2>📮 ایمپورت مرسولات پستی</h2>
            <button wire:click="close" class="sg-modal-close">✕</button>
        </div>

        <div class="sg-modal-body">
            <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if BLOCK]><![endif]--><?php endif; ?><?php if(empty($columns)): ?>
                
                <div class="form-group">
                    <label>فایل CSV/TSV (خروجی از شرکت پستی)</label>
                    <input type="file" wire:model="file" accept=".csv,.tsv,.txt" class="form-control">
                    <div wire:loading wire:target="file" style="text-align:center;padding:10px;color:var(--primary)">⏳ در حال بارگذاری...</div>
                </div>
                <div style="padding:10px 12px;background:rgba(52,152,219,.08);border-radius:10px;font-size:11.5px;line-height:1.7">
                    💡 تطبیق با سفارشات بر اساس <strong>شماره تلفن گیرنده</strong>.<br>
                    🔖 از Excel: File → Save As → CSV UTF-8
                </div>
            <?php else: ?>
                
                <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px">
                    <div style="padding:8px 14px;background:var(--bg);border-radius:10px;font-size:12px">📋 <strong><?php echo e($__bladeCompiler->applyEchoHandler(\App\Support\PersianNumber::toFa(count($rows)))); ?></strong> ردیف</div>
                    <div style="padding:8px 14px;background:rgba(39,174,96,.1);border-radius:10px;font-size:12px;color:var(--success)">🎯 <strong><?php echo e($__bladeCompiler->applyEchoHandler(\App\Support\PersianNumber::toFa($matched))); ?></strong> تطبیق</div>
                    <div style="padding:8px 14px;background:rgba(231,76,60,.1);border-radius:10px;font-size:12px;color:var(--danger)">⚠️ <strong><?php echo e($__bladeCompiler->applyEchoHandler(\App\Support\PersianNumber::toFa($unmatched))); ?></strong> بدون تطبیق</div>
                </div>

                
                <div style="font-weight:700;font-size:12.5px;color:var(--primary);margin-bottom:8px">🗺️ نگاشت ستون‌ها</div>
                <div style="max-height:280px;overflow:auto;border-radius:10px;border:1px solid var(--border);margin-bottom:14px">
                    <table style="width:100%;border-collapse:collapse;font-size:12px">
                        <thead style="position:sticky;top:0;background:var(--thead-bg)">
                            <tr>
                                <th style="padding:8px;text-align:right">ستون فایل</th>
                                <th style="padding:8px;text-align:right">نمونه</th>
                                <th style="padding:8px;text-align:right">فیلد مقصد</th>
                            </tr>
                        </thead>
                        <tbody>
                            <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if BLOCK]><![endif]--><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::openLoop(); ?><?php endif; ?><?php $__currentLoopData = $columns; $__env->addLoop($__currentLoopData); foreach($__currentLoopData as $i => $col): $__env->incrementLoopIndices(); $loop = $__env->getLastLoop(); ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::startLoopIteration(); ?><?php endif; ?>
                                <tr style="border-top:1px solid var(--border)">
                                    <td style="padding:8px;font-weight:700"><?php echo e($__bladeCompiler->applyEchoHandler($col)); ?></td>
                                    <td style="padding:8px;font-size:10.5px;opacity:.7;max-width:150px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap"><?php echo e($__bladeCompiler->applyEchoHandler($rows[0][$i] ?? '—')); ?></td>
                                    <td style="padding:8px">
                                        <select wire:model.live="mapping.<?php echo e($__bladeCompiler->applyEchoHandler($i)); ?>" class="form-control" style="padding:4px 8px;font-size:11px">
                                            <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if BLOCK]><![endif]--><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::openLoop(); ?><?php endif; ?><?php $__currentLoopData = $availableFields; $__env->addLoop($__currentLoopData); foreach($__currentLoopData as $k => $v): $__env->incrementLoopIndices(); $loop = $__env->getLastLoop(); ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::startLoopIteration(); ?><?php endif; ?>
                                                <option value="<?php echo e($__bladeCompiler->applyEchoHandler($k)); ?>"><?php echo e($__bladeCompiler->applyEchoHandler($v)); ?></option>
                                            <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::endLoop(); ?><?php endif; ?><?php endforeach; $__env->popLoop(); $loop = $__env->getLastLoop(); ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if ENDBLOCK]><![endif]--><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::closeLoop(); ?><?php endif; ?>
                                        </select>
                                    </td>
                                </tr>
                            <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::endLoop(); ?><?php endif; ?><?php endforeach; $__env->popLoop(); $loop = $__env->getLastLoop(); ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if ENDBLOCK]><![endif]--><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::closeLoop(); ?><?php endif; ?>
                        </tbody>
                    </table>
                </div>

                
                <details style="margin-bottom:14px">
                    <summary style="cursor:pointer;font-weight:700;font-size:12px;color:var(--primary);padding:8px;background:var(--bg);border-radius:8px">👁️ پیش‌نمایش ۵ ردیف</summary>
                    <div style="max-height:240px;overflow:auto;margin-top:8px;border:1px solid var(--border);border-radius:8px">
                        <table style="width:100%;border-collapse:collapse;font-size:10.5px">
                            <thead style="background:var(--thead-bg);position:sticky;top:0">
                                <tr>
                                    <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if BLOCK]><![endif]--><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::openLoop(); ?><?php endif; ?><?php $__currentLoopData = $columns; $__env->addLoop($__currentLoopData); foreach($__currentLoopData as $col): $__env->incrementLoopIndices(); $loop = $__env->getLastLoop(); ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::startLoopIteration(); ?><?php endif; ?><th style="padding:6px;text-align:right;white-space:nowrap"><?php echo e($__bladeCompiler->applyEchoHandler($col)); ?></th><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::endLoop(); ?><?php endif; ?><?php endforeach; $__env->popLoop(); $loop = $__env->getLastLoop(); ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if ENDBLOCK]><![endif]--><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::closeLoop(); ?><?php endif; ?>
                                </tr>
                            </thead>
                            <tbody>
                                <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if BLOCK]><![endif]--><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::openLoop(); ?><?php endif; ?><?php $__currentLoopData = $preview; $__env->addLoop($__currentLoopData); foreach($__currentLoopData as $row): $__env->incrementLoopIndices(); $loop = $__env->getLastLoop(); ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::startLoopIteration(); ?><?php endif; ?>
                                    <tr style="border-top:1px solid var(--border)">
                                        <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if BLOCK]><![endif]--><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::openLoop(); ?><?php endif; ?><?php $__currentLoopData = $row; $__env->addLoop($__currentLoopData); foreach($__currentLoopData as $cell): $__env->incrementLoopIndices(); $loop = $__env->getLastLoop(); ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::startLoopIteration(); ?><?php endif; ?>
                                            <td style="padding:6px;max-width:120px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap"><?php echo e($__bladeCompiler->applyEchoHandler($cell)); ?></td>
                                        <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::endLoop(); ?><?php endif; ?><?php endforeach; $__env->popLoop(); $loop = $__env->getLastLoop(); ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if ENDBLOCK]><![endif]--><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::closeLoop(); ?><?php endif; ?>
                                    </tr>
                                <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::endLoop(); ?><?php endif; ?><?php endforeach; $__env->popLoop(); $loop = $__env->getLastLoop(); ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if ENDBLOCK]><![endif]--><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::closeLoop(); ?><?php endif; ?>
                            </tbody>
                        </table>
                    </div>
                </details>
            <?php endif; ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if ENDBLOCK]><![endif]--><?php endif; ?>
        </div>

        <div class="sg-modal-footer">
            <button wire:click="close" class="btn btn-outline">انصراف</button>
            <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if BLOCK]><![endif]--><?php endif; ?><?php if(!empty($columns)): ?>
                <button wire:click="save" wire:loading.attr="disabled" class="btn btn-success">
                    <span wire:loading.remove wire:target="save">✅ اعمال و بروزرسانی</span>
                    <span wire:loading wire:target="save">⏳ در حال اعمال...</span>
                </button>
            <?php endif; ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if ENDBLOCK]><![endif]--><?php endif; ?>
        </div>
    </div>
</div>
<?php endif; ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if ENDBLOCK]><![endif]--><?php endif; ?>
</div>
<?php /**PATH /data/data/com.termux/files/home/shopgun-v2.2/resources/views/livewire/orders/import-postal.blade.php ENDPATH**/ ?>