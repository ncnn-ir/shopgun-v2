<?php

namespace App\Livewire\Products;

use App\Application\Bulk\BulkEngine;
use App\Models\BulkItem;
use App\Models\BulkRun;
use Livewire\Component;
use Livewire\WithPagination;

/**
 * ★ BulkRunDetail — صفحه جزئیات یک Bulk Run
 * نمایش همه آیتم‌ها با فیلتر و صفحه‌بندی و retry
 */
class BulkRunDetail extends Component
{
    use WithPagination;

    public int $runId;
    public ?BulkRun $run = null;

    public string $filterStatus = '';
    public string $search = '';
    public string $sortBy = 'id';
    public string $sortDir = 'desc';

    public bool $showItemDetail = false;
    public ?array $itemDetail = null;

    public function mount(int $run): void
    {
        $this->runId = $run;
        $this->run = BulkRun::find($run);
        if (!$this->run) {
            abort(404, 'Run یافت نشد');
        }
    }

    public function updatingFilterStatus(): void { $this->resetPage(); }
    public function updatingSearch(): void { $this->resetPage(); }

    public function refresh(): void
    {
        $this->run = BulkRun::find($this->runId);
        if ($this->run) $this->run->recalcCounters();
        $this->dispatch('notify', type: 'success', message: 'بروزرسانی شد');
    }

    public function retryFailed(): void
    {
        if (!$this->run) return;
        try {
            (new BulkEngine())->retryFailed($this->run);
            $this->dispatch('notify', type: 'success', message: 'آیتم‌های ناموفق به صف جدید اضافه شدند');
        } catch (\Throwable $e) {
            $this->dispatch('notify', type: 'error', message: $e->getMessage());
        }
    }

    public function cancel(): void
    {
        if (!$this->run) return;
        (new BulkEngine())->cancel($this->run);
        $this->run = BulkRun::find($this->runId);
        $this->dispatch('notify', type: 'success', message: 'لغو شد');
    }

    public function showItem(int $itemId): void
    {
        $item = BulkItem::find($itemId);
        if (!$item) return;

        $this->itemDetail = [
            'id' => $item->id,
            'sku' => $item->sku,
            'status' => $item->status,
            'woo_product_id' => $item->woo_product_id,
            'error_message' => $item->error_message,
            'error_code' => $item->error_code,
            'warnings' => $item->validation_warnings ?? [],
            'input' => $item->input_data ?? [],
            'request' => $item->request_payload,
            'response' => $item->response_payload,
            'diff' => $item->diff_data,
            'attempt' => $item->attempt,
            'edit_url' => $item->woo_edit_url,
            'view_url' => $item->woo_view_url,
            'started_at' => $item->started_at?->format('Y/m/d H:i:s'),
            'finished_at' => $item->finished_at?->format('Y/m/d H:i:s'),
        ];
        $this->showItemDetail = true;
    }

    public function closeItem(): void
    {
        $this->showItemDetail = false;
        $this->itemDetail = null;
    }

    public function render()
    {
        $items = BulkItem::query()
            ->where('run_id', $this->runId)
            ->when($this->filterStatus, fn($q) => $q->where('status', $this->filterStatus))
            ->when($this->search, fn($q) => $q->where('sku', 'like', "%{$this->search}%"))
            ->orderBy($this->sortBy, $this->sortDir)
            ->paginate(30);

        $statusCounts = BulkItem::query()
            ->where('run_id', $this->runId)
            ->selectRaw('status, COUNT(*) as cnt')
            ->groupBy('status')
            ->pluck('cnt', 'status')
            ->toArray();

        return view('livewire.products.bulk-run-detail', [
            'items' => $items,
            'statusCounts' => $statusCounts,
        ])->layout('components.layouts.app');
    }
}
