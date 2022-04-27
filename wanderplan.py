import locale
import os
import logging as log
import sys
import shutil
import datetime
import pandas as pd

# temporäres Logfile anlegen
log.basicConfig(format='%(asctime)s %(message)s',
                filename='wplogtmp.txt',
                datefmt='%Y/%m/%d %I:%M:%S',
                force=True)
log.warning(f"===> Wanderplan-Generierung vom {datetime.date.today()} <===")

# zur korrekten Ermittlung des Wochentages
locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')

# Import des Wanderplan Excel mit Pandas und Openpyxl:
wpfile = 'WEBINP_Wanderplan_PWV_Speyer_aktuell.xlsx'
log.warning(f'Lese {wpfile}.')
df = pd.read_excel(wpfile, engine='openpyxl')

# Ermittle Datum des Wanderplans aus dem Modifikationsdatum der Datei
wpstand = datetime.date.fromtimestamp(os.path.getmtime(wpfile)). \
    strftime('%d.%m.%Y')
log.warning(f'Änderungsstand der Excel-Datei: {wpstand}.')

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
def wpmailgen():
    global wpmailto
    wpmailto = '<br><b><a href=\"mailto:info@pwv-speyer.de?subject=Anmeldung/Workshop: ' + \
        line["Veranstaltung"]
    wpmailto += '''&body=Hallo Pfälzerwald-Team Speyer,%0D%0A
%0D%0AIch möchte folgende Personen zu einer Wanderung mit dem PWV Speyer anmelden:%0D%0A'''
    wpmailto += '%0D%0AWanderung: ' + wtype[line["Icon"]]
    wpmailto += '%0D%0ATitel:     ' + line["Veranstaltung"]
    wpmailto += '%0D%0ADatum:     {0}, den {1}'.format(
        line['Datum'].strftime('%A'), line['Datum'].strftime('%d. %B %Y'))
    if line["Icon"] == "MON":
        wpmailto += '%0D%0A%0D%0ALang/Kurz:     _________________________ (Anmeldung für Kurz- oder Langwanderung)'
    wpmailto += '''%0D%0A
%0D%0APerson 1:       _________________________ (Vor- und Nachname)
%0D%0A
%0D%0APerson 2:       _________________________ (Vor- und Nachname)
%0D%0A
%0D%0APerson 3:       _________________________ (Vor- und Nachname)
%0D%0A
%0D%0APerson 4:       _________________________ (Vor- und Nachname)
%0D%0A
'''
    if line['Hinweis'] != '':
        wpmailto += '%0D%0AHinweis:       ' + line['Hinweis'] + '%0D%0A'
    wpmailto += '''%0D%0AIch bitte um kurze Bestätigung.
%0D%0A
%0D%0AViele Grüße
%0D%0A\">⇒Anmeldung</a></b>
'''


# Seitenheader
wpheader = '''
<html lang="de">
<meta charset="UTF-8">
<link rel="stylesheet" href="wanderplan.css">'''

# Tabellen-Header
wptabhead = '<h3>Stand: ' + wpstand + '''</h3>
<table id="wanderplan">
<thead><tr>
  <th style=\"text-align:center;\">Datum</th>
  <th>Veranstaltung </b>(alte Wanderungen einblenden: <input type="checkbox" id="historie" onchange="historie"()>)<b></th>
  <th style=\"text-align:center;\">Art</th>
  <th>Wanderführung/<br>Organisation</th>
  <th>Details/Links</th>
</tr></thead>
'''

