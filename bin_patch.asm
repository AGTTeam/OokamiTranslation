.nds

;Detect what game the patch is being applied to
.if readascii("data/repack/header.bin", 0xc, 0x6) == "YU5J2J"
  FIRST_GAME   equ 0x1
  SECOND_GAME  equ 0x0
  ARM_FILE     equ "data/repack/arm9.bin"
  SUB_PATH     equ "/data/opsub.dat"
  ;Position in RAM for the digit8 file used for injection
  INJECT_START equ 0x02121e60
  ;Position in RAM for the end of the file
  INJECT_END   equ 0x02121f70
  ;Free portion of RAM to load the opening sub graphics
  SUB_RAM      equ 0x020a9000
  SUB_OP_SIZE  equ 0x9A00
  ;Bottom screen BG VRAM + 1 tile of space (0x800)
  SUB_VRAM     equ 0x06204800
  ;Position for the Special Message subs
  SUB_VRAM2    equ 0x06214800
  ;Function to load a file in RAM
  RAM_FUNC     equ 0x0205464c
.else
  FIRST_GAME   equ 0x0
  SECOND_GAME  equ 0x1
  ARM_FILE     equ "data/repack/arm9_dec.bin"
  SUB_PATH     equ "data/opsub.dat"
  INJECT_START equ 0x021962a0
  INJECT_END   equ 0x021963b0
  SUB_RAM      equ 0x023a7140
  SUB_VRAM     equ 0x06214800
  RAM_FUNC     equ 0x02098828
.endif

