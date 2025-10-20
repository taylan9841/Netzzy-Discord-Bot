# cogs/log_system.py
import discord
from discord.ext import commands

# KRİTİK: KANAL ID'niz doğru ayarlanmış durumda.
LOG_CHANNEL_ID = 1429592594198823042 

class LogSystem(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.get_log_channel = lambda: self.bot.get_channel(LOG_CHANNEL_ID)

    # ----------------------------------------------------
    # 1. Mesaj Silinme Olayı (on_message_delete)
    # ----------------------------------------------------
    @commands.Cog.listener()
    async def on_message_delete(self, message):
        
        # Bot mesajlarını, DM'leri ve log kanalının kendisini yoksay
        if message.author.bot or not message.guild or message.channel.id == LOG_CHANNEL_ID:
            return

        log_channel = self.get_log_channel()
        if not log_channel:
            return

        # Mesaj içeriği kontrolü: Cache'te yoksa bile log göndermeyi garanti etme
        deleted_content = message.content if message.content else "*Mesaj içeriği önbellekten alınamadı (Çok eski veya izin eksikliği).*"
        
        embed = discord.Embed(
            title="🗑️ Mesaj Silindi",
            description=f"**Kanal:** {message.channel.mention}",
            color=discord.Color.red()
        )
        
        # SİLİNEN MESAJ İÇERİĞİ GÖSTERİMİ
        embed.add_field(name="İçerik", value=f"```\n{deleted_content[:1024]}\n```", inline=False)
            
        embed.set_author(
            name=f"Yazan: {message.author.display_name} ({message.author})",
            icon_url=message.author.display_avatar.url
        )

        embed.set_footer(text=f"Kullanıcı ID: {message.author.id} | Mesaj ID: {message.id}")
        embed.timestamp = discord.utils.utcnow()
        
        try:
            await log_channel.send(embed=embed)
        except discord.errors.Forbidden:
            print(f"HATA: Botun Log Kanalı ({LOG_CHANNEL_ID})'na mesaj gönderme izni yok.")
            pass


    # ----------------------------------------------------
    # 2. Mesaj Düzenlenme Olayı (on_message_edit)
    # ----------------------------------------------------
    @commands.Cog.listener()
    async def on_message_edit(self, before, after):
        # Bot mesajlarını, DM'leri ve içeriği değişmeyen mesajları yoksay
        if before.author.bot or not before.guild or before.channel.id == LOG_CHANNEL_ID:
            return
            
        if before.content == after.content:
            return

        log_channel = self.get_log_channel()
        if not log_channel:
            return
            
        embed = discord.Embed(
            title="✏️ Mesaj Düzenlendi",
            description=f"**Kanal:** {before.channel.mention}\n[Mesaja Git]({after.jump_url})",
            color=discord.Color.yellow()
        )

        embed.add_field(name="Önceki İçerik", value=f"```\n{before.content[:1024] or 'Yok (Boş veya çok uzun)'}\n```", inline=False)
        embed.add_field(name="Yeni İçerik", value=f"```\n{after.content[:1024] or 'Yok (Boş veya çok uzun)'}\n```", inline=False)
        
        embed.set_author(
            name=f"Düzenleyen: {before.author.display_name} ({before.author})",
            icon_url=before.author.display_avatar.url
        )
        
        embed.set_footer(text=f"Kullanıcı ID: {before.author.id} | Mesaj ID: {before.id}")
        embed.timestamp = discord.utils.utcnow()

        try:
            await log_channel.send(embed=embed)
        except discord.errors.Forbidden:
             print(f"HATA: Botun Log Kanalı ({LOG_CHANNEL_ID})'na mesaj gönderme izni yok.")
             pass


# KURULUM FONKSİYONU
async def setup(bot):
    # Düzeltme yapıldı: Artık gereksiz uyarı kodu yok.
    await bot.add_cog(LogSystem(bot))
