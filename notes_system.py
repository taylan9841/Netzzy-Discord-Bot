import discord
from discord.ext import commands
import json
import os


class NotesSystem(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        # Notların saklandığı dosya yolu
        self.file_path = "notes.json"
        self.notes = self.load_notes()

    def load_notes(self):
        # notes.json dosyasını yükler, yoksa veya bozuksa boş bir sözlük döndürür
        if not os.path.exists(self.file_path):
            return {}
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError):
            print(
                "⚠️ HATA: notes.json dosyası bozuk veya boş. Boş sözlük oluşturuldu."
            )
            return {}

    def save_notes(self):
        # Notları dosyaya kaydeder
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.notes, f, indent=4)

    # ----------------------------------------------------------------------
    # KOMUTLAR
    # ----------------------------------------------------------------------

    @commands.command(name="notekle", aliases=["addnote"])
    async def not_ekle(self, ctx, key: str, *, value: str):
        """Yeni bir not ekler. Kullanım: !notekle anahtar_kelime Notun içerigi"""
        user_id = str(ctx.author.id)
        if user_id not in self.notes:
            self.notes[user_id] = {}

        self.notes[user_id][key.lower()] = value
        self.save_notes()
        await ctx.send(f"✅ **'{key}'** başlıklı notunuz başarıyla eklendi.")

    @commands.command(name="not_gor", aliases=["notgor", "oku"])
    async def not_gor(self, ctx, key: str):
        """Eklenmiş bir notu görüntüler. Kullanım: !not_gor anahtar_kelime"""
        user_id = str(ctx.author.id)
        key = key.lower()

        if user_id in self.notes and key in self.notes[user_id]:
            await ctx.send(
                f"📝 **{key.capitalize()}** notunuz:\n>>> {self.notes[user_id][key]}"
            )
        else:
            await ctx.send(
                f"❌ **'{key}'** başlığıyla kayıtlı bir notunuz bulunamadı.")

    @commands.command(name="notlarim", aliases=["mynotes"])
    async def notlarim(self, ctx):
        """Kaydettiğiniz tüm notların listesini gösterir."""
        user_id = str(ctx.author.id)

        if user_id not in self.notes or not self.notes[user_id]:
            return await ctx.send(
                "❌ Kayıtlı herhangi bir notunuz bulunmamaktadır.")

        notes_list = "\n".join(
            [f"- {key.capitalize()}" for key in self.notes[user_id].keys()])

        embed = discord.Embed(title=f"📝 {ctx.author.name} Notları",
                              description=notes_list,
                              color=discord.Color.blue())
        await ctx.send(embed=embed)

    @commands.command(name="notsil", aliases=["delnote"])
    async def not_sil(self, ctx, key: str):
        """Kaydettiğiniz bir notu siler. Kullanım: !notsil anahtar_kelime"""
        user_id = str(ctx.author.id)
        key = key.lower()

        if user_id in self.notes and key in self.notes[user_id]:
            del self.notes[user_id][key]
            self.save_notes()
            await ctx.send(
                f"🗑️ **'{key}'** başlıklı notunuz başarıyla silindi.")
        else:
            await ctx.send(
                f"❌ **'{key}'** başlığıyla kayıtlı bir notunuz bulunamadı.")


# Cog'un yüklenmesi için gerekli kurulum fonksiyonu
async def setup(bot):
    await bot.add_cog(NotesSystem(bot))
