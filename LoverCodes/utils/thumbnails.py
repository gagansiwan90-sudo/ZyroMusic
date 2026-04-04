import os
import re
import aiofiles
import aiohttp
from PIL import Image, ImageDraw, ImageEnhance, ImageFilter, ImageFont, ImageOps
from unidecode import unidecode
from youtubesearchpython.__future__ import VideosSearch
from LoverCodes import app
from config import YOUTUBE_IMG_URL

def changeImageSize(maxWidth, maxHeight, image):
    widthRatio = maxWidth / image.size[0]
    heightRatio = maxHeight / image.size[1]
    newWidth = int(widthRatio * image.size[0])
    newHeight = int(heightRatio * image.size[1])
    newImage = image.resize((newWidth, newHeight))
    return newImage

def truncate(text):
    list = text.split(" ")
    text1 = ""
    text2 = ""    
    for i in list:
        if len(text1) + len(i) < 30:        
            text1 += " " + i
        elif len(text2) + len(i) < 30:       
            text2 += " " + i

    text1 = text1.strip()
    text2 = text2.strip()     
    return [text1,text2]

def crop_center_circle(img, output_size, border, crop_scale=1.5):
    half_the_width = img.size[0] / 2
    half_the_height = img.size[1] / 2
    larger_size = int(output_size * crop_scale)
    img = img.crop(
        (
            half_the_width - larger_size/2,
            half_the_height - larger_size/2,
            half_the_width + larger_size/2,
            half_the_height + larger_size/2
        )
    )
    
    img = img.resize((output_size - 2*border, output_size - 2*border))
    
    
    final_img = Image.new("RGBA", (output_size, output_size), "white")
    
    
    mask_main = Image.new("L", (output_size - 2*border, output_size - 2*border), 0)
    draw_main = ImageDraw.Draw(mask_main)
    draw_main.ellipse((0, 0, output_size - 2*border, output_size - 2*border), fill=255)
    
    final_img.paste(img, (border, border), mask_main)
    
    
    mask_border = Image.new("L", (output_size, output_size), 0)
    draw_border = ImageDraw.Draw(mask_border)
    draw_border.ellipse((0, 0, output_size, output_size), fill=255)
    
    result = Image.composite(final_img, Image.new("RGBA", final_img.size, (0, 0, 0, 0)), mask_border)
    
    return result



