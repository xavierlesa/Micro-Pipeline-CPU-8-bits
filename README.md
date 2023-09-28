# Micro Pipeline CPU de 8 bit hecho a mano (DRAFT)


Este proyecto está fuertemente inspirado en las series de videos de

@BenEater [Building an 8-bit breadboard computer!](https://www.youtube.com/playlist?list=PLowKtXNTBypGqImE405J2565dvjafglHU)

@weirdboyjim [Making an 8 Bit pipelined CPU](https://www.youtube.com/playlist?list=PLFhc0MFC8MiCDOh3cGFji3qQfXziB9yOw)

@slu467 [Breadboard 8-Bit CPU with Minimalistic Design](https://www.youtube.com/playlist?list=PLYlQj5cfIcBVRMsr9yxHmvCzMqonI6O6N)

todos fueron muy inspiradores y una excelente guía para introducirse en esto de armar un CPU a mano.


## Pipeline

Un CPU basado en Pipeline tiene la particularidad de ser un poco más rápido pero
también tiene una serie desafios interesantes, como el "hazard" o el riesgo de que dos
instrucciones quieran acceder al mismo tiempo a un recurso.

En una arquitectura pipeline, las instrucciones son ejecutadas concurrentemente, a
diferencia de una arquitectura tradicional donde las instrucciones son ejecutadas una a
una, utilizando (o bloqueando) todos los recursos hasta que la instrucción finalice su
ejecución.

El ejemplo más visual es el de una panadería con una amazadora, un fermentador y un horno.

En el modelo "tradicional" el proceso sería:

| Estado | Instrucción |
|--------|-------------|
| 1      | Preparar ingredientes |
| 2      | Amasado |
| 3      | Reposo y fermentado |
| 4      | Horneado |

Cada iteración empiza nuevamente en el estado 1 y cada instrucción bloquea el estado, es
decir no se puede volver al Amasado si no se pasa por Reposo, Horneado, etc.

En camio en el modelo de pipeline, las instrucciones son ejecutadas una trás otra sin
esperar (hay restricciones - hazard) a que la anterior termine su ejecución.


| Estado / Instrucción | 1 | 2 | 3 | 4 |
|----------------------|---|---|---|---|
| | Preparar ingredientes | Amasado | Reposo y fermentado | Horneado |
| | | Preparar ingredientes | Amasado | Reposo y fermentado |
| | | | Preparar ingredientes | Amasado |
| | | | | Preparar ingredientes |


Las instrucciones son ejecutadas una trás otra y de forma concurrente, esto es una
ventaja en velocidad y performance, pero la complejidad de las instrucciones está dada
por la candidad de estados que puede manejar el pipeline.


Para el CPU que estoy armando no planeo ejecutar más de 2 o 3 estados en el pipeline,
siendo estos Fetch, Decode, Exec.

| 1 | 2 | 3 |
|---|---|---|
| Fetch | Decode | Exec |
| | Fetch | Decode |
| | | Fetch |



## Arquitectura 

La idea de este proyecto no es hacer un super CPU, sino solo un CPU que pueda ejecutar
una serie de instrucciones reducidas, nada muy complejo. Por lo que en un principio va a
contar con los siguientes recursos:

- Reloj
- Contador de programa de 16 bits (al menos al inicio sin segmentación)
- Memoria 32k x 8 bits
- Pipeline de tres estados (Fetch, Decode, Exec) / tres latches tipo d de 8 bit cada uno con
  líneas de control /OE y CP
- Registros A y B
- ALU
- Un Bus de datos
- Logica de control
- Puerto I/O (UART o similar)



## Mapa de Memoria y Bancos de Memoria

Pensado en como usar de la forma más eficinte los componentes del CPU, el espació y el
consumo, creo que es interesante pensar en como se va a acceder y como se van aguardar
los programas.

La manera clásica, es por ejemplo, usando un Registro PC (Program Counter) de 16 bits y
acceder a los 64kb de memoria posible de una forma lineal.

Ejemplo:

```
0x8000: 0xF0 0x56       ; LD A, 0x65
0x8002: 0xF1 0x01       ; LD B, 0x01
0x8004: 0xC0            ; SUB A, B, A
0x8005: 0xFA 0x1080     ; BEQ A, 0x8010 <-- saltar si A es 0 a la posición 0x8010 (16 bits)
0x8008: 0x00 0x0280     ; JMP 0x0480 <-- salto incondicional a 0x8004
0x800B: ...
....
0x8010: 0xFF            ; ...
```

Otra forma y la cual me parece interesate explorar, es la de usar bancos de memoria y
asignar una dimensión fija para cada banco. Por ejemplo de 256 bytes los cuales se 
pueden direccionar con solo 8 bits = 0x00..0xFF.

De esta manera cada bloque de programa tiene un número fijo de 256 bytes. Esto puede
parecer una desventaja al inicio, pero ciertamente tiene sus ventajas, como ser que
solo necesitamos contar (PC Reg) en 8 bits y con solo dos 74HC283 lo podemos hacer 
y luego usamos un Registro dedicado al banco con un 7HC574.

La ventajas son:

- Reducción de espacio en memoria:

    Al solo usar direcciones de 8 bits (1 byte) las instrucciones con saltos solo
    ocupan 1 byte extra en vez de 2 bytes para las direcciones de 16 bits.

- Reducción de uso de componentes:

    Solo es necesario un solo contador de 8 bits y un registro de banco.
    En comparación con dos contadores de 8 bits y 2 registros.
    

Ejemplos:

Dos tipos de asignaciones, + PC o asignación absoluta.

```
;; asignación relativa al PC, cambio del banco pero mantiene el PC.
0x00:   0xBF 0x80       ; asignar el banco 0x80 + relativo del PC
0x02:   0xF0 0x56       ; LD A, 0x65 <-- instrucción 0x02 del banco 0x80
0x04:   0xF1 0x01       ; LD B, 0x01
0x06:   0xC0            ; SUB A, B, A
0x07:   0xFA 0x10       ; BEQ A, 0x10 <-- saltar si A es 0 a la posición 0x10
0x09:   0x00            ; JMP 0x06 <-- salto incondicional a 0x06
0x0A:   ...
....
0x10:   0xFF            ; ...
```

asignación absoluta del banco, salta a la posición 0x00 del banco
```
;; asignación del banco y reset del PC.
0x00:   0xBE 0x80       ; asignar el banco 0x80 y PC a 0x00
;; PC Reset
0x00:   0xF0 0x56       ; LD A, 0x65 <-- instrucción 0x00 del banco 0x80
0x02:   0xF1 0x01       ; LD B, 0x01
0x04:   0xC0            ; SUB A, B, A
0x05:   0xFA 0x10       ; BEQ A, 0x10 <-- saltar si A es 0 a la posición 0x10
0x07:   0x00            ; JMP 0x02 <-- salto incondicional a 0x02
....
0x10:   0xFF            ; ...
```


Algunas desventajas:

- Programas más complejos:

    Los saltos a direcciones absolutas entre bancos, son mas complejas/lentas ya que
    primero hay que setear el banco y luego hacer el salto a la dirección relativa.

- Fragmentación de programas:

    A la hora de programar hay que pensar cuidadozamente que la rutina no supere las 256
    instrucciones a las que estamos limitados por banco. Si esto sucede hay que agrgar
    algunas instrucciones extras para los saltos entre bancos y no perder datos entre
    estos.


```
+------------------------------------------------------+-----------------------+
|                      Logic Controls                  |         Stage         |
+-------+-------+------+------+------+------+-----+----+-----------------------+
| D7    | D6    | D5   | D4   | D3   | D2   | D1  | D0 |                       |
+-------+-------+------+------+------+------+-----+----+-----------------------+
| PC_I0 | PC_I1 | RA_I | RA_O | RB_I | RB_O | M_O | IR |                       |
+-------+-------+------+------+------+------+-----+----+-----------------------+
| 0     | 0     | 0    | 0    | 0    | 0    | 1   | 1  |  Fetch (MEM[PC] > IR) |
+-------+-------+------+------+------+------+-----+----+-----------------------+
| 0     | 0     | 0    | 0    | D    | C    | B   | A  |  Exec (IR > LC)       |   
+-------+-------+------+------+------+------+-----+----+-----------------------+



+-----------------------------------+
|         µCode true-table          |
+---+---+---+---+-------------------+
| D | C | B | A | OP                |
+---+---+---+---+-------------------+
| 0 | 0 | 0 | 0 | NOP               |
+---+---+---+---+-------------------+
| 0 | 0 | 0 | 1 | MEM[PC] > RA      |
+---+---+---+---+-------------------+
| 0 | 0 | 1 | 0 | MEM[PC] > RB      |
+---+---+---+---+-------------------+
| 0 | 0 | 1 | 1 | OutA / A & B > A  |
+---+---+---+---+-------------------+
| 0 | 1 | 0 | 0 | A > B             |
+---+---+---+---+-------------------+
| 0 | 1 | 0 | 1 | B > A             |
+---+---+---+---+-------------------+
| 0 | 1 | 1 | 0 | OutB / A & B > B  |
+---+---+---+---+-------------------+
| 0 | 1 | 1 | 1 | JMP               |
+---+---+---+---+-------------------+
| 1 | 0 | 0 | 0 |                   |
+---+---+---+---+-------------------+
| 1 | 0 | 0 | 1 |                   |
+---+---+---+---+-------------------+

```


## Secuencia de arranque

La secuencia de arranque o bootstrap carga la primer instrucción y sincroniza las demás
instrucciones en órden. Este paso es importante ya que determina como serán ejecutadas
las demás instrucciones en secuencia, por lo tanto espera una instrucción (INST WORD) y
no un operando (DATA WORD).


```
MEM[PC] > INST REG > LC (Logic Control)

PC: 0000
MEM: 0000

```


## Set de instrucciones

Las instrucciones para este CPU van a estar categorizadas en 4 grupos:

- Lectura/Escritura en Registros/Memoria

    Estas son las instrucciones encargadas de escribir y leer en memoria y en 
    los registros, así como mover datos entre estos.
    `LD`, `LDA`, `LDR`, `ST`.

- Aritméticas y Lógicas

    Instrucciones para operaciónes matemáticas como suma, resta, 
    multiplicación, división, inc/dec, etc.
    `ADD`, `ADDI`, `SUB`, `SUBI`, `AND`, `OR`, `XOR`.
    

- Saltos y llamadas a subrutinas

    Solo vamos a contar con saltos condiciones e incondicionales así como 
    llamadas a subrutinas.
    `JMP`, `BEQ`, `BNEQ`


- Otras / Miscelanias

    Otras instrucciones como HALT y NOP.
    `NOP`.


**Referencias**

`0bxxxx`: Indica un valor binario de 4 bits 1/2 word.

`0byyyyxxxx`: Indica un valor binario de 8 bits 1 word.

`0xnn`: Indica un valor hexadecimal de 1 word.

`0xnnnn`: Indica un valor hexadecimal de 2 word (16 bits) para asignar direcciones por
        ejemplo.


También es valido usar 1F00h o 1F00H para describir un valor hexadecimal.
Ej `1fh`, `1FH`, `1fH`, `0x1f`, `0x1F` son todas representaciones validas para el mismo valor.

**ACC**: Refiere al Acumulador, y siempre apunta al registro A

**A o RA**: Registro A

**B o RB**: Registro B

**[m]**: Indica el valor en una posición de memoria.

**addr**: Indica una posición de memoria.


Las direcciones se cargan desde el LSB al MSB y se lee desde MSB al LSB, esto implica
que la carga en memoria se debe hacer desde LSB a MSB, ejemplo:


```asm
MOV A,[1F00H]

0100H: E4H 
0101H: 00H  <-- LSB
0102H: 1FH  <-- MSB
```

## Registros

Por ahora solo hay dos registros el **A** y **B**, identificados por las direcciones `0x01` y `0x10`
respectivamente.

| R  | addr | Descripción |
|----|------|-------------|
| A  | 01H  | Registro de proposito general y acumulador, en este es hacen la mayoria de |
|    |      | las operaciones matemáticas y lógicas.                                     |
| B  | 10H  | Registro de proposito general, intercambio de datos con y registro         |
|    |      | temporal.                                                                  |

Para acceder a las operaciones de registro solo es necesario identificar y asignar el
registro y sumarlo a  la instrucción. Ejemplo:

```asm
MOV A, 57H  ; El valor HEX de MOV es 0b1111xx00 donde xx es la dirección del registro
            ; en el caso del Reg A 01H -> 0b0100
            ;   0b11110000 --> F0H
            ; + 0b00000100 --> 04H
            ; ------------
            ;   0b11110100 --> F4H

0100H: F4 57
```


## Lectura/Escritura en Registros/Memoria

### Inmediato

|Operador   | Operando | Hexa        |  Descripción                                       |
|-----------|----------|-------------|----------------------------------------------------|
|MOVi r,x   | 57H      | Fx 57       |  Rr <- 57H, Carga en Rr el inmediato 57H.          |


### Absoluto

|Operador   | Operando | Hexa        |  Descripción                                       |
|-----------|----------|-------------|----------------------------------------------------|
|MOVa r,[m] | 1F00H    | E4 00 1F    |  Rr <- [1F00H], Carga en Rr lo que existe en la    |
|           |          |             |  dirección de memoria 1F00H. La dirección se carga |
|           |          |             |  desde el LSB al MSB y se lee desde MSB al LSB.    |

### Relativo

|Operador   | Operando | Hexa        |  Descripción                                       |
|-----------|----------|-------------|----------------------------------------------------|
|MOVr r,#m  | 1F00H    | D4 00 1F    |  Rr <- #1F00H, Carga en Rr lo que existe en la     |
|           |          |             |  dirección de memoria relativa al inmediato 1F00H. |
|           |          |             |  En ambos la dirección se carga desde el LSB al    |
|           |          |             |  MSB y se lee desde MSB al LSB.                    |

```
0100H: MOVr A, F0 01
...                 \
01F0H: F0 0F  <------+
....         \
0FF0H: 5A <---+
```

### Swap

|Operador   | Operando | Hexa        |  Descripción                                        |
|-----------|----------|-------------|-----------------------------------------------------|
|MOV A,x    | 57H      | F4 57       |  RA <- 57H, Carga en el ACC el inmediato 57H.       |
|MOV A,[m]  | 1F00H    | E4 00 1F    |  RA <- [1F00H], Carga en el ACC lo que existe en la |
|           |          |             |  dirección de memoria 1F00H. La dirección se carga  |
|           |          |             |  desde el LSB al MSB y se lee desde MSB al LSB.     |
|MOV A,#m   | 1F00H    | E4 00 1F    |  RA <- #1F00H, Carga en el ACC lo que existe en la  |
|           |          |             |  dirección de memoria relativa al inmediato 1F00H.  |
|MOV [m],A  | 1F00H    | D4 00 1F    |  [1F00H] <- RA, Carga en la dirección de memoria    |
|           |          |             |  1F00H lo que hay en el ACC.                        |
|MOV B,x    | 57H      | F8 57       |  RB <- 57H, Carga en RB el inmediato 57H.           |
|MOV B,[m]  | 1F00H    | E8 00 1F    |  RA <- [1F00H], Carga en RB lo que existe en la     |
|           |          |             |  dirección de memoria 1F00H.                        |
|MOV [m],B  | 1F00H    | D8 00 1F    |  [1F00H] <- RA, Carga en la dirección de memoria    |
|           |          |             |  1F00H lo que hay en RB.                            |


```asm
;; fibonacci
org 0100H

start:
  MOV A,1         ; Inicializa ACC con 1
  CLR B           ; Borra B con 0
loop:
  OUT A           ; Muestra en ROUT el valor de ACC
  MOV [0F00H],A   ; Guarda en [m] el valor del ACC
  ADD A,B         ; Suma B en ACC y guarda en ACC
  MOV B,[0F00H]   ; Guarda en B lo que hay en [m]
  JPZ loop        ; Si la operación anterior (ADD) es no afecta el carry C = 0 salta

  HALT            ; fin
```

## Aritméticas y Lógicas

```
       __    __
CLK __/  \__/


0 NOP: No operation
1 LDA: Load next word to REG A
2 LDB: Load next word to REG B
3 AND: And operation between REG B and REG A and store in REG A
4 OR:  Or operation between REG B and REG A and store in REG A
5 JMP: Jump to next word addr
6 JPZ: Jump if previous operation result Zero (no carry bit) to next word addr
7 INC: Increment REG A
8 DEC: Decrement REG A
9 EX:  Exchange content of REG A to REG B and REG B to REG A
A STA: Store REG A to next word addr
B STB: Store REG B to next word addr
C OUT: Write out REG A to bus and enable OE (Output Enable) to read from external

Estructura de instrucción:

S R  F  OP
0 00 00 000
| |  |  |
| |  |  +--> Op Code, ADD, LOAD, CMP, JMP, etc.
| |  +-----> Función interna 00 ADD, 01 SHIFT, 10 AND, 11 OR
| +--------> Registro 00 RZ, 01 RA, 10 RB, 11 RC
+----------> Fuente 

Opcode/func (5) | Par Registros (3)

00000             000
|                 |
|                 +--> indica que registros se usan en las operaciones con registros
+--------------------> Opcode


Opcodes

LD[A|R|I]
ST[A|R|I]

SUM
SUB


AND
XOR
OR

NOP



```
