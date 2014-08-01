<?php

function evp_to_svg ($id,$max_point,$scale,$input_name="temp_evp.evp")
	{
	//open the relavent file and store its contents
	
	if ($input_name=="temp_evp.evp")
		{
		$output_name = $id;
		}
	else
		{
		$dist = strpos($input_name,".evp");
		$output_name = $id."_".(substr($input_name,0,$dist));
		}
	
	$evp_temp_data = file_get_contents("users/".$_COOKIE['login_name']."/".$input_name);	
	$conv_output = fopen("users/".$_COOKIE['login_name']."/svg_files/temp/".$output_name.".svg","w+");
	
/*
	$evp_temp_data = file_get_contents("2.evp");
	$small_evp_temp_data = file_get_contents("2_small.evp");
	$evp_temp_data_array = array($evp_temp_data, $small_evp_temp_data);
	
	$conv_output = fopen("1.svg","w+");
	$conv_output_small = fopen("1_small.svg","w+");
	$which_output_array = array($conv_output,$conv_output_small);
*/

	
	//output header information
	fwrite($conv_output,"<?xml version=\"1.0\" encoding=\"UTF-8\" standalone=\"no\"?>
	<svg xmlns:svg=\"http://www.w3.org/2000/svg\" xmlns=\"http://www.w3.org/2000/svg\"
	xmlns:xlink=\"http://www.w3.org/1999/xlink\" version=\"1.0\"
	 width=\"".$scale."\" height=\"".$scale."\" id=\"svg2232\">\r\r<defs>\r");
	
	
	//find the paths, and save in array				
	$each_path = explode("p",$evp_temp_data);
	
	//find linear and radial gradient definitions and output
	
	$num_paths = count($each_path);
	$j_lim = $num_paths-1;
	
	//The Linear Gradients are outputed in this loop
	for ($j=1; $j<=$j_lim; $j++)
		{
		$end_path_id = strcspn($each_path[$j],"rn");		
		$path_id = substr($each_path[$j],0,$end_path_id);
		$obj_type = substr($each_path[$j],$end_path_id,1);
	
		if ($obj_type == "r")
			{
			$start_fill_loc = strcspn($each_path[$j],"gl");
			$end_fill_loc = strcspn($each_path[$j],"o");
			$range_fill_loc = $end_fill_loc-$start_fill_loc;
		
			$fill_loc_coords = substr($each_path[$j],$start_fill_loc,$range_fill_loc);
		
			$fill_loc=explode(",",$fill_loc_coords);
		
			fwrite($conv_output,"<linearGradient id=\"linearGradient".$path_id."\" x1=\"".$fill_loc[1]."%\" y1=\"".$fill_loc[2]."%\" x2=\"".$fill_loc[3]."%\" y2=\"".$fill_loc[4]."%\">");			
			
			$start_fill_info=strcspn($each_path[$j],'o');
			$end_fill_info=strcspn($each_path[$j],'s');
			$range_fill_info=$end_fill_info-$start_fill_info;
		
			$fill_info=substr($each_path[$j],$start_fill_info,$range_fill_info);
		
			$each_fill=explode("o",$fill_info);
			$num_fills=count($each_fill)-1;
		
			for ($k=1; $k<=$num_fills; $k++)
				{
					$fill_values=explode(",",$each_fill[$k]);
					fwrite($conv_output,"\r\t<stop stop-color=\"#".$fill_values[1]."\" stop-opacity=\"".$fill_values[2]."\" offset=\"".$fill_values[3]."%\" />");   
				}
			fwrite($conv_output,"\r</linearGradient>\r\r");
			}
		}
	
	//The Radial Gradients are outputed in this loop
	for ($j=1; $j<=$j_lim; $j++)
		{
		$end_path_id = strcspn($each_path[$j],'rn');
		$path_id = substr($each_path[$j],0,$end_path_id);	
		$obj_type = substr($each_path[$j],$end_path_id,1);
		
		if ($obj_type == "r")
			{
			$start_fill_loc = strcspn($each_path[$j],"gl");
			$end_fill_loc = strcspn($each_path[$j],"o");
			$range_fill_loc = $end_fill_loc-$start_fill_loc;
		
			$fill_loc_coords = substr($each_path[$j],$start_fill_loc,$range_fill_loc);
		
			$fill_loc=explode(",",$fill_loc_coords);
		
			fwrite($conv_output,"<radialGradient id=\"radialGradient".$path_id."\" xlink:href=\"#linearGradient".$path_id."\" cx=\"".$fill_loc[5]."%\" cy=\"".$fill_loc[6]."%\" fx=\"".$fill_loc[7]."%\" fy=\"".$fill_loc[8]."%\" r=\"".$fill_loc[9]."%\" />\r"); 
			}
		}
	
	fwrite($conv_output,"</defs>\r\r");
		
	//find information for each path, and loop into output
	for ($j=1; $j<=$j_lim; $j++)
		{	
		// Find-write path id number, and begining of path tag
		
		$end_path_id = strcspn($each_path[$j],'rn');
		
		$path_id = substr($each_path[$j],0,$end_path_id);   					
			
		fwrite($conv_output,"<path id = \"path".$path_id."\" d=\"M \r"); 
		
		//Find the points making up the path
		$start_path_points = strcspn($each_path[$j],'t');
		$end_path_points = strcspn($each_path[$j],'gl');
		$range_path_points = $end_path_points-$start_path_points;
		
		$path_points = substr($each_path[$j],$start_path_points,$range_path_points); 			
	
		//Add path points to an array nested in $each_path
		$each_point=explode("t",$path_points);
		$num_points=count($each_point)-1;
	
		//find and output the first two values of the path
		$first_point=explode(";",$each_point[1]);
		
		$obj_type = substr($each_path[$j],$end_path_id,1);
		
		if ($obj_type == "r")
	
			{
			fwrite($conv_output,$first_point[2]." C ".$first_point[3]);
		
			$i_lim=$num_points;
			for ($i=2; $i<=$i_lim; $i++)
				{
				$each_coord=explode(";",$each_point[$i]);
			
				fwrite($conv_output," ".$each_coord[1]." ".$each_coord[2]." C ".$each_coord[3]);   
				}
		
			fwrite($conv_output," ".$first_point[1]." ".$first_point[2]." z\"\r");
	
	
			$find_grad_type = strcspn($each_path[$j],"gl");
			$grad_type = substr($each_path[$j],$find_grad_type,1);
			
			$start_stroke_info = strcspn($each_path[$j],'s');
			$end_stroke_info = strcspn($each_path[$j],'z');
			$range_stroke_info = $end_stroke_info-$start_stroke_info;
			
			$stroke_info = substr($each_path[$j],$start_stroke_info+1,$range_stroke_info-1);
			$stroke_info_array = explode(",",$stroke_info);
	
			if ($grad_type == "g")
				{
				fwrite($conv_output," style=\"fill:url(#radialGradient".$path_id.");fill-rule:evenodd;stroke:#".$stroke_info_array[0].";stroke-width:".$stroke_info_array[1].";stroke-opacity:".$stroke_info_array[2]."\" />\r\r");
				}
				
			elseif ($grad_type == "l")
				{
				fwrite($conv_output," style=\"fill:url(#linearGradient".$path_id.");fill-rule:evenodd;stroke:#".$stroke_info_array[0].";stroke-width:".$stroke_info_array[1].";stroke-opacity:".$stroke_info_array[2]."\" />\r\r");
				}
	
			else
				{
				echo "Can't find gradient type";
				}
			}
	
		elseif ($obj_type == "n")
			{
			fwrite($conv_output,$first_point[1]." C ".$first_point[2]);
			$i_lim=$num_points-1;
			
			for ($i=2; $i<=$i_lim; $i++)
				{
				$each_coord=explode(";",$each_point[$i]);
				fwrite($conv_output," ".$each_coord[1]." ".$each_coord[2]." C ".$each_coord[3]);   
				}
		
			$each_coord=explode(";",$each_point[$i_lim+1]);
			fwrite($conv_output," ".$each_coord[1]." ".$each_coord[2]."\"");
			
			$start_stroke_info = strcspn($each_path[$j],'s');
			$end_stroke_info = strcspn($each_path[$j],'z');
			$range_stroke_info = $end_stroke_info-$start_stroke_info;
		
			$stroke_info = substr($each_path[$j],$start_stroke_info+1,$range_stroke_info-1);
			$stroke_info_array = explode(",",$stroke_info);
		
			fwrite($conv_output," style=\"fill:none;stroke:#".$stroke_info_array[0].";stroke-width:".$stroke_info_array[1].";stroke-opacity:".$stroke_info_array[2]."\" />\r\r");
	
			}
	
	
		else
			{
			echo "no 'r' or 'n' found to describe object type";
			}
	
		}
	 
	fwrite($conv_output,"</svg>");
	fclose($conv_output);
	
	}

?>