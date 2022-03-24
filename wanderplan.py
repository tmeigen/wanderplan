import locale
import os
import sys
import shutil
import datetime
import time
# print("Starte import pandas")
import pandas as pd

# zur korrekten Ermittlung des Wochentages
locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')

wpfile = "WEBINP_Wanderplan_PWV_Speyer_aktuell.xlsx"

# Import des Wanderplan Excel mit Pandas und Openpyxl:
print("Lese " + wpfile + ".")
df = pd.read_excel(wpfile, engine='openpyxl')

# Ermittle Datum des Wanderplans aus dem Modifikationsdatum der Datei
wpstand = datetime.datetime.fromtimestamp(os.path.getmtime(wpfile)).strftime('%d.%m.%Y')

# Beseitigung von nan
df = df.fillna('')  # Umwandlung von nan Feldern in leere Strings

# Umwandlung des Dataframes in List of Dicts
wpdata = df.to_dict('records')

# Langtexte Wander-Typen für Mailto-Inhalt
wtype = {
    "MON": "Monatswanderung",
    "FAM": "Familienwanderung",
    "FUN": "Besondere Veranstaltung",
    "JSW": "Jungseniorenwanderung",
    "MTR": "Monatstreffen",
    "RAD-B": "Radwanderung",
    "RAD-R": "Radwanderung",
    "SEN": "Seniorenwanderung",
    "SPW": "Sportwanderung"
}

# Script für das Ein-/Ausblenden vergangener Veranstaltungen anhängen
wpscript = '<script type="text/javascript" src="wanderplan.js"></script>'

# Generator für Anmeldungs-Mailto
def wpmailgen():
    global wpmailto
    wpmailto = '<br><b><a href=\"mailto:info@pwv-speyer.de?subject=Anmeldung/Workshop: ' + line["Veranstaltung"]
    wpmailto += '''&body=Hallo PWV-Team Speyer,%0D%0A
%0D%0AIch möchte folgende Personen zu einer Wanderung mit dem PWV Speyer anmelden:%0D%0A'''
    wpmailto += '%0D%0AWanderung: ' + wtype[line["Icon"]]
    wpmailto += '%0D%0ATitel:     ' + line["Veranstaltung"]
    wpmailto += '%0D%0ADatum:     {0}, den {1}%0D%0A'.format(
        line['Datum'].strftime('%A'), line['Datum'].strftime('%d. %B %Y'))
    if line['Hinweis'] != '':
        wpmailto += '%0D%0AHinweis:       ' + line['Hinweis']
    if line["Icon"] == "MON":
        wpmailto += '%0D%0ALang/Kurz:     _________________________ (Anmeldung für Kurz- oder Langwanderung)'
    wpmailto += '''%0D%0A
%0D%0APerson 1:       _________________________ (Vor- und Nachname)
%0D%0A
%0D%0APerson 2:       _________________________ (Vor- und Nachname)
%0D%0A
%0D%0APerson 3:       _________________________ (Vor- und Nachname)
%0D%0A
%0D%0APerson 4:       _________________________ (Vor- und Nachname)
%0D%0A
%0D%0AIch bitte um kurze Bestätigung.
%0D%0A
%0D%0AViele Grüße
%0D%0A\">⇒Anmeldung</a></b>
'''

# Seitenheader
wpheader = '''
<html lang="de">
<meta charset="UTF-8">
<link rel="stylesheet" href="wanderplan.css">
<h3 style="font-family: Arial, Helvetica, sans-serif;">Stand: ''' + wpstand + '</h3>'

# Tabellen-Header
wptabhead = '''
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
print("Generiere HTML-Tabelle.")
wptable = '<tbody>'
for line in wpdata[0:]:
    # Filtern vergangener Termine bis minus 1 Woche
    # (if line['Datum'] <= wpgendate - datetime.timedelta(days=7):)
#    try:
    if line['Datum'] >= datetime.datetime.today():
        wpzukunft = True
    else:
        wpzukunft = False
#    except ValueError:
#       print("Seltsamer Formatfehler bei 1blu Hoster => Abbruch")
#        break

    if wpzukunft:
        wptable += '<tr>'
    else:
        wptable += '<tr class=\"noshow\" style=\"display:none; color:gray; background-color: #e4e4e4;\">'

    # Datumspalte
    wptable += "<td style=\"text-align:center;\"><b>{0}<br>{1}</b></td>" \
        .format(line['Datum'].strftime('%A'), line['Datum'].strftime('%d.%m.%Y'))

    # Veranstaltung - 1. Zeile, immer sichtbar, fett
    if line['Absage'] != '':
        erstezeile = "<del>" + line['Veranstaltung'] + "</del>"
        if wpzukunft == True:
           erstezeile += '<span style="color: red">' + " &gt;&gt;&gt;" + line['Absage'] + "&lt;&lt;&lt;" + '</span>'
        else:
           erstezeile += " &gt;&gt;&gt;" + line['Absage'] + '&lt;&lt;&lt;'
    elif line['Ausgebucht'] != '':
        erstezeile = line['Veranstaltung'] + " &gt;&gt;&gt;" + line['Ausgebucht'] + '&lt;&lt;&lt;'
    else:
        erstezeile = line['Veranstaltung']

    # Veranstaltung 2 - Beschreibung der Wanderung
    folgezeilen = ""
    if line['Veranstaltung 2 '] != "":
        folgezeilen += "<br>" +line['Veranstaltung 2 ']

    # Veranstaltung 3 - Ergänzungen nur für künftige Termine, wie Treffpunkt, Bus oder Kosten
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
    if line['Ausschreibung'] != "":
        # Anmeldefrist, sofern nicht verstrichen
        if line['Anmeldefrist'] != '':
            if line['Anmeldefrist'] > datetime.datetime.today():
                wpmailgen()  # Anmeldelink generieren
        wptable += "<td><b><a href={0}>⇒Beschreibung</a></b>{1}</td>".format(
            line['Ausschreibung'], wpmailto)
    else:
        wptable += '<td></td>'

    wptable += "</tr>\n"
wptable += "</tbody > </table > </body> </html>"

# Zusammenbau der HTML-Seite
wphtml = wpheader + wptabhead + wptable + wpscript

# archiv-Verzeichnis ggf. anlegen
if not os.path.exists('./archiv'):
    os.makedirs('./archiv')

# Archivierung der bisherigen HTML-Datei
wpquelle = "./wanderplan.html"
wpziel = "./archiv/wanderplan" + datetime.datetime.now().strftime("%y%m%d-%H%M%S") +".html"
try:
    shutil.copy(wpquelle, wpziel)
except PermissionError: print("Fehlende Zugriffsrechte beim Archivieren der HTML-Seite!")
except: print("Fehler beim Archivieren der HTML-Seite!")
print("HTML-Seite archiviert")

# Schreiben der HTML-Datei
try:
    print("Schreibe wanderplan.html mit {0} Veranstaltungen.".format(len(wpdata)))
    wpout = open("wanderplan.html", "w")
    print("Datei geöffnet.")
    wpout.writelines(wphtml)
    print("Inhalt geschrieben.")
    # print(wphtml)
    wpout.close()
    print("HTML-Seite erfolgreich geschlossen.")
    print("Fertig!")
except:
    e = sys.exc_info()
    print("Fehler beim Schreiben der HTML-Seite." + e)
