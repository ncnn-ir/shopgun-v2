<?php $__bladeCompiler = app('blade.compiler'); ?><!DOCTYPE html>
<html lang="fa" dir="rtl" data-theme="<?php echo e($__bladeCompiler->applyEchoHandler(\App\Models\AppSetting::get('theme', 'light'))); ?>">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width,initial-scale=1.0,viewport-fit=cover">
    <meta name="theme-color" content="#1a5276">
    <meta name="mobile-web-app-capable" content="yes">
    <meta name="apple-mobile-web-app-capable" content="yes">
    <meta name="csrf-token" content="<?php echo e($__bladeCompiler->applyEchoHandler(csrf_token())); ?>">
    <title>جواهری مشاهیر</title>

    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">
    <link href="https://fonts.googleapis.com/css2?family=Great+Vibes&family=Playfair+Display:wght@400;700&family=Inter:wght@400;600;700&display=swap" rel="stylesheet">

    <script>
        (function(){
            var t = localStorage.getItem('theme') || '<?php echo e($__bladeCompiler->applyEchoHandler(\App\Models\AppSetting::get("theme", "light"))); ?>';
            document.documentElement.setAttribute('data-theme', t);
        })();
    </script>

    <?php echo app('Illuminate\Foundation\Vite')(['resources/css/app.css', 'resources/js/app.js']); ?>
    <?php echo $__bladeCompiler->applyEchoHandler(\Livewire\Mechanisms\FrontendAssets\FrontendAssets::styles()); ?>


    <link rel="stylesheet" href="<?php echo e($__bladeCompiler->applyEchoHandler(asset('css/legacy.css'))); ?>?v=1">
    <script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>

    <?php echo $__env->yieldPushContent('styles'); ?>
    <link rel="stylesheet" href="<?php echo e($__bladeCompiler->applyEchoHandler(asset('css/reports.css'))); ?>?v=1">
<link rel="stylesheet" href="<?php echo e($__bladeCompiler->applyEchoHandler(asset('css/settings-tabs-fix.css'))); ?>">
    <?php
        try {
            $_p = \App\Models\AppSetting::get('primary_color', '#1a5276');
            $_g = \App\Models\AppSetting::get('accent_color', '#c9a84c');
            $_f = \App\Models\AppSetting::get('font_family', 'Vazirmatn');
        } catch (\Throwable $e) {
            $_p = '#1a5276'; $_g = '#c9a84c'; $_f = 'Vazirmatn';
        }
    ?>
    <style>
        :root {
            --primary: <?php echo e($__bladeCompiler->applyEchoHandler($_p)); ?> !important;
            --gold: <?php echo e($__bladeCompiler->applyEchoHandler($_g)); ?> !important;
            --primary-dynamic: <?php echo e($__bladeCompiler->applyEchoHandler($_p)); ?>;
            --gold-dynamic: <?php echo e($__bladeCompiler->applyEchoHandler($_g)); ?>;
            --font-dynamic: <?php echo e($__bladeCompiler->applyEchoHandler($_f)); ?>;
        }
        body { font-family: var(--font-dynamic), 'Vazirmatn', Tahoma, sans-serif !important; }
    </style>
    <link rel="stylesheet" href="{{ asset('css/extra.css?v=4">

    
    @powerGridStyles

</head>
<body>

<?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if BLOCK]><![endif]--><?php endif; ?><?php if(auth()->guard()->check()): ?>
    <?php
$__split = function ($name, $params = []) {
    return [$name, $params];
};
[$__name, $__params] = $__split('global-search', []);

$__keyOuter = $__key ?? null;

$__key = null;
$__componentSlots = [];

$__key ??= \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::generateKey('lw-4279593050-0', $__key);

$__html = app('livewire')->mount($__name, $__params, $__key, $__componentSlots);

echo $__html;

unset($__html);
unset($__key);
$__key = $__keyOuter;
unset($__keyOuter);
unset($__name);
unset($__params);
unset($__componentSlots);
unset($__split);
?>
    <?php
