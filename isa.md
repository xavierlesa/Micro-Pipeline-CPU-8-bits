# ISA - Basado en RISC-V, 16 bits / 2 words.

## Formatos R, I, J de instrucción de 16 bits.

## Instrucciones R

Bits        4       3       3       3       3   
Posición    15..12  11..9   8..6    5..3    2..0

Tipo-R      opcode  rd      rs      rt      fn   

add         0000    rd      rs      rt      000     rd = rs + rt
adc         0000    rd      rs      rt      001     rd = rs + rt + carry
sub         0000    rd      rs      rt      010     rd = rs - rt
sbb         0000    rd      rs      rt      011     rd = rs - rt - borrow

and         0000    rd      rs      rt      100     rd = rs & rt
or          0000    rd      rs      rt      101     rd = rs | rt
xor         0000    rd      rs      rt      110     rd = rs ^ rt
sll         0000    rd      rs      00      111     rd = rs << 1

la          0001    rd      rs      rt      000     rd = Mem[rs:rt] // Load Absolute
sa          0001    rd      rs      rt      001     Mem[rs:rt] = rd // Store Absolute



## Instrucciones I

Bits        4       3       3       6   
Posición    15..12  11..9   8..6    5..0
Tipo-I      opcode  rd      rs      imm

addi        0010    rd      rs      int6    rd = rs + int6
subi        0011    rd      rs      int6    rd = rs - int6
lb          0100    rd      rs      int6    rd = Mem[rs + int6]
sb          0101    rd      rs      int6    Mem[rs + int6] = rd // sb $t1, 64($t2)
li          0110    rd      int3    int6    rd = int9 (solo los primeros 8 bits)

beqz        1000    int3    rs      int6    if(rs == 0) PC = PC +/- int9[8:0]
bnez        1001    int3    rs      int6    if(rs != 0) PC = PC +/- int9[8:0]

**int6*: Un valor inmediato de 6 bits con signo, desde 32, a -32
**int9*: Un valor inmediato de 9 bits, solo pueden ser asignados los primero 8 bits
a los registros, el MSB de descarta.


## Instrucciones J

Bits        4       12
Posición    15..12  11..0
Tipo-J      opcode  imm

j           1100    int12   PC = (PC << 4) + int12
jal         1101    int12   PC = (PC << 4) + int12 // y guarda en $t7:$t6 = PC
ret         1110    --      PC = $t7:$t6


- Opcode de 4 bits (hasta 16 instrucciones).
- Registros de proposito general $t1 a $t3 y zero $z o $t0 o $0.
- Registros de return address $t6 y $t7 son usados juntos como $ra
- Registros de argumentos $t4 y $t5 son usados para argumentos en subrutinas
- Ramas y saltos relativos y absolutos



## Registros

Dirección   Registro  Descripción

000         $z        Registro de solo lectura, valor 0x0, solo para tipo R e I.
001         $1        Registro de proposito general 1
010         $2        Registro de proposito general 2
011         $3        Registro de proposito general 3
100         $4        Registro v1 para argumento 1 de subrutinas
101         $5        Registro v2 para argumento 2 de subrutinas
110         $6        Registro RA parte baja
111         $7        Registro RA parte alta



### Cálculo de Direcciones

Las direcciones para saltos y asignación se calculan de forma relativa al PC y el
desaplazamiento al bit más significativo. Pueden ser de 6, 8 o 9 bits según la
instrucción.