;Plug the custom code at the end of the digit8 font
.open "data/repack/data/font/digit8.NFTR",INJECT_START
.org INJECT_END
  ;Copy the relevant info from the font file
  FONT_DATA:
  .import "data/font_data.bin",0,0x5f
  .align

  ;Add WVF support to script dialogs
  VWF:
  push {lr}
  .if FIRST_GAME
    ;Read the current character and set r0 to the VWF value
    ldrb r1,[r6,0xe5]
    ldr r2,=FONT_DATA
    sub r1,r1,0x20
    add r1,r1,r2
    ldrb r1,[r1]
    add r0,r0,r1
  .else
    ;TODO
  .endif
  pop {pc}
  .pool

  ;Center the choices text. This is originally calculated by
  ;multiplying the max line length by a constant
  CENTERING:
  push {lr}
  .if FIRST_GAME
    ;r1 = Result
    ;r9 = Pointer to the string
    push {r0,r2,r3,r9}
    ldr r0,=FONT_DATA
    mov r1,0x0
    mov r3,0x0
    ;Loop the choice characters
    @@loop:
    ;Read the character
    ldrb r2,[r9],0x1
    ;Finish when reaching 0
    cmp r2,0x0
    beq @@end
    ;Handle newlines
    cmp r2,0x0a
    cmpne r2,0x0d
    beq @@newline
    ;Handle shift-jis
    ;>=0xe0
    cmp r2,0xe0
    addge r3,r3,0xc
    addge r9,r9,0x1
    bge @@loop
    ;>0xa0
    cmp r2,0xa0
    addgt r3,r3,0x6
    bgt @@loop
    ;>=0x81
    cmp r2,0x81
    addge r3,r3,0xc
    addge r9,r9,0x1
    bge @@loop
    ;Add the character width
    sub r2,r2,0x20
    add r2,r0,r2
    ldrb r2,[r2]
    add r3,r3,r2
    b @@loop
    @@newline:
    cmp r3,r1
    movgt r1,r3
    mov r3,0x0
    b @@loop
    @@end:
    ;Get the max value
    cmp r3,r1
    movgt r1,r3
    ;Divide by 2
    lsr r1,r1,0x1
    pop {r0,r2,r3,r9}
  .else
    ;TODO
  .endif
  pop {pc}
  .pool

  ;File containing the the opening sub graphics
  SUB_FILE:
  .asciiz SUB_PATH
  ;Current frame for audio subtitles
  AUDIO_FRAME:
  .dh 0x0
  .align

  ;Load the subtitles file in ram
  SUBTITLE:
  push {lr,r0-r2}
  .if FIRST_GAME
    ;This functions loads the file r1 into r0+0xc, but only up
    ;to 0xa78 bytes, so we temporarily modify that max size
    SUB_SIZE equ 0x02054690
    ldr r0,=SUB_SIZE
    ldr r1,=0xfffff
    str r1,[r0]
  .endif
  ;Load the file
  ldr r0,=SUB_RAM
  sub r0,r0,0xc
  ldr r1,=SUB_FILE
  bl RAM_FUNC
  .if FIRST_GAME
    ;Restore the size pointer
    ldr r0,=SUB_SIZE
    ldr r1,=0xa78
    str r1,[r0]
    ;Check if we need to enable the BG
    ldr r0,=AUDIO_FRAME
    ldrh r0,[r0]
    cmp r0,0x0
    beq @@ret
  .endif
  ;Enable BG1 (2nd bit)
  ldr r0,=0x4001001
  ldrb r1,[r0]
  orr r1,r1,0x2
  strb r1,[r0]
  ;Set BG1 values (High priority, 8bit, tiles=5, map=2)
  add r0,r0,0x9
  mov r1,0x0294
  strh r1,[r0]
  ;Reset BG1 scrolling, needed if the video plays again
  ;after being idle in the main menu
  add r0,r0,0xc
  mov r1,0x0
  strh r1,[r0]
  ;Set the map
  ldr r0,=0x6201000
  mov r1,0x0
  @@mapLoop:
  strh r1,[r0],0x2
  add r1,0x1
  cmp r1,0x60
  bne @@mapLoop
  ;Set VRAM H to LCD
  ldr r0,=0x04000248
  mov r1,0x80
  strb r1,[r0]
  .if FIRST_GAME
    ldr r0,=0x0689a002
    ldr r1,=0x63df
    strh r1,[r0]
  .else
    ;Copy the palette
    ldr r0,=0x06898000
    ldr r1,=0x0689a000
    mov r2,0x80
    @@palLoop:
    ldr r4,[r0],0x4
    str r4,[r1],0x4
    sub r2,r2,0x1
    cmp r2,0x0
    bne @@palLoop
  .endif
  ;Set VRAM H back to ext palette
  ldr r0,=0x04000248
  mov r1,0x82
  strb r1,[r0]
  ;Go back to normal execution
  @@ret:
  pop {r0-r2}
  .if FIRST_GAME
    add r0,r6,0x1000
  .else
    mov r4,r0
  .endif
  pop {pc}
  .pool

  .if SECOND_GAME
    SUBTITLE_RAM:
    push {lr}
    ldr r2,=SUB_RAM
    ldr r2,[r2]
    cmp r2,0x0
    movne r2,0x8c0
    popne {pc}
    ldr r2,=0xfffff
    pop {pc}
    .pool
  .endif

  ;Draw or clear the subtitles at the current frame
  SUBTITLE_FRAME:
  push {lr,r0-r3}
  ;Check if we need to do something in the current frame (r1)
  ldr r0,=SUB_RAM
  .if FIRST_GAME
    ldr r2,=AUDIO_FRAME
    ldrh r2,[r2]
    cmp r2,0x0
    addne r0,r0,SUB_OP_SIZE
  .endif
  ldr r2,[r0]
  ldr r3,[r0,r2]
  cmp r1,r3
  bne @@end
  ;Push the rest of the registers and get current offset/clear
  push {r4-r11}
  add r2,r2,0x4
  ldr r3,[r0,r2]
  ;Increase the sub counter
  add r2,r2,0x4
  str r2,[r0]
  ;Setup registers
  .if FIRST_GAME
    ldr r1,=AUDIO_FRAME
    ldrh r1,[r1]
    cmp r1,0x0
    ldreq r1,=SUB_VRAM
    ldrne r1,=SUB_VRAM2
  .else
    ldr r1,=SUB_VRAM
  .endif
  add r0,r0,r3
  ;Check the compression series
  ;If r3 1, this is a repeating series with one single tile repeated r2 times
  ;Otherwise, there are r2 different tiles
  @@series:
  ldrh r3,[r0],0x2
  ldrh r2,[r0],0x2
  cmp r2,0x0
  beq @@seriesEnd
  ;Multiply by 2 since 8 words are copied at a time and a tile is 16 words
  lsl r3,r3,0x1
  lsl r2,r2,0x1
  ;Copy 8 words at a time
  @@loop:
  ldmia r0!,{r4-r11}
  stmia r1!,{r4-r11}
  sub r2,r2,0x1
  cmp r2,0x0
  beq @@series
  ;Go back to the loop if this isn't a repating series
  cmp r3,0x0
  beq @@loop
  ;Otherwise, check if it needs to go back one tile in RAM and write it again
  sub r3,r3,0x1
  cmp r3,0x0
  moveq r3,0x2
  subeq r0,r0,0x40
  b @@loop
  ;Pop the registers
  @@seriesEnd:
  pop {r4-r11}
  ;Go back to normal execution
  @@end:
  pop {r0-r3}
  .if FIRST_GAME
    ldr r0,[r10,0x8]
  .else
    add r1,r1,0x1
  .endif
  pop {pc}
  .pool

  ;Add subtitles for the special message
  .if FIRST_GAME
    SPECIAL_NAME:
    .asciiz "HOR_SYS_420.ahx"
    .align

    SPECIAL:
    push {lr,r0-r2,r4}
    ;Compare r3 with HOR_SYS_420.ahx
    ldr r0,=SPECIAL_NAME
    mov r1,0x0
    @@loop:
    ldrb r2,[r0,r1]
    ldrb r4,[r3,r1]
    cmp r2,r4
    bne @@end
    cmp r2,0x0
    beq @@found
    add r1,r1,0x1
    b @@loop
    ;Matched, load the subtitle file in ram
    @@found:
    ldr r0,=AUDIO_FRAME
    mov r1,0x1
    strh r1,[r0]
    bl SUBTITLE
    ;Restore the stack and jump to the original function call
    @@end:
    pop {lr,r0-r2,r4}
    b 0x2069774
    .pool

    SPECIAL_FRAME:
    push {lr,r0-r1}
    ;Check if the special message is playing
    ldr r0,=AUDIO_FRAME
    ldrh r1,[r0]
    cmp r1,0x0
    beq @@ret
    ;Increase the frame and call the frame function
    add r1,r1,0x1
    strh r1,[r0]
    bl SUBTITLE_FRAME
    @@ret:
    pop {lr,r0-r1}
    b 0x0205818c
    .pool

    SPECIAL_STOP:
    push {r0-r1}
    ;Check if the special message is playing
    ldr r0,=AUDIO_FRAME
    ldrh r1,[r0]
    cmp r1,0x0
    beq @@ret
    ;Set audio frame to 0
    mov r1,0x0
    strh r1,[r0]
    ;Disable BG1 (2nd bit)
    ldr r0,=0x4001001
    ldrb r1,[r0]
    and r1,r1,0xfd
    strb r1,[r0]
    @@ret:
    pop {r0-r1}
    b 0x020664d4
    .pool
  .endif
