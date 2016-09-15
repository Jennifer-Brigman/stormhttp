### 0.0.27 - Development

- **FEATURE** Added better compliance to WebSocket RFC.
- **FEATURE** Remove cryptography module and replace with fernet module.

### 0.0.26 - Stable - September 14th, 2016

- **FEATURE** Added WebSocket support for versions 7, 8, and 13.
- **FEATURE** Move `match_info` attribute to `HttpUrl`.
- **SPEEDUP** Optimizations to `Server.route_request()`

#### 0.0.25 - September 11th, 2016

- **FEATURE** Add support for server-side `Sessions`.
- **FEATURE** Add simple and encrypted `SessionStorage` implementations.
- **FEATURE** Add abstract class for server-side `Sessions` that must be fetched. (Redis, etc)
- **BUG-FIX** Fix `TemplateMiddleware` rendering without requiring a certain order.

#### 0.0.24 - September 8th, 2016

- **FEATURE** Add `TemplateMiddleware` for dynamic html templating.
- **FEATURE** Add `CacheControlMiddleware` for controlling caching behaviour.
- **SPEEDUP** Optimizations to HTTP primitives and `HttpParser`.
