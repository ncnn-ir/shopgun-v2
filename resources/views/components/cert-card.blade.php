{{--
╔══════════════════════════════════════════════════════════════╗
║  Certificate Card Component — ShopGun V2                     ║
║  بر اساس «جواهری مشاهیر v6.14»                                ║
╚══════════════════════════════════════════════════════════════╝

استفاده:
    <x-cert-card :certificate="$cert" />
    <x-cert-card :certificate="$cert" width="7" height="7" />
--}}

@props([
    'certificate',
    'width'   => 6.5,
    'height'  => 6.5,
    'logos'   => [],
    'bgImage' => null,
    'descImage' => null,
    'hideDesc'  => false,
])

@php
    use App\Support\PersianNumber;

    $code      = $certificate->code;
    $serial    = $certificate->serial ?? '';
    $stoneEn   = $certificate->stone?->name_en ?? $certificate->stone_name_en ?? '';
    $stoneName = $certificate->stone?->name ?? $certificate->stone_name ?? '';
    $metalEn   = $certificate->metal?->name_en ?? $certificate->metal_name_en ?? '';
    $carat     = $certificate->metal?->carat ?? $certificate->metal_carat ?? '';

    $origin    = $certificate->stone?->origin_en ?? $certificate->origin_en ?? '';
    $flag      = $certificate->stone?->flag ?? $certificate->stone_flag ?? '';

    // ★ حذف .00 اضافه
    $length = rtrim(rtrim(number_format((float)($certificate->length ?? 0), 2, '.', ''), '0'), '.');
    $width_ = rtrim(rtrim(number_format((float)($certificate->width  ?? 0), 2, '.', ''), '0'), '.');
    $weight = rtrim(rtrim(number_format((float)($certificate->weight ?? 0), 2, '.', ''), '0'), '.');
    $brilliant = $certificate->brilliant ?? 0;
    $stones = $length . '*' . $width_;

    $url   = "https://mashahirid.ir/Q/{$code}";
    $qrUrl = 'https://api.qrserver.com/v1/create-qr-code/?size=200x200&margin=1&data=' . urlencode($url);

    // ★ تصویر: اولویت با image_url (سرور)، سپس image (Base64)
    $imageUrl = $certificate->image_url ?? '';
    if (!$imageUrl && !empty($certificate->image) && str_starts_with($certificate->image, 'data:')) {
        $imageUrl = $certificate->image;
    }

    $pxW = (int) round($width  * 96 / 2.54);
    $pxH = (int) round($height * 96 / 2.54);

    $flagUrl = $flag ? 'https://flagcdn.com/w40/' . strtolower($flag) . '.png' : '';
@endphp

<div class="cert-wrapper" data-cert-code="{{ $code }}" wire:key="cert-{{ $code }}">
    <div class="certificate {{ $hideDesc ? 'cert-desc-hidden' : '' }}"
         style="width: {{ $pxW }}px; height: {{ $pxH }}px;">

        {{-- پس‌زمینه --}}
        @if($bgImage)
            <div class="cert-bg-layer" style="background-image: url('{{ $bgImage }}')"></div>
        @endif

        <div class="cert-main">
            {{-- بخش بالا: متن + تصویر --}}
            <div class="cert-top-section">
                <div class="cert-right-text">
                    <div class="cert-title-script">Certificate</div>
                    <div class="cert-subtitle-script">Quality Guarantee</div>

                    <div class="cert-desc-area">
                        @if($descImage)
                            <img src="{{ $descImage }}" alt="">
                        @else
                            <div class="cert-auth-text">
                                This certificate is only for authenticity of purchased product.
                            </div>
                        @endif
                    </div>

                    <div class="cert-sig-block">
                        <div class="cert-sig-line">Quality Guarantee</div>
                        <div class="cert-sig-label">تضمین کیفیت</div>
                    </div>
                </div>

                <div class="cert-img-frame-wrap">
                    <div class="cert-img-frame">
                        @if($imageUrl)
                            <img src="{{ $imageUrl }}" alt="" crossorigin="anonymous">
                        @else
                            <div style="display:flex;align-items:center;justify-content:center;width:100%;height:100%;font-size:28px;">💎</div>
                        @endif
                    </div>
                    @if($serial)
                        <div class="cert-serial-balloon">{{ $serial }}</div>
                    @endif
                </div>
            </div>

            {{-- پنل QR --}}
            <div class="cert-qr-panel">
                <div class="cert-logo-mini">
                    @if(!empty($logos))
                        @foreach($logos as $i => $logo)
                            <div class="ico"><img src="{{ $logo }}" alt=""></div>
                        @endforeach
                    @else
                        <div class="ico"><span>💎</span></div>
                    @endif
                </div>

                <div class="cert-qr-wrap">
                    <div class="cert-qr-url">mashahirid.ir/{{ $code }}</div>
                    <div class="cert-qr-inner">
                        <div class="cert-qr-box">
                            <img src="{{ $qrUrl }}" alt="QR">
                        </div>
                        <div class="cert-code-inline">
                            <span class="lbl">CODE</span>
                            <span class="val">{{ $code }}</span>
                        </div>
                    </div>
                </div>
            </div>

            {{-- جدول پایین --}}
            <div class="cert-table-wrap">
                <table class="cert-bottom-table">
                    <colgroup>
                        <col style="width:25%"><col style="width:25%">
                        <col style="width:25%"><col style="width:25%">
                    </colgroup>
                    <tr>
                        <td class="tbl-label">Stone</td>
                        <td class="tbl-value">{{ $stoneEn }}</td>
                        <td class="tbl-label">Metal</td>
                        <td class="tbl-value">
                            {{ $metalEn }}
                            @if($carat) <span class="unit">{{ $carat }}</span> @endif
                        </td>
                    </tr>
                    <tr>
                        <td class="tbl-label">Originality</td>
                        <td class="tbl-value">
                            {{ $origin }}
                            @if($flagUrl)
                                <img src="{{ $flagUrl }}" style="width:14px;vertical-align:middle;border-radius:2px;" alt="">
                            @endif
                        </td>
                        <td class="tbl-label">Stone S</td>
                        <td class="tbl-value">
                            {{ $stones }} <span class="unit">mm</span>
                        </td>
                    </tr>
                    <tr>
                        <td class="tbl-label">Brillant</td>
                        <td class="tbl-value">{{ PersianNumber::toFa($brilliant) }}</td>
                        <td class="tbl-label">Total W</td>
                        <td class="tbl-value">
                            {{ $weight }} <span class="unit">gr</span>
                        </td>
                    </tr>
                </table>
            </div>
        </div>
    </div>

    {{-- دکمه‌های عملیات --}}
    <div class="cert-actions" style="display:flex;gap:6px;justify-content:center;margin-top:8px;">
        <button type="button" class="btn btn-sm btn-outline"
                onclick="window.ShopGunCert.openCertPreview('{{ $code }}', {width: {{ $width }}, height: {{ $height }}})">
            👁️ پیش‌نمایش
        </button>
        <button type="button" class="btn btn-sm btn-outline"
                onclick="window.ShopGunCert.printCertsA4(['{{ $code }}'], {width: {{ $width }}, height: {{ $height }}})">
            🖨️ چاپ
        </button>
        <button type="button" class="btn btn-sm btn-outline"
                onclick="window.ShopGunCert.exportCertPNG('{{ $code }}', {width: {{ $width }}, height: {{ $height }}})">
            📸 PNG
        </button>
    </div>
</div>
