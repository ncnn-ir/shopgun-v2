<div>

    {{-- ═══ Toolbar ═══ --}}
    <div class="sg-toolbar">
        <div class="sg-toolbar-right">
            <input type="text" wire:model.live.debounce.400ms="search"
                   placeholder="🔍 کد/SKU/سنگ..." class="form-control" style="width:220px">
        </div>
        <div style="display:flex;gap:6px">
            <button type="button" onclick="Livewire.dispatch('open-cert-form')"
                    class="btn btn-primary">➕ شناسنامه جدید</button>
        </div>
    </div>

    {{-- ═══ Table ═══ --}}
    <div class="sg-table-container">
        <div class="sg-table-header">
            <h2>💎 شناسنامه‌ها
                <span style="background:var(--gold);color:var(--primary);padding:2px 10px;border-radius:20px;font-size:10.5px;font-weight:700">
                    {{ \App\Support\PersianNumber::toFa($certificates->total()) }}
                </span>
            </h2>
        </div>

        <div class="sg-table-scroll">
            <table class="sg-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>کد</th>
                        <th>تصویر</th>
                        <th>سنگ</th>
                        <th>فلز</th>
                        <th>ابعاد</th>
                        <th>وزن</th>
                        <th>تاریخ</th>
                        <th>عملیات</th>
                    </tr>
                </thead>
                <tbody>
                    @forelse($certificates as $c)
                        <tr wire:key="cert-{{ $c->id }}">
                            <td><span class="sg-row-num">{{ \App\Support\PersianNumber::toFa($loop->iteration) }}</span></td>

                            <td>
                                <strong>{{ $c->code }}</strong>
                                @if($c->sku)
                                    <div style="font-size:10px;opacity:.6;direction:ltr">{{ $c->sku }}</div>
                                @endif
                            </td>

                            <td>
                                @if($c->image_path)
                                    <img src="{{ asset('storage/' . $c->image_path) }}"
                                         style="width:38px;height:38px;object-fit:cover;border-radius:8px;border:2px solid var(--border)"
                                         onerror="this.replaceWith(document.createTextNode('💎'))">
                                @else
                                    <div style="width:38px;height:38px;background:#f5f5f5;border-radius:8px;display:flex;align-items:center;justify-content:center">💎</div>
                                @endif
                            </td>

                            <td>
                                <span style="background:var(--bg);padding:3px 10px;border-radius:20px;font-size:11px;font-weight:600">
                                    {{ $c->stone_name }}
                                </span>
                            </td>

                            <td>{{ $c->metal_en ?? $c->metal }}</td>

                            <td>{{ $c->length_clean }}×{{ $c->width_clean }}</td>

                            <td>{{ $c->weight_clean }}</td>

                            <td style="font-size:10.5px">
                                {{ \App\Support\PersianDate::format($c->issued_at ?? $c->created_at, 'Y/m/d') }}
                            </td>

                            <td>
                                <div class="sg-action-btns">
                                    <button type="button"
                                            onclick="Livewire.dispatch('open-cert-view', { certId: {{ $c->id }} })"
                                            class="sg-action-btn view" title="نمایش">👁️</button>

                                    <button type="button"
                                            onclick="Livewire.dispatch('open-cert-form', { certId: {{ $c->id }} })"
                                            class="sg-action-btn edit" title="ویرایش">✏️</button>

                                    <button type="button"
                                            onclick="downloadCert({{ $c->id }}, '{{ $c->code }}')"
                                            class="sg-action-btn"
                                            style="background:rgba(8,145,178,.15);color:#0891b2"
                                            title="دانلود PNG">📥</button>

                                    <button wire:click="delete({{ $c->id }})"
                                            wire:confirm="حذف شود؟"
                                            class="sg-action-btn delete" title="حذف">🗑️</button>
                                </div>
                            </td>
                        </tr>
                    @empty
                        <tr>
                            <td colspan="9">
                                <div style="text-align:center;padding:40px;color:var(--text-light)">
                                    <div style="font-size:44px;opacity:.5">💎</div>
                                    <p>شناسنامه‌ای نیست</p>
                                    <button type="button" onclick="Livewire.dispatch('open-cert-form')"
                                            class="btn btn-primary btn-sm" style="margin-top:10px">
                                        ➕ اولین شناسنامه
                                    </button>
                                </div>
                            </td>
                        </tr>
                    @endforelse
                </tbody>
            </table>
        </div>

        <div style="padding:14px">{{ $certificates->links() }}</div>
    </div>
</div>


<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script>
function downloadCert(id, code) {
    // استفاده از پنجره مخفی + html2canvas
    var w = window.open('', '_blank', 'width=900,height=900');
    if (!w) { alert('پاپ‌آپ بلاک شده — لطفا اجازه بده'); return; }

    // لود HTML کارت
    fetch('/certificates/' + id + '/render')
        .then(function(r) {
            if (!r.ok) throw new Error('HTTP ' + r.status);
            return r.text();
        })
        .then(function(html) {
            w.document.open();
            w.document.write(html);
            w.document.close();

            // صبر کن چیزها لود بشن
            setTimeout(function() {
                var card = w.document.querySelector('.certificate');
                if (!card) {
                    w.close();
                    alert('کارت در HTML نبود');
                    return;
                }

                html2canvas(card, {
                    scale: 3,
                    backgroundColor: '#fffef9',
                    useCORS: true,
                    allowTaint: true,
                    logging: false,
                    onclone: function(clonedDoc) {
                        var c = clonedDoc.querySelector('.certificate');
                        if (!c) return;
                        var els = [c].concat(Array.from(c.querySelectorAll('*')));
                        els.forEach(function(el) {
                            var cs = w.getComputedStyle(el);
                            ['color', 'backgroundColor', 'borderColor', 'fill', 'stroke'].forEach(function(prop) {
                                try {
                                    var val = cs[prop];
                                    if (val && val.indexOf('oklch') !== -1) el.style[prop] = '#999999';
                                } catch (e) {}
                            });
                        });
                    }
                }).then(function(canvas) {
                    var a = w.document.createElement('a');
                    a.download = 'cert-' + code + '.png';
                    a.href = canvas.toDataURL('image/png');
                    a.click();
                    setTimeout(function() { w.close(); }, 1500);
                }).catch(function(e) {
                    w.close();
                    alert('خطا: ' + e.message);
                });
            }, 2000);
        })
        .catch(function(e) {
            w.close();
            alert('خطا: ' + e.message);
        });
}
</script>
