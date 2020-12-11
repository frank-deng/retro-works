RunWait %1% %2% %3% %4% %5% %6% %7% %8% %9%
ExitApp

; Muhenkan (PC98 NFER key) -> {vk1D}
*LAlt::Send {Blind}{vk1D DownTemp}
*LAlt Up::Send {Blind}{vk1D Up}

; Henkan (PC98 XFER key) -> {vk1C}
*RAlt::Send {Blind}{vk1C DownTemp}
*RAlt Up::Send {Blind}{vk1C Up}
*RCtrl::Send {Blind}{LAlt DownTemp}
*RCtrl Up::Send {Blind}{LAlt Up}

;Kana / かな -> {vkF2}
LWin & LAlt::Send {vkF2}
Ctrl & Space::ControlSend WinExist("A"),^{Space}

LWin & /::Send {vke2}

;IME ON/OF -> {vkF3}, {vkF4}
