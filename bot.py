import discord
from discord import app_commands
import asyncio
import os
import tempfile
from dotenv import load_dotenv
from flask import Flask
import threading

load_dotenv()

# ================== KEEP ALIVE (cho Render Free không sleep) ==================
app = Flask(__name__)

@app.route('/')
def home():
    return "✅ Nightobufuscator Bot đang chạy 24/7 trên Render Free!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port, debug=False)

# ================== DISCORD BOT ==================
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

WRAPPER = "obf_vm.lua"  # file wrapper với Nightobufuscator watermark

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot {bot.user} ONLINE - Nightobufuscator VM sẵn sàng!")

@tree.command(name="obf", description="Obfuscate Luau script với Nightobufuscator VM mạnh nhất (free)")
async def obf(interaction: discord.Interaction, file: discord.Attachment):
    await interaction.response.defer()

    if file.size > 10 * 1024 * 1024:
        return await interaction.followup.send("❌ File lớn hơn 10MB!")

    if not os.path.exists(WRAPPER):
        return await interaction.followup.send("❌ Chưa có obf_vm.lua!")

    status_msg = await interaction.followup.send("🔄 Bắt đầu obfuscate Nightobufuscator VM MAX...")

    code = (await file.read()).decode('utf-8', errors='ignore')

    try:
        # Bước 1: Lưu code tạm
        with tempfile.NamedTemporaryFile(mode='w', suffix='.luau', delete=False, encoding='utf-8') as f:
            f.write(code)
            inp = f.name

        await status_msg.edit(content="📥 Bước 1: Tải và lưu script gốc... [■■■■■■■■■■] 10%")

        # Giả lập progress bar (vì Hercules không có progress thật, dùng sleep để update từng bước)
        await asyncio.sleep(1)  # Giả thời gian chèn watermark
        await status_msg.edit(content="🔑 Bước 2: Chèn Nightguard encrypted watermark... [■■■■■■■■■■■■■■■■] 30%")

        await asyncio.sleep(1)  # Giả thời gian chuẩn bị
        await status_msg.edit(content="🚀 Bước 3: Chạy Hercules VM + Anti-Tamper + Compressor... [■■■■■■■■■■■■■■■■■■■■■■■■■■] 50%")

        # Chạy subprocess thật
        proc = await asyncio.create_subprocess_exec("lua", WRAPPER, inp,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)
        await proc.communicate()

        await asyncio.sleep(1)  # Giả thời gian xử lý output
        await status_msg.edit(content="🧹 Bước 4: Xóa watermark cũ + thêm Nightobufuscator header... [■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■] 70%")

        out = inp.replace('.luau', '_obfuscated.lua')
        if not os.path.exists(out):
            return await status_msg.edit(content="❌ Lỗi obfuscate, thử lại!")

        await asyncio.sleep(1)  # Giả thời gian thêm user watermark
        await status_msg.edit(content="📤 Bước 5: Chuẩn bị gửi file obfuscated... [■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■] 90%")

        with open(out, 'a', encoding='utf-8') as f:
            f.write(f"\n-- Obfuscated by {interaction.user} • Nightobufuscator VM • {discord.utils.utcnow().strftime('%Y-%m-%d %H:%M')}")

        await asyncio.sleep(1)  # Giả hoàn tất
        await status_msg.edit(
            content="✅ **XONG 100%!** Nightobufuscator VM + Nightguard encrypted + Anti-Tamper. [■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■] 100%",
            attachments=[discord.File(out, filename=f"{file.filename}_Nightobf.luau")]
        )
    finally:
        for p in [inp, out] if 'out' in locals() else [inp]:
            if os.path.exists(p):
                try: os.unlink(p)
                except: pass

# ================== CHẠY SONG SONG (Bot + Keep Alive) ==================
if __name__ == "__main__":
    flask_thread = threading.Thread(target=run_flask, daemon=True)
    flask_thread.start()
    bot.run(os.getenv("DISCORD_TOKEN"))
