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