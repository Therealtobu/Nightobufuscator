import discord
from discord import app_commands
import asyncio
import os
import tempfile
import requests
from dotenv import load_dotenv
from flask import Flask
import threading

load_dotenv()

# ================== KEEP ALIVE ==================
app = Flask(__name__)
@app.route('/') 
def home(): return "✅ Nightobufuscator đang chạy 24/7"
def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# ================== BOT ==================
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

WRAPPER = "obf_vm.lua"

@bot.event
async def on_ready():
    await tree.sync()
    print(f"✅ Bot {bot.user} ONLINE - Nightobufuscator Art Mode sẵn sàng!")

@tree.command(name="obf", description="Obfuscate + vẽ ASCII Night Guard (siêu đặc biệt)")
async def obf(interaction: discord.Interaction, file: discord.Attachment):
    await interaction.response.defer()
    if file.size > 8 * 1024 * 1024:
        return await interaction.followup.send("❌ File >8MB!")

    code = (await file.read()).decode('utf-8', errors='ignore')
    status = await interaction.followup.send("📤 Đang upload lên 0x0.st...")

    try:
        # Bước 1: Upload lên 0x0.st
        r = requests.post("https://0x0.st", files={'file': ('script.luau', code)})
        raw_url = r.text.strip()
        loadstring_code = f'loadstring(game:HttpGet("{raw_url}"))()'

        await status.edit(content="🔑 Đang tạo loadstring + obfuscate cực mạnh...")

        # Bước 2: Obfuscate loadstring bằng Hercules
        with tempfile.NamedTemporaryFile(mode='w', suffix='.luau', delete=False, encoding='utf-8') as f:
            f.write(loadstring_code)
            inp = f.name

        proc = await asyncio.create_subprocess_exec("lua", WRAPPER, inp)
        await proc.communicate()

        out = inp.replace('.luau', '_obfuscated.lua')

        # Bước 3: Thêm ASCII Art "NIGHT GUARD" cực đẹp
        ascii_art = """--   _   _ _       _     _   
--  | \\ | (_) __ _| |__ | |_ 
--  |  \\| | |/ _` | '_ \\| __|
--  | |\\  | | (_| | | | | |_ 
--  |_| \\_|_|\\__, |_| |_|\\__|
--           |___/             
-- 
--   G  U  A  R  D
-- 
-- Nightobufuscator - Protected & Encrypted
-- https://0x0.st/raw_link
"""

        with open(out, 'r', encoding='utf-8') as f:
            obf_code = f.read()

        final_code = ascii_art + "\n" + obf_code

        with open(out, 'w', encoding='utf-8') as f:
            f.write(final_code)

        await status.edit(
            content="✅ **XONG!** File đã được vẽ thành ASCII Art \"NIGHT GUARD\" + obfuscate cực mạnh.",
            attachments=[discord.File(out, filename=f"{file.filename}_NightGuard_Art.luau")]
        )
    finally:
        for p in [inp, out] if 'out' in locals() else [inp]:
            if os.path.exists(p): os.unlink(p)

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.run(os.getenv("DISCORD_TOKEN"))
