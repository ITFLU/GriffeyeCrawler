# GriffeyeCrawler - Changelog

## Version 1.0 - 01.03.2023
Umstellung auf CLI-Version und "UI" für Standardfälle
- Feature: Möglichkeit zur Angabe der zu verwendenden Datum-Felder
- Feature: Möglichkeit zum Auschluss unerwünschter Pfade
- Feature: Möglichkeit zur Ausgabe im JSON-Format
- Feature: Möglichkeit zum Ändern der Sprache in der Ergebnisdatei
- Feature: Möglichkeit zur Definition des Ergebnispfads bzw. der Ergebnidatei

## Version 0.5.2 - 21.02.2023
- Bugfix: Probleme mit mehreren aufeinander folgenden Gänsefüsschen (in "Series Names") behoben

## Version 0.5.1 - 15.02.2023
- Bugfix: Probleme mit dem Unicode-Symbol (\uFEFF) als erstes Zeichen im Header behoben
- Bugfix: Probleme mit Zeilen, welche Gänsefüsschen und den Separator darin enthalten, korrigiert

## Version 0.5 - 23.09.2022
- Feature: Häufigste Speicherorte enthalten nun die summierten Browsercache Totale pro Browser ähnlich Thumbcache (#14)
- Feature: Unix-Timestamp (01.01.1970) ebenfalls als "undefiniert" behandeln (#15)
- Feature: CSV-Separator wird nun anhand der Headerzeile ermittelt (#16)
- Feature: Ergebnisdatei wird nun im selben Pfad mit demselben Namen (x.docx) wie die Inputdatei erstellt (#18)
- Feature: Werte unter 1% Prozent werden neu als "<1%" anstelle des vorherigen "0%" (aufgrund der Rundung) dargestellt.
- Bugfix: Fehler bei der Bereinigung von Zeilen mit Komma innerhalb von " behoben, wenn Komma Separator ist  (#17)
- Bugfix: Fehler beim Parsen des Dateipfads durch unterschiedliche Pfadgenerierung bei Drag-n-Drop in verschiedenen Terminals behoben

## Version 0.4 - 09.12.2021
- Feature: Thumbcaches werden gesammelt als einen Eintrag in den Top-Pfaden aufgelistet (#12)
- Bugfix: Output-Verzeichnis wird bei Nichtauffinden automatisch erstellt (#11)
- Update: Erkannte Caches um diverse Kommunikations-Apps erweitert
 
## Version 0.3 - 23.11.2021
- Feature: Tabellen um den Wert "unique" (binary) erweitert (#9)
- Feature: Leere "Created Time" wo möglich durch "Last Write Time" ersetzen. Bis jetzt nur bei Mobiles aufgefallen... (#10)
 
## Version 0.2.1
- Update: Total-Tabellen "komprimiert", um weniger Platz im Rapport einzunehmen

## Version 0.2
- Feature: Im Gesamttotal unter 'Anzahl Geräte' Gerätetotal anzeigen
- Feature: Datum von gecarvten Files (01.01.0001) als 'undefiniert' anzeigen
- Update: In GriffeyeCrawler umbenannt

## Version 0.1
- Initial Version
