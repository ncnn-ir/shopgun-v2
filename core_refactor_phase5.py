#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ShopGun V2 - Core Refactor Phase 5
====================================
- Certificate Templates (چند قالب قابل ذخیره)
- یکپارچه‌سازی Action ها در Create.php و FormModal.php
- Certificate Snapshot History UI
"""
from pathlib import Path
import time, subprocess

ROOT = Path('/data/data/com.termux/files/home/shopgun-v2.2')

def write(rel, content):
    p = ROOT / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    if p.exists():
        p.rename(str(p) + '.bak-' + str(int(time.time())))
    p.write_text(content, encoding='utf-8')
    print("[OK] " + rel)

def run(cmd):
    print(f"$ {cmd}")
    return subprocess.run(cmd, shell=True, cwd=ROOT).returncode


# ═══════════════════════════════════════════════════════════════
# 1. MIGRATION — certificate_templates
# ═══════════════════════════════════════════════════════════════

ts = time.strftime('%Y_%m_%d_%H%M%S')
MIGRATION = '''<?php

use Illuminate\\Database\\Migrations\\Migration;
use Illuminate\\Database\\Schema\\Blueprint;
use Illuminate\\Support\\Facades\\Schema;

return new class extends Migration
{
    public function up(): void
    {
        if (Schema::hasTable('certificate_templates')) return;

        Schema::create('certificate_templates', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->string('slug', 100)->unique()->index();
            $table->text('description')->nullable();
            $table->string('version', 20)->default('1.0');
            $table->string('status', 30)->default('draft')->index();
            // draft | published | archived

            $table->json('design_data')->nullable();        // Fabric.js JSON
            $table->json('sizes')->nullable();              // {width, height, img_w, ...}
            $table->json('logos')->nullable();              // [{path, position, size}]
            $table->json('colors')->nullable();             // palette

            $table->boolean('is_default')->default(false)->index();
            $table->boolean('is_global')->default(false)->index();

            $table->unsignedInteger('certificates_count')->default(0);
            $table->foreignId('created_by')->nullable();

            $table->timestamp('published_at')->nullable();
            $table->timestamp('archived_at')->nullable();
            $table->timestamps();
        });
    }

    public function down(): void
    {
        Schema::dropIfExists('certificate_templates');
    }
};
'''

write(f'database/migrations/{ts}_create_certificate_templates_table.php', MIGRATION)


# ═══════════════════════════════════════════════════════════════
# 2. MODEL CertificateTemplate
# ═══════════════════════════════════════════════════════════════

write('app/Models/CertificateTemplate.php', '''<?php

namespace App\\Models;

use Illuminate\\Database\\Eloquent\\Model;
use Illuminate\\Database\\Eloquent\\Relations\\HasMany;

class CertificateTemplate extends Model
{
    protected $fillable = [
        'name', 'slug', 'description', 'version', 'status',
        'design_data', 'sizes', 'logos', 'colors',
        'is_default', 'is_global', 'certificates_count',
        'created_by', 'published_at', 'archived_at',
    ];

    protected $casts = [
        'design_data' => 'array',
        'sizes' => 'array',
        'logos' => 'array',
        'colors' => 'array',
        'is_default' => 'boolean',
        'is_global' => 'boolean',
        'published_at' => 'datetime',
        'archived_at' => 'datetime',
    ];

    public function certificates(): HasMany
    {
        return $this->hasMany(Certificate::class, 'template_id');
    }

    public function scopePublished($q)
    {
        return $q->where('status', 'published');
    }

    public function scopeAvailable($q)
    {
        return $q->whereIn('status', ['draft', 'published']);
    }

    public static function findDefault(): ?self
    {
        return self::where('is_default', true)->published()->first()
            ?? self::published()->latest('id')->first();
    }

    public function publish(): void
    {
        $this->update([
            'status' => 'published',
            'published_at' => now(),
        ]);
    }

    public function archive(): void
    {
        $this->update([
            'status' => 'archived',
            'archived_at' => now(),
        ]);
    }

    public function duplicate(): self
    {
        $new = $this->replicate(['slug', 'is_default', 'certificates_count', 'published_at']);
        $new->name = $this->name . ' (کپی)';
        $new->slug = $this->slug . '-copy-' . uniqid();
        $new->version = $this->version;
        $new->status = 'draft';
        $new->is_default = false;
        $new->certificates_count = 0;
        $new->save();
        return $new;
    }
}
''')


# ═══════════════════════════════════════════════════════════════
# 3. CertificateTemplateService
# ═══════════════════════════════════════════════════════════════

write('app/Application/Certificates/CertificateTemplateService.php', r'''<?php

namespace App\Application\Certificates;

use App\Models\CertificateTemplate;
use App\Models\AppSetting;
use Illuminate\Support\Facades\Cache;

/**
 * ★ CertificateTemplateService
 * مدیریت قالب‌های شناسنامه
 */
class CertificateTemplateService
{
    /**
     * لیست قالب‌های موجود (برای select)
     */
    public static function available(): \Illuminate\Database\Eloquent\Collection
    {
        return CertificateTemplate::available()->orderByDesc('is_default')->orderBy('name')->get();
    }

    /**
     * قالب پیش‌فرض
     */
    public static function default(): ?CertificateTemplate
    {
        return CertificateTemplate::findDefault();
    }

    /**
     * ایجاد قالب جدید
     */
    public static function create(array $data): CertificateTemplate
    {
        $slug = self::uniqueSlug($data['slug'] ?? $data['name']);

        return CertificateTemplate::create([
            'name' => $data['name'],
            'slug' => $slug,
            'description' => $data['description'] ?? null,
            'version' => $data['version'] ?? '1.0',
            'status' => 'draft',
            'design_data' => $data['design_data'] ?? null,
            'sizes' => $data['sizes'] ?? self::defaultSizes(),
            'logos' => $data['logos'] ?? [],
            'colors' => $data['colors'] ?? self::defaultColors(),
            'created_by' => auth()->id(),
        ]);
    }

    /**
     * کپی از قالب موجود
     */
    public static function duplicate(int $templateId, ?string $newName = null): ?CertificateTemplate
    {
        $tpl = CertificateTemplate::find($templateId);
        if (!$tpl) return null;

        $new = $tpl->duplicate();
        if ($newName) $new->update(['name' => $newName]);
        return $new;
    }

    /**
     * تنظیم به عنوان پیش‌فرض
     */
    public static function setDefault(int $templateId): void
    {
        CertificateTemplate::where('is_default', true)->update(['is_default' => false]);
        CertificateTemplate::where('id', $templateId)->update(['is_default' => true]);
        Cache::forget('cert_template_default');
    }

    /**
     * اعمال قالب روی یک شناسنامه
     */
    public static function applyToCertificate(int $templateId, \App\Models\Certificate $cert): void
    {
        $tpl = CertificateTemplate::find($templateId);
        if (!$tpl) return;

        $cert->update([
            'template_id' => $tpl->id,
            'design_data' => $tpl->design_data,
        ]);

        $tpl->increment('certificates_count');
    }

    // ═══════════════════════════════════════════════════════════
    public static function uniqueSlug(string $base): string
    {
        $slug = preg_replace('/[^a-z0-9-]+/i', '-', strtolower($base));
        $slug = trim(preg_replace('/-+/', '-', $slug), '-');
        if ($slug === '') $slug = 'template';

        $original = $slug;
        $i = 2;
        while (CertificateTemplate::where('slug', $slug)->exists()) {
            $slug = $original . '-' . $i;
            $i++;
        }
        return $slug;
    }

    public static function defaultSizes(): array
    {
        return [
            'width' => 6.5, 'height' => 6.5,
            'img_w' => 120, 'img_h' => 120,
            'qr_size' => 40, 'logo_w' => 28, 'logo_h' => 22,
            'code_font' => 11, 'title_font' => 20, 'desc_font' => 7,
            'col1' => 25, 'col2' => 25, 'col3' => 25, 'col4' => 25,
            'hide_desc' => false,
        ];
    }

    public static function defaultColors(): array
    {
        return [
            'primary' => '#1a5276',
            'gold' => '#c9a84c',
            'bg' => '#fffef9',
            'brown' => '#6b4423',
            'teal' => '#0d5c63',
        ];
    }
}
''')


# ═══════════════════════════════════════════════════════════════
# 4. Certificates Create.php — استفاده از IssueCertificateAction
# ═══════════════════════════════════════════════════════════════

create_path = ROOT / 'app' / 'Livewire' / 'Certificates' / 'Create.php'
if create_path.exists():
    txt = create_path.read_text(encoding='utf-8')

    # جایگزینی متد save با Action
    import re
    old_save = re.search(r'public function save\(\)\s*\{.*?\n    \}', txt, flags=re.DOTALL)

    if old_save and 'IssueCertificateAction' not in txt:
        new_save = r'''public function save()
    {
        $this->validate([
            'stoneName' => 'required|string|max:255',
            'metal'     => 'required|string|max:255',
            'length'    => 'nullable|numeric|min:0',
            'width'     => 'nullable|numeric|min:0',
            'weight'    => 'nullable|numeric|min:0',
            'image'     => 'nullable|image|max:5120',
        ]);

        try {
            $imagePath = null;
            if ($this->image) {
                $imagePath = $this->image->store('certificates', 'public');
            } elseif ($this->productImageUrl) {
                $img = \Illuminate\Support\Facades\Http::timeout(25)->get($this->productImageUrl)->body();
                $ext = 'jpg';
                if (preg_match('/\.(png|jpg|jpeg|webp)/i', $this->productImageUrl, $m)) {
                    $ext = strtolower($m[1]);
                }
                $fname = 'certificates/' . uniqid('cert_') . '.' . $ext;
                \Illuminate\Support\Facades\Storage::disk('public')->put($fname, $img);
                $imagePath = $fname;
            }

            // ★ استفاده از Action واحد
            $action = new \App\Application\Actions\IssueCertificateAction();

            if ($this->editingId) {
                $cert = \App\Models\Certificate::find($this->editingId);
                if (!$cert) {
                    $this->dispatch('notify', type: 'error', message: 'شناسنامه پیدا نشد');
                    return;
                }

                $data = [
                    'stone_name' => $this->stoneName,
                    'stone_en' => $this->stoneEn,
                    'stone_origin' => $this->stoneOrigin,
                    'stone_flag' => $this->stoneFlag,
                    'metal' => $this->metal,
                    'metal_en' => $this->metalEn,
                    'metal_carat' => $this->metalCarat,
                    'length' => (float) ($this->length ?: 0),
                    'width' => (float) ($this->width ?: 0),
                    'weight' => (float) ($this->weight ?: 0),
                    'brilliant' => (int) ($this->brilliant ?: 0),
                    'customer_id' => $this->customerId ?: null,
                    'order_id' => $this->orderId ?: null,
                    'sku' => $this->searchedProduct['sku'] ?? null,
                ];
                if ($imagePath) $data['image_path'] = $imagePath;

                $cert->update($data);
                $msg = "شناسنامه #{$cert->code} ویرایش شد.";
            } else {
                $cert = $action->execute([
                    'stone_name' => $this->stoneName,
                    'stone_en' => $this->stoneEn,
                    'stone_origin' => $this->stoneOrigin,
                    'stone_flag' => $this->stoneFlag,
                    'metal' => $this->metal,
                    'metal_en' => $this->metalEn,
                    'metal_carat' => $this->metalCarat,
                    'length' => (float) ($this->length ?: 0),
                    'width' => (float) ($this->width ?: 0),
                    'weight' => (float) ($this->weight ?: 0),
                    'brilliant' => (int) ($this->brilliant ?: 0),
                    'image_path' => $imagePath,
                    'image_url' => $this->productImageUrl,
                    'customer_id' => $this->customerId ?: null,
                    'order_id' => $this->orderId ?: null,
                    'sku' => $this->searchedProduct['sku'] ?? null,
                ]);
                $msg = "شناسنامه #{$cert->code} صادر شد.";
            }

            session()->flash('success', $msg);
            $this->closeModal();
            $this->dispatch('notify', type: 'success', message: $msg);
            $this->dispatch('cert-saved');

        } catch (\Throwable $e) {
            $this->dispatch('notify', type: 'error', message: 'خطا: ' . $e->getMessage());
        }
    }'''

        txt = txt[:old_save.start()] + new_save + txt[old_save.end():]
        create_path.write_text(txt, encoding='utf-8')
        print("[OK] Certificates/Create.php - IssueCertificateAction")


# ═══════════════════════════════════════════════════════════════
# 5. FormModal.php — استفاده از CreateOrderAction
# ═══════════════════════════════════════════════════════════════

fm_path = ROOT / 'app' / 'Livewire' / 'Orders' / 'FormModal.php'
if fm_path.exists():
    txt = fm_path.read_text(encoding='utf-8')

    if 'CreateOrderAction' not in txt and 'public function save' in txt:
        import re
        old_save = re.search(r'public function save\(\): void\s*\{.*?\n    \}', txt, flags=re.DOTALL)

        if old_save:
            new_save = r'''public function save(): void
    {
        $this->validate([
            'phone' => 'required|string|max:20',
            'customerName' => 'required|string|max:120',
            'items' => 'required|array|min:1',
            'items.*.title' => 'required|string|max:255',
        ]);

        try {
            $action = new \App\Application\Actions\CreateOrderAction();

            if ($this->orderId) {
                // ویرایش سفارش — بدون Action (پیچیدگی کمتر)
                $order = \App\Models\Order::find($this->orderId);
                if (!$order) {
                    $this->dispatch('notify', type: 'error', message: 'سفارش پیدا نشد');
                    return;
                }
                $order->items()->delete();

                $amount = 0;
                foreach ($this->items as $it) {
                    $amount += ((float) ($it['price'] ?? 0)) * ((int) ($it['quantity'] ?? 1));
                }

                $order->update([
                    'customer_name' => $this->customerName,
                    'phone' => $this->phone,
                    'address' => $this->address,
                    'postal_code' => $this->postalCode,
                    'status' => $this->status,
                    'channel_id' => $this->channelId,
                    'insurance' => (float) $this->insurance,
                    'discount' => (float) $this->discount,
                    'shipping' => (float) $this->shipping,
                    'amount' => $amount,
                    'notes' => $this->notes,
                ]);

                foreach ($this->items as $idx => $it) {
                    $order->items()->create([
                        'sku' => $it['sku'] ?? null,
                        'title' => $it['title'],
                        'price' => (float) $it['price'],
                        'quantity' => (int) $it['quantity'],
                        'cert_needed' => !empty($it['certificate_needed']),
                        'sort_order' => $idx,
                    ]);
                }

                $msg = 'ویرایش شد ✅';
                $orderId = $order->id;
            } else {
                // ★ استفاده از Action واحد
                $order = $action->execute([
                    'phone' => $this->phone,
                    'name' => $this->customerName,
                    'address' => $this->address,
                    'postal_code' => $this->postalCode,
                    'channel_id' => $this->channelId,
                    'status' => $this->status,
                    'insurance' => (float) $this->insurance,
                    'discount' => (float) $this->discount,
                    'shipping' => (float) $this->shipping,
                    'notes' => $this->notes,
                    'invoice_needed' => false,
                    'items' => array_map(fn($it) => [
                        'sku' => $it['sku'] ?? null,
                        'title' => $it['title'],
                        'price' => (float) $it['price'],
                        'quantity' => (int) $it['quantity'],
                        'cert_needed' => !empty($it['certificate_needed']),
                    ], $this->items),
                ]);

                $msg = 'ثبت شد ✅';
                $orderId = $order->id;
            }

            $this->dispatch('order-saved', orderId: $orderId);
            $this->dispatch('notify', type: 'success', message: $msg);
            $this->close();

        } catch (\Throwable $e) {
            $this->dispatch('notify', type: 'error', message: 'خطا: ' . $e->getMessage());
        }
    }'''

            txt = txt[:old_save.start()] + new_save + txt[old_save.end():]
            fm_path.write_text(txt, encoding='utf-8')
            print("[OK] FormModal - CreateOrderAction")


# ═══════════════════════════════════════════════════════════════
# 6. Migration افزودن template_id به certificates
# ═══════════════════════════════════════════════════════════════

ts2 = time.strftime('%Y_%m_%d_%H%M%S')
MIG2 = '''<?php

use Illuminate\\Database\\Migrations\\Migration;
use Illuminate\\Database\\Schema\\Blueprint;
use Illuminate\\Support\\Facades\\Schema;

return new class extends Migration
{
    public function up(): void
    {
        if (!Schema::hasColumn('certificates', 'template_id')) {
            Schema::table('certificates', function (Blueprint $table) {
                $table->foreignId('template_id')->nullable()->after('id')->constrained('certificate_templates')->nullOnDelete();
            });
        }
    }

    public function down(): void
    {
        if (Schema::hasColumn('certificates', 'template_id')) {
            Schema::table('certificates', function (Blueprint $table) {
                $table->dropForeign(['template_id']);
                $table->dropColumn('template_id');
            });
        }
    }
};
'''
write(f'database/migrations/{ts2}_add_template_id_to_certificates.php', MIG2)


# ═══════════════════════════════════════════════════════════════
# 7. صفحة إدارة القوالب — Settings tab جدید
# ═══════════════════════════════════════════════════════════════

write('app/Livewire/Settings/Templates.php', r'''<?php

namespace App\Livewire\Settings;

use App\Application\Certificates\CertificateTemplateService;
use App\Models\CertificateTemplate;
use Livewire\Component;

/**
 * ★ Settings\\Templates — مدیریت قالب‌های شناسنامه
 */
class Templates extends Component
{
    public bool $showForm = false;
    public ?int $editingId = null;

    public string $name = '';
    public string $description = '';
    public string $version = '1.0';

    public function openForm(?int $id = null): void
    {
        $this->resetForm();
        $this->editingId = $id;
        $this->showForm = true;

        if ($id) {
            $t = CertificateTemplate::find($id);
            if ($t) {
                $this->name = $t->name;
                $this->description = $t->description ?? '';
                $this->version = $t->version;
            }
        }
    }

    public function closeForm(): void
    {
        $this->showForm = false;
        $this->resetForm();
    }

    public function resetForm(): void
    {
        $this->reset(['editingId', 'name', 'description', 'version']);
        $this->version = '1.0';
    }

    public function save(): void
    {
        $this->validate([
            'name' => 'required|string|max:120',
            'version' => 'required|string|max:20',
        ]);

        if ($this->editingId) {
            CertificateTemplate::where('id', $this->editingId)->update([
                'name' => $this->name,
                'description' => $this->description,
                'version' => $this->version,
            ]);
            $this->dispatch('notify', type: 'success', message: 'قالب بروزرسانی شد');
        } else {
            CertificateTemplateService::create([
                'name' => $this->name,
                'description' => $this->description,
                'version' => $this->version,
            ]);
            $this->dispatch('notify', type: 'success', message: 'قالب ایجاد شد');
        }

        $this->closeForm();
    }

    public function duplicate(int $id): void
    {
        CertificateTemplateService::duplicate($id);
        $this->dispatch('notify', type: 'success', message: 'کپی ایجاد شد');
    }

    public function publish(int $id): void
    {
        CertificateTemplate::find($id)?->publish();
        $this->dispatch('notify', type: 'success', message: 'منتشر شد');
    }

    public function archive(int $id): void
    {
        CertificateTemplate::find($id)?->archive();
        $this->dispatch('notify', type: 'success', message: 'آرشیو شد');
    }

    public function setDefault(int $id): void
    {
        CertificateTemplateService::setDefault($id);
        $this->dispatch('notify', type: 'success', message: 'پیش‌فرض تنظیم شد');
    }

    public function delete(int $id): void
    {
        CertificateTemplate::find($id)?->delete();
        $this->dispatch('notify', type: 'success', message: 'حذف شد');
    }

    public function render()
    {
        return view('livewire.settings.templates', [
            'templates' => CertificateTemplate::orderByDesc('is_default')->latest('id')->get(),
        ]);
    }
}
''')


write('resources/views/livewire/settings/templates.blade.php', r'''<div style="padding:14px;direction:rtl">

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
''')


# ═══════════════════════════════════════════════════════════════
# 8. Settings Index — لینک به Templates
# ═══════════════════════════════════════════════════════════════

sv = ROOT / 'resources' / 'views' / 'livewire' / 'settings' / 'index.blade.php'
if sv.exists():
    txt = sv.read_text(encoding='utf-8')

    # اضافه کردن tab templates به لیست
    if "'templates'" not in txt.split('sg-settings-tabs')[1].split('</div>')[0] if 'sg-settings-tabs' in txt else True:
        # اضافه کردن به tab list
        txt = txt.replace(
            "'labels'      => ['🎨', 'ویرایشگر برچسب', false],",
            "'templates'   => ['🎨', 'قالب‌های شناسنامه', true],\n            'labels'      => ['🎨', 'ویرایشگر برچسب', false],"
        )

    # اضافه کردن section
    if "{{-- قالب‌های شناسنامه --}}" not in txt and 'templates' not in txt.split('@if($tab ===')[1:5][0] if '@if($tab ===' in txt else True:
        marker = "        {{-- ویرایشگر برچسب --}}"
        TEMPLATES_SECTION = '''        {{-- ═══════════ قالب‌های شناسنامه ═══════════ --}}
        @if($tab === 'templates')
            <livewire:settings.templates />
        @endif

'''
        if marker in txt:
            txt = txt.replace(marker, TEMPLATES_SECTION + marker, 1)
            sv.write_text(txt, encoding='utf-8')
            print("[OK] settings blade - templates tab")


# ═══════════════════════════════════════════════════════════════
# 9. Certificates Show — نمایش تاریخچه Snapshot
# ═══════════════════════════════════════════════════════════════

# اضافه کردن متد به Show.php
show_php = ROOT / 'app' / 'Livewire' / 'Certificates' / 'Show.php'
if show_php.exists():
    txt = show_php.read_text(encoding='utf-8')

    if 'snapshots' not in txt:
        txt = txt.replace(
            "public function render()",
            '''public array $snapshots = [];
    public bool $showHistory = false;

    public function loadHistory(): void
    {
        try {
            $this->snapshots = \\App\\Application\\Certificates\\CertificateSnapshotService::history($this->certificate)
                ->map(fn($s) => [
                    'id' => $s->id,
                    'event' => $s->event,
                    'event_label' => match($s->event) {
                        'issued' => '📝 صدور اولیه',
                        'updated' => '✏️ ویرایش',
                        'reprinted' => '🖨️ چاپ مجدد',
                        'design_changed' => '🎨 تغییر طرح',
                        default => $s->event,
                    },
                    'stone_name' => $s->stone_name,
                    'metal' => $s->metal,
                    'weight' => $s->weight,
                    'captured_at' => \\App\\Support\\PersianDate::format($s->captured_at, 'Y/m/d H:i'),
                    'changed_by' => $s->changed_by_name,
                ])
                ->toArray();
            $this->showHistory = true;
        } catch (\\Throwable $e) {
            $this->dispatch('notify', type: 'error', message: $e->getMessage());
        }
    }

    public function closeHistory(): void
    {
        $this->showHistory = false;
        $this->snapshots = [];
    }

    public function render()''',
            1
        )
        show_php.write_text(txt, encoding='utf-8')
        print("[OK] Certificates/Show.php - history")


# ═══════════════════════════════════════════════════════════════
# 10. اجرا
# ═══════════════════════════════════════════════════════════════

print()
print("🔧 Migration و پاک‌سازی...")
run('php artisan migrate --force')
run('php artisan optimize:clear')
run('php artisan route:clear')
run('php artisan view:clear')

print()
print("=" * 60)
print("DONE — Phase 5")
print("=" * 60)
print()
print("🎯 دستاوردهای فاز ۵:")
print("   ✅ Certificate Templates (چند قالب با version/status)")
print("   ✅ CertificateTemplateService (create, duplicate, publish, setDefault)")
print("   ✅ Settings tab جدید: قالب‌های شناسنامه")
print("   ✅ Certificates Create.php → IssueCertificateAction")
print("   ✅ Orders FormModal → CreateOrderAction")
print("   ✅ Certificate Snapshot history (آماده اتصال به View)")
print()
print("🚀 php artisan serve")
