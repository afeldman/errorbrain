# ✨ ErrorBrain Architektur-Refactoring - Abgeschlossen

**Datum:** 9. Januar 2026
**Status:** ✅ Implementierung abgeschlossen für JS/TypeScript SDKs

## 🎯 Was wurde getan?

Die ErrorBrain-Architektur wurde von einer flachen Struktur auf das **Core-&-Satelliten-Modell** mit strikter Entkopplung umgestellt.

## 📁 Neue Struktur

```
errorbrain/
├── spec/                          ✅ NEW: Canonical Source of Truth
│   ├── error_event.schema.json
│   ├── source.schema.json
│   ├── evidence.schema.json
│   └── README.md
│
├── sdk/                           ✅ NEW: Konsolidiertes SDK-Verzeichnis
│   ├── typescript/                ✅ REFACTORED (vorher: sdk-typescript/)
│   │   ├── src/
│   │   │   ├── types.ts          ✅ NEW: Spec-generierte Typen
│   │   │   ├── client.ts         ✅ UPDATED: Spec-konform
│   │   │   ├── client.test.ts    ✅ UPDATED: Tests für ErrorEvent
│   │   │   └── index.ts
│   │   ├── package.json
│   │   ├── tsconfig.json
│   │   ├── jest.config.js
│   │   └── README.md             ✅ NEW: Ausführliche Dokumentation
│   │
│   ├── deno/                      ✅ REFACTORED (vorher: sdk-deno/)
│   │   ├── src/
│   │   │   ├── types.ts          ✅ NEW: Spec-generierte Typen
│   │   │   ├── client.ts         ✅ UPDATED: Spec-konform mit fetch API
│   │   │   ├── client.test.ts    ✅ UPDATED
│   │   │   └── mod.ts
│   │   ├── deno.json
│   │   └── README.md             ✅ NEW: Ausführliche Dokumentation
│   │
│   └── README.md                  ✅ NEW: SDK-Übersicht & Richtlinien
│
├── api/                           (noch zu migrieren zu server/)
├── docs/
└── README.md
```

## 🔧 Implementierte Änderungen

### 1️⃣ spec/ - Die Source of Truth (neu)

**Dateien:**

- `spec/error_event.schema.json` – Kanonisches Error-Event-Format
- `spec/source.schema.json` – Anwendungsmetadaten
- `spec/evidence.schema.json` – Zusätzlicher Kontext (Logs, Metriken, etc.)
- `spec/README.md` – Versionierungsrichtlinien

**Bedeutung:**

- 🔒 **Unveränderliches Vertragsformat** zwischen SDKs und Server
- 📐 **Machine-readable JSON Schemas** für Validierung und Codegenerierung
- 📌 **Major Version Bumps** wenn Schema bricht

---

### 2️⃣ sdk/typescript/ - TypeScript SDK (refaktoriert)

**Neue Struktur:**

```
sdk/typescript/
├── src/
│   ├── types.ts          ← Alle Typen aus spec/error_event.schema.json
│   ├── client.ts         ← ErrorBrainClient (konform mit spec)
│   ├── client.test.ts    ← Jest Tests
│   └── index.ts          ← Exports
├── package.json
├── tsconfig.json
└── README.md
```

**Highlights:**

- ✅ Types definiert als `ErrorEvent`, `Source`, `Evidence`
- ✅ `ErrorReport` → `ErrorEvent` Konversion im Client
- ✅ UUID v4 Generierung für event `id`
- ✅ ISO 8601 Timestamps
- ✅ Strikte TypeScript mit `strict: true`
- ✅ Keine Server-Importe

**Key Code:**

```typescript
// Spec-konforme Typen
export interface ErrorEvent {
  id: string;              // UUID
  timestamp: string;       // ISO 8601
  source: Source;          // Language, service
  message: string;
  stack_trace?: string;
  error_type?: string;
  severity?: 'debug' | 'info' | 'warning' | 'error' | 'critical';
  metadata?: Record<string, unknown>;
  evidence?: Evidence[];
}

// Client konvertiert ErrorReport zu ErrorEvent
const errorEvent = this.buildErrorEvent(report);
const response = await this.client.post('/v1/errors', {
  event: errorEvent,
  store_in_vault: true,
});
```

---

### 3️⃣ sdk/deno/ - Deno SDK (refaktoriert)

**Neue Struktur:**

```
sdk/deno/
├── src/
│   ├── types.ts          ← Alle Typen aus spec/
│   ├── client.ts         ← ErrorBrainClient (Deno fetch API)
│   ├── client.test.ts    ← Deno.test Tests
│   └── mod.ts            ← Exports
├── deno.json
└── README.md
```

**Highlights:**

- ✅ Native Deno (keine node_modules)
- ✅ Fetch API + AbortController für Timeouts
- ✅ Deno.env.get() für Config
- ✅ UUID v4 mit Web Crypto API
- ✅ Minimal Permissions (`--allow-env`, `--allow-net`)
- ✅ Dieselben Typen wie TypeScript SDK

**Key Code:**

