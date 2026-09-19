<?php

namespace App\Livewire;

use Livewire\Attributes\On;
use Livewire\Component;

/**
 * ★ PopupManager — مدیریت مرکزی پاپ‌آپ‌ها
 * - Stacking (z-index) خودکار
 * - Close on outside click
 * - ESC to close top
 */
class PopupManager extends Component
{
    public array $stack = [];  // [{id, component, params, zIndex}]

    #[On('popup-open')]
    public function open(string $component, array $params = [], ?string $id = null): void
    {
        $id = $id ?? uniqid('popup_');

        // اگه همون قبلاً بازه، دوباره بازش نکن
        foreach ($this->stack as $p) {
            if ($p['id'] === $id) return;
        }

        $this->stack[] = [
            'id' => $id,
            'component' => $component,
            'params' => $params,
            'zIndex' => 1000 + count($this->stack) * 10,
            'opened_at' => now()->toIso8601String(),
        ];
    }

    #[On('popup-close')]
    public function close(?string $id = null): void
    {
        if ($id === null) {
            // آخرین پاپ‌آپ رو ببند
            array_pop($this->stack);
        } else {
            $this->stack = array_values(array_filter(
                $this->stack,
                fn($p) => $p['id'] !== $id
            ));
        }
    }

    #[On('popup-close-all')]
    public function closeAll(): void
    {
        $this->stack = [];
    }

    public function render()
    {
        return view('livewire.popup-manager');
    }
}
