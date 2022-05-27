ENTRY(main)

MEMORY {
  FLASH(rwx): ORIGIN = 0x00000000, LENGTH = 128K
}

SECTIONS {
  .text : {
    *(.text)
  }> FLASH
}
