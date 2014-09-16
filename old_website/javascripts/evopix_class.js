// JavaScript Document
function evopic($parsed_json_string,$world_canvas,$fill_defs)
	{
	this.$properties_array = $parsed_json_string; //Includes => 'ID', 'parent1', 'parent2', 'user_id', 'name', 'birth_date', 'hype', 'breeder', 'evp_file', 'land_id'
	
	this.$min_max = this.find_min_max(); //returns {min_x, min_y, max_x, max_y}
	
	this.set_gradients($world_canvas,$fill_defs);
	this.$svg = this.evp2svg($world_canvas);
	
	this.scale = function ($minX, $maxX)
		{
		var $range_output = $maxX-$minX;	
		var $range_this_guy = this.$min_max.max_x - this.$min_max.min_x;	
		return ($range_output/$range_this_guy);	
		}
	
	}


evopic.prototype.find_min_max = function()
	{
	var $min_x=false;
	var $min_y;
	var $max_x;
	var $max_y;
	var $paths_array = this.$properties_array['evp_file'].split("p");
	$paths_array.shift();
	
	var coord = function (x,y) 
		{
		if(!x) var x=0;
		if(!y) var y=0;
		return {x: x, y: y};
		}
		
	function B1(t) { return t*t*t }
	function B2(t) { return 3*t*t*(1-t) }
	function B3(t) { return 3*t*(1-t)*(1-t) }
	function B4(t) { return (1-t)*(1-t)*(1-t) }
	
	function getBezier(percent,C1,C2,C3,C4) 
		{
		var pos = new coord();
		pos.x = C1.x*B1(percent) + C2.x*B2(percent) + C3.x*B3(percent) + C4.x*B4(percent);
		pos.y = C1.y*B1(percent) + C2.y*B2(percent) + C3.y*B3(percent) + C4.y*B4(percent);
		return pos;
		}
	
	var find_bez_min_max = function($input_curve)
		{
		//start by setting min/max to some valid point on the curve. In this case, e1.
		var $minX=$input_curve.e1.x, $minY=$input_curve.e1.y, $maxX=$input_curve.e1.x, $maxY=$input_curve.e1.y;	
		
		for(var $i=0; $i <= 100; $i++)
			{
			var $position = getBezier(($i/100),$input_curve.e1,$input_curve.c1,$input_curve.c2,$input_curve.e2);
			$minX = $position.x < $minX ? $position.x : $minX;
			$minY = $position.y < $minY ? $position.y : $minY;
			$maxX = $position.x > $maxX ? $position.x : $maxX;
			$maxY = $position.y > $maxY ? $position.y : $maxY;	
			}
		
		return {min_x:$minX,min_y:$minY,max_x:$maxX,max_y:$maxY};
		}
		
	var bezier_points = function($e1,$c1,$c2,$e2)
		{
		if(!$e1 || !$c1 || !$c2 || !$e2)
			{return false;}
		var min_x = Math.min($e1.x,$c1.x,$c2.x,$e2.x);
		var min_y = Math.min($e1.y,$c1.y,$c2.y,$e2.y);
		var max_x = Math.max($e1.x,$c1.x,$c2.x,$e2.x);
		var max_y = Math.max($e1.y,$c1.y,$c2.y,$e2.y);
		return{e1:$e1,c1:$c1,c2:$c2,e2:$e2,min_x:min_x,min_y:min_y,max_x:max_x,max_y:max_y}		
		}
	
	var split_evp_points = function($point)
		{
		var $temp;
		var $coords_array = $point.split(";");	
		$temp = $coords_array[1].split(",");
		var $control_left = new coord($temp[0],$temp[1]);
		$temp = $coords_array[2].split(",");
		var $end = new coord($temp[0],$temp[1]);
		$temp = $coords_array[3].split(",");
		var $control_right = new coord($temp[0],$temp[1]);
		return{left:$control_left,right:$control_right,end:$end};
		}
	
	var $first = false; //totally did not do a good job designing evp format, need to store first point
	for(var $i = 0; $i < $paths_array.length; $i++)
		{	
		var $points_match = $paths_array[$i].match(/t[;.,\r\n\dt\-]*/).toString();
		var $points_array = $points_match.split('t');
		$points_array.shift();
		
		var $next_t;
		
		//I'm going to assume that the furthest point, whether control or end, will generate the furthest curve. Not necessarily true, but will hopefully be a good enough approximation.		
		var $coords_array;
		for(var $j= 0; $j < $points_array.length; $j++)
			{
			$coords_array = new split_evp_points($points_array[$j]);
			if($first == false)
				{
				$first = {e1:0,c1:$coords_array.left,c2:$coords_array.right,e2:$coords_array.end};	
				$next_t = {e2:$coords_array.end};				
				continue;
				}
			
			$next_t = new bezier_points ($next_t.e2,$coords_array.left,$coords_array.right,$coords_array.end);
			
			if($min_x == false)
				{
				//set all min/max to the first curve, and just go from there
				$min_x = $next_t;
				$min_y = $next_t;
				$max_x = $next_t;
				$max_y = $next_t;	
				}
					
			//check/set min/max
			$min_x = $next_t.min_x < $min_x.min_x ? $next_t : $min_x;
			$min_y = $next_t.min_y < $min_y.min_y ? $next_t : $min_y;
			$max_x = $next_t.max_x > $max_x.max_x ? $next_t : $max_x;
			$max_y = $next_t.max_y > $max_y.max_y ? $next_t : $max_y;			
			}
		
		//deal with last point
		$next_t = new bezier_points ($next_t.e2,$first.c1,$first.c2,$first.e2);
			
		//check/set min/max
		$min_x = $next_t.min_x < $min_x.min_x ? $next_t : $min_x;
		$min_y = $next_t.min_y < $min_y.min_y ? $next_t : $min_y;
		$max_x = $next_t.max_x > $max_x.max_x ? $next_t : $max_x;
		$max_y = $next_t.max_y > $max_y.max_y ? $next_t : $max_y;	 	
		}
	
	//changing the data type of min/max x/y a couple times here, to widdle down to final output
	$min_x = new find_bez_min_max($min_x);
	$min_x = $min_x.min_x;
	
	$min_y = new find_bez_min_max($min_y);
	$min_y = $min_y.min_y;
	
	$max_x = new find_bez_min_max($max_x);
	$max_x = $max_x.max_x;
	
	$max_y = new find_bez_min_max($max_y);
	$max_y = $max_y.max_y;
	
	return {min_x:$min_x, min_y:$min_y, max_x:$max_x, max_y:$max_y};
	}	
	

