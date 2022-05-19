<?php
echo "Wanderplan-Generierung<br>";
# exec("/opt/RZpython3/bin/python3 wanderplan.py 2>&1", $out, $result);
# exec("/opt/RZpython3/bin/python3 -m pip install pandas 2>&1", $out, $result);
# exec("/opt/RZpython3/bin/python3 -m pip install openpyxl 2>&1", $out, $result);
# exec("export PATH=~/.local/bin:$PATH 2>&1", $out, $result);
# exec("echo $PATH 2>&1", $out, $result);
# exec("pwd 2>&1", $out, $result);
# exec("ls -l 2>&1", $out, $result);
exec("/usr/bin/python3 wanderplan.py 2>&1", $out, $result);
echo "Returncode: " .$result ."<br>";
echo "Ausgabe des Scripts: " .$out ."<br>";
# echo "<pre>"; print_r($out);
?>