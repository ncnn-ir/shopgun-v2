<?php

namespace App\Infrastructure\WooCommerce;

use App\Models\AppSetting;
use App\Models\ApiLog;
use Illuminate\Http\Client\PendingRequest;
use Illuminate\Http\Client\Response;
use Illuminate\Support\Facades\Http;
use Illuminate\Support\Facades\Log;

/**
 * ★ WooCommerceClient
 * دروازه واحد به WooCommerce REST API
 *
 * همه سرویس‌ها و کامپوننت‌ها باید از همین کلاس استفاده کنند
 * نه اینکه خودشان HTTP بزنند.
 */
class WooCommerceClient
{
    protected string $baseUrl;
    protected string $wpBase;
    protected string $consumerKey;
    protected string $consumerSecret;
    protected int $defaultTimeout = 45;
    protected int $connectTimeout = 15;
    protected int $defaultRetry = 2;
    protected string $module = 'unknown';

    public function __construct(?array $auth = null)
    {
        if ($auth === null) {
            $url = trim((string) AppSetting::get('commerce_url', ''));
            $key = trim((string) AppSetting::get('commerce_key', ''));
            $secret = trim((string) AppSetting::get('commerce_secret', ''));

            if (!$url || !$key || !$secret) {
                throw new \RuntimeException('تنظیمات کامرس کامل نیست');
            }

            $base = rtrim($url, '/');
            if (!str_contains($base, '/wp-json')) {
                $base .= '/wp-json/wc/v3';
            }

            $auth = [
                'base' => $base,
                'wp_base' => preg_replace('#/wc/v3$#', '', $base),
                'key' => $key,
                'secret' => $secret,
                'site' => rtrim($url, '/'),
            ];
        }

        $this->baseUrl = $auth['base'];
        $this->wpBase = $auth['wp_base'];
        $this->consumerKey = $auth['key'];
        $this->consumerSecret = $auth['secret'];
    }

    /**
     * تعیین ماژول برای لاگ
     */
    public function module(string $name): self
    {
        $this->module = $name;
        return $this;
    }

    /**
     * تنظیمات زمان‌بندی
     */
    public function timeout(int $seconds): self
    {
        $this->defaultTimeout = $seconds;
        return $this;
    }

    public function retry(int $times): self
    {
        $this->defaultRetry = $times;
        return $this;
    }

    // ═══════════════════════════════════════════════════════════
    // Core request با telemetry
    // ═══════════════════════════════════════════════════════════
    public function request(
        string $method,
        string $endpoint,
        array $data = [],
        array $query = []
    ): array {
        $url = $this->baseUrl . '/' . ltrim($endpoint, '/');
        if (!empty($query)) {
            $url .= '?' . http_build_query($query);
        }

        $start = microtime(true);
        $requestId = uniqid('woo_', true);

        $status = null;
        $error = null;
        $body = null;
        $attempts = 0;

        try {
            $client = Http::withBasicAuth($this->consumerKey, $this->consumerSecret)
                ->timeout($this->defaultTimeout)
                ->connectTimeout($this->connectTimeout)
                ->acceptJson();

            // Retry فقط برای خطاهای گذرا
            if ($this->defaultRetry > 0 && in_array($method, ['GET', 'POST', 'PUT'])) {
                $client = $client->retry($this->defaultRetry, 1500, function ($exception) {
                    // فقط روی timeouts و 5xx و 429
                    if ($exception instanceof \Illuminate\Http\Client\ConnectionException) {
                        return true;
                    }
                    return false;
                }, throw: false);
            }

            $response = match (strtoupper($method)) {
                'GET' => $client->get($url),
                'POST' => $client->post($url, $data),
                'PUT' => $client->put($url, $data),
                'DELETE' => $client->delete($url, $data),
                default => throw new \InvalidArgumentException("Method {$method} پشتیبانی نمی‌شود"),
            };

            $status = $response->status();
            $body = $response->json() ?? $response->body();

            // ثبت در ApiLog
            $this->logRequest($requestId, $method, $url, $data, $status, $body, $start, null);

            if (!$response->successful()) {
                return [
                    'ok' => false,
                    'status' => $status,
                    'body' => $body,
                    'error' => "HTTP {$status}",
                ];
            }

            return [
                'ok' => true,
                'status' => $status,
                'body' => $body,
            ];

        } catch (\Throwable $e) {
            $error = $e->getMessage();
            $duration = (int) round((microtime(true) - $start) * 1000);

            $this->logRequest($requestId, $method, $url, $data, $status, null, $start, $error);

            return [
                'ok' => false,
                'status' => $status,
                'error' => $error,
                'body' => null,
            ];
        }
    }

