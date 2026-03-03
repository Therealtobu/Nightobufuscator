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

async def update_progress(embed_msg: discord.Message, steps: list, proc: asyncio.subprocess.Process):
    # Hiệu ứng thật: update bar dần dần theo thời gian, kết hợp với bước
    current_step = 0
    progress = 0
    total_steps = len(steps)
    bar_length = 20  # Độ dài bar

    embed = discord.Embed(title="🔄 Nightobufuscator VM MAX đang chạy...", color=discord.Color.blue())
    embed.add_field(name="Tiến độ", value=f"[{'■' * 0}{' ' * bar_length}] 0%", inline=False)
    embed.add_field(name="Bước hiện tại", value=steps[0], inline=False)
    await embed_msg.edit(embed=embed)

    while proc.returncode is None:  # Trong khi subprocess đang chạy
        await asyncio.sleep(0.5)  # Update mỗi 0.5s để hiệu ứng mượt
        progress += 5  # Tăng 5% mỗi lần (giả lập thời gian thực)
        if progress > 100:
            progress = 100
        filled = int(bar_length * progress / 100)
        bar = f"[{'■' * filled}{' ' * (bar_length - filled)}] {progress}%"

        # Update bước khi đạt mốc %
        if progress >= (current_step + 1) * (100 / total_steps):
            current_step = min(current_step + 1, total_steps - 1)

        embed.set_field_at(0, name="Tiến độ", value=bar, inline=False)
        embed.set_field_at(1, name="Bước hiện tại", value=steps[current_step], inline=False)
        await embed_msg.edit(embed=embed)

        if progress >= 100:
            break

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
        with tempfile.NamedTemporaryFile(mode='w', suffix='.luau', delete=False, encoding='utf-8') as f:
            f.write(code)
            inp = f.name

        # Các bước cho progress
        steps = [
            "📥 Bước 1: Tải và lưu script gốc...",
            "🔑 Bước 2: Chèn Nightguard encrypted watermark...",
            "🚀 Bước 3: Chạy Hercules VM + Anti-Tamper + Compressor...",
            "🧹 Bước 4: Xóa watermark cũ + thêm Nightobufuscator header...",
            "📤 Bước 5: Chuẩn bị gửi file obfuscated..."
        ]

        # Chạy subprocess
        proc = await asyncio.create_subprocess_exec("lua", WRAPPER, inp,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE)

        # Task update progress hiệu ứng thật
        progress_task = asyncio.create_task(update_progress(status_msg, steps, proc))

        # Chờ subprocess xong
        await proc.communicate()

        progress_task.cancel()  # Dừng task khi xong

        out = inp.replace('.luau', '_obfuscated.lua')
        if not os.path.exists(out):
            return await status_msg.edit(content="❌ Lỗi obfuscate, thử lại!")

        with open(out, 'a', encoding='utf-8') as f:
            f.write(f"\n-- Obfuscated by {interaction.user} • Nightobufuscator VM • {discord.utils.utcnow().strftime('%Y-%m-%d %H:%M')}")

        # Embed hoàn tất
        final_embed = discord.Embed(title="✅ Obfuscate hoàn tất!", color=discord.Color.green())
        final_embed.add_field(name="Tiến độ", value="[■■■■■■■■■■■■■■■■■■■■] 100%", inline=False)
        final_embed.add_field(name="Kết quả", value="Nightobufuscator VM + Nightguard encrypted + Anti-Tamper.", inline=False)

        await status_msg.edit(embed=final_embed, attachments=[discord.File(out, filename=f"{file.filename}_Nightobf.luau")])

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
