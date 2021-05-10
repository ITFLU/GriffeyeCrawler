# GriffeyeAnalyzer
Analysiert eine exportierte Dateiliste aus Griffeye pro Gerät &amp; Kategorie
- Summiert die Bilder und Videos
- Fasst die Dateipfade zusammen und unterteilt diese in Cache- & Nicht-Cache-Pfade auf
- Ermittelt die Pfade mit den meisten Inhalten
- Ermittelt das prozentuelle Verhältnis im Browsercache und der übrigen Ablage
- Ermittelt die prozentuelle Verteilung der Dateierstellung im betroffenen Zeitraum
- Generiert eine Ergebnisdatei im TXT oder DOCX-Format

## Installation
- Python 3.x herunterladen (www.python.org) und installieren.
  - Sichergehen, dass "pip" ebenfalls installiert wird (ist standardmässig aktiviert)
  - Ob die Installationen erfolgreich waren mittels ``python --version`` & ``pip --version`` kontrollieren
  - evtl. muss *%APPDATA%\Local\Programs\Python\Python\<Version>* (Python) & *..\Scrips* (pip) in den Umgebungsvariablen erfasst werden
- Das Package *docx* mit ``pip install docx`` installieren

## Start/Ausführung
- *GriffeyeAnalyzer.py* doppelklicken
- Name der zu verarbeitenden CSV-Datei angeben. Der Standardwert (report_all.csv) kann einfach mit Enter bestätigt werden.
- Name der Ergebnisdatei angeben. Der Standardwert (result.docx) kann einfach mit Enter bestätigt werden. Es sind die Formate .txt & .docx möglich.
- Das Ergebnis wird im selben Verzeichnis wie *GriffeyeAnalyzer.py* erstellt. Ausserdem wird bei jeder Verarbeitung die Datei *pathdetails.txt* erstellt, welche detailliertere Informationen zu den ausgewerteten Daten aufweist.
**Bestehende Dateien werden ohne Warnung überschrieben!**

Bei Bedarf können diverse Einstellungen in der Datei *config.json* vorgenommen werden. Diese Datei muss sich im selben Verzeichnis wie *GriffeyeAnalyzer.py* befinden.
