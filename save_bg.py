from PIL import Image, ImageDraw

width, height = 800, 700
img = Image.new("RGB", (width, height), "#87CEEB")
draw = ImageDraw.Draw(img)

def px(x, y, w, h, color):
    sx, sy = width/680, height/400
    draw.rectangle([x*sx, y*sy, (x+w)*sx, (y+h)*sy], fill=color)

def poly(points, color):
    sx, sy = width/680, height/400
    draw.polygon([(x*sx, y*sy) for x,y in points], fill=color)

def circle(cx, cy, r, color):
    sx, sy = width/680, height/400
    draw.ellipse([(cx-r)*sx, (cy-r)*sy, (cx+r)*sx, (cy+r)*sy], fill=color)

def rect_outline(x, y, w, h, color, lw=2):
    sx, sy = width/680, height/400
    draw.rectangle([x*sx, y*sy, (x+w)*sx, (y+h)*sy], outline=color, width=lw)

# Sky gradient layers
px(0, 0, 680, 100, "#87CEEB")
px(0, 100, 680, 100, "#95D4EE")
px(0, 200, 680, 90, "#A8DAED")

# Clouds
px(40, 25, 80, 18, "#FFFFFF"); px(30, 33, 100, 18, "#FFFFFF"); px(50, 15, 60, 18, "#FFFFFF")
px(280, 15, 100, 18, "#FFFFFF"); px(270, 23, 120, 18, "#FFFFFF"); px(290, 7, 80, 18, "#FFFFFF")
px(480, 30, 90, 16, "#FFFFFF"); px(470, 38, 110, 16, "#FFFFFF")

# Ground
px(0, 285, 680, 115, "#5A8A3C")
# Ground detail
px(0, 285, 680, 8, "#4A7A2C")
px(0, 340, 680, 8, "#4A7A2C")

# Path
px(285, 290, 110, 110, "#C4A265")
px(295, 285, 90, 15, "#C4A265")
# Path detail
px(330, 295, 20, 90, "#B89255")

# Dacha main body
px(195, 195, 290, 125, "#F5DEB3")
# Body shading
px(195, 195, 10, 125, "#E5CE93")
px(475, 195, 10, 125, "#E5CE93")

# Roof
poly([(175,198),(340,112),(505,198)], "#8B2500")
poly([(175,198),(340,112),(340,198)], "#A03010")
# Roof ridge
px(315, 110, 50, 14, "#C04020")
# Roof detail lines
for rx in range(190, 340, 20):
    poly([(rx,198),(rx+10,198),(340,112)], "#7A2000")

# Chimney
px(398, 122, 28, 52, "#8B6914")
px(394, 118, 36, 12, "#7A5C10")
px(396, 114, 32, 8, "#9A7824")
# Smoke puffs
px(402, 98, 12, 12, "#DDDDDD")
px(406, 84, 10, 10, "#CCCCCC")
px(400, 72, 10, 10, "#DDDDDD")

# Left window
px(220, 220, 64, 54, "#87CEEB")
px(220, 220, 32, 54, "#9ED8F0")
px(248, 220, 4, 54, "#8B6914")
px(220, 246, 64, 4, "#8B6914")
rect_outline(216, 216, 72, 62, "#8B6914", 3)
# Window sill left
px(212, 276, 80, 8, "#A07830")

# Right window
px(396, 220, 64, 54, "#87CEEB")
px(396, 220, 32, 54, "#9ED8F0")
px(424, 220, 4, 54, "#8B6914")
px(396, 246, 64, 4, "#8B6914")
rect_outline(392, 216, 72, 62, "#8B6914", 3)
# Window sill right
px(388, 276, 80, 8, "#A07830")

# Door
px(313, 250, 54, 70, "#8B6914")
px(317, 254, 22, 56, "#A0784A")
px(341, 254, 22, 56, "#7A5C10")
circle(340, 290, 5, "#FFD700")
rect_outline(309, 246, 62, 74, "#7A5C10", 3)
# Door arch
poly([(309,246),(340,226),(371,246)], "#8B6914")
poly([(313,246),(340,230),(367,246)], "#A0784A")

