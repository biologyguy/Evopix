
<?php
function shift_to_zeros ($evp_file,$scale=0,$output_name="temp_evp.evp")
{

$bob = $evp_file;
$new_bob = fopen("users/".$_COOKIE['login_name']."/".$output_name,"w+");

/*
$bob = file_get_contents("bob.txt");
$new_bob = fopen("new_bob.evp","w+");
$small_bob = fopen("small_bob.evp","w+");
*/

$paths_array = explode("p",$bob);
array_shift($paths_array);

$before_array = array();
$point_coords_array = array();
$grade_stop_array = array();
$stroke_array = array();
$point_id_array = array();
$x_points_array = array();
$y_points_array = array();

foreach($paths_array as $a)
	{
	$end_before = strcspn($a,"rn");
	$before = substr($a,0,$end_before+1);
	array_push($before_array,$before);
//Points stuff	
	$start_path_points = strcspn($a,"t");
	$end_path_points = strcspn($a,"gl");
	$range_path_points = $end_path_points-$start_path_points;
	$path_points = substr($a,$start_path_points,$range_path_points);
	$points_array = explode("t",$path_points);
	array_shift($points_array);
	
	$temp_point_id_array = array();
	$temp_point_coords_array4 = array();
	
	foreach($points_array as $b)
		{
		$end_point_id = strcspn($b,";");
		$point_id = substr($b,0,$end_point_id);
		array_push($temp_point_id_array,$point_id);
		
		$temp_point_coords_array1 = explode(";",$b);
		$temp_point_coords_array3 = array();
		
		for($d=1; $d < 4; $d++)
			{
			$temp_point_coords_array2 = explode(",",$temp_point_coords_array1[$d]);
			array_push ($temp_point_coords_array3,$temp_point_coords_array2[0],$temp_point_coords_array2[1]);
			array_push ($x_points_array,round($temp_point_coords_array2[0]-1));
			array_push ($y_points_array,round($temp_point_coords_array2[1]-1));
			}
		array_push ($temp_point_coords_array4,$temp_point_coords_array3);	
		}
	array_push ($point_id_array,$temp_point_id_array);	
	array_push ($point_coords_array,$temp_point_coords_array4);	
	
	$start_stroke = strcspn($a,"s");
	$range_grade_stop = ($start_stroke - $end_path_points);
	$grade_to_stop = substr($a,$end_path_points,$range_grade_stop);
	//echo "<br/>End path points: ".$end_path_points."<br/>start stroke: ".$start_stroke."<br/>Range: ".$range_grade_stop."<br/>String: ".$grade_to_stop;
	$stroke = substr($a,$start_stroke);
	array_push($grade_stop_array,$grade_to_stop);
	$temp_stroke_array = explode(",",$stroke);
	array_push($stroke_array,$temp_stroke_array);
	
	//make an array storing the median distance from zero of each coordinate in the path
	}

$min_x = min($x_points_array);
$min_y = min($y_points_array);
$max_point = max((max($x_points_array) - $min_x),(max($y_points_array) - $min_y));

if ($scale == 0)
	{
	$scale_factor = 1;
	}
else
	{
	$scale_factor = ($scale/$max_point);
	}
	
$path_counter = 0;

foreach($point_coords_array as $c)
	{
	$point_id_counter = 0;
	fwrite ($new_bob,"p".$before_array[$path_counter]."\r");
	foreach($c as $e)	
		{
		$e[0] = $e[0] - $min_x;
		$e[1] = $e[1] - $min_y;
		$e[2] = $e[2] - $min_x;
		$e[3] = $e[3] - $min_y;
		$e[4] = $e[4] - $min_x;
		$e[5] = $e[5] - $min_y;
		fwrite ($new_bob,"t".$point_id_array[$path_counter][$point_id_counter].";".round(($e[0]*$scale_factor),4).",".round(($e[1]*$scale_factor),4).";".round(($e[2]*$scale_factor),4).",".round(($e[3]*$scale_factor),4).";".round(($e[4]*$scale_factor),4).",".round(($e[5]*$scale_factor),4)."\r");
		$point_id_counter++;
		}
	fwrite ($new_bob,$grade_stop_array[$path_counter].$stroke_array[$path_counter][0].",".round(($stroke_array[$path_counter][1]*$scale_factor),4).",".$stroke_array[$path_counter][2]);
	$path_counter++;
	}
	//print_r ($grade_stop_array);
return ($max_point);
}
?>