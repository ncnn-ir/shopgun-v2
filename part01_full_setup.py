from pathlib import Path
import textwrap

PROJECT = Path.home() / "projects" / "shopgun-v2.1"

if not PROJECT.exists():
    raise SystemExit(f"❌ پروژه پیدا نشد: {PROJECT}")

def write_file(relative_path, content):
    path = PROJECT / relative_path
    path.parent.mkdir(parents=True, exist_ok=True)
    existed = path.exists()
    path.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    action = "🔁" if existed else "✅"
    print(f"{action} {relative_path}")

print("═" * 60)
print("🚀 ساخت کامل ShopGun V2.1")
print("═" * 60)
print()

# =========================================================
# ۱. مدل‌ها
# =========================================================
print("📦 مدل‌ها...")

write_file("app/Models/Channel.php", r"""
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;

class Channel extends Model
{
    protected $fillable = ['key', 'name', 'icon', 'color', 'is_active', 'sort_order'];
    protected $casts = ['is_active' => 'boolean'];

    public function orders(): HasMany
    {
        return $this->hasMany(Order::class);
    }
}
""")

write_file("app/Models/Customer.php", r"""
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\HasMany;
use Spatie\Activitylog\Models\Activity;
use Spatie\Activitylog\Models\Concerns\LogsActivity;
use Spatie\Activitylog\Support\LogOptions;

class Customer extends Model
{
    use LogsActivity;

    protected $fillable = ['name', 'phone', 'postal_code', 'address', 'notes', 'meta'];
    protected $casts = ['meta' => 'array'];

    public function getActivitylogOptions(): LogOptions
    {
        return LogOptions::defaults()
            ->logOnly(['name', 'phone', 'address', 'postal_code'])
            ->logOnlyDirty()
            ->useLogName('customer');
    }

    public function orders(): HasMany
    {
        return $this->hasMany(Order::class);
    }

    public function activities()
    {
        return Activity::query()
            ->where('subject_type', $this->getMorphClass())
            ->where('subject_id', $this->getKey())
            ->latest();
    }
}
""")

write_file("app/Models/Order.php", r"""
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Spatie\Activitylog\Models\Activity;
use Spatie\Activitylog\Models\Concerns\LogsActivity;
use Spatie\Activitylog\Support\LogOptions;

class Order extends Model
{
    use LogsActivity;

    protected $fillable = [
        'order_number', 'customer_id', 'channel_id', 'status',
        'amount', 'insurance', 'address', 'postal_code', 'phone',
        'notes', 'meta',
    ];

    protected $casts = [
        'amount'    => 'decimal:2',
        'insurance' => 'decimal:2',
        'meta'      => 'array',
    ];

    public function getActivitylogOptions(): LogOptions
    {
        return LogOptions::defaults()
            ->logOnly(['status', 'amount', 'insurance', 'address'])
            ->logOnlyDirty()
            ->useLogName('order');
    }

    public function customer(): BelongsTo
    {
        return $this->belongsTo(Customer::class);
    }

    public function channel(): BelongsTo
    {
        return $this->belongsTo(Channel::class);
    }

    public function activities()
    {
        return Activity::query()
            ->where('subject_type', $this->getMorphClass())
            ->where('subject_id', $this->getKey())
            ->latest();
    }

    public function getStatusColorAttribute(): string
    {
        return match ($this->status) {
            'pending'     => 'warning',
            'final-check' => 'info',
            'courier'     => 'success',
            default       => 'ghost',
        };
    }

    public function getStatusLabelAttribute(): string
    {
        return match ($this->status) {
            'pending'     => '📝 ثبت سفارش',
            'final-check' => '🔍 چک نهایی',
            'courier'     => '🚚 تحویل مامور',
            default       => $this->status,
        };
    }
}
""")

