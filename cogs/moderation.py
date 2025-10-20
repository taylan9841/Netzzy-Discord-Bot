# cogs/moderation.py
import discord
from discord.ext import commands

class Moderation(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.banned_words = ["küfür1", "küfür2", "reklam_linki", "websiteadı.com"]
        self.MUTE_ROLE_NAME = "Muted"

    # Otomatik Moderasyon: Mesaj Dinleme
    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or message.content.startswith('!'):
            return

        content = message.content.lower()
        
        # 1. Küfür/Reklam Kontrolü
        for word in self.banned_words:
            if word in content:
                await message.delete()
                await message.channel.send(
                    f'{message.author.mention}, sunucu kurallarına aykırı içerik kullandınız.',
                    delete_after=5
                )
                return 

        # 2. Büyük Harf (Caps Lock) Kontrolü
        if len(message.content) > 10:
            upper_count = sum(1 for char in message.content if char.isupper())
            if (upper_count / len(message.content)) > 0.7:
                await message.delete()
                await message.channel.send(
                    f'{message.author.mention}, lütfen CAPSLOCK kullanmayınız.',
                    delete_after=5
                )
                return

    # Yönetici Komutu: Mute (Susturma)
    @commands.command(name='mute', help='Kullanıcıyı süresiz susturur.')
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: discord.Member, *, reason='Belirtilmedi'):
        if member.id == ctx.author.id:
            return await ctx.send("Kendinizi susturamazsınız.")
        mute_role = discord.utils.get(ctx.guild.roles, name=self.MUTE_ROLE_NAME)
        if not mute_role:
            await ctx.send(f"HATA: '{self.MUTE_ROLE_NAME}' rolü bulunamadı.")
            return
        await member.add_roles(mute_role, reason=f'Susturan: {ctx.author.name} | Sebep: {reason}')
        await ctx.send(f'✅ {member.mention} susturuldu. Sebep: **{reason}**')

    # Yönetici Komutu: Kick (Atma)
    @commands.command(name='kick', help='Kullanıcıyı sunucudan atar.')
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: discord.Member, *, reason='Belirtilmedi'):
        await member.kick(reason=f'Atan: {ctx.author.name} | Sebep: {reason}')
        await ctx.send(f'✅ {member.mention} sunucudan atıldı. Sebep: **{reason}**')

# KURULUM FONKSİYONU
async def setup(bot):
    await bot.add_cog(Moderation(bot))
