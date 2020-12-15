#IfWinActive ahk_exe np21x64w.exe
*Esc::ControlSend,,{Blind}{Esc Down}
*Esc Up::ControlSend,,{Blind}{Esc Up}
*LWin::ControlSend,,{Blind}{LWin Down}
*LWin Up::ControlSend,,{Blind}{LWin Up}

; Muhenkan (PC98 NFER key) -> {vk1D}
*LAlt::ControlSend,,{Blind}{vk1D Down}
*LAlt Up::ControlSend,,{Blind}{vk1D Up}

; Henkan (PC98 XFER key) -> {vk1C}
*RAlt::ControlSend,,{Blind}{vk1C Down}
*RAlt Up::ControlSend,,{Blind}{vk1C Up}

RControl::LAlt

;Kana / かな -> {vkF2}
LWin & LAlt::ControlSend,,{Blind}{vkF2}
Ctrl & Space::ControlSend,,{Blind}^{Space}

;Ro key
LWin & /::ControlSend,,{Blind}{vke2 Down}
LWin & / up::ControlSend,,{Blind}{vke2 Up}

;IME ON/OF -> {vkF3}, {vkF4}

;Close emulator
LWin & Delete::WinClose
#if

#IfWinActive ahk_exe dosbox-x.exe
LWin::F13
LAlt::F14
LControl::F15
#If
