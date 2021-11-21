<?php
	require_once '../dbconfig.php';
	parse_str($_SERVER['QUERY_STRING'],$variables);
	$query = "SELECT `day`,`hour`,`subject`,`room` FROM timetables WHERE `student_id`='{$variables[student_id]}'";	
	foreach($variables as $key => $val) {
		if($key != "limit" AND $key != "student_id" AND !is_array($val)) {

			if($key ==  "day" AND (is_array($variables[hour]))){
				$thereisDay = "true";
				$limit = "true";
				switch ($val) {

					case "Mon":
					  $dayofweek = 1;
					  break;
					case "Tue":
					  $dayofweek = 2;
					  break;
					case "Wed":
					  $dayofweek = 3;
					  break;
					case "Thu":
					  $dayofweek = 4;
					  break;
					case "Fri":
					  $dayofweek = 5;
					  break;
					case "Sat":
					  $dayofweek = 6;
					  break;
					case "Sun":
					  $dayofweek = 0;
					  break;
				}
				$query .= " AND (day_week < {$dayofweek} OR day_week > {$dayofweek} OR (day_week = {$dayofweek}";

			} elseif($key == "day") {
				$query .= " AND day = '{$val}'";
				$thereisDaynoHour = "true";
			} else {
				$query .= " AND {$key}='{$val}'";
			}
		} elseif(is_array($val)) {

			$keys = array_keys($val);
			switch ($keys[0]) {

				case "gt":
				  $query .= " AND {$key} > '{$val[gt]}'";
				  break;

				case "lt":
				  $query .= " AND {$key} < '{$val[lt]}'";
				  $islt = "true";
				  break;

				case "gte":
				  $query .= " AND {$key} >= '{$val[gte]}'";
				  break;

				case "lte":
				  $query .= " AND {$key} <= '{$val[lte]}'";
				  $islt = "true";
				  break;
			}
		}
	}

        if($thereisDay == "true") {
		if($islt != "true"){
			$query .= ")) ORDER BY CASE WHEN (day_week = {$dayofweek}) THEN day_week - 10";
			$query .= " WHEN (day_week - {$dayofweek} < 0) THEN day_week + 10";
			$query .= " ELSE (day_week) END, hour";

		} elseif($islt == "true") {

			$query .= ")) ORDER BY CASE WHEN (day_week = {$dayofweek}) THEN day_week + 10";
                        $query .= " WHEN (day_week - {$dayofweek} < 0) THEN day_week + 10";
                        $query .= " ELSE (day_week-10) END DESC, hour DESC";
		}

	} elseif($thereisDaynoHour == "true") {

		$query .= " ORDER BY day_week, hour";
	} elseif($limit != "true") {
		$query .= " ORDER BY CASE WHEN (day_week = DAYOFWEEK(CURDATE())-1 AND hour < CURRENT_TIME) THEN day_week + 7";
		$query .= " WHEN (day_week - DAYOFWEEK(CURDATE())+1 < 0) THEN day_week + DAYOFWEEK(CURDATE())";
		$query .= " ELSE (day_week - DAYOFWEEK(CURDATE())) END";
	}

	if(array_key_exists("limit",$variables)) {
		$query .= " LIMIT {$variables[limit]}";
	} else if($limit == "true") {
		$query .= " LIMIT 1";
	}
	$result = mysqli_query($connection, $query) or die("Error in Selecting " . mysqli_error($connection));
	$emparray = array();
	while($row =mysqli_fetch_assoc($result)) {
        	$emparray[] = $row;
	}
	echo json_encode(['timetables' => $emparray]);
	mysqli_close($connection);
?>
