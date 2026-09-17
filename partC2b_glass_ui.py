from pathlib import Path
import textwrap

PROJECT = Path.home() / "projects" / "shopgun-v2.1"
if not PROJECT.exists():
    raise SystemExit("❌ پروژه پیدا نشد")

def write_file(rel, content):
    path = PROJECT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    existed = path.exists()
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    print(f"{'🔁' if existed else '✅'} {rel}")

print("═" * 60)
print("🎨 Part C-2 (بخش ۲) — Glass UI + اتصال Designer")
print("═" * 60)
print()

# =========================================================
# ۱. CertRenderer Service — رندر کارت با طراحی ذخیره‌شده
# =========================================================

write_file("app/Services/CertRenderer.php", r"""
<?php

namespace App\Services;

use App\Models\Certificate;
use App\Support\CertConfig;

class CertRenderer
{
    /**
     * رندر یه کارت شناسنامه به HTML (برای چاپ/PNG)
     */
    public static function renderHtml(Certificate $cert, array $opts = []): string
    {
        $sizes  = CertConfig::sizes();
        $assets = CertConfig::assets();
        $hide   = CertConfig::hideDesc();
        $design = $cert->design_or_default;

        // ابعاد پیکسلی
        $pxW = (int) round($sizes['width']  * 96 / 2.54);
        $pxH = (int) round($sizes['height'] * 96 / 2.54);

        $scale = $sizes['width'] / 6.5;

        $imgW = (int) round($sizes['img_w'] * $scale);
        $imgH = (int) round($sizes['img_h'] * $scale);
        $qrS  = (int) round($sizes['qr_size'] * $scale);
        $logoW = (int) round($sizes['logo_w'] * $scale);
        $logoH = (int) round($sizes['logo_h'] * $scale);

        $bgStyle = $assets['bg_image'] ? "background-image:url('{$assets['bg_image']}');" : '';

        $imgSrc = $cert->image_path ? asset('storage/' . $cert->image_path) : '';
        $qrUrl  = $cert->qr_url;

        // جایگذاری متغیرها
        $vars = [
            '{code}'      => $cert->code,
            '{serial}'    => $cert->serial ?? '',
            '{stoneName}' => $cert->stone_name ?? '',
            '{stoneEn}'   => $cert->stone_en ?? '',
            '{origin}'    => $cert->stone_origin ?? '',
            '{metal}'     => $cert->metal ?? '',
            '{metalEn}'   => $cert->metal_en ?? $cert->metal ?? '',
            '{carat}'     => $cert->metal_carat ?? '',
            '{length}'    => $cert->length,
            '{width}'     => $cert->width,
            '{weight}'    => $cert->weight,
            '{brilliant}' => $cert->brilliant,
        ];

        // عناصر طراحی
        $elementsHtml = '';
        if (! empty($design['elements'])) {
            foreach ($design['elements'] as $el) {
                $x = (int) ($el['x'] ?? 0);
                $y = (int) ($el['y'] ?? 0);

                if (($el['type'] ?? '') === 'text') {
                    $text = strtr($el['text'] ?? '', $vars);
                    $fs   = (int) ($el['fontSize'] ?? 14);
                    $fill = $el['fill'] ?? '#334155';
                    $fw   = $el['fontWeight'] ?? 'normal';
                    $elementsHtml .= "<div style='position:absolute;left:{$x}px;top:{$y}px;font-size:{$fs}px;color:{$fill};font-weight:{$fw};font-family:Tahoma,sans-serif;'>{$text}</div>";
                } elseif (($el['type'] ?? '') === 'qr') {
                    $size = (int) ($el['size'] ?? 100);
                    $elementsHtml .= "<img src='{$qrUrl}' style='position:absolute;left:{$x}px;top:{$y}px;width:{$size}px;height:{$size}px;' />";
                }
            }
        }

        // پنل QR + لوگو (پایین چپ)
        $qrPanel = '';
        if ($qrS > 0) {
            $qrPanel = "<div style='position:absolute;bottom:4px;left:4px;display:flex;gap:4px;align-items:center;'>";
            if ($assets['logo_image']) {
                $qrPanel .= "<img src='{$assets['logo_image']}' style='width:{$logoW}px;height:{$logoH}px;object-fit:contain;' />";
            }
            $qrPanel .= "<img src='{$qrUrl}' style='width:{$qrS}px;height:{$qrS}px;' />";
            $qrPanel .= "</div>";
        }

        // تصویر محصول (راست)
        $imgPanel = '';
        if ($imgSrc) {
            $imgPanel = "<img src='{$imgSrc}' style='position:absolute;top:4px;right:4px;width:{$imgW}px;height:{$imgH}px;object-fit:contain;border:1px solid #b8860b;border-radius:4px;background:#fff;' />";
        }

        // توضیحات
        $descPanel = '';
        if (! $hide && $assets['desc_image']) {
            $descPanel = "<img src='{$assets['desc_image']}' style='position:absolute;bottom:4px;right:4px;max-width:40%;max-height:30%;object-fit:contain;' />";
        }

        return <<<HTML
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<title>Certificate {$cert->code}</title>
<style>
    @page { size: A4; margin: 8mm; }
    * { box-sizing: border-box; margin: 0; padding: 0; }
    body { background: #fff; font-family: Tahoma, sans-serif; }

    .cert {
        position: relative;
        width: {$pxW}px;
        height: {$pxH}px;
        background-color: #fffef9;
        {$bgStyle}
        background-size: cover;
        background-position: center;
        border: 1.5px solid #b8860b;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,.15);
    }
    .cert .content {
        position: relative;
        width: 100%;
        height: 100%;
        padding: 8px;
    }
</style>
</head>
<body>
<div class="cert">
    <div class="content">
        {$elementsHtml}
        {$imgPanel}
        {$descPanel}
        {$qrPanel}
    </div>
</div>
</body>
</html>
HTML;
    }

    /**
     * رندر لیست کارت‌ها روی یه صفحه A4 (چندتایی)
     */
    public static function renderBatchHtml(array $certs, int $cols = 3): string
    {
        $sizes = CertConfig::sizes();
        $cssW  = $sizes['width'];
        $cssH  = $sizes['height'];

        $gap = $cols === 1 ? 0 : round((210 - ($cols * $cssW) - 6) / max(1, $cols - 1), 2);

        $cards = '';
        foreach ($certs as $cert) {
            $html = self::renderHtml($cert);

            // فقط بدنه‌ی کارت رو استخراج کن
            if (preg_match('/<body>(.*)<\/body>/s', $html, $m)) {
                $bodyContent = $m[1];
            } else {
                $bodyContent = $html;
            }

            $cards .= "<div class='batch-card'>{$bodyContent}</div>";
        }

        return <<<HTML
<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
<meta charset="UTF-8">
<title>Batch Print</title>
<style>
    @page { size: A4; margin: 6mm; }
    * { box-sizing: border-box; margin: 0; padding: 0; -webkit-print-color-adjust: exact; print-color-adjust: exact; }
    body { background: #fff; }

    .grid {
        display: grid;
        grid-template-columns: repeat({$cols}, {$cssW}cm);
        column-gap: {$gap}cm;
        row-gap: 3mm;
        justify-content: center;
    }

    .batch-card .cert {
        width: {$cssW}cm !important;
        height: {$cssH}cm !important;
        page-break-inside: avoid;
        break-inside: avoid;
    }
</style>
</head>
<body>
<div class="grid">
    {$cards}
</div>
</body>
</html>
HTML;
    }
}
""")

