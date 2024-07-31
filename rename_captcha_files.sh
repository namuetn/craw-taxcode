img_path = './model_bypass_captcha/captcha_folder/2226h.png'
from PIL import Image

original_image = Image.open('captcha.png').convert("RGBA")

width, height = original_image.size

new_width = int(width * 1.2)
new_height = int(height * 1.2)

new_image = Image.new('RGBA', (new_width, new_height), (255, 255, 255, 255))

paste_position = ((new_width - width) // 2, (new_height - height) // 2)

new_image.paste(original_image, paste_position, original_image)

output_path = 'captcha_wb.png'
new_image.save(output_path)

new_image.show()
output_path