write_file("app/Models/Certificate.php", r"""
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;
use Spatie\Activitylog\Models\Activity;
use Spatie\Activitylog\Models\Concerns\LogsActivity;
use Spatie\Activitylog\Support\LogOptions;

class Certificate extends Model
{
    use LogsActivity;

    protected $fillable = [
        'code', 'serial', 'sku', 'stone_name', 'stone_en', 'stone_origin', 'stone_flag',
        'metal', 'metal_en', 'metal_carat', 'length', 'width', 'weight', 'brilliant',
        'image_path', 'order_id', 'customer_id', 'issued_at', 'design_data', 'meta',
    ];

    protected $casts = [
        'length'      => 'decimal:2',
        'width'       => 'decimal:2',
        'weight'      => 'decimal:3',
        'brilliant'   => 'integer',
        'issued_at'   => 'datetime',
        'design_data' => 'array',
        'meta'        => 'array',
    ];

    public function getActivitylogOptions(): LogOptions
    {
        return LogOptions::defaults()
            ->logOnly(['code', 'stone_name', 'metal', 'weight'])
            ->logOnlyDirty()
            ->useLogName('certificate');
    }

    public function order(): BelongsTo { return $this->belongsTo(Order::class); }
    public function customer(): BelongsTo { return $this->belongsTo(Customer::class); }

    public function activities()
    {
        return Activity::query()
            ->where('subject_type', $this->getMorphClass())
            ->where('subject_id', $this->getKey())
            ->latest();
    }

    public static function generateCode(): string
    {
        do { $code = (string) random_int(100000, 999999); }
        while (self::where('code', $code)->exists());
        return $code;
    }

    public static function generateSerial(string $code, string $stoneEn = 'XXX'): string
    {
        $now  = now();
        $ymd  = $now->format('ymd');
        $hm   = $now->format('Hi');
        $abbr = strtoupper(substr(preg_replace('/[^A-Za-z]/', '', $stoneEn), 0, 3)) ?: 'XXX';
        return "MJ-{$ymd}-{$hm}-{$code}-{$abbr}-A";
    }

    public function getPublicUrlAttribute(): string
    {
        return url("/Q/{$this->code}");
    }

    public function getQrUrlAttribute(): string
    {
        return 'https://api.qrserver.com/v1/create-qr-code/?size=300x300&margin=1&data=' . urlencode($this->public_url);
    }
}
""")

write_file("app/Models/Integration.php", r"""
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Support\Facades\Crypt;

class Integration extends Model
{
    protected $fillable = [
        'key', 'name', 'base_url', 'consumer_key', 'consumer_secret',
        'is_active', 'last_sync_at', 'sync_stats', 'settings',
    ];

    protected $casts = [
        'is_active'    => 'boolean',
        'last_sync_at' => 'datetime',
        'sync_stats'   => 'array',
        'settings'     => 'array',
    ];
}
""")

write_file("app/Models/AppNotification.php", r"""
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;
use Illuminate\Database\Eloquent\Relations\BelongsTo;

class AppNotification extends Model
{
    protected $table = 'app_notifications';

    protected $fillable = ['user_id', 'type', 'title', 'message', 'icon', 'url', 'is_read', 'data'];
    protected $casts = ['is_read' => 'boolean', 'data' => 'array'];

    public function user(): BelongsTo { return $this->belongsTo(User::class); }

    public static function broadcast(string $type, string $title, string $message, string $icon = '🔔', ?string $url = null, array $data = []): void
    {
        foreach (User::all() as $user) {
            self::create([
                'user_id' => $user->id,
                'type'    => $type,
                'title'   => $title,
                'message' => $message,
                'icon'    => $icon,
                'url'     => $url,
                'data'    => $data,
            ]);
        }
    }
}
""")

write_file("app/Models/User.php", r"""
<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Factories\HasFactory;
use Illuminate\Foundation\Auth\User as Authenticatable;
use Illuminate\Notifications\Notifiable;
use Spatie\Permission\Traits\HasRoles;

class User extends Authenticatable
{
    use HasFactory, Notifiable, HasRoles;

    protected $fillable = ['name', 'email', 'password'];
    protected $hidden   = ['password', 'remember_token'];

    protected function casts(): array
    {
        return [
            'email_verified_at' => 'datetime',
            'password'          => 'hashed',
        ];
    }
}
""")

# =========================================================
# ۲. مایگریشن‌ها
# =========================================================
print()
print("📦 مایگریشن‌ها...")

write_file("database/migrations/2026_09_16_000001_create_channels_table.php", r"""
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('channels', function (Blueprint $table) {
            $table->id();
            $table->string('key')->unique();
            $table->string('name');
            $table->string('icon')->nullable();
            $table->string('color')->nullable();
            $table->boolean('is_active')->default(true);
            $table->integer('sort_order')->default(0);
            $table->timestamps();
        });
    }

    public function down(): void { Schema::dropIfExists('channels'); }
};
""")

write_file("database/migrations/2026_09_16_000002_create_customers_table.php", r"""
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('customers', function (Blueprint $table) {
            $table->id();
            $table->string('name')->nullable();
            $table->string('phone')->unique()->index();
            $table->string('postal_code')->nullable();
            $table->text('address')->nullable();
            $table->text('notes')->nullable();
            $table->json('meta')->nullable();
            $table->timestamps();
            $table->index('name');
        });
    }

    public function down(): void { Schema::dropIfExists('customers'); }
};
""")

