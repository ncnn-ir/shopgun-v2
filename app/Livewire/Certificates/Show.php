<?php

namespace App\Livewire\Certificates;

use App\Models\Certificate;
use App\Services\CertRenderer;
use App\Support\CertConfig;
use Livewire\Component;

class Show extends Component
{
    public Certificate $certificate;
    public string $cardHtml = '';     // ★ فقط کارت (بدون iframe)
    public string $batchHtml = '';    // ★ برای چاپ

    public function mount(Certificate $certificate): void
    {
        $this->certificate = $certificate->load(['customer', 'order']);
        $this->cardHtml  = CertRenderer::renderCard($this->certificate);
        $this->batchHtml = CertRenderer::renderBatchHtml([$this->certificate]);
    }

    public function delete()
    {
        $code = $this->certificate->code;
        $this->certificate->delete();
        session()->flash('success', "شناسنامه #{$code} حذف شد.");
        return redirect()->route('certificates.index');
    }

    public array $snapshots = [];
    public bool $showHistory = false;

    public function loadHistory(): void
    {
        try {
            $this->snapshots = \App\Application\Certificates\CertificateSnapshotService::history($this->certificate)
                ->map(fn($s) => [
                    'id' => $s->id,
                    'event' => $s->event,
                    'event_label' => match($s->event) {
                        'issued' => '📝 صدور اولیه',
                        'updated' => '✏️ ویرایش',
                        'reprinted' => '🖨️ چاپ مجدد',
                        'design_changed' => '🎨 تغییر طرح',
                        default => $s->event,
                    },
                    'stone_name' => $s->stone_name,
                    'metal' => $s->metal,
                    'weight' => $s->weight,
                    'captured_at' => \App\Support\PersianDate::format($s->captured_at, 'Y/m/d H:i'),
                    'changed_by' => $s->changed_by_name,
                ])
                ->toArray();
            $this->showHistory = true;
        } catch (\Throwable $e) {
            $this->dispatch('notify', type: 'error', message: $e->getMessage());
        }
    }

    public function closeHistory(): void
    {
        $this->showHistory = false;
        $this->snapshots = [];
    }

    public function render()
    {
        return view('livewire.certificates.show', [
            'sizes' => CertConfig::sizes(),
        ])->layout('components.layouts.app');
    }
}
