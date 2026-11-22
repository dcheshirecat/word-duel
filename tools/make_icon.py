from PIL import Image, ImageDraw

size = 512
img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(img)

# Light blue rounded background
draw.rounded_rectangle([0, 0, size, size], radius=80, fill="#87CEEB")

# Rainbow arcs
cx, cy = 256, 490
rainbow = [
    ("#E53935", 240), ("#FB8C00", 225), ("#FDD835", 210),
    ("#43A047", 195), ("#1E88E5", 180), ("#8E24AA", 165)
]
for color, r in rainbow:
    bbox = [cx-r, cy-r, cx+r, cy+r]
    draw.arc(bbox, start=200, end=340, fill=color, width=18)

# Draw W as polyline
w_points = [
    (160, 155), (204, 295), (256, 195), (308, 295), (352, 155)
]

# Draw thick white W
for i in range(len(w_points)-1):
    x1, y1 = w_points[i]
    x2, y2 = w_points[i+1]
    draw.line([x1, y1, x2, y2], fill="#FFFFFF", width=36)

# Round the joints
for x, y in w_points:
    draw.ellipse([x-18, y-18, x+18, y+18], fill="#FFFFFF")

img.save("icon.png")
print("Icon saved as icon.png!")