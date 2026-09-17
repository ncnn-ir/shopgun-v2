# -*- coding: utf-8 -*-
"""ShopGun V2 - Fix Create + Edit + Download"""
from pathlib import Path
import time, re

ROOT = Path(r'D:\prodo\shopgun-v2.2')

def write(rel, content):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        p.rename(str(p) + '.bak-' + str(int(time.time())))
    p.write_text(content, encoding='utf-8')
    print("[OK] " + rel)


# ═══════════════════════════════════════════════════════════════
# 1. CREATE.PHP — کاملاً بازنویسی
# ═══════════════════════════════════════════════════════════════

CREATE = r'''<?php

namespace App\Livewire\Certificates;

use App\Models\Certificate;
use App\Models\Customer;
use App\Models\Order;
use Livewire\Attributes\On;
use Livewire\Component;
use Livewire\WithFileUploads;

class Create extends Component
{
    use WithFileUploads;

    public int $step = 1;
    public bool $show = false;
    public ?int $editingId = null;

    public string $stoneName   = '';
    public string $stoneEn     = '';
    public string $stoneOrigin = 'نیشابور';
    public string $stoneFlag   = 'ir';
    public string $stoneIcon   = '💠';
    public string $metal       = 'نقره 925';
    public string $metalEn     = 'Silver 925';
    public string $metalCarat  = '925';

    public string $length    = '';
    public string $width     = '';
    public string $weight    = '';
    public string $brilliant = '0';

    public ?int $customerId = null;
    public ?int $orderId    = null;

    public $image = null;

    public array $stoneOptions = [
        ['name' => 'فیروزه عجمی',   'en' => 'Turquoise Ajami',   'origin' => 'نیشابور',   'flag' => 'ir', 'icon' => '💠'],
        ['name' => 'فیروزه شجری',   'en' => 'Turquoise Shajari', 'origin' => 'نیشابور',   'flag' => 'ir', 'icon' => '💠'],
        ['name' => 'عقیق یمانی',    'en' => 'Yemeni Agate',      'origin' => 'یمن',        'flag' => 'ye', 'icon' => '🔴'],
        ['name' => 'عقیق سلیمانی',  'en' => 'Solomoni Agate',    'origin' => 'یمن',        'flag' => 'ye', 'icon' => '❤️'],
        ['name' => 'عقیق شجر',      'en' => 'Dendritic Agate',   'origin' => 'یمن',        'flag' => 'ye', 'icon' => '🌿'],
        ['name' => 'در نجف',        'en' => 'Najaf Pearl',       'origin' => 'عراق',       'flag' => 'iq', 'icon' => '⚪'],
        ['name' => 'الماس',         'en' => 'Diamond',           'origin' => 'آفریقا',     'flag' => 'za', 'icon' => '💎'],
        ['name' => 'یاقوت سرخ',     'en' => 'Ruby',              'origin' => 'میانمار',    'flag' => 'mm', 'icon' => '❤️'],
        ['name' => 'یاقوت کبود',    'en' => 'Blue Sapphire',     'origin' => 'سری‌لانکا',  'flag' => 'lk', 'icon' => '🔵'],
        ['name' => 'زمرد',          'en' => 'Emerald',           'origin' => 'کلمبیا',     'flag' => 'co', 'icon' => '🟢'],
        ['name' => 'توپاز',         'en' => 'Topaz',             'origin' => 'برزیل',      'flag' => 'br', 'icon' => '💛'],
        ['name' => 'آمیتیست',       'en' => 'Amethyst',          'origin' => 'برزیل',      'flag' => 'br', 'icon' => '🟣'],
    ];

    public array $metalOptions = [
        ['name' => 'نقره 925',      'en' => 'Silver 925',      'carat' => '925'],
        ['name' => 'نقره 999',      'en' => 'Fine Silver',     'carat' => '999'],
        ['name' => 'طلا 18K',       'en' => 'Gold 18K',        'carat' => '750'],
        ['name' => 'طلا 21K',       'en' => 'Gold 21K',        'carat' => '875'],
        ['name' => 'طلا 22K',       'en' => 'Gold 22K',        'carat' => '916'],
        ['name' => 'طلا 24K',       'en' => 'Gold 24K',        'carat' => '999'],
        ['name' => 'پلاتین 950',    'en' => 'Platinum 950',    'carat' => '950'],
        ['name' => 'استیل',         'en' => 'Stainless Steel', 'carat' => '-'],
    ];

    #[On('open-cert-form')]
    public function openModal($certId = null): void
    {
        $this->resetForm();
        $this->editingId = is_numeric($certId) ? (int)$certId : null;

        if ($this->editingId) {
            $c = Certificate::find($this->editingId);
            if ($c) {
                $this->stoneName   = (string) ($c->stone_name ?? '');
                $this->stoneEn     = (string) ($c->stone_en ?? '');
                $this->stoneOrigin = (string) ($c->stone_origin ?? 'نیشابور');
                $this->stoneFlag   = (string) ($c->stone_flag ?? 'ir');
                $this->metal       = (string) ($c->metal ?? 'نقره 925');
                $this->metalEn     = (string) ($c->metal_en ?? '');
                $this->metalCarat  = (string) ($c->metal_carat ?? '');
                $this->length      = (string) ($c->length ?? '');
                $this->width       = (string) ($c->width ?? '');
                $this->weight      = (string) ($c->weight ?? '');
                $this->brilliant   = (string) ($c->brilliant ?? '0');
                $this->customerId  = $c->customer_id ? (int)$c->customer_id : null;
                $this->orderId     = $c->order_id ? (int)$c->order_id : null;
            }
        }

        $this->step = 1;
        $this->show = true;
    }

    public function closeModal(): void
    {
        $this->show = false;
        $this->resetForm();
    }

    protected function resetForm(): void
    {
        $this->step = 1;
        $this->stoneName = '';
        $this->stoneEn = '';
        $this->stoneOrigin = 'نیشابور';
        $this->stoneFlag = 'ir';
        $this->stoneIcon = '💠';
        $this->metal = 'نقره 925';
        $this->metalEn = 'Silver 925';
        $this->metalCarat = '925';
        $this->length = '';
        $this->width = '';
        $this->weight = '';
        $this->brilliant = '0';
        $this->customerId = null;
        $this->orderId = null;
        $this->image = null;
        $this->editingId = null;
        $this->resetErrorBag();
    }

    public function selectStone(int $index): void
    {
        $s = $this->stoneOptions[$index] ?? null;
        if (!$s) return;
        $this->stoneName   = $s['name'];
        $this->stoneEn     = $s['en'];
        $this->stoneOrigin = $s['origin'];
        $this->stoneFlag   = $s['flag'];
        $this->stoneIcon   = $s['icon'];
    }

    public function selectMetal(int $index): void
    {
        $m = $this->metalOptions[$index] ?? null;
        if (!$m) return;
        $this->metal      = $m['name'];
        $this->metalEn    = $m['en'];
        $this->metalCarat = $m['carat'];
    }

    public function nextStep(): void
    {
        if ($this->step === 1) {
            $this->validate([
                'stoneName' => 'required|string',
                'metal'     => 'required|string',
            ], [
                'stoneName.required' => 'سنگ را انتخاب کن',
                'metal.required'     => 'فلز را انتخاب کن',
            ]);
        }
        if ($this->step === 2) {
            $this->validate([
                'length' => 'required|numeric|min:0',
                'width'  => 'required|numeric|min:0',
                'weight' => 'required|numeric|min:0',
            ], [
                'length.required' => 'طول الزامی است',
                'width.required'  => 'عرض الزامی است',
                'weight.required' => 'وزن الزامی است',
            ]);
        }
        $this->step = min(3, $this->step + 1);
    }

    public function prevStep(): void
    {
        $this->step = max(1, $this->step - 1);
    }

    public function save()
    {
        $this->validate([
            'stoneName' => 'required|string|max:255',
            'metal'     => 'required|string|max:255',
            'length'    => 'nullable|numeric|min:0',
            'width'     => 'nullable|numeric|min:0',
            'weight'    => 'nullable|numeric|min:0',
            'image'     => 'nullable|image|max:5120',
        ]);

        $imagePath = null;
        if ($this->image) {
            try {
                $imagePath = $this->image->store('certificates', 'public');
            } catch (\Throwable $e) {
                \Log::error('Cert image upload: ' . $e->getMessage());
            }
        }

        if ($this->editingId) {
            $cert = Certificate::find($this->editingId);
            if (!$cert) {
                $this->dispatch('notify', type: 'error', message: 'شناسنامه پیدا نشد');
                return;
            }

            $data = [
                'stone_name'   => $this->stoneName,
                'stone_en'     => $this->stoneEn,
                'stone_origin' => $this->stoneOrigin,
                'stone_flag'   => $this->stoneFlag,
                'metal'        => $this->metal,
                'metal_en'     => $this->metalEn,
                'metal_carat'  => $this->metalCarat,
                'length'       => (float) ($this->length ?: 0),
                'width'        => (float) ($this->width ?: 0),
                'weight'       => (float) ($this->weight ?: 0),
                'brilliant'    => (int) ($this->brilliant ?: 0),
                'customer_id'  => $this->customerId ?: null,
                'order_id'     => $this->orderId ?: null,
            ];
            if ($imagePath) $data['image_path'] = $imagePath;

            $cert->update($data);
            $msg = "شناسنامه #{$cert->code} ویرایش شد.";
        } else {
            $code = Certificate::generateCode();
            $serial = Certificate::generateSerial($code, $this->stoneEn ?: $this->stoneName);

            $cert = Certificate::create([
                'code'         => $code,
                'serial'       => $serial,
                'stone_name'   => $this->stoneName,
                'stone_en'     => $this->stoneEn,
                'stone_origin' => $this->stoneOrigin,
                'stone_flag'   => $this->stoneFlag,
                'metal'        => $this->metal,
                'metal_en'     => $this->metalEn,
                'metal_carat'  => $this->metalCarat,
                'length'       => (float) ($this->length ?: 0),
                'width'        => (float) ($this->width ?: 0),
                'weight'       => (float) ($this->weight ?: 0),
                'brilliant'    => (int) ($this->brilliant ?: 0),
                'image_path'   => $imagePath,
                'customer_id'  => $this->customerId ?: null,
                'order_id'     => $this->orderId ?: null,
                'issued_at'    => now(),
            ]);
            $msg = "شناسنامه #{$code} صادر شد.";
        }

        session()->flash('success', $msg);
        $this->closeModal();
        $this->dispatch('notify', type: 'success', message: $msg);
        $this->dispatch('cert-saved');

        // ★ redirect به index اگه تازه ساخته شده
        if (!$this->editingId) {
            // مقدار قبلی رو نگه ندار
        }
    }

    public function render()
    {
        return view('livewire.certificates.create', [
            'customers' => Customer::orderBy('name')->limit(200)->get(),
            'orders'    => Order::latest('id')->limit(100)->get(),
        ]);
    }
}
'''

