import os
import io
import base64
import requests
from flask import Flask, request, jsonify
from PIL import Image, ImageDraw, ImageFont

# Initialize Flask app
app = Flask(__name__)

# Replace with your actual ImgBB API key
IMGBB_API_KEY = "b402067f6bfc278112333ae2d974c093"
BASE_DIR = os.path.dirname(__file__)

def load_font(path, size):
    """
    Load a font file from the fonts directory.
    Uses a default font if the specified one isn't found.
    """
    try:
        font_path = os.path.join(BASE_DIR, "fonts", path)
        return ImageFont.truetype(font_path, size)
    except Exception as e:
        print(f"Font loading error for {path}: {e}")
        return ImageFont.load_default()

def draw_bangla_text(base_img, position, text, font, fill=(0, 0, 0)):
    """Draw Bangla text on the image."""
    if not text or not isinstance(text, str):
        return base_img
    draw = ImageDraw.Draw(base_img)
    # Correctly draw the text. The font must support Bangla characters.
    draw.text(position, text, font=font, fill=fill)
    return base_img

@app.route('/generate', methods=['GET'])
def generate_nid():
    try:
        # Get query parameters directly; they are already Unicode strings
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

        # Load fonts. Ensure these font files are present in a 'fonts' directory.
        font_bn = load_font("NotoSansBengali-Regular.ttf", 24)
        font_en = load_font("DejaVuSans.ttf", 22)
        font_sign = load_font("sign.ttf", 16)

        black = (0, 0, 0)
        red = (255, 0, 0)

        # Draw text on the image
        draw_bangla_text(img, (240, 127), name_bn, font_bn, black)   # Name (BN)
        draw_bangla_text(img, (240, 187), father, font_bn, black)     # Father
        draw_bangla_text(img, (240, 217), mother, font_bn, black)     # Mother
        draw_bangla_text(img, (90, 448), address, font_bn, black)     # Address
        draw_bangla_text(img, (395, 596), issue, font_bn, black)      # Issue Date

        draw = ImageDraw.Draw(img)
        draw.text((240, 160), name_en, font=font_en, fill=black)           # Name (EN)
        draw.text((287, 252), dob, font=font_en, fill=red)                 # Date of Birth
        draw.text((252, 285), nid, font=font_en, fill=red)                 # NID
        draw.text((60, 270), sign, font=font_sign, fill=black)             # Signature
        draw.text((230, 525), blood, font=font_en, fill=black)             # Blood Group

        # Fetch and paste passport photo
        try:
            photo_response = requests.get(photo_url, timeout=10)
            if photo_response.status_code != 200:
                return jsonify({"error": f"Photo fetch failed with status code: {photo_response.status_code}"})
            photo_bytes = io.BytesIO(photo_response.content)
            passport_img = Image.open(photo_bytes).convert("RGB")
            passport_img = passport_img.resize((120, 140))
            img.paste(passport_img, (30, 120))
        except Exception as e:
            return jsonify({"error": f"Photo fetch failed: {str(e)}"})

        # Save to bytes
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        buffered.seek(0)

        # Upload to imgbb
        encoded_image = base64.b64encode(buffered.read()).decode('utf-8')
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
    # When deploying to Vercel, the app will be run by a different process.
    # This block is mainly for local testing.
    app.run(debug=True)

