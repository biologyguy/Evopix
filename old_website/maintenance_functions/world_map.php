<?php
/************************************************************************/
/*This file contains 3 functions:										*/
/*create_land_units(), build_world(), and set_land_type()				*/
/*These are used to set up the world map								*/
/*It takes about 11 minutes to run set_land_type() on a 1000x1000 grid	*/
/************************************************************************/

/* comment out the next line to run script*/
die("Hold it there tiger, make sure you actually want to run these functions, becuase they could seriously bung up the database."); 
require_once('../../includes/evopix/db_connect.php');
set_time_limit(2000);
$time = time();
?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Untitled Document</title>
</head>

<body>
<?php
//Makes a square world and sets default values.
//create_land_units(50);
function create_land_units($size)
	{
	for($i=-$size;$i <= $size;$i++)
		{
		for($j=-$size;$j <= $size;$j++)
			{
			mysql_query("insert into land_unit (x_coord,y_coord,colour,land_type,fog) values (".$j.",".$i.",'#008000',1,1);");			
			}			
		}	
	}



//Fills in land types, spiralling around the square world, and assigning water (1), beach (2), or land (3), based on the value of ajacent units. When assigning water, there is a random chance of beach. This algorithm is agnostic to whether it has been run previously, but requires that the outer perimeter of the world is already set to water. If continents are going to get much bigger than 1000x1000, then this will need to be rewritten to stop running through the entire algorithm once the entire coast is built.
//build_world(499);   
function build_world($size) //NOTE: Size should be set at half minus 1 the actual lenght of one side of the continent
	{
	for($i=$size; $i >= 1; $i--)
		{
		//from bottom left to top left
		for($j=(-$i); $j < $i; $j++)
			{
			$a = mysql_fetch_assoc(mysql_query("SELECT * FROM land_unit where x_coord=".-$i." and y_coord=".($j-1).";")); //South
			$b = mysql_fetch_assoc(mysql_query("SELECT * FROM land_unit where x_coord=".(-$i-1)." and y_coord=".($j-1).";")); //SouthWest
			$c = mysql_fetch_assoc(mysql_query("SELECT * FROM land_unit where x_coord=".(-$i-1)." and y_coord=".$j.";")); //West
			$d = mysql_fetch_assoc(mysql_query("SELECT * FROM land_unit where x_coord=".(-$i-1)." and y_coord=".($j+1).";")); //NorthWest		
			$x = (-$i);
			$y = ($j);
			set_land_type($a,$b,$c,$d,$x,$y);
			}
		
		//from top left to top right
		for($j=(-$i);$j < $i; $j++)
			{
			$a = mysql_fetch_assoc(mysql_query("SELECT * FROM land_unit where x_coord=".($j-1)." and y_coord=".$i.";")); //West
			$b = mysql_fetch_assoc(mysql_query("SELECT * FROM land_unit where x_coord=".($j-1)." and y_coord=".($i+1).";")); //NorthWest	
			$c = mysql_fetch_assoc(mysql_query("SELECT * FROM land_unit where x_coord=".$j." and y_coord=".($i+1).";")); //North
			$d = mysql_fetch_assoc(mysql_query("SELECT * FROM land_unit where x_coord=".($j+1)." and y_coord=".($i+1).";")); //NorthEast
			$x = ($j);
			$y = ($i);
			set_land_type($a,$b,$c,$d,$x,$y);		
			}
		
		//from top right to bottom right
		for($j=$i;$j > -$i; $j--)
			{
			$a = mysql_fetch_assoc(mysql_query("SELECT * FROM land_unit where x_coord=".$i." and y_coord=".($j+1).";")); //North
			$b = mysql_fetch_assoc(mysql_query("SELECT * FROM land_unit where x_coord=".($i+1)." and y_coord=".($j+1).";")); //NorthEast
			$c = mysql_fetch_assoc(mysql_query("SELECT * FROM land_unit where x_coord=".($i+1)." and y_coord=".$j.";")); //East
			$d = mysql_fetch_assoc(mysql_query("SELECT * FROM land_unit where x_coord=".($i+1)." and y_coord=".($j-1).";")); //SouthEast			
			$x = ($i);
			$y = ($j);
			set_land_type($a,$b,$c,$d,$x,$y);		
			}
		
		//from bottom right to bottom left
		for($j=$i;$j >= -$i+1; $j--)
			{
			$a = mysql_fetch_assoc(mysql_query("SELECT * FROM land_unit where x_coord=".($j+1)." and y_coord=".-$i.";")); //East
			$b = mysql_fetch_assoc(mysql_query("SELECT * FROM land_unit where x_coord=".($j+1)." and y_coord=".(-$i-1).";")); //SouthEast
			$c = mysql_fetch_assoc(mysql_query("SELECT * FROM land_unit where x_coord=".$j." and y_coord=".(-$i-1).";")); //South
			$d = mysql_fetch_assoc(mysql_query("SELECT * FROM land_unit where x_coord=".($j-1)." and y_coord=".(-$i-1).";")); //SouthWest					
			$x = ($j);
			$y = (-$i);
			set_land_type($a,$b,$c,$d,$x,$y);		
			}
		}
	//set the final spots at -1,0 and 0,0 to land
	mysql_query("update land_unit set land_type=3, colour='#008000' where (x_coord=0 and y_coord=0) or (x_coord=0 and y_coord=-1);");
	}