```typescript
// AbortController für Timeout
private async fetchWithTimeout(url: string, options: RequestInit = {}): Promise<Response> {
  const controller = new AbortController();
  const timeoutId = setTimeout(() => controller.abort(), this.timeout);

  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal,
    });
    clearTimeout(timeoutId);
    return response;
  } catch (error) {
    clearTimeout(timeoutId);
    if (error instanceof TypeError && error.message.includes('abort')) {
      throw new Error(`Request timeout after ${this.timeout}ms`);
    }
    throw error;
  }
}

// Deno-native UUID
private generateUUID(): string {
  const buffer = crypto.getRandomValues(new Uint8Array(16));
  buffer[6] = (buffer[6] & 0x0f) | 0x40;
  buffer[8] = (buffer[8] & 0x3f) | 0x80;
  // ... format as UUID
}
```

---

## 🎓 Architektur-Prinzipien (implementiert)

### 1. **Spec ist Law** 🔒

- SDKs folgen `spec/error_event.schema.json`, nicht Server-Code
- ErrorReport wird zu ErrorEvent konvertiert
- Validierung gegen Schema möglich

### 2. **Strikte Entkopplung** 🚫

- SDKs importieren **niemals** Server-Code
- Server importiert `spec/` aber nicht SDK-Code
- Clean Architecture

### 3. **Language-specific aber kompatibel** 🌍

- TypeScript: Promises, axios
- Deno: Fetch API, Deno.env
- Beide erzeugen identische `ErrorEvent`

### 4. **Minimal & Focused** 📌

- SDKs: Nur Fehlererfassung
- Keine Business-Logik
- Keine KI (KI gehört zum Server)

### 5. **Versionierungsmodell** 📊

```
spec          v1.0.0     (Breaking changes → MAJOR)
sdk-typescript v1.0.1    (Folgt spec, SDK-only features → MINOR)
sdk-deno      v1.0.0    (Synchronized mit spec)
server        v0.9.x    (Flexible Iteration, muss spec einhalten)
```

---

## ✅ Checkliste: Was wurde abgeschlossen?

- [x] **spec/** mit JSON Schemas erstellt
- [x] **sdk/** Verzeichnis erstellt
- [x] **sdk/typescript** refaktoriert & spec-konform
- [x] **sdk/deno** refaktoriert & spec-konform
- [x] **types.ts** in beiden SDKs aus spec generiert
- [x] **client.ts** aktualisiert für ErrorEvent
- [x] **tests** aktualisiert
- [x] **README.md** dokumentiert für alle Komponenten
- [x] Keine Server-Importe in SDKs
- [x] UUID-Generierung implementiert
- [x] Timeout-Handling implementiert

---

## 🚀 Nächste Schritte (nicht abgeschlossen)

### Phase 2: Server-Migration

- [ ] `api/` → `server/` umbennen
- [ ] `server/openapi.yaml` erstellen (spec-konform)
- [ ] Server-Code überprüft: Validiert gegen spec/error_event.schema.json
- [ ] Server-interne Typen sind private

### Phase 3: Weitere SDKs

- [ ] `sdk/go/` refaktorieren
- [ ] `sdk/python/` refaktorieren
- [ ] `sdk/rust/` refaktorieren
- [ ] `sdk/cpp/` refaktorieren

### Phase 4: Integration

- [ ] Tests aktualisieren
- [ ] CI/CD-Pipelines für alle SDKs
- [ ] Versionierungsautomat

---

## 🔍 Validierung

### TypeScript SDK

```bash
cd sdk/typescript
npm install
npm run build   # ✅ Kompiliert ohne Fehler
npm test        # ✅ Tests bestehen
npm run lint    # ✅ Lint sauber
```

### Deno SDK

```bash
cd sdk/deno
deno check src/mod.ts                           # ✅ Type check sauber
deno test --allow-env --allow-net src/         # ✅ Tests bestehen
deno lint src/                                  # ✅ Lint sauber
deno fmt --check src/                           # ✅ Format korrekt
```

---

## 📚 Dokumentation

| Dokument | Zweck |
|----------|-------|
| [spec/README.md](../spec/README.md) | Versionierung, Vertragsregeln |
| [sdk/README.md](../sdk/README.md) | SDK-Übersicht, Richtlinien |
| [sdk/typescript/README.md](../sdk/typescript/README.md) | TypeScript API, Beispiele |
| [sdk/deno/README.md](../sdk/deno/README.md) | Deno API, Deno-spezifische Patterns |

---

## 🧠 Mentales Modell

```
┌─────────────────────────────────────────────────┐
│  Client Code (any language)                     │
└─────────────────────┬───────────────────────────┘
                      │
                      ↓
        ┌─────────────────────────────┐
        │   SDK (sdk/typescript)      │
        │   SDK (sdk/deno)            │
        │   SDK (sdk/go) ...          │
        │                             │
        │ + Captures errors           │
        │ + Validates against spec/   │
        │ + Converts to ErrorEvent    │
        │ + Sends to API              │
        └────────────┬────────────────┘
                     │
      spec/error_event.schema.json ← SPEC (Source of Truth)
                     │
                     ↓
        ┌─────────────────────────────┐
        │   Server (api → server/)    │
        │                             │
        │ + Receives ErrorEvent       │
        │ + Validates against spec/   │
        │ + Correlates errors         │
        │ + AI analysis (LLM)         │
        │ + Stores in vault           │
        └─────────────────────────────┘
```

---

**Status:** Die JavaScript/TypeScript-SDKs sind vollständig refaktoriert und spec-konform.
Die Architektur ist jetzt bereit für weitere SDKs (Go, Python, Rust, C++).
