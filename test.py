import tensorflow as tf
import matplotlib.pyplot as plt

# Đường dẫn đến file ảnh
img_path = './model_bypass_captcha/captcha_folder/2226h.png'


# Đọc và giải mã ảnh
img = tf.io.read_file(img_path)
img = tf.io.decode_png(img, channels=1)

# Chuyển đổi ảnh thành float32
img = tf.image.convert_image_dtype(img, tf.float32)

# Kích thước ảnh gốc
img_shape = tf.shape(img)

# Tạo nền trắng
background = tf.ones([img_shape[0], img_shape[1], 1], dtype=tf.float32)

# Kết hợp ảnh gốc với nền trắng (nếu cần)
combined_img = tf.maximum(img, background)

# Hiển thị ảnh kết hợp
plt.imshow(tf.squeeze(combined_img), cmap='gray')
plt.axis('off')
plt.show()
