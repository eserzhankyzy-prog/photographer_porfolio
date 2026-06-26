from flask import Blueprint, jsonify
from models import Photo
from flask import jsonify
import requests

api_bp = Blueprint('api', __name__)
@api_bp.route('/weather')
def weather():

    city = "Almaty"

    url = f"https://wttr.in/{city}?format=j1"

    response = requests.get(url)

    data = response.json()

    return jsonify({
        "city": city,
        "temperature": data["current_condition"][0]["temp_C"],
        "weather": data["current_condition"][0]["weatherDesc"][0]["value"]
    })
@api_bp.route('/photos')
def get_photos():

    photos = Photo.query.all()

    result = []

    for photo in photos:
        result.append({
            "id": photo.id,
            "title": photo.title,
            "image_path": photo.image_path,
            "category": photo.category,
            "description": photo.description,
            "price": photo.price,
            "shoot_date": photo.shoot_date.isoformat() if photo.shoot_date else None,
            "album_id": photo.album_id
        })

    return jsonify(result)
