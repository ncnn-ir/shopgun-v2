<?php

namespace App\Livewire\Certificates;

use App\Models\Certificate;
use App\Models\CertSetting;
use Livewire\Attributes\On;
use Livewire\Component;

class Designer extends Component
{
    public ?Certificate $certificate = null;
    public string $designJson = 'null';
    public string $statusMessage = '';
    public bool $isGlobal = false;

    public function mount(?Certificate $certificate = null): void
    {
        if ($certificate && $certificate->exists) {
            $this->certificate = $certificate;
            $this->isGlobal = false;
            $design = $certificate->design_data;
        } else {
            $this->isGlobal = true;
            $design = CertSetting::get('global_design', null);
        }

        if ($design) {
            $this->designJson = is_string($design) ? $design : json_encode($design, JSON_UNESCAPED_UNICODE);
        } else {
            $this->designJson = 'null';
        }
    }

    #[On('designer-save')]
    public function saveDesign($json = null): void
    {
        $design = $this->decodeJson($json);
        if ($design === null) {
            $this->statusMessage = '❌ JSON نامعتبر';
            return;
        }

        if (!$this->certificate) {
            $this->statusMessage = '❌ شناسنامه‌ای موجود نیست';
            return;
        }

        $this->certificate->update(['design_data' => $design]);
        $this->designJson = is_string($json) ? $json : json_encode($json, JSON_UNESCAPED_UNICODE);
        $this->statusMessage = '✅ طراحی ذخیره شد در ' . now()->format('H:i:s');
    }

    #[On('global-designer-save')]
    public function saveGlobalDesign($json = null): void
    {
        $design = $this->decodeJson($json);
        if ($design === null) {
            $this->statusMessage = '❌ JSON نامعتبر';
            return;
        }

        CertSetting::set('global_design', $design, 'cert');
        $this->designJson = is_string($json) ? $json : json_encode($json, JSON_UNESCAPED_UNICODE);
        $this->statusMessage = '✅ طرح پیش‌فرض برای همه شناسنامه‌ها ذخیره شد';
    }

    protected function decodeJson($json): ?array
    {
        if (is_string($json)) {
            $d = json_decode($json, true);
            return is_array($d) ? $d : null;
        }
        if (is_array($json)) return $json;
        return null;
    }

    public function resetDesign(): void
    {
        if ($this->isGlobal) {
            CertSetting::set('global_design', null, 'cert');
        } elseif ($this->certificate) {
            $this->certificate->update(['design_data' => null]);
        }
        $this->designJson = 'null';
        $this->statusMessage = '↺ طراحی ریست شد';
    }

    public function render()
    {
        return view('livewire.certificates.designer')
            ->layout('components.layouts.app');
    }
}
