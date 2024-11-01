import pymem
import time
import json

start_point = "HUI"
end_point = "PIZDA"
inData = ""
outData = ""
inHashData = ""
outHashData = ""
in_countByte = 0
out_cuntByte = 0
in_cmd_list = []
out_cmd_list = ""
in_body_size = 0
out_body_size = 0
out_clear = ""


pm = pymem.Pymem("VoxelCore.exe")
handle = pm.process_handle

def sand_command(command):
    global outData
    global out_cmd_list
    # print(json.dumps(command, ensure_ascii=False, indent=4))
    print(f"outCMD: {json.dumps(command)}")
    cmd_line = json.dumps(command)
    # убираем пробелы в cmd_line
    cmd_line = cmd_line.replace(" ", "")
    out_cmd_list += cmd_line + ";"
    if out_body_size > len(out_cmd_list):
        ostatok = out_body_size - len(out_cmd_list)
        outData = start_point + out_cmd_list + "_"*ostatok + end_point
    else:
        print("Ошибка вместимости буфера!")
        out_cmd_list = ""
        # outData = out_clear
        sand_command(command)
    
def get_command(command):
    # print(json.dumps(command, ensure_ascii=False, indent=4))
    print(f"inCMD: {json.dumps(command)}")
    cmd = command["com"]
    if cmd == "obp":
        data = command["dt"]
        id = data["id"]
        x = data["x"]
        y = data["y"]
        z = data["z"]
        # print(f"Блок id {id} поставили на X:{x} Y:{y} Z:{z}" )

        out_cmd = {
            "com": cmd,
            "dt":{
                "id": id,
                "x": x,
                "y": y+1,
                "z": z
            }
        }
        sand_command(out_cmd)
def read_data(json_strings):
    global in_cmd_list
    # json_strings = '{"dt":{"id":9,"z":-6,"y":108,"x":-21},"com":"obb"};{"dt":{"id":9,"z":-5,"y":108,"x":-21},"com":"obb"};{"dt":{"id":14,"z":-3,"y":108,"x":-23},"com":"obb"};'
    json_parts = json_strings.strip().split(';')
    for part in json_parts:
        if part and "com" in part:  # Проверяем, что строка не пустая
            # print(part)
            command = json.loads(part)
            # print(slovar)
            if command not in in_cmd_list:
                in_cmd_list.append(command)
                get_command(command)
def read_mem(type ,validate_address, HashData, countByte):
    find_console = False
    # print(f"\n validate_address: {validate_address}")
    n = 0
    for i in validate_address:
        n += 1
        try:
            mem_value = pymem.memory.read_string(handle, i, countByte)
            if start_point in mem_value and end_point in mem_value:
                # print(f"({n}) {mem_value}")
                if HashData != mem_value.strip():
                    body = mem_value[len(start_point):-len(end_point)]
                    read_data(body)
                find_console = True
            # else:
            #     validate_address.remove(i)
        except UnicodeDecodeError as e:
            pass
            # print(f"({n}) Ошибка чтения строки по адресу {i}: {e}")
    print(f"read_console {type}: {find_console}")
def write_mem(type ,validate_address, HashData, countByte):
    HashData = HashData[:-2]
    byteData = HashData.encode('utf-8')
    find_console = False
    # print(f"\n validate_address: {validate_address}")
    n = 0
    for i in validate_address:
        n += 1
        try:
            pymem.memory.write_string(handle, i, byteData)
        except Exception as e:
            print(f"({n}) Ошибка записи строки по адресу {i}: {e}")
        else:
            find_console = True
    print(f"write_console {type}: {find_console}")
def validator(HashData, in_trig):
    global in_countByte
    global out_cuntByte
    indexPattern = HashData.encode('utf-8')
    countByte = len(indexPattern)+10
    if in_trig:
        print(f"handshake IN: {HashData}")
        in_countByte = countByte
    else:
        print(f"handshake OUT: {HashData}")
        out_cuntByte = countByte
    validate_address = []
    for _ in range(5):
        print(f"\n validate_address: {validate_address}")
        next_region = pymem.pattern.pattern_scan_all(handle, indexPattern, return_multiple=True)
        for i in next_region:
            try:
                mem_value = pymem.memory.read_string(handle, i, countByte)
                if i not in validate_address:
                    validate_address.append(i)
                # if start_point in mem_value and end_point in mem_value:
                #     
                #         print(mem_value)
                #         validate_address.append(i)
            except UnicodeDecodeError as e:
                print(f"Ошибка чтения строки по адресу {i}: {e}")
    return validate_address

with open('hash.txt', 'r') as file:
    inData = file.read()
    inHashData = file.read()
with open('hash2.txt', 'r') as file:
    outData = file.read()
    outHashData = file.read()
out_body_size = len(outData) - len(start_point) - len(end_point)
out_clear = start_point + "_"*out_body_size + end_point

in_valid = validator(inData, True)
out_valid = validator(outData, False)

# Записываем в файл signal.txt validate_sucess
with open('signal.txt', 'w') as file:
    file.write("validate_success")
outData = out_clear
write_mem("OUT" ,out_valid, outData, out_cuntByte)
while True:
    print("tick..")
    # input("послать GAYCOMMAND..")
    read_mem("IN" ,in_valid, inHashData, in_countByte)
    write_mem("OUT" ,out_valid, outData, out_cuntByte)
    # outData = out_clear
    print("")
    time.sleep(0.05)
    
# out_cmd = {
#         "com": "GAYCOMMAND",
#         "dt":{
#             "id": str(time.time()).split(".")[1],
#             "x": 9,
#             "y": 1,
#             "z": 1
#         }
#     }
# sand_command(out_cmd)
# print("outData: " + outData)