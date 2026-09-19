<?php

namespace App\Http\Controllers;

use App\Models\Order;
use Illuminate\Http\Request;

class OrderChannelController extends Controller
{
    public function update(Request $request, Order $order)
    {
        $data = $request->validate([
            'sales_channel' => 'nullable|string|max:64',
        ]);

        $order->sales_channel = $data['sales_channel'] ?? null;
        $order->save();

        return response()->json(['ok' => true, 'channel' => $order->sales_channel]);
    }
}