write('app/Livewire/Certificates/Create.php', CREATE)


# ═══════════════════════════════════════════════════════════════
# 2. VIEWMODAL.PHP — بازنویسی برای dispatch درست
# ═══════════════════════════════════════════════════════════════

VM_PHP = r'''<?php

namespace App\Livewire\Certificates;

use App\Models\Certificate;
use App\Services\CertRenderer;
use Livewire\Attributes\On;
use Livewire\Component;

class ViewModal extends Component
{
    public bool $show = false;
    public ?int $certId = null;
    public ?Certificate $certificate = null;
    public string $cardHtml = '';

    #[On('open-cert-view')]
    public function open($certId = null): void
    {
        if (!is_numeric($certId)) return;

        $this->certId = (int) $certId;
        $this->certificate = Certificate::with(['customer', 'order'])->find($this->certId);

        if ($this->certificate) {
            try {
                $this->cardHtml = CertRenderer::renderCard($this->certificate);
            } catch (\Throwable $e) {
                $this->cardHtml = '<div style="padding:20px;color:#dc2626">خطا در رندر: '
                    . htmlspecialchars($e->getMessage()) . '</div>';
            }
        }
        $this->show = true;
    }

    public function close(): void
    {
        $this->show = false;
        $this->certId = null;
        $this->certificate = null;
        $this->cardHtml = '';
    }

    public function edit(): void
    {
        if (!$this->certificate) return;
        $id = $this->certificate->id;
        $this->close();
        // ★ dispatch به Create modal
        $this->dispatch('open-cert-form', certId: $id);
    }

    public function delete(): void
    {
        if (!$this->certificate) return;
        $code = $this->certificate->code;
        $this->certificate->delete();
        $this->close();
        $this->dispatch('cert-saved');
        $this->dispatch('notify', type: 'success', message: "شناسنامه #{$code} حذف شد");
    }

    public function render()
    {
        return view('livewire.certificates.view-modal');
    }
}
'''

