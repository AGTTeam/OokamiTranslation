.nds

.open "data/repack/arm9.bin",0x02000000
;Hook the dialog text writing function
.org 0x0203a8ec
  ;Original: add r0,r0,0x6
  b DIALOG_VWF_HACK
  DIALOG_VWF_HACK_RETURN:
.close

;Plug the custom code at the end of the digit8 font
.open "data/repack/data/font/digit8.NFTR",0x02121e60
.org 0x02121f70
  ;Copy the relevant info from the font file
  FONT_DATA:
  .import "data/font_data.bin",0,0x5E
  .align

  ;Add WVF support to script dialogs
  DIALOG_VWF_HACK:
  ldrsb r1,[r6,0xe5] ;Read the current character
  sub r1,r1,0x20     ;Subtract the first character code
  ldr r2,=FONT_DATA  ;r2 = font HDWC offset
  add r1,r1,r2       ;Add it to r1
  ldrb r1,[r1]       ;Set r1 to the next offset
  add r0,r0,r1       ;Add it to r0
  b DIALOG_VWF_HACK_RETURN
  .pool
.close
