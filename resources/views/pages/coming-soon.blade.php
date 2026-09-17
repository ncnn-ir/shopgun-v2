@extends('components.layouts.app')

@section('content')
<div class="p-6 text-center">
    <div class="text-6xl mb-4">🚧</div>
    <h1 class="text-2xl font-bold mb-2">{{ $title ?? 'این صفحه' }}</h1>
    <p class="text-base-content/60">به زودی فعال می‌شود</p>
    <a href="{{ url()->previous() }}" class="btn btn-primary btn-sm mt-6">→ بازگشت</a>
</div>
@endsection
