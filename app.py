import os
import io
import base64
import requests
from flask import Flask, request, jsonify
from PIL import Image, ImageDraw, ImageFont
import bangla  # 🔥 বাংলা টেক্সট শেপিং ঠিক করার জন্য

app = Flask(__name__)

IMGBB_API_KEY = "b402067f6bfc278112333ae2d974c093"
BASE_DIR = os.path.dirname(__file__)

def load_font(path, size):
    try:
        return ImageFont.truetype(os.path.join(BASE_DIR, path), size)
    except Exception as e:
        return ImageFont.load_default()

@app.route('/generate', methods=['GET'])
def generate_nid():
    try:
        # Query parameters
        name_bn = request.args.get("name_bn", "নাম")
        name_en = request.args.get("name_en", "Name")
        father = request.args.get("father", "Father")
        mother = request.args.get("mother", "Mother")
        dob = request.args.get("dob", "01-01-2000")
        nid = request.args.get("nid", "1234567890")
        address = request.args.get("address", "Dhaka, Bangladesh")
        blood = request.args.get("blood", "O+")
        sign = request.args.get("sign", "Zeron")
        issue = request.args.get("issue", "০৯/০৯/২০২৫")

        photo_url = request.args.get(
            "photo",
            "https://i.ibb.co.com/cL21hkZ/IMG-20241022-192024-450.jpg"
        )

        # Load NID template
        img = Image.open("nid.png").convert("RGB")
        draw = ImageDraw.Draw(img)

        # Fonts
        font_bn = load_font("fonts/NotoSansBengali-Regular.ttf", 24)
        font_en = load_font("fonts/DejaVuSans.ttf", 22)
        font_sign = load_font("fonts/sign.ttf", 16)

        black = (0, 0, 0)
        red = (255, 0, 0)

        # ✅ Bangla shaping fix
        name_bn = bangla.convert(name_bn)
        father = bangla.convert(father)
        mother = bangla.convert(mother)
        address = bangla.convert(address)
        issue = bangla.convert(issue)

        # Draw text
        draw.text((240, 127), name_bn, font=font_bn, fill=black)
        draw.text((240, 160), name_en, font=font_en, fill=black)
        draw.text((240, 187), father, font=font_bn, fill=black)
        draw.text((240, 217), mother, font=font_bn, fill=black)
        draw.text((287, 252), dob, font=font_en, fill=red)
        draw.text((252, 285), nid, font=font_en, fill=red)
        draw.text((60, 270), sign, font=font_sign, fill=black)
        draw.text((90, 448), address, font=font_bn, fill=black)
        draw.text((230, 525), blood, font=font_en, fill=black)
        draw.text((395, 596), issue, font=font_bn, fill=black)

        # Fetch and paste passport photo
        try:
            photo_response = requests.get(photo_url)
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
            data={"key": IMGBB_API_KEY, "image": encoded_image}
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
    app.run(debug=True)
