from pathlib import Path
import textwrap

PROJECT = Path.home() / "projects" / "shopgun-v2.1"

def write_file(rel, content):
    path = PROJECT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    print(f"✅ {rel}")

# =========================================================
# Certificates Show Component
# =========================================================

write_file("app/Livewire/Certificates/Show.php", r"""
<?php

namespace App\Livewire\Certificates;

use App\Models\Certificate;
use Livewire\Component;

class Show extends Component
{
    public Certificate $certificate;

    public function mount(Certificate $certificate): void
    {
        $this->certificate = $certificate->load(['customer', 'order']);
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
        return view('livewire.certificates.show')
            ->layout('components.layouts.app');
    }
}
""")

write_file("resources/views/livewire/certificates/show.blade.php", r"""
<div class="p-4 md:p-6 max-w-4xl mx-auto">

    <div class="flex flex-wrap items-center justify-between gap-3 mb-6">
        <div class="flex items-center gap-3">
            <a href="{{ route('certificates.index') }}" class="btn btn-ghost btn-sm">→</a>
            <div>
                <h1 class="text-xl md:text-2xl font-bold">شناسنامه #{{ $certificate->code }}</h1>
                <div class="text-xs text-base-content/60 mt-1 font-mono" dir="ltr">
                    {{ $certificate->serial }}
                </div>
            </div>
        </div>

        <div class="flex gap-2">
            <a href="{{ $certificate->public_url }}" target="_blank" class="btn btn-outline btn-sm">
                🔗 لینک عمومی
            </a>
            <button wire:click="delete" wire:confirm="شناسنامه حذف شود؟" class="btn btn-error btn-sm">🗑️</button>
        </div>
    </div>

    @if (session('success'))
        <div class="alert alert-success mb-4 text-sm"><span>{{ session('success') }}</span></div>
    @endif

    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">

        {{-- تصویر --}}
        <div class="card bg-base-100 shadow">
            <div class="card-body">
                <h2 class="card-title text-base mb-2">📸 تصویر</h2>
                @if($certificate->image_path)
                    <img src="{{ asset('storage/' . $certificate->image_path) }}"
                         class="w-full rounded-lg border border-base-300" />
                @else
                    <div class="aspect-square bg-base-200 rounded-lg flex items-center justify-center text-4xl">💎</div>
                @endif

                <div class="mt-4 text-center">
                    <img src="{{ $certificate->qr_url }}" class="w-32 h-32 mx-auto rounded-lg border" />
                    <div class="text-xs text-base-content/60 mt-2">QR کد عمومی</div>
                </div>
            </div>
        </div>

        {{-- جزئیات --}}
        <div class="card bg-base-100 shadow md:col-span-2">
            <div class="card-body">
                <h2 class="card-title text-base mb-4">📋 مشخصات</h2>

                <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-sm">
                    <div class="flex justify-between p-2 rounded bg-base-200/50">
                        <span class="text-base-content/60">💎 سنگ:</span>
                        <span class="font-bold">{{ $certificate->stone_name }}</span>
                    </div>
                    <div class="flex justify-between p-2 rounded bg-base-200/50">
                        <span class="text-base-content/60">🌐 انگلیسی:</span>
                        <span dir="ltr">{{ $certificate->stone_en }}</span>
                    </div>
                    <div class="flex justify-between p-2 rounded bg-base-200/50">
                        <span class="text-base-content/60">🏳️ اصالت:</span>
                        <span>{{ $certificate->stone_origin }} ({{ $certificate->stone_flag }})</span>
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
                    <div class="flex justify-between p-2 rounded bg-base-200/50">
                        <span class="text-base-content/60">✨ برلیان:</span>
                        <span>{{ $certificate->brilliant }}</span>
                    </div>
                    <div class="flex justify-between p-2 rounded bg-base-200/50">
                        <span class="text-base-content/60">🔢 SKU:</span>
                        <span class="font-mono" dir="ltr">{{ $certificate->sku ?? '—' }}</span>
                    </div>
                </div>

                <div class="divider my-3"></div>

                @if($certificate->customer)
                    <div class="flex justify-between text-sm p-2 rounded bg-base-200/50 mb-2">
                        <span class="text-base-content/60">👤 مشتری:</span>
                        <a href="{{ route('customers.show', $certificate->customer) }}" class="link link-primary font-bold">
                            {{ $certificate->customer->name }}
                        </a>
                    </div>
                @endif

                @if($certificate->order)
                    <div class="flex justify-between text-sm p-2 rounded bg-base-200/50 mb-2">
                        <span class="text-base-content/60">📦 سفارش:</span>
                        <a href="{{ route('orders.show', $certificate->order) }}" class="link link-primary font-bold">
                            #{{ $certificate->order->order_number }}
                        </a>
                    </div>
                @endif

                <div class="flex justify-between text-sm p-2 rounded bg-base-200/50">
                    <span class="text-base-content/60">📅 تاریخ صدور:</span>
                    <span>{{ $certificate->issued_at?->format('Y/m/d H:i') }}</span>
                </div>
            </div>
        </div>
    </div>

    {{-- چاپ سریع --}}
    <div class="mt-4 flex gap-2 justify-end">
        <a href="{{ route('certificates.print-a4', ['ids' => $certificate->id]) }}"
           target="_blank" class="btn btn-primary btn-sm">
            🖨️ چاپ A4
        </a>
    </div>
</div>
""")

print()
print("═" * 60)
print("✅ Certificates Show ساخته شد")
print("═" * 60)
print()
print("📌 اجرا کن:")
print("   php artisan optimize:clear")
print("   php artisan serve --host=0.0.0.0 --port=8000")
print()
