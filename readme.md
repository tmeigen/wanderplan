# Wanderplan - HTML Generator für Wanderpläne des PWV Speyer

## Inhalt
- wanderplan.py: Generator in Python
- wanderplan.html: generierte HTML-Seite für die Einbettung in www.pwv-speyer.de
- wanderplan.php: Script für den Aufruf des Generators per URL
- wanderplan.xlsm: Excel-Datei, die die Planungsdaten enthält
- wanderplan.csv: (geplant) CSV-Datei für den Import in Google Calendar
- readme.md: diese Datei

## Installation auf Hosting-Server über SSH-Zugang
Feststellen der Unix Version
- uname -a

Feststellen der verfügbaren Python Version
- ls /usr/bin/py3versions -s

Anlegen Verzeichnis
- Anlegen eines Verzeichnisses /wanderplan im Web-Verzeichnis
- Kopieren der Programm-Dateien (wanderplan.*) in dieses Verzeichnis
- ggf. Anpassen des Start-Scriptes wanderplan.php, damit es über http://<domain>/wanderplan/wanderplan.php erreichbar ist

Installation der benötigten Python-Pakete
- python3 -m pip install pandas
- python3 -m pip install openpyxl

Danach sollte die Generierung aufrufbar sein über:
- SSH: python3 wanderplan.py und/oder
- http://<domain>/wanderplan/wanderplan.php

# Spec HTML-Rendering
## Spalte „Datum“
- [x] zweizeilig (Wochentag | Datum)
- in schwarz, falls Datum in der Zukunft liegt; in grau wenn Termin in der Vergangenheit liegt
## Spalte „Veranstaltung“
- [x] Erste Zeile fett
  - Spalte F im Excel;
  - [x] in schwarz, falls Datum in der Zukunft liegt; in grau wenn Termin in der Vergangenheit liegt
  - [ ] Eventuell ergänzt um die Abgesagt-Info, also „>>>“ &Text in Spalte O & „<<<“, in Rot falls Datum in der Zukunft; in Grau wenn Termin in der Vergangenheit liegt
  - Eventuell ergänzt um die Ausgebucht-Info, also „–“ & Text in Spalte P & „–“ , Normale Farbgebung, als Schwarz / Grau
- Folgezeilen (eine oder mehr), je nachdem
  - [x] nicht fett, in schwarz, falls Datum in der Zukunft liegt; in grau wenn Termin in der Vergangenheit liegt
  - [ ] „ca. „ & km-Angabe in Spalte H, bei MON „LW ca.“ & Spalte H & „, KW: ca.“ & Spalte I, bei SPW Höhenmeter mit „ca.“ dahinter
  - Wenn Termin in der Zukunft:
    - [ ] Treffpunkt aus Spalte M ergänzen
    - [ ] Dahinter Corona-Hinweise aus Spalte Q
- Noch nicht implementiert:
  - Anmeldefrist, Teilnehmerbegrenzung, Preis (è neue Spalten in Excel notwendig; nur anzeigen, wenn Beschreibung vorhanden UND Anmeldefrist noch nicht abgelaufen)
## Spalte „Art“
- [ ] Link auf entsprechendes Icon aus Spalte E generieren
## Spalte „Wanderführung/Organisation“
- [ ] in Schwarz, falls Datum in der Zukunft liegt; in Grau wenn Termin in der Vergangenheit liegt
- [x] Wanderführung aus Spalte K, wenn MON, dann „LW:“ & Spalte K in zweite Zeile „KW:“ & Spalte L
## Spalte „Details / Anmeldung“
- [ ] Link auf PDF, falls Dateiname in Spalte N vorhanden, Text „è Beschreibung“
- [ ] MailTo-Link in neuer Zeile, falls Dateiname in Spalte N UND Veranstaltung in der Zukunft liegt, Text „è Anmeldung“; Mailtext siehe unten (variiert nach Typ, KW/LW-Abfrage bei MON)
- [ ] Logik um die Anzeige des Anmeldelinks könnte man noch schlauer machen (noch nicht implementiert):
  - [ ] Erscheinen nicht von Datum des Makroruns abhängig machen, sondern von separater Anmeldefrist im Excel
  - [ ] Also neue Spalte im Excel einfügen und HTML-Generator entsprechend aufschlauen
- Text im MailTo-Link könnte man noch schlauer machen, z. B.
  - [ ] Ggf. Abfrage zu Bezahlung è Auswahl „Bar/Bus“ oder „BEZ“
  - [ ] Ggf. Abfrage zu Buszustieg è Platzhalter zum Erfassen der Bushaltestelle
  - [ ] Ggf. Abfrage zu Gast/Mitglied è Auswahlmöglichkeit „Mitglied“ oder „Gast“
  - [ ] Also neue Spalten im Excel einfügen und HTML-Generator entsprechend aufschlauen
- Fernziel (wenn überhaupt) Generell könnte man die Anmeldung auch komplett online programmieren, oder über Ticketsystem abwickeln, aber Datenschutz…
 
## Aufgaben Bernhard
 - Spalten für Google Calendar umbenennen
   - Datum -> Start Date
   - Veranstaltung -> Subject
   - 
 - Spalten Monat und Tag entfernen
 - Spalten KM, KMKW und HM als Text formatieren oder besser noch: alles in ein Feld Veranstaltung 2 schreiben
 - warum Veranstaltung 2