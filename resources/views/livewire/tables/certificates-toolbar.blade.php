<div style="display:flex;gap:6px;flex-wrap:wrap;padding:8px 12px;background:#f8fafc;border-bottom:1px solid #e2e8f0;align-items:center">
    <button type="button" onclick="Livewire.dispatch('open-cert-form')"
            class="btn btn-primary btn-sm">➕ شناسنامه جدید</button>

    <button type="button" onclick="Livewire.dispatch('open-auto-cert')"
            class="btn btn-success btn-sm"
            style="background:linear-gradient(135deg,#16a34a,#15803d);color:#fff">
        ⚡ صدور خودکار (از SKU سایت)
    </button>

    <div style="margin-right:auto;display:flex;gap:6px;align-items:center">
        <span style="font-size:11px;color:#64748b">🖨️ چاپ کل:</span>
        <button type="button" onclick="printAllCerts()"
                style="background:#1a5276;color:#fff;border:none;padding:6px 12px;border-radius:8px;font-size:11px;font-weight:700;cursor:pointer">
            چاپ همه (A4)
        </button>
    </div>
</div>

<script>
function printAllCerts() {
    // همه شناسنامه‌های صفحه فعلی
    var ids = Array.from(document.querySelectorAll('[data-cert-row-id]'))
        .map(el => el.dataset.certRowId).filter(Boolean);
    if (!ids.length) { alert('شناسنامه‌ای نیست'); return; }
    window.open('{{ route("certificates.print") }}?ids=' + ids.join(',') + '&auto=1', '_blank');
}
</script>