write('app/Livewire/Certificates/ViewModal.php', VM_PHP)


# ═══════════════════════════════════════════════════════════════
# 3. CREATE BLADE — بازنویسی برای اطمینان
# ═══════════════════════════════════════════════════════════════

CREATE_BLADE = r'''<div>
@if($show)
<div style="position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:97;display:flex;align-items:flex-start;justify-content:center;padding:10px;overflow-y:auto"
     wire:key="cert-form-{{ $editingId ?? 'new' }}"
     @keydown.escape.window="$wire.closeModal()">

    <div style="background:#fff;width:100%;max-width:880px;margin:10px auto;border-radius:16px;box-shadow:0 20px 60px rgba(0,0,0,.4);overflow:hidden;direction:rtl;font-family:Vazirmatn,Tahoma,sans-serif">

        <div style="background:linear-gradient(135deg,#1a5276,#0d3b5e);color:#fff;padding:14px 18px;display:flex;align-items:center;justify-content:space-between">
            <h2 style="margin:0;font-size:16px;font-weight:700">
                {{ $editingId ? '✏️ ویرایش شناسنامه' : '💎 شناسنامه جدید' }}
            </h2>
            <button type="button" wire:click="closeModal" style="width:32px;height:32px;border-radius:50%;background:rgba(255,255,255,.2);color:#fff;border:none;cursor:pointer;font-size:15px">X</button>
        </div>

        <div style="padding:16px;max-height:calc(100vh - 180px);overflow-y:auto">

            {{-- Steps --}}
            <div style="display:flex;justify-content:space-between;margin-bottom:24px;position:relative;padding:0 20px">
                <div style="position:absolute;top:18px;left:60px;right:60px;height:2px;background:#e2e8f0;z-index:0"></div>
                @foreach([1 => 'سنگ و فلز', 2 => 'مشخصات', 3 => 'تصویر'] as $num => $label)
                    <div style="position:relative;z-index:1;display:flex;flex-direction:column;align-items:center;flex:1">
                        <div style="width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;
                            background:{{ $step >= $num ? 'linear-gradient(135deg,#1a5276,#0d3b5e)' : '#f1f5f9' }};
                            color:{{ $step >= $num ? '#fff' : '#64748b' }};">
                            {{ $num }}
                        </div>
                        <div style="font-size:11px;font-weight:700;margin-top:6px;color:{{ $step >= $num ? '#1a5276' : '#94a3b8' }}">{{ $label }}</div>
                    </div>
                @endforeach
            </div>

            {{-- STEP 1 --}}
            @if($step === 1)
                <div style="margin-bottom:20px">
                    <h3 style="font-size:14px;font-weight:700;color:#1a5276;margin:0 0 12px">💎 سنگ را انتخاب کن</h3>
                    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(110px,1fr));gap:8px">
                        @foreach($stoneOptions as $i => $s)
                            <button type="button" wire:click="selectStone({{ $i }})"
                                    style="padding:10px 4px;border:2px solid {{ $stoneName === $s['name'] ? '#c9a84c' : '#e2e8f0' }};background:{{ $stoneName === $s['name'] ? '#fef3c7' : '#fff' }};border-radius:10px;cursor:pointer">
                                <div style="font-size:26px;margin-bottom:4px">{{ $s['icon'] }}</div>
                                <div style="font-size:11px;font-weight:700;color:#1e293b">{{ $s['name'] }}</div>
                            </button>
                        @endforeach
                    </div>
                    @error('stoneName') <div style="color:#dc2626;font-size:11px;margin-top:8px">{{ $message }}</div> @enderror
                </div>

                <div>
                    <h3 style="font-size:14px;font-weight:700;color:#1a5276;margin:0 0 12px">⚙️ فلز را انتخاب کن</h3>
                    <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(100px,1fr));gap:8px">
                        @foreach($metalOptions as $i => $m)
                            <button type="button" wire:click="selectMetal({{ $i }})"
                                    style="padding:12px 6px;border:2px solid {{ $metal === $m['name'] ? '#c9a84c' : '#e2e8f0' }};background:{{ $metal === $m['name'] ? '#fef3c7' : '#fff' }};border-radius:10px;cursor:pointer;font-weight:700;font-size:12px;color:#1e293b">
                                {{ $m['name'] }}
                            </button>
                        @endforeach
                    </div>
                    @error('metal') <div style="color:#dc2626;font-size:11px;margin-top:8px">{{ $message }}</div> @enderror
                </div>
            @endif

            {{-- STEP 2 --}}
            @if($step === 2)
                <div style="background:linear-gradient(135deg,#fef3c7,#fde68a);padding:10px 14px;border-radius:10px;margin-bottom:16px;font-size:13px;font-weight:700;color:#78350f">
                    💎 {{ $stoneName }} — ⚙️ {{ $metal }}
                </div>

                <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(160px,1fr));gap:14px">
                    <div>
                        <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">طول (mm)</label>
                        <input type="number" step="0.01" wire:model="length" dir="ltr"
                               style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-family:monospace;font-size:13px;background:#f8fafc;box-sizing:border-box;text-align:center">
                        @error('length') <div style="color:#dc2626;font-size:10px;margin-top:3px">{{ $message }}</div> @enderror
                    </div>
                    <div>
                        <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">عرض (mm)</label>
                        <input type="number" step="0.01" wire:model="width" dir="ltr"
                               style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-family:monospace;font-size:13px;background:#f8fafc;box-sizing:border-box;text-align:center">
                        @error('width') <div style="color:#dc2626;font-size:10px;margin-top:3px">{{ $message }}</div> @enderror
                    </div>
                    <div>
                        <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">وزن (گرم)</label>
                        <input type="number" step="0.001" wire:model="weight" dir="ltr"
                               style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-family:monospace;font-size:13px;background:#f8fafc;box-sizing:border-box;text-align:center">
                        @error('weight') <div style="color:#dc2626;font-size:10px;margin-top:3px">{{ $message }}</div> @enderror
                    </div>
                    <div>
                        <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">عیار</label>
                        <input type="text" value="{{ $metalCarat }}" readonly dir="ltr"
                               style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-family:monospace;font-size:13px;background:#e2e8f0;box-sizing:border-box;text-align:center">
                    </div>
                    <div>
                        <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">برلیان</label>
                        <input type="number" wire:model="brilliant" dir="ltr"
                               style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-family:monospace;font-size:13px;background:#f8fafc;box-sizing:border-box;text-align:center">
                    </div>
                </div>
            @endif

            {{-- STEP 3 --}}
            @if($step === 3)
                <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:16px">
                    <div>
                        <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">👤 مشتری (اختیاری)</label>
                        <select wire:model="customerId" style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:13px;background:#f8fafc;box-sizing:border-box">
                            <option value="">— بدون مشتری —</option>
                            @foreach($customers as $c)
                                <option value="{{ $c->id }}">{{ $c->name }} — {{ $c->phone }}</option>
                            @endforeach
                        </select>
                    </div>
                    <div>
                        <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">📦 سفارش (اختیاری)</label>
                        <select wire:model="orderId" style="width:100%;padding:9px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:13px;background:#f8fafc;box-sizing:border-box">
                            <option value="">— بدون سفارش —</option>
                            @foreach($orders as $o)
                                <option value="{{ $o->id }}">#{{ $o->order_number }}</option>
                            @endforeach
                        </select>
                    </div>
                </div>

                <div>
                    <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">📸 تصویر محصول</label>
                    <input type="file" wire:model="image" accept="image/*"
                           style="width:100%;padding:8px;border:1.5px dashed #cbd5e1;border-radius:8px;background:#f8fafc;box-sizing:border-box">
                    <div wire:loading wire:target="image" style="font-size:11px;color:#0891b2;margin-top:4px">⏳ در حال آپلود...</div>
                    @if($image)
                        <div style="margin-top:10px"><img src="{{ $image->temporaryUrl() }}" style="max-width:120px;border-radius:10px;border:2px solid #c9a84c"></div>
                    @endif
                    @error('image') <div style="color:#dc2626;font-size:10px;margin-top:3px">{{ $message }}</div> @enderror
                </div>
            @endif
        </div>

        <div style="padding:12px 18px;background:#f8fafc;border-top:1px solid #e2e8f0;display:flex;justify-content:space-between;gap:8px">
            <div>
                @if($step > 1)
                    <button type="button" wire:click="prevStep"
                            style="padding:9px 18px;background:#f1f5f9;color:#475569;border:1.5px solid #cbd5e1;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">→ قبل</button>
                @endif
            </div>
            <div style="display:flex;gap:8px">
                <button type="button" wire:click="closeModal"
                        style="padding:9px 18px;background:#fff;color:#475569;border:1.5px solid #cbd5e1;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">انصراف</button>
                @if($step < 3)
                    <button type="button" wire:click="nextStep"
                            style="padding:9px 22px;background:linear-gradient(135deg,#1a5276,#0d3b5e);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">بعد ←</button>
                @else
                    <button type="button" wire:click="save" wire:loading.attr="disabled"
                            style="padding:9px 22px;background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:13px">
                        <span wire:loading.remove wire:target="save">✓ ذخیره</span>
                        <span wire:loading wire:target="save">⏳...</span>
                    </button>
                @endif
            </div>
        </div>
    </div>
</div>
@endif
</div>
'''

