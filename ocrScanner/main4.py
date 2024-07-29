import json

from flask import Flask, jsonify, request, send_from_directory
import os
from flask_cors import CORS
from rembg import remove
import cv2
from PIL import ImageOps
import matplotlib.pyplot as plt
from ArabicOcr import arabicocr
from PIL import Image, ImageEnhance
import requests

app = Flask(__name__)
CORS(app)
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
    if index == 0:
        reg = regions
    else:
        reg = regions2
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
    threshold_image = enhanced_image.point(lambda p: 0 if p > 0 else 255)
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
    organize_ocr_to_json(outputPath, index)


@app.route('/upload', methods=['POST'])
def upload_file():
    if 'image1' not in request.files or 'image2' not in request.files:
        return 'Both images are required', 400

    image1 = request.files['image1']
    image2 = request.files['image2']

    image1.save(os.path.join('uploads', 'first.jpg'))
    image2.save(os.path.join('uploads', 'second.jpg'))

    processImage('uploads/first.jpg', 'output/first.png', 0)
    processImage('uploads/second.jpg', 'output/second.png', 1)
    print(user_model)
    spring_boot_url = 'http://localhost:8080/api/user/create'
    # Send POST request with JSON payload
    response = requests.post(spring_boot_url, json=user_model)
    print(response)
    globals()['user_model'] = {
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
    return jsonify({'message': 'File uploaded successfully'}), 200


regions3 = {
    # "country": [(0, 0), (500, 150)],
    # "id_type": [(500, 0), (1000, 150)],
    "serial": [(1100, 190), (1050, 295)],
    "lastName": [(440, 40), (1230, 35)],
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


def adjust_regions_based_on_start_point2(ocr_result, regions, start_string='PASSPORT'):
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


def get_field_name2(x, y, reg):
    for field, ((x1, y1), (x2, y2)) in reg.items():
        if x1 <= x <= x2 and y1 <= y <= y2:
            return field
    return None


def extract_fields2(ocr_results, index):
    # Sort the OCR results first by the x-coordinate of the center of each box (right to left)
    # and then by the y-coordinate (top to bottom) for boxes with the same x-coordinate
    ocr_results_sorted = sorted(ocr_results, key=lambda result: (
        -(result[0][0][0] + result[0][1][0] + result[0][2][0] + result[0][3][0]) / 4,  # negative for right to left
        (result[0][0][1] + result[0][1][1] + result[0][2][1] + result[0][3][1]) / 4  # top to bottom
    ))
    reg = adjust_regions_based_on_start_point2(ocr_results, regions3)
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


def organize_ocr_to_json2(image_path, index):
    out_image = "output/output-%i.png" % index
    results = arabicocr.arabic_ocr(image_path, out_image)
    print(results)
    fields = extract_fields2(results, index)
    for field, value in fields.items():
        user_model[field] = value
        print(f"{field}: {value}")


def transformImage2(path, index=0):
    ImageEnhance.Contrast(ImageOps.grayscale(Image.open(path))).enhance(1.9).point(lambda p: 0 if p > 0 else 255).save(
        path)
    image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    blurred = cv2.GaussianBlur(image, (3, 3), 0)
    cv2.imwrite(path, blurred)


def processImage2(path, outputPath, index):
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
    transformImage2(outputPath)
    organize_ocr_to_json2(outputPath, index)


@app.route('/uploadPassport', methods=['POST'])
def upload_file_passport():
    image1 = request.files['image1']

    image1.save(os.path.join('uploads', 'pass.jpg'))

    processImage2('uploads/pass.jpg', 'output/pass.png', 0)
    print(user_model)
    spring_boot_url = 'http://localhost:8080/api/user/create'
    # Send POST request with JSON payload
    response = requests.post(spring_boot_url, json=user_model)
    print(response)
    globals()['user_model'] = {
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
    return jsonify({'message': 'File uploaded successfully'}), 200


def transformType(path, threshold,crop):
    if crop:
       ImageEnhance.Contrast(ImageOps.grayscale(Image.open(path))).enhance(1.9).point(
           lambda p: 0 if p > threshold else 255).save(
           path)
    image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    blurred = cv2.GaussianBlur(image, (3, 3), 0)
    cv2.imwrite(path, blurred)


def ocr_Type(image_path):
    results = arabicocr.arabic_ocr(image_path, image_path)
    print(results)
    # fields = extract_fields2(results, index)
    # for field, value in fields.items():
    #     user_model[field] = value
    #     print(f"{field}: {value}")


def processingType(path, width, height, threshold,crop):
    desired_width = int(width)
    desired_height = int(height)
    if crop:
         input = Image.open(path)
         output = remove(input)
         output.save(path)
         image = cv2.imread(path)
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
         resized_image = cv2.resize(brightened_image, (desired_width, desired_height))
         cv2.imwrite(path, resized_image)
    else:
        image = cv2.imread(path)
        resized_image = cv2.resize(image, (desired_width, desired_height))
        cv2.imwrite(path, resized_image)
    transformType(path, int(threshold),crop)
    ocr_Type(path)


@app.route('/uploadType/<type_id>', methods=['POST'])
def upload_type(type_id):
    spring_boot_url = 'http://localhost:8080/api/type/' + type_id
    response = requests.get(spring_boot_url)
    content = response.content
    content_str = content.decode('utf-8')
    json_object = json.loads(content_str)
    print(json_object)
    image1 = request.files['image1']
    image1.save(os.path.join('uploads', f'{type_id}.png'))
    processingType(f'uploads/{type_id}.png', json_object['width'], json_object['height'], json_object['threshold'], json_object['crop'])

    return jsonify({'message': 'File uploaded successfully', 'path': f'uploads/{type_id}.png'}), 200


@app.route('/getImage/<id>', methods=['GET'])
def get_file(id):
    try:
        return send_from_directory('uploads', f'{id}.png')
    except FileNotFoundError:
        return jsonify({'message': 'File not found'}), 404


def transform_labels_to_regions(labels):
    regions = {
    }
    for label in labels:
        name = label['name']
        regions[name] = [
            (label['top_x'], label['top_y']),
            (label['bottom_x'], label['bottom_y'])
        ]

    return regions


def get_field_scan(x, y, reg):
    for field, ((x1, y1), (x2, y2)) in reg.items():
        if x1 <= x <= x2 and y1 <= y <= y2:
            return field
    return None


def extract_scan(ocr_results, regs):
    # Sort the OCR results first by the x-coordinate of the center of each box (right to left)
    # and then by the y-coordinate (top to bottom) for boxes with the same x-coordinate
    ocr_results_sorted = sorted(ocr_results, key=lambda result: (
        -(result[0][0][0] + result[0][1][0] + result[0][2][0] + result[0][3][0]) / 4,  # negative for right to left
        (result[0][0][1] + result[0][1][1] + result[0][2][1] + result[0][3][1]) / 4  # top to bottom
    ))
    fields = {key: "" for key in regs}
    for result in ocr_results_sorted:
        (box, text, confidence) = result
        x = (box[0][0] + box[1][0] + box[2][0] + box[3][0]) / 4
        y = (box[0][1] + box[1][1] + box[2][1] + box[3][1]) / 4
        field_name = get_field_scan(x, y, regs)
        if field_name:
            fields[field_name] += " " + text if fields[field_name] else text
    return fields


def organize_scan(image_path, regs):
    obj = {}
    results = arabicocr.arabic_ocr(image_path, image_path)
    fields = extract_scan(results, regs)
    for field, value in fields.items():
        obj[field] = value
        print(f"{field}: {value}")
    print(obj)
    return obj


def transformScan(path, threshold,crop):
    if crop:
        ImageEnhance.Contrast(ImageOps.grayscale(Image.open(path))).enhance(1.9).point(
            lambda p: 0 if p > threshold else 255).save(
            path)
    image = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    blurred = cv2.GaussianBlur(image, (3, 3), 0)
    cv2.imwrite(path, blurred)


def processingScan(path, width, height, threshold, regs,crop):
    desired_width = int(width)
    desired_height = int(height)
    if crop:
         input = Image.open(path)
         output = remove(input)
         output.save(path)
         image = cv2.imread(path)
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
         resized_image = cv2.resize(brightened_image, (desired_width, desired_height))
         cv2.imwrite(path, resized_image)
    else:
        image = cv2.imread(path)
        resized_image = cv2.resize(image, (desired_width, desired_height))
        cv2.imwrite(path, resized_image)
    transformScan(path, int(threshold),crop)
    return organize_scan(path, regs)


@app.route('/scan/<id>', methods=['POST'])
def scan(id):
    spring_boot_url = 'http://localhost:8080/api/type/' + id
    response = requests.get(spring_boot_url)
    content = response.content
    content_str = content.decode('utf-8')
    json_object = json.loads(content_str)
    print(json_object)
    image1 = request.files['image1']
    image1.save(os.path.join('uploads', f'{id}_scanner.png'))
    obj = processingScan(f'uploads/{id}_scanner.png', json_object['width'], json_object['height'], json_object['threshold'],
                   transform_labels_to_regions(json_object['labels']), json_object['crop'])

    return jsonify(obj), 200


if __name__ == '__main__':
    app.run(debug=True)

if __name__ == '__main__':
    if not os.path.exists('uploads'):
        os.makedirs('uploads')
    app.run(debug=True)
