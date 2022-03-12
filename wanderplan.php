<?php
echo "Wanderplan-Generierung";
exec("/usr/bin/python3 wanderplan.py>&1", $out, $result);
echo "Returncode: " .$result ."<br>";
echo "Ausgabe des Scripts: " ."<br>";
echo "<pre>"; print_r($out);
?>