write('resources/views/livewire/certificates/create.blade.php', CREATE_BLADE)


# ═══════════════════════════════════════════════════════════════
# 4. LAYOUT — اطمینان از حضور همه modal ها
# ═══════════════════════════════════════════════════════════════

layout = ROOT / 'resources' / 'views' / 'components' / 'layouts' / 'app.blade.php'
if layout.exists():
    txt = layout.read_text(encoding='utf-8')

    # حذف همه modal های قدیمی
    for m in ['certificates.create', 'certificates.view-modal', 'orders.form-modal',
              'orders.view-modal', 'customers.profile-modal', 'components.shipment-timeline',
              'orders.import-postal', 'global-search']:
        pattern = r'<livewire:' + re.escape(m) + r'[^/]*/>\s*'
        txt = re.sub(pattern, '', txt)

    # اضافه کردن بلوک کامل
    if '@auth' in txt:
        modals_block = '''@auth
    <livewire:global-search />
    <livewire:components.shipment-timeline />
    <livewire:orders.import-postal :key="'imp'" />
    <livewire:orders.form-modal :key="'ofm'" />
    <livewire:orders.view-modal :key="'ovm'" />
    <livewire:customers.profile-modal :key="'cpm'" />
    <livewire:certificates.view-modal :key="'cvm'" />
    <livewire:certificates.create :key="'ccm'" />
@endauth'''
        txt = re.sub(r'@auth.*?@endauth', modals_block, txt, count=1, flags=re.DOTALL)

    layout.write_text(txt, encoding='utf-8')
    print("[OK] layout - all modals")


