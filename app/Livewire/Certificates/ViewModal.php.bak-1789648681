<?php

namespace App\Livewire\Certificates;

use App\Models\Certificate;
use App\Services\CertRenderer;
use Livewire\Component;

class ViewModal extends Component
{
    public bool $show = false;
    public ?int $certId = null;
    public ?Certificate $certificate = null;
    public string $cardHtml = '';
    public string $batchHtml = '';

    protected $listeners = ['open-cert-view' => 'open'];

    public function open(int $certId): void
    {
        $this->certId = $certId;
        $this->certificate = Certificate::with(['customer', 'order'])->find($certId);

        if ($this->certificate) {
            $this->cardHtml  = CertRenderer::renderCard($this->certificate);
            $this->batchHtml = CertRenderer::renderBatchHtml([$this->certificate]);
        }
        $this->show = true;
    }

    public function close(): void
    {
        $this->show = false;
        $this->certId = null;
        $this->certificate = null;
        $this->cardHtml = '';
        $this->batchHtml = '';
    }

    public function render()
    {
        return view('livewire.certificates.view-modal');
    }
}
