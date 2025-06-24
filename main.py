import discord
from discord import app_commands
from discord.ext import commands
import os
from dotenv import load_dotenv
from db import session
from models import User, VoiceLog
from datetime import datetime, timedelta, timezone
from sqlalchemy import func

# 環境変数のロード
load_dotenv()
TOKEN = os.getenv("TOKEN")
TEXT_CHANNEL_ID = int(os.getenv("TEXT_CHANNEL_ID"))
VOICE_CHANNEL_ID = int(os.getenv("VOICE_CHANNEL_ID"))

JST = timezone(timedelta(hours=+9), "Asia/Tokyo")

active_logs = {}

bot = commands.Bot(command_prefix="/", intents=discord.Intents.all())
tree = bot.tree


@bot.event
async def on_ready():
    await tree.sync()
    print("Are you ready?")


@bot.event
async def on_voice_state_update(member, before, after):
    if member.bot:
        return

    user = session.query(User).filter_by(discord_id=str(member.id)).first()
    if not user:
        user = User(discord_id=str(member.id))
        session.add(user)
        session.commit()

    # 入室処理
    if before.channel is None and after.channel is not None:
        if after.channel.id == VOICE_CHANNEL_ID:
            log = VoiceLog(user_id=user.id, join_time=datetime.now(JST))
            session.add(log)
            session.commit()
            active_logs[member.id] = log
            print(f"{member.display_name} が入室しました。")

    # 退室処理
    elif before.channel is not None and after.channel is None:
        if before.channel.id == VOICE_CHANNEL_ID and member.id in active_logs:
            log = active_logs.pop(member.id)
            log.leave_time = datetime.now(JST)
            log.join_time = log.join_time.replace(tzinfo=JST)
            log.duration = int((log.leave_time - log.join_time).total_seconds())
            session.commit()
            print(f"{member.display_name} が退室しました。 滞在時間: {log.duration} 秒")


@tree.command(name="ranking", description="ランキングを表示します")
@app_commands.describe(arg="日数（例: 7）")
async def ranking(ctx, arg: int = 7):
    if ctx.channel.id != TEXT_CHANNEL_ID:
        return
    if ctx.channel.id != TEXT_CHANNEL_ID:
        return

    # argが指定なければ7日間
    try:
        days = int(arg) if arg is not None else 7
    except ValueError:
        await ctx.send("引数には日数の数字を指定してください。例: `/ranking 7`")
        return

    end = datetime.now(JST)
    start = end - timedelta(days=days)

    # DBからユーザーごとの滞在時間合計を取得
    results = (
        session.query(
            User.discord_id,
            func.coalesce(func.sum(VoiceLog.duration), 0),
        )
        .join(VoiceLog)
        .filter(VoiceLog.join_time >= start, VoiceLog.join_time <= end)
        .group_by(User.id)
        .order_by(func.sum(VoiceLog.duration).desc())
        .all()
    )

    if not results:
        await ctx.send(f"過去{days}日間のデータがありません。")
        return

    lines = [f"過去{days}日間のランキング:"]
    for i, (discord_id, total_seconds) in enumerate(results, start=1):
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        time_str = f"{hours}時間{minutes}分{seconds}秒"
        lines.append(f"{i}. <@{discord_id}> — {time_str}")

    await ctx.send("\n".join(lines))


bot.run(TOKEN)
