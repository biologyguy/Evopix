<?php
function new_evopix ()
	{
	$evopix_id=fopen("evopix_id.txt","r+") or exit("evopix_id.txt file not found");

	$last_num=fgets($evopix_id);
	fseek($evopix_id,0);
	$new_id = $last_num + 1;
	fwrite($evopix_id,$new_id);
	$new_evopix=fopen("svg_files/".$new_id.".svg","w+");		

	//echo "New EvoPix created and named ".$new_id.".svg <br />"; 

	$template=fopen("conversion_output.txt","r") or exit("conversion_output.txt file not found");

	$template_contents=file_get_contents("conversion_output.txt");
	
	fwrite($new_evopix,$template_contents);

	//	echo "<object type='image/svg+xml' data='svg_files/".$new_id.".svg' width='1000' height='1000'></object>";
		


	fclose($evopix_id);
	fclose($new_evopix);
	fclose($template);

	}
?>