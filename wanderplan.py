# from cmath import nan
import locale
import sys
import datetime
import pandas as pd

locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8') # zur korrekten Ermittlung des Wochentages

# Import des Wanderplan Excel mit Pandas und Openpyxl:
print("Lese wanderplan.xlsm")
df = pd.read_excel("wanderplan.xlsm", engine='openpyxl')

# Umwandlung der Spalte Datum in String im Format dd.mm.yy und Beseitigung von nan
df['Tag'] = df['Tag'].dt.strftime('%A') # Wochentag
df['Datum'] = df['Datum'].dt.strftime('%d.%m.%Y') # Datum im Format tt.mm.yyyy
df = df.fillna('') # Umwandlung von nan Feldern in leere Strings

# Umwandlung des Dataframes in List of Dicts
wpdata = df.to_dict('records')

# Setzen der Styles
wpstyle = '''
<html lang="de">
<meta charset="UTF-8">
<style>
    #wanderplan {
      font-family: "Open Sans", Arial, Helvetica, sans-serif;
      color: #545454;
      border-collapse: collapse;
      width: 100%;
    }
    
    #wanderplan th {
      padding-top: 8px;
      padding-bottom: 8px;
      text-align: left;
      background-color: #089901;
      color: white;
    }
    
    #wanderplan td, #wanderplan th {
      border: 1px solid #ddd;
      padding: 4px;
    }

    .checkbox {
      background-color: #4CAF50; /* Green */
      border: none;
      color: white;
      padding: 5px 5px;
      text-align: center;
      text-decoration: none;
      display: inline-block;
      margin: 4px 2px;
      cursor: pointer;
    }

    a {color: #089901;}
    a:link {text-decoration: none;}
    a:visited {text-decoration: none;}
    a:hover {text-decoration: underline;}
    a:active {text-decoration: underline;}

    #wanderplan tr:hover {background-color: #ddd;}
</style>
'''

# Header-Zeile
wptable = '''
<p style="font-family: Arial, Helvetica, sans-serif;">Stand: 07.02.2022</p>
<table id="wanderplan">
<thead><tr>
  <th style=\"text-align:center;\">Datum</th>
  <th>Veranstaltung </b>(bisherige einblenden: <input type="checkbox" id="historie" onchange="historie"()>)<b></th>
  <th>Art</th>
  <th>Wanderführung/<br>Organisation</th>
  <th>Details/Links</th>
</tr></thead>
<tbody>
</body>
</html>
'''

# Füllen der Tabellenzellen je Spalte
print("Generiere HTML-Tabelle.")
for line in wpdata[0:]:
  # Filtern vergangener Termine
  try:
    wpdatum = datetime.datetime.strptime(line['Datum'], '%d.%m.%Y')
    if wpdatum > datetime.datetime.today(): wzukunft = True
    else: wzukunft = False
  except ValueError:
    print("Seltsamer Formatfehler bei 1blu Hoster => Abbruch")
    break

  if wzukunft: wptable += '<tr>'
  else: wptable += '<tr class=\"noshow\" style=\"display:none; color:grey\">' # ausblenden alter Termine

  # Datumspalte
  wptable += "<td style=\"text-align:center;\"><b>{0}<br>{1}</b></td>" \
    .format(line['Tag'],line['Datum'])

  # Veranstaltungspalte
  folgezeile = line['Veranstaltung 2 '].strip()
  if wzukunft: # für künftige Termine ggf Treffpunkt und Corona-Regeln hinzufügen
    if line['Treffpunkt'] != "": folgezeile += " - Treffpunkt: " + line['Treffpunkt']
    if line['Corona-Regeln'] != "": folgezeile += ", " + line['Corona-Regeln']
  wptable += "<td><b>{0}</b><br>{1}</td>".format(line['Veranstaltung'].strip(),folgezeile)

  # Art: Link auf Icon
  wptable += "<td><img src=\"./icons/{0}xs.png\"></td>".format(line['Icon'].strip())
  
  # Wanderführer
  if line['WFKW'] != '':
    wptable += '<td>LW: {0}<BR>KW: {1}</td>'.format(line['WF'], line['WFKW'])
  else:
    wptable += '<td>{0}</td>'.format(line['WF'])
  
  # Ausschreibung mit Link
  if line['Ausschreibung'] != "":
    wptable += "<td><b><a href={0}>⇒ Beschreibung</a></b></td>".format(line['Ausschreibung'].strip())
  else:
    wptable += '<td></td>'
  
  wptable += "</tr>\n"
wptable += "</tbody></table>"

# Script für das Ein-/Ausblenden vergangener Veranstaltungen anhängen
wptable += '''
<script type="text/javascript">
const historie = document.getElementById('historie')
historie.addEventListener('change', (event) => {
  var myClasses = document.querySelectorAll('.noshow');
    i = 0;
    l = myClasses.length;
  for (i; i < l; i++) {
    if (document.getElementById('historie').checked) {
      myClasses[i].style.display="table-row";}
    else {
      myClasses[i].style.display="none";
      }
    }
  }
)
</script>'''

# Anlegen der Ziel-HTML
print("Schreibe wanderplan.html mit {0} Veranstaltungen.".format(len(wpdata)))
print(wpstyle + wptable )
wpout = open("wanderplan.html", "w")
try:
  wpout.writelines(wpstyle + wptable)
except:
  e = sys.exc_info()
  print("Fehler beim Schreiben der HTML-Seite." + e)
wpout.close()