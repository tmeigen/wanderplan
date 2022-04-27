<?php
exec("/usr/bin/python3 wanderplan.py >& wplogtmp.txt");
echo nl2br(file_get_contents( "wplogtmp.txt" ));
exec("cat wplogtmp.txt >> wplog.txt");
exec("rm wplogtmp.txt");
?>