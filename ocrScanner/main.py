import cv2
import fitz
import json
from ArabicOcr import arabicocr
from PIL import Image, ImageOps, ImageEnhance

user_model = {
    "firstname": "",
    "lastname": "",
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
                user_model["firstname"] += f" {text}"
            elif within_region(center_point, lastname_region):
                user_model["lastname"] += f" {text}"
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


def transformImage(path,index = 0):
    image = Image.open(path)
    gray_image = ImageOps.grayscale(image)
    enhancer = ImageEnhance.Contrast(gray_image)
    enhanced_image = enhancer.enhance(2.0)
    thresh = 5
    threshold_image = enhanced_image.point(lambda p: 0 if p > thresh else 255)
    threshold_image.save(path)
    image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    blurred = cv2.GaussianBlur(image, (1, 1), 0)
    cv2.imwrite(path, blurred)


pdf = "CIN.pdf"
paths = []
doc = fitz.open(pdf)
for page in doc:
    pix = page.get_pixmap()
    pix.save("page-%i.png" % page.number)
    paths.append("page-%i.png" % page.number)

for index, p in enumerate(paths):
    transformImage(p,index)
    json_result = organize_ocr_to_json(p,index)

print(user_model)
