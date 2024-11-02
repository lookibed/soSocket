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
sand_list_str = ""

--получаем данные с сервера
get_data = ""
HASH2 = ""
get_list_str = ""
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
local function get_command(command)
   -- print(json.tostring(command, true))
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
function sand_masage(data)
   -- цикл на повторение сообщения 2 раза
   for i = 1, 3 do
      local bodyjs = json.tostring(data, false)
      local body = string.gsub(bodyjs, "%s+", "")
      
      -- Добавляем body в таблицу команд
      sand_list_str = sand_list_str .. body .. ";"
      local start_cut = #start_point + #sand_list_str
      -- print("buffer size: "..buffer_size)
      local need_size = #end_point + start_cut
      -- print("need size: "..need_size)
      if sand_data_size > need_size then
         local ostatok_count = sand_data_size - need_size
         -- print("ostatok count: "..ostatok_count)
         local end_cut = ostatok_count + start_cut
         local ostatok = string.sub(clear_msg, start_cut, end_cut-1)
         -- print("ostatok: ".. string.len(ostatok))
         sand_data = start_point .. sand_list_str .. ostatok .. end_point
         -- -- print("buffer: "..string.len(buffer))
         -- return buffer
         break
      else
         -- print("Ошибка вместимости буфера!")
         sand_list_str = ""
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
   -- если в data есть ;
   if string.find(data, ";") then
	   -- разбиваем на массив по ; и перебираем каждый
      local z = 0
      for i in string.gmatch(data, "[^;]+") do
         if string.find(i, "{") then
            z = z + 1
            if z == 1 then
               i = string.sub(i,#start_point+1,#i)
            end
            -- print(z.." "..i)
            if not string.find(get_list_str, i) then
               get_list_str = get_list_str .. i .. ";"
               local cmd = json.parse(i)
               get_command(cmd)
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
      local document = Document.new("core:console")
      document.log.text = ""
      -- get_data = get_data
      console.log(get_data)
      get_masage(get_data)
      -- collectgarbage("collect")
      -- типа это все что нужно на отправку в этом тике поэтому чистим sand_data 
      -- sand_data = clear_msg
   end
end
function on_block_placed(blockid, x, y, z)
   -- sand_data = cl_send()
   local set_block = {
      com = "obp",
      dt = {
         id = blockid,
         x = x,
         y = y,
         z = z
      }
   }
   sand_masage(set_block)
   
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
   sand_masage(del_block)
end
function on_world_quit()
   local path = file.find("signal2.txt")
   file.write(path, "world_quit")
end
