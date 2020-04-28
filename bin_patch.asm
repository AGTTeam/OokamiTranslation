.nds

;Detect what game the patch is being applied to
.if readascii("data/repack/header.bin", 0xc, 0x6) == "YU5J2J"
  FIRST_GAME   equ 0x1
  ARM_FILE     equ "data/repack/arm9.bin"
  ;Position in RAM for the digit8 file used for injection
  INJECT_START equ 0x02121e60
  ;Position in RAM for the end of the file
  INJECT_END   equ 0x02121f70
  ;Free portion of RAM to load the opening sub graphics
  SUB_RAM      equ 0x020a9000
  ;Bottom screen BG VRAM + 1 tile of space (0x800)
  SUB_VRAM     equ 0x06204800
.else
  FIRST_GAME   equ 0x0
  ARM_FILE     equ "data/repack/arm9_dec.bin"
  INJECT_START equ 0x021962a0
  INJECT_END   equ 0x021963b0
.endif

;Plug the custom code at the end of the digit8 font
.open "data/repack/data/font/digit8.NFTR",INJECT_START
.org INJECT_END
  ;Copy the relevant info from the font file
  FONT_DATA:
  .import "data/font_data.bin",0,0x5E
  .align

  .if FIRST_GAME
    ;Add WVF support to script dialogs
    VWF_HACK:
    ldrsb r1,[r6,0xe5] ;Read the current character
    sub r1,r1,0x20     ;Subtract the first character code
    ldr r2,=FONT_DATA  ;r2 = font HDWC offset
    add r1,r1,r2       ;Add it to r1
    ldrb r1,[r1]       ;Set r1 to the next offset
    add r0,r0,r1       ;Add it to r0
    b VWF_HACK_RETURN
    .pool

    ;File containing the the opening sub graphics
    SUB_FILE:
    .ascii "/data/opsub.dat"
    .align

    ;Load the subtitles file in ram
    SUBTITLE_HACK:
    ;This functions loads the file r1 into r0+0xc, but only up
    ;to 0xa78 bytes, so we temporarily modify that max size
    SUB_SIZE equ 0x02054690
    ldr r0,=SUB_SIZE
    ldr r1,=0xfffff
    str r1,[r0]
    ;Load the file
    ldr r0,=SUB_RAM
    sub r0,r0,0xc
    ldr r1,=SUB_FILE
    bl 0x0205464c
    ;Restore the size pointer
    ldr r0,=SUB_SIZE
    ldr r1,=0xa78
    str r1,[r0]
    ;Go back to normal execution
    add r0,r6,0x1000
    b SUBTITLE_HACK_RETURN
    .pool

    ;Draw or clear the subtitles at the current frame
    SUBTITLE_FRAME:
    push {r1-r3}
    ;Check if we need to do something in the current frame (r1)
    ldr r0,=SUB_RAM
    ldr r2,[r0]
    ldr r3,[r0,r2]
    cmp r1,r3
    bne SUBTITLE_END
    ;Push the rest of the registers and get current offset/clear
    push {r4-r10}
    add r2,r2,0x4
    ldr r3,[r0,r2]
    ;Increase the sub counter
    add r2,r2,0x4
    str r2,[r0]
    ;Setup registers
    ldr r1,=SUB_VRAM
    mov r2,0x80
    ;Check if a clear is needed
    ;Otherwise, add the offset and start copying
    cmp r3,0x0
    addne r0,r0,r3
    bne SUBTITLE_LOOP
    ;Set all registers to the background color
    SUBTITLE_CLEAR:
    ldr r3,=0xc3c3c3c3
    mov r4,r3 :: mov r5,r3 :: mov r6,r3 :: mov r7,r3 :: mov r8,r3 :: mov r9,r3 :: mov r10,r3
    ;Write it 8 words at time
    SUBTITLE_CLEAR_LOOP:
    stmia r1!,{r3-r10}
    sub r2,r2,0x1
    cmp r2,0x0
    bne SUBTITLE_CLEAR_LOOP
    pop {r4-r10}
    b SUBTITLE_END
    ;Copy 8 words at a time
    SUBTITLE_LOOP:
    ldmia r0!,{r3-r10}
    stmia r1!,{r3-r10}
    sub r2,r2,0x1
    cmp r2,0x0
    bne SUBTITLE_LOOP
    pop {r4-r10}
    ;Go back to normal execution
    SUBTITLE_END:
    pop {r1-r3}
    ldr r0,[r10,0x8]
    b SUBTITLE_FRAME_RETURN
    .pool
  .endif
.close

;Inject custom code
.open ARM_FILE,0x02000000
  .if FIRST_GAME
    .org 0x0203a8ec
      ;Original: add r0,r0,0x6
      b VWF_HACK
      VWF_HACK_RETURN:
    .org 0x020216d0
      ;Original: add r0,r6,0x1000
      b SUBTITLE_HACK
      SUBTITLE_HACK_RETURN:
    .org 0x0206ba2c
      ;Original: ldr r0,[r10,0x8]
      b SUBTITLE_FRAME
      SUBTITLE_FRAME_RETURN:
  .endif
.close
