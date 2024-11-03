import pymem
import time
import json
print("soSocketApi run!")

while True:
    start_point = "HUI"
    end_point = "PIZDA"
    scan_in = 3
    scan_out = 2
    inData = ""
    outData = ""
    inHashData = ""
    outHashData = ""
    in_countByte = 0
    out_cuntByte = 0
    in_cmd_list = []
    out_cmd_str = ""
    out_cmd_list = []
    in_body_size = 0
    out_body_size = 0
    out_clear = ""

    print("Одижание подключения к миру..")
    while True:
        # читаем "signal2.txt" и выводим содердимое
        print("Зайдите в мир.. (с контент паком soSocket)")
        world_opan = ""
        with open('signal2.txt', 'r') as f:
            world_opan = f.read()
        if world_opan == "world_opan":
            # очищаем файл
            # with open("signal2.txt", "w") as f:
            #     f.write("")
            break
        time.sleep(1)
        
    print("Вы зашли в мир. Подключение к VoxelCore.exe")
    pm = pymem.Pymem("VoxelCore.exe")
    handle = pm.process_handle

    def sand_command(command):
        global outData, out_cmd_list, out_cmd_str
        for _ in range(2):
            # print(json.dumps(command, ensure_ascii=False, indent=4))
            print(f"sv --> vc {json.dumps(command)}")
            cmd_line = json.dumps(command)
            # убираем пробелы в cmd_line
            cmd_line = cmd_line.replace(" ", "")
            if cmd_line not in out_cmd_list:
                out_cmd_str += cmd_line + ";"
                if out_body_size > len(out_cmd_str):
                    out_cmd_list.append(cmd_line)
                    ostatok = out_body_size - len(out_cmd_str)
                    outData = start_point + out_cmd_str + "_"*ostatok + end_point
                    break
                else:
                    print("Ошибка вместимости буфера!")
                    out_cmd_str = ""
                    out_cmd_list = []
                    # outData = out_clear
                    # sand_command(command)
    def get_command(command):
        # print(json.dumps(command, ensure_ascii=False, indent=4))
        print(f"sv <-- vc {json.dumps(command)}")
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
            #для теста ставим блок в ответ игроку выше его
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
                # if command not in in_cmd_list:
                    # in_cmd_list.append(command)
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
        # print(f"read_console {type}: {find_console}")
        return find_console
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
        # print(f"write_console {type}: {find_console}")
        return find_console
    def validator(HashData, in_trig):
        global in_countByte, out_cuntByte, step_scan
        indexPattern = HashData.encode('utf-8')
        countByte = len(indexPattern)+10
        scan_cout = 0
        
        if in_trig:
            print(f"handshake IN: {HashData}")
            in_countByte = countByte
            scan_cout = scan_in
        else:
            print(f"handshake OUT: {HashData}")
            out_cuntByte = countByte
            scan_cout = scan_out
        validate_address = []
        for _ in range(scan_cout):
            
            print(f"\n validate_address: {validate_address}")
            prigress = step_scan/(scan_in + scan_out)
            print(f"progress scan: {prigress*100}%")
            next_region = pymem.pattern.pattern_scan_all(handle, indexPattern, return_multiple=True)
            step_scan +=1
            for i in next_region:
                try:
                    mem_value = pymem.memory.read_string(handle, i, countByte)
                    # if start_point in mem_value and end_point in mem_value:
                except UnicodeDecodeError as e:
                    print(f"Ошибка чтения строки по адресу {i}: {e}")
                else:
                    if i not in validate_address:
                        validate_address.append(i)
            prigress = step_scan/(scan_in + scan_out)
            print(f"progress scan: {prigress*100}%")
        return validate_address

    with open('hash.txt', 'r') as file:
        inData = file.read()
        inHashData = file.read()
    with open('hash2.txt', 'r') as file:
        outData = file.read()
        outHashData = file.read()
    out_body_size = len(outData) - len(start_point) - len(end_point)
    out_clear = start_point + "_"*out_body_size + end_point

    step_scan = 0
    in_valid = validator(inData, True)
    out_valid = validator(outData, False)

    # Записываем в файл signal.txt validate_sucess
    with open('signal.txt', 'w') as file:
        file.write("validate_success")
    outData = out_clear
    write_mem("OUT" ,out_valid, outData, out_cuntByte)
    timer_value = time.time()
    Runtime = True
    print(f"\n Подключение завершено. Можно играть!")
    while Runtime:
        # print("tick..")
        # проверка на world_quit мира
        current_time = time.time()
        if (current_time - timer_value) >= 2:
            with open('signal2.txt', 'r') as file:
                signal = file.read()
            if signal == "world_quit":
                with open('signal2.txt', 'w') as file:
                    file.write("")
                print("Вы вышли из мира. Отключение от процесса VoxelCore.exe")
                Runtime = False
            timer_value = time.time()
        read_status = read_mem("IN" ,in_valid, inHashData, in_countByte)
        write_status = write_mem("OUT" ,out_valid, outData, out_cuntByte)
        if not read_status:
            print("Ошибка чтения памяти. Перезайдите в мир и перезапустите api!")
        if not write_status:
            print("Ошибка записи памяти. Перезайдите в мир и перезапустите api!")
        # print("")
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