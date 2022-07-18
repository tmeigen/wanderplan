import locale
import os
import logging as log
import sys
import shutil
import datetime
import pandas as pd

# temporäres Logfile anlegen
log.basicConfig(level=log.INFO,
                format='%(asctime)s %(message)s',
                filename='wplogtmp.txt',
                filemode='w',
                datefmt='%Y/%m/%d %H:%M:%S',
                force=True)
log.info(f"===> Wanderplan-Generierung vom {datetime.date.today()} <===")

# zur korrekten Ermittlung des Wochentages
locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')

# Import des Wanderplan Excel mit Pandas und Openpyxl:
wpfile = 'WEBINP_Wanderplan_PWV_Speyer_aktuell.xlsx'
log.info(f"Lese {wpfile}.")
df = pd.read_excel(wpfile, engine='openpyxl')

# Ermittle Datum des Wanderplans aus dem Modifikationsdatum der Datei
wpstand = datetime.date.fromtimestamp(os.path.getmtime(wpfile)). \
    strftime('%d.%m.%Y')
log.info(f"Änderungsstand der Excel-Datei: {wpstand}.")

# Konvertierungen
df = df.fillna('')  # Umwandlung von nan Feldern in leere Strings
# Umwandlung von Timestamp in Datum
df['Datum'] = pd.to_datetime(df['Datum']).dt.date
df['Anmeldefrist'] = pd.to_datetime(df['Anmeldefrist']).dt.date

# Umwandlung des Dataframes in List of Dicts
wpdata = df.to_dict('records')

# Langtexte Wander-Typen für Mailto-Inhalt
wtype = {
    'FAM': 'Familienwanderung',
    'FUN': 'Besondere Veranstaltung',
    'JSW': 'Jungseniorenwanderung',
    'MON': 'Monatswanderung',
    'MTR': 'Monatstreffen',
    'RAD-B': 'Radwanderung',
    'RAD-R': 'Radwanderung',
    'SEN': 'Seniorenwanderung',
    'SPW': 'Sportwanderung'
}

# Script für das Ein-/Ausblenden vergangener Veranstaltungen anhängen
wpscript = '<script type="text/javascript" src="wanderplan.js"></script>'


# Generator für Anmeldungs-Mailto
def wpmailgen(hike):
    # Nach Verstreichen der Anmeldefrist "Nachmeldung" anzeigen
    if hike['Anmeldefrist'] >= datetime.date.today():
        wpmeldung = "Anmeldung"
    else:
        wpmeldung = "Nachmeldung"

    wpmailto = (
        f"<br><b><a href=\"mailto:PWV Speyer<info@pwv-speyer.de>?subject={wpmeldung}: {hike['Veranstaltung']}"
        f"&body=Wanderung: {wtype[hike['Icon']]}%0D%0A"
        f"Titel:     {hike['Veranstaltung']}%0D%0A"
        f"Datum:     {hike['Datum'].strftime('%A')}, den {hike['Datum'].strftime('%d. %B %Y')}%0D%0A%0D%0A"
        f"Hallo Pfälzerwald-Team Speyer,%0D%0A%0D%0A"
        f"ich möchte folgende Personen zu einer Wanderung mit dem PWV Speyer anmelden:%0D%0A%0D%0A"
    )
    if hike["Icon"] == "MON":
        wpmailto += '%0D%0ALang/Kurz:     _________________________ (Anmeldung für Kurz- oder Langwanderung)'
    wpmailto += (
        "Person 1:       _________________________ (Vor- und Nachname)%0D%0A%0D%0A"
        "Person 2:       _________________________ (Vor- und Nachname)%0D%0A%0D%0A"
        "Person 3:       _________________________ (Vor- und Nachname)%0D%0A%0D%0A"
        "Person 4:       _________________________ (Vor- und Nachname)%0D%0A%0D%0A"
    )
    if hike['Hinweis'] != '':
        wpmailto += f"Hinweis:       {hike['Hinweis']}%0D%0A"
    wpmailto += (
        f"%0D%0AIch bitte um kurze Bestätigung."
        f"%0D%0A%0D%0A"
        f"Viele Grüße%0D%0A\">"
        f"⇒{wpmeldung}</a></b>"
    )
    return wpmailto


