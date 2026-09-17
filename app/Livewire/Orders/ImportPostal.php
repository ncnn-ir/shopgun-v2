<?php
namespace App\Livewire\Orders;

use App\Models\Order;
use Livewire\Attributes\On;
use Livewire\Component;
use Livewire\WithFileUploads;

class ImportPostal extends Component
{
    use WithFileUploads;

    public bool $show = false;
    public $file = null;
    public array $columns = [];
    public array $rows = [];
    public array $mapping = [];    // index => field name
    public array $preview = [];
    public int $matched = 0;
    public int $unmatched = 0;

    public array $availableFields = [
        '' => '— نادیده بگیر —',
        'phone' => '📱 تلفن گیرنده',
        'tracking' => '📮 کد رهگیری',
        'status' => '🚦 وضعیت',
        'weight' => '⚖️ وزن',
        'insurance' => '💰 بیمه',
        'cost' => '💸 کرایه',
        'date' => '📅 تاریخ',
        'receiver' => '👤 نام گیرنده',
        'city' => '🏙️ شهر',
    ];

    #[On('open-import-postal')]
    public function open(): void
    {
        $this->reset(['file','columns','rows','mapping','preview','matched','unmatched']);
        $this->show = true;
    }

    public function close(): void { $this->show = false; }

    public function updatedFile(): void
    {
        $this->validate(['file' => 'file|max:10240']);

        $path = $this->file->getRealPath();
        $content = file_get_contents($path);
        $content = preg_replace('/^\xEF\xBB\xBF/', '', $content);

        $delimiter = $this->detectDelimiter($content);
        $allRows = $this->parseCsv($content, $delimiter);

        if (count($allRows) < 2) {
            $this->dispatch('notify', type: 'error', message: 'فایل خالی یا نامعتبر');
            return;
        }

        $this->columns = $allRows[0];
        $this->rows = array_slice($allRows, 1);
        $this->rows = array_values(array_filter($this->rows, fn($r) => count(array_filter($r, fn($c) => trim($c) !== '')) > 0));
        $this->preview = array_slice($this->rows, 0, 5);

        // Auto-detect mapping
        $this->mapping = [];
        foreach ($this->columns as $i => $col) {
            $this->mapping[$i] = $this->autoDetect($col);
        }

        $this->calculateStats();
        $this->dispatch('notify', type: 'success', message: count($this->rows) . ' ردیف بارگذاری شد');
    }

    protected function detectDelimiter(string $content): string
    {
        $candidates = ["\t", ",", ";", "|"];
        $lines = array_slice(array_filter(explode("\n", $content)), 0, 5);
        $best = ','; $bestScore = 0;
        foreach ($candidates as $d) {
            $score = 0;
            foreach ($lines as $line) $score += substr_count($line, $d);
            if ($score > $bestScore) { $bestScore = $score; $best = $d; }
        }
        return $best;
    }

    protected function parseCsv(string $text, string $delimiter): array
    {
        $rows = []; $cur = ''; $row = []; $inQuotes = false;
        $len = strlen($text);
        for ($i = 0; $i < $len; $i++) {
            $ch = $text[$i];
            if ($inQuotes) {
                if ($ch === '"') {
                    if ($i + 1 < $len && $text[$i + 1] === '"') { $cur .= '"'; $i++; }
                    else $inQuotes = false;
                } else $cur .= $ch;
            } else {
                if ($ch === '"') $inQuotes = true;
                elseif ($ch === $delimiter) { $row[] = $cur; $cur = ''; }
                elseif ($ch === "\n" || $ch === "\r") {
                    if ($cur !== '' || count($row)) { $row[] = $cur; $rows[] = $row; $row = []; $cur = ''; }
                    if ($ch === "\r" && $i + 1 < $len && $text[$i + 1] === "\n") $i++;
                } else $cur .= $ch;
            }
        }
        if ($cur !== '' || count($row)) { $row[] = $cur; $rows[] = $row; }
        return $rows;
    }

    protected function autoDetect(string $col): string
    {
        $c = mb_strtolower(trim($col));
        if (preg_match('/تلفن|موبایل|phone|mobile|tel/u', $c)) return 'phone';
        if (preg_match('/رهگیری|مرسوله|tracking|barcode|بارکد/u', $c)) return 'tracking';
        if (preg_match('/وضعیت|status/u', $c)) return 'status';
        if (preg_match('/وزن|weight/u', $c)) return 'weight';
        if (preg_match('/بیمه|insurance/u', $c)) return 'insurance';
        if (preg_match('/کرایه|هزینه|cost|fee/u', $c)) return 'cost';
        if (preg_match('/تاریخ|date/u', $c)) return 'date';
        if (preg_match('/گیرنده|receiver|name/u', $c)) return 'receiver';
        if (preg_match('/شهر|city/u', $c)) return 'city';
        return '';
    }

    public function updatedMapping(): void { $this->calculateStats(); }

    protected function calculateStats(): void
    {
        $this->matched = 0;
        $this->unmatched = 0;

        foreach ($this->rows as $row) {
            $data = $this->extractRow($row);
            if (empty($data['phone'])) { $this->unmatched++; continue; }
            $np = preg_replace('/\D/', '', $data['phone']);
            if (str_starts_with($np, '98')) $np = substr($np, 2);
            if (str_starts_with($np, '0')) $np = substr($np, 1);

            $exists = Order::where('phone', 'like', "%{$np}%")->exists();
            if ($exists) $this->matched++;
            else $this->unmatched++;
        }
    }

    protected function extractRow(array $row): array
    {
        $data = [];
        foreach ($this->mapping as $idx => $field) {
            if (!$field) continue;
            $data[$field] = trim($row[$idx] ?? '');
        }
        return $data;
    }

    public function save(): void
    {
        $applied = 0; $skipped = 0;

        foreach ($this->rows as $row) {
            $data = $this->extractRow($row);
            if (empty($data['phone'])) { $skipped++; continue; }

            $np = preg_replace('/\D/', '', $data['phone']);
            if (str_starts_with($np, '98')) $np = substr($np, 2);
            if (str_starts_with($np, '0')) $np = substr($np, 1);

            // پیدا کردن آخرین سفارش این مشتری
            $order = Order::where('phone', 'like', "%{$np}%")->latest('id')->first();
            if (!$order) { $skipped++; continue; }

            $update = [];
            if (!empty($data['tracking'])) $update['tracking_code'] = $data['tracking'];
            if (!empty($data['status'])) $update['postal_status'] = $data['status'];
            if (!empty($data['weight'])) $update['weight'] = (float) preg_replace('/[^\d.]/', '', $data['weight']);
            if (!empty($data['insurance'])) $update['insurance'] = (float) preg_replace('/[^\d.]/', '', $data['insurance']);
            if (!empty($data['cost'])) $update['shipping'] = (float) preg_replace('/[^\d.]/', '', $data['cost']);

            // ذخیره در meta برای اطمینان
            $meta = $order->meta ?? [];
            $meta['postal'] = array_merge($meta['postal'] ?? [], $data);
            $update['meta'] = $meta;

            if (!empty($update)) {
                $order->update($update);
                $applied++;
            } else {
                $skipped++;
            }
        }

        $this->dispatch('order-saved');
        $this->dispatch('notify', type: 'success', message: "{$applied} سفارش بروزرسانی شد · {$skipped} رد شد");
        $this->close();
    }

    public function render() { return view('livewire.orders.import-postal'); }
}
