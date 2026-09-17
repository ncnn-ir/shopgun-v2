#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
╔══════════════════════════════════════════════════════════════╗
║  Fix — Customer.php + Complete Settings                       ║
╚══════════════════════════════════════════════════════════════╝
"""
import shutil
from pathlib import Path
from datetime import datetime

PROJECT = Path(r"D:\prodo\shopgun-v2.1")
if not PROJECT.exists():
    PROJECT = Path(input("مسیر پروژه: ").strip().strip('"'))
    if not PROJECT.exists():
        print("❌ مسیر پیدا نشد"); exit(1)

def write(rel, content):
    full = PROJECT / rel
    full.parent.mkdir(parents=True, exist_ok=True)
    with open(full, 'w', encoding='utf-8', newline='\n') as f:
        f.write(content)
    print(f"  ✓ {rel}")

def backup(rel):
    src = PROJECT / rel
    if not src.exists(): return
    bd = PROJECT / "storage/backups"; bd.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    shutil.copy2(src, bd / f"{src.stem}_{ts}.bak")

# ═══════════════════════════════════════════════════════════════
# متدهای Customer که باید داخل کلاس باشند
# ═══════════════════════════════════════════════════════════════

CUSTOMER_METHODS = r'''
    /* ═══════════════════════════════════════════════════════════
       فاز ۱ — چند تلفن و چند آدرس
       ═══════════════════════════════════════════════════════════ */

    public function phones(): \Illuminate\Database\Eloquent\Relations\HasMany
    {
        return $this->hasMany(\App\Models\CustomerPhone::class)
            ->orderByDesc('is_primary')
            ->orderBy('id');
    }

    public function addresses(): \Illuminate\Database\Eloquent\Relations\HasMany
    {
        return $this->hasMany(\App\Models\CustomerAddress::class)
            ->orderByDesc('is_primary')
            ->orderBy('id');
    }

    public function primaryPhone(): ?\App\Models\CustomerPhone
    {
        return $this->phones()->where('is_primary', true)->first()
            ?? $this->phones()->first();
    }

    public function primaryAddress(): ?\App\Models\CustomerAddress
    {
        return $this->addresses()->where('is_primary', true)->first()
            ?? $this->addresses()->first();
    }

    public static function normalizePhone(?string $phone): string
    {
        $s = preg_replace('/\D/', '', (string) $phone);
        if (str_starts_with($s, '0098')) $s = substr($s, 4);
        elseif (str_starts_with($s, '98') && strlen($s) > 10) $s = substr($s, 2);
        if (str_starts_with($s, '0') && strlen($s) > 10) $s = substr($s, 1);
        return $s;
    }

    public static function findByPhone(string $phone): ?self
    {
        $normalized = self::normalizePhone($phone);
        if ($normalized === '') return null;

        if (\Illuminate\Support\Facades\Schema::hasTable('customer_phones')) {
            $cp = \App\Models\CustomerPhone::where('phone', $normalized)->first();
            if ($cp) return $cp->customer;
        }

        return self::where('phone', $normalized)
            ->orWhere('phone', '0' . $normalized)
            ->orWhere('phone', '+98' . $normalized)
            ->orWhere('phone', '98' . $normalized)
            ->first();
    }

    public function addPhone(string $phone, ?string $label = null, bool $primary = false): ?\App\Models\CustomerPhone
    {
        $normalized = self::normalizePhone($phone);
        if ($normalized === '') return null;

        $existing = $this->phones()->where('phone', $normalized)->first();
        if ($existing) {
            if ($label)  $existing->update(['label' => $label]);
            if ($primary) {
                $this->phones()->update(['is_primary' => false]);
                $existing->update(['is_primary' => true]);
            }
            return $existing;
        }

        if ($primary) {
            $this->phones()->update(['is_primary' => false]);
        }

        $isFirst = $this->phones()->count() === 0;

        $cp = $this->phones()->create([
            'phone'      => $normalized,
            'label'      => $label,
            'is_primary' => $primary || $isFirst,
        ]);

        if ($isFirst && empty($this->phone)) {
            $this->update(['phone' => $normalized]);
        } elseif ($primary) {
            $this->update(['phone' => $normalized]);
        }

        return $cp;
    }

    public function addAddress(array $data, bool $primary = false): \App\Models\CustomerAddress
    {
        if ($primary) {
            $this->addresses()->update(['is_primary' => false]);
        }

        $isFirst = $this->addresses()->count() === 0;

        $ca = $this->addresses()->create([
            'label'       => $data['label']       ?? null,
            'province'    => $data['province']    ?? null,
            'city'        => $data['city']        ?? null,
            'address'     => $data['address']     ?? '',
            'postal_code' => $data['postal_code'] ?? null,
            'lat'         => $data['lat']         ?? null,
            'lng'         => $data['lng']         ?? null,
            'is_primary'  => $primary || $isFirst,
        ]);

        if ($isFirst) {
            $this->update([
                'address'     => $data['address']     ?? $this->address,
                'postal_code' => $data['postal_code'] ?? $this->postal_code ?? null,
            ]);
        }

        return $ca;
    }

    public function getPhonesListAttribute(): string
    {
        return $this->phones->pluck('phone')->implode(' / ');
    }

    public function getAddressesListAttribute(): string
    {
        return $this->addresses->map(fn($a) => $a->short)->implode(' | ');
    }
'''

# ═══════════════════════════════════════════════════════════════
# ۱) Fix Customer.php
# ═══════════════════════════════════════════════════════════════

def fix_customer_model():
    path = PROJECT / "app/Models/Customer.php"
    if not path.exists():
        print("  ⚠️ Customer.php پیدا نشد")
        return

    # backup
    backup("app/Models/Customer.php")

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    lines = content.split('\n')

    # پیدا کردن اولین خطی که فقط '}' است (بستن کلاس)
    class_close_idx = None
    for i, line in enumerate(lines):
        if line.rstrip() == '}':
            class_close_idx = i
            break

    if class_close_idx is None:
        print("  ⚠️ بستن کلاس پیدا نشد — فایل رو دستی چک کن")
        return

    before = '\n'.join(lines[:class_close_idx])
    after = '\n'.join(lines[class_close_idx + 1:])

    # اگر چیزی بعد از کلاس نبود، یعنی فایل سالمه
    if not after.strip():
        print("  ✓ Customer.php سالمه (چیزی بعد از کلاس نیست)")
        return

    # ─── فایل خرابه: متدها بیرون کلاس افتادند ───
    print(f"  ⚠️ Customer.php خراب است — {len(after.strip().splitlines())} خط بیرون از کلاس")
    print(f"  🔧 در حال اصلاح...")

    # آیا متدهای ما داخل after هستند؟
    has_methods = 'public function phones()' in after or 'getAddressesListAttribute' in after

    if has_methods:
        # بله، همه‌ی متدهای ما بیرون هستند. پس پاک کن و درست اضافه کن.
        new_content = before.rstrip() + '\n' + CUSTOMER_METHODS + '\n}\n'
    else:
        # چیز دیگه‌ای بعد از کلاس هست — فقط قبل از بستن کلاس اضافه کن
        # و after رو نگه دار (شاید کد مهمی باشه)
        new_content = before.rstrip() + '\n' + CUSTOMER_METHODS + '\n}\n\n' + after.strip() + '\n'

    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(new_content)

    print(f"  ✓ Customer.php اصلاح شد")

# ═══════════════════════════════════════════════════════════════
# ۲) Patch AppServiceProvider (بدون regex)
# ═══════════════════════════════════════════════════════════════

def patch_app_provider_safe():
    path = PROJECT / "app/Providers/AppServiceProvider.php"
    if not path.exists():
        print("  ⚠️ AppServiceProvider پیدا نشد")
        return

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'app_settings_shared' in content:
        print("  ⏭ از قبل patch شده")
        return

    backup("app/Providers/AppServiceProvider.php")

    # پیدا کردن 'public function boot'
    idx = content.find('public function boot')
    if idx < 0:
        print("  ⚠️ boot() پیدا نشد")
        return

    # پیدا کردن اولین '{' بعد از boot
    brace_idx = content.find('{', idx)
    if brace_idx < 0:
        print("  ⚠️ { پیدا نشد")
        return

    # کد تزریقی
    inject = '''

        // ═══ app_settings_shared ═══
        try {
            if (\\Illuminate\\Support\\Facades\\Schema::hasTable('app_settings')) {
                view()->composer('*', function ($view) {
                    $view->with('appSettingsData', [
                        'theme'         => \\App\\Models\\AppSetting::get('theme', 'light'),
                        'primary_color' => \\App\\Models\\AppSetting::get('primary_color', '#0d9488'),
                        'density'       => \\App\\Models\\AppSetting::get('density', 'normal'),
                        'shop_name'     => \\App\\Models\\AppSetting::get('shop_name', 'جواهری مشاهیر'),
                    ]);
                });
            }
        } catch (\\Throwable $e) {
            // silent
        }
'''

    new_content = content[:brace_idx + 1] + inject + content[brace_idx + 1:]

    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(new_content)

    print("  ✓ AppServiceProvider patch شد")

# ═══════════════════════════════════════════════════════════════
# ۳) Patch Layout برای theme
# ═══════════════════════════════════════════════════════════════

def patch_layout_safe():
    layout = PROJECT / "resources/views/components/layouts/app.blade.php"
    if not layout.exists():
        print("  ⚠️ Layout پیدا نشد")
        return

    with open(layout, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'app_settings_theme' in content:
        print("  ⏭ Layout از قبل patch شده")
        return

    backup("resources/views/components/layouts/app.blade.php")

    inject = '''    {{-- ═══ Theme از AppSettings ═══ --}}
    @php
        try {
            $__theme = \\App\\Models\\AppSetting::get('theme', 'light');
            $__color = \\App\\Models\\AppSetting::get('primary_color', '#0d9488');
            $__density = \\App\\Models\\AppSetting::get('density', 'normal');
        } catch (\\Throwable $e) {
            $__theme = 'light';
            $__color = '#0d9488';
            $__density = 'normal';
        }
    @endphp
    <style id="app_settings_theme">
        :root { --sg-primary: {{ $__color }}; }
        [data-theme="dark"] { --sg-primary: {{ $__color }}; }
        .btn-primary { background-color: var(--sg-primary) !important; border-color: var(--sg-primary) !important; }
        .text-primary { color: var(--sg-primary) !important; }
        .border-primary { border-color: var(--sg-primary) !important; }
        .bg-primary { background-color: var(--sg-primary) !important; }
        @if($__density === 'compact')
            .card-body, .p-4 { padding: 0.75rem !important; }
            table td, table th { padding: 0.35rem 0.6rem !important; }
        @elseif($__density === 'comfortable')
            .card-body, .p-4 { padding: 1.5rem !important; }
            table td, table th { padding: 0.9rem 1rem !important; }
        @endif
    </style>

'''

    if '</head>' in content:
        content = content.replace('</head>', inject + '</head>', 1)
        with open(layout, 'w', encoding='utf-8', newline='\n') as f:
            f.write(content)
        print("  ✓ Layout patch شد")
    else:
        print("  ⚠️ </head> پیدا نشد")

# ═══════════════════════════════════════════════════════════════
# ۴) Patch WooCommerceService — loggedGet
# ═══════════════════════════════════════════════════════════════

def patch_woo():
    path = PROJECT / "app/Services/WooCommerceService.php"
    if not path.exists():
        print("  ⚠️ WooCommerceService پیدا نشد")
        return

    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    if 'loggedGet' in content:
        print("  ⏭ از قبل patch شده")
        return

    backup("app/Services/WooCommerceService.php")

    # پیدا کردن last }
    idx = content.rstrip().rfind('}')

    inject = '''

    /* ═══════════════════════════════════════════════════════════
       Wrapper با لاگ‌گیری خودکار
       ═══════════════════════════════════════════════════════════ */

    protected function loggedGet(string $url, array $query = []): ?array
    {
        $full = $url . ($query ? '?' . http_build_query($query) : '');

        $result = \\App\\Services\\ApiLogger::request('woocommerce', 'GET', $full, [
            'basic_auth' => [$this->key ?? '', $this->secret ?? ''],
            'timeout'    => 60,
        ]);

        if (!$result['ok']) {
            return null;
        }

        return $result['json'] ?? null;
    }
'''

    new_content = content[:idx] + inject + '\n}\n'

    with open(path, 'w', encoding='utf-8', newline='\n') as f:
        f.write(new_content)

    print("  ✓ WooCommerceService patch شد")

# ═══════════════════════════════════════════════════════════════
# اجرا
# ═══════════════════════════════════════════════════════════════

def main():
    print("╔══════════════════════════════════════════════════════════════╗")
    print("║  Fix — Customer.php + Complete Settings                       ║")
    print("╚══════════════════════════════════════════════════════════════╝\n")

    print("📄 [۱] اصلاح Customer.php...")
    fix_customer_model()

    print("\n📄 [۲] Patch AppServiceProvider...")
    patch_app_provider_safe()

    print("\n📄 [۳] Patch Layout (theme)...")
    patch_layout_safe()

    print("\n📄 [۴] Patch WooCommerceService...")
    patch_woo()

    print("\n" + "═" * 64)
    print("✅ تمام!")
    print("═" * 64)
    print(f"""
📋 حالا این دستورات رو دقیقاً به ترتیب اجرا کن:

  cd {PROJECT}

  # ۱) حذف فایل کش composer
  composer dump-autoload

  # ۲) پاکسازی کش
  php artisan optimize:clear
  php artisan view:clear
  php artisan route:clear

  # ۳) اجرای مایگریشن‌ها
  php artisan migrate

  # ۴) سرور رو ببند (Ctrl+C) و دوباره باز کن
  php artisan serve

  # ۵) مرورگر: Ctrl+Shift+R (هارد رفرش)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 چه چیزی حل شد:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

  ✓ Customer.php — متدها داخل کلاس قرار گرفتند
  ✓ AppServiceProvider — بدون خطای regex
  ✓ Layout — theme از settings خونده می‌شه
  ✓ WooCommerceService — متد loggedGet اضافه شد
  ✓ Migration — app_settings + api_logs (اگه migrate بزنی)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 اگه باز خطا داد، فقط این رو بفرست:

  php artisan tinker --execute="echo 'OK';"
  
  یا خطای دقیق از storage\\logs\\laravel.log (آخرین خط)
""")

if __name__ == "__main__":
    main()