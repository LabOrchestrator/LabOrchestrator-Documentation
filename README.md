![Status](https://img.shields.io/badge/status-stable-brightgreen)
[![License](https://img.shields.io/github/license/laborchestrator/laborchestrator-documentation)](https://github.com/LabOrchestrator/LabOrchestrator-documentation/blob/main/LICENSE)
[![Issues](https://img.shields.io/github/issues/laborchestrator/laborchestrator-documentation)](https://github.com/laborchestrator/laborchestrator-documentation/issues)
[![Downloads](https://img.shields.io/github/downloads/laborchestrator/laborchestrator-documentation/total)](https://github.com/LabOrchestrator/LabOrchestrator-Documentation)

# LabOrchestrator-Documentation

This is the project documentation. It contains an installation guide but also a full project description and the documentation about the prototype and some development steps. It's a big guide, but it should contain everything that needs to be documented.

## Orchestrator and research goals

- [x] Kubernetes und KubeVirt installieren, Kubernetes Templates und Base Images anschauen, KubeVirt Base VMs in Kuberetes starten und stoppen (1 Woche)
- [x] Evaluation Web-Terminal Tools (0.5 – 1 Woche)
- [x] Evaluation Web-VNC Tools (0.5 – 1 Woche)
- [ ] Docker Base Images mit Web-Terminal Tool (0.5 Wochen)
- [x] VM Base Image mit Web-VNC Tool (0.5 – 1 Woche)
- [x] Kubernetes Template mit vorherigen Base Images bereitstellen und testen (1 Woche)
- [x] Evaluation einer Routing Lösung (1 Woche, Worst Case 2 Wochen)
- [x] Kubernetes Usergebundenes Routing mit Autorisierung (1 Woche)

## Library goals

- [x] Library: Lernmodul starten und stoppen (1 – 2 Wochen)
- [x] Library: Routing und Autorisierung im Proxy automatisch konfigurieren (1 Woche)
- [x] Library: Lernmodule hinzufügen und entfernen (1 Wochen)
- [x] Library: Anleitung hinzufügen (0.5 Wochen)
- [x] Library: Features der Anleitungen hinzufügen (1 – 2 Wochen)


- [x] Lernmodule starten und stoppen (muss)
- [ ] Lernmodule pausieren und fortfahren (kann)
- [x] Lernmodule hinzufügen und entfernen (muss)
- [x] Routing für Lernmodule konfigurieren (muss)
- [x] Beim Routing eine Authentification-Möglichkeit hinzufügen (muss)
- [x] Authentification-Details für Lernmodule anzeigen (muss)
- [x] User und ihre Lernmodule verknüpfen (muss)
- [x] Anleitungen hinzufügen (muss)
- [x] Lernmodule und Anleitungen verknüpfen (muss)

## Instruction goals

- [x] Markdown oder HTML Syntax (kann)
- [x] Seiten mit Text (muss)
- [x] Controller zur Auswahl der VM (muss)
- [x] Schritte pro Seite (kann)
- [ ] Schritte abhaken (kann)
- [ ] Fortschrittsbar zu abgehakten Schritten (kann)
- [x] Bilder und andere Medien einbinden (kann)
- [x] Wissenstexte darstellen (muss)
- [ ] Interaktion mit VMs, beispielsweise Texte in das Clipboard der VM kopieren (kann)
- [ ] Variablen (kann)


## API goals

- [x] Webschnittstelle: User- und Permission-Management (1 Woche)
- [x] Abbilden aller Library Funktionalitäten als REST-Schnittstelle und in Datenbankmodellen
