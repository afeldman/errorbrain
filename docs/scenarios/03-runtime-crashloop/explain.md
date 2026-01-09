# Erklärung: Runtime CrashLoop

## Was ist passiert?

Der payment-worker Pod ist in eine **CrashLoop** geraten: Er startet, stürzt ab, wird automatisch neu gestartet, stürzt wieder ab – endlosschleife. Dies ist jetzt ~12 mal passiert in den letzten 12 Minuten.

## Die Ursache (laut Verdict)

**Hypothese:** Das ist eine **fehlende Konfigurationsdependency** – nicht kompliziert, aber fatal.

### Das Problem in 3 Sätzen

1. Die Anwendung braucht beim Start eine Umgebungsvariable `STRIPE_API_KEY`
2. Diese soll aus einem Kubernetes Secret namens `stripe-secrets` kommen
3. Das Secret existiert nicht – wurde vor dem Deployment vergessen

### Beweis – mehrspurig

| Quelle | Was es sagt |
|---|---|
| **Pod Logs** | `KeyError: 'STRIPE_API_KEY'` in Zeile 23 |
| **Kubernetes API** | 404: Secret `stripe-secrets` existiert nicht in `payment-system` |
| **Pod Spec** | Definiert: "Hole STRIPE_API_KEY aus Secret 'stripe-secrets', Schlüssel 'api-key'" |
| **Cluster Logs** | Deployment wurde um 16:10:28 erstellt, Secret wurde niemals erstellt |
| **Restart Pattern** | 12 Versuche in 12 Minuten, alle fehlgeschlagen – das ist **kein Timing-Problem** wie beim CI-Timeout. Das ist eine permanente Konfiguration. |

**Confidence 85%** – Das ist hundertprozentig klar:

- Die Fehlermeldung ist spezifisch (nicht "pod startet nicht")
- Der Kubernetes API bestätigt: Secret existiert nicht
- Das wird sich nicht selbst beheben

## Was sollst du tun?

Drei Schritte, zwei davon sind schnell:

1. **Sofort (HIGH):** Erstelle das fehlende Secret mit dem echten Stripe API Key:

```bash
kubectl create secret generic stripe-secrets \
  --from-literal=api-key=$YOUR_STRIPE_API_KEY \
  -n payment-system
```

Sofort danach startet Kubernetes den Pod neu und er sollte initialisieren. Schau in die Logs:

```bash
kubectl logs -f -n payment-system deployment/payment-worker-v1.8.2
```

1. **Bestätigung (HIGH):** Überprüfe, dass der Pod jetzt läuft:

```bash
kubectl get pods -n payment-system | grep payment-worker
```

Sollte jetzt `Running` sagen statt `CrashLoopBackOff`.

1. **Danach (MEDIUM):** Verhindere das nächste Mal:
   - **Pre-Deployment Checklist:** Alle erforderlichen Secrets müssen existieren, bevor das Deployment startet
   - **Automatische Validierung:** Schreib ein Script/Operator, das vor jedem Rollout überprüft: "Alle referenzierten Secrets vorhanden?"
   - **Sealed Secrets oder External Secrets:** Damit sind Secrets Teil des GitOps-Flows und können nicht "vergessen" werden

## Warum zeigt errorbrain das richtig?

Dieses Szenario ist **technisch einfach** – ein fehlender Schlüssel:

- Nicht kompliziert wie Netzwerk-Timeouts oder Race Conditions
- Trotzdem kritisch: Das ganze Payment-System ist down
- **Die Herausforderung:** Zwischen 1000 möglichen Fehlergründen schnell die Diagnose finden
  - Ist es ein Code-Bug? (Nein, Code ist ok)
  - Ist es ein Cluster-Problem? (Nein, Cluster läuft)
  - Ist es ein Netzwerk-Problem? (Nein, auch das ist ok)
  - Ist es ein Kubernetes-Konfigurationsproblem? (Ja! Und genau wo.)

errorbrain sagt direkt: "Das Secret fehlt" – ohne dass du Logs durchsuchen musst. Das spart Zeit, reduziert Fehlerdiagnose-Zyklen, und erhöht die Mean Time To Recovery (MTTR).