$__split = function ($name, $params = []) {
    return [$name, $params];
};
[$__name, $__params] = $__split('components.shipment-timeline', []);

$__keyOuter = $__key ?? null;

$__key = null;
$__componentSlots = [];

$__key ??= \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::generateKey('lw-4279593050-1', $__key);

$__html = app('livewire')->mount($__name, $__params, $__key, $__componentSlots);

echo $__html;

unset($__html);
unset($__key);
$__key = $__keyOuter;
unset($__keyOuter);
unset($__name);
unset($__params);
unset($__componentSlots);
unset($__split);
?>
    <?php
$__split = function ($name, $params = []) {
    return [$name, $params];
};
[$__name, $__params] = $__split('orders.import-postal', []);

$__keyOuter = $__key ?? null;

$__key = 'imp';
$__componentSlots = [];

$__key ??= \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::generateKey('lw-4279593050-2', $__key);

$__html = app('livewire')->mount($__name, $__params, $__key, $__componentSlots);

echo $__html;

unset($__html);
unset($__key);
$__key = $__keyOuter;
unset($__keyOuter);
unset($__name);
unset($__params);
unset($__componentSlots);
unset($__split);
?>
    <?php
$__split = function ($name, $params = []) {
    return [$name, $params];
};
[$__name, $__params] = $__split('orders.form-modal', []);

$__keyOuter = $__key ?? null;

$__key = 'ofm';
$__componentSlots = [];

$__key ??= \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::generateKey('lw-4279593050-3', $__key);

$__html = app('livewire')->mount($__name, $__params, $__key, $__componentSlots);

echo $__html;

unset($__html);
unset($__key);
$__key = $__keyOuter;
unset($__keyOuter);
unset($__name);
unset($__params);
unset($__componentSlots);
unset($__split);
?>
    <?php
$__split = function ($name, $params = []) {
    return [$name, $params];
};
[$__name, $__params] = $__split('orders.view-modal', []);

$__keyOuter = $__key ?? null;

$__key = 'ovm';
$__componentSlots = [];

$__key ??= \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::generateKey('lw-4279593050-4', $__key);

$__html = app('livewire')->mount($__name, $__params, $__key, $__componentSlots);

echo $__html;

unset($__html);
unset($__key);
$__key = $__keyOuter;
unset($__keyOuter);
unset($__name);
unset($__params);
unset($__componentSlots);
unset($__split);
?>
    <?php
$__split = function ($name, $params = []) {
    return [$name, $params];
};
[$__name, $__params] = $__split('customers.profile-modal', []);

$__keyOuter = $__key ?? null;

$__key = 'cpm';
$__componentSlots = [];

$__key ??= \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::generateKey('lw-4279593050-5', $__key);

$__html = app('livewire')->mount($__name, $__params, $__key, $__componentSlots);

echo $__html;

unset($__html);
unset($__key);
$__key = $__keyOuter;
unset($__keyOuter);
unset($__name);
unset($__params);
unset($__componentSlots);
unset($__split);
?>
    <?php
$__split = function ($name, $params = []) {
    return [$name, $params];
};
[$__name, $__params] = $__split('certificates.view-modal', []);

$__keyOuter = $__key ?? null;

$__key = 'cvm';
$__componentSlots = [];

$__key ??= \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::generateKey('lw-4279593050-6', $__key);

$__html = app('livewire')->mount($__name, $__params, $__key, $__componentSlots);

echo $__html;

unset($__html);
unset($__key);
$__key = $__keyOuter;
unset($__keyOuter);
unset($__name);
unset($__params);
unset($__componentSlots);
unset($__split);
?>
<?php endif; ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if ENDBLOCK]><![endif]--><?php endif; ?>


