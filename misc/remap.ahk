#UseHook

#HotIf WinActive("ahk_exe dosbox-x.exe")
Esc::F13
Tab::F14
LCtrl::F15
LAlt::F16
LWin::AppsKey
RWin::AppsKey
AppsKey::F17
#HotIf

#HotIf WinActive("ahk_exe fgfs.exe")
Left::Insert
Right::Enter
Up::PgUp
Down::PgDn
#HotIf

#HotIf WinActive("ahk_exe np21x64w.exe")
; Muhenkan (PC98 NFER key) -> {vk1D}
LAlt::vk1D
; Henkan (PC98 XFER key) -> {vk1C}
RAlt::vk1C
RControl::LAlt
;Kana / ¤«¤Ê -> {vkF2}
LWin & LAlt::vkF2
;Ro key
LWin & /::vkE2
;IME ON/OF -> {vkF3}, {vkF4}

;Disable IME keys
LWin::Return
RWin::Return
AppsKey::Return
LWin & Space::Return
RWin & Space::Return
Ctrl & Space::Return

#HotIf
