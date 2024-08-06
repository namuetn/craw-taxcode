import cv2
import numpy as np

# Đọc ảnh
image = cv2.imread('./2aare_wb.png')
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# Áp dụng GaussianBlur để làm mờ ảnh
blurred = cv2.GaussianBlur(gray, (5, 5), 0)

# Sử dụng adaptive thresholding để tạo ảnh nhị phân
binary = cv2.adaptiveThreshold(blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                               cv2.THRESH_BINARY_INV, 151, 122)

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

# Lưu ảnh kết quả
cv2.imwrite('output_image.png', result)

# Hiển thị ảnh kết quả
# cv2.imshow('Result', result)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