    protected function logRequest(
        string $requestId,
        string $method,
        string $url,
        array $request,
        ?int $status,
        $response,
        float $start,
        ?string $error
    ): void {
        try {
            ApiLog::record([
                'service' => 'woocommerce',
                'method' => strtoupper($method),
                'url' => mb_substr($url, 0, 900),
                'status_code' => $status,
                'duration_ms' => (int) round((microtime(true) - $start) * 1000),
                'request_body' => !empty($request) ? mb_substr(json_encode($request, JSON_UNESCAPED_UNICODE), 0, 3000) : null,
                'response_body' => $response ? mb_substr(is_string($response) ? $response : json_encode($response, JSON_UNESCAPED_UNICODE), 0, 5000) : null,
                'error' => $error,
            ]);
        } catch (\Throwable $e) {
            Log::warning('ApiLog failed: ' . $e->getMessage());
        }
    }

    // ═══════════════════════════════════════════════════════════
    // APIهای کاربردی
    // ═══════════════════════════════════════════════════════════

    public function testConnection(): array
    {
        return $this->request('GET', 'products', [], ['per_page' => 1]);
    }

    public function products(array $query = []): array
    {
        return $this->request('GET', 'products', [], $query);
    }

    public function product(int $id): array
    {
        return $this->request('GET', "products/{$id}");
    }

    public function productBySku(string $sku): array
    {
        return $this->request('GET', 'products', [], ['sku' => $sku, 'per_page' => 1]);
    }

    public function batchProducts(array $payload): array
    {
        return $this->request('POST', 'products/batch', $payload);
    }

    public function orders(array $query = []): array
    {
        return $this->request('GET', 'orders', [], $query);
    }

    public function customers(array $query = []): array
    {
        return $this->request('GET', 'customers', [], $query);
    }

    public function categories(array $query = []): array
    {
        return $this->request('GET', 'products/categories', [], $query);
    }

    public function attributes(): array
    {
        return $this->request('GET', 'products/attributes');
    }

    public function attributeTerms(int $attrId): array
    {
        return $this->request('GET', "products/attributes/{$attrId}/terms", [], ['per_page' => 100]);
    }

    public function users(): array
    {
        // از wp/v2
        $url = $this->wpBase . '/wp/v2/users';
        try {
            $r = Http::withBasicAuth($this->consumerKey, $this->consumerSecret)
                ->timeout($this->defaultTimeout)
                ->get($url);
            if ($r->successful()) {
                return ['ok' => true, 'body' => $r->json()];
            }
            return ['ok' => false, 'error' => "HTTP {$r->status()}"];
        } catch (\Throwable $e) {
            return ['ok' => false, 'error' => $e->getMessage()];
        }
    }

    public function mediaSearch(string $filename): array
    {
        $url = $this->wpBase . '/wp/v2/media';
        try {
            $r = Http::withBasicAuth($this->consumerKey, $this->consumerSecret)
                ->timeout($this->defaultTimeout)
                ->get($url, ['search' => $filename, 'per_page' => 5]);
            if ($r->successful()) {
                return ['ok' => true, 'body' => $r->json()];
            }
            return ['ok' => false, 'error' => "HTTP {$r->status()}"];
        } catch (\Throwable $e) {
            return ['ok' => false, 'error' => $e->getMessage()];
        }
    }


    /**
     * لیست Media از wp/v2/media
     */
    public function mediaList(int $perPage = 100, int $page = 1): array
    {
        $url = $this->wpBase . '/wp/v2/media';
        try {
            $r = Http::withBasicAuth($this->consumerKey, $this->consumerSecret)
                ->timeout($this->defaultTimeout)
                ->connectTimeout($this->connectTimeout)
                ->get($url, [
                    'per_page' => $perPage,
                    'page' => $page,
                    'media_type' => 'image',
                ]);

            if ($r->successful()) {
                return ['ok' => true, 'body' => $r->json()];
            }
            return ['ok' => false, 'error' => "HTTP {$r->status()}"];
        } catch (\Throwable $e) {
            return ['ok' => false, 'error' => $e->getMessage()];
        }
    }

    public function mediaFindByFilename(string $filename): array
    {
        $url = $this->wpBase . '/wp/v2/media';
        try {
            $r = Http::withBasicAuth($this->consumerKey, $this->consumerSecret)
                ->timeout(15)
                ->get($url, ['search' => $filename, 'per_page' => 5]);

            if ($r->successful()) {
                return ['ok' => true, 'body' => $r->json()];
            }
            return ['ok' => false, 'error' => "HTTP {$r->status()}"];
        } catch (\Throwable $e) {
            return ['ok' => false, 'error' => $e->getMessage()];
        }
    }

    public function getSiteUrl(): string
    {
        return rtrim((string) AppSetting::get('commerce_url', ''), '/');
    }
}
