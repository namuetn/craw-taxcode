import easyocr
from pathlib import Path
import cv2
from PIL import Image


def bypass_captcha(dir_img, reader):
    total = len(dir_img)
    total_success = 0
    total_failure = 0
    for captcha in dir_img:
        file_name = captcha.split('/')[-1]
        label = file_name.split('.')[0]
        result = reader.readtext(captcha)
        for detection in result:
            if detection[1] == label:
                total_success += 1
                print(f'Success with {label} captcha: {total_success}/{total}')
            else:
                total_failure += 1
                print(f'Failure with {label} and {detection[1]} captcha: {total_failure}/{total}')

    percentage_success = (total_success/total) * 100
    print(f"Percentage of success: {int(percentage_success)}%")


def insert_white_background_image(dir_img):
    for captcha in dir_img:
        file_name = captcha.split('/')[-1]
        label = file_name.split('.')[0]

        image = cv2.imread(captcha)
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Áp dụng GaussianBlur để làm mờ ảnh
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                    cv2.THRESH_BINARY, 155, 122)

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

        cv2.imwrite(f'process_image_folder/{file_name}', binary)
    print('Preprocess captcha successfully')


if __name__ == '__main__':
    white_direc = Path('white_image_folder')    
    dir_white_img = sorted(list(map(str, list(white_direc.glob("*.png")))))
    
    process_direc = Path('process_image_folder') 
    if not process_direc.is_dir():
        process_direc.mkdir(parents=True, exist_ok=True)
        insert_white_background_image(dir_white_img)

    reader = easyocr.Reader(['en'])
    dir_process_img = sorted(list(map(str, list(process_direc.glob("*.png")))))
    bypass_captcha(dir_process_img, reader)



import ddddocr
from PIL import Image
from pathlib import Path

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



# ------------------------------------------------ ddddocr-------------------------------------------------------------------


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


if __name__ == '__main__':
    ocr = ddddocr.DdddOcr()
    # direc = Path('model_bypass_captcha/captcha_folder')
    # dir_img = sorted(list(map(str, list(direc.glob("*.png")))))

    # white_direc = Path('white_image_folder')
    # if not white_direc.is_dir():
    #     white_direc.mkdir(parents=True, exist_ok=True)
    #     insert_white_background_image(dir_img)    
    direc = Path('process_image_folder')
    dir_white_img = sorted(list(map(str, list(direc.glob("*.png")))))
    bypass_captcha(dir_white_img)