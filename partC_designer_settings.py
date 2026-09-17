from pathlib import Path
import textwrap

PROJECT = Path.home() / "projects" / "shopgun-v2.1"
if not PROJECT.exists():
    raise SystemExit("❌ پروژه پیدا نشد")

def write_file(rel, content):
    path = PROJECT / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    existed = path.exists()
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    print(f"{'🔁' if existed else '✅'} {rel}")

print("═" * 60)
print("🎨 Part C — Designer + تنظیمات سنگ/فلز")
print("═" * 60)
print()

# =========================================================
# ۱. Migrations — Stones, Metals, Certificates Settings
# =========================================================

write_file("database/migrations/2026_09_16_030001_create_stones_table.php", r"""
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('stones', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->string('en')->nullable();
            $table->string('origin')->nullable();
            $table->string('origin_en')->nullable();
            $table->string('flag', 4)->nullable();
            $table->string('balloon')->nullable();
            $table->string('icon')->default('💎');
            $table->string('png_path')->nullable();
            $table->boolean('is_active')->default(true);
            $table->integer('sort_order')->default(0);
            $table->timestamps();
        });
    }

    public function down(): void { Schema::dropIfExists('stones'); }
};
""")

write_file("database/migrations/2026_09_16_030002_create_metals_table.php", r"""
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('metals', function (Blueprint $table) {
            $table->id();
            $table->string('name');
            $table->string('en')->nullable();
            $table->string('carat')->nullable();
            $table->string('icon')->default('⚙️');
            $table->boolean('is_active')->default(true);
            $table->integer('sort_order')->default(0);
            $table->timestamps();
        });
    }

    public function down(): void { Schema::dropIfExists('metals'); }
};
""")

write_file("database/migrations/2026_09_16_030003_create_cert_settings_table.php", r"""
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('cert_settings', function (Blueprint $table) {
            $table->id();
            $table->string('key')->unique();
            $table->text('value')->nullable();
            $table->string('group')->default('general');
            $table->timestamps();
        });
    }

    public function down(): void { Schema::dropIfExists('cert_settings'); }
};
""")

# =========================================================
# ۲. Models
# =========================================================

write_file("app/Models/Stone.php", r"""
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Stone extends Model
{
    protected $fillable = [
        'name', 'en', 'origin', 'origin_en', 'flag', 'balloon',
        'icon', 'png_path', 'is_active', 'sort_order',
    ];

    protected $casts = [
        'is_active' => 'boolean',
        'sort_order' => 'integer',
    ];

    public function getPngUrlAttribute(): ?string
    {
        return $this->png_path ? asset('storage/' . $this->png_path) : null;
    }
}
""")

write_file("app/Models/Metal.php", r"""
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class Metal extends Model
{
    protected $fillable = ['name', 'en', 'carat', 'icon', 'is_active', 'sort_order'];

    protected $casts = [
        'is_active' => 'boolean',
        'sort_order' => 'integer',
    ];
}
""")

write_file("app/Models/CertSetting.php", r"""
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class CertSetting extends Model
{
    protected $fillable = ['key', 'value', 'group'];

    public static function get(string $key, $default = null)
    {
        $s = self::where('key', $key)->first();
        if (! $s) return $default;

        $v = $s->value;
        if (is_string($v)) {
            if (str_starts_with($v, '{') || str_starts_with($v, '[')) {
                return json_decode($v, true) ?: $default;
            }
            if (is_numeric($v)) return $v + 0;
            if ($v === 'true')  return true;
            if ($v === 'false') return false;
        }

        return $v ?? $default;
    }

    public static function set(string $key, $value, string $group = 'general'): void
    {
        if (is_array($value) || is_object($value)) {
            $value = json_encode($value, JSON_UNESCAPED_UNICODE);
        } elseif (is_bool($value)) {
            $value = $value ? 'true' : 'false';
        }

        self::updateOrCreate(
            ['key' => $key],
            ['value' => (string) $value, 'group' => $group]
        );
    }
}
""")

# =========================================================
# ۳. Seeder — سنگ‌ها و فلزات پیش‌فرض
# =========================================================

