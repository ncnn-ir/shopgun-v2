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
