<?php
        require_once '../dbconfig.php';
        parse_str($_SERVER['QUERY_STRING'],$variables);

        $query = "SELECT * FROM `marks` WHERE `student_id`='{$variables[student_id]}' ORDER BY `marks`.`subject` ASC";
        if(count($variables) > 0) {
                foreach($variables as $key => $val) {
                        if($key != "limit" AND $key != "student_id") {
                                $query .= " AND {$key}='{$val}'";
                        }
                }
        }
        if(array_key_exists("limit",$variables)) {
                $query .= " LIMIT {$variables[limit]}";
        }
        $result = mysqli_query($connection, $query) or die("Error in Selecting " . mysqli_error($connection));
        $emparray = array();
        while($row =mysqli_fetch_assoc($result)) {
                $emparray[] = $row;
        }

        echo json_encode(['marks' => $emparray]);
        mysqli_close($connection);
?>