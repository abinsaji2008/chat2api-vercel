# Chat2API Vercel

Vercel-compatible adaptation of the core `lanqian528/chat2api` service.

## Endpoint

```
POST /v1/chat/completions
```

With `API_PREFIX=myapi`:

```
POST /myapi/v1/chat/completions
```

## Vercel environment variables

Required for a protected public API:

```env
API_PREFIX=
AUTHORIZATION=your-private-api-key
```

Provide ChatGPT web credentials either directly in the request `Authorization: Bearer ...` header, or configure a server-side token pool:

```env
CHATGPT_TOKENS=access_token_1,access_token_2
```

The upstream project accepts both ChatGPT AccessTokens and 45-character RefreshTokens. RefreshTokens are exchanged for AccessTokens automatically.

Optional:

```env
CHATGPT_BASE_URL=https://chatgpt.com
PROXY_URL=
SENTINEL_PROXY_URL=
EXPORT_PROXY_URL=
HISTORY_DISABLED=true
POW_DIFFICULTY=000032
RETRY_TIMES=3
CONVERSATION_ONLY=false
ENABLE_LIMIT=true
UPLOAD_BY_URL=false
CHECK_MODEL=false
SCHEDULED_REFRESH=false
RANDOM_TOKEN=true
OAI_LANGUAGE=en-US
AUTH_KEY=
TURNSTILE_SOLVER_URL=
ARK0SE_TOKEN_URL=
ENABLE_GATEWAY=false
AUTO_SEED=true
```

### Vercel-specific behavior

Because Vercel functions are ephemeral, runtime cache/state is stored under `/tmp/chat2api`. A durable token pool should therefore be supplied with `CHATGPT_TOKENS` rather than relying on files written by the `/tokens` endpoints.

Do not commit AccessTokens, RefreshTokens, cookies, or other credentials to GitHub.

## Postman

Headers:

```
Content-Type: application/json
Authorization: Bearer YOUR_API_TOKEN
```

Body:

```json
{
  "model": "gpt-4o",
  "messages": [
    {
      "role": "user",
      "content": "Hello"
    }
  ],
  "stream": false
}
```
