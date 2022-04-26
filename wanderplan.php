<?php
exec("/usr/bin/python3 wanderplan.py >& wplog.txt");
echo nl2br(file_get_contents( "wplog.txt" ));
?>