# cogs/event_roles.py
import discord
from discord.ext import commands

ROLE_MAP = {
    "Roblox Etkinlik": "🔔",
    "Turnuva Duyuru": "🎮",
    "Çekiliş Duyuru": "💸"
}


# 1. Seçim Menüsü Sınıfı (Dropdown Mantığı)
class EventRoleSelect(discord.ui.Select):

    def __init__(self):
        options = []
        for label, emoji in ROLE_MAP.items():
            options.append(
                discord.SelectOption(
                    label=label,
                    value=label,
                    emoji=emoji,
                    description=f"{label} rolünü alıp/kaldırır."))

        super().__init__(
            custom_id="event_role_select_menu",  # Kalıcı View için KRİTİK
            placeholder="Bildirim Rollerinizi Seçin (Çoklu Seçim)...",
            min_values=0,
            max_values=len(options),
            options=options)

    async def callback(self, interaction: discord.Interaction):
        member = interaction.user
        guild = interaction.guild
        selected_role_names = self.values
        roles_added = []
        roles_removed = []

        for role_name in ROLE_MAP.keys():
            role = discord.utils.get(guild.roles, name=role_name)
            if not role: continue
            is_selected = role_name in selected_role_names
            has_role = role in member.roles

            if is_selected and not has_role:
                await member.add_roles(role)
                roles_added.append(role_name)
            elif not is_selected and has_role:
                await member.remove_roles(role)
                roles_removed.append(role_name)

        response_text = "Rolleriniz güncellendi:\n"
        if roles_added:
            response_text += f"➕ Eklendi: {', '.join(roles_added)}\n"
        if roles_removed:
            response_text += f"➖ Kaldırıldı: {', '.join(roles_removed)}"
        if not roles_added and not roles_removed:
            response_text = "Rollerinizde bir değişiklik yapılmadı."

        await interaction.response.send_message(response_text, ephemeral=True)


# 2. Mesajın Görüntüleme Sınıfı (View)
class EventRoleView(discord.ui.View):

    def __init__(self):
        super().__init__(timeout=None)  # Kalıcı View için KRİTİK
        self.add_item(EventRoleSelect())


# 3. Cog Ana Sınıfı
class EventRoles(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        bot.add_view(EventRoleView())

    @commands.command(name='etkinlikmenusu',
                      help='Etkinlik Rolü Seçim Menüsünü gönderir.')
    @commands.has_permissions(administrator=True)
    async def send_event_menu(self, ctx):
        embed = discord.Embed(
            title="🔔 ETKİNLİK BİLDİRİM ROLÜ SEÇİMİ",
            description=
            "Aşağıdaki menüyü kullanarak almak istediğiniz bildirim rollerini seçebilirsiniz.",
            color=discord.Color.blue())
        embed.set_footer(
            text=
            "Roblox Türkiye Botu | Değiştirmek için menüyü tekrar kullanın.")
        view = EventRoleView()
        await ctx.send(embed=embed, view=view)


# KURULUM FONKSİYONU
async def setup(bot):
    await bot.add_cog(EventRoles(bot))
