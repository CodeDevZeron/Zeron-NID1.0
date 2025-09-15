import os
import io
import base64
import requests
from flask import Flask, request, jsonify
from PIL import Image, ImageDraw, ImageFont

app = Flask(__name__)

IMGBB_API_KEY = "b402067f6bfc278112333ae2d974c093"
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FONT_DIR = os.path.join(BASE_DIR, "fonts")

def load_font(filename, size):
    """
    Load a font file from the fonts directory.
    This version is more robust for serverless environments like Vercel.
    """
    font_path = os.path.join(FONT_DIR, filename)
    print(f"Attempting to load font from: {font_path}")  # Vercel will show this in logs
    try:
        return ImageFont.truetype(font_path, size)
    except IOError:
        print(f"Error: The font file '{filename}' was not found or could not be loaded. Please ensure it is in the 'fonts' directory.")
        return ImageFont.load_default()
    except Exception as e:
        print(f"An unexpected error occurred while loading the font: {e}")
        return ImageFont.load_default()

@app.route('/generate', methods=['GET'])
def generate_nid():
    try:
        # Get query parameters
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
        img_path = os.path.join(BASE_DIR, "nid.png")
        if not os.path.exists(img_path):
            return jsonify({"error": f"NID template file not found at {img_path}"}), 500
        img = Image.open(img_path).convert("RGB")
        draw = ImageDraw.Draw(img)

        # Load fonts. You MUST ensure these files are in your fonts directory.
        font_bn = load_font("NotoSansBengali-Regular.ttf", 24)
        font_en = load_font("DejaVuSans.ttf", 22)
        font_sign = load_font("sign.ttf", 16)

        black = (0, 0, 0)
        red = (255, 0, 0)

        # Draw Bangla text
        draw.text((240, 127), name_bn, font=font_bn, fill=black)
        draw.text((240, 187), father, font=font_bn, fill=black)
        draw.text((240, 217), mother, font=font_bn, fill=black)
        draw.text((90, 448), address, font=font_bn, fill=black)
        draw.text((395, 596), issue, font=font_bn, fill=black)

        # Draw English text
        draw.text((240, 160), name_en, font=font_en, fill=black)
        draw.text((287, 252), dob, font=font_en, fill=red)
        draw.text((252, 285), nid, font=font_en, fill=red)
        draw.text((60, 270), sign, font=font_sign, fill=black)
        draw.text((230, 525), blood, font=font_en, fill=black)

        # Fetch and paste passport photo
        try:
            photo_response = requests.get(photo_url, timeout=10)
            if photo_response.status_code != 200:
                return jsonify({"error": f"Photo fetch failed with status code: {photo_response.status_code}"})
            photo_bytes = io.BytesIO(photo_response.content)
            passport_img = Image.open(photo_bytes).convert("RGB").resize((120, 140))
            img.paste(passport_img, (30, 120))
        except Exception as e:
            return jsonify({"error": f"Photo fetch failed: {str(e)}"}), 500

        # Save and upload
        buffered = io.BytesIO()
        img.save(buffered, format="JPEG")
        encoded_image = base64.b64encode(buffered.getvalue()).decode('utf-8')

        response = requests.post(
            "https://api.imgbb.com/1/upload",
            data={"key": IMGBB_API_KEY, "image": encoded_image},
            timeout=10
        ).json()

        if not response.get("success"):
            return jsonify({"error": "Upload failed", "api_by": "@DevZeron"}), 500

        return jsonify({"image_url": response["data"]["url"], "api_by": "@DevZeron"})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

