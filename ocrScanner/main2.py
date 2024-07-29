from flask import Flask, jsonify, request
import requests
import os
from flask_cors import CORS
import cv2
import fitz
import json
from ArabicOcr import arabicocr
from PIL import Image, ImageOps, ImageEnhance
from spellchecker import SpellChecker
import sys
import locale

# Ensure the default encoding is UTF-8

user_model = {
    "firstName": "",
    "lastName": "",
    "address": "",
    "numbers": "",
    "serialDate": "",
    "region": "",
    "serial": "",
    "religion": "",
    "status": "",
    "deadline": "",
    "gender": "",
    "job": ""
}


spell = SpellChecker(language='ar')

def correct_arabic_spelling(text):
    # Split text into words
    words = text.split()
    corrected_words = []

    for word in words:
        # Check if the word is misspelled
        if word in spell:
            corrected_words.append(word)
        else:
            # Get the most likely correction
            corrected_word = spell.correction(word)
            corrected_words.append(corrected_word)

    # Join the corrected words back into a single string
    corrected_text = ' '.join(corrected_words)
    return corrected_text
def organize_ocr_to_json(image_path, index=0):
    # Define the output image path (can be any valid path)
    out_image = "output-%i.png" % index

    # Perform OCR on the given image

    results = arabicocr.arabic_ocr(image_path, out_image)
    if index == 0:
        firstname_region = ((300, 140), (811, 216))
        lastname_region = ((300, 207), (811, 273))
        address_region = ((300, 255), (811, 324))
        region_region = ((300, 315), (811, 376))
        numbers_region = ((300, 425), (811, 482))

        # Helper function to check if a point is within a region
        def within_region(point, region):
            (x, y) = point
            (top_left, bottom_right) = region
            (x1, y1) = top_left
            (x2, y2) = bottom_right
            return x1 <= x <= x2 and y1 <= y <= y2

        # Process OCR results
        for result in results:
            coordinates = result[0]
            text = result[1]
            # Calculate the center point of the bounding box
            center_x = (coordinates[0][0] + coordinates[2][0]) // 2
            center_y = (coordinates[0][1] + coordinates[2][1]) // 2
            center_point = (center_x, center_y)

            # Check which region the text belongs to and update the user model accordingly
            if within_region(center_point, firstname_region):
                user_model["firstName"] += f" {text}"
            elif within_region(center_point, lastname_region):
                user_model["lastName"] += f" {text}"
            elif within_region(center_point, address_region):
                user_model["address"] += f" {text}"
            elif within_region(center_point, numbers_region):
                user_model["serial"] += f" {text}"
            elif within_region(center_point, region_region):
                user_model["region"] += f" {text}"

        # Clean up whitespace
        for key in user_model:
            user_model[key] = user_model[key].strip()

        # Convert the user model dictionary to a JSON object
        user_model_json = json.dumps(user_model, ensure_ascii=False)

        return user_model_json
    if index == 1:
        numberDate_region = ((214, 38), (380, 106))
        function_region = ((516, 88), (687, 144))
        gender_region = ((571, 161), (676, 232))
        religion_region = ((421, 169), (552, 240))
        satuts_region = ((249, 164), (382, 248))
        deadline_region = ((249, 246), (697, 325))

        # Helper function to check if a point is within a region
        def within_region(point, region):
            (x, y) = point
            (top_left, bottom_right) = region
            (x1, y1) = top_left
            (x2, y2) = bottom_right
            return x1 <= x <= x2 and y1 <= y <= y2

        # Process OCR results
        for result in results:
            coordinates = result[0]
            text = result[1]
            # Calculate the center point of the bounding box
            center_x = (coordinates[0][0] + coordinates[2][0]) // 2
            center_y = (coordinates[0][1] + coordinates[2][1]) // 2
            center_point = (center_x, center_y)

            # Check which region the text belongs to and update the user model accordingly
            if within_region(center_point, numberDate_region):
                user_model["serialDate"] += f" {text}"
            elif within_region(center_point, function_region):
                user_model["job"] += f" {text}"
            elif within_region(center_point, gender_region):
                user_model["gender"] += f" {text}"
            elif within_region(center_point, religion_region):
                user_model["religion"] += f" {text}"
            elif within_region(center_point, satuts_region):
                user_model["status"] += f" {text}"
            elif within_region(center_point, deadline_region):
                user_model["deadline"] += f" {text}"

        # Clean up whitespace
        for key in user_model:
            user_model[key] = user_model[key].strip()

        # Convert the user model dictionary to a JSON object
        user_model_json = json.dumps(user_model, ensure_ascii=False)

        return user_model_json


def transformImage(path, index=0):
    image = Image.open(path)
    gray_image = ImageOps.grayscale(image)
    enhancer = ImageEnhance.Contrast(gray_image)
    enhanced_image = enhancer.enhance(2.0)
    if index == 0:
        thresh = 55
    else:
        thresh = 130
    threshold_image = enhanced_image.point(lambda p: 0 if p > thresh else 255)
    threshold_image.save(path)
    image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    blurred = cv2.GaussianBlur(image, (1, 1), 0)
    cv2.imwrite(path, blurred)


app = Flask(__name__)
CORS(app)


# Route to receive PDF file
@app.route('/upload', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part in the request'}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    # Save file locally
    file.save(os.path.join('uploads', file.filename))
    paths = []
    pdf = 'uploads/' + file.filename
    doc = fitz.open(pdf)
    for page in doc:
        pix = page.get_pixmap()
        pix.save("page-%i.png" % page.number)
        paths.append("page-%i.png" % page.number)

    for index, p in enumerate(paths):
        transformImage(p, index)
        json_result = organize_ocr_to_json(p, index)

    print(user_model)
    spring_boot_url = 'http://localhost:8080/api/user/create'
    # Send POST request with JSON payload
    response = requests.post(spring_boot_url, json=user_model)
    print(response)
    globals()['user_model'] = {
        "firstName": "",
        "lastName": "",
        "address": "",
        "numbers": "",
        "serialDate": "",
        "region": "",
        "serial": "",
        "religion": "",
        "status": "",
        "deadline": "",
        "gender": "",
        "job": ""
    }
    return jsonify({'message': 'File uploaded successfully'}), 200


if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