write_file("database/seeders/StoneMetalSeeder.php", r"""
<?php

namespace Database\Seeders;

use App\Models\Metal;
use App\Models\Stone;
use Illuminate\Database\Seeder;

class StoneMetalSeeder extends Seeder
{
    public function run(): void
    {
        $stones = [
            ['name'=>'فیروزه عجمی',   'en'=>'Turquoise Ajami',   'origin'=>'نیشابور',  'flag'=>'ir', 'balloon'=>'عجمی',      'icon'=>'💠'],
            ['name'=>'فیروزه شجری',   'en'=>'Turquoise Shajari', 'origin'=>'نیشابور',  'flag'=>'ir', 'balloon'=>'شجری',      'icon'=>'💠'],
            ['name'=>'عقیق یمانی',    'en'=>'Yemeni Agate',      'origin'=>'یمن',      'flag'=>'ye', 'balloon'=>'یمانی',     'icon'=>'🔴'],
            ['name'=>'عقیق سلیمانی',  'en'=>'Solomoni Agate',    'origin'=>'یمن',      'flag'=>'ye', 'balloon'=>'سلیمانی',   'icon'=>'❤️'],
            ['name'=>'عقیق شجر',      'en'=>'Dendritic Agate',   'origin'=>'یمن',      'flag'=>'ye', 'balloon'=>'شجری',      'icon'=>'🌿'],
            ['name'=>'در نجف',        'en'=>'Najaf Pearl',       'origin'=>'عراق',     'flag'=>'iq', 'balloon'=>'در نجف',    'icon'=>'⚪'],
            ['name'=>'الماس',         'en'=>'Diamond',           'origin'=>'آفریقا',   'flag'=>'za', 'balloon'=>'الماس',     'icon'=>'💎'],
            ['name'=>'یاقوت سرخ',     'en'=>'Ruby',              'origin'=>'میانمار',  'flag'=>'mm', 'balloon'=>'یاقوت',     'icon'=>'❤️'],
            ['name'=>'یاقوت کبود',    'en'=>'Blue Sapphire',     'origin'=>'سری‌لانکا','flag'=>'lk', 'balloon'=>'کبود',      'icon'=>'🔵'],
            ['name'=>'زمرد',          'en'=>'Emerald',           'origin'=>'کلمبیا',   'flag'=>'co', 'balloon'=>'زمرد',      'icon'=>'🟢'],
            ['name'=>'توپاز',         'en'=>'Topaz',             'origin'=>'برزیل',    'flag'=>'br', 'balloon'=>'توپاز',     'icon'=>'💛'],
            ['name'=>'آمیتیست',       'en'=>'Amethyst',          'origin'=>'برزیل',    'flag'=>'br', 'balloon'=>'بنفش',      'icon'=>'🟣'],
            ['name'=>'چشم ببر',       'en'=>'Tiger Eye',         'origin'=>'آفریقا',   'flag'=>'za', 'balloon'=>'چشم ببر',   'icon'=>'🐯'],
            ['name'=>'لاجورد',        'en'=>'Lapis Lazuli',      'origin'=>'افغانستان','flag'=>'af', 'balloon'=>'لاجورد',    'icon'=>'💙'],
            ['name'=>'حدید',          'en'=>'Hematite',          'origin'=>'ایران',    'flag'=>'ir', 'balloon'=>'حدید',      'icon'=>'⚫'],
            ['name'=>'مرجان',         'en'=>'Coral',             'origin'=>'مدیترانه', 'flag'=>'it', 'balloon'=>'مرجان',     'icon'=>'🟠'],
        ];

        foreach ($stones as $i => $s) {
            Stone::updateOrCreate(
                ['en' => $s['en']],
                array_merge($s, ['is_active' => true, 'sort_order' => $i])
            );
        }

        $metals = [
            ['name'=>'نقره 925',   'en'=>'Silver 925',      'carat'=>'925', 'icon'=>'🥈'],
            ['name'=>'نقره 999',   'en'=>'Fine Silver',     'carat'=>'999', 'icon'=>'⚪'],
            ['name'=>'طلا 18K',    'en'=>'Gold 18K',        'carat'=>'750', 'icon'=>'✨'],
            ['name'=>'طلا 21K',    'en'=>'Gold 21K',        'carat'=>'875', 'icon'=>'🌟'],
            ['name'=>'طلا 22K',    'en'=>'Gold 22K',        'carat'=>'916', 'icon'=>'⭐'],
            ['name'=>'طلا 24K',    'en'=>'Gold 24K',        'carat'=>'999', 'icon'=>'🌟'],
            ['name'=>'پلاتین 950', 'en'=>'Platinum 950',    'carat'=>'950', 'icon'=>'⚙️'],
            ['name'=>'استیل',      'en'=>'Stainless Steel', 'carat'=>'-',   'icon'=>'🔩'],
        ];

        foreach ($metals as $i => $m) {
            Metal::updateOrCreate(
                ['name' => $m['name']],
                array_merge($m, ['is_active' => true, 'sort_order' => $i])
            );
        }

        // تنظیمات پیش‌فرض شناسنامه
        $defaults = [
            'cert.width'      => '6.5',
            'cert.height'     => '6.5',
            'cert.img_w'      => '120',
            'cert.img_h'      => '120',
            'cert.qr_size'    => '40',
            'cert.logo_w'     => '28',
            'cert.logo_h'     => '22',
            'cert.code_font'  => '11',
            'cert.title_font' => '20',
            'cert.desc_font'  => '7',
            'cert.table_label_font' => '8',
            'cert.table_value_font' => '8',
            'cert.hide_desc'  => 'false',
            'cert.bg_image'   => '',
            'cert.desc_image' => '',
            'cert.logo_image' => '',
            'cert.design_data' => '{}',
        ];

        foreach ($defaults as $k => $v) {
            CertSetting::updateOrCreate(
                ['key' => $k],
                ['value' => $v, 'group' => 'certificate']
            );
        }

        $this->command->info('✅ ' . count($stones) . ' سنگ و ' . count($metals) . ' فلز اضافه شد');
    }
}
""")

write_file("database/seeders/DatabaseSeeder.php", r"""
<?php

namespace Database\Seeders;

use Illuminate\Database\Seeder;

class DatabaseSeeder extends Seeder
{
    public function run(): void
    {
        $this->call([
            RoleAndUserSeeder::class,
            ChannelSeeder::class,
            StoneMetalSeeder::class,
            SampleDataSeeder::class,
        ]);
    }
}
""")

# =========================================================
# ۴. Livewire: Settings/Stones
# =========================================================

write_file("app/Livewire/Settings/Stones.php", r"""
<?php

namespace App\Livewire\Settings;

use App\Models\Stone;
use Livewire\Component;
use Livewire\WithFileUploads;
use Livewire\WithPagination;

class Stones extends Component
{
    use WithPagination, WithFileUploads;

    public string $search = '';

    // فرم افزودن/ویرایش
    public bool $showForm = false;
    public ?int $editingId = null;

    public string $name = '';
    public string $en = '';
    public string $origin = '';
    public string $originEn = '';
    public string $flag = 'ir';
    public string $balloon = '';
    public string $icon = '💎';
    public $png = null;

    public array $countries = [
        'ir'=>'🇮🇷 ایران','af'=>'🇦🇫 افغانستان','iq'=>'🇮🇶 عراق','tr'=>'🇹🇷 ترکیه',
        'ye'=>'🇾🇪 یمن','sa'=>'🇸🇦 عربستان','ae'=>'🇦🇪 امارات','pk'=>'🇵🇰 پاکستان',
        'in'=>'🇮🇳 هند','cn'=>'🇨🇳 چین','us'=>'🇺🇸 آمریکا','gb'=>'🇬🇧 انگلیس',
        'de'=>'🇩🇪 آلمان','fr'=>'🇫🇷 فرانسه','it'=>'🇮🇹 ایتالیا','ru'=>'🇷🇺 روسیه',
        'jp'=>'🇯🇵 ژاپن','kr'=>'🇰🇷 کره','th'=>'🇹🇭 تایلند','my'=>'🇲🇾 مالزی',
        'au'=>'🇦🇺 استرالیا','ca'=>'🇨🇦 کانادا','br'=>'🇧🇷 برزیل','za'=>'🇿🇦 آفریقای جنوبی',
        'mm'=>'🇲🇲 میانمار','lk'=>'🇱🇰 سری‌لانکا','co'=>'🇨🇴 کلمبیا','zm'=>'🇿🇲 زامبیا',
        'eg'=>'🇪🇬 مصر','ke'=>'🇰🇪 کنیا','mg'=>'🇲🇬 ماداگاسکار','kh'=>'🇰🇭 کامبوج',
    ];

    public function updatingSearch(): void { $this->resetPage(); }

    public function openForm(?int $id = null): void
    {
        $this->resetForm();
        $this->editingId = $id;
        $this->showForm = true;

        if ($id) {
            $s = Stone::find($id);
            if ($s) {
                $this->name     = $s->name;
                $this->en       = $s->en ?? '';
                $this->origin   = $s->origin ?? '';
                $this->originEn = $s->origin_en ?? '';
                $this->flag     = $s->flag ?? 'ir';
                $this->balloon  = $s->balloon ?? '';
                $this->icon     = $s->icon ?? '💎';
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
        $this->reset(['editingId', 'name', 'en', 'origin', 'originEn', 'flag', 'balloon', 'icon', 'png']);
        $this->icon = '💎';
        $this->flag = 'ir';
    }

    public function save(): void
    {
        $this->validate([
            'name' => 'required|string|max:255',
            'en'   => 'nullable|string|max:255',
            'png'  => 'nullable|image|max:2048',
        ]);

        $data = [
            'name'      => $this->name,
            'en'        => $this->en,
            'origin'    => $this->origin,
            'origin_en' => $this->originEn ?: $this->origin,
            'flag'      => $this->flag,
            'balloon'   => $this->balloon ?: $this->name,
            'icon'      => $this->icon,
            'is_active' => true,
        ];

        if ($this->png) {
            $data['png_path'] = $this->png->store('stones', 'public');
        }

        if ($this->editingId) {
            Stone::find($this->editingId)?->update($data);
            session()->flash('success', 'سنگ ویرایش شد');
        } else {
            Stone::create($data);
            session()->flash('success', 'سنگ اضافه شد');
        }

        $this->closeForm();
    }

    public function delete(int $id): void
    {
        Stone::find($id)?->delete();
        session()->flash('success', 'سنگ حذف شد');
    }

    public function toggleActive(int $id): void
    {
        $s = Stone::find($id);
        if ($s) {
            $s->update(['is_active' => ! $s->is_active]);
        }
    }

    public function render()
    {
        $stones = Stone::query()
            ->when($this->search, function ($q) {
                $q->where('name', 'like', "%{$this->search}%")
                  ->orWhere('en', 'like', "%{$this->search}%");
            })
            ->orderBy('sort_order')
            ->orderBy('name')
            ->paginate(24);

        return view('livewire.settings.stones', compact('stones'))
            ->layout('components.layouts.app');
    }
}
""")

