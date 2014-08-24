<?php
include("includes/header.php");
$evopic_query = mysql_query("SELECT evopix.*, test_land_unit.land_id, test_land_unit.x_coord, test_land_unit.y_coord, test_land_unit.land_type, test_land_unit.colour, test_land_unit.fog FROM `evopix` 
							JOIN test_land_unit on test_land_unit.evopic_id = evopix.ID
							WHERE (test_land_unit.x_coord <= 7 
							AND test_land_unit.x_coord >= -7
							AND test_land_unit.y_coord <= 7 
							AND test_land_unit.y_coord >= -7);");
$evopic_array = array();
while ($row = mysql_fetch_assoc($evopic_query))
	{
	array_push($evopic_array,$row);	
	}

$evopic_json = json_encode($evopic_array);
?>
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>Farm</title>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
    <link rel='shortcut icon' href='/favicon.ico'>
    <link href="includes/styles.css" rel="stylesheet" type="text/css" media="all" />
	<script type="text/javascript" src="https://ajax.googleapis.com/ajax/libs/jquery/1.8.2/jquery.min.js"></script>
    <script type="text/javascript" src="javascripts/jquery.svg.min.js"></script>
	<script type="text/javascript" src="javascripts/jquery.svgdom.min.js"></script>
    <script type="text/javascript" src="javascripts/jquery.svganim.min.js"></script>
    <script type="text/javascript" src="javascripts/JQueryUI/jquery-ui.custom.min.js"></script>
    <script language="javascript" type="application/javascript" src="javascripts/evopix_class.js"></script>
    <script language="javascript" type="application/javascript" src="javascripts/land_unit_class.js"></script>
    <script language="javascript" type="application/javascript">
    $(document).ready(function() 
        {	
		$('div#world_canvas').svg();
		var $world_canvas = $('#world_canvas').svg('get');
		//need to include a script to the svg canvas that allows me to drag elements around
		//$world_canvas.script('<?php include('javascripts/svg_drag.js'); ?>');
		var $fill_defs = $world_canvas.defs('fill_defs');
		var $land_group = $world_canvas.group('land_group');
		var $evopic_array = new Array;
		var $parsed_json_array = <?php echo $evopic_json ?>;
		
		for (var $i = 0; $i < $parsed_json_array.length; $i++)
			{
			/*if ($parsed_json_array[$i]['ID'] == 34146)
				{$('#error').val($parsed_json_array[$i]['evp_file']);}*/
			var $evopic = new evopic($parsed_json_array[$i],$world_canvas,$fill_defs);	
			var $evopic_scale =  $evopic.scale(0,80);		
			//NOTE: translation equation (to account for isometric positioning) => ChangeX = (1/2 width)*(X+Y), ChangeY = (Y-X)*(1/4 width)

			
			var $trans_x = (80*(parseInt($evopic.$properties_array['x_coord'])+parseInt($evopic.$properties_array['y_coord']))+320)/$evopic_scale;
			var $trans_y = (40*(parseInt($evopic.$properties_array['y_coord'])-parseInt($evopic.$properties_array['x_coord']))+320)/$evopic_scale;
			
			var $land_unit = $world_canvas.path($land_group,"M -40,40 40,0 120,40 40,80 z",{id:'land_'+$evopic.$properties_array['land_id'],fill:'green',stroke:'black'});
			
			$world_canvas.change($land_unit,{transform:'translate('+ ($trans_x*$evopic_scale)  +','+ ($trans_y*$evopic_scale) +')'});
			
			$world_canvas.change($evopic.$svg,{transform:'scale('+ $evopic_scale +') translate('+ $trans_x +','+ $trans_y +')'});
			
			
			
			$evopic_array[$parsed_json_array[$i]['ID']] = $evopic;
			}
		
		//$('#error').html($min_max);
		
	   //$world_canvas.script('var makeSVGElementDraggable = svgDrag.setupCanvasForDragging(document.documentElement,true); var test1 = document.getElementById("evopic_10304"); makeSVGElementDraggable(test1);');
		//$evopic_array[10304].draggable();
		
		
		//$world_canvas.change($bob.$svg,{display:''});
	    //$('#error').html($min_max);
		//$('#error').val($evopic_array[10304].$properties_array['evp_file']);
		//$('#error').val($world_canvas.toSVG($evopic_array[10304].$svg));
        //$('#error').val($('#world_canvas').html());
		});
    </script>

</head>
    <body>
    <img id="background_image" src="images/background_sun.svg"/>
    <img id="background_hills" src="images/background_hills.svg"/>
    <div id="main_content">
    <h1>EvoPix</h1>
    <hr />
	<div id="world_canvas"></div>
    
   <!--<div id="error"></div>-->
   <!--<textarea id='error' cols="110" rows="20"></textarea>-->
	
	<?php 
	include("includes/footer.php"); ?>
    
    </div>
    
    </body>
</html>