# cogs/leaderboard_system.py DOSYASININ TAM VE GÜNCEL İÇERİĞİ
import discord
from discord.ext import commands, tasks
import json
import os
from datetime import datetime, timedelta

STATS_FILE = 'server_stats.json'

# --- KRİTİK YAPILANDIRMA AYARLARI ---
# 1. DUYURUNUN GİDECEĞİ KANAL ID'si
ANNOUNCEMENT_CHANNEL_ID = 1422192916767445072  # <--- KONTROL EDİN
# 2. Sesli sohbette takibin yapılacağı kanal ID'leri
TRACKED_VOICE_CHANNEL_IDS = [
    1422193067141627904, 1422193070941802496, 1422193074943299674,
    1422193079800041667, 1422193085193912320
]  # <--- KONTROL EDİN
# 3. YENİ AYAR: Duyuruyu Etiketleyecek Rolün ID'si (Örn: Etkinlik Duyuru Rolü)
ANNOUNCEMENT_ROLE_ID = 1429580018001903656  # <--- LÜTFEN KENDİ ETKİNLİK ROL ID'nizle DEĞİŞTİRİN
# ------------------------------------

XP_PER_MESSAGE = 1
VOICE_XP_PER_MINUTE = 5


class LeaderboardSystem(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.stats_db = self.load_db()
        self.voice_timers = {}
        self.weekly_reset_day = 6  # Pazar
        self.weekly_reset_time = 20  # 20:00 (Saat)
        self.check_weekly_reset.start()

    def cog_unload(self):
        self.check_weekly_reset.cancel()

    # --- Veritabanı Yükleme/Kaydetme Fonksiyonları ---

    def load_db(self):
        if os.path.exists(STATS_FILE):
            try:
                with open(STATS_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    if 'last_reset_date' not in data:
                        data['last_reset_date'] = datetime.min.isoformat()
                    return data
            except (json.JSONDecodeError, IOError):
                return {
                    'users': {},
                    'last_reset_date': datetime.min.isoformat()
                }
        return {'users': {}, 'last_reset_date': datetime.min.isoformat()}

    def save_db(self):
        with open(STATS_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.stats_db, f, indent=4, ensure_ascii=False)

    # --- Olay Dinleyicileri (Veri Toplama) ---

    @commands.Cog.listener()
    async def on_message(self, message):
        if message.author.bot or not message.guild:
            return

        user_id = str(message.author.id)
        if user_id not in self.stats_db['users']:
            self.stats_db['users'][user_id] = {
                'messages': 0,
                'voice_time': 0,
                'xp': 0
            }

        self.stats_db['users'][user_id]['messages'] += 1
        self.stats_db['users'][user_id]['xp'] += XP_PER_MESSAGE
        self.save_db()

    @commands.Cog.listener()
    async def on_voice_state_update(self, member, before, after):
        if member.bot:
            return

        user_id = str(member.id)
        now = datetime.now()

        if after.channel and after.channel.id in TRACKED_VOICE_CHANNEL_IDS and not before.channel:
            self.voice_timers[user_id] = now

        elif before.channel and before.channel.id in TRACKED_VOICE_CHANNEL_IDS and not after.channel:
            if user_id in self.voice_timers:
                duration = (now - self.voice_timers[user_id]).total_seconds()

                if duration >= 60:
                    if user_id not in self.stats_db['users']:
                        self.stats_db['users'][user_id] = {
                            'messages': 0,
                            'voice_time': 0,
                            'xp': 0
                        }

                    self.stats_db['users'][user_id]['voice_time'] += int(
                        duration)
                    self.stats_db['users'][user_id]['xp'] += int(
                        duration / 60) * VOICE_XP_PER_MINUTE
                    self.save_db()

                del self.voice_timers[user_id]

    # --- 14 Günlük (İki Haftalık) Sıfırlama Döngüsü ---

    @tasks.loop(minutes=1)
    async def check_weekly_reset(self):
        now = datetime.now()

        if now.weekday(
        ) == self.weekly_reset_day and now.hour == self.weekly_reset_time and now.minute == 0:

            last_reset = datetime.fromisoformat(
                self.stats_db.get('last_reset_date', datetime.min.isoformat()))

            if (now - last_reset) >= timedelta(days=14):
                await self.post_leaderboard_and_reset()

    @check_weekly_reset.before_loop
    async def before_check_weekly_reset(self):
        await self.bot.wait_until_ready()

    # --- MANUEL DUYURU KOMUTU (Hata aldığınız komut) ---

    @commands.command(
        name='liderduyur',
        help='Liderlik duyurusunu hemen yapar ve istatistikleri sıfırlar.')
    @commands.has_permissions(administrator=True)
    async def manual_leaderboard_announce(self, ctx):
        await ctx.send(
            "⌛ Liderlik tablosu duyurusu oluşturuluyor ve istatistikler sıfırlanıyor..."
        )
        try:
            await self.post_leaderboard_and_reset()
            await ctx.send(
                "✅ Duyuru başarıyla **Duyuru Kanalına** gönderildi ve istatistikler sıfırlandı."
            )
        except Exception as e:
            # Hata oluştuğunda nerede hata olduğunu daha net görelim
            await ctx.send(f"❌ Duyuru sırasında bir hata oluştu: {e}")

    # --- Liderlik Tablosu Komutu ---
    # ... (kod aynı kalıyor)

    @commands.command(
        name='top5',
        help='En çok mesaj/sesli sohbette kalan ilk 5 üyeyi gösterir.')
    async def top_leaders(self, ctx, type: str = 'xp'):
        type = type.lower()
        valid_types = ['xp', 'messages', 'voice_time']

        if type not in valid_types:
            return await ctx.send(
                f"❌ Geçersiz tür. Kullanım: `!top5 xp`, `!top5 messages` veya `!top5 voice_time`"
            )

        sorted_leaders = sorted(self.stats_db['users'].items(),
                                key=lambda item: item[1].get(type, 0),
                                reverse=True)

        embed = discord.Embed(
            title=f"🥇 Sunucu Liderlik Sıralaması",
            description=f"Sıralama Metriği: **{type.upper()}**",
            color=discord.Color.dark_teal())

        description_lines = []
        for index, (user_id, stats) in enumerate(sorted_leaders[:10]):
            member = ctx.guild.get_member(int(user_id))
            if member:
                value = stats.get(type, 0)

                if type == 'voice_time':
                    minutes = int(value / 60)
                    hours = int(minutes / 60)
                    minutes %= 60
                    value_str = f"**{hours}**s **{minutes}**dk"
                else:
                    value_str = f"**{value}** {type.upper()}"

                description_lines.append(
                    f"**{index + 1}.** {member.mention} - {value_str}")

        if not description_lines:
            embed.add_field(
                name="Veri Yok",
                value="Liderlik tablosu henüz boş. Aktivite bekliyor!")
        else:
            embed.description = "\n".join(description_lines)

        await ctx.send(embed=embed)

    # --- İKİ HAFTALIK DUYURU VE SIFIRLAMA FONKSİYONU (GÜNCELLENDİ) ---

    async def post_leaderboard_and_reset(self):
        announcement_channel = self.bot.get_channel(ANNOUNCEMENT_CHANNEL_ID)
        if not announcement_channel:
            raise Exception(
                "Duyuru kanalı ID'si yanlış veya kanala erişim yok.")

        # Etiketlenecek rolü al
        mention_role = announcement_channel.guild.get_role(
            ANNOUNCEMENT_ROLE_ID)

        # Etiketlenecek rol yoksa veya ID 0 ise, etiketleme yapma
        mention_message = ""
        if mention_role:
            # Rolü mention olarak hazırla
            mention_message = mention_role.mention

        sorted_leaders = sorted(self.stats_db['users'].items(),
                                key=lambda item: item[1].get('xp', 0),
                                reverse=True)[:5]

        leader_mentions = []
        trophy_emojis = ["👑", "🥈", "🥉", "4️⃣", "5️⃣"]

        for index, (user_id, stats) in enumerate(sorted_leaders):
            member = announcement_channel.guild.get_member(int(user_id))
            if member:
                leader_mentions.append(
                    f"{trophy_emojis[index]} {member.mention} | **{stats['xp']} XP** "
                    f"({stats['messages']} mesaj, {int(stats['voice_time'] / 60)} dakika VC)"
                )

        embed = discord.Embed(
            title="✨ İKİ HAFTALIK ETKİLEŞİM ŞAMPİYONLARI! ✨",
            description=
            "Roblox Türkiye topluluğunun son iki haftadaki en aktif üyeleri belirlendi! İşte zirvedeki isimler:",
            color=discord.Color.purple(),
            timestamp=datetime.now())

        if leader_mentions:
            embed.add_field(name="🏆 HAFTANIN EN AKTİFLERİ",
                            value="\n".join(leader_mentions),
                            inline=False)
        else:
            embed.add_field(name="😕 Veri Yok",
                            value="Bu dönemde yeterli aktivite kaydedilemedi.")

        embed.set_footer(
            text=
            "Tüm istatistikler sıfırlandı. Yeni dönem başladı! İlk 10'a girmek için hemen aktif ol!"
        )

        # Etiketleme mesajı (mention_message) embed'in hemen üstüne gönderilir
        await announcement_channel.send(content=mention_message, embed=embed)

        self.stats_db['users'] = {}
        self.stats_db['last_reset_date'] = datetime.now().isoformat()
        self.save_db()


# KURULUM FONKSİYONU
async def setup(bot):
    await bot.add_cog(LeaderboardSystem(bot))
