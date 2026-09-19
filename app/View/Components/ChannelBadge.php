<?php

namespace App\View\Components;

use Illuminate\View\Component;

class ChannelBadge extends Component
{
    public string $channel;
    public string $label;
    public string $icon;
    public string $cssClass;
    public string $raw;

    public const MAP = [
        'basalam'      => ['باسلام',       '🟢'],
        'digikala'     => ['دیجی‌کالا',     '🔴'],
        'torob'        => ['ترب',          '🟠'],
        'divar'        => ['دیوار',        '🟣'],
        'sheypoor'     => ['شیپور',        '🟪'],
        'bamilo'       => ['بامیلو',       '🟡'],
        'instagram'    => ['اینستاگرام',   '📸'],
        'telegram'     => ['تلگرام',       '✈️'],
        'whatsapp'     => ['واتساپ',       '💬'],
        'eitaa'        => ['ایتا',         '📨'],
        'zibal'        => ['زیبال',        '💠'],
        'sadad'        => ['سداد',         '🏦'],
        'zarinpal'     => ['زرین‌پال',      '💛'],
        'asanpardakht' => ['آسان پرداخت',  '🔷'],
        'idpay'        => ['آی‌دی‌پی',      '🆔'],
        'nextpay'      => ['نکست‌پی',      '⬛'],
        'payir'        => ['پی‌پینگ',       '🔵'],
        'mellat'       => ['بانک ملت',     '🟥'],
        'saman'        => ['سامان',        '🟩'],
        'parsian'      => ['پارسیان',      '🟫'],
        'pasargad'     => ['پاسارگاد',     '🟦'],
        'website'      => ['سایت',         '🌐'],
        'woocommerce'  => ['ووکامرس',      '🛒'],
        'phone'        => ['تلفنی',        '📞'],
        'in_person'    => ['حضوری',        '🏪'],
        'pos'          => ['کارتخوان',     '💳'],
        'online'       => ['آنلاین',       '🌍'],
    ];

    public function __construct(?string $channel = null)
    {
        $raw = (string) $channel;
        $ch = strtolower(trim($raw));
        $ch = str_replace(['-', ' ', '_'], '', $ch);

        $aliases = [
            'wc'=>'woocommerce','woo'=>'woocommerce','wordpress'=>'woocommerce',
            'site'=>'website','web'=>'website',
            'insta'=>'instagram','ig'=>'instagram',
            'tel'=>'telegram','tg'=>'telegram',
            'wa'=>'whatsapp','digi'=>'digikala','djk'=>'digikala',
            'bassalam'=>'basalam','bslm'=>'basalam',
            'sheypur'=>'sheypoor',
            'zarin'=>'zarinpal','zp'=>'zarinpal',
            'cardreader'=>'pos','cash'=>'in_person','shop'=>'in_person',
            'other'=>'online',
        ];
        if (isset($aliases[$ch])) $ch = $aliases[$ch];

        $this->raw = $raw ?: 'نامشخص';
        $this->channel = $ch ?: 'online';

        if (isset(self::MAP[$this->channel])) {
            [$this->label, $this->icon] = self::MAP[$this->channel];
            $this->cssClass = 'ch-' . $this->channel;
        } else {
            $this->label = $raw ?: 'نامشخص';
            $this->icon = '❓';
            $this->cssClass = 'ch-unknown';
        }
    }

    public static function allChannels(): array { return self::MAP; }

    public function render() { return view('components.channel-badge'); }
}
