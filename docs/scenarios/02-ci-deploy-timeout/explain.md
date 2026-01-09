# Erklärung: CI Deployment Timeout

## Was ist passiert?

Das Deployment für app-api-v2.3.0 hat sich nach 30 Minuten nicht vollständig durchgeführt. Nur 3 von 8 Replicas waren bereit.

## Die Ursache (laut Verdict)

**Hypothese:** Das Deployment ist durch einen **zeitlich zufälligen Konflikt** blockiert: Die Anwendung hängt von PostgreSQL ab, aber gerade während des Deployments läuft eine geplante Wartung auf der Datenbank.

### Das ist nicht einfach "Fehler"

1. **Das Deployment selbst ist richtig** – die Konfiguration, der Code, alles ist ok
2. **Die Datenbank-Wartung ist geplant und normal** – notwendig und erwartet
3. **Das Problem: Timing** – beides passiert gleichzeitig, und der Deployment-Job weiß nicht von der Wartung

### Beweise aus mehreren Quellen

| Zeitstempel | Was geschah | Wer sagt das |
|---|---|---|
| 15:30:00 | PostgreSQL Maintenance angekündigt, Port 5432 entfernt | Kubernetes Service |
| 15:35:22 | Wartung startet (5 min verspätet) | PostgreSQL Maintenance Pod |
| 15:40:00 | CI/CD Pipeline startet Deployment (unwissentlich während Wartung) | CI/CD Logs |
| 15:44:50 | postgres_up Metric fällt auf 0 | Prometheus |
| 15:45:15 | App Pods versuchen DB zu erreichen → "connection refused" | App Logs |
| 15:45:30 | Deployment Timeout nach 30 Min | Kubernetes Deployment Status |

**Confidence 85%** – Das ist nicht mehrdeutig:

- PostgreSQL ist tatsächlich nicht erreichbar (Metrik, Logs, Connection Tests alle bestätigen das)
- Die Wartung ist geplant und dokumentiert
- Die zeitliche Abfolge ist kausal: Wartung → Pods können nicht starten → Timeout

## Was sollst du tun?

Das Verdict empfiehlt drei konkrete Schritte:

1. **Jetzt (HIGH):** Warte, bis die PostgreSQL-Wartung (maint-2026-01-09-1) abgeschlossen ist und überprüfe, dass die postgres_up Metrik wieder auf 1 ist.

2. **Unmittelbar danach (HIGH):** Retry das Deployment. Es sollte jetzt funktionieren, da die Abhängigkeit wieder verfügbar ist.

3. **Danach (MEDIUM):** Verhindere das nächste Mal: Koordiniere Maintenance-Fenster mit CI/CD-Plänen. Möglichkeiten:
   - Maintenance darf nicht während Auto-Deploy-Zeiten stattfinden
   - CI/CD muss ein "Maintenance-aware Mode" haben (Deployment pausieren)
   - Wartungs-Ankündigungen sollten automatisch zu CI/CD-Plänen synchronisiert werden

## Warum zeigt errorbrain das richtig?

Dieses Szenario zeigt den **echten Wert** von errorbrain:

- **Es ist kein Fehler im Code** – aber der Deployment-Job gibt auf
- **Es ist kein Fehler in der Infrastruktur** – die Wartung ist normal und geplant
- **Es ist ein Koordinationsproblem** – zwei Team-Prozesse kollidieren zeitlich
- **Ohne gute Diagnose** könntest du stundenlang Debug-Logs wälzen und nach Bugs suchen, die nicht existieren
- **Mit errorbrain:** In unter 5 Minuten klar, dass es die Maintenance-Fenster sind

Das ist typisch für Produktivumgebungen: Nicht immer sind Fehler **kausal** – manchmal sind es **zeitliche Konflikte zwischen unabhängigen Prozessen**. errorbrain hilft dir, die zu erkennen.