<header class="sg-main-header">
    <div class="sg-header-right">
        <div class="sg-logo-container" id="headerLogo" onclick="document.getElementById('headerLogoInput').click()">
            <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if BLOCK]><![endif]--><?php endif; ?><?php if(\App\Models\AppSetting::get('header_logo')): ?>
                <img src="<?php echo e($__bladeCompiler->applyEchoHandler(\App\Models\AppSetting::get('header_logo'))); ?>">
            <?php else: ?>
                💎
            <?php endif; ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if ENDBLOCK]><![endif]--><?php endif; ?>
        </div>
        <input type="file" id="headerLogoInput" accept="image/*" style="display:none" onchange="sgHandleHeaderLogo(event)">
        <div class="sg-header-title">
            <h1><?php echo e($__bladeCompiler->applyEchoHandler(\App\Models\AppSetting::get('shop_name', 'جواهری مشاهیر'))); ?></h1>
            <p>مدیریت سفارشات و شناسنامه</p>
        </div>
    </div>

    <div class="sg-header-date" id="headerDate">📅 در حال بارگذاری...</div>

    <div class="sg-header-actions">
        <button class="sg-header-icon-btn" onclick="sgToggleTheme()" id="themeIconBtn">🌙</button>
        <a href="<?php echo e($__bladeCompiler->applyEchoHandler(route('activity-log'))); ?>" wire:navigate class="sg-header-icon-btn" title="لاگ">📜</a>
        <a href="<?php echo e($__bladeCompiler->applyEchoHandler(route('settings.index'))); ?>" wire:navigate class="sg-header-icon-btn" title="تنظیمات">⚙️</a>
        <a href="<?php echo e($__bladeCompiler->applyEchoHandler(route('settings.health'))); ?>" wire:navigate class="sg-header-icon-btn" title="سلامت سیستم">🩺</a>
    </div>
</header>


<div class="sg-tabs-bar">
    <?php
        $tabs = [
            ['route' => 'orders.index',       'icon' => '📦', 'label' => 'سفارشات'],
            ['route' => 'customers.index',    'icon' => '👥', 'label' => 'مشتریان'],
            ['route' => 'certificates.index', 'icon' => '💎', 'label' => 'شناسنامه‌ها'],
            ['route' => 'reports.index',      'icon' => '📊', 'label' => 'گزارش‌ها'],
            ['route' => 'settings.index',     'icon' => '⚙️', 'label' => 'تنظیمات'],
        ];
    ?>
    <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if BLOCK]><![endif]--><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::openLoop(); ?><?php endif; ?><?php $__currentLoopData = $tabs; $__env->addLoop($__currentLoopData); foreach($__currentLoopData as $tab): $__env->incrementLoopIndices(); $loop = $__env->getLastLoop(); ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::startLoopIteration(); ?><?php endif; ?>
        <?php $isActive = request()->routeIs($tab['route']) || request()->routeIs(explode('.', $tab['route'])[0].'.*'); ?>
        <a href="<?php echo e($__bladeCompiler->applyEchoHandler(route($tab['route']))); ?>" wire:navigate class="sg-tab-btn <?php echo e($__bladeCompiler->applyEchoHandler($isActive ? 'active' : '')); ?>">
            <span><?php echo e($__bladeCompiler->applyEchoHandler($tab['icon'])); ?></span>
            <span><?php echo e($__bladeCompiler->applyEchoHandler($tab['label'])); ?></span>
        </a>
    <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::endLoop(); ?><?php endif; ?><?php endforeach; $__env->popLoop(); $loop = $__env->getLastLoop(); ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if ENDBLOCK]><![endif]--><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::closeLoop(); ?><?php endif; ?>
</div>


<main>
    <?php echo e($__bladeCompiler->applyEchoHandler($slot)); ?>

</main>


