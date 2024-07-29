from rembg import remove
import cv2
from PIL import Image, ImageOps, ImageEnhance
import matplotlib.pyplot as plt
from ArabicOcr import arabicocr
from spellchecker import SpellChecker
import numpy as np
from PIL import Image, ImageEnhance


def calculate_brightness(image):
    grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return np.mean(grayscale_image)


def calculate_contrast(image):
    grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return grayscale_image.std()


def choose_threshold(image):
    brightness = calculate_brightness(image)
    contrast = calculate_contrast(image)

    # Basic heuristic for choosing a threshold based on brightness and contrast
    if brightness < 100:
        threshold = 0
    elif brightness > 200:
        threshold = 100
    else:
        if contrast < 100:
            threshold = 0
        else:
            threshold = 100

    return threshold


regions = {
    "country": [(0, 0), (500, 150)],
    "id_type": [(500, 0), (1000, 150)],
    "serial": [(350, 150), (850, 250)],
    "lastName": [(450, 260), (890, 360)],
    "firstName": [(650, 320), (896, 400)],
    "full_name": [(500, 250), (1000, 350)],
    "dob_label": [(0, 350), (500, 450)],
    "birthday": [(430, 440), (985, 502)],
    "dob_month": [(700, 350), (850, 450)],
    "dob_year": [(850, 350), (1000, 450)],
    "birthplace": [(520, 480), (980, 550)],
    # "mother": [(190, 40), (960, 140)],
    # "job": [(184, 114), (694, 180)],
    # "serialPrint": [(693, 400), (946, 474)],
    # "dateExport": [(23, 301), (480, 381)],
    # "address": [(40, 180), (680, 310)],
}
regions2 = {
    "mother": [(190, 40), (960, 140)],
    "job": [(184, 114), (694, 180)],
    "serialPrint": [(693, 400), (946, 474)],
    "serialDate": [(23, 301), (480, 381)],
    "address": [(40, 180), (680, 310)],
}

user_model = {
    "firstName": "",
    "lastName": "",
    "birthplace": "",
    "birthday": "",
    "address": "",
    "numbers": "",
    "serialDate": "",
    "region": "",
    "serial": "",
    "religion": "",
    "status": "",
    "deadline": "",
    "gender": "",
    "job": "",
    "mother": "",
    "dateExport": "",
    "serialPrint": "",
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


def get_field_name(x, y,reg):
    for field, ((x1, y1), (x2, y2)) in reg.items():
        if x1 <= x <= x2 and y1 <= y <= y2:
            return field
    return None


def extract_fields(ocr_results, index):
    # Sort the OCR results first by the x-coordinate of the center of each box (right to left)
    # and then by the y-coordinate (top to bottom) for boxes with the same x-coordinate
    ocr_results_sorted = sorted(ocr_results, key=lambda result: (
        -(result[0][0][0] + result[0][1][0] + result[0][2][0] + result[0][3][0]) / 4,  # negative for right to left
        (result[0][0][1] + result[0][1][1] + result[0][2][1] + result[0][3][1]) / 4  # top to bottom
    ))
    if index == 0:
        reg = regions
    else:
        reg = regions2
    fields = {key: "" for key in reg}
    for result in ocr_results_sorted:
        (box, text, confidence) = result
        x = (box[0][0] + box[1][0] + box[2][0] + box[3][0]) / 4
        y = (box[0][1] + box[1][1] + box[2][1] + box[3][1]) / 4
        field_name = get_field_name(x, y,reg)
        if field_name:
            fields[field_name] += " " + text if fields[field_name] else text
    return fields


def organize_ocr_to_json(image_path, index):
    out_image = "output/output-%i.png" % index
    results = arabicocr.arabic_ocr(image_path, out_image)
    print(results)
    fields = extract_fields(results,index)
    for field, value in fields.items():
        user_model[field] = value
        print(f"{field}: {value}")


def show_image(window_title, image):
    plt.imshow(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    plt.title(window_title)
    plt.axis('off')
    plt.show()


def transformImage(path, index=0):
    image = Image.open(path)
    gray_image = ImageOps.grayscale(image)
    enhancer = ImageEnhance.Contrast(gray_image)
    enhanced_image = enhancer.enhance(1.9)
    threshold_image = enhanced_image.point(lambda p: 255 if p > 0 else 0)
    threshold_image.save(path)
    image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    blurred = cv2.GaussianBlur(image, (1, 1), 0)
    cv2.imwrite(path, blurred)


def processImage(path, outputPath, index):
    input = Image.open(path)
    output = remove(input)
    output.save(outputPath)
    image = cv2.imread(outputPath)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    largest_contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(largest_contour)
    cropped_image = image[y:y + h, x:x + w]
    lab_image = cv2.cvtColor(cropped_image, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab_image)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    cl_l_channel = clahe.apply(l_channel)
    merged_lab = cv2.merge((cl_l_channel, a_channel, b_channel))
    brightened_image = cv2.cvtColor(merged_lab, cv2.COLOR_LAB2BGR)
    desired_width = 1000
    desired_height = 600
    resized_image = cv2.resize(brightened_image, (desired_width, desired_height))
    cv2.imwrite(outputPath, resized_image)
    transformImage(outputPath)
    organize_ocr_to_json(outputPath,index)


processImage('input/fac.jpg', 'output/facRM.png', 0)
processImage('input/der.jpg', 'output/facRM.png', 1)
print(user_model)