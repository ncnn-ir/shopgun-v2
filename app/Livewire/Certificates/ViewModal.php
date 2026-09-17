<?php

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
