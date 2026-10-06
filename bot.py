import discord
from discord.ext import commands
import random
import json
import os

# =========================
# الإعدادات
# =========================

TOKEN = "ضع_توكن_البوت_هنا"
PREFIX = "!"

intents = discord.Intents.default()
intents.message_content = True
intents.members = True

bot = commands.Bot(
    command_prefix=PREFIX,
    intents=intents,
    help_command=None
)

# =========================
# ملف XP
# =========================

FILE = "xp.json"

if os.path.exists(FILE):
    with open(FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
else:
    data = {}


def save_data():
    with open(FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def get_user(user_id):
    user_id = str(user_id)

    if user_id not in data:
        data[user_id] = {
            "xp": 0,
            "level": 1,
            "wins": 0
        }

    return data[user_id]


def add_xp(user_id, amount):
    user = get_user(user_id)

    user["xp"] += amount

    # كل مستوى يحتاج 100 XP إضافية
    needed = user["level"] * 100

    if user["xp"] >= needed:
        user["xp"] -= needed
        user["level"] += 1
        save_data()
        return True

    save_data()
    return False


# =========================
# تشغيل البوت
# =========================

@bot.event
async def on_ready():
    print("================================")
    print(f"✅ البوت يعمل: {bot.user}")
    print("🎮 Bot Games جاهز!")
    print("================================")


# =========================
# XP عند إرسال رسالة
# =========================

@bot.event
async def on_message(message):

    if message.author.bot:
        return

    leveled_up = add_xp(
        message.author.id,
        random.randint(5, 15)
    )

    if leveled_up:
        user = get_user(message.author.id)

        await message.channel.send(
            f"🎉 مبروك {message.author.mention}!\n"
            f"⬆️ وصلت إلى المستوى **{user['level']}**!"
        )

    await bot.process_commands(message)


# =========================
# 🎲 لعبة النرد
# =========================

@bot.command()
async def نرد(ctx):

    number = random.randint(1, 6)

    add_xp(ctx.author.id, 10)

    await ctx.send(
        f"🎲 {ctx.author.mention} رميت النرد!\n"
        f"النتيجة: **{number}**\n"
        f"⭐ حصلت على 10 XP!"
    )


# =========================
# 🪙 لعبة العملة
# =========================

@bot.command()
async def عملة(ctx):

    result = random.choice([
        "🪙 وجه",
        "🪙 كتابة"
    ])

    add_xp(ctx.author.id, 10)

    await ctx.send(
        f"{ctx.author.mention}\n"
        f"النتيجة: **{result}**\n"
        f"⭐ +10 XP"
    )


# =========================
# 🎯 تخمين الرقم
# =========================

@bot.command()
async def تخمين(ctx):

    number = random.randint(1, 10)

    await ctx.send(
        f"🎯 {ctx.author.mention}\n"
        f"خمن رقمًا من **1 إلى 10**!"
    )

    def check(message):
        return (
            message.author == ctx.author
            and message.channel == ctx.channel
        )

    try:
        message = await bot.wait_for(
            "message",
            timeout=15,
            check=check
        )

        guess = int(message.content)

        if guess == number:

            user = get_user(ctx.author.id)
            user["wins"] += 1

            add_xp(ctx.author.id, 50)

            await ctx.send(
                f"🎉 صحيح!\n"
                f"الرقم كان **{number}**\n"
                f"🏆 فزت!\n"
                f"⭐ +50 XP"
            )

        else:
            await ctx.send(
                f"❌ خطأ!\n"
                f"الرقم الصحيح كان **{number}**."
            )

        save_data()

    except ValueError:
        await ctx.send("❌ اكتب رقمًا فقط.")

    except TimeoutError:
        await ctx.send("⏰ انتهى الوقت!")


# =========================
# ✊ حجر ورق مقص
# =========================

@bot.command()
async def حجر(ctx):

    choices = [
        "🪨 حجر",
        "📄 ورق",
        "✂️ مقص"
    ]

    bot_choice = random.choice(choices)

    await ctx.send(
        f"🎮 {ctx.author.mention}\n"
        f"اكتب بعد هذه الرسالة:\n"
        f"`حجر` أو `ورق` أو `مقص`"
    )

    def check(message):
        return (
            message.author == ctx.author
            and message.channel == ctx.channel
            and message.content in ["حجر", "ورق", "مقص"]
        )

    try:
        message = await bot.wait_for(
            "message",
            timeout=15,
            check=check
        )

        player = message.content

        translate = {
            "حجر": "🪨 حجر",
            "ورق": "📄 ورق",
            "مقص": "✂️ مقص"
        }

        player_choice = translate[player]

        if player_choice == bot_choice:
            result = "🤝 تعادل!"

        elif (
            (player_choice == "🪨 حجر" and bot_choice == "✂️ مقص")
            or
            (player_choice == "📄 ورق" and bot_choice == "🪨 حجر")
            or
            (player_choice == "✂️ مقص" and bot_choice == "📄 ورق")
        ):
            result = "🎉 فزت! +30 XP"

            user = get_user(ctx.author.id)
            user["wins"] += 1
            add_xp(ctx.author.id, 30)

        else:
            result = "😢 خسرت!"

        await ctx.send(
            f"أنت: **{player_choice}**\n"
            f"البوت: **{bot_choice}**\n\n"
            f"{result}"
        )

        save_data()

    except TimeoutError:
        await ctx.send("⏰ انتهى الوقت!")


# =========================
# 👤 ملف اللاعب
# =========================

@bot.command()
async def مستواي(ctx):

    user = get_user(ctx.author.id)

    await ctx.send(
        f"👤 **إحصائيات {ctx.author.name}**\n\n"
        f"⭐ المستوى: **{user['level']}**\n"
        f"✨ XP: **{user['xp']}**\n"
        f"🏆 الانتصارات: **{user['wins']}**"
    )


# =========================
# 🏆 Leaderboard
# =========================

@bot.command()
async def ترتيب(ctx):

    if not data:
        await ctx.send("📊 لا يوجد لاعبون حتى الآن.")
        return

    ranking = sorted(
        data.items(),
        key=lambda x: (
            x[1]["level"],
            x[1]["xp"],
            x[1]["wins"]
        ),
        reverse=True
    )

    text = "🏆 **أفضل اللاعبين**\n\n"

    medals = ["🥇", "🥈", "🥉"]

    for i, (user_id, user) in enumerate(ranking[:10]):

        member = ctx.guild.get_member(int(user_id))

        if member:
            name = member.display_name
        else:
            name = f"لاعب {user_id}"

        medal = medals[i] if i < 3 else f"**{i + 1}.**"

        text += (
            f"{medal} **{name}**\n"
            f"   ⭐ Level {user['level']} | "
            f"XP {user['xp']} | "
            f"🏆 {user['wins']} فوز\n\n"
        )

    await ctx.send(text)


# =========================
# 🆘 المساعدة
# =========================

@bot.command()
async def مساعدة(ctx):

    embed = discord.Embed(
        title="🎮 بوت الألعاب",
        description="أوامر الألعاب ونظام XP",
        color=discord.Color.blue()
    )

    embed.add_field(
        name="🎮 الألعاب",
        value=(
            "`!نرد` 🎲\n"
            "`!عملة` 🪙\n"
            "`!تخمين` 🎯\n"
            "`!حجر` ✊"
        ),
        inline=False
    )

    embed.add_field(
        name="⭐ نظام XP",
        value=(
            "`!مستواي` — معلوماتك\n"
            "`!ترتيب` — أفضل اللاعبين"
        ),
        inline=False
    )

    await ctx.send(embed=embed)


# =========================
# تشغيل
# =========================

bot.run(TOKEN)
