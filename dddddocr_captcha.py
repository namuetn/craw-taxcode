import ddddocr
from PIL import Image
from pathlib import Path
import cv2

def insert_white_background_image(dir_img):
    for captcha in dir_img:
        file_name = captcha.split('/')[-1]
        label = file_name.split('.')[0]

        output_path = f'./white_image_folder/{file_name}'
        original_image = Image.open(captcha).convert("RGBA")

        width, height = original_image.size

        new_width = int(width * 1.2)
        new_height = int(height * 1.2)

        new_image = Image.new('RGBA', (new_width, new_height), (255, 255, 255, 255))

        paste_position = ((new_width - width) // 2, (new_height - height) // 2)

        new_image.paste(original_image, paste_position, original_image)

        new_image.save(output_path)
    print('Insert while background captcha successfully')


def bypass_captcha(dir_img):
    total = len(dir_img)
    total_success = 0
    total_failure = 0
    for captcha in dir_img:
        file_name = captcha.split('/')[-1]
        label = file_name.split('.')[0]
        image = open(captcha, "rb").read()
        result = ocr.classification(image, png_fix=True)
        if result == label:
            total_success += 1
            print(f'Success with {label} captcha: {total_success}/{total}')
        else:
            total_failure += 1
            print(f'Failure with {label} captcha: {total_failure}/{total}')

    percentage_success = (total_success/total) * 100
    print(f"Percentage of success: {int(percentage_success)}%")


def preprocess_img(dir_img):
    for captcha in dir_img:
        file_name = captcha.split('/')[-1]
        label = file_name.split('.')[0]

        image = cv2.imread(captcha)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Áp dụng GaussianBlur để làm mờ ảnh
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        binary = cv2.adaptiveThreshold(blurred, 250, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                    cv2.THRESH_BINARY, 181, 129)

        # Dùng phép toán hình thái học để loại bỏ đường lưới
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        morph = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

        # Tìm và loại bỏ các đường lưới
        contours, _ = cv2.findContours(morph, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for contour in contours:
            if cv2.contourArea(contour) < 500:
                cv2.drawContours(binary, [contour], -1, (0, 0, 0), thickness=cv2.FILLED)

        # Sử dụng inpainting để khôi phục các vùng bị ảnh hưởng
        result = cv2.inpaint(image, binary, 3, cv2.INPAINT_TELEA)

        cv2.imwrite(f'./screenshots_pre/{file_name}', binary)
    print('Preprocess captcha successfully')

if __name__ == '__main__':
    ocr = ddddocr.DdddOcr()
    direc = Path('./screenshots')
    dir_img = sorted(list(map(str, list(direc.glob("*.png")))))

    pre_direc = Path('./screenshots_pre')
    if not pre_direc.is_dir():
        pre_direc.mkdir(parents=True, exist_ok=True)
    preprocess_img(dir_img)    
    direc = Path('./screenshots_pre')
    dir_white_img = sorted(list(map(str, list(direc.glob("*.png")))))
    bypass_captcha(dir_white_img)