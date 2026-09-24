# Chat2API Vercel

Vercel adapter with optional ChatGPT browser-cookie authentication.

Set Vercel environment variables:

```env
AUTHORIZATION=your-private-api-key
API_PREFIX=optional-prefix
CHATGPT_COOKIES=your-cookie-header
ENABLE_GATEWAY=false
```

POST `/[API_PREFIX/]v1/chat/completions`
GET `/health`

Never commit real cookies or API keys.