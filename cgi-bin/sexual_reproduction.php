
<?php
/*Small variable log
$a, $b, $c, $d, $e, $f, $g, $h, $i, $j, $k, $l, $m, $n, $o, $p, $q, $r, $s, $t, $u
*/
function sex_repo ($mom,$dad)
{
//create arrays with all the attributes of parent 1


$paths_array_p1 = explode("p",$mom);
$num_paths_p1 = count($paths_array_p1);

$path_id_array_p1 = array();
$point_id_array_p1 = array();
$point_coords_array_p1 = array();
$num_points_per_path_array_p1 = array();
$num_stops_per_path_array_p1 = array();
$stop_parameters_array_p1 = array();
$stop_id_array_p1 = array();
$grade_parameters_array_p1 = array();
$stroke_parameters_array_p1 = array();
$median_array_p1 = array();
$median_array_p2 = array();
$path_type_array_p1 = array();
$path_type_array_p2 = array();

for($a = 1; $a < $num_paths_p1; $a++)
	{
	$end_path_id = strcspn($paths_array_p1[$a],"rn");
	$path_id = substr($paths_array_p1[$a],0,$end_path_id);
	$path_type = substr($paths_array_p1[$a],$end_path_id,1);
	array_push($path_id_array_p1,$path_id);
	array_push($path_type_array_p1,$path_type);
		
//Points stuff	
	$start_path_points = strcspn($paths_array_p1[$a],"t");
	$end_path_points = strcspn($paths_array_p1[$a],"gl");
	$range_path_points = $end_path_points-$start_path_points;
	$path_points = substr($paths_array_p1[$a],$start_path_points,$range_path_points);
	$points_array_p1 = explode("t",$path_points);
	$num_points_p1 = count($points_array_p1);
	$temp_point_id_array1 = array();
	array_push($num_points_per_path_array_p1,($num_points_p1-1));
	$temp_point_coords_array4 = array();
	$dist_from_zero_array_for_median = array();
	
	
	for($b = 1; $b < $num_points_p1; $b++)
		{
		$end_point_id = strcspn($points_array_p1[$b],";");
		$point_id = substr($points_array_p1[$b],0,$end_point_id);
		array_push($temp_point_id_array1,$point_id);
		$temp_point_coords_array1 = explode(";",$points_array_p1[$b]);
		$temp_point_coords_array3 = array();
		
		for($d=1; $d < 4; $d++)
			{
			$temp_point_coords_array2 = explode(",",$temp_point_coords_array1[$d]);
			array_push ($temp_point_coords_array3,$temp_point_coords_array2[0],$temp_point_coords_array2[1]);
			$dist_from_zero = sqrt((pow($temp_point_coords_array2[0],2)+pow($temp_point_coords_array2[1],2)));
			array_push($dist_from_zero_array_for_median,$dist_from_zero);
			}
		array_push ($temp_point_coords_array4,$temp_point_coords_array3);	
		}
	array_push ($point_id_array_p1,$temp_point_id_array1);	
	array_push ($point_coords_array_p1,$temp_point_coords_array4);	
	
	//make an array storing the median distance from zero of each coordinate in the path
	$path_minimum = min($dist_from_zero_array_for_median);
	$path_median = median($dist_from_zero_array_for_median)-$path_minimum;
	array_push($median_array_p1,$path_median);
	
	
//Gradient stuff
	if ($path_type == "r")
		{
		$start_grade = strcspn($paths_array_p1[$a],"gl");
		$end_grade = strcspn($paths_array_p1[$a],"o");
		$range_grade = $end_grade-$start_grade;
		$grade = substr($paths_array_p1[$a],$start_grade,$range_grade);
		$grade_type_p1 = substr($paths_array_p1[$a],$start_grade,1);
		$grade_parameters_p1 = explode(",",$grade);
		array_pop($grade_parameters_p1);
		array_push($grade_parameters_array_p1,$grade_parameters_p1);
		

//Stops stuff
		$start_stops = strcspn($paths_array_p1[$a],"o");
		$end_stops = strcspn($paths_array_p1[$a],"s");
		$range_stops = $end_stops-$start_stops;
		$stops = substr($paths_array_p1[$a],$start_stops,$range_stops);
		$stops_array = explode("o",$stops);
		$num_stops = count($stops_array)-1;
		array_push($num_stops_per_path_array_p1,$num_stops);
		$temp_stop_params_array = array();
		$temp_stop_id_array = array();
				
		for($c = 1; $c <= $num_stops; $c++)
			{
			$stop_parameters = explode(",",$stops_array[$c]);
			array_pop($stop_parameters);
			array_push($temp_stop_params_array,$stop_parameters);
			array_push($temp_stop_id_array,$stop_parameters[0]);
			}
		array_push($stop_parameters_array_p1,$temp_stop_params_array);
		array_push($stop_id_array_p1,$temp_stop_id_array);
		}
		
	else
		{
		array_push($grade_parameters_array_p1,"blank");
		array_push($stop_parameters_array_p1,"blank");
		array_push($stop_id_array_p1,"blank");
		}
		
		
//stroke stuff
	$start_stroke = (strcspn($paths_array_p1[$a],"s"))+1;
	$end_stroke = strcspn($paths_array_p1[$a],"z");
	$range_stroke = $end_stroke-$start_stroke;
	$grade = substr($paths_array_p1[$a],$start_stroke,$range_stroke);
	$stroke_parameters_p1 = explode(",",$grade);
	array_push($stroke_parameters_array_p1,$stroke_parameters_p1);
				
	}
//End of parent 1 stuff


// Create arrays for all the atributes of parent 2

$paths_array_p2 = explode("p",$dad);
$num_paths_p2 = count($paths_array_p2);

$path_id_array_p2 = array();
$point_id_array_p2 = array();
$point_coords_array_p2 = array();
$num_points_per_path_array_p2 = array();
$num_stops_per_path_array_p2 = array();
$stop_parameters_array_p2 = array();
$stop_id_array_p2 = array();
$grade_parameters_array_p2 = array();
$stroke_parameters_array_p2 = array();

for($a = 1; $a < $num_paths_p2; $a++)
	{
	$end_path_id = strcspn($paths_array_p2[$a],"rn");
	$path_id = substr($paths_array_p2[$a],0,$end_path_id);
	$path_type = substr($paths_array_p2[$a],$end_path_id,1);
	array_push($path_id_array_p2,$path_id);
	array_push($path_type_array_p2,$path_type);
		
//Points stuff	
	$start_path_points = strcspn($paths_array_p2[$a],"t");
	$end_path_points = strcspn($paths_array_p2[$a],"gl");
	$range_path_points = $end_path_points-$start_path_points;
	$path_points = substr($paths_array_p2[$a],$start_path_points,$range_path_points);
	$points_array_p2 = explode("t",$path_points);
	$num_points_p2 = count($points_array_p2);
	$temp_point_id_array1 = array();
	array_push($num_points_per_path_array_p2,($num_points_p2-1));
	$temp_point_coords_array4 = array();
	$dist_from_zero_array_for_median = array();
	
	for($b = 1; $b < $num_points_p2; $b++)
		{
		$end_point_id = strcspn($points_array_p2[$b],";");
		$point_id = substr($points_array_p2[$b],0,$end_point_id);
		array_push($temp_point_id_array1,$point_id);
		$temp_point_coords_array1 = explode(";",$points_array_p2[$b]);
		$temp_point_coords_array3 = array();
		
		for($d=1; $d < 4; $d++)
			{
			$temp_point_coords_array2 = explode(",",$temp_point_coords_array1[$d]);
			array_push ($temp_point_coords_array3,$temp_point_coords_array2[0],$temp_point_coords_array2[1]);
			$dist_from_zero = sqrt((pow($temp_point_coords_array2[0],2)+pow($temp_point_coords_array2[1],2)));
			array_push($dist_from_zero_array_for_median,$dist_from_zero);
			}
		array_push ($temp_point_coords_array4,$temp_point_coords_array3);
		}
	array_push ($point_coords_array_p2,$temp_point_coords_array4);
	array_push ($point_id_array_p2,$temp_point_id_array1);
	
	//make an array storing the median distance from zero of each coordinate in the path
	$path_minimum = min($dist_from_zero_array_for_median);
	$path_median = median($dist_from_zero_array_for_median)-$path_minimum;
	array_push($median_array_p2,$path_median);
	
//Gradient stuff
	if ($path_type == "r")
		{
		$start_grade = strcspn($paths_array_p2[$a],"gl");
		$end_grade = strcspn($paths_array_p2[$a],"o");
		$range_grade = $end_grade-$start_grade;
		$grade = substr($paths_array_p2[$a],$start_grade,$range_grade);
		$grade_type_p2 = substr($paths_array_p2[$a],$start_grade,1);
		$grade_parameters_p2 = explode(",",$grade);
		array_pop($grade_parameters_p2);
		array_push($grade_parameters_array_p2,$grade_parameters_p2);
		

//Stops stuff
		$start_stops = strcspn($paths_array_p2[$a],"o");
		$end_stops = strcspn($paths_array_p2[$a],"s");
		$range_stops = $end_stops-$start_stops;
		$stops = substr($paths_array_p2[$a],$start_stops,$range_stops);
		$stops_array = explode("o",$stops);
		$num_stops = count($stops_array)-1;
		array_push($num_stops_per_path_array_p2,$num_stops);
		$temp_stop_params_array = array();
		$temp_stop_id_array = array();
				
		for($c = 1; $c <= $num_stops; $c++)
			{
			$stop_parameters = explode(",",$stops_array[$c]);
			array_pop($stop_parameters);
			array_push($temp_stop_params_array,$stop_parameters);
			array_push($temp_stop_id_array,$stop_parameters[0]);
			}
		array_push($stop_parameters_array_p2,$temp_stop_params_array);
		array_push($stop_id_array_p2,$temp_stop_id_array);
		}
	else
		{
		array_push($grade_parameters_array_p2,"blank");
		array_push($stop_parameters_array_p2,"blank");
		array_push($stop_id_array_p2,1000000);
		}				
		
//stroke stuff
	$start_stroke = (strcspn($paths_array_p2[$a],"s"))+1;
	$end_stroke = strcspn($paths_array_p2[$a],"z");
	$range_stroke = $end_stroke-$start_stroke;
	$grade = substr($paths_array_p2[$a],$start_stroke,$range_stroke);
	$stroke_parameters_p2 = explode(",",$grade);
	array_push($stroke_parameters_array_p2,$stroke_parameters_p2);
				
	}
//End of parent #2 stuff



//Compare paths 
//Create a new array with the common path ids, and delete those ids from the original arrays
$common_paths_array = array_intersect($path_id_array_p1,$path_id_array_p2);

//Create an array which contains the wieght of each path (based on #points in path vs. total #point), this will be used as the 'base similarity score'. 
$total_num_coords = 0;
foreach($point_coords_array_p1 as $f)
	{
	foreach($f as $g)
		{
		$total_num_coords = $total_num_coords + (count($g));		
		}
	}

foreach($point_coords_array_p2 as $f)
	{
	foreach($f as $g)
		{
		$total_num_coords = $total_num_coords + (count($g));
		}
	}
	
$path_weight_array_p1 = array();
foreach($num_points_per_path_array_p1 as $h)
	{
	array_push($path_weight_array_p1,($h*6/$total_num_coords));
	}

$path_weight_array_p2 = array();
foreach($num_points_per_path_array_p2 as $h)
	{
	array_push($path_weight_array_p2,($h*6/$total_num_coords));
	}


//Create a temp path id arrays from which common paths can be deleted
$unique_path_id_array_p1 = array();
foreach ($path_id_array_p1 as $i)
	{
	array_push($unique_path_id_array_p1,$i);
	}
	
$unique_path_id_array_p2 = array();
foreach ($path_id_array_p2 as $i)
	{
	array_push($unique_path_id_array_p2,$i);
	}

//Remove the common paths from the temp id arrays
foreach ($common_paths_array as $remove)
	{
	$delete_from_p1  = array_search($remove,$unique_path_id_array_p1);
	array_splice($unique_path_id_array_p1,$delete_from_p1,1);
	$delete_from_p2  = array_search($remove,$unique_path_id_array_p2);
	array_splice($unique_path_id_array_p2,$delete_from_p2,1);
	}

//Identify the unique paths, and reduce their similarity score to zero from the path wieght arrays
foreach($unique_path_id_array_p1 as $j)
	{
	$unique_id = array_search ($j,$path_id_array_p1);
	$path_weight_array_p1[$unique_id] = 0;
	}

foreach($unique_path_id_array_p2 as $j)
	{
	$unique_id = array_search ($j,$path_id_array_p2);
	$path_weight_array_p2[$unique_id] = 0;
	}

//compare the points (70%), stops (20%), gradient (5%), and stroke (5%) between common paths, and modify the similarity score as is appropriate
foreach ($common_paths_array as $k)
	{
	$common_path_p1 = array_search ($k,$path_id_array_p1);
	$common_path_p2 = array_search ($k,$path_id_array_p2);
			
	//find the common points in the common paths
	$common_points_array = array_intersect($point_id_array_p1[$common_path_p1],$point_id_array_p2[$common_path_p2]);
	
	//Determine the similarity between the common points
	$point_similarity_array = array();
	foreach ($common_points_array as $p)
		{
		$common_point_p1 = array_search ($p, $point_id_array_p1[$common_path_p1]);
		$common_point_p2 = array_search ($p, $point_id_array_p2[$common_path_p2]);
		
		//Find the distance between each of the three sets of coordinates makeing up the common point
		//control handle1
		$d_coord1 = sqrt((pow($point_coords_array_p1[$common_path_p1][$common_point_p1][0]-$point_coords_array_p2[$common_path_p2][$common_point_p2][0],2))+(pow($point_coords_array_p1[$common_path_p1][$common_point_p1][1]-$point_coords_array_p2[$common_path_p2][$common_point_p2][1],2)));

		//point the line passes through
		$d_coord2 = sqrt((pow($point_coords_array_p1[$common_path_p1][$common_point_p1][2]-$point_coords_array_p2[$common_path_p2][$common_point_p2][2],2))+(pow($point_coords_array_p1[$common_path_p1][$common_point_p1][3]-$point_coords_array_p2[$common_path_p2][$common_point_p2][3],2)));
		
		//control handel2
		$d_coord3 = sqrt((pow($point_coords_array_p1[$common_path_p1][$common_point_p1][4]-$point_coords_array_p2[$common_path_p2][$common_point_p2][4],2))+(pow($point_coords_array_p1[$common_path_p1][$common_point_p1][5]-$point_coords_array_p2[$common_path_p2][$common_point_p2][5],2)));
		
		//finds the average median distance from zero of the common path
		$this_median = ($median_array_p1[$common_path_p1]+$median_array_p2[$common_path_p2])/2;
		
		//I'm pretending that the median value is equal to 1 standard deviation from zero, then the difference 
		$z_score1 = ($d_coord1/$this_median)/sqrt(2);
		$z_score2 = ($d_coord2/$this_median)/sqrt(2);
		$z_score3 = ($d_coord3/$this_median)/sqrt(2);
		
		//this is an approximation of the 'error function' (erf), which gives a normal distribution 
		$point_sim1 = sqrt(1-(pow(M_E,(-(pow((2*$z_score1)/M_SQRTPI,2))))));
		$point_sim2 = sqrt(1-(pow(M_E,(-(pow((2*$z_score2)/M_SQRTPI,2))))));
		$point_sim3 = sqrt(1-(pow(M_E,(-(pow((2*$z_score3)/M_SQRTPI,2))))));
		
		//tally up the total similarity score for the point and push into an array
		$point_sim_tally = ((1-$point_sim1)+(1-$point_sim2)+(1-$point_sim3))/3;
		array_push($point_similarity_array,$point_sim_tally);
		}
		
	//tally up total weight of all the points
	$num_points_in_common_path = $num_points_per_path_array_p1[$common_path_p1]+$num_points_per_path_array_p2[$common_path_p2];
	$final_point_sim_tally = (array_sum($point_similarity_array)*2)/$num_points_in_common_path;
		
	if ($path_type_array_p1[$common_path_p1] == "r")
		{
		//find the common stops in the common paths
		$common_stops_array = array_intersect($stop_id_array_p1[$common_path_p1],$stop_id_array_p2[$common_path_p2]);
		
		//Determine the similarity between the common stops
		$stop_similarity_array = array();
		foreach ($common_stops_array as $q)
			{
			$common_stop_p1 = array_search ($q, $stop_id_array_p1[$common_path_p1]);
			$common_stop_p2 = array_search ($q, $stop_id_array_p2[$common_path_p2]);
			
			//determine the difference in colour of each stop
			$red_p1 = hexdec(substr($stop_parameters_array_p1[$common_path_p1][$common_stop_p1][1],0,2));
			$green_p1 = hexdec(substr($stop_parameters_array_p1[$common_path_p1][$common_stop_p1][1],2,2));
			$blue_p1 = hexdec(substr($stop_parameters_array_p1[$common_path_p1][$common_stop_p1][1],4,2));
			
			$red_p2 = hexdec(substr($stop_parameters_array_p2[$common_path_p2][$common_stop_p2][1],0,2));
			$green_p2 = hexdec(substr($stop_parameters_array_p2[$common_path_p2][$common_stop_p2][1],2,2));
			$blue_p2 = hexdec(substr($stop_parameters_array_p2[$common_path_p2][$common_stop_p2][1],4,2));
			
			$red_sim = 1-(abs($red_p1 - $red_p2)/255);
			$green_sim = 1-(abs($green_p1 - $green_p2)/255);
			$blue_sim = 1-(abs($blue_p1 - $blue_p2)/255);
			
			$stop_sim = ($red_sim + $green_sim + $blue_sim)/3;
			
			
			//determine the difference in stop opacity
			$opacity_sim = 1 - abs($stop_parameters_array_p1[$common_path_p1][$common_stop_p1][2] - $stop_parameters_array_p2[$common_path_p2][$common_stop_p2][2]);
			//determine the difference in stop location
			$location_sim = 1 - abs(($stop_parameters_array_p1[$common_path_p1][$common_stop_p1][3]/100) - ($stop_parameters_array_p2[$common_path_p2][$common_stop_p2][3]/100));
						
			array_push ($stop_similarity_array,(($stop_sim + $opacity_sim + $location_sim)/3));
			}
				
		$final_stop_sim_tally = (array_sum($stop_similarity_array)*2)/(count($stop_id_array_p1[$common_path_p1])+count($stop_id_array_p2[$common_path_p2]));
		
		
		//time for the gradient stuff! This is still inside the 'if' statement controlling the stops stuff.
		//once again, use the erf function. Set the 'z_score' to equal (dGrad/100)/sqrt(2)
		$grade_sim_array = array();
		for ($r = 1; $r <= 9; $r++)
			{
			$grade_diff = abs($grade_parameters_array_p1[$common_path_p1][$r] - $grade_parameters_array_p2[$common_path_p2][$r]);
			$z_score_grade = ($grade_diff/100)/sqrt(2);
			$grade_sim = 1-(sqrt(1-(pow(M_E,(-(pow((2*$z_score_grade)/M_SQRTPI,2)))))));
			array_push($grade_sim_array,$grade_sim);
			
			}
		$final_grade_sim_tally = array_sum($grade_sim_array)/9;
		
		}
	//Stroke information in this part.
	
	//determine the difference in colour of each stroke
	$red_p1 = hexdec(substr($stroke_parameters_array_p1[$common_path_p1][0],0,2));
	$green_p1 = hexdec(substr($stroke_parameters_array_p1[$common_path_p1][0],2,2));
	$blue_p1 = hexdec(substr($stroke_parameters_array_p1[$common_path_p1][0],4,2));
	
	$red_p2 = hexdec(substr($stroke_parameters_array_p2[$common_path_p2][0],0,2));
	$green_p2 = hexdec(substr($stroke_parameters_array_p2[$common_path_p2][0],2,2));
	$blue_p2 = hexdec(substr($stroke_parameters_array_p2[$common_path_p2][0],4,2));
	
	$red_sim = 1-(abs($red_p1 - $red_p2)/255);
	$green_sim = 1-(abs($green_p1 - $green_p2)/255);
	$blue_sim = 1-(abs($blue_p1 - $blue_p2)/255);
	
	$stroke_color_sim = ($red_sim + $green_sim + $blue_sim)/3;
	
	//Determine differnce in stroke thickness
	$thickness_diff = abs($stroke_parameters_array_p1[$common_path_p1][1] - $stroke_parameters_array_p2[$common_path_p2][1]);
	$z_score_thickness = ($thickness_diff/10)/sqrt(2);
	$thickness_sim = 1-(sqrt(1-(pow(M_E,(-(pow((2*$z_score_thickness)/M_SQRTPI,2)))))));
	
	
	//Determine difference in opacity
	$opacity_sim = 1 - abs($stroke_parameters_array_p1[$common_path_p1][2] - $stroke_parameters_array_p2[$common_path_p2][2]);
	
	//Final stroke sim tally
	$final_stroke_sim_tally = ($stroke_color_sim + $thickness_sim + $opacity_sim)/3;
	
	//Create a similarity score for this path
	$final_path_sim_tally = (0.7 * $final_point_sim_tally) + (0.2 * $final_stop_sim_tally) + (0.05 * $final_grade_sim_tally) + (0.05 * $final_stroke_sim_tally);
	$path_weight_array_p1[$common_path_p1] = $path_weight_array_p1[$common_path_p1] * $final_path_sim_tally;
	$path_weight_array_p2[$common_path_p2] = $path_weight_array_p2[$common_path_p2] * $final_path_sim_tally;
	}	

//Final similarity score between the two EvoPix being compared
$similarity_score = (array_sum($path_weight_array_p2) + array_sum($path_weight_array_p1));


//If the two parents are able to breed, then this is where they do it
if ($similarity_score >= 0.78)
	{
	mysql_connect ("localhost", "root", "ggf06hbf");
	mysql_select_db("evopix");
	$db_place_hold = (10000000000 * lcg_value());
	mysql_query("insert into evopix (place_hold,birth_date,time_in_wild) values (".$db_place_hold.",".time().",".time().");");
	$new_evopic_id_from_mysql = (mysql_fetch_row(mysql_query("select id from evopix where place_hold = '".$db_place_hold."';")));
	mysql_query("update evopix set place_hold = '0' where id = '".$new_evopic_id_from_mysql[0]."';");
	
	$breeding_output = fopen("temp_evp_files/".($new_evopic_id_from_mysql[0]).".evp","w+");
	
	//I'm using the path ID arrays here to identify the order that paths need to fit into the offspring. The values of $path_id_array_p1 are compared to $path_id_array_p2, and if the value is unique, it is slotted into the appropriate location of the copy array 50% of the time. The same is then done comparing p2 to p1.   
	$copy_path_id_array_p1 = array();
	$copy_path_id_array_p2 = array();
	
	foreach ($path_id_array_p1 as $i)
		{
		array_push($copy_path_id_array_p1,$i);
		}
		
	foreach ($path_id_array_p2 as $i)
		{
		array_push($copy_path_id_array_p2,$i);
		}
		
	foreach ($path_id_array_p1 as $s)
		{
		if (in_array($s, $path_id_array_p2))
			{
			$path_id_key_p1 = array_search($s, $copy_path_id_array_p2);
			}
		else
			{
				if(lcg_value() > 0.5)
				{
				array_splice($copy_path_id_array_p2,($path_id_key_p1+1),0,$s);
				$path_id_key_p1++;
				}
			}
		}
	
	foreach ($path_id_array_p2 as $s)
		{
		if (in_array($s, $path_id_array_p1))
			{
			$path_id_key_p2 = array_search($s, $copy_path_id_array_p1);
			}
		else
			{
				if(lcg_value() > 0.5)
				{
				array_splice($copy_path_id_array_p1,($path_id_key_p2+1),0,$s);
				$path_id_key_p2++;
				}
			}
		}
	
	$offspring_path_id_array = array_intersect($copy_path_id_array_p1,$copy_path_id_array_p2);
	
	//Send the new offspring to the breeding output
	foreach ($offspring_path_id_array as $t)
		{
		$current_path_id_p1 = array_search($t,$path_id_array_p1);
		$current_path_id_p2 = array_search($t,$path_id_array_p2);
		
		if (in_array($t,$path_id_array_p1) && in_array($t,$path_id_array_p2))
			{
			$change_factor = lcg_value();
			$reset_change_fact = round(abs((sqrt(-2*log(lcg_value()))*cos(2*M_PI*lcg_value())* 15)));
			fwrite($breeding_output,"p".$t.$path_type_array_p1[$current_path_id_p1]."\r");
			
			//Generate an offspring point ID array for this path
			$copy_point_id_array_p1 = array();
			$copy_point_id_array_p2 = array();
			
			foreach ($point_id_array_p1[$current_path_id_p1] as $i)
				{
				array_push($copy_point_id_array_p1,$i);
				}
				
			foreach ($point_id_array_p2[$current_path_id_p2] as $i)
				{
				array_push($copy_point_id_array_p2,$i);
				}
				
			foreach ($point_id_array_p1[$current_path_id_p1] as $s)
				{
				$point_id_key_p1 = 0;
				$point_id_key_p2 = 0;
				if (in_array($s, $point_id_array_p2[$current_path_id_p2]))
					{
					$point_id_key_p1 = array_search($s, $copy_point_id_array_p2);
					}
				else
					{
						if($change_factor > 0.5)
						{
						array_splice($copy_point_id_array_p2,($point_id_key_p1+1),0,$s);
						$point_id_key_p1++;
						}
					}
				}
			
			foreach ($point_id_array_p2[$current_path_id_p2] as $s)
				{
				if (in_array($s, $point_id_array_p1[$current_path_id_p1]))
					{
					$point_id_key_p2 = array_search($s, $copy_point_id_array_p1);
					}
				else
					{
						if($change_factor < 0.5)
						{
						array_splice($copy_point_id_array_p1,($point_id_key_p2+1),0,$s);
						$point_id_key_p2++;
						}
					}
				}
			
			$offspring_point_id_array = array_intersect($copy_point_id_array_p1,$copy_point_id_array_p2);
			
			//Get all the coordinates for the offspring points, modify them by the change factor, then print to the evp file
			foreach($offspring_point_id_array as $u)
				{
				//Reset $change_factor at a low rate. This will set up a 'linkage' type mechanism that allows for 'recombination' of paths between the parents
							
				if ($reset_change_fact < 1)
					{
					$change_factor = lcg_value();
					$reset_change_fact = round(abs((sqrt(-2*log(lcg_value()))*cos(2*M_PI*lcg_value())* 15)));
					}
				
				$reset_change_fact--;
				
				$current_point_id_p1 = array_search($u,$point_id_array_p1[$current_path_id_p1]);
				$current_point_id_p2 = array_search($u,$point_id_array_p2[$current_path_id_p2]);	
							
				if (in_array($u,$point_id_array_p1[$current_path_id_p1]) && in_array($u,$point_id_array_p2[$current_path_id_p2]))
					{
					$offspring_coord_0 = ($change_factor * (($point_coords_array_p1[$current_path_id_p1][$current_point_id_p1][0])-($point_coords_array_p2[$current_path_id_p2][$current_point_id_p2][0]))) + ($point_coords_array_p2[$current_path_id_p2][$current_point_id_p2][0]);
					
					$offspring_coord_1 = ($change_factor * (($point_coords_array_p1[$current_path_id_p1][$current_point_id_p1][1])-($point_coords_array_p2[$current_path_id_p2][$current_point_id_p2][1]))) + ($point_coords_array_p2[$current_path_id_p2][$current_point_id_p2][1]);
					
					$offspring_coord_2 = ($change_factor * (($point_coords_array_p1[$current_path_id_p1][$current_point_id_p1][2])-($point_coords_array_p2[$current_path_id_p2][$current_point_id_p2][2]))) + ($point_coords_array_p2[$current_path_id_p2][$current_point_id_p2][2]);
					
					$offspring_coord_3 = ($change_factor * (($point_coords_array_p1[$current_path_id_p1][$current_point_id_p1][3])-($point_coords_array_p2[$current_path_id_p2][$current_point_id_p2][3]))) + ($point_coords_array_p2[$current_path_id_p2][$current_point_id_p2][3]);
					
					$offspring_coord_4 = ($change_factor * (($point_coords_array_p1[$current_path_id_p1][$current_point_id_p1][4])-($point_coords_array_p2[$current_path_id_p2][$current_point_id_p2][4]))) + ($point_coords_array_p2[$current_path_id_p2][$current_point_id_p2][4]);
					
					$offspring_coord_5 = ($change_factor * (($point_coords_array_p1[$current_path_id_p1][$current_point_id_p1][5])-($point_coords_array_p2[$current_path_id_p2][$current_point_id_p2][5]))) + ($point_coords_array_p2[$current_path_id_p2][$current_point_id_p2][5]);
					
					fwrite($breeding_output,"t".$u.";".$offspring_coord_0.",".$offspring_coord_1.";".$offspring_coord_2.",".$offspring_coord_3.";".$offspring_coord_4.",".$offspring_coord_5."\r");
					}
					
				elseif(in_array($u,$point_id_array_p1[$current_path_id_p1]))
					{
					fwrite($breeding_output,"t".$u.";".($point_coords_array_p1[$current_path_id_p1][$current_point_id_p1][0]).",".($point_coords_array_p1[$current_path_id_p1][$current_point_id_p1][1]).";".($point_coords_array_p1[$current_path_id_p1][$current_point_id_p1][2]).",".($point_coords_array_p1[$current_path_id_p1][$current_point_id_p1][3]).";".($point_coords_array_p1[$current_path_id_p1][$current_point_id_p1][4]).",".($point_coords_array_p1[$current_path_id_p1][$current_point_id_p1][5]));
					}
					
				elseif(in_array($u,$point_id_array_p2[$current_path_id_p2]))
					{
					fwrite($breeding_output,"t".$u.";".$point_coords_array_p2[$current_path_id_p2][$current_point_id_p2][0].",".$point_coords_array_p2[$current_path_id_p2][$current_point_id_p2][1].";".$point_coords_array_p2[$current_path_id_p2][$current_point_id_p2][2].",".$point_coords_array_p2[$current_path_id_p2][$current_point_id_p2][3].";".$point_coords_array_p2[$current_path_id_p2][$current_point_id_p2][4].",".$point_coords_array_p2[$current_path_id_p2][$current_point_id_p2][5]);
					}
				}
		
			}
		
		elseif(in_array($t,$path_id_array_p1))
			{
			fwrite($breeding_output,"p".$t.$path_type_array_p1[$current_path_id_p1]."\r");
			foreach($point_id_array_p1[$current_path_id_p1] as $u)
				{
				$current_point_id_p1 = array_search($u,$point_id_array_p1[$current_path_id_p1]); 
							
				fwrite($breeding_output,"t".$u.";".$point_coords_array_p1[$current_path_id_p1][$current_point_id_p1][0].",".$point_coords_array_p1[$current_path_id_p1][$current_point_id_p1][1].";".$point_coords_array_p1[$current_path_id_p1][$current_point_id_p1][2].",".$point_coords_array_p1[$current_path_id_p1][$current_point_id_p1][3].";".$point_coords_array_p1[$current_path_id_p1][$current_point_id_p1][4].",".$point_coords_array_p1[$current_path_id_p1][$current_point_id_p1][5]);
				}
			}
		
		elseif(in_array($t,$path_id_array_p2))
			{
			fwrite($breeding_output,"p".$t.$path_type_array_p2[$current_path_id_p2]."\r");
			foreach($point_id_array_p2[$current_path_id_p2] as $u)
				{
				$current_point_id_p2 = array_search($u,$point_id_array_p2[$current_path_id_p2]);
				
				fwrite($breeding_output,"t".$u.";".$point_coords_array_p2[$current_path_id_p2][$current_point_id_p2][0].",".$point_coords_array_p2[$current_path_id_p2][$current_point_id_p2][1].";".$point_coords_array_p2[$current_path_id_p2][$current_point_id_p2][2].",".$point_coords_array_p2[$current_path_id_p2][$current_point_id_p2][3].";".$point_coords_array_p2[$current_path_id_p2][$current_point_id_p2][4].",".$point_coords_array_p2[$current_path_id_p2][$current_point_id_p2][5]);
				}
			}
		
		//Add gradient information if applicable
		if	(in_array($t,$path_id_array_p1) && in_array($t,$path_id_array_p2))
			{
			if ($path_type_array_p1[$current_path_id_p1] == "r")
				{
				if ($change_factor > 0.5)
					{
					$offspring_grade_0 = $grade_parameters_array_p1[$current_path_id_p1][0];
					}
				else 
					{
					$offspring_grade_0 = $grade_parameters_array_p2[$current_path_id_p2][0];
					}
				
				$offspring_grade_1 = ($change_factor * (($grade_parameters_array_p1[$current_path_id_p1][1])-($grade_parameters_array_p2[$current_path_id_p2][1]))) + ($grade_parameters_array_p2[$current_path_id_p2][1]);
				
				$offspring_grade_2 = ($change_factor * (($grade_parameters_array_p1[$current_path_id_p1][2])-($grade_parameters_array_p2[$current_path_id_p2][2]))) + ($grade_parameters_array_p2[$current_path_id_p2][2]);
				
				$offspring_grade_3 = ($change_factor * (($grade_parameters_array_p1[$current_path_id_p1][3])-($grade_parameters_array_p2[$current_path_id_p2][3]))) + ($grade_parameters_array_p2[$current_path_id_p2][3]);
				
				$offspring_grade_4 = ($change_factor * (($grade_parameters_array_p1[$current_path_id_p1][4])-($grade_parameters_array_p2[$current_path_id_p2][4]))) + ($grade_parameters_array_p2[$current_path_id_p2][4]);
				
				$offspring_grade_5 = ($change_factor * (($grade_parameters_array_p1[$current_path_id_p1][5])-($grade_parameters_array_p2[$current_path_id_p2][5]))) + ($grade_parameters_array_p2[$current_path_id_p2][5]);
				
				$offspring_grade_6 = ($change_factor * (($grade_parameters_array_p1[$current_path_id_p1][6])-($grade_parameters_array_p2[$current_path_id_p2][6]))) + ($grade_parameters_array_p2[$current_path_id_p2][6]);
				
				$offspring_grade_7 = ($change_factor * (($grade_parameters_array_p1[$current_path_id_p1][7])-($grade_parameters_array_p2[$current_path_id_p2][7]))) + ($grade_parameters_array_p2[$current_path_id_p2][7]);
				
				$offspring_grade_8 = ($change_factor * (($grade_parameters_array_p1[$current_path_id_p1][8])-($grade_parameters_array_p2[$current_path_id_p2][8]))) + ($grade_parameters_array_p2[$current_path_id_p2][8]);
				
				$offspring_grade_9 = ($change_factor * (($grade_parameters_array_p1[$current_path_id_p1][9])-($grade_parameters_array_p2[$current_path_id_p2][9]))) + ($grade_parameters_array_p2[$current_path_id_p2][9]);
								
				fwrite($breeding_output,$offspring_grade_0.",".$offspring_grade_1.",".$offspring_grade_2.",".$offspring_grade_3.",".$offspring_grade_4.",".$offspring_grade_5.",".$offspring_grade_6.",".$offspring_grade_7.",".$offspring_grade_8.",".$offspring_grade_9.",\r");
				}
			else
				{
				fwrite($breeding_output,"l\r");
				}	
			}
		
		elseif(in_array($t,$path_id_array_p1))
			{
			if ($path_type_array_p1[$current_path_id_p1] == "r")
				{
				$offspring_grade_0 = $grade_parameters_array_p1[$current_path_id_p1][0];
				$offspring_grade_1 = $grade_parameters_array_p1[$current_path_id_p1][1];
				$offspring_grade_2 = $grade_parameters_array_p1[$current_path_id_p1][2];
				$offspring_grade_3 = $grade_parameters_array_p1[$current_path_id_p1][3];
				$offspring_grade_4 = $grade_parameters_array_p1[$current_path_id_p1][4];
				$offspring_grade_5 = $grade_parameters_array_p1[$current_path_id_p1][5];
				$offspring_grade_6 = $grade_parameters_array_p1[$current_path_id_p1][6];
				$offspring_grade_7 = $grade_parameters_array_p1[$current_path_id_p1][7];
				$offspring_grade_8 = $grade_parameters_array_p1[$current_path_id_p1][8];
				$offspring_grade_9 = $grade_parameters_array_p1[$current_path_id_p1][9];
				
				fwrite($breeding_output,$offspring_grade_0.",".$offspring_grade_1.",".$offspring_grade_2.",".$offspring_grade_3.",".$offspring_grade_4.",".$offspring_grade_5.",".$offspring_grade_6.",".$offspring_grade_7.",".$offspring_grade_8.",".$offspring_grade_9.",\r");
				}
			else
				{
				fwrite($breeding_output,"l\r");
				}
			}		
		
		elseif(in_array($t,$path_id_array_p2))
			{
			if ($path_type_array_p2[$current_path_id_p2] == "r")
				{
				$offspring_grade_0 = $grade_parameters_array_p2[$current_path_id_p2][0];
				$offspring_grade_1 = $grade_parameters_array_p2[$current_path_id_p2][1];
				$offspring_grade_2 = $grade_parameters_array_p2[$current_path_id_p2][2];
				$offspring_grade_3 = $grade_parameters_array_p2[$current_path_id_p2][3];
				$offspring_grade_4 = $grade_parameters_array_p2[$current_path_id_p2][4];
				$offspring_grade_5 = $grade_parameters_array_p2[$current_path_id_p2][5];
				$offspring_grade_6 = $grade_parameters_array_p2[$current_path_id_p2][6];
				$offspring_grade_7 = $grade_parameters_array_p2[$current_path_id_p2][7];
				$offspring_grade_8 = $grade_parameters_array_p2[$current_path_id_p2][8];
				$offspring_grade_9 = $grade_parameters_array_p2[$current_path_id_p2][9];
				
				fwrite($breeding_output,$offspring_grade_0.",".$offspring_grade_1.",".$offspring_grade_2.",".$offspring_grade_3.",".$offspring_grade_4.",".$offspring_grade_5.",".$offspring_grade_6.",".$offspring_grade_7.",".$offspring_grade_8.",".$offspring_grade_9.",\r");
				}
			else
				{
				fwrite($breeding_output,"l\r");
				}	
			}
		//put the stop info next
		if	(in_array($t,$path_id_array_p1) && in_array($t,$path_id_array_p2))
			{
			if ($path_type_array_p1[$current_path_id_p1] == "r")
				{
				$copy_stop_id_array_p1 = array();
				$copy_stop_id_array_p2 = array();
				
				foreach ($stop_id_array_p1[$current_path_id_p1] as $i)
					{
					array_push($copy_stop_id_array_p1,$i);
					}
					
				foreach ($stop_id_array_p2[$current_path_id_p2] as $i)
					{
					array_push($copy_stop_id_array_p2,$i);
					}
					
				foreach ($stop_id_array_p1[$current_path_id_p1] as $s)
					{
					$stop_id_key_p1 = 0;
					$stop_id_key_p2 = 0;
					if (in_array($s, $stop_id_array_p2[$current_path_id_p2]))
						{
						$stop_id_key_p1 = array_search($s, $copy_stop_id_array_p2);
						}
					else
						{
							if($change_factor > 0.5)
							{
							array_splice($copy_stop_id_array_p2,($stop_id_key_p1+1),0,$s);
							$stop_id_key_p1++;
							}
						}
					}
				
				foreach ($stop_id_array_p2[$current_path_id_p2] as $s)
					{
					if (in_array($s, $stop_id_array_p1[$current_path_id_p1]))
						{
						$stop_id_key_p2 = array_search($s, $copy_stop_id_array_p1);
						}
					else
						{
							if($change_factor < 0.5)
							{
							array_splice($copy_stop_id_array_p1,($stop_id_key_p2+1),0,$s);
							$stop_id_key_p2++;
							}
						}
					}
				
				$offspring_stop_id_array = array_intersect($copy_stop_id_array_p1,$copy_stop_id_array_p2);
				
				//Get all the parameters of the offspring stops, modify them by the change factor, then print to the evp file
				foreach($offspring_stop_id_array as $u)
					{
					$current_stop_id_p1 = array_search($u,$stop_id_array_p1[$current_path_id_p1]);
					$current_stop_id_p2 = array_search($u,$stop_id_array_p2[$current_path_id_p2]);	
								
					if (in_array($u,$stop_id_array_p1[$current_path_id_p1]) && in_array($u,$stop_id_array_p2[$current_path_id_p2]))
						{
						$red_p1 = hexdec(substr($stop_parameters_array_p1[$current_path_id_p1][$current_stop_id_p1][1],0,2));
						$green_p1 = hexdec(substr($stop_parameters_array_p1[$current_path_id_p1][$current_stop_id_p1][1],2,2));
						$blue_p1 = hexdec(substr($stop_parameters_array_p1[$current_path_id_p1][$current_stop_id_p1][1],4,2));
						
						$red_p2 = hexdec(substr($stop_parameters_array_p2[$current_path_id_p2][$current_stop_id_p2][1],0,2));
						$green_p2 = hexdec(substr($stop_parameters_array_p2[$current_path_id_p2][$current_stop_id_p2][1],2,2));
						$blue_p2 = hexdec(substr($stop_parameters_array_p2[$current_path_id_p2][$current_stop_id_p2][1],4,2));
						
						$offspring_red = dechex(($change_factor * ($red_p1-$red_p2)) + $red_p2);
						if (hexdec($offspring_red) < 16)
							{
							$offspring_red = "0".$offspring_red;
							}
							
						$offspring_green = dechex(($change_factor * ($green_p1-$green_p2)) + $green_p2);
						if (hexdec($offspring_green) < 16)
							{
							$offspring_green = "0".$offspring_green;
							}
						
						$offspring_blue = dechex(($change_factor * ($blue_p1-$blue_p2)) + $blue_p2);
						if (hexdec($offspring_blue) < 16)
							{
							$offspring_blue = "0".$offspring_blue;
							}
						
						$offspring_opacity = ($change_factor*(($stop_parameters_array_p1[$current_path_id_p1][$current_stop_id_p1][2])-($stop_parameters_array_p2[$current_path_id_p2][$current_stop_id_p2][2])))+($stop_parameters_array_p2[$current_path_id_p2][$current_stop_id_p2][2]);
						
						$offspring_stop_loc = ($change_factor*(($stop_parameters_array_p1[$current_path_id_p1][$current_stop_id_p1][3])-($stop_parameters_array_p2[$current_path_id_p2][$current_stop_id_p2][3])))+($stop_parameters_array_p2[$current_path_id_p2][$current_stop_id_p2][3]);
						
						
						fwrite($breeding_output,"o".$u.",".$offspring_red.$offspring_green.$offspring_blue.",".$offspring_opacity.",".$offspring_stop_loc.",\r");
						}
						
					elseif(in_array($u,$stop_id_array_p1[$current_path_id_p1]))
						{
						fwrite($breeding_output,"o".$u.",".$stop_parameters_array_p1[$current_path_id_p1][$current_stop_id_p1][1].",".$stop_parameters_array_p1[$current_path_id_p1][$current_stop_id_p1][2].",".$stop_parameters_array_p1[$current_path_id_p1][$current_stop_id_p1][3].",\r");
						}
						
					elseif(in_array($u,$point_id_array_p2[$current_path_id_p2]))
						{
						fwrite($breeding_output,"o".$u.",".$stop_parameters_array_p2[$current_path_id_p2][$current_stop_id_p2][1].",".$stop_parameters_array_p2[$current_path_id_p2][$current_stop_id_p2][2].",".$stop_parameters_array_p2[$current_path_id_p2][$current_stop_id_p2][3].",\r");
						}
					}
				
				}
			}
		elseif(in_array($t,$path_id_array_p1))
			{
			if ($path_type_array_p1[$current_path_id_p1] == "r")
				{
				foreach($stop_id_array_p1[$current_path_id_p1] as $u)
					{
					$current_stop_id_p1 = array_search($u,$stop_id_array_p1[$current_path_id_p1]); 
								
					fwrite($breeding_output,"o".$u.",".$stop_parameters_array_p1[$current_path_id_p1][$current_stop_id_p1][1].",".$stop_parameters_array_p1[$current_path_id_p1][$current_stop_id_p1][2].",".$stop_parameters_array_p1[$current_path_id_p1][$current_stop_id_p1][3].",\r");
					}
				}	
			}
		
		elseif(in_array($t,$path_id_array_p2))
			{
			if ($path_type_array_p2[$current_path_id_p2] == "r")
				{
				foreach($stop_id_array_p2[$current_path_id_p2] as $u)
					{
					$current_stop_id_p2 = array_search($u,$stop_id_array_p2[$current_path_id_p2]);
					
					fwrite($breeding_output,"o".$u.",".$stop_parameters_array_p2[$current_path_id_p2][$current_stop_id_p2][1].",".$stop_parameters_array_p2[$current_path_id_p2][$current_stop_id_p2][2].",".$stop_parameters_array_p2[$current_path_id_p2][$current_stop_id_p2][3].",\r");
					}
				}	
			}
		//Finally, the stroke info
		if	(in_array($t,$path_id_array_p1) && in_array($t,$path_id_array_p2))
			{
			$red_p1 = hexdec(substr($stroke_parameters_array_p1[$current_path_id_p1][0],0,2));
			$green_p1 = hexdec(substr($stroke_parameters_array_p1[$current_path_id_p1][0],2,2));
			$blue_p1 = hexdec(substr($stroke_parameters_array_p1[$current_path_id_p1][0],4,2));
			
			$red_p2 = hexdec(substr($stroke_parameters_array_p2[$current_path_id_p2][0],0,2));
			$green_p2 = hexdec(substr($stroke_parameters_array_p2[$current_path_id_p2][0],2,2));
			$blue_p2 = hexdec(substr($stroke_parameters_array_p2[$current_path_id_p2][0],4,2)); 
			
			$offspring_red = dechex(($change_factor * ($red_p1-$red_p2)) + $red_p2);
			if (hexdec($offspring_red) < 16)
				{
				$offspring_red = "0".$offspring_red;
				}
				
			$offspring_green = dechex(($change_factor * ($green_p1-$green_p2)) + $green_p2);
			if (hexdec($offspring_green) < 16)
				{
				$offspring_green = "0".$offspring_green;
				}
			
			$offspring_blue = dechex(($change_factor * ($blue_p1-$blue_p2)) + $blue_p2);
			if (hexdec($offspring_blue) < 16)
				{
				$offspring_blue = "0".$offspring_blue;
				}
			
			$offspring_stroke_thickness = ($change_factor * (($stroke_parameters_array_p1[$current_path_id_p1][1])-($stroke_parameters_array_p2[$current_path_id_p2][1]))) + ($stroke_parameters_array_p2[$current_path_id_p2][1]);
			
			$offspring_stroke_opacity = ($change_factor * (($stroke_parameters_array_p1[$current_path_id_p1][2])-($stroke_parameters_array_p2[$current_path_id_p2][2]))) + ($stroke_parameters_array_p2[$current_path_id_p2][2]);
							
			fwrite($breeding_output,"s".$offspring_red.$offspring_green.$offspring_blue.",".$offspring_stroke_thickness.",".$offspring_stroke_opacity."z\r");
			}
			
		
		elseif(in_array($t,$path_id_array_p1))
			{
			fwrite($breeding_output,"s".$stroke_parameters_array_p1[$current_path_id_p1][0].",".$stroke_parameters_array_p1[$current_path_id_p1][1].",".$stroke_parameters_array_p1[$current_path_id_p1][2]."z\r");
			}		
		
		elseif(in_array($t,$path_id_array_p2))
			{
			fwrite($breeding_output,"s".$stroke_parameters_array_p2[$current_path_id_p2][0].",".$stroke_parameters_array_p2[$current_path_id_p2][1].",".$stroke_parameters_array_p2[$current_path_id_p2][2]."z\r");
			}

		fwrite($breeding_output,"\r");		
		}
	//get rid of this IF statement before releasing for real
	/* if ($new_evopic_id_from_mysql[0] % 3 == 0)
		{
		echo "Similarity score: ".round($similarity_score,4);
		} */
	}
else
	{
	/* echo "<h2>These two EvoPix are not able to breed with one another</h2><br/>
	Similarity score of: ".$similarity_score; */
	$return_array = array($similarity_score);
	return ($return_array);
	}

//include ("output_check.php");
$return_array = array($similarity_score,$new_evopic_id_from_mysql[0]);
return ($return_array);
//end function
}
?>

