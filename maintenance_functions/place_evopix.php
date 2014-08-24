<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
<title>Place Evopix</title>
</head>
<body>
<?php
/************************************************************************/
/*This function will grab all of the evopix from the database,          */
/*and place them in the world, starting at 0,0 and essentially          */
/*spiraling outward to fill the rest.                                   */
/************************************************************************/

/* comment out the next line to run script*/
die("Hold it there tiger, make sure you actually want to run this function, becuase it will seriously bung up the database."); 
include('../includes/header.php');
set_time_limit(2000);
ini_set('memory_limit','1G');
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
//place_evopix("test_land_unit");

function place_evopix($world)
	{
	//reset all of the land units to evopic_id=NULL before proceeding, so there aren't any conflicts in the database (evopic_id is indexed unique).
	mysql_query("update ".$world." set evopic_id=null;");
	
	$evopic_query = mysql_query("SELECT * FROM evopix");
	$land_unit_query = mysql_query("SELECT * FROM ".$world);
	$land_unit_array = array();
	
	while ($row = mysql_fetch_assoc($land_unit_query))
		{
		$next_array = array("sum"=>(abs($row['x_coord'])+abs($row['y_coord'])),"x_coord"=>$row['x_coord'],"y_coord"=>$row['y_coord'],"land_type"=>$row['land_type']);
		array_push($land_unit_array,$next_array);		
		}
	
	$land_unit_array = sort_multi_array($land_unit_array,'sum'); 

	foreach($land_unit_array as $row)
		{
		//echo $row['sum']." - ".$row['x_coord']." - ".$row['y_coord']."<br />";
		if(! $next_evopic = mysql_fetch_assoc($evopic_query))
			{break;}		
		if(mt_rand(1,10) > 2 && $row['land_type'] == 3)
			{
			mysql_query("update ".$world." set evopic_id=".$next_evopic['ID']." where x_coord=".$row['x_coord']." and y_coord=".$row['y_coord'].";") or die("Oops, this died with: ".mysql_error()."<br />Full SQL used: update ".$world." set evopic_id=".$next_evopic['ID']." where x_coord=".$row['x_coord']." and y_coord=".$row['y_coord'].";");	
			}
		}	
	}

echo "<br />completed in ". (time() - $time)/60 ." minutes";	

//grabbed this off the internet
function sort_multi_array ($array, $key)
{
  $keys = array();
  for ($i=1;$i<func_num_args();$i++) {
    $keys[$i-1] = func_get_arg($i);
  }

  // create a custom search function to pass to usort
  $func = function ($a, $b) use ($keys) {
    for ($i=0;$i<count($keys);$i++) {
      if ($a[$keys[$i]] != $b[$keys[$i]]) {
        return ($a[$keys[$i]] < $b[$keys[$i]]) ? -1 : 1;
      }
    }
    return 0;
  };

  usort($array, $func);

  return $array;
}
?>

</body>
</html>