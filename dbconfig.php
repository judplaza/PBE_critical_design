<?php
$user = "pbe";
$password = "telematica";
$database = "pbe";

$connection = mysqli_connect("localhost","$user","$password","$database") or die("Error " . mysqli_error($connection));
?>