evopic.prototype.scale = function()
	{
		
	}
	

evopic.prototype.set_gradients = function($world_canvas,$fill_defs)
	{
	//find the paths, and save in array				
	var $each_path = this.$properties_array['evp_file'].split("p");
	
	var $num_paths = $each_path.length;
	var $j_lim = $num_paths-1;
	
	//find linear and radial gradient definitions and output to <defs>
	for (var $j=1; $j<=$j_lim; $j++)
		{
		var $path_id = $each_path[$j].match(/[0-9]+/);
		var $obj_type = $each_path[$j].match(/[rn]/);
	
		if ($obj_type[0] == "r")
			{
			var $grad_type = $each_path[$j].match(/[gl]/);
			var $fill_loc_coords = $each_path[$j].match(/[gl].+/);
			var $fill_loc = $fill_loc_coords[0].split(",");
			
			var $fill_info = $each_path[$j].match(/o.+/);
			var $each_fill = $fill_info[0].split("o");
			var $num_fills = ($each_fill.length)-1;
			
			var $stops_output = new Array;
			for (var $k=1; $k<=$num_fills; $k++)
				{
				$stops_output[$k-1] = new Array;
				var $fill_values = $each_fill[$k].split(",");
				//each stop gets ['opacity','colour','offset']	
				$stops_output[$k-1] = [$fill_values[3] + "%","#" + $fill_values[1],$fill_values[2]];   		
				}
			if($grad_type[0] == "l")
				{
			//linearGradient(parent, id, stops, x1, y1, x2, y2, settings)
			$world_canvas.linearGradient($fill_defs,this.$properties_array['ID'] + "linearGradient" + $path_id[0],$stops_output,$fill_loc[1]+"%",$fill_loc[2] + "%",$fill_loc[3] + "%",$fill_loc[4] + "%");
				}
				
			if($grad_type[0] == "g")
				{
				//radialGradient(parent, id, stops, cx, cy, r, fx, fy, settings)	
				$world_canvas.radialGradient($fill_defs,this.$properties_array['ID'] + 'radialGradient' + $path_id[0],$stops_output,$fill_loc[5]+'%',$fill_loc[6]+'%',$fill_loc[9]+'%',$fill_loc[7]+'%',$fill_loc[8]+'%');						
				}
			}
		}	
	}

