"riscv64-unknown-elf-gcc.exe -mabi=ilp32 -march=rv32i -static -mcmodel=medany -S -o main.S main.c"

"riscv64-unknown-elf-gcc.exe -mabi=ilp32 -march=rv32i -static -mcmodel=medany -c -o main.o main.c"

"riscv64-unknown-elf-gcc.exe -mabi=ilp32 -march=rv32i -static -mcmodel=medany -nostdlib -nostartfiles -T linker.ld -o final.elf main.o"

"riscv64-unknown-elf-objdump.exe -m riscv -d final.elf"

"riscv64-unknown-elf-objcopy -I binary -O elf32-little final.bin final1.elf"

"riscv64-unknown-elf-objdump.exe -m riscv -D final1.elf"
"0x00200093"
"""

with open("final.bin", "rb") as f:
    data = f.read()

output = ""

for i in range(0, len(data), 4):
    hex_val, = struct.unpack("<L", data[i:i+4])
    output += hex(hex_val)[2:].zfill(8) + "\n"
print(output)
"""

import struct
import subprocess

from flask import Flask, request, jsonify, render_template

app = Flask(__name__, template_folder="")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/assemble", methods=["POST"])
def assemble():
    data = request.json.get("data")

    with open("user_codes/assemble.c", "w") as f:
        f.write(data)
    
    result = subprocess.run("riscv64-unknown-elf-gcc.exe -mabi=ilp32 -march=rv32i -static -mcmodel=medany -S -o user_codes/assemble.S user_codes/assemble.c")
    print(result)

    with open("user_codes/assemble.S", "r") as f:
        assmebled_code = f.read()
    
    assmebled_code_formatted = assmebled_code[assmebled_code.index("main:"):assmebled_code.index(".size")]

    return jsonify({"data": assmebled_code_formatted})


@app.route("/disassemble", methods=["POST"])
def disassemble():
    data = request.json.get("data")

    disassemble_bin = b""
    for line in data.split("\n"):
        line = line.strip()
        if not line:
            continue
        val = int(line, 16)
        disassemble_bin += struct.pack("<L", val)
    
    with open("user_codes/disassemble.bin", "wb") as f:
        f.write(disassemble_bin)

    result = subprocess.run("riscv64-unknown-elf-objcopy -I binary -O elf32-little user_codes/disassemble.bin user_codes/disassemble.elf")
    print(result)
    result = subprocess.run("riscv64-unknown-elf-objdump.exe -m riscv -M no-aliases -D user_codes/disassemble.elf", capture_output=True)
    print(result)

    disassmebled_code = result.stdout.decode("utf-8")
    print(disassmebled_code)
    #result.returncode
    disassmebled_code_formatted = ""
    for line in disassmebled_code.split("\n"):
        tokens = line.split("\t")
        if len(tokens) == 4:
            disassmebled_code_formatted += tokens[2] + "\t" + tokens[3]

    return jsonify({"data": disassmebled_code_formatted})

app.run(host="0.0.0.0", port=80, debug=True)