write_file("resources/views/livewire/settings/stones.blade.php", r"""
<div class="p-4 md:p-6 space-y-4">

    @if (session('success'))
        <div class="alert alert-success text-sm py-2"><span>{{ session('success') }}</span></div>
    @endif

    <div class="flex flex-wrap items-center justify-between gap-3">
        <h1 class="text-xl md:text-2xl font-bold">💎 مدیریت سنگ‌ها</h1>
        <button wire:click="openForm()" class="btn btn-primary btn-sm">➕ سنگ جدید</button>
    </div>

    <div class="bg-base-100 rounded-lg shadow border p-3">
        <input type="text" wire:model.live.debounce.400ms="search"
               placeholder="🔍 جستجوی سنگ..." class="input input-bordered input-sm w-full md:w-80" />
    </div>

    {{-- Grid سنگ‌ها --}}
    <div class="grid grid-cols-2 sm:grid-cols-3 md:grid-cols-4 lg:grid-cols-6 gap-3">
        @forelse($stones as $stone)
            <div wire:key="stone-{{ $stone->id }}"
                 class="card bg-base-100 shadow border {{ ! $stone->is_active ? 'opacity-50' : '' }} hover:shadow-lg transition">

                <div class="card-body p-3 items-center text-center relative">
                    {{-- حذف --}}
                    <button wire:click="delete({{ $stone->id }})" wire:confirm="حذف شود؟"
                            class="absolute top-1 left-1 btn btn-error btn-xs btn-circle opacity-70 hover:opacity-100">✕</button>

                    {{-- Active toggle --}}
                    <button wire:click="toggleActive({{ $stone->id }})"
                            class="absolute top-1 right-1 btn btn-xs btn-circle {{ $stone->is_active ? 'btn-success' : 'btn-ghost' }}">
                        {{ $stone->is_active ? '✓' : '—' }}
                    </button>

                    {{-- آیکون/تصویر --}}
                    <div class="w-16 h-16 rounded-xl bg-base-200 flex items-center justify-center overflow-hidden">
                        @if($stone->png_path)
                            <img src="{{ $stone->png_url }}" class="w-full h-full object-contain" alt="">
                        @else
                            <span class="text-3xl">{{ $stone->icon ?? '💎' }}</span>
                        @endif
                    </div>

                    <div class="font-bold text-xs mt-2 leading-tight">{{ $stone->name }}</div>
                    @if($stone->en)
                        <div class="text-[10px] text-base-content/50" dir="ltr">{{ $stone->en }}</div>
                    @endif
                    @if($stone->origin)
                        <div class="text-[10px] text-base-content/60 mt-1">
                            {{ $stone->flag }} {{ $stone->origin }}
                        </div>
                    @endif

                    <button wire:click="openForm({{ $stone->id }})" class="btn btn-ghost btn-xs mt-1 w-full">
                        ✏️ ویرایش
                    </button>
                </div>
            </div>
        @empty
            <div class="col-span-full text-center py-12 text-base-content/50">
                <div class="text-4xl mb-2">💎</div>
                سنگی نیست
            </div>
        @endforelse
    </div>

    <div>{{ $stones->links() }}</div>

    {{-- Modal فرم سنگ --}}
    @if($showForm)
    <div class="fixed inset-0 z-[90] flex items-start justify-center p-4 overflow-y-auto">
        <div class="fixed inset-0 bg-black/60 backdrop-blur-md" wire:click="closeForm"></div>

        <div class="relative bg-base-100 rounded-2xl shadow-2xl w-full max-w-lg my-8 md:my-16 border border-base-300">

            <div class="flex items-center justify-between p-4 border-b border-base-300 bg-gradient-to-l from-primary/10 to-transparent rounded-t-2xl">
                <div class="flex items-center gap-3">
                    <div class="w-9 h-9 rounded-lg bg-gradient-to-br from-cyan-500 to-teal-600 flex items-center justify-center text-white shadow">
                        {{ $editingId ? '✏️' : '💎' }}
                    </div>
                    <h2 class="font-bold text-base">{{ $editingId ? 'ویرایش سنگ' : 'سنگ جدید' }}</h2>
                </div>
                <button wire:click="closeForm" class="btn btn-ghost btn-sm btn-circle">✕</button>
            </div>

            <div class="p-5 space-y-3 max-h-[calc(100vh-14rem)] overflow-y-auto">

                <div class="grid grid-cols-2 gap-3">
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">نام فارسی *</span></label>
                        <input type="text" wire:model="name" class="input input-bordered input-sm w-full" />
                        @error('name') <span class="text-error text-xs">{{ $message }}</span> @enderror
                    </div>
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">نام انگلیسی</span></label>
                        <input type="text" wire:model="en" dir="ltr" class="input input-bordered input-sm w-full" />
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-3">
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">اصالت (شهر/کشور)</span></label>
                        <input type="text" wire:model="origin" class="input input-bordered input-sm w-full" />
                    </div>
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">کشور</span></label>
                        <select wire:model="flag" class="select select-bordered select-sm w-full">
                            @foreach($countries as $k => $v)
                                <option value="{{ $k }}">{{ $v }}</option>
                            @endforeach
                        </select>
                    </div>
                </div>

                <div class="grid grid-cols-2 gap-3">
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">برچسب (balloon)</span></label>
                        <input type="text" wire:model="balloon" class="input input-bordered input-sm w-full" placeholder="مثلاً: عجمی" />
                    </div>
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">آیکون (ایموجی)</span></label>
                        <input type="text" wire:model="icon" class="input input-bordered input-sm w-full text-center text-2xl" />
                    </div>
                </div>

                <div class="form-control">
                    <label class="label py-1"><span class="label-text text-xs font-bold">تصویر PNG (اختیاری)</span></label>
                    <input type="file" wire:model="png" accept="image/png,image/*"
                           class="file-input file-input-bordered file-input-sm w-full" />
                    @if($png)
                        <div class="mt-2">
                            <img src="{{ $png->temporaryUrl() }}" class="w-20 h-20 object-contain border rounded" />
                        </div>
                    @endif
                    @error('png') <span class="text-error text-xs">{{ $message }}</span> @enderror
                </div>
            </div>

            <div class="p-4 border-t border-base-300 flex justify-end gap-2 rounded-b-2xl bg-base-200/50">
                <button wire:click="closeForm" class="btn btn-ghost btn-sm">انصراف</button>
                <button wire:click="save" wire:loading.attr="disabled" class="btn btn-primary btn-sm">
                    <span wire:loading.remove wire:target="save">✅ ذخیره</span>
                    <span wire:loading wire:target="save">⏳...</span>
                </button>
            </div>
        </div>
    </div>
    @endif
</div>
""")

