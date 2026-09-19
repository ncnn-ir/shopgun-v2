<?php

namespace App\Models;

use Illuminate\Database\Eloquent\Model;

class WooUser extends Model
{
    protected $table = 'woo_users';

    protected $fillable = ['woo_id', 'name', 'slug', 'email', 'roles', 'synced_at'];
    protected $casts = ['roles' => 'array', 'synced_at' => 'datetime'];
}
