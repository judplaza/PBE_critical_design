<?php
        require_once '../dbconfig.php';
        parse_str($_SERVER['QUERY_STRING'],$variables);

        $query = "SELECT `date`,`subject`,`name` FROM `tasks` WHERE `student_id`='{$variables[student_id]}'";
        if(count($variables)>0){
                foreach($variables as $key => $val){
                        if($key !="limit" AND $key!="student_id"){
                                if(!is_array($val)){
                                        $query.=" AND `{$key}`='{$val}'";
                                }else{
                                        if($val[gte]!="now"){
                                                $query.=" AND `date`>='{$val[gte]}'";
                                        }else{
                                                $query.=" AND `date`>=CURRENT_DATE";
                                        }
                                }
                        }
                }
        }
        $query .= " ORDER BY `date` ASC";
        if(array_key_exists("limit",$variables)){
                $query.= " LIMIT {$variables[limit]}";
        }
        $result = mysqli_query($connection,$query) or die("Error in Selecting " .mysqli_error($connection));
        $emparray = array();
        while($row = mysqli_fetch_assoc($result)){
                $emparray[] = $row;
        }
        echo json_encode(['tasks'=>$emparray]);
        mysqli_close($connection);
?>