# Tabellen-Inhalt - Füllen der Tabellenzellen je Spalte
log.warning('Generiere HTML-Tabelle und HTML-Teaser.')
wptable = '<tbody>'
wpteaser = '<ul>'
wpteaserzahl = 0
for line in wpdata[0:]:
    if line['Datum'] >= datetime.date.today():
        wpzukunft = True
    else:
        wpzukunft = False

    if wpzukunft:
        wptable += '<tr>'
    else:
        wptable += '<tr class=\"noshow\" style=\"display:none; color:gray; ' \
                   'background-color: #e4e4e4;\">'

    # Datumspalte
    wptable += '<td style=\"text-align:center;\"><b>{0}<br>{1}</b></td>' \
        .format(line['Datum'].strftime('%A'),
                line['Datum'].strftime('%d.%m.%Y'))

    # Veranstaltung - 1. Zeile, immer sichtbar, fett
    if line['Absage'] != '':
        erstezeile = "<del>" + line['Veranstaltung'] + "</del>"
        if wpzukunft is True:
            erstezeile += '<span style="color: red">' + " &gt;&gt;&gt;" + \
                line['Absage'] + "&lt;&lt;&lt;" + '</span>'
        else:
            erstezeile += " &gt;&gt;&gt;" + line['Absage'] + '&lt;&lt;&lt;'
    elif line['Ausgebucht'] != '':
        erstezeile = line['Veranstaltung'] + " &gt;&gt;&gt;" + \
                     line['Ausgebucht'] + '&lt;&lt;&lt;'
    else:
        erstezeile = line['Veranstaltung']

    # Veranstaltung 2 - Beschreibung der Wanderung
    folgezeilen = ""
    if line['Veranstaltung 2 '] != "":
        folgezeilen += "<br>" + line['Veranstaltung 2 ']

    # Veranstaltung 3 - Ergänzungen nur für künftige Termine,
    # wie Treffpunkt, Bus oder Kosten
    if wpzukunft:
        if line['Veranstaltung 3'] != "":
            folgezeilen += "<BR>" + line['Veranstaltung 3']
    wptable += "<td><b>{0}</b>{1}</td>".format(erstezeile, folgezeilen)

    # Art: Link auf Icon im Unterordner /icons
    wptable += "<td style=\"text-align:center;\"><img src=\"./icons/{0}xs.png\"></td>".format(
        line['Icon'])

    # Wanderführer
    if line['WFKW'] != '':
        wptable += '<td>LW: {0}<BR>KW: {1}</td>'.format(
            line['WF'], line['WFKW'])
    else:
        wptable += '<td>{0}</td>'.format(line['WF'])

    # Ausschreibung mit Link
    wpmailto = ''
    wptable += '<td>'
    if line['Ausschreibung'] != "":
        # Anmeldefrist, sofern nicht verstrichen
        if not pd.isnull(line['Anmeldefrist']):
            if line['Anmeldefrist'] >= datetime.date.today():
                wpmailgen()  # Anmeldelink generieren
        wptable += '<b><a href=\"../download/{0}\" target=\"_blank\">⇒Beschreibung</a></b>{1}'.format(
            line['Ausschreibung'], wpmailto)
    if line['Wanderbericht'] != "":
        wptable += '<br><b><a href=\"{0}\">⇒Wanderbericht</a></b>'.format(
            line['Wanderbericht'])
    wptable += "</td></tr>\n"

    # Teaser mit den nächsten n Wanderungen für die Startseite erstellen
    if (wpzukunft is True) and (wpteaserzahl < 4) and \
            (line['Absage'] == '') and (line['Ausgebucht'] == ''):
        wpteaser += "<li><h3>{0} - {1} ({2})</h3></li>" \
            .format(line['Datum'].strftime('%d.%m.%Y'), line['Veranstaltung'], wtype[line["Icon"]])
        wpteaserzahl += 1

wptable += "</tbody > </table > </body> </html>"
wpteaser += "</ul>"

# Zusammenbau der HTML-Seite
wphtml = wpheader + wptabhead + wptable + wpscript

# Zusammenbau des Teasers
wpteashtml = wpheader + wpteaser

# archiv-Verzeichnis ggf. anlegen
if not os.path.exists('./archiv'):
    os.makedirs('./archiv')

# Archivierung der bisherigen HTML-Datei
wpquelle = "./wptable.html"
wpziel = "./archiv/wptable" + \
    datetime.datetime.now().strftime("%y%m%d-%H%M%S") + ".html"
try:
    shutil.copy(wpquelle, wpziel)
except:
    log.error('Fehler beim Archivieren der HTML-Seite!')
log.warning('HTML-Seite archiviert')

# Schreiben der Wanderplan-HTML-Datei
try:
    log.warning(f'Schreibe wptable.html mit {len(wpdata)} Veranstaltungen.')
    wpout = open('wptable.html', 'w')
    wpout.writelines(wphtml)
    wpout.close()
except:
    log.error(
        f'Fehler beim Schreiben der Wanderplan-HTML-Seite: {sys.exc_info()}')

# Schreiben der Teaser-HTML-Datei
try:
    log.warning('Schreibe wpteaser.html.')
    wpout = open('wpteaser.html', 'w')
    wpout.writelines(wpteashtml)
    wpout.close()
except:
    log.error(f'Fehler beim Schreiben der Teaser-HTML-Seite: {sys.exc_info()}')

log.warning('Fertig!')
