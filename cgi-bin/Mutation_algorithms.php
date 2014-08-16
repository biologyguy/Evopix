
<?php
/*
small variable log
$a, $b, $c, $d $m, $n, $f, $g, $h, $k, $i, $o, $j, $y, $r, 
*/
function mute_alg($incoming)
{
mysql_connect ("localhost", "root", "ggf06hbf");
mysql_select_db("evopix");

$bob = file_get_contents("temp_evp_files/".$incoming.".evp");

$mute_output = fopen("temp_evp_files/".$incoming.".evp","w+");

$paths_array = explode("p",$bob);
$number_paths = count($paths_array);

for($y = $number_paths-1; $y > 0; $y--)
	{
	$paths_array[$y] = trim($paths_array[$y]);
	}

//Path splits
$path_split_mutation_rate = 1/5000;
$path_split_mute_counter = 0;
$m = 0;
$n = 0;
$path_split_for_mute = (abs(sqrt(-2*log(lcg_value()))*cos(2*M_PI*lcg_value())*(pow(2,$n)/$path_split_mutation_rate)));

while ($m == 0)
	{
	if ($number_paths >= $path_split_for_mute) 
		{
		$path_split_mute_counter++;
		$n++;
		$path_split_for_mute = (abs(sqrt(-2*log(lcg_value()))*cos(2*M_PI*lcg_value())*(pow(2,$n)/$path_split_mutation_rate)));
		}	

	else
		{
		$m++;
		}
	}

while ($path_split_mute_counter > 0)
	{
	$which_path = mt_rand(1,$number_paths-1);
		
	$end_path_id = strcspn($paths_array[$which_path],"rn");
	$path_id = substr($paths_array[$which_path],0,$end_path_id+1);
	$path_type = substr($paths_array[$which_path],$end_path_id,1);
	
	$start_path_points = strcspn($paths_array[$which_path],";");
	$end_path_points = strcspn($paths_array[$which_path],"gl");
	$range_path_points = $end_path_points-$start_path_points;
	$path_points = substr($paths_array[$which_path],$start_path_points-2,$range_path_points+1);
	$path_points_array = explode("t",$path_points);
	$num_points = count($path_points_array);
	
	$past_points = substr($paths_array[$which_path],$end_path_points);
	
	$which_point = mt_rand(1,$num_points-2);

// add information back into $paths_array[$which_path], and make a new path with the remainder 	
	$new_path =" ";
	trim($new_path);
		
	for ($f = $num_points-1; $f > $which_point; $f--)
		{
		$new_path = "t".$path_points_array[$f].$new_path;
		}
	
	$old_path = " ";
	trim($old_path);
	
	for ($g = $which_point; $g > 0; $g--)
		{
		$old_path = "t".$path_points_array[$g].$old_path;
		}
	
	$paths_array[$which_path] = $path_id.$old_path.$past_points;
	
	$temp_path_split_array = array();
	
	for($h = $number_paths; $h > $which_path; $h--)
		{
		$temp = end($paths_array);
		array_pop($paths_array);
		array_push ($temp_path_split_array,$temp);
		} 
	
	$number_paths++;
	
	//Access MySQL and retrieve unique new path id
	$db_place_hold = round(10000000000 * lcg_value());
	mysql_query("insert into paths (place_hold) values (".$db_place_hold.");");
	$new_path_id_from_mysql = (mysql_fetch_row(mysql_query("select path_id from paths where place_hold = '".$db_place_hold."';")));
	mysql_query("update paths set place_hold = '0', parent = '".$path_id."', parent_evopic='".$incoming."' where path_id = '".$new_path_id_from_mysql[0]."';");
	
	
	$paths_array[$which_path+1] = ($new_path_id_from_mysql[0]).$path_type.$new_path.$past_points;
		
	$num_in_temp_array = count($temp_path_split_array);
	
	for ($k = 1; $k <= $num_in_temp_array; $k++)
		{
		$temp = end($temp_path_split_array);
		array_pop($temp_path_split_array);
		array_push ($paths_array,$temp);
		} 
	
	$path_split_mute_counter--;
	}


for ($i=1; $i <= $number_paths-1; $i++)
	{
	$end_path_id = strcspn($paths_array[$i],"rn");
	$path_id = substr($paths_array[$i],0,$end_path_id+1);
	
	$start_path_points = strcspn($paths_array[$i],"t");
	$end_path_points = strcspn($paths_array[$i],"gl");
	$range_path_points = $end_path_points-$start_path_points;
	$path_points = substr($paths_array[$i],$start_path_points-1,$range_path_points+1);
	
	$path_points_array = explode("t",$path_points);
	array_shift($path_points_array);	
	
	$num_points = count($path_points_array);

//duplicate a point  -  need to access MySQL here and fetch new point_id (check that this won't kill any of the code)########################################
	$split_point_mutation_rate = 1/3000;
	
	$split_point_mute_counter = 0;
	$m = 0;
	$n = 0;
	$point_splits_for_mute = (abs(sqrt(-2*log(lcg_value()))*cos(2*M_PI*lcg_value())*(pow(2,$n)/$split_point_mutation_rate)));
	
	while ($m == 0)
		{
		if ($num_points >= $point_splits_for_mute) 
			{
			$split_point_mute_counter++;
			$n++;
			$point_splits_for_mute = (abs(sqrt(-2*log(lcg_value()))*cos(2*M_PI*lcg_value())*(pow(2,$n)/$split_point_mutation_rate)));
			
			}	
	
		else
			{
			$m++;
			}
		}
	
	while ($split_point_mute_counter >= 1)
		{
		$split_which_point = mt_rand(1,$num_points);
		$point_split_array = array();
		for($o = $num_points; $o > $split_which_point; $o--)
			{
			$temp = end($path_points_array);
			array_pop($path_points_array);
			array_push ($point_split_array,$temp);
			}

		$num_points++;
		$point_parent_array = explode(";",$path_points_array[$split_which_point-1]);
		
		$path_points_array[$split_which_point-1] = ($point_parent_array[0]).";".$point_parent_array[1].";".$point_parent_array[2].";".$point_parent_array[2]."\r";
		//Fetch a new point id from MySQL, and update the database
		$db_place_hold = round(10000000000 * lcg_value());
		mysql_query("insert into points (place_hold) values (".$db_place_hold.");");
		$new_point_id_from_mysql = (mysql_fetch_row(mysql_query("select point_id from points where place_hold = '".$db_place_hold."';")));
		mysql_query("update points set place_hold = '0', parent = '".$point_parent_array[0]."', parent_evopic='".$incoming."' where point_id = '".$new_point_id_from_mysql[0]."';");

		array_push ($path_points_array,$new_point_id_from_mysql[0].";".$point_parent_array[2].";".$point_parent_array[2].";".$point_parent_array[3]);
		
		for ($o = (count($point_split_array)-1); $o >= 0; $o--)
			{
			array_push ($path_points_array,$point_split_array[$o]);
			}
	
		$split_point_mute_counter--;
		}

	//delete a point
	$delete_point_mute_rate = 1/9000;
	
	$delete_point_mute_counter = 0;
	$m = 0;
	$n = 0;
	$point_deletes_for_mute = (abs(sqrt(-2*log(lcg_value()))*cos(2*M_PI*lcg_value())*(pow(2,$n)/$delete_point_mute_rate)));
	
	while ($m == 0)
		{
		if ($num_points >= $point_deletes_for_mute) 
			{
			$delete_point_mute_counter++;
			$n++;
			$point_deletes_for_mute = (abs(sqrt(-2*log(lcg_value()))*cos(2*M_PI*lcg_value())*(pow(2,$n)/$delete_point_mute_rate)));
			
			}	
	
		else
			{
			$m++;
			}
		}
	
	while ($delete_point_mute_counter >= 1)
		{
		$delete_which_point = mt_rand(1,$num_points);
		$point_delete_array = array();
		for($o = $num_points; $o >= $delete_which_point; $o--)
			{
			$temp = end($path_points_array);
			array_pop($path_points_array);
			array_push ($point_delete_array,$temp);
			}
	
		$num_points--;
							
		for ($o = (count($point_delete_array)-2); $o >= 0; $o--)
			{
			array_push ($path_points_array,$point_delete_array[$o]);
			}
	
		$delete_point_mute_counter--;
		}
		
/*************************************************
Merge points







*************************************************/


//This 'if' statement breaks the current instance of the paths loop if there are zero points, removing the path from the picture 
	
	if ($num_points == 0)
		{
		$booga_booga = 0;
		}
	
	//Point mutations		
	else
		{				
		$mutation_rate = 1/40;
		
		$point_mute_counter = 0;
		$m = 0;
		$n = 0;
		$points_for_mute = (abs(sqrt(-2*log(lcg_value()))*cos(2*M_PI*lcg_value())*(pow(2,$n)/$mutation_rate)));
		
		while ($m == 0)
			{
			if ($num_points >= $points_for_mute) 
				{
				$point_mute_counter++;
				$n++;
				$points_for_mute = (abs(sqrt(-2*log(lcg_value()))*cos(2*M_PI*lcg_value())*(pow(2,$n)/$mutation_rate)));
				
				}	
			else
				{
				$m++;
				}
			}
	
		while ($point_mute_counter >= 1)
			{
//build an array which contains the distance of each pair of coordinate values from the origin (the hypotenuse of a right angle triange) contained in the path
				$ind_points_array = array();
				foreach ($path_points_array as $value_a)
					{
					$a = explode(";",$value_a);
			
					for ($j=1; $j <= 3; $j++)
						{
						$b = explode(",",$a[$j]);	
						$dist_from_zero = sqrt((pow($b[0],2)+pow($b[1],2)));
						array_push($ind_points_array,$dist_from_zero);
						}
					}
				//Some stuff to determine how far the mutated point will move, and in which direction
				$min_point = min($ind_points_array);
				
				$median_point = sqrt(pow((median ($ind_points_array)-$min_point),2)/2);
				$distance_changed = abs((sqrt(-2*log(lcg_value()))*cos(2*M_PI*lcg_value())*($median_point * 0.2)));
				$direction_change = (mt_rand(1,3599999)/10000);
				$change_x = sin(deg2rad($direction_change))*$distance_changed;
				$change_y = cos(deg2rad($direction_change))*$distance_changed;
								
				$change_point = mt_rand(1,$num_points);
				
	//this will mutate only one of: the actual point or its control handels
				if (lcg_value() >= 0.75)
					{
					$mute_point = explode(";",$path_points_array[$change_point-1]);
									
					switch (mt_rand(1,3))
						{
						case 1:
					$mute_point_coord = explode(",",$mute_point[1]);	
					$new_x = $mute_point_coord[0]+$change_x;
					$new_y = $mute_point_coord[1]+$change_y;
					$path_points_array[$change_point-1] = $mute_point[0].";".$new_x.",".$new_y.";".$mute_point[2].";".$mute_point[3]."\r";
					break;
	
						case 2:
					$mute_point_coord = explode(",",$mute_point[2]);	
					$new_x = $mute_point_coord[0]+$change_x;
					$new_y = $mute_point_coord[1]+$change_y;
	
					$path_points_array[$change_point-1] = $mute_point[0].";".$mute_point[1].";".$new_x.",".$new_y.";".$mute_point[3]."\r";
					break;
	
						case 3:
					$mute_point_coord = explode(",",$mute_point[3]);	
					$new_x = $mute_point_coord[0]+$change_x;
					$new_y = $mute_point_coord[1]+$change_y;
					$path_points_array[$change_point-1] = $mute_point[0].";".$mute_point[1].";".$mute_point[2].";".$new_x.",".$new_y."\r";
					break;					
						}
					}
			//this will mutate the actual point and its two control handles equally
				else
					{
					$mute_point = explode(";",$path_points_array[$change_point-1]);
					$new_mute_points_array = array();
				
					for ($k=1; $k <= 3; $k++)
						{
						$mute_point_coords = explode(",",$mute_point[$k]);
						$new_x = $mute_point_coords[0] + $change_x;
						$new_y = $mute_point_coords[1] + $change_y;
						array_push($new_mute_points_array,$new_x,$new_y);
						}
					$path_points_array[$change_point-1] = $mute_point[0].";".$new_mute_points_array[0].",".$new_mute_points_array[1].";".$new_mute_points_array[2].",".$new_mute_points_array[3].";".$new_mute_points_array[4].",".$new_mute_points_array[5]."\r";	
					}
				$point_mute_counter--;			
			}
		fwrite($mute_output,"p".$path_id."\r");
		
		for($y=$num_points-1; $y>=0; $y--)
			{
			$path_points_array[$y] = trim($path_points_array[$y]);
			}
		
		foreach ($path_points_array as $value_b)
			{
			fwrite ($mute_output,"t".$value_b);
			}
		//mutation of gradient type
		$end_path_id = strcspn($paths_array[$i],"rn");
		$path_type = substr($paths_array[$i],$end_path_id,1);
	
		if ($path_type == "r")
			{
			$start_grade_info = (strcspn($paths_array[$i],"gl"));
			$end_grade_info = strcspn($paths_array[$i],"o");
			$range_grade_info = $end_grade_info-$start_grade_info;
			$grade_info = substr($paths_array[$i],$start_grade_info,$range_grade_info-1);			
			$grade_info_array = explode(",",$grade_info);
					
			if (lcg_value() >= 0.99)
				{
				if (lcg_value() > 0.45)
					{
					$grade_info_array[0] = "l";
					}
				else
					{
					$grade_info_array[0] = "g";
					}
				}
		
		//mutation of gradient coordinates 
								
			$r = 1;
	//mutation rate	
			while ($r == 1)
				{
				if (lcg_value() <= 1/500) 
					{
					switch (mt_rand(1,9))
						{
						case 1:
						$change = (sqrt(-2*log(lcg_value()))*cos(2*M_PI*lcg_value()))*2;
						$grade_info_array[1] = $grade_info_array[1]+$change;
						break;
	
						case 2:
						$change = (sqrt(-2*log(lcg_value()))*cos(2*M_PI*lcg_value()))*2;
						$grade_info_array[2] = $grade_info_array[2]+$change;
						break;
	
						case 3:
						$change = (sqrt(-2*log(lcg_value()))*cos(2*M_PI*lcg_value()))*2;
						$grade_info_array[3] = $grade_info_array[3]+$change;
						break;
	
						case 4:
						$change = (sqrt(-2*log(lcg_value()))*cos(2*M_PI*lcg_value()))*2;
						$grade_info_array[4] = $grade_info_array[4]+$change;
						break;
	
						case 5:
						$change = (sqrt(-2*log(lcg_value()))*cos(2*M_PI*lcg_value()))*2;
						$grade_info_array[5] = $grade_info_array[5]+$change;
						break;
	
						case 6:
						$change = (sqrt(-2*log(lcg_value()))*cos(2*M_PI*lcg_value()))*2;
						$grade_info_array[6] = $grade_info_array[6]+$change;
						break;
	
						case 7:
						$change = (sqrt(-2*log(lcg_value()))*cos(2*M_PI*lcg_value()))*2;
						$grade_info_array[7] = $grade_info_array[7]+$change;
						break;
	
						case 8:
						$change = (sqrt(-2*log(lcg_value()))*cos(2*M_PI*lcg_value()))*2;
						$grade_info_array[8] = $grade_info_array[8]+$change;
						break;
	
						case 9:
						$change = (algorithmsqrt(-2*log(lcg_value()))*cos(2*M_PI*lcg_value()))*2;
						$grade_info_array[9] = $grade_info_array[9]+$change;
						break;
						}
		
					}
				else
					{
					$r--;			
					}
				}
			fwrite ($mute_output,$grade_info_array[0].",".$grade_info_array[1].",".$grade_info_array[2].",".$grade_info_array[3].",".$grade_info_array[4].",".$grade_info_array[5].",".$grade_info_array[6].",".$grade_info_array[7].",".$grade_info_array[8].",".$grade_info_array[9].",");
			}
		else
			{	
			fwrite ($mute_output,"l");
			}
		//Stops information
	
		if ($path_type == "r")
			{
			$start_stops = (strcspn($paths_array[$i],"o"));
			$end_stops = strcspn($paths_array[$i],"s");
			$range_stops = $end_stops-$start_stops;
			$stops = substr($paths_array[$i],$start_stops,$range_stops);
			$stops_array = explode("o",$stops);
			$num_stops = count($stops_array)-1;
			
			for ($y = $num_stops; $y > 0; $y--) 
				{
				$stops_array[$y] = trim($stops_array[$y]);
				}
			
			//Duplicate or delete a stop
			$split_stop_mutation_rate = 1/500;
	
			$split_stop_mute_counter = 0;
			$m = 0;
			$n = 0;
			$stop_splits_for_mute = (abs(sqrt(-2*log(lcg_value()))*cos(2*M_PI*lcg_value())*(pow(2,$n)/$split_stop_mutation_rate)));
	
			while ($m == 0)
				{
				if ($num_stops >= $stop_splits_for_mute) 
					{
					$split_stop_mute_counter++;
					$n++;
					$stop_splits_for_mute = (abs(sqrt(-2*log(lcg_value()))*cos(2*M_PI*lcg_value())*(pow(2,$n)/$split_stop_mutation_rate)));
		
					}	
				else
					{
					$m++;
					}
				}
	
			while ($split_stop_mute_counter >= 1)
				{
				$split_which_stop = mt_rand(1,$num_stops);
				$stop_split_array = array();
	//duplicate a stop			
				if (lcg_value() > 0.65)
					{
					for($o = $num_stops; $o > $split_which_stop; $o--)
						{
						$temp = end($stops_array);
						array_pop($stops_array);
						array_push ($stop_split_array,$temp);
						}
	
					$num_stops++;
					
					$parent_stop_id_span = strcspn($stops_array[$split_which_stop],",");
					$parent_stop_id = substr($stops_array[$split_which_stop],0,$parent_stop_id_span);

					$db_place_hold = round(10000000000 * lcg_value());
					mysql_query("insert into stops (place_hold) values (".$db_place_hold.");");
					$new_stop_id_from_mysql = (mysql_fetch_row(mysql_query("select stop_id from stops where place_hold = '".$db_place_hold."';")));
					mysql_query("update stops set place_hold = '0', parent = '".$parent_stop_id."', parent_evopic='".$incoming."' where stop_id = '".$new_stop_id_from_mysql[0]."';");					
						
					$stop_info_sans_id = strpos($stops_array[$split_which_stop],",");
					array_push ($stops_array,$new_stop_id_from_mysql[0].(substr($stops_array[$split_which_stop],$stop_info_sans_id)));
									
					
					for ($o = (count($stop_split_array)-1); $o >= 0; $o--)
						{
						array_push ($stops_array,$stop_split_array[$o]);
						}
					//delete a stop
					}
	
				elseif ($num_stops > 1)
					{
					for($o = $num_stops; $o >= $split_which_stop; $o--)
						{
						$temp = end($stops_array);
						array_pop($stops_array);
						array_push ($stop_split_array,$temp);
						}
	
					$num_stops--;
					
					
					for ($o = (count($stop_split_array)-2); $o >= 0; $o--)
						{
						array_push ($stops_array,$stop_split_array[$o]);
						}
					}
	
				$split_stop_mute_counter--;
				}	
										
	
	
			$mutation_rate = 1/30;
	
	//number of stops recieving mutations
			$stops_mute_counter = 0;
			$m = 0;
			$n = 0;
			$stops_for_mute = (abs(sqrt(-2*log(lcg_value()))*cos(2*M_PI*lcg_value())*(pow(2,$n)/$mutation_rate)));
	
			while ($m == 0)
				{
				if ($num_stops >= $stops_for_mute) 
					{
					$stops_mute_counter++;
	/*350*/					$n++;
					$stops_for_mute = (abs(sqrt(-2*log(lcg_value()))*cos(2*M_PI*lcg_value())*(pow(2,$n)/$mutation_rate)));
					}	
	
				else
					{
					$m++;
					}
				}
			//the part of the stop which is mutated
			while ($stops_mute_counter >= 1)
				{
				$mute_stop = mt_rand(1,$num_stops);
				$single_stop_array = explode(",",$stops_array[$mute_stop]);
				switch (mt_rand(1,3))
					{
					case 1:
	//mutate stop color							
					$change = (sqrt(-2*log(lcg_value()))*cos(2*M_PI*lcg_value()))*20;
					$red = substr($single_stop_array[1],0,2);
					$green = substr($single_stop_array[1],2,2);
					$blue = substr($single_stop_array[1],4,2);
					switch (mt_rand(1,3))
						{
						case 1:
						$change_red = dechex(abs(hexdec($red)+$change));
						if (hexdec($change_red) <= 15)
							{
							$single_stop_array[1] = "0".$change_red.$green.$blue;
							}
						elseif (hexdec($change_red) > 255)
							{
							$overshoot_correction = dechex(255-(hexdec($change_red)-255)); 
							$single_stop_array[1] = $overshoot_correction.$green.$blue;
							}
					
						else 
							{
							$single_stop_array[1] = $change_red.$green.$blue;
							}
						break;
			
						case 2:
						$change_green = dechex(abs(hexdec($green)+$change));
			
						if (hexdec($change_green) <= 15)
							{
							$single_stop_array[1] = $red."0".$change_green.$blue;
							}
							
						elseif (hexdec($change_green) > 255)
							{
							$overshoot_correction = dechex(255-(hexdec($change_green)-255)); 
							$single_stop_array[1] = $red.$overshoot_correction.$blue;
							}
					
						else
							{
							$single_stop_array[1] = $red.$change_green.$blue;
							}
							
						break;
	
						case 3:
						$change_blue = dechex(abs(hexdec($blue)+$change));
				
						if (hexdec($change_blue) <= 15)
							{
							$single_stop_array[1] = $red.$green."0".$change_blue;
							}
							
						elseif (hexdec($change_blue) > 255)
							{
							$overshoot_correction = dechex(255-(hexdec($change_blue)-255)); 
							$single_stop_array[1] = $red.$green.$overshoot_correction;
							}
					
						else
						$single_stop_array[1] = $red.$green.$change_blue;
						break;
						} 
			
								
					break;
	//mutate stop opacity					
					case 2:
					$opacity_change = $single_stop_array[2]+((sqrt(-2*log(lcg_value()))*cos(2*M_PI*lcg_value()))*0.02);
					if ($opacity_change <= 1 && $opacity_change > 0)
						{
						$single_stop_array[2] = $opacity_change;
						}
					
					elseif ($opacity_change < 0)
						{
						$single_stop_array[2] = abs($opacity_change);
						}
	
					else
						{
						$opacity_change = 1-($opacity_change-1);
						$single_stop_array[2] = $opacity_change;
						}
					break;
	//mutate stop location
					case 3:
					$stop_change = $single_stop_array[3]+((sqrt(-2*log(lcg_value()))*cos(2*M_PI*lcg_value()))*2);
					if ($stop_change > 100)
						{
						$stop_change = 100-($stop_change-100);
						$single_stop_array[3] = $stop_change;
						}
			
					else								
						{
						$single_stop_array[3] = abs($stop_change);
						}
					break;
		
					}
				$stops_array[$mute_stop] = $single_stop_array[0].",".$single_stop_array[1].",".$single_stop_array[2].",".$single_stop_array[3].",";
				$stops_mute_counter--;
				}
			fwrite ($mute_output,"\r");
			for ($j = 1; $j < $num_stops+1; $j++)
				{
				fwrite ($mute_output,"o".$stops_array[$j]);
				}
			}
		//stroke information
		$start_stroke = (strcspn($paths_array[$i],"s")+1);
		$end_stroke = strcspn($paths_array[$i],"z");
		$range_stroke = $end_stroke-$start_stroke;
		$stroke = substr($paths_array[$i],$start_stroke,$range_stroke);
		$stroke_array = explode(",",$stroke);
	
	//mutation rate for stroke color
		$r = 1;
		while ($r == 1)
			{
			if (lcg_value() <= (1/250))
				{
				$change = (sqrt(-2*log(lcg_value()))*cos(2*M_PI*lcg_value()))*5;
				$red = substr($stroke_array[0],0,2);
				$green = substr($stroke_array[0],2,2);
				$blue = substr($stroke_array[0],4,2);
				switch (mt_rand(1,3))
					{
					case 1:
					$change_red = dechex(abs(hexdec($red)+$change));
					
					if (hexdec($change_red) <= 15)
						{
						$stroke_array[0] = "0".$change_red.$green.$blue;
						}
					
					elseif (hexdec($change_red) > 255)
						{
						$overshoot_correction = dechex(255-(hexdec($change_red)-255)); 
						$stroke_array[0] = $overshoot_correction.$green.$blue;
						}
						
					else 
						{
						$stroke_array[0] = $change_red.$green.$blue;
						}
						
					break;
				
					case 2:
					$change_green = dechex(abs(hexdec($green)+$change));
					
					if (hexdec($change_green) <= 15)
						{
						$stroke_array[0] = $red."0".$change_green.$blue;
						}
						
					elseif (hexdec($change_green) > 255)
						{
						$overshoot_correction = dechex(255-(hexdec($change_green)-255)); 
						$stroke_array[0] = $red.$overshoot_correction.$blue;
						}
						
					else
						{
						$stroke_array[0] = $red.$change_green.$blue;
						}
					break;
	
					case 3:
					$change_blue = dechex(abs(hexdec($blue)+$change));
					
					if (hexdec($change_blue) <= 15)
						{
						$stroke_array[0] = $red.$green."0".$change_blue;
						}
	
					elseif (hexdec($change_blue) > 255)
						{
						$overshoot_correction = dechex(255-(hexdec($change_blue)-255)); 
						$stroke_array[0] = $red.$green.$overshoot_correction;
						}
						
					else
						{
						$stroke_array[0] = $red.$green.$change_blue;
						}
						
					break;
					}
			//echo "stroke mutation occured";
				}
			else
				{
				$r--;
				}
			}
	//mutation rate for stroke width
		if (lcg_value() <= 1/500)
			{
			$stroke_array[1] = $stroke_array[1] + ((sqrt(-2*log(lcg_value()))*cos(2*M_PI*lcg_value()))*0.2);
			}
				
	//mutation rate for stroke opacity
		if (lcg_value() <= 1/500)
			{
			$stroke_opacity_change = (sqrt(-2*log(lcg_value()))*cos(2*M_PI*lcg_value()))*0.05;
			if (($stroke_opacity_change + $stroke_array[2]) < 0)
				{
				$stroke_array[2] = abs($stroke_opacity_change + $stroke_array[2]);
				}
	
			if (($stroke_opacity_change + $stroke_array[2]) > 1)
				{
				$stroke_array[2] = (1 - (($stroke_opacity_change + $stroke_array[2]) - 1));
				}
	
			else
				{
				$stroke_array[2] = $stroke_array[2] + $stroke_opacity_change;
				}
			}
		
		fwrite ($mute_output,"\rs".$stroke_array[0].",".$stroke_array[1].",".$stroke_array[2]."z\r\r");
		}
	}

fclose($mute_output);

$current_file = file_get_contents("temp_evp_files/".$incoming.".evp");
mysql_query("update evopix set evp_file='".$current_file."' where id = '".$incoming."';");

unlink("temp_evp_files/".$incoming.".evp");
return ($current_file);

}
?>
