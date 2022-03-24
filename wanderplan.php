<?php
echo "Wanderplan-Generierung<br>";
exec("/usr/bin/python3 wanderplan.py 2>&1", $out, $result);
echo "Returncode: " .$result ."<br>";
echo "Ausgabe des Scripts: " ."<br>";
echo "<pre>"; print_r($out);
?>