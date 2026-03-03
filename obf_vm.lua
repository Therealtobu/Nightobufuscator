cd \~/Nightobufuscator

cat > obf_vm.lua << 'EOF'
-- obf_vm.lua - Hercules VM THẬT + TỰ ĐỘNG CHÈN "Nightguard encrypted" (đã mã hóa)
local input = arg[1]
if not input then
    print("❌ Usage: lua obf_vm.lua script.luau")
    os.exit(1)
end

-- Đọc code gốc
local f = io.open(input, "r")
local original = f:read("*all")
f:close()

-- Đoạn watermark đã mã hóa (không lộ chữ Nightguard encrypted)
local watermark = [[
print((function(s,k)return s:gsub(".",function(c)return string.char(c:byte()\~k)end)end)('dCMB^M_KXN\nODIXSZ^ON',42))
]]

-- Ghép watermark vào đầu script
local new_code = watermark .. "\n" .. original

-- Ghi tạm file mới
local temp_input = input .. ".temp"
local tf = io.open(temp_input, "w")
tf:write(new_code)
tf:close()

print("🔥 Đang obfuscate Hercules VM MAX + Nightguard watermark...")

-- Chạy Hercules full mạnh nhất
os.execute(string.format('lua hercules-obfuscator/hercules.lua "%s" --max --antitamper --compressor --overwrite', temp_input))

-- Tìm output
local out = temp_input:gsub("%.[^%.]+$", "_obfuscated.lua")
if not io.open(out, "r") then out = temp_input .. "_obfuscated.lua" end

-- Ghi lại file cuối cùng (chỉ giữ Nightguard watermark runtime)
local final = io.open(out, "w")
final:write("-- [Nightguard Encrypted - Hercules REAL VM MAX]\n")
for _, line in ipairs(lines) do
    final:write(line .. "\n")
end
final:close()

-- Xóa file tạm
os.remove(temp_input)

print("✅ XONG! Nightguard encrypted đã được chèn + mã hóa + VM bảo vệ → " .. out)
EOF
