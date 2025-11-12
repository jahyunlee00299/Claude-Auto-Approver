"""
승인 아이콘 생성 - 제공된 귀여운 캐릭터 재현
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_approval_icon():
    """제공된 귀여운 캐릭터와 유사한 아이콘 생성"""
    # 128x128 크기의 투명 배경 이미지
    img = Image.new('RGBA', (128, 128), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # 색상 정의
    black = (50, 50, 50, 255)
    white = (255, 255, 255, 255)
    pink = (255, 192, 203, 255)  # 분홍색 볼

    # 머리/얼굴 (둥근 사각형처럼)
    # 머리 윤곽
    head_top = 25
    head_bottom = 75
    head_left = 35
    head_right = 93

    # 머리 그리기 (둥근 모양)
    draw.ellipse([head_left, head_top, head_right, head_bottom],
                 fill=white, outline=black, width=3)

    # 귀 왼쪽 (둥근 형태)
    ear_left_x = head_left + 5
    ear_left_y = head_top - 5
    draw.ellipse([ear_left_x, ear_left_y, ear_left_x + 20, ear_left_y + 25],
                 fill=white, outline=black, width=3)

    # 귀 오른쪽
    ear_right_x = head_right - 25
    ear_right_y = head_top - 5
    draw.ellipse([ear_right_x, ear_right_y, ear_right_x + 20, ear_right_y + 25],
                 fill=white, outline=black, width=3)

    # 눈 (작은 검은 점)
    eye_y = head_top + 20
    # 왼쪽 눈
    draw.ellipse([head_left + 18, eye_y, head_left + 25, eye_y + 7], fill=black)
    # 오른쪽 눈
    draw.ellipse([head_right - 25, eye_y, head_right - 18, eye_y + 7], fill=black)

    # 핑크색 볼
    cheek_y = eye_y + 10
    # 왼쪽 볼
    draw.ellipse([head_left + 10, cheek_y, head_left + 25, cheek_y + 12],
                 fill=pink, outline=None)
    # 오른쪽 볼
    draw.ellipse([head_right - 25, cheek_y, head_right - 10, cheek_y + 12],
                 fill=pink, outline=None)

    # 코와 입 (w 모양)
    nose_x = 64
    nose_y = eye_y + 12
    # 작은 코
    draw.ellipse([nose_x - 2, nose_y, nose_x + 2, nose_y + 3], fill=black)
    # W 모양 입
    draw.arc([nose_x - 8, nose_y + 2, nose_x - 2, nose_y + 8],
             start=0, end=180, fill=black, width=2)
    draw.arc([nose_x + 2, nose_y + 2, nose_x + 8, nose_y + 8],
             start=0, end=180, fill=black, width=2)

    # 몸통 (네모난 옷/판초 모양)
    body_top = head_bottom - 10
    body_bottom = 100
    body_left = head_left - 10
    body_right = head_right + 10

    # 몸통 그리기 (직사각형 형태의 옷)
    points = [
        (body_left, body_top),
        (body_right, body_top),
        (body_right + 5, body_bottom),
        (body_left - 5, body_bottom)
    ]
    draw.polygon(points, fill=white, outline=black, width=3)

    # 왼팔 (위로 든 팔)
    arm_left_x = body_left - 8
    arm_left_y = body_top - 10
    draw.ellipse([arm_left_x - 12, arm_left_y - 5, arm_left_x + 5, arm_left_y + 15],
                 fill=white, outline=black, width=2)

    # 오른팔
    arm_right_x = body_right + 8
    arm_right_y = body_top + 5
    draw.ellipse([arm_right_x - 5, arm_right_y, arm_right_x + 12, arm_right_y + 20],
                 fill=white, outline=black, width=2)

    # 다리/발
    # 왼쪽 다리
    leg_left_x = head_left + 15
    draw.ellipse([leg_left_x, body_bottom - 5, leg_left_x + 12, body_bottom + 10],
                 fill=white, outline=black, width=2)

    # 오른쪽 다리
    leg_right_x = head_right - 27
    draw.ellipse([leg_right_x, body_bottom - 5, leg_right_x + 12, body_bottom + 10],
                 fill=white, outline=black, width=2)

    # 반짝임 효과 (작은 원과 선)
    # 왼쪽 위 반짝임
    sparkle_x = arm_left_x - 10
    sparkle_y = arm_left_y - 10
    # 작은 원
    draw.ellipse([sparkle_x - 3, sparkle_y - 3, sparkle_x + 3, sparkle_y + 3],
                 fill=(255, 220, 0, 200))
    # 십자 모양 반짝임
    draw.line([(sparkle_x - 6, sparkle_y), (sparkle_x + 6, sparkle_y)],
              fill=(255, 220, 0, 150), width=1)
    draw.line([(sparkle_x, sparkle_y - 6), (sparkle_x, sparkle_y + 6)],
              fill=(255, 220, 0, 150), width=1)

    # 이미지 저장
    icon_path = os.path.join(os.path.dirname(__file__), "approval_icon.png")
    img.save(icon_path)
    print(f"승인 아이콘이 생성되었습니다: {icon_path}")
    return icon_path

if __name__ == "__main__":
    create_approval_icon()
    print("\napproval_icon.png가 성공적으로 생성되었습니다!")
    print("이제 알림에 귀여운 캐릭터 아이콘이 표시됩니다.")