write_file("database/migrations/2026_09_16_000003_create_orders_table.php", r"""
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('orders', function (Blueprint $table) {
            $table->id();
            $table->string('order_number')->unique()->index();
            $table->foreignId('customer_id')->nullable()->constrained('customers')->nullOnDelete();
            $table->foreignId('channel_id')->nullable()->constrained('channels')->nullOnDelete();
            $table->string('status')->default('pending')->index();
            $table->decimal('amount', 15, 2)->default(0);
            $table->decimal('insurance', 15, 2)->default(0);
            $table->text('address')->nullable();
            $table->string('postal_code')->nullable();
            $table->string('phone')->nullable()->index();
            $table->text('notes')->nullable();
            $table->json('meta')->nullable();
            $table->timestamps();
            $table->index('created_at');
        });
    }

    public function down(): void { Schema::dropIfExists('orders'); }
};
""")

write_file("database/migrations/2026_09_16_000004_create_certificates_table.php", r"""
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('certificates', function (Blueprint $table) {
            $table->id();
            $table->string('code')->unique()->index();
            $table->string('serial')->unique()->index();
            $table->string('sku')->nullable()->index();
            $table->string('stone_name');
            $table->string('stone_en')->nullable();
            $table->string('stone_origin')->nullable();
            $table->string('stone_flag', 4)->nullable();
            $table->string('metal');
            $table->string('metal_en')->nullable();
            $table->string('metal_carat')->nullable();
            $table->decimal('length', 8, 2)->default(0);
            $table->decimal('width', 8, 2)->default(0);
            $table->decimal('weight', 10, 3)->default(0);
            $table->integer('brilliant')->default(0);
            $table->string('image_path')->nullable();
            $table->foreignId('order_id')->nullable()->constrained('orders')->nullOnDelete();
            $table->foreignId('customer_id')->nullable()->constrained('customers')->nullOnDelete();
            $table->timestamp('issued_at')->nullable();
            $table->json('design_data')->nullable();
            $table->json('meta')->nullable();
            $table->timestamps();
            $table->index('issued_at');
        });
    }

    public function down(): void { Schema::dropIfExists('certificates'); }
};
""")

write_file("database/migrations/2026_09_16_000005_create_integrations_table.php", r"""
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('integrations', function (Blueprint $table) {
            $table->id();
            $table->string('key')->unique();
            $table->string('name');
            $table->string('base_url')->nullable();
            $table->text('consumer_key')->nullable();
            $table->text('consumer_secret')->nullable();
            $table->boolean('is_active')->default(false);
            $table->timestamp('last_sync_at')->nullable();
            $table->json('sync_stats')->nullable();
            $table->json('settings')->nullable();
            $table->timestamps();
        });
    }

    public function down(): void { Schema::dropIfExists('integrations'); }
};
""")

write_file("database/migrations/2026_09_16_000006_create_app_notifications_table.php", r"""
<?php

use Illuminate\Database\Migrations\Migration;
use Illuminate\Database\Schema\Blueprint;
use Illuminate\Support\Facades\Schema;

return new class extends Migration {
    public function up(): void
    {
        Schema::create('app_notifications', function (Blueprint $table) {
            $table->id();
            $table->foreignId('user_id')->constrained('users')->cascadeOnDelete();
            $table->string('type')->default('info');
            $table->string('title');
            $table->text('message');
            $table->string('icon')->default('🔔');
            $table->string('url')->nullable();
            $table->boolean('is_read')->default(false);
            $table->json('data')->nullable();
            $table->timestamps();
            $table->index(['user_id', 'is_read']);
        });
    }

    public function down(): void { Schema::dropIfExists('app_notifications'); }
};
""")

# =========================================================
# ۳. Seeder ها
# =========================================================
print()
print("📦 Seeder ها...")

