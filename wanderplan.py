import locale
import os
import sys
import shutil
import datetime
import pandas as pd

# zur korrekten Ermittlung des Wochentages
locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')

# Import des Wanderplan Excel mit Pandas und Openpyxl:
print("Lese WEBINP_Wanderplan_PWV_Speyer_aktuell.xlsx")
df = pd.read_excel(
    "WEBINP_Wanderplan_PWV_Speyer_aktuell.xlsx", engine='openpyxl')

# Umwandlung der Spalte Datum in String im Format dd.mm.yy und Beseitigung von nan
df['Tag'] = df['Tag'].dt.strftime('%A')  # Wochentag
df['Datum'] = df['Datum'].dt.strftime('%d.%m.%Y')  # Datum im Format tt.mm.yyyy
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
def genwmailto():
    global mailto
    mailto = '<br><b><a href=\"mailto:info@pwv-speyer.de?subject=Anmeldung/Workshop: ' + line["Veranstaltung"]
    mailto += '''&body=Hallo PWV-Team Speyer,%0D%0A
%0D%0AIch möchte folgende Personen zu einer Wanderung mit dem PWV Speyer anmelden:%0D%0A'''
    mailto += '%0D%0AWanderung: ' + wtype[line["Icon"]]
    mailto += '%0D%0ATitel:     ' + line["Veranstaltung"]
    mailto += '%0D%0ADatum:     {0}, den {1}%0D%0A'.format(
        line['Tag'], line['Datum'])
    if line["Icon"] == "MON":
        mailto += '''%0D%0ALang/Kurz:     _________________________ (Anmeldung für Kurz- oder Langwanderung)'''
    mailto += '''%0D%0A
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
'''

# Tabellen-Header
wptabhead = '''
<p style="font-family: Arial, Helvetica, sans-serif;">Stand: 07.02.2022</p>
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
    try:
        wpdatum = datetime.datetime.strptime(line['Datum'], '%d.%m.%Y')
        if wpdatum >= datetime.datetime.today():
            wzukunft = True
        else:
            wzukunft = False
    except ValueError:
        print("Seltsamer Formatfehler bei 1blu Hoster => Abbruch")
        break

    if wzukunft:
        wptable += '<tr>'
    else:
        # ausblenden alter Termine
        wptable += '<tr class=\"noshow\" style=\"display:none; color:gray; background-color: #e4e4e4;\">'

    # Datumspalte
    wptable += "<td style=\"text-align:center;\"><b>{0}<br>{1}</b></td>" \
        .format(line['Tag'], line['Datum'])

    # Veranstaltung - 1. Zeile, immer sichtbar, fett

    if line['Absage'] != '':
        erstezeile = "<del>" + line['Veranstaltung'] + "</del>"
        if wzukunft == True:
           erstezeile += '<span style="color: red">' + " &gt;&gt;&gt;" + line['Absage'] + "&lt;&lt;&lt;" + '</span>'
        else:
           erstezeile += " &gt;&gt;&gt;" + line['Absage'] + '&lt;&lt;&lt;'
    elif line['Ausgebucht'] != '':
        erstezeile = line['Veranstaltung'] + " &gt;&gt;&gt;" + line['Ausgebucht'] + '&lt;&lt;&lt;'
    else:
        erstezeile = line['Veranstaltung']

    # Veranstaltung 2 - Beschreibung der Wanderung
    folgezeile = ""
    if line['Veranstaltung 2 '] != "":
        folgezeile += "<br>" +line['Veranstaltung 2 ']
    if line['KM'] != "":
        folgezeile += "<br>LW: " + line['KM']
    if line['KMKW'] != "":
        folgezeile += ", KW: ca. " + line['KMKW']
    if line['HM'] != "":
        folgezeile += ", HM: " + line['HM']

    # Veranstaltung 3 - Ergänzungen nur für künftige Termine, wie Treffpunkt, Bus oder Kosten
    if wzukunft:
        if line['Treffpunkt'] != "":
            folgezeile += "<BR>Treffpunkt: " + line['Treffpunkt']
        if line['Corona-Regeln'] != "":
            folgezeile += "<BR>" + line['Corona-Regeln']
    wptable += "<td><b>{0}</b>{1}</td>".format(
        erstezeile, folgezeile)

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
    if line['Ausschreibung'] != "":
# --> Anmeldefrist, sofern nicht verstrichen
        if wzukunft: # Anmeldelink generieren
            genwmailto()
        else:
            mailto = ''
        wptable += "<td><b><a href={0}>⇒Beschreibung</a></b>{1}</td>".format(
            line['Ausschreibung'], mailto)
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
source = "./wanderplan.html"
destination = "./archiv/wanderplan" + datetime.datetime.now().strftime("%y%m%d-%H%M%S") +".html"
try:
    shutil.copy(source, destination)
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
except:
    e = sys.exc_info()
    print("Fehler beim Schreiben der HTML-Seite." + e)
