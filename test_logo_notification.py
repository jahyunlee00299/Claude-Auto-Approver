"""
Notification test with logo included
"""
import sys
import os
from PIL import Image, ImageDraw, ImageFont

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def create_sample_logo():
    """Generate a simple sample logo"""
    # Create a 128x128 sized image
    img = Image.new('RGBA', (128, 128), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # Draw a simple circle and text
    draw.ellipse([10, 10, 118, 118], fill=(100, 150, 255, 255), outline=(50, 100, 200, 255), width=3)

    # Add text in the center
    text = "CA"
    try:
        # Use default font
        font = ImageFont.truetype("arial.ttf", 48)
    except:
        # Fall back to the default font if not found
        font = ImageFont.load_default()

    # Calculate text position
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (128 - text_width) // 2
    y = (128 - text_height) // 2

    draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)

    # Save the image
    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
    img.save(logo_path)
    print(f"샘플 로고가 생성되었습니다: {logo_path}")
    return logo_path

def test_with_logo():
    """Notification test with logo included"""
    from ocr_auto_approver import show_notification_popup

    # Check logo file
    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")

    if not os.path.exists(logo_path):
        print("로고 파일이 없습니다. 샘플 로고를 생성합니다...")
        create_sample_logo()
    else:
        print(f"기존 로고 파일을 사용합니다: {logo_path}")

    # Show notification
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