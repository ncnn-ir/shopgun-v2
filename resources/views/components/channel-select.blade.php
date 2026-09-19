@props(['order'])
<select
    class="ch-select"
    onchange="
        fetch('{{ route('orders.channel.update', $order->id) }}', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRF-TOKEN': '{{ csrf_token() }}',
                'Accept': 'application/json'
            },
            body: JSON.stringify({ sales_channel: this.value })
        }).then(r => r.json()).then(d => {
            if (d.ok) {
                this.style.transition = 'all .3s';
                this.style.boxShadow = '0 0 0 3px rgba(16,185,129,.4)';
                setTimeout(() => this.style.boxShadow = '', 800);
            }
        }).catch(e => alert('خطا در ذخیره'));
    "
    title="کانال فروش">
    @foreach(\App\View\Components\ChannelBadge::allChannels() as $key => $info)
        <option value="{{ $key }}" @selected($order->sales_channel === $key)>
            {{ $info[1] }} {{ $info[0] }}
        </option>
    @endforeach
</select>
