#  Time Avatar module - changes profile photo every minute with current time
#  Author: custom
#  meta: requires pillow Pyrogram

import asyncio
import os
import logging
from datetime import datetime

from PIL import Image, ImageDraw, ImageFont

from pyrogram import Client, filters

from utils import modules_help, prefix

# Global state
TIME_AVATAR_ENABLED = False
TIME_AVATAR_TASK = None
PREV_PHOTO_PATH = None


def generate_time_image():
    """Generate an image with current time text"""
    img = Image.new("RGB", (512, 512), color=(73, 109, 137))
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
    except Exception:
        font = ImageFont.load_default()

    current_time = datetime.now().strftime("%H:%M:%S")

    draw.text((20, 20), current_time, font=font, fill=(255, 255, 255))

    # Add date below
    date_text = datetime.now().strftime("%d.%m.%Y")
    date_font = ImageFont.load_default()
    draw.text((20, 100), date_text, font=date_font, fill=(255, 255, 255))

    return img


async def time_avatar_task(client):
    """Background task that changes profile photo every minute"""
    global TIME_AVATAR_ENABLED, PREV_PHOTO_PATH

    while TIME_AVATAR_ENABLED:
        try:
            # Generate time image
            img = generate_time_image()

            # Save to temp file
            temp_file = f"temp_avatar_{datetime.now().timestamp()}.png"
            img.save(temp_file)

            # Delete previous photo if exists
            global PREV_PHOTO_PATH
            if PREV_PHOTO_PATH and os.path.exists(PREV_PHOTO_PATH):
                os.remove(PREV_PHOTO_PATH)

            # Set as profile photo using Pyrogram's set_profile_photo
            await client.set_profile_photo(temp_file)

            # Track this photo for deletion next cycle
            PREV_PHOTO_PATH = temp_file

        except Exception as e:
            logging.error("Time avatar error: %s", e)

        # Wait 60 seconds
        await asyncio.sleep(60)


@Client.on_message(filters.command("timeavatar", prefix) & filters.me)
async def timeavatar_cmd(_, message):
    global TIME_AVATAR_ENABLED, TIME_AVATAR_TASK

    if TIME_AVATAR_ENABLED:
        TIME_AVATAR_ENABLED = False
        if TIME_AVATAR_TASK:
            TIME_AVATAR_TASK.cancel()
            TIME_AVATAR_TASK = None
        await message.reply_text("<b>Time avatar disabled</b>")
        # Reset prev photo path
        global PREV_PHOTO_PATH
        PREV_PHOTO_PATH = None
        return

    TIME_AVATAR_ENABLED = True
    TIME_AVATAR_TASK = asyncio.create_task(time_avatar_task(_))
    await message.reply_text("<b>Time avatar enabled - will update every minute</b>")


modules_help["timeavatar"] = {
    "timeavatar": "Toggle time-based profile picture update (updates every minute)",
}