# =========================================================
# ۵. Livewire: Settings/Metals
# =========================================================

write_file("app/Livewire/Settings/Metals.php", r"""
<?php

namespace App\Livewire\Settings;

use App\Models\Metal;
use Livewire\Component;
use Livewire\WithPagination;

class Metals extends Component
{
    use WithPagination;

    public string $search = '';

    public bool $showForm = false;
    public ?int $editingId = null;
    public string $name = '';
    public string $en = '';
    public string $carat = '';
    public string $icon = '⚙️';

    public function updatingSearch(): void { $this->resetPage(); }

    public function openForm(?int $id = null): void
    {
        $this->resetForm();
        $this->editingId = $id;
        $this->showForm = true;

        if ($id) {
            $m = Metal::find($id);
            if ($m) {
                $this->name  = $m->name;
                $this->en    = $m->en ?? '';
                $this->carat = $m->carat ?? '';
                $this->icon  = $m->icon ?? '⚙️';
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
        $this->reset(['editingId', 'name', 'en', 'carat']);
        $this->icon = '⚙️';
    }

    public function save(): void
    {
        $this->validate([
            'name'  => 'required|string|max:255',
            'carat' => 'nullable|string|max:20',
        ]);

        $data = [
            'name'      => $this->name,
            'en'        => $this->en,
            'carat'     => $this->carat,
            'icon'      => $this->icon,
            'is_active' => true,
        ];

        if ($this->editingId) {
            Metal::find($this->editingId)?->update($data);
            session()->flash('success', 'فلز ویرایش شد');
        } else {
            Metal::create($data);
            session()->flash('success', 'فلز اضافه شد');
        }

        $this->closeForm();
    }

    public function delete(int $id): void
    {
        Metal::find($id)?->delete();
        session()->flash('success', 'فلز حذف شد');
    }

    public function toggleActive(int $id): void
    {
        $m = Metal::find($id);
        if ($m) $m->update(['is_active' => ! $m->is_active]);
    }

    public function render()
    {
        $metals = Metal::query()
            ->when($this->search, fn ($q) => $q->where('name', 'like', "%{$this->search}%"))
            ->orderBy('sort_order')
            ->paginate(20);

        return view('livewire.settings.metals', compact('metals'))
            ->layout('components.layouts.app');
    }
}
""")

