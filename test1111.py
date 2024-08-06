import requests
from bs4 import BeautifulSoup

# Gửi yêu cầu đến trang web
url = 'https://example.com'
response = requests.get(url)

# Lấy cookie từ phản hồi
cookies = response.cookies

# In ra các cookie
for cookie in cookies:
    print(f'{cookie.name}: {cookie.value}')

# Sử dụng Beautiful Soup để phân tích HTML
soup = BeautifulSoup(response.text, 'html.parser')

# Ví dụ: In ra tiêu đề trang
print(soup.title.text)