# =========================================================
# ۲. Certificates/Show — کارت مربعی + دکمه‌های عملیات
# =========================================================

write_file("app/Livewire/Certificates/Show.php", r"""
<?php

namespace App\Livewire\Certificates;

use App\Models\Certificate;
use App\Services\CertRenderer;
use App\Support\CertConfig;
use Livewire\Component;

class Show extends Component
{
    public Certificate $certificate;
    public string $html = '';

    public function mount(Certificate $certificate): void
    {
        $this->certificate = $certificate->load(['customer', 'order']);
        $this->html = CertRenderer::renderHtml($this->certificate);
    }

    public function delete()
    {
        $code = $this->certificate->code;
        $this->certificate->delete();
        session()->flash('success', "شناسنامه #{$code} حذف شد.");
        return redirect()->route('certificates.index');
    }

    public function render()
    {
        return view('livewire.certificates.show', [
            'sizes' => CertConfig::sizes(),
        ])->layout('components.layouts.app');
    }
}
""")

write_file("resources/views/livewire/certificates/show.blade.php", r"""
<div class="p-4 md:p-6 max-w-5xl mx-auto">

    <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
        <div class="flex items-center gap-3">
            <a href="{{ route('certificates.index') }}" class="btn btn-ghost btn-sm">→</a>
            <div>
                <h1 class="text-xl md:text-2xl font-bold">شناسنامه #{{ $certificate->code }}</h1>
                <div class="text-xs text-base-content/60 mt-0.5 font-mono" dir="ltr">{{ $certificate->serial }}</div>
            </div>
        </div>
        <div class="flex flex-wrap gap-2">
            <a href="{{ $certificate->public_url }}" target="_blank" class="btn btn-outline btn-sm">🔗 لینک</a>
            <a href="{{ route('certificates.designer', $certificate->id) }}" class="btn btn-secondary btn-sm">🎨 ویرایشگر</a>
            <button onclick="printCurrentCert()" class="btn btn-info btn-sm">🖨️ چاپ</button>
            <button onclick="exportCurrentCertPng()" class="btn btn-success btn-sm">📸 PNG</button>
            <button wire:click="delete" wire:confirm="حذف شود؟" class="btn btn-error btn-sm">🗑️</button>
        </div>
    </div>

    @if (session('success'))
        <div class="alert alert-success mb-4 text-sm"><span>{{ session('success') }}</span></div>
    @endif

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-4">

        {{-- پیش‌نمایش کارت --}}
        <div class="lg:col-span-2 card bg-base-100 shadow border">
            <div class="card-body items-center">
                <h2 class="font-bold text-base mb-3 w-full">🎴 پیش‌نمایش کارت</h2>
                <div class="bg-base-200 rounded-lg p-4 flex justify-center overflow-auto w-full"
                     id="certPreviewStage">
                    <iframe id="certPreviewFrame"
                            style="width: {{ $sizes['width'] * 60 }}px; height: {{ $sizes['height'] * 60 }}px; border: 0; background: #fff;"
                            srcdoc="{{ htmlspecialchars($html, ENT_QUOTES) }}"></iframe>
                </div>
                <div class="text-xs text-base-content/60 mt-2">
                    ابعاد: {{ $sizes['width'] }}×{{ $sizes['height'] }} سانتی‌متر
                </div>
            </div>
        </div>

        {{-- اطلاعات --}}
        <div class="card bg-base-100 shadow border">
            <div class="card-body">
                <h2 class="font-bold text-base mb-3">📋 مشخصات</h2>
                <div class="space-y-2 text-sm">
                    <div class="flex justify-between p-2 rounded bg-base-200/50">
                        <span class="text-base-content/60">💎 سنگ:</span>
                        <span class="font-bold">{{ $certificate->stone_name }}</span>
                    </div>
                    <div class="flex justify-between p-2 rounded bg-base-200/50">
                        <span class="text-base-content/60">⚙️ فلز:</span>
                        <span>{{ $certificate->metal }} ({{ $certificate->metal_carat }})</span>
                    </div>
                    <div class="flex justify-between p-2 rounded bg-base-200/50">
                        <span class="text-base-content/60">📐 ابعاد:</span>
                        <span>{{ $certificate->length }}×{{ $certificate->width }} mm</span>
                    </div>
                    <div class="flex justify-between p-2 rounded bg-base-200/50">
                        <span class="text-base-content/60">⚖️ وزن:</span>
                        <span>{{ $certificate->weight }} gr</span>
                    </div>
                    @if($certificate->customer)
                        <div class="flex justify-between p-2 rounded bg-base-200/50">
                            <span class="text-base-content/60">👤 مشتری:</span>
                            <a href="{{ route('customers.show', $certificate->customer) }}" class="link link-primary font-bold">
                                {{ $certificate->customer->name }}
                            </a>
                        </div>
                    @endif
                    @if($certificate->order)
                        <div class="flex justify-between p-2 rounded bg-base-200/50">
                            <span class="text-base-content/60">📦 سفارش:</span>
                            <a href="{{ route('orders.show', $certificate->order) }}" class="link link-primary font-bold">
                                #{{ $certificate->order->order_number }}
                            </a>
                        </div>
                    @endif
                </div>
            </div>
        </div>
    </div>
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script>
function getPreviewFrame() {
    return document.getElementById('certPreviewFrame');
}

function printCurrentCert() {
    const frame = getPreviewFrame();
    const win = window.open('', '', 'width=800,height=800');
    win.document.write(frame.srcdoc);
    win.document.close();
    setTimeout(() => {
        win.print();
        setTimeout(() => win.close(), 500);
    }, 500);
}

function exportCurrentCertPng() {
    const frame = getPreviewFrame();
    const doc = frame.contentDocument || frame.contentWindow.document;
    const cert = doc.querySelector('.cert');
    if (!cert) { alert('کارت پیدا نشد'); return; }

    // بزرگ‌نمایی قبل از capture
    const oldTransform = cert.style.transform;
    const oldTransformOrigin = cert.style.transformOrigin;
    const targetW = Math.round({{ $sizes['width'] }} * 300 / 2.54);
    const realW = cert.offsetWidth;
    const scale = targetW / realW;
    cert.style.transform = 'scale(' + scale + ')';
    cert.style.transformOrigin = 'top right';

    html2canvas(cert, {
        scale: 1,
        backgroundColor: '#fffef9',
        useCORS: true,
        allowTaint: true,
        width: cert.offsetWidth * scale,
        height: cert.offsetHeight * scale,
        windowWidth: cert.offsetWidth * scale,
        windowHeight: cert.offsetHeight * scale,
    }).then(canvas => {
        cert.style.transform = oldTransform;
        cert.style.transformOrigin = oldTransformOrigin;

        const a = document.createElement('a');
        a.download = 'certificate-{{ $certificate->code }}.png';
        a.href = canvas.toDataURL('image/png');
        a.click();
    }).catch(err => {
        console.error(err);
        alert('خطا در ساخت PNG');
    });
}
</script>
""")

