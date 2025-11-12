"""
로고가 포함된 알림 테스트
"""
import sys
import os
from PIL import Image, ImageDraw, ImageFont

# 현재 디렉토리를 Python 경로에 추가
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_sample_logo():
    """간단한 샘플 로고 생성"""
    # 128x128 크기의 이미지 생성
    img = Image.new('RGBA', (128, 128), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # 간단한 원과 텍스트 그리기
    draw.ellipse([10, 10, 118, 118], fill=(100, 150, 255, 255), outline=(50, 100, 200, 255), width=3)

    # 중앙에 텍스트 추가
    text = "CA"
    try:
        # 기본 폰트 사용
        font = ImageFont.truetype("arial.ttf", 48)
    except:
        # 폰트를 찾을 수 없으면 기본 폰트 사용
        font = ImageFont.load_default()

    # 텍스트 위치 계산
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (128 - text_width) // 2
    y = (128 - text_height) // 2

    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)

    # 이미지 저장
    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
    img.save(logo_path)
    print(f"샘플 로고가 생성되었습니다: {logo_path}")
    return logo_path

def test_with_logo():
    """로고가 포함된 알림 테스트"""
    from ocr_auto_approver import show_notification_popup

    # 로고 파일 확인
    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")

    if not os.path.exists(logo_path):
        print("로고 파일이 없습니다. 샘플 로고를 생성합니다...")
        create_sample_logo()
    else:
        print(f"기존 로고 파일을 사용합니다: {logo_path}")

    # 알림 표시
    print("\n로고가 포함된 알림을 표시합니다...")
    show_notification_popup(
        title="자동 승인 완료",
        message="승인이 성공적으로 처리되었습니다",
        window_info="PowerShell - Claude Auto Approver Test",
        duration=5
    )

    print("\n테스트 완료!")
    print("참고: 제공하신 귀여운 캐릭터 이미지를 logo.png로 저장하시면")
    print("      해당 이미지가 알림에 표시됩니다.")

if __name__ == "__main__":
    test_with_logo()