# GriffeyeCrawler
Analysiert eine exportierte Dateiliste aus Griffeye pro Gerät &amp; Kategorie
- Summiert die Bilder und Videos
- Fasst die Dateipfade zusammen und unterteilt diese in Cache- & Nicht-Cache-Pfade auf
- Ermittelt die Pfade mit den meisten Inhalten
- Ermittelt das prozentuelle Verhältnis im Browsercache und der übrigen Ablage
- Ermittelt die prozentuelle Verteilung der Dateierstellung im betroffenen Zeitraum
- Generiert eine Ergebnisdatei im TXT oder DOCX-Format

## Mit EXE
Es ist **keine** Installation notwendig...
Start/Ausführung verhalten sich gleich wie unter *Ohne EXE - Start/Ausführung* beschrieben, mit dem Unterschied, dass *GriffeyeCrawler.exe* ausgeführt werden muss.

## Ohne EXE
### Installation
- Python 3.x herunterladen (www.python.org) und installieren.
  - Sichergehen, dass "pip" ebenfalls installiert wird (ist standardmässig aktiviert)
  - Ob die Installationen erfolgreich waren mittels ``python --version`` & ``pip --version`` kontrollieren
  - evtl. muss *%APPDATA%\Local\Programs\Python\Python\<Version>* (Python) & *..\Scripts* (pip) in den Umgebungsvariablen erfasst werden
- Das Package *docx* mit ``pip install python-docx`` installieren

### Start/Ausführung
- *GriffeyeCrawler.py* doppelklicken
- Name der zu verarbeitenden CSV-Datei angeben. Der Standardwert (report_all.csv) kann einfach mit Enter bestätigt werden. Die entsprechende Datei kann auch mittels Drag-and-Drop ins Terminal gezogen werden.
- Name der Ergebnisdatei angeben. Der Standardwert (result.docx) kann einfach mit Enter bestätigt werden. Es sind die Formate .txt & .docx möglich.
- Das Ergebnis wird im Verzeichnis *_files* erstellt (Standardeinstellung). Ausserdem wird bei jeder Verarbeitung die Datei *pathdetails.txt* erstellt, welche detailliertere Informationen zu den ausgewerteten Daten aufweist.
**Bestehende Dateien werden ohne Warnung überschrieben!**

Bei Bedarf können diverse Einstellungen in der Datei *config.json* vorgenommen werden. Diese Datei muss sich im selben Verzeichnis wie *GriffeyeCrawler.py* befinden.
