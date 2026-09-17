<div style="display:flex;gap:4px">
    <button type="button" onclick="Livewire.dispatch('open-cert-view', { certId: {{ $row->id }} })" class="sg-action-btn view">👁️</button>
    <button type="button" onclick="Livewire.dispatch('open-cert-form', { certId: {{ $row->id }} })" class="sg-action-btn edit">✏️</button>
    <button type="button" onclick="window.open('{{ route("certificates.print") }}?ids={{ $row->id }}&auto=1','_blank')" class="sg-action-btn print">🖨️</button>
</div>
