<div style="padding:14px;direction:rtl">

    <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px;flex-wrap:wrap;gap:8px">
        <div>
            <h2 style="margin:0;font-size:16px;font-weight:700;color:#1a5276">🎨 قالب‌های شناسنامه</h2>
            <p style="margin:4px 0 0;font-size:11.5px;color:#64748b">چند نسخه از طرح شناسنامه بساز، منتشر کن، و روی شناسنامه‌ها اعمال کن</p>
        </div>
        <button wire:click="openForm()"
                style="padding:8px 18px;background:linear-gradient(135deg,#1a5276,#0d3b5e);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">
            ➕ قالب جدید
        </button>
    </div>

    @if($templates->isEmpty())
        <div style="text-align:center;padding:40px;color:#94a3b8;background:#fff;border-radius:12px;border:1px solid #e2e8f0">
            <div style="font-size:44px;opacity:.4">🎨</div>
            <div style="font-size:13px;margin-top:8px">هنوز قالبی ساخته نشده</div>
            <button wire:click="openForm()" style="margin-top:10px;padding:7px 16px;background:#1a5276;color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">➕ اولین قالب</button>
        </div>
    @else
        <div style="display:grid;grid-template-columns:repeat(auto-fill,minmax(260px,1fr));gap:12px">
            @foreach($templates as $t)
                <div style="background:#fff;border:1.5px solid {{ $t->is_default ? '#c9a84c' : '#e2e8f0' }};border-radius:12px;padding:14px;position:relative">
                    @if($t->is_default)
                        <div style="position:absolute;top:-8px;right:12px;background:#c9a84c;color:#fff;padding:2px 10px;border-radius:10px;font-size:10px;font-weight:700">🌟 پیش‌فرض</div>
                    @endif

                    <div style="display:flex;align-items:center;gap:10px;margin-bottom:10px">
                        <div style="width:40px;height:40px;border-radius:10px;background:linear-gradient(135deg,#fef3c7,#fde68a);display:flex;align-items:center;justify-content:center;font-size:20px">🎨</div>
                        <div style="flex:1;min-width:0">
                            <div style="font-weight:700;font-size:13px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap">{{ $t->name }}</div>
                            <div style="font-family:monospace;font-size:10px;color:#94a3b8">v{{ $t->version }}</div>
                        </div>
                        <span style="padding:3px 10px;border-radius:10px;font-size:10px;font-weight:700;
                            @if($t->status === 'published') background:#d1fae5;color:#065f46
                            @elseif($t->status === 'draft') background:#fef3c7;color:#92400e
                            @else background:#f1f5f9;color:#475569 @endif">
                            {{ match($t->status) { 'published'=>'✅ منتشر', 'draft'=>'📝 پیش‌نویس', 'archived'=>'📦 آرشیو', default=>$t->status } }}
                        </span>
                    </div>

                    @if($t->description)
                        <div style="font-size:11px;color:#64748b;margin-bottom:8px;line-height:1.5">{{ \Illuminate\Support\Str::limit($t->description, 80) }}</div>
                    @endif

                    <div style="font-size:10.5px;color:#94a3b8;margin-bottom:10px">
                        📊 استفاده شده: {{ \App\Support\PersianNumber::toFa($t->certificates_count) }} شناسنامه
                    </div>

                    <div style="display:flex;gap:4px;flex-wrap:wrap">
                        <a href="{{ route('certificates.designer') }}?template={{ $t->id }}" wire:navigate
                           style="flex:1;text-align:center;padding:6px 10px;background:#7c3aed;color:#fff;border:none;border-radius:6px;font-weight:700;font-size:11px;text-decoration:none">
                            🎨 ویرایش
                        </a>
                        <button wire:click="duplicate({{ $t->id }})" title="کپی"
                                style="padding:6px 10px;background:#f1f5f9;color:#475569;border:1px solid #cbd5e1;border-radius:6px;font-size:11px;cursor:pointer">📋</button>
                        @if($t->status === 'draft')
                            <button wire:click="publish({{ $t->id }})" title="انتشار"
                                    style="padding:6px 10px;background:#d1fae5;color:#065f46;border:1px solid #34d399;border-radius:6px;font-size:11px;font-weight:700;cursor:pointer">✓</button>
                        @endif
                        @if(!$t->is_default && $t->status === 'published')
                            <button wire:click="setDefault({{ $t->id }})" title="پیش‌فرض"
                                    style="padding:6px 10px;background:#fef3c7;color:#92400e;border:1px solid #fbbf24;border-radius:6px;font-size:11px;cursor:pointer">🌟</button>
                        @endif
                        <button wire:click="openForm({{ $t->id }})" title="ویرایش نام"
                                style="padding:6px 10px;background:#fff;color:#475569;border:1px solid #cbd5e1;border-radius:6px;font-size:11px;cursor:pointer">✏️</button>
                        <button wire:click="delete({{ $t->id }})" wire:confirm="حذف شود؟" title="حذف"
                                style="padding:6px 10px;background:#fee2e2;color:#dc2626;border:1px solid #fca5a5;border-radius:6px;font-size:11px;cursor:pointer">🗑️</button>
                    </div>
                </div>
            @endforeach
        </div>
    @endif

    {{-- Form Modal --}}
    @if($showForm)
        <div style="position:fixed;inset:0;background:rgba(0,0,0,.75);z-index:95;display:flex;align-items:center;justify-content:center;padding:14px"
             @keydown.escape.window="$wire.closeForm()">
            <div style="background:#fff;width:100%;max-width:440px;border-radius:14px;overflow:hidden">
                <div style="background:linear-gradient(135deg,#1a5276,#0d3b5e);color:#fff;padding:12px 16px;display:flex;justify-content:space-between;align-items:center">
                    <h3 style="margin:0;font-size:14px">{{ $editingId ? '✏️ ویرایش قالب' : '➕ قالب جدید' }}</h3>
                    <button wire:click="closeForm" style="background:rgba(255,255,255,.2);color:#fff;border:none;width:28px;height:28px;border-radius:50%;cursor:pointer;font-size:13px">✕</button>
                </div>
                <div style="padding:14px">
                    <div style="margin-bottom:10px">
                        <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">نام قالب *</label>
                        <input type="text" wire:model="name" style="width:100%;padding:8px 10px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:12px;box-sizing:border-box">
                        @error('name') <div style="color:#dc2626;font-size:10.5px;margin-top:3px">{{ $message }}</div> @enderror
                    </div>
                    <div style="margin-bottom:10px">
                        <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">توضیحات</label>
                        <textarea wire:model="description" rows="3" style="width:100%;padding:8px 10px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:12px;box-sizing:border-box"></textarea>
                    </div>
                    <div>
                        <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">نسخه *</label>
                        <input type="text" wire:model="version" dir="ltr" style="width:100%;padding:8px 10px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:12px;font-family:monospace;box-sizing:border-box">
                    </div>
                </div>
                <div style="padding:12px 16px;background:#f8fafc;border-top:1px solid #e2e8f0;display:flex;justify-content:flex-end;gap:6px">
                    <button wire:click="closeForm" style="padding:7px 14px;background:#fff;color:#475569;border:1.5px solid #cbd5e1;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">انصراف</button>
                    <button wire:click="save" style="padding:7px 18px;background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer;font-size:12px">💾 ذخیره</button>
                </div>
            </div>
        </div>
    @endif
</div>