write_file("resources/views/livewire/settings/metals.blade.php", r"""
<div class="p-4 md:p-6 space-y-4">

    @if (session('success'))
        <div class="alert alert-success text-sm py-2"><span>{{ session('success') }}</span></div>
    @endif

    <div class="flex flex-wrap items-center justify-between gap-3">
        <h1 class="text-xl md:text-2xl font-bold">⚙️ مدیریت فلزات</h1>
        <button wire:click="openForm()" class="btn btn-primary btn-sm">➕ فلز جدید</button>
    </div>

    <div class="bg-base-100 rounded-lg shadow border p-3">
        <input type="text" wire:model.live.debounce.400ms="search"
               placeholder="🔍 جستجو..." class="input input-bordered input-sm w-full md:w-80" />
    </div>

    <div class="bg-base-100 rounded-lg shadow border overflow-hidden">
        <div class="pro-table-wrap">
            <table class="pro-table">
                <thead>
                    <tr>
                        <th>آیکون</th>
                        <th>نام</th>
                        <th>English</th>
                        <th>عیار</th>
                        <th>وضعیت</th>
                        <th>عملیات</th>
                    </tr>
                </thead>
                <tbody>
                    @forelse($metals as $m)
                        <tr wire:key="metal-{{ $m->id }}" class="{{ ! $m->is_active ? 'opacity-50' : '' }}">
                            <td class="text-2xl">{{ $m->icon }}</td>
                            <td class="font-bold">{{ $m->name }}</td>
                            <td dir="ltr">{{ $m->en }}</td>
                            <td class="font-mono">{{ $m->carat }}</td>
                            <td>
                                <button wire:click="toggleActive({{ $m->id }})"
                                        class="badge badge-{{ $m->is_active ? 'success' : 'ghost' }} badge-sm cursor-pointer">
                                    {{ $m->is_active ? '✓ فعال' : 'غیرفعال' }}
                                </button>
                            </td>
                            <td>
                                <div class="flex gap-1">
                                    <button wire:click="openForm({{ $m->id }})" class="btn btn-ghost btn-xs">✏️</button>
                                    <button wire:click="delete({{ $m->id }})" wire:confirm="حذف شود؟"
                                            class="btn btn-ghost btn-xs text-error">🗑️</button>
                                </div>
                            </td>
                        </tr>
                    @empty
                        <tr><td colspan="6" class="text-center py-8 text-base-content/50">فلزی نیست</td></tr>
                    @endforelse
                </tbody>
            </table>
        </div>
    </div>

    <div>{{ $metals->links() }}</div>

    @if($showForm)
    <div class="fixed inset-0 z-[90] flex items-start justify-center p-4 overflow-y-auto">
        <div class="fixed inset-0 bg-black/60 backdrop-blur-md" wire:click="closeForm"></div>

        <div class="relative bg-base-100 rounded-2xl shadow-2xl w-full max-w-md my-8 md:my-16 border border-base-300">
            <div class="flex items-center justify-between p-4 border-b border-base-300 bg-gradient-to-l from-primary/10 to-transparent rounded-t-2xl">
                <div class="flex items-center gap-3">
                    <div class="w-9 h-9 rounded-lg bg-gradient-to-br from-cyan-500 to-teal-600 flex items-center justify-center text-white shadow">
                        {{ $editingId ? '✏️' : '⚙️' }}
                    </div>
                    <h2 class="font-bold text-base">{{ $editingId ? 'ویرایش فلز' : 'فلز جدید' }}</h2>
                </div>
                <button wire:click="closeForm" class="btn btn-ghost btn-sm btn-circle">✕</button>
            </div>

            <div class="p-5 space-y-3">
                <div class="form-control">
                    <label class="label py-1"><span class="label-text text-xs font-bold">نام *</span></label>
                    <input type="text" wire:model="name" class="input input-bordered input-sm w-full" />
                    @error('name') <span class="text-error text-xs">{{ $message }}</span> @enderror
                </div>
                <div class="form-control">
                    <label class="label py-1"><span class="label-text text-xs font-bold">English</span></label>
                    <input type="text" wire:model="en" dir="ltr" class="input input-bordered input-sm w-full" />
                </div>
                <div class="grid grid-cols-2 gap-3">
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">عیار</span></label>
                        <input type="text" wire:model="carat" dir="ltr" class="input input-bordered input-sm w-full font-mono" />
                    </div>
                    <div class="form-control">
                        <label class="label py-1"><span class="label-text text-xs font-bold">آیکون</span></label>
                        <input type="text" wire:model="icon" class="input input-bordered input-sm w-full text-center text-2xl" />
                    </div>
                </div>
            </div>

            <div class="p-4 border-t border-base-300 flex justify-end gap-2 rounded-b-2xl bg-base-200/50">
                <button wire:click="closeForm" class="btn btn-ghost btn-sm">انصراف</button>
                <button wire:click="save" wire:loading.attr="disabled" class="btn btn-primary btn-sm">
                    <span wire:loading.remove wire:target="save">✅ ذخیره</span>
                    <span wire:loading wire:target="save">⏳...</span>
                </button>
            </div>
        </div>
    </div>
    @endif
</div>
""")

# =========================================================
# ۶. Livewire: Certificates/Designer
# =========================================================

write_file("app/Livewire/Certificates/Designer.php", r"""
<?php

namespace App\Livewire\Certificates;

use App\Models\CertSetting;
use App\Models\Certificate;
use Livewire\Component;

class Designer extends Component
{
    public ?int $certificateId = null;
    public Certificate $certificate;

    public array $design = [];

    public function mount(?int $certificate = null): void
    {
        // اگه شناسنامه مشخص نشده، اولین رو بگیر
        if ($certificate) {
            $this->certificateId = $certificate;
            $this->certificate = Certificate::findOrFail($certificate);
        } else {
            $first = Certificate::first();
            if ($first) {
                $this->certificateId = $first->id;
                $this->certificate = $first;
            } else {
                // شناسنامه خالی برای طراحی
                $this->certificate = new Certificate([
                    'code' => '000000',
                    'serial' => 'MJ-DESIGN',
                    'stone_name' => 'فیروزه عجمی',
                    'stone_en' => 'Turquoise Ajami',
                    'stone_origin' => 'نیشابور',
                    'stone_flag' => 'ir',
                    'metal' => 'نقره 925',
                    'metal_en' => 'Silver 925',
                    'metal_carat' => '925',
                    'length' => 13,
                    'width' => 9,
                    'weight' => 1.28,
                    'brilliant' => 5,
                ]);
            }
        }

        $this->design = $this->certificate->design_data ?? $this->getDefaultDesign();
    }

    public function getDefaultDesign(): array
    {
        return [
            'version' => '1.0',
            'elements' => [
                ['id' => 'title',    'type' => 'text', 'text' => 'Certificate',        'x' => 180, 'y' => 30,  'fontSize' => 28, 'fontFamily' => 'serif',    'fill' => '#6b4423', 'fontWeight' => 'bold'],
                ['id' => 'stone',    'type' => 'text', 'text' => '{stoneEn}',          'x' => 160, 'y' => 90,  'fontSize' => 20, 'fontFamily' => 'sans',     'fill' => '#0369a1', 'fontWeight' => 'bold'],
                ['id' => 'metal',    'type' => 'text', 'text' => '{metal} ({carat})',  'x' => 160, 'y' => 130, 'fontSize' => 14, 'fontFamily' => 'sans',     'fill' => '#334155'],
                ['id' => 'size',     'type' => 'text', 'text' => '{length}×{width} mm','x' => 160, 'y' => 165, 'fontSize' => 12, 'fontFamily' => 'sans',     'fill' => '#334155'],
                ['id' => 'weight',   'type' => 'text', 'text' => 'Weight: {weight} gr','x' => 160, 'y' => 195, 'fontSize' => 12, 'fontFamily' => 'sans',     'fill' => '#334155'],
                ['id' => 'code',     'type' => 'text', 'text' => 'Code: {code}',       'x' => 160, 'y' => 230, 'fontSize' => 14, 'fontFamily' => 'monospace','fill' => '#b45309', 'fontWeight' => 'bold'],
                ['id' => 'qr',       'type' => 'qr',   'text' => '',                    'x' => 420, 'y' => 400, 'size' => 100],
            ]
        ];
    }

    public function save(array $design): void
    {
        $this->design = $design;
        $this->certificate->update(['design_data' => $design]);

        session()->flash('success', 'طراحی ذخیره شد');
    }

    public function render()
    {
        return view('livewire.certificates.designer')
            ->layout('components.layouts.app');
    }
}
""")