evopic.prototype.evp2svg = function($world_canvas)
	{
	//find the paths, and save in array	
	//NOTE!!! The evopic group object returned is set at display:'none', so needs to be displayed			
	var $each_path = this.$properties_array['evp_file'].split("p");
	var $evopic_group = $world_canvas.group("evopic_"+this.$properties_array['ID']); //group(parent, id, settings)
	
	var $num_paths = $each_path.length;
	var $j_lim = $num_paths-1;
		
	//find information for each path, and loop into output
	for ($j=1; $j<=$j_lim; $j++)
		{	
		var $path_id = $each_path[$j].match(/[0-9]+/);
		var $grad_type = $each_path[$j].match(/[gl]/);
		var $obj_type = $each_path[$j].match(/[rn]/);
		var $stroke_info = $each_path[$j].match(/s.+z/);
		$stroke_info = $stroke_info[0].match(/[\d,.\-]+/);
		var $stroke_info_array = $stroke_info[0].split(",");
					
		//Find the points making up the path
		var $path_points = $each_path[$j].match(/t[;.,\r\dt\-]*/);
		$path_points[0] = $path_points[0].substr(0,($path_points[0].length-1));
		
		//Add path points to an array nested in $each_path
		var $each_point = $path_points[0].split("t");
		var $num_points = $each_point.length-1;
	
		//find and output the first two values of the path
		var $first_point = $each_point[1].split(";");
		
		var $svg_output = "M ";		
		if ($obj_type[0] == "r")
			{
			$svg_output += $first_point[2] + " C " + $first_point[3];
		
			var $i_lim = $num_points;
			for (var $i=2; $i<=$i_lim; $i++)
				{
				var $each_coord = $each_point[$i].split(";");
			
				$svg_output += " " + $each_coord[1] + " " + $each_coord[2] + " C " + $each_coord[3];   
				}
		
			$svg_output += " " + $first_point[1] + " " + $first_point[2] + " z";
			
			var $gradient_string = $grad_type[0] == "g" ? "url(#" + this.$properties_array['ID'] + "radialGradient" + $path_id[0] + ")" : "url(#" + this.$properties_array['ID'] + "linearGradient" + $path_id[0] + ")";			
			
			$world_canvas.path($evopic_group,$svg_output,{fill:$gradient_string,fillRule:'evenodd',stroke:'#' + $stroke_info_array[0],strokeWidth:$stroke_info_array[1],strokeOpacity:$stroke_info_array[2]});				
			}
	
		else if ($obj_type[0] == "n")
			{
			$svg_output += $first_point[1] + " C " + $first_point[2];
			var $i_lim = $num_points-1;
			var $each_coord;
			
			for ($i=2; $i<=$i_lim; $i++)
				{
				$each_coord = $each_point[$i].split(";");
				$svg_output += " " + $each_coord[1] + " " + $each_coord[2] + " C " + $each_coord[3];   
				}
		
			$each_coord = $each_point[$i_lim+1].split(";");
			$svg_output += " " + $each_coord[1] + " " + $each_coord[2] + "'";
			
			$world_canvas.path($evopic_group,$svg_output,{fill:'none',stroke:'#'+$stroke_info_array[0],strokeWidth:$stroke_info_array[1],strokeOpacity:$stroke_info_array[2]});
			}		
		}	
	return $evopic_group;
	}

function coords($x,$y)
	{
	var main_x = is_int($x) ? $x : 0;
	var main_y = is_int($y) ? $y : 0;
	
	this.set = function($newX,$newY)
		{
		main_x = is_int($newX) ? $newX : 0;
		main_y = is_int($newY) ? $newY : 0;	
		}
	
	this.x = function()
		{
		return main_x;	
		}
	
	this.y = function()
		{
		return main_y;	
		}
	}

function is_int($input)
	{
	return (typeof($input)=='number' && parseInt($input)==$input);
	}