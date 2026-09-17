<div style="padding:14px" dir="rtl">

    <div style="display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:16px;flex-wrap:wrap">
        <h1 style="margin:0;font-size:20px;font-weight:700">💎 شناسنامه‌ها — جدول حرفه‌ای</h1>

        <div style="display:flex;gap:8px;flex-wrap:wrap">
            <a href="{{ route('certificates.index') }}" wire:navigate class="btn btn-outline btn-sm"
               style="padding:8px 14px;font-size:13px">← بازگشت</a>

            <button type="button" onclick="Livewire.dispatch('open-cert-form')"
                    class="btn btn-primary"
                    style="padding:8px 18px;font-size:13px;font-weight:700;background:linear-gradient(135deg,#1a5276,#0d3b5e);color:#fff;border:none;border-radius:8px;cursor:pointer;height:38px">
                ➕ شناسنامه جدید
            </button>

            <button type="button" onclick="printAllCerts()"
                    style="padding:8px 18px;font-size:13px;font-weight:700;background:linear-gradient(135deg,#7c3aed,#5b21b6);color:#fff;border:none;border-radius:8px;cursor:pointer;height:38px">
                🖨️ چاپ همه
            </button>
        </div>
    </div>

    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:12px;overflow:hidden">
        <livewire:tables.certificates-table />
    </div>
</div>

<script>
function printAllCerts() {
    var ids = Array.from(document.querySelectorAll('table tbody tr'))
        .map(function(tr) {
            var btn = tr.querySelector('[onclick*="open-cert-view"]');
            if (!btn) return null;
            var m = btn.getAttribute('onclick').match(/certId:\s*(\d+)/);
            return m ? m[1] : null;
        })
        .filter(Boolean);

    if (!ids.length) { alert('شناسنامه‌ای در صفحه نیست'); return; }
    window.open('/certificates/print?ids=' + ids.join(',') + '&auto=1', '_blank');
}
</script>
