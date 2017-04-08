#!/usr/bin/php
<?php
function int2bcd($n) {
	return array(
		$n % 10,
		((int)($n / 10) % 10),
		((int)($n / 100) % 10),
		((int)($n / 1000) % 10),
	);
}
function check($na){
	$d = $na[0];
	if ($d == $na[1]) {
		return 0;
	} else if ($d == $na[2]) {
		return 0;
	} else if ($d == $na[3]) {
		return 0;
	}

	$d = $na[1];
	if ($d == $na[2]) {
		return 0;
	} else if ($d == $na[3]) {
		return 0;
	}

	if ($na[2] == $na[3]) {
		return 0;
	}
	return 1;
}
?>#ifndef __guessnum_h__
#define __guessnum_h__

#include <stdint.h>

#define CANDIDATES_COUNT 5040
uint64_t candidates[CANDIDATES_COUNT] = {
<?php
for ($n = 123; $n <= 9876; $n++) {
	$na = int2bcd($n);
	if (check($na)) {
		echo sprintf("0x%04d%04d%04d%04d,\n", $na[0], $na[1], $na[2], $na[3]);
		//echo sprintf("0x%02d%02d%02d%02d,\n", $na[0], $na[1], $na[2], $na[3]);
	}
}
?>
};

#endif

