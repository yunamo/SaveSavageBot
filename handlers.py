from aiogram import Router, types, F
from aiogram.types import (
    FSInputFile,
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

from downloader import download_tiktok, download_instagram
import moviepy.editor as mp
import time, json, os, secrets

router = Router()

user_lang = {}
user_timestamps = {}

stats = {
    "total_downloads": 0,
    "platforms": {"tiktok": 0, "instagram": 0},
    "user_downloads": {}
}

mp3_jobs: dict[str,str] = {}

with open("locales.json", encoding="utf-8") as f:
    LOCALES = json.load(f)


# ========================= LANG TEXT =========================
def L(uid, key, **kwargs):
    lang = user_lang.get(uid, "ru")
    txt = LOCALES.get(lang, LOCALES["ru"]).get(key, key)
    return txt.format(**kwargs) if kwargs else txt


# ========================= URL FIX =========================
def normalize_url(url: str) -> str:
    url = url.strip()
    url = url.replace("eeinstagram.com", "instagram.com")
    url = url.replace("ddinstagram.com", "instagram.com")
    return url


# ========================= KEYBOARD =========================
def main_keyboard(uid):
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=L(uid, "btn_stats")), KeyboardButton(text=L(uid, "btn_settings"))],
            [KeyboardButton(text=L(uid, "btn_about"))]
        ],
        resize_keyboard=True
    )


def mp3_button(url):
    token = secrets.token_urlsafe(8)
    mp3_jobs[token] = url
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text=L(None, "btn_mp3"), callback_data=f"mp3|{token}")]]
    )


# ========================= /start =========================
@router.message(F.text.startswith("/start"))
async def start(message: types.Message):
    uid = message.from_user.id
    user_lang[uid] = user_lang.get(uid, "ru")

    await message.answer(
        L(uid, "start", name=message.from_user.first_name),
        reply_markup=main_keyboard(uid)
    )


# ========================= STATS =========================
@router.message(F.text.in_({
    "📊 Статистика",   # ru, kg
    "📊 Statistics",   # en
    "📊 Statistika",   # uz
    "📊 الإحصائيات",   # ar
    "📊 统计数据",      # zh
    "📊 통계"          # ko
}))
async def stats_msg(message: types.Message):
    uid = message.from_user.id
    await message.answer(
        L(
            uid,
            "stats",
            total=stats["total_downloads"],
            user_total=stats["user_downloads"].get(uid, 0),
            tiktok=stats["platforms"]["tiktok"],
            instagram=stats["platforms"]["instagram"]
        ),
        reply_markup=main_keyboard(uid)
    )


# ========================= SETTINGS =========================
@router.message(F.text.in_({
    "⚙ Настройки",    # ru
    "⚙ Settings",     # en
    "⚙ Sozlamalar",   # uz
    "⚙ Орнотуулар",   # kg
    "⚙ الإعدادات",    # ar
    "⚙ 设置",         # zh
    "⚙ 설정"          # ko
}))
async def settings(message: types.Message):
    uid = message.from_user.id
    kb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=L(uid, "btn_change_lang"))],
            [KeyboardButton(text=L(uid, "btn_back"))]
        ],
        resize_keyboard=True
    )
    await message.answer(L(uid, "btn_settings"), reply_markup=kb)


# ========================= LANGUAGE CHOOSE =========================
@router.message(lambda m: m.text == L(m.from_user.id, "btn_change_lang"))
async def lang_choose(msg: types.Message):
    kb = ReplyKeyboardMarkup(
        keyboard=[[
            KeyboardButton(text="🇷🇺 Русский"),
            KeyboardButton(text="🇬🇧 English"),
            KeyboardButton(text="🇺🇿 O‘zbekcha")
        ], [
            KeyboardButton(text="🇰🇬 Кыргызча"),
            KeyboardButton(text="🇸🇦 العربية")
        ], [
            KeyboardButton(text="🇨🇳 中文"),
            KeyboardButton(text="🇰🇷 한국어")
        ]],
        resize_keyboard=True
    )
    await msg.answer(L(msg.from_user.id, "choose_language"), reply_markup=kb)


# ========================= LANGUAGE SETTERS =========================
@router.message(F.text == "🇷🇺 Русский")
async def set_ru(m: types.Message):
    user_lang[m.from_user.id] = "ru"
    await m.answer(L(m.from_user.id, "language_changed"), reply_markup=main_keyboard(m.from_user.id))


