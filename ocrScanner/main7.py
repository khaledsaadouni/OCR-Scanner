from rembg import remove
import cv2
from PIL import Image, ImageOps, ImageEnhance
import matplotlib.pyplot as plt
from ArabicOcr import arabicocr
from spellchecker import SpellChecker
import numpy as np
from PIL import Image, ImageEnhance


user_model = {
    "fullName": "",
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


regions = {
    # "country": [(0, 0), (500, 150)],
    # "id_type": [(500, 0), (1000, 150)],
    # "serial": [(350, 150), (850, 250)],
    "lastName": [(440, 40), (1172, 35)],
    "firstName": [(440, 100), (1172, 100)],
    "nationality": [(440, 165), (700, 170)],
    "gender": [(440, 305), (323, 330)],
    "birthday": [(440, 235), (532, 240)],
    # "dob_month": [(700, 350), (850, 450)],
    # "dob_year": [(850, 350), (1000, 450)],
    # "birthplace": [(850, 783), (1231, 845)],
    # # "mother": [(190, 40), (960, 140)],
    "job": [(1038, 125), (1318, 170)],
    # # "serialPrint": [(693, 400), (946, 474)],
    # # "dateExport": [(23, 301), (480, 381)],
    # # "address": [(40, 180), (680, 310)],
    # # "address": [(40, 180), (680, 310)],
    "fullName": [(783, -16), (1350, 50)],
}


def adjust_regions_based_on_start_point(ocr_result, regions, start_string='PASSPORT'):
    # Find the bounding box containing the start string
    start_bbox = None
    for result in ocr_result:
        if start_string in result[1]:
            start_bbox = result[0]
            break

    if not start_bbox:
        raise ValueError(f"Start string '{start_string}' not found in OCR results.")

    # Extract top-left and bottom-right coordinates of the start string bounding box
    start_top_left = start_bbox[0]
    start_bottom_right = start_bbox[2]

    start_x1, start_y1 = start_top_left
    start_x2, start_y2 = start_bottom_right

    # Calculate the offset
    offset_x1 = start_x1
    offset_y1 = start_y1
    offset_x2 = start_x2
    offset_y2 = start_y2

    # Adjust the coordinates of the regions
    adjusted_regions = {}
    for key, (top_left, bottom_right) in regions.items():
        new_top_left = (top_left[0] + offset_x1, top_left[1] + offset_y1)
        new_bottom_right = (bottom_right[0] + offset_x2, bottom_right[1] + offset_y2)
        adjusted_regions[key] = [new_top_left, new_bottom_right]

    return adjusted_regions
def get_field_name(x, y, reg):
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
    reg = adjust_regions_based_on_start_point(ocr_results,regions)
    print(reg)
    fields = {key: "" for key in reg}
    for result in ocr_results_sorted:
        (box, text, confidence) = result
        x = (box[0][0] + box[1][0] + box[2][0] + box[3][0]) / 4
        y = (box[0][1] + box[1][1] + box[2][1] + box[3][1]) / 4
        field_name = get_field_name(x, y, reg)
        if field_name:
            fields[field_name] += " " + text if fields[field_name] else text
    return fields


def organize_ocr_to_json(image_path, index):
    out_image = "output/output-%i.png" % index
    results = arabicocr.arabic_ocr(image_path, out_image)
    print(results)
    fields = extract_fields(results, index)
    for field, value in fields.items():
        user_model[field] = value
        print(f"{field}: {value}")


def transformImage(path, index=0):
    ImageEnhance.Contrast(ImageOps.grayscale(Image.open(path))).enhance(1.8).point(lambda p: 0 if p >0 else 255).save(
        path)
    image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    blurred = cv2.GaussianBlur(image, (3, 3), 0)
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
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(4, 4))
    cl_l_channel = clahe.apply(l_channel)
    merged_lab = cv2.merge((cl_l_channel, a_channel, b_channel))
    brightened_image = cv2.cvtColor(merged_lab, cv2.COLOR_LAB2BGR)
    desired_width = 1700
    desired_height = 1200
    resized_image = cv2.resize(brightened_image, (desired_width, desired_height))
    cv2.imwrite(outputPath, resized_image)
    transformImage(outputPath)
    organize_ocr_to_json(outputPath, index)


processImage('input/pass1.jpg', 'output/pass1.png', 0)
processImage('input/pass2.jpg', 'output/pass2.png', 1)
processImage('input/pass3.jpg', 'output/pass3.png', 2)
