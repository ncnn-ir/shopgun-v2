# -*- coding: utf-8 -*-
from pathlib import Path
import time

ROOT = Path(r'D:\prodo\shopgun-v2.2')

p = ROOT / 'resources' / 'views' / 'livewire' / 'certificates' / 'index.blade.php'
if p.exists():
    p.rename(str(p) + '.bak-' + str(int(time.time())))
    print("[OK] backup")

CONTENT = r'''<div>

    {{-- ═══ Toolbar ═══ --}}
    <div class="sg-toolbar">
        <div class="sg-toolbar-right">
            <input type="text" wire:model.live.debounce.400ms="search"
                   placeholder="🔍 کد/SKU/سنگ..." class="form-control" style="width:220px">
        </div>
        <div style="display:flex;gap:6px">
            <a href="{{ route('certificates.designer') }}" wire:navigate
               class="btn btn-secondary btn-sm">🎨 ویرایشگر</a>
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
    fetch('/certificates/' + id + '/render')
        .then(function(r) {
            if (!r.ok) throw new Error('HTTP ' + r.status);
            return r.text();
        })
        .then(function(html) {
            var iframe = document.createElement('iframe');
            iframe.style.cssText = 'position:fixed;left:-99999px;top:0;width:1400px;height:1400px;border:0';
            document.body.appendChild(iframe);

            var doc = iframe.contentDocument || iframe.contentWindow.document;
            doc.open();
            doc.write(html);
            doc.close();

            setTimeout(function() {
                var card = doc.querySelector('.certificate');
                if (!card) {
                    document.body.removeChild(iframe);
                    alert('کارت پیدا نشد');
                    return;
                }

                var cw = card.offsetWidth || 600;
                var ch = card.offsetHeight || 600;

                html2canvas(card, {
                    scale: 3,
                    backgroundColor: '#fffef9',
                    useCORS: true,
                    allowTaint: true,
                    logging: false,
                    width: cw,
                    height: ch,
                    windowWidth: cw,
                    windowHeight: ch,
                    onclone: function(clonedDoc) {
                        var clonedCard = clonedDoc.querySelector('.certificate');
                        if (!clonedCard) return;
                        var els = [clonedCard].concat(Array.from(clonedCard.querySelectorAll('*')));
                        els.forEach(function(el) {
                            var cs = window.getComputedStyle(el);
                            ['color', 'backgroundColor', 'borderColor', 'fill', 'stroke'].forEach(function(prop) {
                                var val = cs[prop];
                                if (val && val.indexOf('oklch') !== -1) {
                                    el.style[prop] = '#999999';
                                }
                            });
                        });
                    }
                }).then(function(canvas) {
                    document.body.removeChild(iframe);
                    var a = document.createElement('a');
                    a.download = 'cert-' + code + '.png';
                    a.href = canvas.toDataURL('image/png');
                    a.click();
                }).catch(function(e) {
                    document.body.removeChild(iframe);
                    alert('خطا: ' + e.message);
                });
            }, 1800);
        })
        .catch(function(e) {
            alert('خطا در دریافت HTML: ' + e.message);
        });
}
</script>
'''

p.write_text(CONTENT, encoding='utf-8')
print("[OK] certificates/index.blade.php بازنویسی شد")

print()
print("Run:")
print("  php artisan view:clear")
print("  php artisan optimize:clear")
print("  php artisan serve")