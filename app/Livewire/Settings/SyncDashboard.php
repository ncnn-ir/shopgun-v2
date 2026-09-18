<?php

namespace App\Livewire\Settings;

use App\Application\Sync\SyncEngine;
use App\Models\SyncItem;
use App\Models\SyncRun;
use Livewire\Component;
use Livewire\WithPagination;

/**
 * ★ SyncDashboard — داشبورد سینک
 */
class SyncDashboard extends Component
{
    use WithPagination;

    public string $activeTab = 'overview';

    // Start form
    public string $syncType = 'full';
    public string $syncMode = 'full';
    public bool $syncMedia = false;

    // Progress
    public ?int $currentRunId = null;
    public array $progressData = [];
    public array $syncLog = [];

    // Items filter
    public string $filterEntity = '';
    public string $filterStatus = '';

    // ═══════════════════════════════════════════════════════════
    public function startSync(): void
    {
        @set_time_limit(900);

        try {
            $engine = new SyncEngine();
            $run = $engine->createRun($this->syncType, $this->syncMode, [
                'media' => $this->syncMedia,
            ]);

            $this->currentRunId = $run->id;
            $this->activeTab = 'progress';

            $this->dispatch('notify', type: 'success', message: "سینک #{$run->id} در حال اجرا...");

            // اجرای سریع (روی local سریع‌تره از queue)
            match ($this->syncType) {
                'products' => $engine->syncProducts($run),
                'catalog' => $engine->syncCatalog($run),
                'media' => $engine->syncMedia($run),
                'full' => $engine->syncFull($run),
            };

            $this->refreshProgress();
            $this->dispatch('notify', type: 'success', message: '✅ سینک کامل شد');

        } catch (\Throwable $e) {
            $this->dispatch('notify', type: 'error', message: '❌ ' . $e->getMessage());
        }
    }

    public function refreshProgress(): void
    {
        if (!$this->currentRunId) return;

        $run = SyncRun::find($this->currentRunId);
        if (!$run) return;

        $run->recalcCounters();
        $run->refresh();

        $this->progressData = [
            'id' => $run->id,
            'type' => $run->type,
            'status' => $run->status,
            'total' => $run->total_items,
            'processed' => $run->processed_items,
            'created' => $run->created_items,
            'updated' => $run->updated_items,
            'failed' => $run->failed_items,
            'skipped' => $run->skipped_items,
            'percent' => $run->progress_percent,
            'duration' => $run->duration,
        ];

        $this->syncLog = SyncItem::where('sync_run_id', $run->id)
            ->latest('finished_at')
            ->limit(30)
            ->get()
            ->map(fn($i) => [
                'time' => $i->finished_at?->format('H:i:s') ?? '—',
                'msg' => match ($i->status) {
                    'created' => "✨ {$i->entity_type} #{$i->entity_id}",
                    'updated' => "🔄 {$i->entity_type} #{$i->entity_id}",
                    'skipped' => "⏭️ {$i->entity_type} #{$i->entity_id}",
                    'failed' => "❌ {$i->entity_type} #{$i->entity_id}: " . mb_substr($i->error_message ?? '?', 0, 50),
                    default => "{$i->entity_type} #{$i->entity_id}",
                },
                'type' => match ($i->status) {
                    'created', 'updated' => 'success',
                    'failed' => 'error',
                    'skipped' => 'warn',
                    default => 'info',
                },
            ])
            ->toArray();
    }

    public function viewRun(int $runId): void
    {
        $this->currentRunId = $runId;
        $this->activeTab = 'items';
        $this->refreshProgress();
    }

    public function cancelRun(): void
    {
        if (!$this->currentRunId) return;
        $run = SyncRun::find($this->currentRunId);
        if ($run) (new SyncEngine())->cancel($run);
        $this->refreshProgress();
        $this->dispatch('notify', type: 'success', message: 'لغو شد');
    }

    public function deleteRun(int $id): void
    {
        SyncRun::find($id)?->delete();
        $this->dispatch('notify', type: 'success', message: 'حذف شد');
    }

    public function render()
    {
        $runs = SyncRun::latest('id')->limit(20)->paginate(15, ['*'], 'runs');

        $items = collect();
        if ($this->currentRunId && $this->activeTab === 'items') {
            $items = SyncItem::where('sync_run_id', $this->currentRunId)
                ->when($this->filterEntity, fn($q) => $q->where('entity_type', $this->filterEntity))
                ->when($this->filterStatus, fn($q) => $q->where('status', $this->filterStatus))
                ->orderByDesc('id')
                ->paginate(30);
        }

        return view('livewire.settings.sync-dashboard', [
            'runs' => $runs,
            'items' => $items,
        ]);
    }
}
