<?php

namespace App\Livewire\Settings;

use App\Application\Certificates\CertificateTemplateService;
use App\Models\CertificateTemplate;
use Livewire\Component;

/**
 * ★ Settings\\Templates — مدیریت قالب‌های شناسنامه
 */
class Templates extends Component
{
    public bool $showForm = false;
    public ?int $editingId = null;

    public string $name = '';
    public string $description = '';
    public string $version = '1.0';

    public function openForm(?int $id = null): void
    {
        $this->resetForm();
        $this->editingId = $id;
        $this->showForm = true;

        if ($id) {
            $t = CertificateTemplate::find($id);
            if ($t) {
                $this->name = $t->name;
                $this->description = $t->description ?? '';
                $this->version = $t->version;
            }
        }
    }

    public function closeForm(): void
    {
        $this->showForm = false;
        $this->resetForm();
    }

    public function resetForm(): void
    {
        $this->reset(['editingId', 'name', 'description', 'version']);
        $this->version = '1.0';
    }

    public function save(): void
    {
        $this->validate([
            'name' => 'required|string|max:120',
            'version' => 'required|string|max:20',
        ]);

        if ($this->editingId) {
            CertificateTemplate::where('id', $this->editingId)->update([
                'name' => $this->name,
                'description' => $this->description,
                'version' => $this->version,
            ]);
            $this->dispatch('notify', type: 'success', message: 'قالب بروزرسانی شد');
        } else {
            CertificateTemplateService::create([
                'name' => $this->name,
                'description' => $this->description,
                'version' => $this->version,
            ]);
            $this->dispatch('notify', type: 'success', message: 'قالب ایجاد شد');
        }

        $this->closeForm();
    }

    public function duplicate(int $id): void
    {
        CertificateTemplateService::duplicate($id);
        $this->dispatch('notify', type: 'success', message: 'کپی ایجاد شد');
    }

    public function publish(int $id): void
    {
        CertificateTemplate::find($id)?->publish();
        $this->dispatch('notify', type: 'success', message: 'منتشر شد');
    }

    public function archive(int $id): void
    {
        CertificateTemplate::find($id)?->archive();
        $this->dispatch('notify', type: 'success', message: 'آرشیو شد');
    }

    public function setDefault(int $id): void
    {
        CertificateTemplateService::setDefault($id);
        $this->dispatch('notify', type: 'success', message: 'پیش‌فرض تنظیم شد');
    }

    public function delete(int $id): void
    {
        CertificateTemplate::find($id)?->delete();
        $this->dispatch('notify', type: 'success', message: 'حذف شد');
    }

    public function render()
    {
        return view('livewire.settings.templates', [
            'templates' => CertificateTemplate::orderByDesc('is_default')->latest('id')->get(),
        ]);
    }
}