.close

;Inject custom code
.open ARM_FILE,0x02000000
  .if FIRST_GAME
    .org 0x0203a8ec
      ;add r0,r0,0x6
      bl VWF
    .org 0x02030304
      ;add r1,r6,r6,lsl 0x1
      bl CENTERING
    .org 0x020216d0
      ;add r0,r6,0x1000
      bl SUBTITLE
    .org 0x0206ba2c
      ;ldr r0,[r10,0x8]
      bl SUBTITLE_FRAME
    .org 0x02055b64
      ;bl 0x2069774
      bl SPECIAL
    .org 0x020582b0
      ;bl 0x0205818c
      bl SPECIAL_FRAME
    .org 0x02069698
      ;bl 0x020664d4
      bl SPECIAL_STOP

    ;Increase space for the market header
    .org 0x0204500c
      ;mov r3,0x19
      mov r3,0x20
    .org 0x020450dc
      ;mov r3,0x19
      mov r3,0x20

    ;Tweak rumor text position
    .org 0x0206cca4
      ;mov r2,r1 (0x8)
      mov r2,0x6
    .org 0x0206cd6c
      ;mov r2,0x1c
      mov r2,0x16
    .org 0x0206ce94
      ;mov r2,0x70
      mov r2,0x72
  .else
    ;TODO: VWF hack
    .org 0x0209d1c4
      ;mov r4,r0
      bl SUBTITLE
    .org 0x02098854
      ;mov r2,0x8c0
      bl SUBTITLE_RAM
    .org 0x0209f1e0
      ;add r1,r1,0x1
      bl SUBTITLE_FRAME
  .endif
.close
