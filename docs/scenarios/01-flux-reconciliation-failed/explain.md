# Erklärung: Flux Reconciliation Failed

## Was ist passiert?

Der Flux-Controller konnte die GitOps-Konfiguration nicht anwenden, weil eine erforderliche Konfigurationsdependency fehlte.

## Die Ursache (laut Verdict)

**Hypothese:** GitOps-Reconciliation wurde blockiert durch fehlende Konfigurationsdependency.

Das System erkennt folgendes Muster:

1. **Unmittelbare Fehlerquelle:** Der Helm-Chart `app-api-service` v3.2.1 erwartet einen Schlüssel `database.password` in der ConfigMap, aber dieser ist nicht vorhanden.

2. **Kontext (aus den Beweisen):**
   - Die ConfigMap `app-config-values` wurde vor 45 Sekunden modifiziert (kurz vor dem Fehler)
   - Ein Commit von SecOps mit der Nachricht "Rotate secrets - remove hardcoded db password" wurde gerade gepusht
   - Das erklärt den fehlenden Schlüssel: absichtliche Entfernung während einer Secret-Rotation

3. **Diagnose:** Das ist kein zufälliger Fehler – es ist ein Koordinationsproblem zwischen zwei Teams:
   - **SecOps** hat den Passwort-Schlüssel aus der ConfigMap entfernt (richtig, aus Security-Sicht)
   - **Infrastructure-Team** hat nicht zeitgleich den Helm-Chart angepasst, um eine neue Secret-Referenz zu verwenden (z.B. External Secrets, Sealed Secrets)

## Was sollst du tun?

Das Verdict empfiehlt drei konkrete Aktionen (in Prioritätsordnung):

1. **Sofort (HIGH):** Entweder den fehlenden Schlüssel wiederherstellen ODER den Chart so anpassen, dass er die neue Secret-Strategie nutzt. Überprüfe die letzten Commits von SecOps, um zu verstehen, welche neue Strategie geplant ist.

2. **Validieren (HIGH):** Stelle sicher, dass der Chart in der neuen Konfiguration lokal funktioniert (`helm template` vor dem Commit).

3. **Präventiv (MEDIUM):** Etabliere einen koordinierten Prozess zwischen SecOps und Infrastructure, damit solche Rotationen nicht wieder zur Überraschung führen.

## Warum ist das Verdict zuverlässig?

- **Confidence 85%** – Das System sieht ein klares Muster:
  - Zeitlich sehr nah beieinander (ConfigMap-Änderung → Fehler, 45s Abstand)
  - Ursache und Wirkung sind kausal verbunden (fehlender Schlüssel ↔ Validierungsfehler)
  - Beweise aus mehreren unabhängigen Quellen (Logs, Git-History, K8s-Events, HTTP API)

- **Keine Mehrdeutigkeit** – Das ist nicht "das Deployment ist langsam" oder "CPU zu hoch" – es ist eine konkrete, nachverfolgbare Abhängigkeitsverletzung.