<nav class="sg-mobile-bar">
    <div class="sg-mobile-bar-inner">
        <?php
            $items = [
                ['dashboard','🏠','خانه'],
                ['orders.index','📦','سفارش'],
                ['orders.create','➕','جدید'],
                ['customers.index','👥','مشتری'],
                ['certificates.index','💎','کارت'],
                ['certificates.create','✨','کارت جدید'],
                ['reports.index','📊','گزارش'],
                ['settings.index','⚙️','تنظیم'],
                ['activity-log','📜','لاگ'],
            ];
        ?>
        <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if BLOCK]><![endif]--><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::openLoop(); ?><?php endif; ?><?php $__currentLoopData = $items; $__env->addLoop($__currentLoopData); foreach($__currentLoopData as $it): $__env->incrementLoopIndices(); $loop = $__env->getLastLoop(); ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::startLoopIteration(); ?><?php endif; ?>
            <?php
                $isActive = request()->routeIs($it[0]) || request()->routeIs(explode('.', $it[0])[0] . '.*');
                $cls = 'sg-mobile-bar-btn';
                if ($it[0] === 'orders.create') $cls .= ' add';
                elseif ($isActive) $cls .= ' active';
            ?>
            <a href="<?php echo e($__bladeCompiler->applyEchoHandler(route($it[0]))); ?>" wire:navigate class="<?php echo e($__bladeCompiler->applyEchoHandler($cls)); ?>">
                <span class="ico"><?php echo e($__bladeCompiler->applyEchoHandler($it[1])); ?></span>
                <span><?php echo e($__bladeCompiler->applyEchoHandler($it[2])); ?></span>
            </a>
        <?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::endLoop(); ?><?php endif; ?><?php endforeach; $__env->popLoop(); $loop = $__env->getLastLoop(); ?><?php if(\Livewire\Mechanisms\ExtendBlade\ExtendBlade::isRenderingLivewireComponent()): ?><!--[if ENDBLOCK]><![endif]--><?php \Livewire\Features\SupportCompiledWireKeys\SupportCompiledWireKeys::closeLoop(); ?><?php endif; ?>
    </div>
</nav>


<div class="sg-toast-container" id="toastContainer"></div>

