from aiogram.types import Message, InputMediaPhoto
from aiogram import F

from bot import bot, router
from services.database import albums


@router.message(F.photo & F.media_group_id)
async def album_handler(message: Message):
    media_group_id = message.media_group_id
    if media_group_id not in albums:
        albums[media_group_id] = []
    file_id = message.photo[-1].file_id
    albums[media_group_id].append(InputMediaPhoto(media=file_id))
    if len(albums[media_group_id]) == 3:
        await bot.send_media_group(chat_id=message.chat.id, media=albums[media_group_id])
        del albums[media_group_id]


@router.message(F.photo)
async def photo_handler(message: Message):
    if message.media_group_id:
        return
    file_id = message.photo[-1].file_id
    file = await bot.get_file(file_id)
    await message.answer(f"📷 Спасибо за фото!\n{file_id}\n{file.file_path}")


@router.message(F.document)
async def document_handler(message: Message):
    file_name = message.document.file_name
    file_size = message.document.file_size
    file_id = message.document.file_id
    await message.answer(f"📄 Спасибо за документ!\nИмя: {file_name}\nРазмер: {file_size} байт\nID: {file_id}")


@router.message(F.audio)
async def audio_handler(message: Message):
    file_name = message.audio.file_name
    file_performer = message.audio.performer
    duration = message.audio.duration
    file_id = message.audio.file_id
    await message.answer(
        f"🎵 Спасибо за аудио!\nИмя: {file_name}\nИсполнитель: {file_performer}\n"
        f"Длительность: {duration} секунд\nID: {file_id}"
    )


@router.message(F.video)
async def video_handler(message: Message):
    file_id = message.video.file_id
    file_size = message.video.file_size
    width = message.video.width
    height = message.video.height
    duration = message.video.duration
    await message.answer(
        f"🎬 Спасибо за видео!\nID: {file_id}\nРазмер: {file_size} байт\n"
        f"Ширина: {width}\nВысота: {height}\nДлительность: {duration} секунд"
    )


@router.message(F.sticker)
async def sticker_handler(message: Message):
    file_id = message.sticker.file_id
    set_name = message.sticker.set_name
    emoji = message.sticker.emoji
    await message.answer(f"🎨 Спасибо за стикер!\nID: {file_id}\nНазвание набора: {set_name}\nЭмодзи: {emoji}")