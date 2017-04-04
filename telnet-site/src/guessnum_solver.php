<?php
function isValidNumber($n){
	for ($i = 0; $i < 3; $i++) {
		if (strpos($n, $n[$i]) != strrpos($n, $n[$i])){
			return false;
		}
	}
	return true;
}
function compare($n0, $n1){
	$a = $b = 0;
	for ($i = 0; $i < 4; $i++) {
		if ($n0[$i] == $n1[$i]) {
			$a++;
		} else {
			for ($j = 0; $j < 4; $j++) {
				if ($n0[$i] == $n1[$j] && $i != $j) {
					$b++;
				}
			}
		}
	}
	return (($a<<4)|$b);
}

if (isset($_POST['submit_data'])) {
	$input_all = array();
	foreach($_POST['num'] as $i => $num){
		if (preg_match('/^\d{4}$/', $num) && isValidNumber($num)) {
			$input_all[] = array('num'=>$num, 'result'=>intval($_POST['result'][$i]));
		}
	}

	$selected_num=array();
	for ($nn = 123; $nn <= 9876; $nn++) {
		$n = sprintf('%04d', $nn);
		if (!isValidNumber($n)) {
			continue;
		}
		$selected = true;
		foreach($input_all as $input){
			if ($input['result'] != compare($n, $input['num'])){
				$selected = false;
				break;
			}
		}
		if ($selected){
			$selected_num[]=$n;
		}
	}
}
?><!DOCTYPE html>
<html>
	<head>
		<meta charset='utf-8'/>
		<title>Bulls and Cows Solver</title>
	</head>
	<body>
		<h1>Bulls and Cows Solver</h1>
		<form method='post' action='guessnum_solver.php'>
			<input type='hidden' name='submit_data' value='yes'/>
			<div><?php for ($i=0; $i<8; $i++) { ?>
					<input type='text' name='num[]' value='<?=isset($input_all[$i])?$input_all[$i]['num']:''?>' maxlength=4 size=4/><!--
					--><select name='result[]'><?php
					$results = array(
						'0A0B' => 0x00,
						'0A1B' => 0x01,
						'0A2B' => 0x02,
						'0A3B' => 0x03,
						'0A4B' => 0x04,
						'1A0B' => 0x10,
						'1A1B' => 0x11,
						'1A2B' => 0x12,
						'1A3B' => 0x13,
						'2A0B' => 0x20,
						'2A1B' => 0x21,
						'2A2B' => 0x22,
						'3A0B' => 0x30,
						'4A0B' => 0x40,
					);
					foreach ($results as $k => $v){
						$sel = isset($input_all[$i]) && $input_all[$i]['result']==$v ? 'selected=\'selected\'' : '';
						echo "<option value='$v' $sel>$k</option>";
					}
					?></select>&nbsp;&nbsp;
					<?php if (0==($i+1)%4) { echo '</div><div>'; } ?>
			<?php } ?></div>
			<p><input type='submit' value='Submit'/></p>
		</form>
		<h2><hr/>Possible Answers</h2>
		<table><tr><?php
			foreach($selected_num as $i => $n){
				echo '<td>'.$n.'</td>';
				if (($i+1)%16 == 0) {
					echo '</tr><tr>';
				}
			}
		?></tr></table>
	</body>
</html>
