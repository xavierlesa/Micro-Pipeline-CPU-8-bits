# Cosas por hacer

## Program Counter

Versión simplificada - 74HC193 Presettable synchronous 4-bit binary up/down counter

#### Señales:

| Señal   | Pin | Descripción                           |
|---------|-----|---------------------------------------|
| PC_EN   |     | Program Counter Enable                |
| ~PC_LDL |     | Program Counter Load LOW + !~MEM_CE   |
| ~PC_LDH |     | Program Counter Load HIGH + !~MEM_CE  |
| PC_RST  |     | Program Counter Reset                 |

`~` active low

`~MEM_CE`: Memory Chip Enable es active LOW, por lo que al cargar `PC_LDL` o `PC_LDH`
esta señal pasa a `~MEM_CE` a HIGH para desactivar la Memoria durante la carga del `PC`.

#### Conexión a los Buses:

Solo al bus de registros (REG_BUS) y es solo lectura.

```
REG_BUS /8/
        | |
        | |====/8/====> PC_ADDRL    8 bits
        | |
        | |====/8/====> PC_ADDRH    8 bits

```