write_file("resources/views/livewire/certificates/designer.blade.php", r"""
<div class="p-4 md:p-6 max-w-7xl mx-auto">

    <div class="flex flex-wrap items-center justify-between gap-3 mb-4">
        <div class="flex items-center gap-3">
            <a href="{{ route('certificates.index') }}" class="btn btn-ghost btn-sm">→</a>
            <div>
                <h1 class="text-xl md:text-2xl font-bold">🎨 ویرایشگر شناسنامه</h1>
                <div class="text-xs text-base-content/60 mt-0.5">
                    {{ $certificate->code }} — {{ $certificate->stone_name }}
                </div>
            </div>
        </div>
        <div class="flex gap-2">
            <button onclick="designerExportPng()" class="btn btn-secondary btn-sm">📸 PNG</button>
            <button onclick="designerPrint()" class="btn btn-info btn-sm">🖨️ چاپ</button>
            <button onclick="designerSave()" class="btn btn-primary btn-sm">💾 ذخیره</button>
        </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-4 gap-4">

        {{-- ابزار چپ --}}
        <div class="card bg-base-100 shadow border lg:order-1 order-2">
            <div class="card-body p-3">
                <h3 class="font-bold text-sm mb-3">🧰 ابزار</h3>

                <div class="space-y-2">
                    <button onclick="designerAddText('متن جدید')" class="btn btn-outline btn-sm w-full justify-start">
                        📝 متن جدید
                    </button>
                    <button onclick="designerAddPlaceholder('{stoneEn}')" class="btn btn-outline btn-sm w-full justify-start">
                        💎 سنگ
                    </button>
                    <button onclick="designerAddPlaceholder('{metal}')" class="btn btn-outline btn-sm w-full justify-start">
                        ⚙️ فلز
                    </button>
                    <button onclick="designerAddPlaceholder('{weight} gr')" class="btn btn-outline btn-sm w-full justify-start">
                        ⚖️ وزن
                    </button>
                    <button onclick="designerAddPlaceholder('{length}×{width}')" class="btn btn-outline btn-sm w-full justify-start">
                        📐 ابعاد
                    </button>
                    <button onclick="designerAddPlaceholder('#{code}')" class="btn btn-outline btn-sm w-full justify-start">
                        🔢 کد
                    </button>
                    <button onclick="designerAddQR()" class="btn btn-outline btn-sm w-full justify-start">
                        📱 QR کد
                    </button>
                </div>

                <div class="divider my-2 text-xs">ویرایش</div>

                <div class="space-y-2">
                    <button onclick="designerDelete()" class="btn btn-error btn-sm w-full">🗑️ حذف انتخاب</button>
                    <button onclick="designerBringForward()" class="btn btn-ghost btn-sm w-full">⬆️ بالا</button>
                    <button onclick="designerSendBackward()" class="btn btn-ghost btn-sm w-full">⬇️ پایین</button>
                </div>

                <div class="divider my-2 text-xs">ویژگی‌ها</div>

                <div id="propsPanel" class="text-xs space-y-2 text-base-content/60">
                    شیئی انتخاب کن
                </div>
            </div>
        </div>

        {{-- بوم --}}
        <div class="card bg-base-100 shadow border lg:col-span-3 lg:order-2 order-1">
            <div class="card-body p-3">
                <div class="bg-base-200 rounded-lg p-4 flex justify-center overflow-auto min-h-[500px]">
                    <canvas id="designerCanvas" width="600" height="600"
                            class="border-4 border-white shadow-xl bg-white rounded-lg"></canvas>
                </div>
                <div class="text-xs text-base-content/60 text-center mt-2">
                    🖱 عناصر رو بکش، گوشه رو بگیر تا تغییر سایز بدی
                </div>
            </div>
        </div>
    </div>

    @if (session('success'))
        <div class="alert alert-success mt-4 text-sm"><span>{{ session('success') }}</span></div>
    @endif
</div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/fabric.js/5.3.1/fabric.min.js"></script>
<script>
    let canvas;
    let initialDesign = @json($design ?? []);
    let certData = {
        code:        @json($certificate->code ?? ''),
        stoneEn:     @json($certificate->stone_en ?? ''),
        stoneName:   @json($certificate->stone_name ?? ''),
        metal:       @json($certificate->metal ?? ''),
        metalEn:     @json($certificate->metal_en ?? ''),
        carat:       @json($certificate->metal_carat ?? ''),
        weight:      @json($certificate->weight ?? ''),
        length:      @json($certificate->length ?? ''),
        width:       @json($certificate->width ?? ''),
        brilliant:   @json($certificate->brilliant ?? ''),
    };

    const defaultDesign = @json($design ?? null);

    document.addEventListener('DOMContentLoaded', () => {
        canvas = new fabric.Canvas('designerCanvas', { backgroundColor: '#fffef9' });

        // بارگذاری طراحی
        if (defaultDesign && defaultDesign.elements && defaultDesign.elements.length) {
            defaultDesign.elements.forEach(el => {
                if (el.type === 'text') {
                    addText(el.text, el.x, el.y, el);
                } else if (el.type === 'qr') {
                    addQR(el.x, el.y, el.size || 100);
                }
            });
        } else {
            // طراحی پیش‌فرض
            addText('Certificate',  180, 30,  { fontSize: 28, fontWeight: 'bold', fill: '#6b4423' });
            addText('{stoneEn}',    160, 90,  { fontSize: 20, fontWeight: 'bold', fill: '#0369a1' });
            addText('{metal}',      160, 130, { fontSize: 14, fill: '#334155' });
            addText('{length}×{width} mm', 160, 165, { fontSize: 12, fill: '#334155' });
            addText('Weight: {weight} gr', 160, 195, { fontSize: 12, fill: '#334155' });
            addText('Code: {code}', 160, 230, { fontSize: 14, fontWeight: 'bold', fill: '#b45309' });
        }

        canvas.on('selection:created', updatePropsPanel);
        canvas.on('selection:updated', updatePropsPanel);
        canvas.on('selection:cleared', () => {
            document.getElementById('propsPanel').innerHTML = 'شیئی انتخاب کن';
        });
    });

    function replacePlaceholders(text) {
        return text
            .replace(/{code}/g, certData.code)
            .replace(/{stoneEn}/g, certData.stoneEn)
            .replace(/{stoneName}/g, certData.stoneName)
            .replace(/{metal}/g, certData.metal)
            .replace(/{metalEn}/g, certData.metalEn)
            .replace(/{carat}/g, certData.carat)
            .replace(/{weight}/g, certData.weight)
            .replace(/{length}/g, certData.length)
            .replace(/{width}/g, certData.width)
            .replace(/{brilliant}/g, certData.brilliant);
    }

    function addText(text, x, y, opts = {}) {
        const displayed = replacePlaceholders(text);
        const t = new fabric.Text(displayed, Object.assign({
            left: x, top: y,
            fontSize: 18,
            fill: '#334155',
            fontFamily: 'Tahoma, sans-serif',
            direction: 'rtl',
        }, opts));
        t._rawText = text; // ذخیره متن اصلی با placeholder
        canvas.add(t);
        canvas.setActiveObject(t);
        canvas.renderAll();
    }

    function designerAddText(text) {
        addText(text, 100, 100, { fontSize: 16 });
    }

    function designerAddPlaceholder(ph) {
        addText(ph, 100, 150, { fontSize: 14, fill: '#0369a1' });
    }

    function addQR(x = 400, y = 400, size = 100) {
        const url = 'https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=' + encodeURIComponent('https://mashahirid.ir/Q/' + certData.code);
        fabric.Image.fromURL(url, (img) => {
            img.scaleToWidth(size);
            img.set({ left: x, top: y });
            canvas.add(img);
            canvas.setActiveObject(img);
            canvas.renderAll();
        }, { crossOrigin: 'anonymous' });
    }

    function designerAddQR() { addQR(); }

    function designerDelete() {
        const active = canvas.getActiveObjects();
        if (active.length) {
            active.forEach(obj => canvas.remove(obj));
            canvas.discardActiveObject();
            canvas.renderAll();
        }
    }

    function designerBringForward() {
        const a = canvas.getActiveObject();
        if (a) canvas.bringForward(a);
    }

    function designerSendBackward() {
        const a = canvas.getActiveObject();
        if (a) canvas.sendBackwards(a);
    }

    function updatePropsPanel() {
        const obj = canvas.getActiveObject();
        if (!obj) return;

        const panel = document.getElementById('propsPanel');
        panel.innerHTML = `
            <div><strong>${obj.type}</strong></div>
            <div>X: ${Math.round(obj.left)} · Y: ${Math.round(obj.top)}</div>
            ${obj.type === 'text' ? `
                <label class="block mt-2">متن (placeholder مجاز)</label>
                <input type="text" id="propText" value="${obj._rawText || obj.text}" class="input input-bordered input-xs w-full" />
                <label class="block mt-2">اندازه فونت</label>
                <input type="number" id="propFontSize" value="${obj.fontSize || 14}" class="input input-bordered input-xs w-full" />
                <label class="block mt-2">رنگ</label>
                <input type="color" id="propFill" value="${obj.fill || '#334155'}" class="input input-bordered input-xs w-full h-8" />
                <button onclick="applyTextProps()" class="btn btn-primary btn-xs w-full mt-2">اعمال</button>
            ` : ''}
        `;
    }

    function applyTextProps() {
        const obj = canvas.getActiveObject();
        if (!obj || obj.type !== 'text') return;

        const rawText = document.getElementById('propText').value;
        obj._rawText = rawText;
        obj.set('text', replacePlaceholders(rawText));
        obj.set('fontSize', parseInt(document.getElementById('propFontSize').value) || 14);
        obj.set('fill', document.getElementById('propFill').value);
        canvas.renderAll();
    }

    function designerSave() {
        const elements = [];
        canvas.getObjects().forEach(obj => {
            if (obj.type === 'text') {
                elements.push({
                    id:    'txt_' + Math.random().toString(36).substr(2, 6),
                    type:  'text',
                    text:  obj._rawText || obj.text,
                    x:     Math.round(obj.left),
                    y:     Math.round(obj.top),
                    fontSize:   obj.fontSize,
                    fontFamily: obj.fontFamily,
                    fill:       obj.fill,
                    fontWeight: obj.fontWeight || 'normal',
                });
            } else if (obj.type === 'image') {
                elements.push({
                    id:   'img_' + Math.random().toString(36).substr(2, 6),
                    type: 'qr',
                    x:    Math.round(obj.left),
                    y:    Math.round(obj.top),
                    size: Math.round(obj.width * (obj.scaleX || 1)),
                });
            }
        });

        @this.call('save', { version: '1.0', elements: elements });
        alert('طراحی ذخیره شد ✅');
    }

    function designerExportPng() {
        const dataURL = canvas.toDataURL({ format: 'png', multiplier: 3 });
        const link = document.createElement('a');
        link.download = 'certificate-' + certData.code + '.png';
        link.href = dataURL;
        link.click();
    }

    function designerPrint() {
        const dataURL = canvas.toDataURL({ format: 'png', multiplier: 3 });
        const w = window.open('');
        w.document.write(`
            <html dir="rtl"><head><title>چاپ</title>
            <style>@page{size:A4;margin:10mm}body{margin:0;display:flex;justify-content:center;padding:20px}img{max-width:100%}</style>
            </head><body onload="window.print();setTimeout(()=>window.close(),500)"><img src="${dataURL}"></body></html>
        `);
        w.document.close();
    }
</script>
""")