# =========================================================
# ۳. Certificates/Index — با دکمه‌های کامل
# =========================================================

write_file("resources/views/livewire/certificates/index.blade.php", r"""
<div class="p-4 md:p-6 space-y-4">

    @if (session('success'))
        <div class="alert alert-success text-sm py-2"><span>{{ session('success') }}</span></div>
    @endif

    <div class="flex flex-wrap items-center justify-between gap-3">
        <h1 class="text-xl md:text-2xl font-bold">💎 شناسنامه‌ها</h1>
        <div class="flex gap-2">
            <a href="{{ route('certificates.designer') }}" class="btn btn-secondary btn-sm">🎨 ویرایشگر</a>
            <a href="{{ route('certificates.create') }}" class="btn btn-primary btn-sm">➕ شناسنامه جدید</a>
        </div>
    </div>

    <div class="bg-base-100 rounded-lg shadow border p-3">
        <input type="text" wire:model.live.debounce.400ms="search"
               placeholder="🔍 کد، SKU، سنگ..." class="input input-bordered input-sm w-full md:w-80" />
    </div>

    <div class="bg-base-100 rounded-lg shadow border overflow-hidden">
        <div class="pro-table-wrap">
            <table class="pro-table">
                <thead>
                    <tr>
                        <th>کد</th>
                        <th>SKU</th>
                        <th>سنگ</th>
                        <th>فلز</th>
                        <th>ابعاد</th>
                        <th>وزن</th>
                        <th>مشتری</th>
                        <th>تاریخ</th>
                        <th>عملیات</th>
                    </tr>
                </thead>
                <tbody>
                    @forelse($certificates as $c)
                        <tr>
                            <td class="font-mono font-bold">
                                <a href="{{ route('certificates.show', $c) }}" class="link link-primary">{{ $c->code }}</a>
                            </td>
                            <td class="font-mono text-xs" dir="ltr">{{ $c->sku ?? '—' }}</td>
                            <td><span class="badge badge-outline badge-sm">{{ $c->stone_name }}</span></td>
                            <td class="text-xs">{{ $c->metal_en ?? $c->metal }}</td>
                            <td class="text-xs">{{ $c->length }}×{{ $c->width }}</td>
                            <td class="text-xs">{{ $c->weight }}</td>
                            <td class="text-xs">{{ $c->customer?->name ?? '—' }}</td>
                            <td class="text-xs">{{ $c->issued_at?->format('Y/m/d') }}</td>
                            <td>
                                <div class="flex gap-1">
                                    <a href="{{ route('certificates.show', $c) }}" class="btn btn-ghost btn-xs" title="نمایش">👁️</a>
                                    <a href="{{ route('certificates.designer', $c->id) }}" class="btn btn-ghost btn-xs" title="ویرایش طراحی">🎨</a>
                                    <button wire:click="delete({{ $c->id }})" wire:confirm="حذف شود؟"
                                            class="btn btn-ghost btn-xs text-error" title="حذف">🗑️</button>
                                </div>
                            </td>
                        </tr>
                    @empty
                        <tr><td colspan="9" class="text-center py-8 text-base-content/50">شناسنامه‌ای نیست</td></tr>
                    @endforelse
                </tbody>
            </table>
        </div>
    </div>

    <div>{{ $certificates->links() }}</div>
</div>
""")

