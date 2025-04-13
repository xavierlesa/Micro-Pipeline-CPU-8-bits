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



# **MIPS-16 Instruction Set Architecture (ISA)**

## **1. Introducción**
Mi implementación MIPS-16 es una versión compacta de la arquitectura MIPS, adaptada para trabajar con un conjunto de instrucciones de 16 bits y registros de 8 bits.
Esta ISA está diseñada especificamente para esta implementación pero puede ser útil para aplicaciones embebidas y entornos donde se requiere un diseño de CPU eficiente y simple.

## **2. Formato General de las Instrucciones**
Las instrucciones en MIPS-16 están compuestas por 16 bits. Dependiendo del tipo de instrucción, estos 16 bits se dividen en diferentes campos que pueden incluir un opcode, registros, valores inmediatos, y otros campos específicos.

### **Campos Comunes en las Instrucciones:**
- **Opcode (4 bits):** Determina la operación que se realizará.
- **Registro Destino (Rd, 3 bits):** Especifica el registro donde se almacenará el resultado.
- **Registro Fuente 1 (Rs1, 3 bits):** Especifica el primer registro fuente para la operación.
- **Registro Fuente 2 (Rs2, 3 bits):** Especifica el segundo registro fuente.
- **Función (Fn, 3 bits):** Especifica la función que se realizará en la instrucción.

También se pueden encontrar campos adicionales en las instrucciones:
- **Inmediato (Imm):** Un valor inmediato que puede variar en tamaño (6, 8 o 12 bits) dependiendo de la instrucción.


## Modo de las Instrucciones

La estrucura de las instrucciones se divide en diferentes modos de operación, y los primeros 4 bits
se refieren siempre al Opcode.


| Modo 0    | Modo 1    | Modo 2    | Modo 3    | Modo 4      |
| --------- | --------- | --------- | --------- | ----------- |
| 4- Opcode | 4- Opcode | 4- Opcode | 4- Opcode | 4- Opcode   |
| 3- Rd     | 3- Rd     | 3- Immed3 | 3- Rd     | 12- Immed12 |
| 3- Rs1    | 3- Rs1    | 3- Rs1    | 1- ???    |             | 
| 3- Rs2    | 6- Immed6 | 3- Rd2    | 8- Immed8 |             |
| 3- Fn     |           | 3- Immed3 |           |             |


#### Aplicación de modos:

| Modo 0    | Modo 1    | Modo 2    | Modo 3    | Modo 4      |
| --------- | --------- | --------- | --------- | ----------- |
| **ALU**   | **ALU**   | **STORE** | **LOAD**  | **JUMP**  |
| ADD       | ADDI      | SB        | LI        | JA          |
| SUB       |           |           |           | JAL         |
| AND       | **LOAD**  | **BRANCH**|           |             |
| OR        | LB        | BEQ       |           |             |
| XOR       |           |           |           |             |



## **3. Tipos de Instrucciones**

### **3.1. Instrucciones Tipo R (Register-Register)**
Las instrucciones tipo R operan entre registros y almacenan el resultado en un registro de destino. 

#### **Formato:**
```
| Opcode (4 bits) | Rs1 (3 bits) | Rs2 (3 bits) | Rd (3 bits) | Function (3 bits) |
```

#### **Ejemplos:**
- **ADD Rd, Rs1, Rs2:** Suma los valores de `Rs1` y `Rs2`, y almacena el resultado en `Rd`.
  - **Función:** 000
- **SUB Rd, Rs1, Rs2:** Resta el valor de `Rs2` de `Rs1`, y almacena el resultado en `Rd`.
  - **Función:** 001
- **AND Rd, Rs1, Rs2:** Realiza una operación AND bit a bit entre `Rs1` y `Rs2`, almacenando el resultado en `Rd`.
  - **Función:** 010


### **3.2. Instrucciones Tipo I (Immediate)**
Las instrucciones tipo I operan con un registro fuente y un valor inmediato, que es un número constante codificado directamente en la instrucción.

#### **Formato:**
```
| Opcode (4 bits) | Rd (3 bits) | Rs1 (3 bits) | Immediate (6 bits) |
```

#### **Ejemplos:**
- **ADDI Rd, Rs1, Imm6:** Suma el valor de `Rs1` con un inmediato de 6 bits, y almacena el resultado en `Rd`.



#### **3.3. Instrucciones Tipo B (Branch)**
Estas instrucciones realizan un salto basado en la comparación de registros.

#### **Formato:**
```
| Opcode (4 bits) | Immediate (3 bits) | Rs1 (3 bits) | Rs2 (3 bits) | Immediate (3 bits) |
```

#### **Ejemplo:**
- **BEQ Rs1, Rs2, Imm6:** Si `Rs1` es igual a `Rs2`, salta a la dirección relativa `Imm6`. el MSB de `Imm6` determina si salta hacia arriba o hacia abajo dejando un salto efecntivo de `+/- 32 bytes`.


### **3.4. Instrucciones Tipo JA (Jump)**
Las instrucciones tipo J manejan saltos absolutos a una dirección específica.
Estas instrucciones permiten realizar saltos incondicionales a una dirección específica de `12 bits` más los 4 bits de PC.

#### **Formato:**
```
| Opcode (4 bits) | Immediate (12 bits) |
```

#### **Ejemplo:**
- **JA Imm12:** Salta a la dirección formada por los 4 bits altos de PC y los 12 bits inmediatos.

#### **3.4.1. Saltos Absolutos con Enlace (JAL)**
Permite saltar a una subrutina y almacenar la dirección de retorno.

#### **Formato:**
```
| Opcode (4 bits) | Immediate (12 bits) |
```

#### **Ejemplo:**
- **JAL Imm12:** Salta a la dirección `PC + Imm12` y guarda la dirección de retorno en los registros `R6` y `R7`.

### **3.4. Instrucciones de Carga y Almacenamiento (Load/Store)**
Estas instrucciones manejan la carga y el almacenamiento de datos entre registros y memoria.

#### **Formato para Carga (LD):**
```
| Opcode (4 bits) | Rs1 (3 bits) | Rd (3 bits) | Immediate (6 bits) |
```

#### **Ejemplo:**
- **LDL Rd, Rs1, Imm6:** Carga los 8 bits inferiores (Low Byte) de la palabra de 16 bits en `Rd`.
- **LDH Rd, Rs1, Imm6:** Carga los 8 bits superiores (High Byte) de la palabra de 16 bits en `Rd`.

#### **Formato para Almacenamiento (ST):**
```
| Opcode (4 bits) | Rs1 (3 bits) | Rd (3 bits) | Immediate (6 bits) |
```

#### **Ejemplo:**
- **STL Rs1, Rd, Imm6:** Almacena los 8 bits inferiores de `Rd` en la dirección de memoria calculada como `Rs1 + Imm6`.
- **STH Rs1, Rd, Imm6:** Almacena los 8 bits superiores de `Rd` en la dirección de memoria calculada como `Rs1 + Imm6`.

