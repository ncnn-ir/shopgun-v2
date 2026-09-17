<?php

namespace App\Livewire;

use Livewire\Component;
use Livewire\WithFileUploads;
use Illuminate\Support\Facades\Storage;

class FileManagerPage extends Component
{
    use WithFileUploads;

    public array $files = [];
    public $upload = null;
    public string $folder = '';
    public string $search = '';

    public function mount(): void
    {
        $this->refresh();
    }

    public function refresh(): void
    {
        $disk = Storage::disk('public');
        $this->files = [];

        if (!$disk->exists($this->folder ?: 'uploads')) {
            $disk->makeDirectory($this->folder ?: 'uploads');
        }

        $allFiles = $disk->files($this->folder ?: 'uploads');
        foreach ($allFiles as $f) {
            $name = basename($f);

            if ($this->search && !str_contains(mb_strtolower($name), mb_strtolower($this->search))) {
                continue;
            }

            $this->files[] = [
                'name'  => $name,
                'path'  => $f,
                'size'  => $disk->size($f),
                'url'   => $disk->url($f),
                'mtime' => $disk->lastModified($f),
                'is_image' => (bool) preg_match('/\.(jpg|jpeg|png|gif|webp|svg|bmp)$/i', $name),
            ];
        }
        usort($this->files, fn($a, $b) => $b['mtime'] <=> $a['mtime']);
    }

    public function updatedSearch(): void
    {
        $this->refresh();
    }

    public function updatedUpload(): void
    {
        $this->validate(['upload' => 'file|max:20480']);
        $name = $this->upload->getClientOriginalName();
        $name = preg_replace('/[^\w\d\.\-_\x{0600}-\x{06FF}]/u', '_', $name);
        $this->upload->storeAs($this->folder ?: 'uploads', $name, 'public');
        $this->upload = null;
        $this->refresh();
        $this->dispatch('notify', type: 'success', message: 'فایل آپلود شد ✅');
    }

    public function delete(string $path): void
    {
        Storage::disk('public')->delete($path);
        $this->refresh();
        $this->dispatch('notify', type: 'success', message: 'فایل حذف شد');
    }

    public function render()
    {
        return view('livewire.file-manager')
            ->layout('components.layouts.app');
    }
}