//Note that this function does a really good job building the beach along the sides of the continent, but breaks a bit at the corners. Not worth the time to build in all the extra IFs to properly make the corners though, so they need to be checked and adjusted manually.
function set_land_type($a,$b,$c,$d,$x,$y)
	{
	//if there is no water adjacent, new unit is land
	if($a['land_type'] != 1 && $b['land_type'] != 1 && $c['land_type'] != 1 && $d['land_type'] != 1)
		{
		mysql_query("update land_unit set land_type=3, colour='#008000' where x_coord=".$x." and y_coord=".$y.";");
		return;
		}
	
	//$a is land and $c is water (or vice versa), new unit is beach
	if(($a['land_type'] == 1 && $c['land_type'] == 3) || ($a['land_type'] == 3 && $c['land_type'] == 1))
		{
		mysql_query("update land_unit set land_type=2, colour='#AF7817' where x_coord=".$x." and y_coord=".$y.";");
		return;
		}
	
	//$a and $c are land, new unit is land
	if($a['land_type'] == 3 && $c['land_type'] == 3)
		{
		mysql_query("update land_unit set land_type=3, colour='#008000' where x_coord=".$x." and y_coord=".$y.";");
		return;
		}
	
	//$a is land and $c is beach (or vice versa), new unit is land
	if(($a['land_type'] == 3 && $c['land_type'] == 2) || ($a['land_type'] == 2 && $c['land_type'] == 3))
		{
		mysql_query("update land_unit set land_type=3, colour='#008000' where x_coord=".$x." and y_coord=".$y.";");
		return;
		}
	
	//both $a and $c are beach, new unit is land
	if($a['land_type'] == 2 && $c['land_type'] == 2)
		{
		mysql_query("update land_unit set land_type=3, colour='#008000' where x_coord=".$x." and y_coord=".$y.";");
		return;
		}
	
	//$b or $d are beach, new unit is beach
	if($b['land_type'] == 2 || $d['land_type'] == 2)
		{
		mysql_query("update land_unit set land_type=2, colour='#AF7817' where x_coord=".$x." and y_coord=".$y.";");
		return;
		}
	
	//$a or $c are beach but the other is water, new unit 50% beach, 50% water
	if(($a['land_type'] == 2 || $c['land_type'] == 2) && ($a['land_type'] == 1 || $c['land_type'] == 1))
		{
		$random = round(rand(1,100));
		if($random <=40)
			{
			mysql_query("update land_unit set land_type=2, colour='#AF7817' where x_coord=".$x." and y_coord=".$y.";");
			}
		
		else
			{
			mysql_query("update land_unit set land_type=1, colour='#3333FF' where x_coord=".$x." and y_coord=".$y.";");
			}
			
		return;
		}
	
	//both $a and $c are water, new unit is 20% beach, 80% water
	if($a['land_type'] == 1 && $c['land_type'] == 1)
		{
		$random = round(rand(1,100));
		
		if($random <= 10)
			{
			mysql_query("update land_unit set land_type=2, colour='#AF7817' where x_coord=".$x." and y_coord=".$y.";");
			}
		
		else
			{
			mysql_query("update land_unit set land_type=1, colour='#3333FF' where x_coord=".$x." and y_coord=".$y.";");
			}
			
		return;
		}			
	
	mysql_query("update land_unit set land_type=0, colour='red' where x_coord=".$x." and y_coord=".$y.";");
	}
?>

<table style="table-layout:fixed">
	<?php
	//this loop fills in a 50x50 table, gabbing the land colors from the database
	/*for($i=-50;$i<=50;$i++)
		{
		echo "<col width='15px' />";	
		}
	for($i=50;$i>=-50;$i--)
		{
		echo "<tr height='10px'>";
		for($j=-50;$j<=50;$j++)
			{
			$land_unit = mysql_fetch_assoc(mysql_query("SELECT * FROM land_unit WHERE x_coord=".$j." AND y_coord=".$i.";"));
			echo "<td style='background-color:".$land_unit['colour']."' id='x-y_".$j."-".$i."'></td>";	
			}
		echo "</tr>";
		}*/
    ?>
  </table> 
  <?php echo "Done! It took ".((time()-$time)/60)." minutes"; ?>  
</body>
</html>