async def get_thumb(videoid):
    if os.path.isfile(f"cache/{videoid}_v4.png"):
        return f"cache/{videoid}_v4.png"

    url = f"https://www.youtube.com/watch?v={videoid}"
    try:
        results = VideosSearch(url, limit=1)
        res = await results.next()
        for result in res["result"]:
            title = result.get("title", "Unknown Title")
            duration = result.get("duration", "0:00")
            thumbnail = result["thumbnails"][0]["url"].split("?")[0]
            channel = result.get("channel", {}).get("name", "Unknown Artist")
    except Exception as e:
        print(f"Error fetching thumb data: {e}")
        title, duration, thumbnail, channel = "Unknown Title", "0:00", YOUTUBE_IMG_URL, "Unknown Artist"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(thumbnail) as resp:
                if resp.status == 200:
                    f = await aiofiles.open(f"cache/thumb{videoid}.png", mode="wb")
                    await f.write(await resp.read())
                    await f.close()
                else:
                    return YOUTUBE_IMG_URL

        img = Image.open(f"cache/thumb{videoid}.png").convert("RGBA")
    except Exception as e:
        print(f"Error in get_thumb (downloading/opening): {e}")
        return YOUTUBE_IMG_URL

    # 1. Create Dynamic Blurred Background from YouTube Thumb (16:9)
    bg_w, bg_h = 1280, 720
    img_ratio = img.width / img.height
    bg_ratio = bg_w / bg_h
    if img_ratio > bg_ratio:
        new_w = int(img.height * bg_ratio)
        offset = (img.width - new_w) // 2
        background = img.crop((offset, 0, offset + new_w, img.height))
    else:
        new_h = int(img.width / bg_ratio)
        offset = (img.height - new_h) // 2
        background = img.crop((0, offset, img.width, offset + new_h))
    
    background = background.resize((bg_w, bg_h), Image.Resampling.LANCZOS)
    background = background.filter(ImageFilter.GaussianBlur(radius=80))
    # Darken and add slight color tint for depth
    overlay = Image.new('RGBA', (bg_w, bg_h), (10, 10, 15, 170))
    background = Image.alpha_composite(background.convert("RGBA"), overlay)
    
    # 2. Localized "Frosted Glass" Blur for the Panel
    panel_x, panel_y, panel_w, panel_h = 100, 110, 1080, 500
    # Crop the background where the panel will be
    glass_area = background.crop((panel_x, panel_y, panel_x+panel_w, panel_y+panel_h))
    # Additional blur for the "30% frosted" look
    glass_area = glass_area.filter(ImageFilter.GaussianBlur(radius=30))
    # Slight white tint for the glass feel
    glass_tint = Image.new('RGBA', glass_area.size, (255, 255, 255, 25))
    glass_area = Image.alpha_composite(glass_area, glass_tint)
    
    # Create mask for rounded panel
    panel_mask = Image.new('L', (panel_w, panel_h), 0)
    ImageDraw.Draw(panel_mask).rounded_rectangle([0, 0, panel_w, panel_h], radius=45, fill=255)
    
    # Paste blurred glass area onto background
    background.paste(glass_area, (panel_x, panel_y), panel_mask)

    # 3. Draw Soft Drop Shadows for 3D Depth
    shadow = Image.new('RGBA', (bg_w, bg_h), (0,0,0,0))
    ds = ImageDraw.Draw(shadow)
    ds.rounded_rectangle([panel_x+15, panel_y+20, panel_x+panel_w+15, panel_y+panel_h+20], radius=45, fill=(0,0,0,120))
    shadow = shadow.filter(ImageFilter.GaussianBlur(radius=35))
    background = Image.alpha_composite(background, shadow)

    # 4. Draw Glass 3D Borders & Sheen
    panel_ui = Image.new('RGBA', (bg_w, bg_h), (0,0,0,0))
    dp = ImageDraw.Draw(panel_ui)
    # Bright 3D Bevel Outline
    dp.rounded_rectangle([panel_x, panel_y, panel_x+panel_w, panel_y+panel_h], radius=45, outline=(255, 255, 255, 150), width=2)
    # Inner light edge highlight
    dp.rounded_rectangle([panel_x+2, panel_y+2, panel_x+panel_w-2, panel_y+panel_h-2], radius=45, outline=(255, 255, 255, 40), width=3)
    
    # 5. Glass Reflection (Moving Sheen)
    sheen = Image.new('RGBA', (bg_w, bg_h), (0,0,0,0))
    dsh = ImageDraw.Draw(sheen)
    for i in range(150):
        alpha = int(60 * (1 - abs(i-75)/75))
        dsh.line([(panel_x+250+i, panel_y), (panel_x+550+i, panel_y+panel_h)], fill=(255,255,255,alpha), width=2)
    background = Image.alpha_composite(background, panel_ui)
    background = Image.alpha_composite(background, sheen)

    # 6. Cover Processing with Dynamic Shadow
    cover_size = 430
    w, h = img.size
    min_dim = min(w, h)
    left, top = (w - min_dim)/2, (h - min_dim)/2
    square_img = img.crop((left, top, left+min_dim, top+min_dim)).resize((cover_size, cover_size), Image.Resampling.LANCZOS)
    
    mask = Image.new('L', (cover_size, cover_size), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, cover_size, cover_size], radius=40, fill=255)
    rounded_cover = Image.new('RGBA', (cover_size, cover_size))
    rounded_cover.paste(square_img, (0, 0), mask)
    
    cover_x, cover_y = 150, (bg_h - cover_size) // 2
    # Floating Shadow behind cover
    cv_shadow = Image.new('RGBA', (bg_w, bg_h), (0,0,0,0))
    ImageDraw.Draw(cv_shadow).rounded_rectangle([cover_x+18, cover_y+22, cover_x+cover_size+18, cover_y+cover_size+22], radius=40, fill=(0,0,0,150))
    cv_shadow = cv_shadow.filter(ImageFilter.GaussianBlur(radius=20))
    background = Image.alpha_composite(background, cv_shadow)
    background.paste(rounded_cover, (cover_x, cover_y), rounded_cover)

    # 7. Metadata (Drawn over the frosted glass)
    draw = ImageDraw.Draw(background)
    font_path = "LoverCodes/assets/assets/font.ttf"
    try:
        font_title = ImageFont.truetype(font_path, 36)
        font_artist = ImageFont.truetype(font_path, 22)
        font_time = ImageFont.truetype(font_path, 18)
        font_badge = ImageFont.truetype(font_path, 15)
    except:
        font_title = ImageFont.load_default()
        font_artist = ImageFont.load_default()
        font_time = ImageFont.load_default()
        font_badge = ImageFont.load_default()

    text_x = cover_x + cover_size + 65
    max_text_w = 1140 - text_x
    
    def truncate_text(text, font, max_w):
        if draw.textlength(text, font) <= max_w: return text
        while draw.textlength(text + '...', font) > max_w and len(text) > 0: text = text[:-1]
        return text + '...'

    short_title = truncate_text(title, font_title, max_text_w)
    short_artist = truncate_text(channel, font_artist, max_text_w)

    title_y = 230
    draw.text((text_x, title_y), short_title, font=font_title, fill=(255, 255, 255, 255))
    draw.text((text_x, title_y + 55), short_artist, font=font_artist, fill=(210, 210, 210, 210))

    # 8. 3D UI Controls & Progress Bar
    bar_y, bar_w = title_y + 145, max_text_w - 40
    # Shadow for bar depth
    draw.rounded_rectangle([text_x+1, bar_y+2, text_x+bar_w+1, bar_y+11], radius=5, fill=(0,0,0,60))
    draw.rounded_rectangle([text_x, bar_y, text_x+bar_w, bar_y+9], radius=5, fill=(255,255,255,45))
    prog_w = int(bar_w * 0.45)
    draw.rounded_rectangle([text_x, bar_y, text_x+prog_w, bar_y+9], radius=5, fill=(255,255,255,255))
    # Glowing progress head
    draw.ellipse([text_x+prog_w-9, bar_y-4, text_x+prog_w+9, bar_y+14], fill=(255,255,255,255))
    
    draw.text((text_x, bar_y + 35), "3:14", font=font_time, fill=(235,235,235,180))
    draw.text((text_x + bar_w - 55, bar_y + 35), duration, font=font_time, fill=(235,235,235,180))

    # 9. Draw Icons (Always sharp on top)
    badge_x, badge_y = text_x, bar_y + 90
    draw.rounded_rectangle([badge_x+3, badge_y+4, badge_x+103, badge_y+41], radius=8, fill=(0,0,0,70))
    draw.rounded_rectangle([badge_x, badge_y, badge_x+100, badge_y+37], radius=8, fill=(245, 197, 24, 255))
    draw.text((badge_x + 12, badge_y + 10), "LOSSLESS\nAUDIO", font=font_badge, fill=(0,0,0,255), spacing=-3)
    
    ctrl_cx, ctrl_cy = text_x + bar_w/2, badge_y + 15
    # Play Center (No shadow)
    draw.ellipse([ctrl_cx-30, ctrl_cy-30, ctrl_cx+30, ctrl_cy+30], outline=(255,255,255,210), width=4)
    draw.rectangle([ctrl_cx-8, ctrl_cy-14, ctrl_cx-2, ctrl_cy+14], fill=(255,255,255,255))
    draw.rectangle([ctrl_cx+2, ctrl_cy-14, ctrl_cx+8, ctrl_cy+14], fill=(255,255,255,255))
    
    nx, ny = ctrl_cx + 90, ctrl_cy
    draw.polygon([(nx, ny-11), (nx+17, ny), (nx, ny+11)], fill=(255,255,255,235))
    draw.rectangle([nx+17, ny-11, nx+22, ny+11], fill=(255,255,255,235))
    
    px, py = ctrl_cx - 90, ctrl_cy
    draw.polygon([(px, py-11), (px-17, py), (px, py+11)], fill=(255,255,255,235))
    draw.rectangle([px-22, py-11, px-17, py+11], fill=(255,255,255,235))

    try: os.remove(f"cache/thumb{videoid}.png")
    except: pass
    
    background.save(f"cache/{videoid}_v4.png")
    return f"cache/{videoid}_v4.png"
