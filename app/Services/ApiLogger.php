<?php

namespace App\Services;

use App\Models\ApiLog;
use Illuminate\Support\Facades\Http;

class ApiLogger
{
    /**
     * درخواست HTTP با لاگ‌گیری خودکار
     */
    public static function request(string $service, string $method, string $url, array $options = []): ?array
    {
        $start = microtime(true);

        $log = [
            'service'  => $service,
            'method'   => strtoupper($method),
            'url'      => mb_substr($url, 0, 1000),
            'request_body' => isset($options['json']) ? json_encode($options['json'], JSON_UNESCAPED_UNICODE) : null,
        ];

        try {
            $client = Http::timeout($options['timeout'] ?? 60)
                ->withOptions($options['withOptions'] ?? []);

            if (!empty($options['basic_auth'])) {
                $client = $client->withBasicAuth(...$options['basic_auth']);
            }
            if (!empty($options['headers'])) {
                $client = $client->withHeaders($options['headers']);
            }

            $response = $client->{strtolower($method)}($url, $options['json'] ?? $options['body'] ?? []);

            $duration = (int) round((microtime(true) - $start) * 1000);
            $body = $response->body();

            $itemsCount = null;
            $decoded = json_decode($body, true);
            if (is_array($decoded)) {
                if (isset($decoded[0])) $itemsCount = count($decoded);
            }

            ApiLog::record(array_merge($log, [
                'status_code'  => $response->status(),
                'duration_ms'  => $duration,
                'response_body' => mb_substr($body, 0, 5000),
                'items_count'  => $itemsCount,
            ]));

            return [
                'ok'     => $response->successful(),
                'status' => $response->status(),
                'body'   => $body,
                'json'   => $decoded,
                'ms'     => $duration,
            ];
        } catch (\Throwable $e) {
            $duration = (int) round((microtime(true) - $start) * 1000);

            ApiLog::record(array_merge($log, [
                'duration_ms' => $duration,
                'error'       => $e->getMessage(),
            ]));

            return [
                'ok'    => false,
                'error' => $e->getMessage(),
                'ms'    => $duration,
            ];
        }
    }

    /**
     * لاگ ساده (بدون درخواست)
     */
    public static function log(string $service, string $message, ?string $error = null): void
    {
        ApiLog::record([
            'service'       => $service,
            'method'        => 'LOG',
            'url'           => mb_substr($message, 0, 500),
            'response_body' => $error,
        ]);
    }
}
