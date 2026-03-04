cd \~/Nightotobufuscator

cat > obf_vm.lua << 'EOF'
-- obf_vm.lua - Tối ưu cho mode Loadstring + ASCII Art Night Guard
local input = arg[1]
if not input then
    print("❌ Usage: lua obf_vm.lua script.luau")
    os.exit(1)
end

print("🔥 Đang obfuscate loadstring với Hercules VM MAX...")

-- Chạy Hercules full mạnh nhất
os.execute(string.format('lua hercules-obfuscator/hercules.lua "%s" --max --antitamper --compressor --overwrite', input))

-- Tìm output
local out = input:gsub("%.[^%.]+$", "_obfuscated.lua")
if not io.open(out, "r") then out = input .. "_obfuscated.lua" end

-- Xóa watermark Hercules cũ
local lines = {}
for line in io.lines(out) do
    if not (line:find("Hercules") or line:find("Protected By") or line:find("hercules-obfuscator")) then
        table.insert(lines, line)
    end
end

-- Ghi lại với header sạch
local f = io.open(out, "w")
f:write("-- [Nightobufuscator - ASCII Art Mode]\n")
f:write("-- Protected Loadstring + Visual Night Guard\n\n")
for _, line in ipairs(lines) do
    f:write(line .. "\n")
end
f:close()

print("✅ XONG! Loadstring đã obfuscate cực mạnh → " .. out)
EOF