<script>
    // ═══ Theme Toggle ═══
    function sgToggleTheme() {
        var html = document.documentElement;
        var cur = html.getAttribute('data-theme') || 'light';
        var next = cur === 'dark' ? 'light' : 'dark';
        html.setAttribute('data-theme', next);
        localStorage.setItem('theme', next);
        document.getElementById('themeIconBtn').textContent = next === 'dark' ? '☀️' : '🌙';

        // ذخیره در سرور
        fetch('<?php echo e($__bladeCompiler->applyEchoHandler(route("settings.update-theme"))); ?>', {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-CSRF-TOKEN': '<?php echo e($__bladeCompiler->applyEchoHandler(csrf_token())); ?>'},
            body: JSON.stringify({theme: next})
        }).catch(function(){});
    }

    // ═══ Toast ═══
    window.sgToast = function(msg, type) {
        type = type || 'info';
        var c = document.getElementById('toastContainer');
        if (!c) return;
        var icons = {success: '✅', error: '❌', info: 'ℹ️', warn: '⚠️'};
        var t = document.createElement('div');
        t.className = 'sg-toast ' + type;
        t.innerHTML = (icons[type] || 'ℹ️') + ' ' + msg;
        c.appendChild(t);
        setTimeout(function() { if (t.parentNode) t.remove(); }, 3200);
    };

    // ═══ Header Logo Upload ═══
    function sgHandleHeaderLogo(e) {
        var f = e.target.files[0]; if (!f) return;
        if (f.size > 2 * 1024 * 1024) { sgToast('حجم زیاد (max 2MB)', 'error'); return; }
        var r = new FileReader();
        r.onload = function(ev) {
            var data = ev.target.result;
            document.getElementById('headerLogo').innerHTML = '<img src="' + data + '">';
            // ذخیره به سرور
            fetch('<?php echo e($__bladeCompiler->applyEchoHandler(route("settings.update-header-logo"))); ?>', {
                method: 'POST',
                headers: {'Content-Type': 'application/json', 'X-CSRF-TOKEN': '<?php echo e($__bladeCompiler->applyEchoHandler(csrf_token())); ?>'},
                body: JSON.stringify({logo: data})
            }).then(function() { sgToast('لوگو ذخیره شد ✅', 'success'); });
        };
        r.readAsDataURL(f);
    }

    // ═══ Header Date ═══
    function sgUpdateHeaderDate() {
        var el = document.getElementById('headerDate');
        if (!el) return;
        var d = new Date();
        var p = toPersianDate(d);
        var months = ['فروردین','اردیبهشت','خرداد','تیر','مرداد','شهریور','مهر','آبان','آذر','دی','بهمن','اسفند'];
        el.innerHTML = '📅 ' + p.day + ' ' + months[p.month-1] + ' ' + p.year + ' · ' + String(d.getHours()).padStart(2,'0') + ':' + String(d.getMinutes()).padStart(2,'0');
    }
    function toPersianDate(d) {
        var gy=d.getFullYear(),gm=d.getMonth()+1,gd=d.getDate();
        var g_d_m=[0,31,59,90,120,151,181,212,243,273,304,334];
        var jy=(gy<=1600)?0:979;gy-=(gy<=1600)?621:1600;
        var gy2=(gm>2)?(gy+1):gy;
        var days=365*gy+Math.floor((gy2+3)/4)-Math.floor((gy2+99)/100)+Math.floor((gy2+399)/400)-80+gd+g_d_m[gm-1];
        jy+=33*Math.floor(days/12053);days%=12053;jy+=4*Math.floor(days/1461);days%=1461;
        if(days>365){jy+=Math.floor((days-1)/365);days=(days-1)%365}
        var jm=(days<186)?1+Math.floor(days/31):7+Math.floor((days-186)/30);
        var jd=1+((days<186)?(days%31):((days-186)%30));
        return {year:jy,month:jm,day:jd};
    }
    sgUpdateHeaderDate();
    setInterval(sgUpdateHeaderDate, 60000);

    // ═══ Init ═══
    document.addEventListener('DOMContentLoaded', function() {
        var cur = document.documentElement.getAttribute('data-theme');
        var icon = document.getElementById('themeIconBtn');
        if (icon) icon.textContent = cur === 'dark' ? '☀️' : '🌙';
    });

    // ═══ Livewire Notify Event ═══
    document.addEventListener('livewire:init', function() {
    Livewire.on('apply-appearance', function(data) {
        var p = Array.isArray(data) ? data[0] : data;
        var root = document.documentElement;
        if (p.primary_color) {
            root.style.setProperty('--primary', p.primary_color);
            document.querySelectorAll('style').forEach(function(s) {
                if (s.textContent.includes('--primary:')) {
                    // no-op
                }
            });
        }
        if (p.accent_color) root.style.setProperty('--gold', p.accent_color);
        if (p.font_family) {
            root.style.setProperty('--font-dynamic', p.font_family);
            document.body.style.fontFamily = p.font_family + ", 'Vazirmatn', Tahoma, sans-serif";
        }
        if (p.theme) {
            root.setAttribute('data-theme', p.theme);
            localStorage.setItem('theme', p.theme);
        }
        if (window.sgToast) sgToast('ظاهر اعمال شد ✅', 'success');
    });

        Livewire.on('notify', function(data) {
            var p = Array.isArray(data) ? data[0] : data;
            sgToast(p.message || '', p.type || 'info');
        });
    });
</script>


    
    <?php echo $__env->yieldPushContent('jalali-scripts'); ?>
<?php echo app('Tighten\Ziggy\BladeRouteGenerator')->generate(); ?>
    
    
    <?php echo $__env->yieldPushContent('jalali-scripts'); ?>
<?php echo $__bladeCompiler->applyEchoHandler(\Livewire\Mechanisms\FrontendAssets\FrontendAssets::scripts()); ?>

<?php echo $__env->yieldPushContent('scripts'); ?>

    
    @powerGridScripts

</body>
</html>
<?php /**PATH /data/data/com.termux/files/home/shopgun-v2.2/resources/views/components/layouts/app.blade.php ENDPATH**/ ?>