-- Пример sand_data, get_data: GAYCOMMAND;GAYCOMMAND;GAYCOMMAND
--16kb 1 пакет

buffer_size = 99--99
start_point = "HUI"
end_point = "PIZDA"

--отправляется на сервак
sand_data = ""
HASH = ""
sand_data_size = 0
sand_list = {}
sand_list_size = 0
sand_list_str = ""

--получаем данные с сервера
get_data = ""
HASH2 = ""
get_list_str = ""
get_list = {}
get_list_size = 0
validate = ""
out_signal = false

local function split(inputstr, sep)
   if sep == nil then
       sep = "%s"  -- Если разделитель не указан, используем пробел
   end
   local t = {}
   for str in string.gmatch(inputstr, "([^"..sep.."]+)") do
       table.insert(t, str)
   end
   return t
end
local function pocket_stats()
   console.log("Server команд: " .. #get_list)
   console.log("Server команды заняли: "..get_list_size.. " байт")
   console.log("Client команд: " .. #sand_list)
   console.log("Client команды заняли: "..#sand_list_str.. " байт")
end
local function get_command(command)
   console.log("server --> client: "..json.tostring(command, false))
   local cmd = command.com
   local data = command.dt
   if cmd == "GAYCOMMAND" then
      -- print("Сервер сообщил вам что вы пидор!")
   elseif cmd == "obp" then
      -- block.place(data.x, data.y, data.z, data.id)
      block.set(data.x, data.y, data.z, data.id)
   elseif cmd == "obb" then
      -- block.destruct(data.x, data.y, data.z)
      block.set(data.x, data.y, data.z, 0)
   end
end
local function generate_hash()
   local trans_data = {"A","B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T", "U", "V", "W", "X", "Y", "Z"}
   local mega_hash = ""
   for i = 1, buffer_size do
      local hash = tostring(math.random())
      hash = string.sub(hash, 3, 12)
      -- print(hash)
      local trans_hash = ""
      for i = 1, #hash do
         local ass = string.sub(hash, i, i)
         local s = trans_data[tonumber(ass) + 1]
         -- print(ass..s)
         trans_hash = trans_hash .. s
      end
      mega_hash = mega_hash .. trans_hash
   end
   -- local hash_b = utf8.tobytes(mega_hash)
   -- mega_hash = utf8.tostring(hash_b)
   return tostring(mega_hash)
   
end
local function cl_send()
   local body = string.rep("__________", buffer_size)
   local buffer = start_point.. body ..end_point
   return buffer
end
function sand_command(command)
   -- цикл на повторение сообщения 2 раза
   local bodyjs = json.tostring(command, false)
   local body = string.gsub(bodyjs, "%s+", "")
   console.log("server <-- client: "..bodyjs)
   for i = 1, 3 do
      if not sand_list[body] then
         -- Добавляем body в таблицу команд
         sand_list_size = sand_data_size + #body + 1
         sand_list_str = sand_list_str .. body .. ";"
         local start_cut = #start_point + #sand_list_str
         -- console.log("buffer size: "..buffer_size)
         local need_size = #end_point + start_cut
         -- console.log("need size: "..need_size)
         if sand_data_size > need_size then
            local ostatok_count = sand_data_size - need_size
            -- console.log("ostatok count: "..ostatok_count)
            table.insert(sand_list, body)
            sand_list[body] = true
            local end_cut = ostatok_count + start_cut
            local ostatok = string.sub(clear_msg, start_cut, end_cut-1)
            -- console.log("ostatok: ".. string.len(ostatok))
            sand_data = start_point .. sand_list_str .. ostatok .. end_point
            break
         else
            console.log("Ошибка вместимости буфера клиента!")
            sand_list_str = ""
            sand_list_size = 0
            sand_list = {}
         end
      end
   end
end
local function sand_hash(body)
   local buffer = start_point.. body ..end_point
   return tostring(buffer)
end
local function sandHandShake()
   HASH = generate_hash()
   sand_data = sand_hash(HASH)
   sand_data_size = string.len(sand_data)
   clear_msg = cl_send()
   local path = file.find("hash.txt")
   -- print(path)
   file.write(path, sand_data)
end
local function getHandShake()
   HASH2 = generate_hash()
   get_data = sand_hash(HASH2)
   -- sand_data_size = string.len(sand_data)
   -- clear_msg = cl_send()
   local path = file.find("hash2.txt")
   -- print(path)
   file.write(path, get_data)
end
local function get_masage(data)
   if string.find(data, ";") then
      local pattern = "[^;]+"
      local z = 0
      for chunk in string.gmatch(data, pattern) do
         z = z + 1
         local cmd_line = chunk
         if z == 1 then   
            cmd_line = string.sub(chunk,#start_point+1,#chunk)
         end
         if string.find(cmd_line, "{") then
            if not get_list[cmd_line] then
               get_list_size = get_list_size + #cmd_line
               local need_size = get_list_size + #start_point + #end_point
               if need_size < sand_data_size then
                  -- добавляем в список
                  table.insert(get_list, cmd_line)
                  get_list[cmd_line] = true
                  -- console.log(cmd_line)s
                  local cmd = json.parse(cmd_line)
                  get_command(cmd)
               else
                  console.log("Ошибка вместимости буфера!")
                  local document = Document.new("core:console")
                  document.log.text = ""
                  get_list = {}
                  get_list_size = 0
               end
            end
         end
      end
   end
end
function on_world_open()
   signal_path = file.find("signal.txt")
   local path = file.find("signal2.txt")
   file.write(path, "world_opan")
   sandHandShake()
   getHandShake()
end
titi = 0
function on_world_tick()
   world.set_day_time(0.5) 
   local timi = "time:(" .. tostring(time.uptime()) .. ")"
   print(sand_data)
   -- -- print(timi)

   if #validate <= 2 then
      if titi >= 10 then
         validate = file.read(signal_path)
      else
         titi = titi +1
      end
   else
      if not out_signal then
         out_signal = true
         file.write(signal_path, "")
      end
      local Sex_code = "return function(x) return x .. '' end"
      local func = loadstring(Sex_code)()
      get_masage(get_data)
   end
end
function on_block_placed(blockid, x, y, z)
   local set_block = {
      com = "obp",
      dt = {
         id = blockid,
         x = x,
         y = y,
         z = z
      }
   }
   sand_command(set_block)
   -- print("on block place")
end
function on_block_broken(blockid, x, y, z)
   local del_block = {
      com = "obb",
      dt = {
         id = blockid,
         x = x,
         y = y,
         z = z
      }
   }
   sand_command(del_block)
end
function on_world_quit()
   local path = file.find("signal2.txt")
   file.write(path, "world_quit")
end
