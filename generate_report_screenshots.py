import os
import shutil
from PIL import Image, ImageDraw, ImageFont

# Directories
out_dir = r"C:\Users\Sujal\Downloads\Agribandhu-AI-main\project_report_screenshots"
os.makedirs(out_dir, exist_ok=True)
drawable_dir = r"C:\Users\Sujal\Downloads\Agribandhu-AI-main\Agribandhu-AI-main\android_app\app\src\main\res\drawable"

# Fonts helper
def get_font(size, bold=False):
    font_names = ["segoeui.ttf", "arial.ttf", "calibri.ttf"]
    if bold:
        font_names = ["segouib.ttf", "arialbd.ttf", "calibrib.ttf"]
    for fn in font_names:
        try:
            return ImageFont.truetype(fn, size)
        except:
            pass
    return ImageFont.load_default()

W, H = 420, 880

# Colors
C_BG = (242, 255, 216)        # @color/green_backgroung #f2ffd8
C_TOOLBAR = (102, 153, 0)     # @color/green #669900
C_WHITE = (255, 255, 255)
C_DARK = (34, 34, 34)
C_MUTED = (100, 100, 100)
C_BORDER = (210, 230, 180)
C_ACCENT_GREEN = (46, 125, 50)
C_ALERT_BG = (255, 243, 205)
C_ALERT_BORDER = (255, 193, 7)
C_ALERT_TEXT = (133, 100, 4)