# Porch
px(287, 308, 106, 12, "#DEB887")
px(285, 295, 10, 25, "#8B6914")
px(385, 295, 10, 25, "#8B6914")
px(283, 305, 114, 6, "#C4A870")

# Fence left
for fx in [55,85,115,145,175]:
    px(fx, 272, 10, 44, "#DEB887")
    px(fx+2, 268, 6, 8, "#C4A870")
px(50, 282, 145, 10, "#DEB887")
px(50, 298, 145, 10, "#DEB887")

# Fence right
for fx in [490,520,550,580,610]:
    px(fx, 272, 10, 44, "#DEB887")
    px(fx+2, 268, 6, 8, "#C4A870")
px(488, 282, 145, 10, "#DEB887")
px(488, 298, 145, 10, "#DEB887")

# Birch tree left - trunk
px(90, 148, 20, 142, "#F5F5F0")
for by in [165,185,205,225,245,265]:
    px(86, by, 10, 10, "#333333")
    px(100, by+10, 10, 10, "#333333")
# Birch foliage
px(50, 90, 100, 70, "#2E7D32")
px(40, 110, 120, 55, "#388E3C")
px(58, 75, 84, 40, "#2E7D32")
px(68, 62, 64, 28, "#1B5E20")
# Foliage highlight
px(80, 68, 30, 20, "#43A047")

# Birch tree right - trunk
px(570, 148, 20, 142, "#F5F5F0")
for by in [165,185,205,225,245,265]:
    px(566, by, 10, 10, "#333333")
    px(580, by+10, 10, 10, "#333333")
# Birch foliage
px(530, 90, 100, 70, "#2E7D32")
px(520, 110, 120, 55, "#388E3C")
px(538, 75, 84, 40, "#2E7D32")
px(548, 62, 64, 28, "#1B5E20")
px(560, 68, 30, 20, "#43A047")

# Sunflowers left
for sx, sy2 in [(155,255),(178,258),(162,262)]:
    px(sx+2, sy2+18, 10, 42, "#4A7C2F")
    px(sx-2, sy2-2, 28, 28, "#FFD700")
    px(sx+2, sy2-6, 20, 36, "#FFD700")
    px(sx-6, sy2+2, 36, 20, "#FFD700")
    circle(sx+10, sy2+10, 9, "#8B4513")
    circle(sx+10, sy2+10, 5, "#5D2E0C")

# Sunflowers right
for sx, sy2 in [(500,255),(523,258),(507,262)]:
    px(sx+2, sy2+18, 10, 42, "#4A7C2F")
    px(sx-2, sy2-2, 28, 28, "#FFD700")
    px(sx+2, sy2-6, 20, 36, "#FFD700")
    px(sx-6, sy2+2, 36, 20, "#FFD700")
    circle(sx+10, sy2+10, 9, "#8B4513")
    circle(sx+10, sy2+10, 5, "#5D2E0C")

# Garden beds left
px(55, 305, 130, 22, "#6B3A2A")
for gx in [60,80,100,120,140]:
    px(gx, 308, 14, 16, "#4CAF50")
    px(gx+4, 305, 6, 6, "#FF5722")

# Garden beds right
px(495, 305, 130, 22, "#6B3A2A")
for gx in [500,520,540,560,580]:
    px(gx, 308, 14, 16, "#4CAF50")
    px(gx+4, 305, 6, 6, "#FF5722")

# Sun
px(608, 18, 52, 52, "#FFD700")
px(598, 28, 72, 32, "#FFD700")
px(620, 8, 28, 72, "#FFD700")
# Sun rays
for angle in [(624,4,12,14),(624,74,12,14),(590,36,14,12),(658,36,14,12),
              (600,12,12,12),(640,12,12,12),(600,64,12,12),(640,64,12,12)]:
    px(*angle, "#FFD700")
# Sun center shine
circle(632, 44, 16, "#FFF176")

# Crop center portion for phone screen
left = (width - 400) // 2
right = left + 400
img = img.crop((left, 0, right, height))
img.save("dacha_bg.png")
print("Cropped and saved!")
print("Improved dacha background saved!")