<div class="sg-page" style="padding:16px;direction:rtl">

    <div style="text-align:center;margin-bottom:24px">
        <div style="font-size:56px;line-height:1">💎</div>
        <h1 style="margin:8px 0 4px;font-size:24px;font-weight:900;color:#1a5276">شاپگان</h1>
        <p style="margin:0;color:#64748b;font-size:12.5px">سیستم مدیریت سفارشات، شناسنامه و انبار</p>
    </div>

    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:12px;max-width:900px;margin:0 auto 24px">
        <div style="background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:16px;text-align:center">
            <div style="font-size:22px;font-weight:800;color:#1a5276">v2.2</div>
            <div style="font-size:11.5px;color:#64748b;margin-top:4px">نسخه</div>
        </div>
        <div style="background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:16px;text-align:center">
            <div style="font-size:22px;font-weight:800;color:#c9a84c">Laravel 13</div>
            <div style="font-size:11.5px;color:#64748b;margin-top:4px">فریم‌ورک</div>
        </div>
        <div style="background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:16px;text-align:center">
            <div style="font-size:22px;font-weight:800;color:#059669">PHP 8.5</div>
            <div style="font-size:11.5px;color:#64748b;margin-top:4px">زبان</div>
        </div>
    </div>

    <div style="max-width:900px;margin:0 auto">
        <div style="background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:18px;margin-bottom:12px">
            <h2 style="margin:0 0 10px;font-size:15px;font-weight:800;color:#1e293b">📚 امکانات</h2>
            <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:8px;font-size:12.5px;color:#475569">
                <div>✅ مدیریت سفارشات</div>
                <div>✅ شناسنامه و قالب‌ها</div>
                <div>✅ همگام‌سازی ووکامرس</div>
                <div>✅ لیست تامین خودکار</div>
                <div>✅ حسابداری و پیامک</div>
                <div>✅ گزارشات تحلیلی</div>
                <div>✅ پشتیبان‌گیری</div>
                <div>✅ مدیریت مشتریان</div>
            </div>
        </div>

        <div style="background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:18px">
            <h2 style="margin:0 0 10px;font-size:15px;font-weight:800;color:#1e293b">🔗 لینک‌ها</h2>
            <div style="display:flex;gap:8px;flex-wrap:wrap">
                <a href="{{ route('dashboard') }}" wire:navigate class="sg-btn sg-btn-gray">🏠 داشبورد</a>
                <a href="{{ route('settings.health') }}" wire:navigate class="sg-btn sg-btn-gray">🩺 سلامت سیستم</a>
                <a href="{{ route('activity-log') }}" wire:navigate class="sg-btn sg-btn-gray">📜 لاگ‌ها</a>
            </div>
        </div>
    </div>
</div>