write_file("database/seeders/RoleAndUserSeeder.php", r"""
<?php

namespace Database\Seeders;

use App\Models\User;
use Illuminate\Database\Seeder;
use Illuminate\Support\Facades\Hash;
use Spatie\Permission\Models\Permission;
use Spatie\Permission\Models\Role;

class RoleAndUserSeeder extends Seeder
{
    public function run(): void
    {
        app()[\Spatie\Permission\PermissionRegistrar::class]->forgetCachedPermissions();

        $permissions = [
            'orders.view', 'orders.create', 'orders.edit', 'orders.delete', 'orders.status', 'orders.export',
            'customers.view', 'customers.create', 'customers.edit', 'customers.delete',
            'certificates.view', 'certificates.create', 'certificates.design', 'certificates.print',
            'settings.view', 'settings.edit', 'users.view', 'users.edit', 'reports.view',
        ];

        foreach ($permissions as $perm) {
            Permission::firstOrCreate(['name' => $perm]);
        }

        $superAdmin = Role::firstOrCreate(['name' => 'super-admin']);
        $superAdmin->syncPermissions(Permission::all());

        $manager = Role::firstOrCreate(['name' => 'manager']);
        $manager->syncPermissions([
            'orders.view', 'orders.create', 'orders.edit', 'orders.status', 'orders.export',
            'customers.view', 'customers.create', 'customers.edit',
            'certificates.view', 'certificates.print', 'reports.view',
        ]);

        $sales = Role::firstOrCreate(['name' => 'sales']);
        $sales->syncPermissions([
            'orders.view', 'orders.create', 'orders.edit', 'orders.status',
            'customers.view', 'customers.create', 'customers.edit',
        ]);

        $viewer = Role::firstOrCreate(['name' => 'viewer']);
        $viewer->syncPermissions(['orders.view', 'customers.view', 'certificates.view', 'reports.view']);

        $admin = User::firstOrCreate(
            ['email' => 'admin@shopgun.local'],
            ['name' => 'مدیر سیستم', 'password' => Hash::make('admin1234')]
        );
        $admin->syncRoles([$superAdmin]);

        $salesUser = User::firstOrCreate(
            ['email' => 'sales@shopgun.local'],
            ['name' => 'فروشنده نمونه', 'password' => Hash::make('sales1234')]
        );
        $salesUser->syncRoles([$sales]);

        $this->command->info('✅ کاربران: admin@shopgun.local/admin1234 · sales@shopgun.local/sales1234');
    }
}
""")

write_file("database/seeders/ChannelSeeder.php", r"""
<?php

namespace Database\Seeders;

use App\Models\Channel;
use Illuminate\Database\Seeder;

class ChannelSeeder extends Seeder
{
    public function run(): void
    {
        $channels = [
            ['key' => 'website',   'name' => 'سایت',       'icon' => '🌐', 'color' => '#1a5276'],
            ['key' => 'instagram', 'name' => 'اینستاگرام', 'icon' => '📷', 'color' => '#e91e63'],
            ['key' => 'telegram',  'name' => 'تلگرام',     'icon' => '✈️', 'color' => '#29b6f6'],
            ['key' => 'phone',     'name' => 'تلفنی',      'icon' => '📞', 'color' => '#66bb6a'],
            ['key' => 'direct',    'name' => 'حضوری',      'icon' => '🤝', 'color' => '#ffb74d'],
            ['key' => 'basalam',   'name' => 'باسلام',     'icon' => '🛍️', 'color' => '#00b894'],
        ];

        foreach ($channels as $i => $c) {
            Channel::updateOrCreate(
                ['key' => $c['key']],
                array_merge($c, ['sort_order' => $i, 'is_active' => true])
            );
        }
    }
}
""")

write_file("database/seeders/SampleDataSeeder.php", r"""
<?php

namespace Database\Seeders;

use App\Models\Channel;
use App\Models\Customer;
use App\Models\Order;
use Illuminate\Database\Seeder;

class SampleDataSeeder extends Seeder
{
    public function run(): void
    {
        $channels = Channel::all();

        if ($channels->isEmpty()) {
            $this->call(ChannelSeeder::class);
            $channels = Channel::all();
        }

        $customers = [
            ['name' => 'علی رضایی',    'phone' => '09151234567', 'postal_code' => '9317613441', 'address' => 'نیشابور - خیابان امام - پلاک ۱۲'],
            ['name' => 'مریم احمدی',   'phone' => '09121234567', 'postal_code' => '9317613442', 'address' => 'مشهد - بلوار وکیل‌آباد - پلاک ۴۵'],
            ['name' => 'حسن موسوی',    'phone' => '09131234567', 'postal_code' => '9317613443', 'address' => 'تهران - خیابان ولیعصر - پلاک ۷۸'],
            ['name' => 'فاطمه کریمی',  'phone' => '09141234567', 'postal_code' => '9317613444', 'address' => 'اصفهان - چهارباغ - پلاک ۹۰'],
            ['name' => 'رضا نوری',     'phone' => '09151234568', 'postal_code' => '9317613445', 'address' => 'شیراز - بلوار زند - پلاک ۲۳'],
        ];

        $customerModels = [];
        foreach ($customers as $data) {
            $customerModels[] = Customer::updateOrCreate(['phone' => $data['phone']], $data);
        }

        $statuses = ['pending', 'final-check', 'courier'];

        for ($i = 1; $i <= 30; $i++) {
            $customer = $customerModels[array_rand($customerModels)];
            $channel  = $channels->random();

            Order::create([
                'order_number' => (string) (317400 + $i),
                'customer_id'  => $customer->id,
                'channel_id'   => $channel->id,
                'status'       => $statuses[array_rand($statuses)],
                'amount'       => rand(500000, 20000000),
                'insurance'    => rand(500, 5000),
                'phone'        => $customer->phone,
                'address'      => $customer->address,
                'postal_code'  => $customer->postal_code,
            ]);
        }

        $this->command->info('✅ ۵ مشتری و ۳۰ سفارش نمونه ساخته شد.');
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
            SampleDataSeeder::class,
        ]);
    }
}
""")