@router.message(F.text == "🇬🇧 English")
async def set_en(m: types.Message):
    user_lang[m.from_user.id] = "en"
    await m.answer(L(m.from_user.id, "language_changed"), reply_markup=main_keyboard(m.from_user.id))


@router.message(F.text == "🇺🇿 O‘zbekcha")
async def set_uz(m: types.Message):
    user_lang[m.from_user.id] = "uz"
    await m.answer(L(m.from_user.id, "language_changed"), reply_markup=main_keyboard(m.from_user.id))


@router.message(F.text == "🇰🇬 Кыргызча")
async def set_kg(m: types.Message):
    user_lang[m.from_user.id] = "kg"
    await m.answer(L(m.from_user.id, "language_changed"), reply_markup=main_keyboard(m.from_user.id))


@router.message(F.text == "🇸🇦 العربية")
async def set_ar(m: types.Message):
    user_lang[m.from_user.id] = "ar"
    await m.answer(L(m.from_user.id, "language_changed"), reply_markup=main_keyboard(m.from_user.id))


@router.message(F.text == "🇨🇳 中文")
async def set_zh(m: types.Message):
    user_lang[m.from_user.id] = "zh"
    await m.answer(L(m.from_user.id, "language_changed"), reply_markup=main_keyboard(m.from_user.id))


@router.message(F.text == "🇰🇷 한국어")
async def set_ko(m: types.Message):
    user_lang[m.from_user.id] = "ko"
    await m.answer(L(m.from_user.id, "language_changed"), reply_markup=main_keyboard(m.from_user.id))


# ========================= BACK =========================
@router.message(lambda m: m.text == L(m.from_user.id, "btn_back"))
async def back(message: types.Message):
    await message.answer(L(message.from_user.id, "btn_back"), reply_markup=main_keyboard(message.from_user.id))


# ========================= ABOUT =========================
@router.message(lambda m: m.text == L(m.from_user.id, "btn_about"))
async def about_msg(message: types.Message):
    await message.answer(L(message.from_user.id, "about"), reply_markup=main_keyboard(message.from_user.id))


# ========================= MP3 =========================
@router.callback_query(F.data.startswith("mp3|"))
async def convert_mp3(call: types.CallbackQuery):
    uid = call.from_user.id
    token = call.data.split("|")[1]
    url = mp3_jobs.get(token)

    if not url:
        return await call.answer(L(uid, "link_expired"), show_alert=True)

    url = normalize_url(url)

    if "tiktok" in url:
        file, title = download_tiktok(url)
    elif "instagram" in url:
        file, title = download_instagram(url)
    else:
        return await call.answer(L(uid, "unsupported"), show_alert=True)

    mp3 = "downloads/audio.mp3"
    video = mp.VideoFileClip(file)
    video.audio.write_audiofile(mp3)
    video.close()

    await call.message.answer_audio(FSInputFile(mp3), caption=L(uid, "mp3_caption"))
    os.remove(mp3)
    mp3_jobs.pop(token, None)


# ========================= DOWNLOADER =========================
@router.message(
    F.text.contains("tiktok.com") |
    F.text.contains("instagram.com") |
    F.text.contains("vm.tiktok.com") |
    F.text.contains("vt.tiktok.com")
)
async def downloader(message: types.Message):
    uid = message.from_user.id
    url = normalize_url(message.text.strip())

    if not url.startswith("http"):
        return await message.answer(L(uid, "unknown_link"))

    if uid in user_timestamps and time.time() - user_timestamps[uid] < 7:
        return await message.answer(L(uid, "cooldown"))

    user_timestamps[uid] = time.time()
    w = await message.answer(L(uid, "downloading"))

    try:
        if "tiktok" in url:
            file, title = download_tiktok(url)
            site = "tiktok"
        elif "instagram" in url:
            file, title = download_instagram(url)
            site = "instagram"
        else:
            return await message.answer(L(uid, "unsupported"))

        stats["total_downloads"] += 1
        stats["platforms"][site] += 1
        stats["user_downloads"][uid] = stats["user_downloads"].get(uid, 0) + 1

        await w.delete()
        size = round(os.path.getsize(file) / 1024 / 1024, 2)

        return await message.answer_video(
            FSInputFile(file),
            caption=L(uid, "result_caption", title=title, size=size),
            reply_markup=mp3_button(url)
        )

    except Exception as e:
        try:
            await w.delete()
        except:
            pass
        # Если нет error_generic в locales — просто покажет ключ.
        return await message.answer(L(uid, "error_generic").replace("{e}", str(e)))