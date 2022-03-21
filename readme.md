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

Danach sollte die Generierung aufrufbar sein über
- SSH: python3 wanderplan.py und/oder
- http://&lt;domain&gt;/wanderplan/wanderplan.php

Einbetten der generierten HTML-Seite in Wordpress
Einbettung über HTML Block mit folgendem Inhalt:
```
<iframe src="<pfad>/wanderplan.html" referrer-policy="same-origin" width="100%" height="3700" frameborder="0" scrolling="no"></iframe>
```
Anpassungen:
- &lt;pfad&gt;
- height:

# Spec HTML-Rendering
## Spalte „Datum“
- [x] zweizeilig (Wochentag | Datum)
- [x] in schwarz, falls Datum in der Zukunft liegt; in grau wenn Termin in der Vergangenheit liegt

## Spalte „Veranstaltung“
- [x] Erste Zeile fett
  - Spalte F im Excel;
  - [x] in schwarz, falls Datum in der Zukunft liegt; in grau wenn Termin in der Vergangenheit liegt
  - [x] Eventuell ergänzt um die Abgesagt-Info, also „>>>“ &Text in Spalte O & „<<<“, in Rot falls Datum in der Zukunft; in Grau wenn Termin in der Vergangenheit liegt
  - [X]Eventuell ergänzt um die Ausgebucht-Info, also „–“ & Text in Spalte P & „–“ , Normale Farbgebung, als Schwarz / Grau
- Folgezeilen (eine oder mehr), je nachdem
  - [x] nicht fett, in schwarz, falls Datum in der Zukunft liegt; in grau wenn Termin in der Vergangenheit liegt
  - [x] „ca. „ & km-Angabe in Spalte H, bei MON „LW ca.“ & Spalte H & „, KW: ca.“ & Spalte I, bei SPW Höhenmeter mit „ca.“ dahinter
  - Wenn Termin in der Zukunft:
    - [x] Treffpunkt aus Spalte M ergänzen
    - [x] Dahinter Corona-Hinweise aus Spalte Q

## Spalte „Art“
- [x] Link auf entsprechendes Icon aus Spalte E generieren

## Spalte „Wanderführung/Organisation“
- [x] in Schwarz, falls Datum in der Zukunft liegt; in Grau wenn Termin in der Vergangenheit liegt
- [x] Wanderführung aus Spalte K, wenn MON, dann „LW:“ & Spalte K in zweite Zeile „KW:“ & Spalte L

## Spalte „Details / Anmeldung“
- [x] Link auf PDF, falls Dateiname in Spalte N vorhanden, Text „è Beschreibung“
- [x] MailTo-Link in neuer Zeile, falls Dateiname in Spalte N UND Veranstaltung in der Zukunft liegt