# =========================================================
# ۴. Observer
# =========================================================
print()
print("📦 Observer و Provider...")

write_file("app/Observers/OrderObserver.php", r"""
<?php

namespace App\Observers;

use App\Models\AppNotification;
use App\Models\Order;

class OrderObserver
{
    public function created(Order $order): void
    {
        AppNotification::broadcast(
            type: 'order_created',
            title: "سفارش جدید #{$order->order_number}",
            message: ($order->customer?->name ?? 'مشتری') . ' — ' . number_format((float) $order->amount),
            icon: '📦',
            url: route('orders.show', $order),
            data: ['order_id' => $order->id],
        );
    }

    public function updated(Order $order): void
    {
        if ($order->wasChanged('status')) {
            AppNotification::broadcast(
                type: 'order_status',
                title: "تغییر وضعیت سفارش #{$order->order_number}",
                message: 'وضعیت جدید: ' . $order->status_label,
                icon: '🔄',
                url: route('orders.show', $order),
                data: ['order_id' => $order->id],
            );
        }
    }
}
""")

write_file("app/Providers/AppServiceProvider.php", r"""
<?php

namespace App\Providers;

use App\Models\Order;
use App\Observers\OrderObserver;
use Illuminate\Support\ServiceProvider;

class AppServiceProvider extends ServiceProvider
{
    public function register(): void {}

    public function boot(): void
    {
        Order::observe(OrderObserver::class);
    }
}
""")

# =========================================================
# ۵. Exports
# =========================================================
print()
print("📦 Export...")

write_file("app/Exports/OrdersExport.php", r"""
<?php

namespace App\Exports;

use App\Models\Order;
use Maatwebsite\Excel\Concerns\FromCollection;
use Maatwebsite\Excel\Concerns\WithHeadings;
use Maatwebsite\Excel\Concerns\WithMapping;
use Maatwebsite\Excel\Concerns\ShouldAutoSize;

class OrdersExport implements FromCollection, WithHeadings, WithMapping, ShouldAutoSize
{
    public function __construct(
        protected string $search = '',
        protected string $statusFilter = '',
        protected string $channelFilter = ''
    ) {}

    public function collection()
    {
        return Order::with(['customer', 'channel'])
            ->when($this->search, function ($q) {
                $q->where(function ($qq) {
                    $qq->where('order_number', 'like', "%{$this->search}%")
                       ->orWhere('phone', 'like', "%{$this->search}%")
                       ->orWhereHas('customer', fn ($cq) => $cq->where('name', 'like', "%{$this->search}%"));
                });
            })
            ->when($this->statusFilter, fn ($q) => $q->where('status', $this->statusFilter))
            ->when($this->channelFilter, fn ($q) => $q->where('channel_id', $this->channelFilter))
            ->latest('id')
            ->get();
    }

    public function headings(): array
    {
        return ['شماره سفارش', 'مشتری', 'تلفن', 'کدپستی', 'آدرس', 'وضعیت', 'کانال', 'بیمه', 'مبلغ', 'تاریخ'];
    }

    public function map($order): array
    {
        return [
            $order->order_number,
            $order->customer?->name ?? '',
            $order->phone,
            $order->postal_code,
            $order->address,
            $order->status_label,
            $order->channel?->name ?? '',
            $order->insurance,
            $order->amount,
            $order->created_at?->format('Y/m/d H:i'),
        ];
    }
}
""")

print()
print("═" * 60)
print("✅ مرحله ۱ کامل شد — مدل‌ها، مایگریشن‌ها، Seederها، Observer، Export")
print("═" * 60)
print()
print("📌 دستورات بعدی:")
print()
print("   cd ~/projects/shopgun-v2.1")
print("   php artisan optimize:clear")
print("   php artisan migrate:fresh --seed --force")
print()
print("⚠️ بعد از اجرا، مرحله ۲ (کامپوننت‌ها و ویوها) رو اجرا کن.")
print()
