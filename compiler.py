#!/usr/local/bin/python3

import sys
import re

type_r = r"(?P<rd>$|r[0-7])\s*,\s*(?P<rs>$|r[0-7])\s*,\s*(?P<rt>$|r[0-7])\s*$"
type_i = r"(?P<rd>$|r[0-7])\s*,\s*(?P<imm>\w+)"

opcodes = dict([
    ("add", type_r),    # add without carry
    ("adc", type_r),    # add with carry
    ("sub", type_r),    # subtract without borrow
    ("sbc", type_r),    # subtract with borrow
    ("and", type_r),    # bitwise and
    ("or",  type_r),    # bitwise or
    ("xor", type_r),    # bitwise xor
    ("sll", type_r),    # shift left logical

    ("addi", type_i),   # add immediate
    ("ld", type_i),     # load byte
    ("lb", type_i),
    ("st", type_i),     # store byte
    ("sb", type_i),
    ("beq", type_i),    # branch if equal
    ("li", type_i),     # load immediate
    ("ja", type_i),     # jump
    ("j", type_i),
    ("jal", type_i),    # jump and link
    ("jl", type_i),
])


def strip_comments(text):
    return re.sub(r'\s*[;#]+.*$', '', text)


def chunkstring(string, length):
    return (string[0 + i: length + i] for i in range(0, len(string), length))


def match_label(text):
    pattern = r'^\s*(?P<label>\w+):'
    return re.match(pattern, text)


def parse_section(text):
    # Definir el patrón regex
    db_pattern = (
        r'(?P<label>\w+)\s+(?P<op>\w+)\s+"(?P<data>.+)",?\s*(?P<values>(\d+,\s*)*\d+)'
    )
    equ_pattern = r"(?P<label>\w+)\s+(?P<op>\w+)\s+(?P<fn>len|start)\((?P<b>\w+)\)"

    # Realizar la búsqueda de coincidencias en la línea
    match = re.match(db_pattern, text)
    equ_match = re.match(equ_pattern, text)

    if match:
        label = match.group("label")
        op = match.group("op")
        data = match.group("data")
        values = match.group("values").split(", ")

        # Procesar los datos para obtener una lista de caracteres
        data = [ord(c) for c in data] + [int(c) for c in values]

        return {"label": label, "op": op, "data": data}

    elif equ_match:
        return equ_match.groupdict()


def populate_sections(sections, section, line):
    section_line = line.strip()
    vdata = parse_section(section_line)
    if vdata:
        if vdata["op"] == "db":
            sections[section].update(
                {vdata["label"]: vdata["data"]})
        elif vdata["op"] == "equ":
            fn = vdata["fn"]
            raw_bytes = sections[section].get(vdata["b"])
            sections[section].update({
                vdata["label"]: len(raw_bytes) if fn == "len" else 0
            })


def print_sections(sections):
    # Itera sobre las sections y las labels para mostrarlo
    for section, data in sections.items():
        print(f"Section {section}: >>")
        for label, dbytes in data.items():
            if isinstance(dbytes, list):
                text = f"{label} ({len(dbytes)}): "
                print(text)
                print(dbytes)
                print()


def main():
    if len(sys.argv) <= 1:
        print("Custom assembler compiler - 202310 V 1.0")
        print()
        print("Usage:")
        print()
        print("    compiler file.asm")
        return

    arg = sys.argv[1]
    unparsed_opcodes = []
    labels = {}
    section = ""
    sections = {}
    in_section = False

    org = 0x0000

    print(f"\r\nCompiling file {arg}\r\n")

    with open(arg, "rb") as fopen:
        for n, _line in enumerate(fopen):
            line = _line.decode().strip()

            # strip comments
            line = strip_comments(line)

            if not line:
                continue

            # end and start a new section/block
            if in_section and line.startswith(".endsection"):
                in_section = False
                section = ""
                continue

            if in_section:
                populate_sections(sections, section, line)
                continue

            # define org
            if line.startswith(".org: "):
                org = line.removeprefix(".org: ").strip()
                continue

            if line.startswith(".section "):
                section = line.removeprefix(".section ").strip(":")
                sections[section] = {}
                in_section = True
                continue

            if label := match_label(line):
                label = label.groupdict()['label']
                labels[label] = -1
                print(f"[{label}]")
                line = label

            unparsed_opcodes.append(line)

    print(40 * "-")
    print(f"Program start at {org}")
    print()

    # Itera sobre los opcodes y valida, también calcula las direcciones
    addr_int = 0
    for ix, raw_opcode in enumerate(unparsed_opcodes):
        # puede ser un opcode o un label
        if opcode := re.match(
            r'^\s*(?P<label>\w+)\s*$',
            raw_opcode
        ):
            if raw_opcode in labels and labels[raw_opcode] != -1:
                sys.exit(f"Label {raw_opcode} already defined at {labels[raw_opcode]}")
            labels[raw_opcode] = addr_int

        elif opcode := re.match(
            r'^\s*(?P<mnemonic>\w+)\s+(?P<operands>.*)\s*$',
            raw_opcode
        ):
            mnemonic = opcode.groupdict()["mnemonic"]
            operands = opcode.groupdict()["operands"]

            if mnemonic not in opcodes:
                sys.exit(f"Opcode `{mnemonic} {operands}` not found at {addr_int:04x}")

            operands_re = opcodes[mnemonic]
            print(f"{addr_int:04x}: {mnemonic} {operands_re}")

            if operand := re.match(operands_re, operands):
                rd, rs, rt = operand.groups()
                print(f"{addr_int:04x}: {mnemonic} {rd}, {rs}, {rt}")

        else:
            print(f">> {addr_int:04x}: {raw_opcode}")
            print("Error: opcode not found")
        # print(f"{addr_int:04x}: {raw_opcode}")

        if raw_opcode in labels:
            continue
        addr_int = addr_int + 1

    print("Sections:")
    print()
    print_sections(sections)


if __name__ == "__main__":
    main()
