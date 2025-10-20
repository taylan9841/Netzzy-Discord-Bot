# cogs/roblox_verify.py
import discord
from discord.ext import commands
import json


class RobloxVerify(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        # BU HATA NORMALDİR. İLK ÇALIŞTIRMADA users.json dosyası henüz yoktur.
        print(
            "HATA: users.json dosyası bozuk veya boş. Boş sözlük oluşturuldu.")
        # self.verified_users = self.load_db() # users.json yüklemesi

    @commands.command(name='verify',
                      help='Roblox hesabınızı Discord ile doğrular.')
    async def verify(self, ctx, roblox_username: str):
        await ctx.send(
            f"Doğrulama sistemi henüz tamamlanmadı, ancak username: {roblox_username} alındı."
        )

    # @commands.command(name='check') # Kontrol komutu


# KURULUM FONKSİYONU
async def setup(bot):
    await bot.add_cog(RobloxVerify(bot))