# Seitenheader
wpheader = (
    '<html lang="de">'
    '<meta charset="UTF-8">'
    '<link rel="stylesheet" href="wanderplan.css">'
)

# Aufbau der Dateien
log.info('Generiere HTML-Tabelle, HTML-Teaser und iCal-Kalender.')
wptabhead = (
    f'<h3>Stand: {wpstand} </h3>'
    '<table id="wanderplan">'
    '<thead><tr>'
    '  <th style=\"text-align:center;\">Datum</th>'
    '  <th>Veranstaltung </b>(alte Wanderungen einblenden: <input type="checkbox" id="historie" onchange="historie"()>)<b></th>'
    '  <th style=\"text-align:center;\">Art</th>'
    '  <th>Wanderführung/<br>Organisation</th>'
    '  <th>Details/Links</th>'
    '</tr></thead>'
)
wptable = "<tbody>"
wpteaser = "<ul>"
wpteasercounter = 0
wpical = (
    "BEGIN:VCALENDAR\r"
    "VERSION:2.0\r"
    "METHOD:PUBLISH\r"
    "PRODID:-//PWV Speyer//NONSGML Wanderplan//DE\r"
    "URL:https://www.pwv-speyer.de/wpgen/wpical.ics\r"
    "NAME:PWV Speyer\r"
    "X-WR-CALNAME:PWV Speyer\r"
    "DESCRIPTION:PWV Speyer Wanderplan\r"
    "X-WR-CALDESC:PWV Speyer Wanderplan\r"
)

# Tabellen-Inhalt - Für alle Termine füllen der Tabellenzellen je Spalte
for wphike in wpdata[0:]:
    wpzukunft = wphike['Datum'] >= datetime.date.today()

    if wpzukunft:
        wptable += '<tr>'
    else:
        wptable += '<tr class=\"noshow\" style=\"display:none; color:gray; ' \
                   'background-color: #e4e4e4;\">'

    # Datumspalte
    if wphike['ManTxtDatum'] == '':
        wptable += f"<td style=\"text-align:center;\"><b>{wphike['Datum'].strftime('%A')}<br>{wphike['Datum'].strftime('%d.%m.%Y')}</b></td>"
    else:
        wptable += f"<td style=\"text-align:center;\"><b>{wphike['ManTxtDatum']}</b></td>"
    # Veranstaltung - 1. Zeile, immer sichtbar, fett
    if wphike['Absage'] != '':
        erstezeile = "<del>" + wphike['Veranstaltung'] + "</del>"
        if wpzukunft is True:
            erstezeile += f'<span style="color: red"> &gt;&gt;&gt;{wphike["Absage"]}&lt;&lt;&lt;</span>'
        else:
            erstezeile += f' &gt;&gt;&gt;{wphike["Absage"]}&lt;&lt;&lt;'
    elif wphike['Ausgebucht'] != '':
        erstezeile = f'{wphike["Veranstaltung"]} &gt;&gt;&gt;{wphike["Ausgebucht"]} &lt;&lt;&lt;'
    else:
        erstezeile = wphike['Veranstaltung']

    # Veranstaltung2 - Beschreibung der Wanderung
    folgezeilen = ""
    if wphike['Veranstaltung2'] != "":
        folgezeilen += f'<br>{wphike["Veranstaltung2"]}'

    # Veranstaltung3 - Ergänzungen nur für zukünftige Termine,
    # wie Treffpunkt, Bus oder Kosten
    if wpzukunft:
        if wphike['Veranstaltung3'] != "":
            folgezeilen += "<BR>" + wphike['Veranstaltung3']
    wptable += f"<td><b>{erstezeile}</b>{folgezeilen}</td>"

    # Art: Link auf Icon im Unterordner /icons
    wptable += f"<td style=\"text-align:center;\"><img src=\"./icons/{wphike['Icon']}xs.png\"></td>"

    # Wanderführer
    if wphike['WFKW'] != '':
        wptable += f"<td>LW: {wphike['WF']}<BR>KW: {wphike['WFKW']}</td>"
    else:
        wptable += f"<td>{wphike['WF']}</td>"

    # Ausschreibung mit Link
    wpmailto = ''
    wptable += '<td>'
    if wphike['Ausschreibung'] != "":
        wptable += f"<b><a href=\"../download/{wphike['Ausschreibung']}\" target=\"_blank\">⇒Beschreibung</a></b>"
        if wphike['Datum'] > datetime.date.today() and \
           wphike['Absage'] != 'ABGESAGT' and \
           wphike['Ausgebucht'] != 'AUSGEBUCHT':
            wptable += f"{wpmailgen(wphike)}"  # Anmeldelink generieren
    if wphike['Wanderbericht'] != "":
        wptable += f"<br><b><a href=\"{wphike['Wanderbericht']}\" target=\"_parent\">⇒Wanderbericht</a></b>"
    wptable += "</td></tr>\n"

    # Teaser mit den nächsten n Wanderungen für die Startseite erstellen
    if (wpzukunft is True) and (wpteasercounter < 4) and \
            (wphike['Absage'] == '') and (wphike['Ausgebucht'] == ''):
        if wphike['Ausschreibung'] == "":
            wpteaser += f"<li><h3>{wphike['Datum'].strftime('%d.%m.%Y')} - {wphike['Veranstaltung']} \
            ({wtype[wphike['Icon']]})</h3></li>"
        else:
            wpteaser += f"<li><h3>{wphike['Datum'].strftime('%d.%m.%Y')} - \
            <a href=\"../download/{wphike['Ausschreibung']}\" target=\"_blank\"> {wphike['Veranstaltung']} \
            ({wtype[wphike['Icon']]})</a></h3></li>"
        wpteasercounter += 1

    # Generiere Termin für iCal Kalender
    wpical += (
        f"BEGIN:VEVENT\r"
        f"UID:pwvspeyer{wphike['Datum'].strftime('%y%m%d')}{wphike['Icon']}\r"
        f"SUMMARY:{wphike['Veranstaltung']} ({wtype[wphike['Icon']]})\r"
        f"DTSTART;VALUE=DATE:{wphike['Datum'].strftime('%Y%m%d')}\r"
        f"DTEND;VALUE=DATE:{wphike['Datum'].strftime('%Y%m%d')}\r"
    )
    if wphike['Ausschreibung'] != "":
        wpical += f"URL:https://www.pwv-speyer.de/download/{wphike['Ausschreibung']}\r"
    else:
        wpical += "URL:https://www.pwv-speyer.de/wanderplan\r"
    wpical += "END:VEVENT\r"

