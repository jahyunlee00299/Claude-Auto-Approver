"""
귀여운 캐릭터 로고 생성
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_cute_character_logo():
    """귀여운 캐릭터 로고 생성"""
    # 128x128 크기의 투명 배경 이미지 생성
    img = Image.new('RGBA', (128, 128), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # 색상 정의
    white = (255, 255, 255, 255)
    black = (60, 60, 60, 255)
    pink = (255, 182, 193, 255)
    light_gray = (245, 245, 245, 255)

    # 몸체 (큰 원)
    body_bounds = [25, 35, 103, 113]
    draw.ellipse(body_bounds, fill=white, outline=black, width=2)

    # 귀 (왼쪽)
    left_ear = [30, 20, 55, 50]
    draw.ellipse(left_ear, fill=white, outline=black, width=2)

    # 귀 (오른쪽)
    right_ear = [73, 20, 98, 50]
    draw.ellipse(right_ear, fill=white, outline=black, width=2)

    # 눈 (왼쪽)
    left_eye = [45, 55, 52, 62]
    draw.ellipse(left_eye, fill=black)

    # 눈 (오른쪽)
    right_eye = [76, 55, 83, 62]
    draw.ellipse(right_eye, fill=black)

    # 볼 (왼쪽) - 핑크색
    left_cheek = [35, 65, 50, 80]
    draw.ellipse(left_cheek, fill=pink, outline=None)

    # 볼 (오른쪽) - 핑크색
    right_cheek = [78, 65, 93, 80]
    draw.ellipse(right_cheek, fill=pink, outline=None)

    # 코
    nose_x, nose_y = 64, 70
    draw.ellipse([nose_x-3, nose_y-3, nose_x+3, nose_y+3], fill=black)

    # 입 (W 모양)
    draw.line([(nose_x, nose_y+2), (nose_x-5, nose_y+5)], fill=black, width=2)
    draw.line([(nose_x, nose_y+2), (nose_x+5, nose_y+5)], fill=black, width=2)

    # 팔 (왼쪽) - 올려진 팔
    draw.ellipse([15, 50, 35, 70], fill=white, outline=black, width=2)
    # 손 부분
    draw.ellipse([10, 45, 25, 60], fill=white, outline=black, width=2)

    # 팔 (오른쪽)
    draw.ellipse([93, 60, 113, 80], fill=white, outline=black, width=2)

    # 발 (왼쪽)
    draw.ellipse([40, 95, 55, 110], fill=white, outline=black, width=2)

    # 발 (오른쪽)
    draw.ellipse([73, 95, 88, 110], fill=white, outline=black, width=2)

    # 작은 원으로 장식 추가 (반짝임 효과)
    sparkle_color = (255, 223, 0, 180)
    # 왼쪽 위
    draw.ellipse([18, 28, 24, 34], fill=sparkle_color)
    # 오른쪽 위
    draw.ellipse([105, 38, 111, 44], fill=sparkle_color)
    # 왼쪽 아래
    draw.ellipse([22, 85, 28, 91], fill=sparkle_color)

    # 이미지 저장
    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
    img.save(logo_path)
    print(f"귀여운 캐릭터 로고가 생성되었습니다: {logo_path}")
    return logo_path

if __name__ == "__main__":
    create_cute_character_logo()
    print("\n로고가 성공적으로 생성되었습니다!")
    print("이제 알림에 귀여운 캐릭터가 표시됩니다.")