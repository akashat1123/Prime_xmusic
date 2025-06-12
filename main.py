# main.py — Prime_xmusic Telegram Bot

import os
from pyrogram import Client, filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton
from pytgcalls import PyTgCalls
from pytgcalls.types import AudioPiped, VideoPiped
from yt_dlp import YoutubeDL
from gtts import gTTS
import asyncio

API_ID = int(os.getenv("25650954"))
API_HASH = os.getenv("f414b0b803bb6c22615e004e74cb00f6")
SESSION = os.getenv("")

app = Client(session_name=SESSION, api_id=API_ID, api_hash=API_HASH)
vc = PyTgCalls(app)

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def ytdl(query):
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': f'{DOWNLOAD_DIR}/%(title)s.%(ext)s',
        'noplaylist': True
    }
    with YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(query, download=True)
        return ydl.prepare_filename(info)

@app.on_message(filters.command("start"))
async def start(_, m: Message):
    await m.reply(
        "👋 Welcome to Prime_xmusic!\nUse /play, /vplay, /tts, /download.",
        reply_markup=InlineKeyboardMarkup([
            [InlineKeyboardButton("Support", url="https://t.me/your_support")]
        ])
    )

@app.on_message(filters.command("play"))
async def play(_, m: Message):
    if len(m.command) < 2:
        return await m.reply("Please provide a song name or URL.")
    query = " ".join(m.command[1:])
    file = ytdl(query)
    await vc.join_group_call(m.chat.id, AudioPiped(file))
    await m.reply(f"🎶 Now playing: {query}", reply_markup=InlineKeyboardMarkup([
        [
            InlineKeyboardButton("⏸ Pause", callback_data="pause"),
            InlineKeyboardButton("⏩ +30s", callback_data="skip"),
            InlineKeyboardButton("⏹ Stop", callback_data="stop")
        ]
    ]))

@app.on_message(filters.command("vplay"))
async def vplay(_, m: Message):
    if len(m.command) < 2:
        return await m.reply("Please provide a video URL.")
    url = m.command[1]
    file = ytdl(url)
    await vc.join_group_call(m.chat.id, VideoPiped(file))
    await m.reply("🎥 Now playing video.")

@app.on_message(filters.command("download"))
async def download(_, m: Message):
    if len(m.command) < 2:
        return await m.reply("Please provide a song name.")
    query = " ".join(m.command[1:])
    file = ytdl(query)
    await m.reply_audio(file)

@app.on_message(filters.command("tts"))
async def tts(_, m: Message):
    if len(m.command) < 2:
        return await m.reply("Provide text to convert.")
    text = " ".join(m.command[1:])
    speech = gTTS(text)
    path = "tts.mp3"
    speech.save(path)
    await m.reply_audio(path)

@app.on_message(filters.command("stop"))
async def stop(_, m: Message):
    await vc.leave_group_call(m.chat.id)
    await m.reply("⏹ Stopped streaming.")

@app.on_callback_query()
async def button(_, cq):
    data = cq.data
    if data == "pause":
        await vc.pause_stream(cq.message.chat.id)
        await cq.answer("Paused")
    elif data == "skip":
        await vc.seek_stream(cq.message.chat.id, 30)
        await cq.answer("Skipped 30s")
    elif data == "stop":
        await vc.leave_group_call(cq.message.chat.id)
        await cq.answer("Stopped")

vc.start()
app.run()