# =========================================================
# ۴. Layout شیشه‌ای — Sidebar + Bottom Bar + Header
# =========================================================

write_file("resources/views/components/layouts/app.blade.php", r"""
<!DOCTYPE html>
<html lang="fa" dir="rtl" data-theme="light">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="csrf-token" content="{{ csrf_token() }}">
    <title>ShopGun — شاپگان</title>
    <link href="https://cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/Vazirmatn-font-face.css" rel="stylesheet">
    <script>
        (function() {
            const t = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', t);
        })();
    </script>
    @vite(['resources/css/app.css', 'resources/js/app.js'])
    @livewireStyles
</head>
<body class="min-h-screen bg-base-200 font-sans text-base-content">

    @auth
        <livewire:global-search />
        <livewire:components.shipment-timeline />
    @endauth

    {{-- Container اصلی --}}
    <div class="flex min-h-screen">

        {{-- =============== Sidebar (Desktop فقط) =============== --}}
        <aside class="hidden lg:flex flex-col w-64 shrink-0 p-4 sticky top-0 h-screen">
            <div class="glass-panel rounded-2xl flex flex-col h-full overflow-hidden">

                {{-- لوگو --}}
                <div class="p-4 border-b border-white/10">
                    <div class="flex items-center gap-3">
                        <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-cyan-400 to-teal-600 flex items-center justify-center text-white font-extrabold text-lg shadow-lg">
                            S
                        </div>
                        <div>
                            <div class="font-extrabold text-base">شاپگان</div>
                            <div class="text-[10px] text-base-content/50">ShopGun v2.1</div>
                        </div>
                    </div>
                </div>

                {{-- منو --}}
                <nav class="flex-1 overflow-y-auto p-3">
                    <ul class="space-y-1">
                        @php
                            $menuItems = [
                                ['route' => 'dashboard',         'icon' => '🏠', 'label' => 'داشبورد'],
                                ['route' => 'orders.index',      'icon' => '📦', 'label' => 'سفارشات'],
                                ['route' => 'customers.index',   'icon' => '👥', 'label' => 'مشتریان'],
                                ['route' => 'certificates.index','icon' => '💎', 'label' => 'شناسنامه‌ها'],
                                ['route' => 'reports.index',     'icon' => '📊', 'label' => 'گزارش‌ها'],
                                ['route' => 'activity-log',      'icon' => '📜', 'label' => 'لاگ'],
                                ['route' => 'settings.index',    'icon' => '⚙️', 'label' => 'تنظیمات'],
                            ];
                        @endphp

                        @foreach($menuItems as $m)
                            @php
                                $isActive = request()->routeIs($m['route']) || request()->routeIs(explode('.', $m['route'])[0] . '.*');
                            @endphp
                            <li>
                                <a href="{{ route($m['route']) }}"
                                   class="flex items-center gap-3 px-3 py-2.5 rounded-xl transition-all
                                          {{ $isActive
                                              ? 'bg-primary/20 text-primary font-bold shadow-inner border border-primary/30'
                                              : 'text-base-content/70 hover:bg-base-200/50 hover:text-base-content' }}">
                                    <span class="text-lg">{{ $m['icon'] }}</span>
                                    <span class="text-sm">{{ $m['label'] }}</span>
                                </a>
                            </li>
                        @endforeach
                    </ul>
                </nav>

                {{-- پایین --}}
                <div class="p-3 border-t border-white/10 text-[10px] text-center text-base-content/40">
                    گروه هنری اقاقیا · ۱۴۰۵
                </div>
            </div>
        </aside>

        {{-- =============== محتوای اصلی =============== --}}
        <div class="flex-1 min-w-0 flex flex-col">

            {{-- =============== Header شیشه‌ای =============== --}}
            <header class="sticky top-0 z-30 p-3 md:p-4">
                <div class="glass-panel rounded-2xl px-4 py-2.5 flex items-center justify-between gap-3 shadow-lg">

                    {{-- چپ: لوگو موبایل + جستجو --}}
                    <div class="flex items-center gap-3 flex-1 min-w-0">
                        <div class="lg:hidden flex items-center gap-2">
                            <div class="w-8 h-8 rounded-lg bg-gradient-to-br from-cyan-400 to-teal-600 flex items-center justify-center text-white font-extrabold text-sm shadow">S</div>
                        </div>

                        <button onclick="window.dispatchEvent(new KeyboardEvent('keydown', {key: 'k', ctrlKey: true}))"
                                class="hidden md:flex items-center gap-2 px-3 py-1.5 rounded-lg bg-base-200/60 hover:bg-base-200 text-xs text-base-content/60 border border-base-300/50 transition">
                            <span>🔍 جستجو</span>
                            <kbd class="kbd kbd-xs">Ctrl+K</kbd>
                        </button>
                    </div>

                    {{-- راست: تم + اعلان + کاربر --}}
                    <div class="flex items-center gap-2">
                        <button onclick="toggleTheme()" class="btn btn-ghost btn-sm btn-circle" title="تغییر تم">
                            <span id="themeIcon">🌙</span>
                        </button>

                        @auth
                            <livewire:notification-center />
                        @endauth

                        <div class="dropdown dropdown-end">
                            <div tabindex="0" role="button" class="btn btn-ghost btn-sm gap-2 px-1.5">
                                <div class="avatar placeholder">
                                    <div class="bg-gradient-to-br from-cyan-400 to-teal-600 text-white rounded-full w-8">
                                        <span class="text-xs font-bold">{{ mb_substr(Auth::user()->name ?? '؟', 0, 1) }}</span>
                                    </div>
                                </div>
                                <span class="hidden sm:inline text-xs">{{ Auth::user()->name ?? 'کاربر' }}</span>
                            </div>
                            <ul tabindex="0" class="dropdown-content menu glass-panel rounded-2xl z-[1] w-52 p-2 mt-2">
                                <li><a href="{{ route('settings.index') }}">⚙️ تنظیمات</a></li>
                                <li><a href="{{ route('activity-log') }}">📜 لاگ</a></li>
                                <li>
                                    <form method="POST" action="{{ route('logout') }}">
                                        @csrf
                                        <button type="submit" class="w-full text-right">🚪 خروج</button>
                                    </form>
                                </li>
                            </ul>
                        </div>
                    </div>
                </div>
            </header>

            {{-- =============== محتوا =============== --}}
            <main class="flex-1 pb-24 lg:pb-6">
                {{ $slot }}
            </main>

            {{-- =============== Bottom Bar (Mobile فقط) =============== --}}
            <nav class="lg:hidden fixed bottom-3 left-3 right-3 z-40">
                <div class="glass-panel rounded-2xl shadow-2xl px-1 py-1.5 overflow-x-auto no-scrollbar">
                    <div class="flex gap-1 min-w-max justify-around">
                        @php
                            $bottomItems = [
                                ['route' => 'dashboard',         'icon' => '🏠', 'label' => 'خانه'],
                                ['route' => 'orders.index',      'icon' => '📦', 'label' => 'سفارش'],
                                ['route' => 'customers.index',   'icon' => '👥', 'label' => 'مشتری'],
                                ['route' => 'certificates.index','icon' => '💎', 'label' => 'کارت'],
                                ['route' => 'reports.index',     'icon' => '📊', 'label' => 'گزارش'],
                                ['route' => 'settings.index',    'icon' => '⚙️', 'label' => 'تنظیم'],
                            ];
                        @endphp

                        @foreach($bottomItems as $m)
                            @php
                                $isActive = request()->routeIs($m['route']) || request()->routeIs(explode('.', $m['route'])[0] . '.*');
                            @endphp
                            <a href="{{ route($m['route']) }}"
                               class="flex flex-col items-center justify-center gap-0.5 min-w-[60px] py-1.5 px-2 rounded-xl transition-all relative
                                      {{ $isActive ? 'bg-primary/20 text-primary' : 'text-base-content/60' }}">
                                <span class="text-xl leading-none">{{ $m['icon'] }}</span>
                                <span class="text-[10px] font-bold leading-none mt-0.5">{{ $m['label'] }}</span>
                                @if($isActive)
                                    <span class="absolute -top-1 right-1/2 translate-x-1/2 w-1.5 h-1.5 rounded-full bg-primary"></span>
                                @endif
                            </a>
                        @endforeach
                    </div>
                </div>
            </nav>

        </div>
    </div>

    <script>
        function toggleTheme() {
            const html = document.documentElement;
            const cur = html.getAttribute('data-theme') || 'light';
            const next = cur === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', next);
            localStorage.setItem('theme', next);
            document.getElementById('themeIcon').textContent = next === 'dark' ? '☀️' : '🌙';
        }
        document.addEventListener('DOMContentLoaded', () => {
            const cur = document.documentElement.getAttribute('data-theme');
            const icon = document.getElementById('themeIcon');
            if (icon) icon.textContent = cur === 'dark' ? '☀️' : '🌙';
        });
    </script>

    @livewireScripts
</body>
</html>
""")

