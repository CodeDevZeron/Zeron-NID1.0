import os
import io
import base64
import requests
from flask import Flask, request, jsonify
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

IMGBB_API_KEY = "b402067f6bfc278112333ae2d974c093"
BASE_DIR = os.path.dirname(__file__)

def load_font(path, size):
    try:
        return ImageFont.truetype(os.path.join(BASE_DIR, path), size)
    except Exception as e:
        print(f"Font loading error: {e}")
        return ImageFont.load_default()

def draw_bangla_text(base_img, position, text, font, fill=(0, 0, 0)):
    """Draw Bangla text on a new layer and paste it onto the base image."""
    if not text or not isinstance(text, str):
        return base_img
    txt_img = Image.new("RGBA", base_img.size, (255, 255, 255, 0))
    d = ImageDraw.Draw(txt_img)
    # Ensure proper rendering with left alignment and anchor
    d.text(position, text, font=font, fill=fill, align="left", anchor="lt", encoding="utf-8")
    base_img.paste(txt_img, (0, 0), txt_img)
    return base_img

@app.route('/generate', methods=['GET'])
def generate_nid():
    try:
        # Query parameters with UTF-8 encoding
        name_bn = request.args.get("name_bn", "রাহাত হোসেন")
        name_en = request.args.get("name_en", "Rahat Hossain")
        father = request.args.get("father", "আব্দুল করিম")
        mother = request.args.get("mother", "আসমা আক্তার")
        dob = request.args.get("dob", "15-08-1998")
        nid = request.args.get("nid", "8765432109")
        address = request.args.get("address", "চট্টগ্রাম, বাংলাদেশ")
        blood = request.args.get("blood", "AB")
        sign = request.args.get("sign", "Zeron")
        issue = request.args.get("issue", "০৯/০৯/২০২৫")

        photo_url = request.args.get(
            "photo",
            "https://i.ibb.co/cL21hkZ/IMG-20241022-192024-450.jpg"
        )

        # Load NID template
        img = Image.open(os.path.join(BASE_DIR, "nid.png")).convert("RGB")

        # Fonts
        font_bn = load_font("fonts/NotoSansBengali-Regular.ttf", 24)
        font_en = load_font("fonts/DejaVuSans.ttf", 22)
        font_sign = load_font("fonts/sign.ttf", 16)

        black = (0, 0, 0)
        red = (255, 0, 0)

        # Draw Bangla text with adjusted positions
        img = draw_bangla_text(img, (240, 130), name_bn, font_bn, black)  # Name (BN)
        img = draw_bangla_text(img, (240, 190), father, font_bn, black)    # Father
        img = draw_bangla_text(img, (240, 220), mother, font_bn, black)    # Mother
        img = draw_bangla_text(img, (90, 450), address, font_bn, black)    # Address
        img = draw_bangla_text(img, (395, 600), issue, font_bn, black)     # Issue Date

        # Draw English text
        draw = ImageDraw.Draw(img)
        draw.text((240, 160), name_en, font=font_en, fill=black)           # Name (EN)
        draw.text((287, 252), dob, font=font_en, fill=red)                # Date of Birth
        draw.text((252, 285), nid, font=font_en, fill=red)                # NID
        draw.text((60, 270), sign, font=font_sign, fill=black)            # Signature
        draw.text((230, 525), blood, font=font_en, fill=black)            # Blood Group

        # Fetch and paste passport photo
        try:
            photo_response = requests.get(photo_url, timeout=10)
            photo_bytes = io.BytesIO(photo_response.content)
            passport_img = Image.open(photo_bytes).convert("RGB")
            passport_img = passport_img.resize((120, 140))  # Resize to fit
            img.paste(passport_img, (30, 120))  # Position for passport photo
        except Exception as e:
            return jsonify({"error": f"Photo fetch failed: {str(e)}"})

        # Save to bytes
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        buffered.seek(0)

        # Upload to imgbb
        encoded_image = base64.b64encode(buffered.read())
        response = requests.post(
            "https://api.imgbb.com/1/upload",
            data={"key": IMGBB_API_KEY, "image": encoded_image},
            timeout=10
        ).json()

        if not response.get("success"):
            return jsonify({"error": "Upload failed", "api_by": "@DevZeron"})

        return jsonify({
            "image_url": response["data"]["url"],
            "api_by": "@DevZeron"
        })
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