# =========================================================
# ۷. Routes به‌روز
# =========================================================

write_file("routes/web.php", r"""
<?php

use Illuminate\Support\Facades\Route;
use Illuminate\Support\Facades\Auth;
use App\Livewire\Auth\Login;
use App\Livewire\Dashboard;
use App\Livewire\ActivityLog;
use App\Livewire\Orders\Index as OrdersIndex;
use App\Livewire\Orders\Create as OrdersCreate;
use App\Livewire\Orders\Show as OrdersShow;
use App\Livewire\Orders\Edit as OrdersEdit;
use App\Livewire\Orders\PrintLabel as OrdersPrintLabel;
use App\Livewire\Orders\BulkPrintLabels as OrdersBulkPrintLabels;
use App\Livewire\Orders\CourierList as OrdersCourierList;
use App\Livewire\Orders\ImportTipax;
use App\Livewire\Customers\Index as CustomersIndex;
use App\Livewire\Customers\Create as CustomersCreate;
use App\Livewire\Customers\Show as CustomersShow;
use App\Livewire\Customers\Edit as CustomersEdit;
use App\Livewire\Certificates\Index as CertificatesIndex;
use App\Livewire\Certificates\Create as CertificatesCreate;
use App\Livewire\Certificates\Show as CertificatesShow;
use App\Livewire\Certificates\Designer as CertificatesDesigner;
use App\Livewire\Reports\Index as ReportsIndex;
use App\Livewire\Settings\Index as SettingsIndex;
use App\Livewire\Settings\Stones as SettingsStones;
use App\Livewire\Settings\Metals as SettingsMetals;

Route::get('/', fn () => redirect('/dashboard'));

Route::middleware('guest')->group(function () {
    Route::get('/login', Login::class)->name('login');
});

Route::middleware('auth')->group(function () {
    Route::post('/logout', function () {
        Auth::logout();
        request()->session()->invalidate();
        request()->session()->regenerateToken();
        return redirect('/login');
    })->name('logout');

    Route::get('/dashboard', Dashboard::class)->name('dashboard');
    Route::get('/activity-log', ActivityLog::class)->name('activity-log');

    Route::prefix('orders')->name('orders.')->group(function () {
        Route::get('/', OrdersIndex::class)->name('index');
        Route::get('/create', OrdersCreate::class)->name('create');
        Route::get('/import-tipax', ImportTipax::class)->name('import-tipax');
        Route::get('/courier-list', OrdersCourierList::class)->name('courier-list');
        Route::get('/bulk-print-labels', OrdersBulkPrintLabels::class)->name('bulk-print-labels');
        Route::get('/{order}/print-label', OrdersPrintLabel::class)->name('print-label');
        Route::get('/{order}/edit', OrdersEdit::class)->name('edit');
        Route::get('/{order}', OrdersShow::class)->name('show');
    });

    Route::prefix('customers')->name('customers.')->group(function () {
        Route::get('/', CustomersIndex::class)->name('index');
        Route::get('/create', CustomersCreate::class)->name('create');
        Route::get('/{customer}/edit', CustomersEdit::class)->name('edit');
        Route::get('/{customer}', CustomersShow::class)->name('show');
    });

    Route::prefix('certificates')->name('certificates.')->group(function () {
        Route::get('/', CertificatesIndex::class)->name('index');
        Route::get('/create', CertificatesCreate::class)->name('create');
        Route::get('/designer/{certificate?}', CertificatesDesigner::class)->name('designer');
        Route::get('/{certificate}', CertificatesShow::class)->name('show');
    });

    Route::get('/reports', ReportsIndex::class)->name('reports.index');

    Route::prefix('settings')->name('settings.')->group(function () {
        Route::get('/', SettingsIndex::class)->name('index');
        Route::get('/stones', SettingsStones::class)->name('stones');
        Route::get('/metals', SettingsMetals::class)->name('metals');
    });
});
""")

