// JavaScript Document
function evopic($id)
	{
	var farm_location = new coords();
	
	_initialize = function()
		{
			
		}
		
		
		
		
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