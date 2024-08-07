import cv2
from PIL import Image

# Đọc ảnh
img_path = './model_bypass_captcha/captcha_folder/yhfhb.png'
output_path = 'yhfhb_wb.png'
original_image = Image.open(img_path).convert("RGBA")

width, height = original_image.size

new_width = int(width * 1.2)
new_height = int(height * 1.2)

new_image = Image.new('RGBA', (new_width, new_height), (255, 255, 255, 255))

paste_position = ((new_width - width) // 2, (new_height - height) // 2)

new_image.paste(original_image, paste_position, original_image)

new_image.save(output_path)


# - ------------------------------------------------------------
image = cv2.imread(output_path)
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Áp dụng GaussianBlur để làm mờ ảnh
blurred = cv2.GaussianBlur(gray, (5, 5), 0)
# blurred = cv2.medianBlur(image, 3) 
# Sử dụng adaptive thresholding để tạo ảnh nhị phân
binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                               cv2.THRESH_BINARY, 155, 140)

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

# # Lưu ảnh kết quả
cv2.imwrite(f'res_{output_path}', binary)

# Hiển thị ảnh kết quả
# cv2.imshow('Result', binary)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
