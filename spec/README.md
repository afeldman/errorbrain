# ErrorBrain Specification

**The canonical source of truth for all SDKs and Server contracts.**

## Schemas

- **error_event.schema.json** - Complete error event format with source and evidence
- **source.schema.json** - Application/service metadata
- **evidence.schema.json** - Additional context items (logs, metrics, HTTP, etc.)

## Version Management

All breaking changes to these schemas require a MAJOR version bump across all SDKs.

## Usage

### Validation

Use these schemas to validate error events in SDKs and Server:

```bash
# Using jsonschema CLI
jsonschema -i error_event.json error_event.schema.json
```

### Code Generation

SDKs should generate strongly-typed models from these schemas to ensure consistency.

## Contract Rules

1. **SDKs follow spec, never deviate**
2. **Server API strictly validates against spec**
3. **Breaking changes to spec require coordinated SDK releases**
4. **Backward compatibility preferred** (use deprecation fields instead of removal)