# Dateiinhalte abschließen
wptable += "</tbody > </table > </body> </html>"
wpteaser += "</ul>"
wpical += "END:VCALENDAR"

# Zusammenbau der HTML-Seite
wphtml = wpheader + wptabhead + wptable + wpscript

# Zusammenbau des Teasers
wpteashtml = wpheader + wpteaser

# archiv-Verzeichnis ggf. anlegen
if not os.path.exists('./archiv'):
    os.makedirs('./archiv')

# Archivierung der bisherigen HTML-Datei
wpquelle = "./wptable.html"
wpziel = f"./archiv/wptable{datetime.datetime.now().strftime('%y%m%d-%H%M%S')}.html"
try:
    shutil.copy(wpquelle, wpziel)
except:
    log.error('Fehler beim Archivieren der HTML-Seite!')
log.info('HTML-Seite archiviert')

# Schreiben der Wanderplan-HTML-Datei
try:
    log.info(f'Schreibe wptable.html mit {len(wpdata)} Veranstaltungen.')
    wpout = open('wptable.html', 'w')
    wpout.writelines(wphtml)
    wpout.close()
except:
    log.error(
        f'Fehler beim Schreiben der Wanderplan-HTML-Seite: {sys.exc_info()}')

# Schreiben der Teaser-HTML-Datei
try:
    log.info('Schreibe wpteaser.html.')
    wpout = open('wpteaser.html', 'w')
    wpout.writelines(wpteashtml)
    wpout.close()
except:
    log.error(f'Fehler beim Schreiben der Teaser-HTML-Seite: {sys.exc_info()}')

# Schreiben der iCal-Datei
try:
    log.info('Schreibe wpical.ics.')
    wpout = open('wpical.ics', 'w')
    wpout.writelines(wpical)
    wpout.close()
except:
    log.error(f'Fehler beim Schreiben der iCal-Datei: {sys.exc_info()}')

log.info('Fertig!')
