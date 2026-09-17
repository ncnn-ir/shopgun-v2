<?php

namespace App\Livewire\Orders;

use App\Services\TipaxImportService;
use Livewire\Component;
use Livewire\WithFileUploads;

class ImportTipax extends Component
{
    use WithFileUploads;

    public $file = null;
    public array $headers = [];
    public array $rows = [];
    public array $mapping = [];
    public ?array $result = null;

    public array $fields = [
        ''              => '— نادیده بگیر —',
        'tracking_code' => '📮 کد رهگیری',
        'order_number'  => '🔢 شماره سفارش',
        'phone'         => '📱 تلفن گیرنده',
        'receiver'      => '👤 نام گیرنده',
        'status'        => '🚦 وضعیت',
        'date'          => '📅 تاریخ',
        'description'   => '📝 توضیح',
        'city'          => '🏙️ شهر',
        'weight'        => '⚖️ وزن',
    ];

    public function updatedFile(): void
    {
        $this->validate(['file' => 'required|file|max:10240']);
        $this->result = null;

        $handle = fopen($this->file->getRealPath(), 'r');
        $bom = fread($handle, 3);
        if ($bom !== "\xEF\xBB\xBF") rewind($handle);

        $this->headers = fgetcsv($handle) ?: [];
        $this->headers = array_map(fn ($h) => trim((string) $h), $this->headers);

        $rows = [];
        while (($r = fgetcsv($handle)) !== false) {
            if (count(array_filter($r)) === 0) continue;
            $rows[] = $r;
        }
        fclose($handle);

        $this->rows = array_slice($rows, 0, 1000);

        $this->mapping = [];
        foreach ($this->headers as $i => $h) {
            $this->mapping[$i] = $this->autoDetect($h);
        }
    }

    protected function autoDetect(string $h): string
    {
        $s = mb_strtolower(trim($h));
        if (preg_match('/رهگیری|tracking|بارکد/u', $s))      return 'tracking_code';
        if (preg_match('/شماره.*سفارش|order.?num/u', $s))    return 'order_number';
        if (preg_match('/تلفن|موبایل|phone|mobile/u', $s))   return 'phone';
        if (preg_match('/گیرنده|receiver|نام/u', $s))        return 'receiver';
        if (preg_match('/وضعیت|status/u', $s))               return 'status';
        if (preg_match('/تاریخ|date|زمان/u', $s))            return 'date';
        if (preg_match('/توضیح|description|ملاحظ/u', $s))    return 'description';
        if (preg_match('/شهر|city/u', $s))                   return 'city';
        if (preg_match('/وزن|weight/u', $s))                 return 'weight';
        return '';
    }

    public function import(): void
    {
        $data = [];
        foreach ($this->rows as $row) {
            $item = [];
            foreach ($this->mapping as $idx => $field) {
                if ($field && isset($row[$idx])) {
                    $item[$field] = trim((string) $row[$idx]);
                }
            }
            if (! empty($item)) $data[] = $item;
        }

        if (empty($data)) {
            session()->flash('error', 'داده‌ای برای ایمپورت نیست');
            return;
        }

        $service = new TipaxImportService();
        $this->result = $service->import($data);

        session()->flash('success', 'ایمپورت انجام شد');
    }

    public function reset_(): void
    {
        $this->reset(['file', 'headers', 'rows', 'mapping', 'result']);
    }

    public function render()
    {
        return view('livewire.orders.import-tipax')
            ->layout('components.layouts.app');
    }
}
