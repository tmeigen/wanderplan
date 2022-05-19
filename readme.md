# Wanderplan - HTML Generator für Wanderpläne des PWV Speyer

**wanderplan** ist ein Tool für den Pfälzerwaldverein Speyer eV, welches die Wanderungen und Termine der Ortsgruppe in eine HTML-Seite hinein generiert, die dann auf der Wortpress-Seite des Vereins veröffentlicht wird. Die Generierung erfolgt jede Nacht über einen Cron-Job und bezieht seine Daten aus einem vom Wanderwart bereitgestelltem Excel.

Besondere Eigenschaften des Tools sind:
* Generierung der HTML-Tabelle im Stil des Pfälzerwaldvereins
* Wenn verfügbar werden Wanderbeschreibungen verlinkt
* Während der Anmeldephase können sich Interessiert sich über einen Mailto-Link anmelden. Dieser Weg wurde gewählt, damit die Webseite keine personenbezogenen Daten verwalten muss. Nach Anmeldeschluss wird der Link nicht mehr angeboten.
* Termine der Vergangenheit werden nur optional angezeigt.
* Es wird zusätzlich eine Teaser-Tabelle mit den nächsten 4 Terminen für die Startseite generiert.
* Es wird eine ICal-Datei mit allen Wanderungen und Terminen für Abonnenten generiert
## Code
- readme.md: diese Datei
- wanderplan.py: HTML-Generator
- wanderplan.php: Script für den Aufruf des Generators per URL
- wanderplan.css: Style-Sheet
- wanderplan.js: eingebettete JavaScripte
- WEBINP_Wanderplan_PWV_Speyer_aktuell.xlsx: Excel-Datei, die die Planungsdaten enthält
- /archiv: Verzeichnis für archivierte HTML-Seiten
- /icons: Icons der Wandertypen
- (wanderplan.csv: (geplant) CSV-Datei für den Import in Google Calendar)

## Installation auf Hosting-Server über SSH-Zugang
Feststellen der Unix Version
- uname -a

### Feststellen der verfügbaren Python Version
- which python

### Anlegen Verzeichnis
- Anlegen eines Verzeichnisses /wanderplan im Web-Verzeichnis
- Kopieren der Programm-Dateien (wanderplan.*) in dieses Verzeichnis
- ggf. Anpassen des Start-Scriptes wanderplan.php, damit es über http://<domain>/wanderplan/wanderplan.php erreichbar ist

### Installation der benötigten Python-Pakete und $PATH anpassen
- python3 -m pip install pandas
- python3 -m pip install openpyxl
- export PATH=~/.local/bin:$PATH

### Danach sollte die Generierung aufrufbar sein über
- SSH: python3 wanderplan.py und/oder
- http://&lt;domain&gt;/wanderplan/wanderplan.php

### Ausgabedateien
- wptable.html: generierte HTML-Seite für die Einbettung in www.pwv-speyer.de
- wpteaser.html: generierte Liste der nächsten n Wanderungen für die Startseite
- wpical.ics: ical-Datei mit allen Terminen für Abonnenten
- wplog.txt: Generierungsprotokoll
### Einbetten der generierten HTML-Seite in Wordpress
Einbettung über HTML Block mit folgendem Inhalt:
```
<iframe src="<pfad>/wptable.html" referrer-policy="same-origin" width="100%" height="4200" frameborder="0" scrolling="no"></iframe>
```
Anpassungen:
- &lt;pfad&gt;
- height: aktuell statisch eingetragen