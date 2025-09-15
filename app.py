from flask import Flask, request, jsonify
from PIL import Image, ImageDraw, ImageFont
import requests, base64, io, os

app = Flask(__name__)

IMGBB_API_KEY = os.environ.get("IMGBB_API_KEY", "b402067f6bfc278112333ae2d974c093")

@app.route('/generate', methods=['GET'])
def generate_nid():
    # Query parameters
    name_bn = request.args.get("name_bn", "নাম")
    name_en = request.args.get("name_en", "Name")
    father = request.args.get("father", "Father")
    mother = request.args.get("mother", "Mother")
    dob = request.args.get("dob", "01-01-2000")
    nid = request.args.get("nid", "1234567890")
    address = request.args.get("address", "ঢাকা, বাংলাদেশ")
    blood = request.args.get("blood", "O+")
    sign = request.args.get("sign", "Zeron")
    Issue = request.args.get("Issue", "০১/০৯/২০২৫")

    photo_url = request.args.get(
        "photo",
        "https://i.ibb.co/cL21hkZ/IMG-20241022-192024-450.jpg"
    )

    # Load NID template
    img = Image.open("assets/nid.png").convert("RGB")
    draw = ImageDraw.Draw(img)

    # Fonts (Bangla + English)
    font_bn = ImageFont.truetype("fonts/SolaimanLipi.ttf", 26, encoding="unic")
    font_en = ImageFont.truetype("fonts/Verdana.ttf", 22)
    font_sign = ImageFont.truetype("fonts/sign.ttf", 18)

    black = (0, 0, 0)
    red = (255, 0, 0)

    # Draw text
    draw.text((240, 127), name_bn, font=font_bn, fill=black)   # Bangla name
    draw.text((240, 160), name_en, font=font_en, fill=black)
    draw.text((240, 187), father, font=font_bn, fill=black)
    draw.text((240, 217), mother, font=font_bn, fill=black)
    draw.text((287, 252), dob, font=font_en, fill=red)
    draw.text((252, 285), nid, font=font_en, fill=red)
    draw.text((60, 270), sign, font=font_sign, fill=black)
    draw.text((90, 448), address, font=font_bn, fill=black)
    draw.text((230, 525), blood, font=font_en, fill=black)
    draw.text((395, 596), Issue, font=font_bn, fill=black)

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

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
