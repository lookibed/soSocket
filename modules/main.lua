SAPI = {}
SAPI.data_ = ""
SAPI.out_ = {}
SAPI.dis_ = nul

SAPI.dis = function (func)
   SAPI.dis_ = func
end
SAPI.con = function (ip, nickname)
   if file.exists("export:inData") then
      print("SAPI: CONNECT FAULED")
   else
      for i, load in ipairs(SAPI.out_) do
         load("u++")
      end
      file.write("export:inData", ip .. "/4307/16284/~cn" .. nickname .. "/" .. json.parse(file.read("world:world.json")).generator .. "/" .. world.get_seed() .. "/" .. table.concat(pack.get_installed(), ",") .. "\t".. SAPI.data_)
      SAPI.data_ = ""
   end
end

--Data
SAPI.out = function (func)
    table.insert(SAPI.out_, func)
end
SAPI.data = function (dat)
    SAPI.data_ = SAPI.data_ .. dat .. "\t"
end