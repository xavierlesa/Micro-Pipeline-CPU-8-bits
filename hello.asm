; define el bloque de memoria desde la posición 0x8000 (RAM)
.org: 0x8000

; reserva un espacio en memoria para el texto
.section text:
        hola db "Hola desde mi RISC-V CPU!", 0
        len_hola equ len(hola)
.endsection

# Inicio de la ejecución
start:
	add r1, r0, r0
	add r0, r0, r0
	add r2, r3, r0
	add r1, r4, r5
	add r1, r7, r9
	add r1, r0, r0
	add r1, r0, r0
        ld $1, len_hola
loop:   
	ld $2, hola      ; me gustaria poder hacer ldr $2, hola[$t]
        st $2
        addi $t, $t, -1
        bnez $t, .loop
