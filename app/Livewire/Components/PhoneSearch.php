<?php

namespace App\Livewire\Components;

use App\Models\Customer;
use App\Models\Order;
use Livewire\Attributes\Modelable;
use Livewire\Component;

class PhoneSearch extends Component
{
    #[Modelable]
    public string $value = '';

    public string $placeholder = '09151234567';
    public array $suggestions = [];
    public bool $showDropdown = false;

    public function updatedValue(): void
    {
        // ارسال فوری مقدار به پدر
        $this->dispatch('phone-typed', value: $this->value);
        $this->search();
    }

    public function search(): void
    {
        $raw    = (string) $this->value;
        $digits = preg_replace('/\D/', '', $raw);
        $norm   = $this->normalize($digits);

        if (strlen($norm) < 3) {
            $this->suggestions  = [];
            $this->showDropdown = false;
            return;
        }

        $map = [];

        // جستجو در سفارشات
        Order::query()
            ->with('customer')
            ->where(function ($q) use ($digits, $norm) {
                $q->where('phone', 'like', "%{$digits}%")
                  ->orWhere('phone', 'like', "%{$norm}%");
            })
            ->latest('id')
            ->limit(30)
            ->get()
            ->each(function ($o) use (&$map) {
                $p = $this->normalize((string) ($o->phone ?? ''));
                if (! $p) return;

                if (! isset($map[$p])) {
                    $map[$p] = [
                        'phone'   => $o->phone,
                        'norm'    => $p,
                        'name'    => $o->customer?->name ?? '',
                        'address' => $o->address ?? '',
                        'postal'  => $o->postal_code ?? '',
                        'count'   => 0,
                        'ts'      => 0,
                    ];
                }
                $map[$p]['count']++;
                $ts = $o->created_at?->getTimestamp() ?? 0;
                if ($ts > $map[$p]['ts']) {
                    $map[$p]['name']    = $o->customer?->name ?? $map[$p]['name'];
                    $map[$p]['address'] = $o->address ?? $map[$p]['address'];
                    $map[$p]['postal']  = $o->postal_code ?? $map[$p]['postal'];
                    $map[$p]['ts']      = $ts;
                }
            });

        // جستجو در مشتریان
        Customer::query()
            ->where(function ($q) use ($digits, $norm) {
                $q->where('phone', 'like', "%{$digits}%")
                  ->orWhere('phone', 'like', "%{$norm}%");
            })
            ->limit(30)
            ->get()
            ->each(function ($c) use (&$map) {
                $p = $this->normalize((string) ($c->phone ?? ''));
                if (! $p) return;

                if (! isset($map[$p])) {
                    $map[$p] = [
                        'phone'   => $c->phone,
                        'norm'    => $p,
                        'name'    => $c->name ?? '',
                        'address' => $c->address ?? '',
                        'postal'  => $c->postal_code ?? '',
                        'count'   => 0,
                        'ts'      => 0,
                    ];
                } else {
                    if (! $map[$p]['name'] && $c->name)         $map[$p]['name']    = $c->name;
                    if (! $map[$p]['address'] && $c->address)   $map[$p]['address'] = $c->address;
                    if (! $map[$p]['postal'] && $c->postal_code) $map[$p]['postal']  = $c->postal_code;
                }
            });

        $list = array_values($map);
        usort($list, function ($a, $b) use ($norm) {
            $aExact = ($a['norm'] === $norm) ? 1 : 0;
            $bExact = ($b['norm'] === $norm) ? 1 : 0;
            if ($aExact !== $bExact) return $bExact - $aExact;
            return ($b['count'] ?? 0) - ($a['count'] ?? 0);
        });

        $this->suggestions  = array_slice($list, 0, 10);
        $this->showDropdown = ! empty($this->suggestions);
    }

    public function select(string $phone, string $name, string $address, string $postal): void
    {
        $this->value = $phone;
        $this->showDropdown = false;
        $this->suggestions  = [];

        $this->dispatch('phone-selected', [
            'phone'   => $phone,
            'name'    => $name,
            'address' => $address,
            'postal'  => $postal,
        ]);
    }

    protected function normalize(string $phone): string
    {
        $digits = preg_replace('/\D/', '', $phone);
        if (str_starts_with($digits, '0098')) {
            $digits = substr($digits, 4);
        } elseif (str_starts_with($digits, '98') && strlen($digits) > 10) {
            $digits = substr($digits, 2);
        }
        if (str_starts_with($digits, '0') && strlen($digits) > 10) {
            $digits = substr($digits, 1);
        }
        return $digits;
    }

    public function render()
    {
        return view('livewire.components.phone-search');
    }
}