def draw_phone_chrome(draw, title):
    # Top Status Bar
    draw.rectangle([0, 0, W, 28], fill=(85, 130, 0))
    f_stat = get_font(12, bold=True)
    draw.text((16, 6), "10:30", fill=C_WHITE, font=f_stat)
    draw.text((W - 85, 6), "5G  85% 🔋", fill=C_WHITE, font=get_font(11))

    # Toolbar
    draw.rectangle([0, 28, W, 80], fill=C_TOOLBAR)
    draw.text((20, 44), "←", fill=C_WHITE, font=get_font(20, bold=True))
    draw.text((55, 43), title, fill=C_WHITE, font=get_font(17, bold=True))
    draw.text((W - 35, 43), "⋮", fill=C_WHITE, font=get_font(20, bold=True))

    # Bottom Android Navigation Bar
    draw.rectangle([0, H - 36, W, H], fill=(230, 240, 215))
    draw.text((80, H - 28), "◀", fill=(120, 120, 120), font=get_font(14))
    draw.text((W//2 - 7, H - 28), "●", fill=(120, 120, 120), font=get_font(14))
    draw.text((W - 90, H - 28), "■", fill=(120, 120, 120), font=get_font(14))


# ==============================================================================
# 1. Figure 6.1: Main_Account Dashboard Screen
# ==============================================================================
def create_fig_6_1():
    img = Image.new("RGB", (W, H), C_BG)
    draw = ImageDraw.Draw(img)
    draw_phone_chrome(draw, "KrishiSarthi Dashboard")

    y = 96
    # Farmer Profile Card
    draw.rounded_rectangle([16, y, W - 16, y + 130], radius=12, fill=C_WHITE, outline=C_BORDER, width=1)
    
    # Farmer avatar
    farmer_icon_p = os.path.join(drawable_dir, "farmer.png")
    if os.path.exists(farmer_icon_p):
        av = Image.open(farmer_icon_p).convert("RGBA").resize((60, 60))
        img.paste(av, (30, y + 20), av)
    else:
        draw.ellipse([30, y + 20, 90, y + 80], fill=(200, 230, 180))

    draw.text((104, y + 18), "Sujal Pokharkar", fill=C_DARK, font=get_font(16, bold=True))
    draw.text((104, y + 40), "📍 Pune, Maharashtra", fill=C_MUTED, font=get_font(12))
    draw.text((104, y + 58), "✉️ sujal.pokharkar@krishisarthi.in", fill=C_MUTED, font=get_font(11))
    
    # Divider line
    draw.line([30, y + 88, W - 30, y + 88], fill=(230, 230, 230), width=1)
    draw.text((30, y + 98), "Plot Allocation: 4.5 Acres", fill=C_ACCENT_GREEN, font=get_font(12, bold=True))
    draw.text((W - 130, y + 98), "Status: Verified Farmer", fill=(100, 140, 50), font=get_font(11))

    y += 144
    # Live Weather Widget Card
    draw.rounded_rectangle([16, y, W - 16, y + 75], radius=10, fill=(235, 248, 255), outline=(180, 215, 240), width=1)
    draw.text((30, y + 12), "🌤️ Pune Live Weather", fill=(20, 80, 140), font=get_font(14, bold=True))
    draw.text((30, y + 36), "Temp: 28.5°C  |  Humidity: 65%  |  Rain: 0.0 mm", fill=(50, 90, 130), font=get_font(12))
    draw.text((30, y + 54), "Advisory: Optimal conditions for vegetative growth", fill=(40, 120, 80), font=get_font(11, bold=True))

    y += 90
    # Active Crops Title
    draw.text((20, y), "My Active Crops (Tracking)", fill=C_DARK, font=get_font(15, bold=True))
    draw.text((W - 95, y + 2), "+ Add Crop", fill=C_TOOLBAR, font=get_font(13, bold=True))

    y += 26
    # Active Crop Cards (Horizontal scrolling preview)
    # Crop 1: Onion
    draw.rounded_rectangle([16, y, 195, y + 180], radius=10, fill=C_WHITE, outline=C_BORDER, width=1)
    onion_p = os.path.join(drawable_dir, "onion.png")
    if os.path.exists(onion_p):
        o_im = Image.open(onion_p).convert("RGBA").resize((163, 85))
        img.paste(o_im, (24, y + 8), o_im)
    draw.text((26, y + 100), "Onion (Pyaz)", fill=C_DARK, font=get_font(13, bold=True))
    draw.text((26, y + 118), "Sown: 15 Sep 2026", fill=C_MUTED, font=get_font(11))
    draw.text((26, y + 134), "Stage: Vegetative (Day 35)", fill=(60, 60, 60), font=get_font(10))
    draw.rounded_rectangle([26, y + 152, 185, y + 172], radius=4, fill=(230, 245, 220))
    draw.text((36, y + 155), "Action: Irrigation Scheduled ➔", fill=C_TOOLBAR, font=get_font(10, bold=True))

    # Crop 2: Tomato
    draw.rounded_rectangle([210, y, W - 16, y + 180], radius=10, fill=C_WHITE, outline=C_BORDER, width=1)
    tom_p = os.path.join(drawable_dir, "tomato.png")
    if os.path.exists(tom_p):
        t_im = Image.open(tom_p).convert("RGBA").resize((163, 85))
        img.paste(t_im, (218, y + 8), t_im)
    draw.text((220, y + 100), "Tomato (Tamatar)", fill=C_DARK, font=get_font(13, bold=True))
    draw.text((220, y + 118), "Sown: 01 Oct 2026", fill=C_MUTED, font=get_font(11))
    draw.text((220, y + 134), "Stage: Vegetative (Day 20)", fill=(60, 60, 60), font=get_font(10))
    draw.rounded_rectangle([220, y + 152, W - 26, y + 172], radius=4, fill=(230, 245, 220))
    draw.text((230, y + 155), "Action: Normal Growth ➔", fill=C_TOOLBAR, font=get_font(10, bold=True))

    y += 194
    # Quick Navigation Section
    draw.text((20, y), "Smart AI Services", fill=C_DARK, font=get_font(15, bold=True))
    y += 24

    buttons = [
        ("AI Crop Doctor", "Instant leaf disease diagnosis & remedies", "🔬"),
        ("Weather Timetable", "Dynamic 7-day weather-adjusted schedule", "📅"),
        ("KrishiSarthi Chatbot", "Ask crop care & fertilizer questions", "💬")
    ]
    for b_title, b_sub, icon in buttons:
        draw.rounded_rectangle([16, y, W - 16, y + 54], radius=8, fill=C_WHITE, outline=C_BORDER, width=1)
        draw.text((28, y + 14), icon, fill=C_TOOLBAR, font=get_font(18))
        draw.text((60, y + 10), b_title, fill=C_DARK, font=get_font(13, bold=True))
        draw.text((60, y + 29), b_sub, fill=C_MUTED, font=get_font(10.5))
        draw.text((W - 35, y + 16), "➔", fill=C_TOOLBAR, font=get_font(16))
        y += 62

    img.save(os.path.join(out_dir, "Figure_6.1_Main_Account_Dashboard.png"), quality=95)
    print("Created Figure 6.1")


# ==============================================================================
# 2. Figure 6.2: Twelve-Crop Selection Grid
# ==============================================================================
def create_fig_6_2():
    img = Image.new("RGB", (W, H), C_BG)
    draw = ImageDraw.Draw(img)
    draw_phone_chrome(draw, "Select Crop - 12 Crops")

    draw.text((16, 92), "Supported Crops Library", fill=C_DARK, font=get_font(15, bold=True))
    draw.text((16, 112), "Choose your crop to initialize dynamic AI schedule & care", fill=C_MUTED, font=get_font(11))

    crops = [
        ("Onion", "Pyaz / Kanda", "onion.png"),
        ("Tomato", "Tamatar", "tomato.png"),
        ("Wheat", "Gehu / Gehun", "wheat.png"),
        ("Potato", "Aloo / Batata", "potato.png"),
        ("Rice", "Paddy / Chawal", "rice.png"),
        ("Maize", "Corn / Makka", "maize.png"),
        ("Cotton", "Kapas", "cotton.png"),
        ("Soybean", "Soya / Soyabean", "soybean.png"),
        ("Sugarcane", "Ganna / Ikshu", "sugarcane.png"),
        ("Chilli", "Mirchi / Mirch", "chilli.png"),
        ("Brinjal", "Baingan / Vangi", "brinjal.png"),
        ("Groundnut", "Peanut / Mungfali", "groundnut.png"),
    ]

    card_w = (W - 32 - 16) // 3
    card_h = 158
    start_y = 138

    for idx, (c_name, c_alias, img_file) in enumerate(crops):
        row = idx // 3
        col = idx % 3
        cx = 16 + col * (card_w + 8)
        cy = start_y + row * (card_h + 10)

        is_selected = (c_name == "Onion")
        border_col = C_TOOLBAR if is_selected else C_BORDER
        bg_col = (250, 255, 245) if is_selected else C_WHITE
        draw.rounded_rectangle([cx, cy, cx + card_w, cy + card_h], radius=8, fill=bg_col, outline=border_col, width=2 if is_selected else 1)

        c_path = os.path.join(drawable_dir, img_file)
        if os.path.exists(c_path):
            c_im = Image.open(c_path).convert("RGBA").resize((card_w - 12, 70))
            img.paste(c_im, (cx + 6, cy + 6), c_im)

        draw.text((cx + 8, cy + 82), c_name, fill=C_DARK, font=get_font(12, bold=True))
        draw.text((cx + 8, cy + 98), c_alias, fill=C_MUTED, font=get_font(9))

        if is_selected:
            draw.rounded_rectangle([cx + 6, cy + 124, cx + card_w - 6, cy + 148], radius=4, fill=C_TOOLBAR)
            draw.text((cx + 20, cy + 130), "Selected ✓", fill=C_WHITE, font=get_font(10, bold=True))
        else:
            draw.rounded_rectangle([cx + 6, cy + 124, cx + card_w - 6, cy + 148], radius=4, fill=(235, 245, 225))
            draw.text((cx + 24, cy + 130), "Select +", fill=C_TOOLBAR, font=get_font(10, bold=True))

    img.save(os.path.join(out_dir, "Figure_6.2_Twelve_Crop_Selection_Grid.png"), quality=95)
    print("Created Figure 6.2")


# ==============================================================================
# 3. Figure 6.3: AI Chatbot Conversation Screen
# ==============================================================================
def create_fig_6_3():
    img = Image.new("RGB", (W, H), C_BG)
    draw = ImageDraw.Draw(img)
    draw_phone_chrome(draw, "KrishiSarthi AI Assistant")

    draw.rectangle([0, 80, W, 106], fill=(235, 245, 220))
    draw.text((20, 86), "🟢 Agronomic NLP Assistant  |  Verified ICAR Guidance", fill=(40, 100, 30), font=get_font(11, bold=True))

    y = 120
    draw.rounded_rectangle([W//2 - 50, y, W//2 + 50, y + 20], radius=10, fill=(220, 230, 205))
    draw.text((W//2 - 32, y + 4), "Today, 10:28 AM", fill=(80, 80, 80), font=get_font(10))

    y += 36
    q1 = "How much urea should I add to my\nonion crop in the vegetative stage?"
    draw.rounded_rectangle([W - 270, y, W - 16, y + 54], radius=12, fill=C_TOOLBAR)
    draw.text((W - 258, y + 8), q1, fill=C_WHITE, font=get_font(12))
    draw.text((W - 55, y + 38), "10:28 AM ✓✓", fill=(215, 245, 175), font=get_font(9))

    y += 66
    b_reply = [
        "🌾 Onion Care (Vegetative Stage, 30-45 Days):",
        "• Recommended Dose: Apply 25-30 kg Urea",
        "  per acre as top-dressing.",
        "• Irrigation: Irrigate immediately after applying",
        "  fertilizer to ensure rapid root uptake.",
        "• Weather Rule: Postpone application if heavy",
        "  rain (>15 mm) is expected in next 24-48 hrs",
        "  to avoid chemical leaching."
    ]
    draw.rounded_rectangle([16, y, W - 40, y + 160], radius=12, fill=C_WHITE, outline=C_BORDER, width=1)
    
    draw.rounded_rectangle([24, y + 8, 85, y + 24], radius=4, fill=(235, 245, 225))
    draw.text((28, y + 10), "🤖 KrishiSarthi", fill=C_TOOLBAR, font=get_font(9, bold=True))

    by = y + 30
    for line in b_reply:
        draw.text((26, by), line, fill=C_DARK, font=get_font(11.5))
        by += 15
    draw.text((W - 85, y + 142), "10:29 AM", fill=C_MUTED, font=get_font(9))

    y += 175
    q2 = "Is there any fungal disease risk\ndue to recent humidity?"
    draw.rounded_rectangle([W - 260, y, W - 16, y + 50], radius=12, fill=C_TOOLBAR)
    draw.text((W - 248, y + 8), q2, fill=C_WHITE, font=get_font(12))
    draw.text((W - 55, y + 34), "10:30 AM ✓✓", fill=(215, 245, 175), font=get_font(9))

    y += 62
    b_reply2 = [
        "⚠️ Alert: High humidity (>70%) favors Purple Blotch.",
        "• Inspect leaf tips for small purple/brown spots.",
        "• Organic Option: Spray 5% Neem Seed Kernel",
        "  Extract (NSKE) or Neem Oil @ 5 ml/liter.",
        "• Upload a leaf photo to 'Crop Doctor' for",
        "  instant automated severity assessment."
    ]
    draw.rounded_rectangle([16, y, W - 40, y + 125], radius=12, fill=C_WHITE, outline=C_BORDER, width=1)
    draw.rounded_rectangle([24, y + 8, 85, y + 24], radius=4, fill=(235, 245, 225))
    draw.text((28, y + 10), "🤖 KrishiSarthi", fill=C_TOOLBAR, font=get_font(9, bold=True))

    by2 = y + 30
    for line in b_reply2:
        draw.text((26, by2), line, fill=C_DARK, font=get_font(11.5))
        by2 += 15

    in_y = H - 85
    draw.rounded_rectangle([16, in_y, W - 65, in_y + 42], radius=21, fill=C_WHITE, outline=C_BORDER, width=1)
    draw.text((32, in_y + 12), "Ask crop, disease, or fertilizer query...", fill=C_MUTED, font=get_font(12))
    draw.text((W - 100, in_y + 11), "📎", fill=C_MUTED, font=get_font(16))

    draw.ellipse([W - 55, in_y, W - 15, in_y + 40], fill=C_TOOLBAR)
    draw.text((W - 42, in_y + 10), "➤", fill=C_WHITE, font=get_font(16))

    img.save(os.path.join(out_dir, "Figure_6.3_AI_Chatbot_Conversation.png"), quality=95)
    print("Created Figure 6.3")


# ==============================================================================
# 4. Figure 6.4: Weather-Adjusted Weekly Timetable
# ==============================================================================
def create_fig_6_4():
    img = Image.new("RGB", (W, H), C_BG)
    draw = ImageDraw.Draw(img)
    draw_phone_chrome(draw, "Weather-Aware Timetable")

    y = 92
    draw.rounded_rectangle([16, y, W - 16, y + 72], radius=10, fill=C_WHITE, outline=C_BORDER, width=1)
    draw.text((26, y + 10), "🧅 Crop: Onion (Kanda / Pyaz)", fill=C_DARK, font=get_font(14, bold=True))
    draw.text((26, y + 32), "Sowing Date: 15 Sep 2026  |  Location: Pune", fill=C_MUTED, font=get_font(11))
    draw.text((26, y + 50), "Current Phenological Stage: Vegetative (Day 35)", fill=C_ACCENT_GREEN, font=get_font(11, bold=True))

    y += 82
    draw.rounded_rectangle([16, y, W - 16, y + 66], radius=10, fill=C_ALERT_BG, outline=C_ALERT_BORDER, width=2)
    draw.text((28, y + 8), "🌧️ RAINFALL ALERT: 22.5 mm Expected on Thursday", fill=(180, 50, 0), font=get_font(12, bold=True))
    draw.text((28, y + 28), "Engine automatically postponed Thursday's irrigation task.", fill=C_ALERT_TEXT, font=get_font(11))
    draw.text((28, y + 46), "Reason: Soil will be saturated; prevents runoff & root rot.", fill=(120, 80, 10), font=get_font(10.5))

    y += 76
    draw.text((20, y), "7-Day Dynamic Action Schedule", fill=C_DARK, font=get_font(14, bold=True))
    y += 22

    tasks = [
        ("Mon, Oct 19 (Day 34)", "Manual Weeding & Hoeing", "Completed ✓", (40, 140, 40), C_WHITE),
        ("Tue, Oct 20 (Day 35)", "Soil Aeration Check", "Completed ✓", (40, 140, 40), C_WHITE),
        ("Wed, Oct 21 (Day 36)", "Foliar Spray (Neem 5ml/L)", "Scheduled", (50, 100, 180), C_WHITE),
        ("Thu, Oct 22 (Day 37)", "⚠️ IRRIGATION POSTPONED", "POSTPONED", (210, 50, 20), (255, 240, 240)),
        ("Fri, Oct 23 (Day 38)", "Drainage & Field Inspection", "Pending", (120, 120, 120), C_WHITE),
        ("Sat, Oct 24 (Day 39)", "Top-Dress Urea (25 kg/acre)", "Scheduled", (50, 100, 180), C_WHITE),
        ("Sun, Oct 25 (Day 40)", "Rest & Canopy Review", "Pending", (120, 120, 120), C_WHITE)
    ]

    for day_str, task_title, status_str, badge_col, bg_box in tasks:
        is_postponed = ("POSTPONED" in status_str)
        border_box = (230, 80, 60) if is_postponed else C_BORDER
        box_h = 58 if is_postponed else 46
        draw.rounded_rectangle([16, y, W - 16, y + box_h], radius=8, fill=bg_box, outline=border_box, width=2 if is_postponed else 1)

        draw.text((26, y + 8), day_str, fill=C_MUTED if not is_postponed else (180, 40, 20), font=get_font(10, bold=is_postponed))
        draw.text((26, y + 24), task_title, fill=C_DARK if not is_postponed else (180, 20, 20), font=get_font(12, bold=True))

        if is_postponed:
            draw.text((26, y + 42), "↳ Rescheduled after rainfall ends to avoid waterlogging", fill=(160, 50, 30), font=get_font(9.5, bold=True))

        badge_w = 80
        draw.rounded_rectangle([W - 16 - badge_w - 8, y + 8, W - 24, y + 28], radius=4, fill=badge_col)
        draw.text((W - 16 - badge_w - 4, y + 11), status_str, fill=C_WHITE, font=get_font(9.5, bold=True))

        y += box_h + 8

    img.save(os.path.join(out_dir, "Figure_6.4_Weather_Adjusted_Weekly_Timetable.png"), quality=95)
    print("Created Figure 6.4")


# ==============================================================================
# 5. Figure 6.5: Crop Doctor Diagnosis Result
# ==============================================================================
def create_fig_6_5():
    img = Image.new("RGB", (W, H), C_BG)
    draw = ImageDraw.Draw(img)
    draw_phone_chrome(draw, "Crop Doctor Diagnosis")

    y = 92
    draw.rounded_rectangle([16, y, W - 16, y + 185], radius=10, fill=C_WHITE, outline=C_BORDER, width=1)
    draw.text((26, y + 10), "Uploaded Leaf Specimen Analysis", fill=C_DARK, font=get_font(13, bold=True))

    draw.rectangle([26, y + 32, W - 26, y + 172], fill=(230, 240, 220))
    draw.polygon([(60, y + 150), (120, y + 60), (280, y + 50), (360, y + 120), (300, y + 165), (150, y + 165)], fill=(120, 180, 80), outline=(80, 140, 50))
    draw.ellipse([140, y + 75, 195, y + 115], fill=(130, 60, 40), outline=(100, 30, 20))
    draw.ellipse([230, y + 90, 280, y + 140], fill=(140, 70, 50), outline=(100, 30, 20))
    draw.ellipse([180, y + 120, 220, y + 155], fill=(120, 50, 30), outline=(100, 30, 20))

    draw.rectangle([130, y + 68, 290, y + 160], outline=(255, 60, 0), width=2)
    draw.rectangle([130, y + 52, 245, y + 68], fill=(255, 60, 0))
    draw.text((135, y + 54), "Lesion: 32.4% (Conf: 94.8%)", fill=C_WHITE, font=get_font(9, bold=True))

    y += 196
    draw.rounded_rectangle([16, y, W - 16, y + 125], radius=10, fill=C_WHITE, outline=C_BORDER, width=1)
    draw.text((26, y + 10), "Pathology Diagnostic Summary", fill=C_DARK, font=get_font(13, bold=True))

    draw.rounded_rectangle([W - 110, y + 8, W - 26, y + 28], radius=4, fill=(230, 70, 50))
    draw.text((W - 98, y + 11), "MODERATE", fill=C_WHITE, font=get_font(9.5, bold=True))

    draw.text((26, y + 36), "Identified Disease:", fill=C_MUTED, font=get_font(11))
    draw.text((135, y + 34), "Purple Blotch (Alternaria porri)", fill=(180, 40, 20), font=get_font(12, bold=True))

    draw.text((26, y + 56), "Host Crop:", fill=C_MUTED, font=get_font(11))
    draw.text((135, y + 56), "Onion (Allium cepa)", fill=C_DARK, font=get_font(11, bold=True))

    draw.text((26, y + 76), "Pathogen Type:", fill=C_MUTED, font=get_font(11))
    draw.text((135, y + 76), "Fungal Pathogen (Foliar)", fill=C_DARK, font=get_font(11))

    draw.text((26, y + 96), "Damaged Area (σ):", fill=C_MUTED, font=get_font(11))
    draw.text((135, y + 96), "32.4% (Inference Time: 184 ms)", fill=C_ACCENT_GREEN, font=get_font(11, bold=True))

    y += 136
    draw.rounded_rectangle([16, y, W - 16, y + 265], radius=10, fill=C_WHITE, outline=C_BORDER, width=1)
    draw.text((26, y + 12), "Prescribed Dual Remediation (ICAR Verified)", fill=C_DARK, font=get_font(13, bold=True))

    draw.rounded_rectangle([24, y + 38, W - 24, y + 130], radius=8, fill=(255, 245, 245), outline=(255, 200, 200), width=1)
    draw.text((34, y + 46), "🧪 Chemical Treatment (Immediate)", fill=(180, 40, 20), font=get_font(12, bold=True))
    draw.text((34, y + 68), "• Spray Mancozeb 75% WP @ 2.5 g/liter of water,", fill=C_DARK, font=get_font(11))
    draw.text((34, y + 86), "  OR Propiconazole 25% EC @ 1 ml/liter.", fill=C_DARK, font=get_font(11))
    draw.text((34, y + 104), "• Spray evenly on upper & lower leaf surfaces.", fill=(140, 40, 40), font=get_font(10.5))

    draw.rounded_rectangle([24, y + 138, W - 24, y + 225], radius=8, fill=(245, 255, 245), outline=(200, 240, 200), width=1)
    draw.text((34, y + 146), "🌿 Organic / Eco-Friendly Remedy", fill=C_ACCENT_GREEN, font=get_font(12, bold=True))
    draw.text((34, y + 168), "• Cold-pressed Neem Oil @ 5 ml/liter + 1 ml liquid", fill=C_DARK, font=get_font(11))
    draw.text((34, y + 186), "  soap surfactant as adhesive agent.", fill=C_DARK, font=get_font(11))
    draw.text((34, y + 204), "• Repeat spray every 7 days until spots fade.", fill=(40, 120, 40), font=get_font(10.5))

    draw.text((26, y + 236), "⚠️ Cultural Advisory: Avoid overhead sprinkler irrigation.", fill=(160, 100, 20), font=get_font(10, bold=True))

    img.save(os.path.join(out_dir, "Figure_6.5_Crop_Doctor_Diagnosis_Result.png"), quality=95)
    print("Created Figure 6.5")


if __name__ == '__main__':
    create_fig_6_1()
    create_fig_6_2()
    create_fig_6_3()
    create_fig_6_4()
    create_fig_6_5()

    proj_dir = r"E:\MIT ADT Degree\SEM 5\PBL Sem 5 - Krishi sarthi\Project file\project_report_screenshots"
    os.makedirs(proj_dir, exist_ok=True)
    for f in os.listdir(out_dir):
        if f.endswith('.png'):
            shutil.copy2(os.path.join(out_dir, f), os.path.join(proj_dir, f))
    print("All screenshots generated and mirrored successfully!")
