from pathlib import Path

PROJECT = Path.home() / "projects" / "shopgun-v2.1"

print("=" * 60)
print("بررسی تمام ویوهای Livewire")
print("=" * 60)

views = [
    "resources/views/livewire/dashboard.blade.php",
    "resources/views/livewire/activity-log.blade.php",
    "resources/views/livewire/orders/index.blade.php",
    "resources/views/livewire/orders/create.blade.php",
    "resources/views/livewire/orders/show.blade.php",
    "resources/views/livewire/orders/edit.blade.php",
    "resources/views/livewire/orders/print-label.blade.php",
    "resources/views/livewire/orders/bulk-print-labels.blade.php",
    "resources/views/livewire/orders/courier-list.blade.php",
    "resources/views/livewire/orders/import-tipax.blade.php",
    "resources/views/livewire/orders/form-modal.blade.php",
    "resources/views/livewire/customers/index.blade.php",
    "resources/views/livewire/customers/create.blade.php",
    "resources/views/livewire/customers/show.blade.php",
    "resources/views/livewire/customers/edit.blade.php",
    "resources/views/livewire/certificates/index.blade.php",
    "resources/views/livewire/certificates/create.blade.php",
    "resources/views/livewire/certificates/show.blade.php",
    "resources/views/livewire/certificates/print-a4.blade.php",
    "resources/views/livewire/reports/index.blade.php",
    "resources/views/livewire/settings/index.blade.php",
    "resources/views/livewire/components/phone-search.blade.php",
    "resources/views/livewire/components/shipment-timeline.blade.php",
    "resources/views/livewire/notification-center.blade.php",
    "resources/views/livewire/global-search.blade.php",
]

issues = []

for v in views:
    p = PROJECT / v
    if not p.exists():
        print(f"❌ وجود نداره: {v}")
        issues.append(v)
        continue

    first_line = p.read_text(encoding="utf-8").strip().split("\n")[0].strip()

    if first_line.startswith("@extends") or first_line.startswith("@section"):
        print(f"⚠️  @extends داره: {v}")
        issues.append(v)
    elif first_line.startswith("<"):
        print(f"✅ OK: {v}")
    else:
        print(f"❓ عجیب: {v}")
        print(f"   خط اول: {first_line[:60]}")
        issues.append(v)

print()
print("=" * 60)
if issues:
    print(f"❌ {len(issues)} ویو مشکل داره")
else:
    print("✅ همه ویوها سالمن")
print("=" * 60)
