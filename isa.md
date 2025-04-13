# Instruction Set Architecture (ISA)

## Formatos R, I, J de instrucción de 16 bits.

## Instrucciones Modo-0 (R)

| Bits       | 4      | 3      | 3      | 3      | 3    |                                   |
|------------|--------|--------|--------|--------|------|-----------------------------------|
| *Posición*| *15..12*| *11..9*| *8..6* | *5..3* | *2..0*|                                   |
| **Tipo-R** | **opcode** | **rd**     | **rs1** | **rs2**    | **fn**   |                    |
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
| **Tipo-I** | **opcode** | **rd** | **rs1** | **imm6** |                            |
| addi       | 0001   | rd     | rs1    | imm6   | rd = rs + imm6                    |
| lb         | 0010   | rd     | rs1    | imm6   | rd = Mem\[rs << 6 + imm6\]          |

## Instrucciones Modo-2 (S, B)

| Bits       | 4      | 3      | 3      | 3      | 3    |                                   |
|------------|--------|--------|--------|--------|------|-----------------------------------|
| *Posición*| *15..12*| *11..9*| *8..6* | *5..3* | *2..0*|                                  |
| **Tipo-R** | **opcode** | **imm3**    | **rs1**| **rs2**    | **imm3**   |                |
| sb         | 0011   | imm3   | rs1    | rs2   |  imm3 | Mem\[rs1 << 6 + imm6\] = rs2 |
| beq        | 0100   | imm3   | rs1     | rs2   | imm3 |  if(rs1 == rs2) PC = PC +/- imm5 |

***+/- imm5**: Un valor inmediato de 6 bits con signo, desde 32, a -32 bytes relativos al PC.*


## Instrucciones J

Bits        4       12
Posición    15..12  11..0
Tipo-J      opcode  imm

j           1001    int12   PC = (PC << 4) + int12
jal         1010    int12   PC = (PC << 4) + int12 // y guarda en $t7:$t6 = PC
ret         1011    --      PC = $t7:$t6


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
