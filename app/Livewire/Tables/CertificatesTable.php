<?php

namespace App\Livewire\Tables;

use App\Models\Certificate;
use Illuminate\Database\Eloquent\Builder;
use PowerComponents\LivewirePowerGrid\Column;
use PowerComponents\LivewirePowerGrid\Facades\Filter;
use PowerComponents\LivewirePowerGrid\Facades\PowerGrid;
use PowerComponents\LivewirePowerGrid\PowerGridComponent;
use PowerComponents\LivewirePowerGrid\PowerGridFields;

final class CertificatesTable extends PowerGridComponent
{
    public string $tableName = 'certificates-table';
    public string $sortField = 'id';
    public string $sortDirection = 'desc';

    public function setUp(): array
    {
        return [
            PowerGrid::header()
                ->showSearchInput()
                ->showToggleColumns(),

            PowerGrid::footer()
                ->showPerPage(perPage: 20, perPageValues: [10, 20, 50, 100])
                ->showRecordCount(),
        ];
    }

    public function datasource(): Builder
    {
        return Certificate::query()->with(['customer']);
    }

    public function fields(): PowerGridFields
    {
        return PowerGrid::fields()
            ->add('id')
            ->add('code')
            ->add('image_html', function ($row) {
                if ($row->image_path) {
                    $url = e(asset('storage/' . $row->image_path));
                    return '<img src="' . $url . '" style="width:38px;height:38px;object-fit:cover;border-radius:8px;border:2px solid #ddd">';
                }
                return '<div style="width:38px;height:38px;background:#f5f5f5;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:18px">💎</div>';
            })
            ->add('stone_name')
            ->add('metal')
            ->add('dimension', fn($row) => ($row->length_clean ?? '0') . '×' . ($row->width_clean ?? '0'))
            ->add('weight_clean')
            ->add('serial')
            ->add('issued_fmt', function ($row) {
                $d = $row->issued_at ?? $row->created_at;
                return $d ? \App\Support\PersianDate::format($d, 'Y/m/d H:i') : '—';
            })
            ->add('actions', function ($row) {
                $id = $row->id;
                $code = e($row->code);
                return '<div style="display:flex;gap:4px;justify-content:center">'
                    . '<button type="button" onclick="Livewire.dispatch(\'open-cert-view\', { certId: ' . $id . ' })" class="sg-action-btn view" title="نمایش">👁️</button>'
                    . '<button type="button" onclick="Livewire.dispatch(\'open-cert-form\', { certId: ' . $id . ' })" class="sg-action-btn edit" title="ویرایش">✏️</button>'
                    . '<button type="button" onclick="downloadCert(' . $id . ', \'' . $code . '\')" class="sg-action-btn" style="background:rgba(8,145,178,.15);color:#0891b2" title="دانلود">📥</button>'
                    . '<button type="button" onclick="window.open(\'/certificates/print?ids=' . $id . '&auto=1\',\'_blank\')" class="sg-action-btn" style="background:rgba(26,82,118,.15);color:#1a5276" title="چاپ">🖨️</button>'
                    . '</div>';
            });
    }

    public function columns(): array
    {
        return [
            Column::add()->title('کد')->field('code')->searchable()->sortable(),
            Column::add()->title('تصویر')->field('image_html'),
            Column::add()->title('سنگ')->field('stone_name')->searchable()->sortable(),
            Column::add()->title('فلز')->field('metal')->searchable(),
            Column::add()->title('ابعاد')->field('dimension'),
            Column::add()->title('وزن')->field('weight_clean')->sortable(),
            Column::add()->title('سریال')->field('serial')->searchable()->hidden(),
            Column::add()->title('تاریخ و ساعت')->field('issued_fmt')->sortable(),
            Column::action('actions')->title('عملیات'),
        ];
    }

    public function filters(): array
    {
        return [
            Filter::inputText('code')->operators(['contains', 'starts_with'])->placeholder('کد...'),
            Filter::inputText('stone_name')->operators(['contains', 'starts_with'])->placeholder('سنگ...'),
            Filter::inputText('metal')->operators(['contains', 'starts_with'])->placeholder('فلز...'),
            Filter::inputText('serial')->operators(['contains', 'starts_with'])->placeholder('سریال...'),
        ];
    }
}
