# Instruction Set Architecture (ISA)

## Formatos R, I, J de instrucción de 16 bits.

## Instrucciones Modo-0 (R)

| Bits       | 4      | 3      | 3      | 3      | 3    |                                   |
|------------|--------|--------|--------|--------|------|-----------------------------------|
| *Posición*| *15..12*| *11..9*| *8..6* | *5..3* | *2..0*|                                   |
| **mnemonic** | **opcode** | **rd**     | **rs1** | **rs2**    | **fn**   |                    |
| add        | 0000   | rd     | rs1    | rs2    | 000  |   rd = rs1 + rs2                   |
| adc        | 0000   | rd     | rs1    | rs2    | 001  |   rd = rs1 + rs2 + carry            | 
| sub        | 0000   | rd     | rs1    | rs2    | 010  |   rd = rs1 - rs2                   |
| sbb        | 0000   | rd     | rs1    | rs2    | 011  |   rd = rs1 - rs2 - borrow           |
| and        | 0000   | rd     | rs1    | rs2    | 100  |   rd = rs1 AND rs2                    |                    
| or         | 0000   | rd     | rs1    | rs2    | 101  |   rd = rs1 OR rs2                    |
| xor        | 0000   | rd     | rs1    | rs2    | 110  |   rd = rs1 XOR rs2                    |
| sll        | 0000   | rd     | rs1    | 00     | 111  |   rd = rs1 << 1                    |


## Instrucciones Modo-1 (I, L)

| Bits       | 4      | 3      | 3      | 6      |                                   |
|------------|--------|--------|--------|--------|-----------------------------------|
| *Posición* |*15..12*| *11..9*| *8..6* | *5..0* |                                   |
| **mnemonic** | **opcode** | **rd** | **rs1** | **imm6** |                            |
| addi       | 0001   | rd     | rs1    | imm6   | rd = rs + imm6                    |
| lb         | 0010   | rd     | rs1    | imm6   | rd = Mem\[rs << 6 + imm6\]          |

## Instrucciones Modo-2 (S, B)

| Bits       | 4      | 3      | 3      | 3      | 3    |                                   |
|------------|--------|--------|--------|--------|------|-----------------------------------|
| *Posición*| *15..12*| *11..9*| *8..6* | *5..3* | *2..0*|                                  |
| **mnemonic** | **opcode** | **imm3** | **rs1** | **rs2** | **imm3** |                          |
| sb         | 0011   | imm3   | rs1    | rs2   |  imm3 | Mem\[rs1 << 6 + imm6\] = rs2 |
| beq        | 0100   | imm3   | rs1     | rs2   | imm3 |  if(rs1 == rs2) PC = PC +/- imm5 |

***+/- imm5**: Un valor inmediato de 5 bits con signo, desde 32, a -32 bytes relativos al PC.*


## Instrucciones Modo-3 (L,I)

| Bits       | 4      | 3      | 1      | 8      |                                   |
|------------|--------|--------|--------|--------|-----------------------------------|
| *Posición* |*15..12*| *11..9*| *8*    | *7..0* |                                   |
| **mnemonic** | **opcode** | **rd** | **??** | **imm8** |                            |
| li          | 0101  | rd     | ??     | imm8   | rd = imm8                         |


## Instrucciones Modo-4 (J,I)

| Bits       | 4      | 12      |                                                    |
|------------|--------|---------|----------------------------------------------------|
| *Posición* |*15..12*| *11..0* |                                                    |
| **mnemonic** | **opcode**  | **imm12** |                                            |
| ja         | 0110  | imm12 | PC = PC & 0xf000 + imm12                           |
| jal        | 0111  | imm12 | r7 = PC(low), r6 = PC(high); PC = PC & 0xf000 + imm12 | 

- Opcode de 4 bits (hasta 16 instrucciones).
- Registro `r0` constante 0 (zero).
- Registros de proposito general `r1` a `r3`.
- Registros de argumentos `r4` y `r5` son usados para argumentos en subrutinas
- Registros de return address `r6` y `r7` son usados juntos como `ra`


## Registros

Dirección   Registro  Descripción

000         r0        Registro de solo lectura, valor 0x0.
001         r1        Registro de proposito general 1
010         r2        Registro de proposito general 2
011         r3        Registro de proposito general 3
100         r4        Registro v1 para argumento 1 de subrutinas
101         r5        Registro v2 para argumento 2 de subrutinas
110         r6        Registro RA parte baja
111         r7        Registro RA parte alta
