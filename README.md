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

- Aritméticas y Lógicas

    Instrucciones para operaciónes matemáticas como suma, resta, 
    multiplicación, división, inc/dec, etc.

- Saltos y llamadas a subrutinas

    Solo vamos a contar con saltos condiciones e incondicionales así como 
    llamadas a subrutinas.

- Otras / Miscelanias

    Otras instrucciones como HALT y NOP


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
|MOV r,x    | 57H      | Fx 57       |  Rr <- 57H, Carga en el Rr el inmediato 57H.       |



### Indirecto

### Directo

### Swap

|Operador   | Operando | Hexa        |  Descripción                                       |
|-----------|----------|-------------|----------------------------------------------------|
|MOV A,x    | 57H      | F4 57       |  RA <- 57H, Carga en el ACC el inmediato 57H.       |
|MOV A,[m]  | 1F00H    | E4 00 1F    |  RA <- [1F00H], Carga en el ACC lo que existe en la |
|           |          |             |  dirección de memoria 1F00H. La dirección se carga |
|           |          |             |  desde el LSB al MSB y se lee desde MSB al LSB.    |
|MOV [m],A  | 1F00H    | D4 00 1F    |  [1F00H] <- RA, Carga en la dirección de memoria    |
|           |          |             |  1F00H lo que hay en el ACC.                       |
|MOV B,x    | 57H      | F8 57       |  RB <- 57H, Carga en RB el inmediato 57H.           |
|MOV B,[m]  | 1F00H    | E8 00 1F    |  RA <- [1F00H], Carga en RB lo que existe en la     |
|           |          |             |  dirección de memoria 1F00H.                       |
|MOV [m],B  | 1F00H    | D8 00 1F    |  [1F00H] <- RA, Carga en la dirección de memoria    |
|           |          |             |  1F00H lo que hay en RB.                           |


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


LW
JMP
NOP

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

## Ejemplo: contador de numeros impares  

Un programa que cuenta de forma impar desde 1 hasta 255 (8 bits)
0b00000000
0b00000001 - impar
0b00000011
0b00000101
0b00000111

CODE:

0x00: 0x01 LDA    - Pone el REG A en 0b00000001
0x01: 0x01 01     - word 0x01
0x02: 0x0C OUT    - Pasa el contenido del REG A a la salida
0x03: 0x07 INC    - Incrementa el REG A
0x04: 0x07 INC    - Incrementa el REG A otra vez porque es impar
0x05: 0x0C OUT    - Pasa el contenido del REG A a la salida
0x06: 0x05 JMP    - Salto incondicional a la posición 0x03
0x07: 0x03 03     - word 0x03


Estructura de instrucción:

S R  F  OP
0 00 00 000
| |  |  |
| |  |  +--> Op Code, ADD, LOAD, CMP, JMP, etc.
| |  +-----> Función interna 00 ADD, 01 SHIFT, 10 AND, 11 OR
| +--------> Registro 00 RZ, 01 RA, 10 RB, 11 RC
+----------> Fuente 


# Grupos de instrucciones

```
