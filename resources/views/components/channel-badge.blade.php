@props(['channel' => null, 'showIcon' => true])
@php $b = new \App\View\Components\ChannelBadge($channel); @endphp
<span class="ch-badge {{ $b->cssClass }}" title="کانال: {{ $b->label }}">
    @if($showIcon)<span class="ch-icon">{{ $b->icon }}</span>@endif
    <span>{{ $b->label }}</span>
</span>