# =========================================================
# ۸. Settings Index — بازنویسی با لینک سنگ/فلز
# =========================================================

write_file("resources/views/livewire/settings/index.blade.php", r"""
<div class="p-4 md:p-6 space-y-5 max-w-4xl mx-auto">

    <h1 class="text-xl md:text-2xl font-bold">⚙️ تنظیمات</h1>

    {{-- دسترسی سریع --}}
    <div class="grid grid-cols-2 md:grid-cols-4 gap-3">
        <a href="{{ route('settings.stones') }}" class="card bg-base-100 shadow hover:shadow-lg transition cursor-pointer">
            <div class="card-body p-4 text-center">
                <div class="text-3xl">💎</div>
                <div class="font-bold text-sm mt-2">سنگ‌ها</div>
            </div>
        </a>
        <a href="{{ route('settings.metals') }}" class="card bg-base-100 shadow hover:shadow-lg transition cursor-pointer">
            <div class="card-body p-4 text-center">
                <div class="text-3xl">⚙️</div>
                <div class="font-bold text-sm mt-2">فلزات</div>
            </div>
        </a>
        <a href="{{ route('certificates.designer') }}" class="card bg-base-100 shadow hover:shadow-lg transition cursor-pointer">
            <div class="card-body p-4 text-center">
                <div class="text-3xl">🎨</div>
                <div class="font-bold text-sm mt-2">طراحی شناسنامه</div>
            </div>
        </a>
        <a href="{{ route('activity-log') }}" class="card bg-base-100 shadow hover:shadow-lg transition cursor-pointer">
            <div class="card-body p-4 text-center">
                <div class="text-3xl">📜</div>
                <div class="font-bold text-sm mt-2">لاگ فعالیت‌ها</div>
            </div>
        </a>
    </div>

    {{-- پروفایل --}}
    <div class="card bg-base-100 shadow">
        <div class="card-body">
            <h2 class="card-title text-base mb-3">👤 پروفایل کاربری</h2>

            @if (session('profile_success'))
                <div class="alert alert-success mb-3 text-sm"><span>{{ session('profile_success') }}</span></div>
            @endif

            <div class="space-y-3">
                <div class="form-control">
                    <label class="label py-1"><span class="label-text font-bold text-sm">نام</span></label>
                    <input type="text" wire:model="name" class="input input-bordered input-sm w-full" />
                </div>
                <div class="form-control">
                    <label class="label py-1"><span class="label-text font-bold text-sm">ایمیل</span></label>
                    <input type="email" wire:model="email" dir="ltr" class="input input-bordered input-sm w-full" />
                </div>
                <div class="flex justify-end">
                    <button wire:click="updateProfile" class="btn btn-primary btn-sm">💾 ذخیره</button>
                </div>
            </div>
        </div>
    </div>

    {{-- تغییر رمز --}}
    <div class="card bg-base-100 shadow">
        <div class="card-body">
            <h2 class="card-title text-base mb-3">🔐 تغییر رمز عبور</h2>

            @if (session('password_success'))
                <div class="alert alert-success mb-3 text-sm"><span>{{ session('password_success') }}</span></div>
            @endif

            <div class="space-y-3">
                <div class="form-control">
                    <label class="label py-1"><span class="label-text font-bold text-sm">رمز جدید</span></label>
                    <input type="password" wire:model="newPassword" dir="ltr" class="input input-bordered input-sm w-full" />
                </div>
                <div class="form-control">
                    <label class="label py-1"><span class="label-text font-bold text-sm">تکرار رمز</span></label>
                    <input type="password" wire:model="newPasswordConfirm" dir="ltr" class="input input-bordered input-sm w-full" />
                </div>
                <div class="flex justify-end">
                    <button wire:click="updatePassword" class="btn btn-warning btn-sm">🔐 تغییر</button>
                </div>
            </div>
        </div>
    </div>

    {{-- درباره --}}
    <div class="card bg-base-100 shadow">
        <div class="card-body">
            <h2 class="card-title text-base mb-3">ℹ️ درباره سیستم</h2>
            <div class="text-sm space-y-1.5 leading-7 text-base-content/80">
                <div><strong>نام:</strong> شاپگان نسخه ۲ (ShopGun V2)</div>
                <div><strong>سازنده:</strong> گروه هنری اقاقیا</div>
                <div><strong>معماری:</strong> امیر حاجی قاسمی</div>
                <div><strong>Laravel:</strong> {{ app()->version() }}</div>
                <div><strong>PHP:</strong> {{ PHP_VERSION }}</div>
            </div>
        </div>
    </div>
</div>
""")

print()
print("═" * 60)
print("✅ Part C کامل شد — Designer + تنظیمات سنگ/فلز")
print("═" * 60)
print()
print("📌 اجرا کن:")
print("   php artisan optimize:clear")
print("   php artisan migrate")
print("   php artisan db:seed --class=StoneMetalSeeder --force")
print("   php artisan storage:link")
print("   npm run build")
print("   php artisan serve --host=0.0.0.0 --port=8000")
print()
print("🎯 صفحات جدید:")
print("   /settings/stones          ← مدیریت سنگ‌ها")
print("   /settings/metals          ← مدیریت فلزات")
print("   /certificates/designer    ← ویرایشگر طراحی")
print()