# =========================================================
# ۵. CSS — Glass Panels + Bottom Bar
# =========================================================

css = PROJECT / "resources/css/app.css"
if css.exists():
    content = css.read_text(encoding="utf-8")

    if "glass-panel" not in content:
        content += """

/* =========================================================
   Glass Panels
   ========================================================= */

.glass-panel {
    background: rgba(255, 255, 255, 0.72);
    backdrop-filter: blur(20px) saturate(180%);
    -webkit-backdrop-filter: blur(20px) saturate(180%);
    border: 1px solid rgba(255, 255, 255, 0.4);
    box-shadow:
        0 4px 16px rgba(15, 23, 42, 0.06),
        inset 0 1px 0 rgba(255, 255, 255, 0.5);
}

[data-theme="dark"] .glass-panel {
    background: rgba(15, 30, 30, 0.72);
    border-color: rgba(125, 211, 208, 0.15);
    box-shadow:
        0 4px 16px rgba(0, 0, 0, 0.4),
        inset 0 1px 0 rgba(125, 211, 208, 0.1);
}

/* Bottom nav scroll */
.no-scrollbar::-webkit-scrollbar { display: none; }
.no-scrollbar { -ms-overflow-style: none; scrollbar-width: none; }

/* Body padding for bottom bar */
@media (max-width: 1023px) {
    body { padding-bottom: 0; }
}

/* Smooth sidebar */
aside { transition: width 0.3s ease; }

/* Fix sidebar menu active state */
aside nav a.active {
    background: rgba(20, 184, 166, 0.15);
}
"""
        css.write_text(content, encoding="utf-8")
        print("🔁 resources/css/app.css (glass panels)")
    else:
        print("✅ resources/css/app.css (بدون تغییر)")

print()
print("═" * 60)
print("✅ Part C-2 (بخش ۲) — Glass UI + اتصال Designer")
print("═" * 60)
print()
print("📌 اجرا کن:")
print("   php artisan optimize:clear")
print("   npm run build")
print("   php artisan serve --host=0.0.0.0 --port=8080")
print()
print("🎯 تست کن:")
print("   /certificates          ← جدول با دکمه‌های جدید")
print("   /certificates/{id}     ← کارت مربعی + چاپ + PNG")
print("   /certificates/designer ← طراحی با سایز")
print()