# ═══════════════════════════════════════════════════════════════
# 5. CERT INDEX — دکمه‌های درست
# ═══════════════════════════════════════════════════════════════

ci = ROOT / 'resources' / 'views' / 'livewire' / 'certificates' / 'index.blade.php'
if ci.exists():
    txt = ci.read_text(encoding='utf-8')

    # دکمه ساخت
    txt = re.sub(
        r'<button[^>]*onclick="Livewire\.dispatch\([^)]+\)"[^>]*>➕ شناسنامه جدید</button>',
        '<button type="button" onclick="Livewire.dispatch(\'open-cert-form\')" class="btn btn-primary">➕ شناسنامه جدید</button>',
        txt
    )

    # دکمه view
    txt = re.sub(
        r'<button[^>]*onclick="Livewire\.dispatch\(\'open-cert-view\'[^)]+\)"[^>]*>👁️</button>',
        '<button type="button" onclick="Livewire.dispatch(\'open-cert-view\', { certId: {{ $c->id }} })" class="sg-action-btn view">👁️</button>',
        txt
    )

    # دکمه edit
    if 'open-cert-form' not in txt.split('👁️')[-1] if '👁️' in txt else True:
        pass

    # جایگزینی دکمه ویرایش
    txt = re.sub(
        r'<a href="\{\{ route\(\'certificates\.designer\'[^<]+</a>',
        '<button type="button" onclick="Livewire.dispatch(\'open-cert-form\', { certId: {{ $c->id }} })" class="sg-action-btn edit">✏️</button>',
        txt
    )

    # دکمه دانلود
    if 'downloadCertRow' not in txt:
        old_del = '<button wire:click="delete({{ $c->id }})" wire:confirm="حذف شود؟" class="sg-action-btn delete">🗑️</button>'
        new_dl = '''<button type="button" onclick="downloadCert({{ $c->id }}, '{{ $c->code }}')" class="sg-action-btn" style="background:rgba(8,145,178,.15);color:#0891b2" title="دانلود PNG">📥</button>
                                    ''' + old_del
        txt = txt.replace(old_del, new_dl, 1)

    # اسکریپت دانلود
    txt = re.sub(r'<script[^>]*html2canvas[^>]*></script>\s*<script>.*?</script>\s*$', '', txt, flags=re.DOTALL)

    DOWNLOAD_SCRIPT = '''
<script src="https://cdnjs.cloudflare.com/ajax/libs/html2canvas/1.4.1/html2canvas.min.js"></script>
<script>
function downloadCert(id, code) {
    fetch('/certificates/' + id + '/render')
        .then(function(r) { return r.text(); })
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
            alert('خطای دریافت: ' + e.message);
        });
}
</script>
'''
    txt = txt + DOWNLOAD_SCRIPT
    ci.write_text(txt, encoding='utf-8')
    print("[OK] cert index - buttons + download")


# ═══════════════════════════════════════════════════════════════
# 6. SHOW route — همان download
# ═══════════════════════════════════════════════════════════════

print()
print("=" * 60)
print("DONE")
print("=" * 60)
print("  php artisan view:clear")
print("  php artisan optimize:clear")
print("  php artisan route:clear")
print("  php artisan serve")