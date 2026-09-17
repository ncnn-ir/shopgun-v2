<div style="padding:14px;max-width:700px;margin:0 auto" dir="rtl">
    <div style="display:flex;align-items:center;gap:10px;margin-bottom:20px">
        <a href="{{ route('customers.show', $customer) }}" style="width:36px;height:36px;border-radius:50%;background:#f1f5f9;display:flex;align-items:center;justify-content:center;text-decoration:none;color:#1a5276;font-weight:700">→</a>
        <h1 style="margin:0;font-size:22px;font-weight:700">✏️ ویرایش مشتری</h1>
    </div>

    <div style="background:#fff;border:1px solid #e2e8f0;border-radius:14px;padding:20px">
        <div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-bottom:14px">
            <div>
                <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">📱 تلفن *</label>
                <input type="text" wire:model="phone" dir="ltr"
                       style="width:100%;padding:10px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-family:monospace;font-size:14px;background:#f8fafc;box-sizing:border-box">
                @error('phone') <div style="color:#dc2626;font-size:10px;margin-top:3px">{{ $message }}</div> @enderror
            </div>
            <div>
                <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">👤 نام</label>
                <input type="text" wire:model="name"
                       style="width:100%;padding:10px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:14px;background:#f8fafc;box-sizing:border-box">
            </div>
        </div>

        <div style="margin-bottom:14px">
            <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">📮 کدپستی</label>
            <input type="text" wire:model="postalCode" dir="ltr"
                   style="width:100%;padding:10px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-family:monospace;font-size:14px;background:#f8fafc;box-sizing:border-box">
        </div>

        <div style="margin-bottom:14px">
            <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">📍 آدرس</label>
            <textarea wire:model="address" rows="3"
                      style="width:100%;padding:10px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:14px;background:#f8fafc;box-sizing:border-box"></textarea>
        </div>

        <div style="margin-bottom:14px">
            <label style="display:block;font-size:11px;font-weight:700;color:#1a5276;margin-bottom:4px">📝 یادداشت</label>
            <textarea wire:model="notes" rows="2"
                      style="width:100%;padding:10px 12px;border:1.5px solid #cbd5e1;border-radius:8px;font-size:14px;background:#f8fafc;box-sizing:border-box"></textarea>
        </div>

        <div style="display:flex;justify-content:flex-end;gap:8px;padding-top:14px;border-top:1px solid #e2e8f0">
            <a href="{{ route('customers.show', $customer) }}"
               style="padding:10px 20px;background:#fff;color:#475569;border:1.5px solid #cbd5e1;border-radius:8px;font-weight:700;text-decoration:none">انصراف</a>
            <button type="button" wire:click="save" wire:loading.attr="disabled"
                    style="padding:10px 24px;background:linear-gradient(135deg,#16a34a,#15803d);color:#fff;border:none;border-radius:8px;font-weight:700;cursor:pointer">
                <span wire:loading.remove wire:target="save">✓ ذخیره</span>
                <span wire:loading wire:target="save">⏳...</span>
            </button>
        </div>
    </div>
</div>
