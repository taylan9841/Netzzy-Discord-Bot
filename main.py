# main.py dosyasının TAM İÇERİĞİ
import discord
from discord.ext import commands
import os
from flask import Flask
from threading import Thread

# -------------------------------------------------------------------------
# 7/24 UPTIME İÇİN GEREKLİ KISIM (Flask Sunucusu)
# -------------------------------------------------------------------------
app = Flask('')


@app.route('/')
def home():
    # Botun aktif olduğunu gösteren basit bir mesaj
    return "Botunuz Replit üzerinde çalışıyor ve Uptime Robot tarafından kontrol ediliyor."


def run_flask_app():
    # Flask uygulamasını 0.0.0.0 IP'sinde 8080 portunda çalıştır
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    # Flask uygulamasını ayrı bir thread'de (iş parçacığı) başlat
    t = Thread(target=run_flask_app)
    t.start()


# -------------------------------------------------------------------------

# Bot ayarları
# Log sisteminin çalışması için discord.Intents.all() önemlidir!
intents = discord.Intents.all()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)


@bot.event
async def on_ready():
    print(f'🤖 Bot Giriş Yaptı: {bot.user.name}')
    await bot.change_presence(activity=discord.Game(
        name="Sunucu Etkileşimini Takip Ediyor"))

    # Cog Yükleme
    # Log sistemini de buraya ekledik.
    cogs_to_load = [
        "cogs.leaderboard_system",
        "cogs.roblox_verify",
        "cogs.event_roles",
        "cogs.notes_system",  # NOT SİSTEMİ
        "cogs.log_system"  # LOG SİSTEMİ
    ]

    for cog in cogs_to_load:
        try:
            await bot.load_extension(cog)
            print(f"✅ {cog} Başarıyla Yüklendi.")
        except Exception as e:
            # Hata oluştuğunda sadece bir cog'un yüklenmemesi diğerlerini durdurmaz
            print(f"❌ Cog Yüklenirken Hata Oluştu: {cog} -> {e}")


# Botu Çalıştırma
if __name__ == "__main__":
    # 7/24 aktif kalma fonksiyonunu çağır
    keep_alive()

    # BOT TOKEN'INI GÜVENLİ YERDEN (Secrets/Ortam Değişkenleri) ÇEKİYORUZ
    TOKEN = os.environ.get('DISCORD_TOKEN')

    if TOKEN:
        bot.run(TOKEN)
    else:
        print(
            "\n\n⚠️ HATA: DISCORD_TOKEN ortam değişkeni bulunamadı. Lütfen Kilit Simgesini (Secrets) kontrol edin."
        )
        print("Bot başlatılamadı.")
