RunWait %1% %2% %3% %4% %5% %6% %7% %8% %9%
ExitApp

LAlt::Send {vk1D}
RAlt::Send {vk1C}
LCtrl & RAlt::Send ^{vk1C}
RCtrl::LAlt
LWin & LAlt::Send {vkF2}
Ctrl & Space::ControlSend WinExist("A"),^{Space}

; Muhenkan (PC98 NFER key)
; Henkan (PC98 XFER key)
;Muhenkan / 無変換 -> {vk1D}
;Henkan / 変換　-> {vk1C}
;Kana / かな -> {vkF2}
;IME ON/OF -> {vkF3}, {vkF4}

