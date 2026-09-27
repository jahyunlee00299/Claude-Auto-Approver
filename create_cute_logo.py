"""
Generate a cute character logo
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_cute_character_logo():
    """Generate a cute character logo"""
    # Create a 128x128 transparent-background image
    img = Image.new('RGBA', (128, 128), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # Color definitions
    white = (255, 255, 255, 255)
    black = (60, 60, 60, 255)
    pink = (255, 182, 193, 255)
    light_gray = (245, 245, 245, 255)

    # Body (big circle)
    body_bounds = [25, 35, 103, 113]
    draw.ellipse(body_bounds, fill=white, outline=black, width=2)

    # Ear (left)
    left_ear = [30, 20, 55, 50]
    draw.ellipse(left_ear, fill=white, outline=black, width=2)

    # Ear (right)
    right_ear = [73, 20, 98, 50]
    draw.ellipse(right_ear, fill=white, outline=black, width=2)

    # Eye (left)
    left_eye = [45, 55, 52, 62]
    draw.ellipse(left_eye, fill=black)

    # Eye (right)
    right_eye = [76, 55, 83, 62]
    draw.ellipse(right_eye, fill=black)

    # Cheek (left) - pink
    left_cheek = [35, 65, 50, 80]
    draw.ellipse(left_cheek, fill=pink, outline=None)

    # Cheek (right) - pink
    right_cheek = [78, 65, 93, 80]
    draw.ellipse(right_cheek, fill=pink, outline=None)

    # Nose
    nose_x, nose_y = 64, 70
    draw.ellipse([nose_x-3, nose_y-3, nose_x+3, nose_y+3], fill=black)

    # Mouth (W shape)
    draw.line([(nose_x, nose_y+2), (nose_x-5, nose_y+5)], fill=black, width=2)
    draw.line([(nose_x, nose_y+2), (nose_x+5, nose_y+5)], fill=black, width=2)

    # Arm (left) - raised arm
    draw.ellipse([15, 50, 35, 70], fill=white, outline=black, width=2)
    # Hand part
    draw.ellipse([10, 45, 25, 60], fill=white, outline=black, width=2)

    # Arm (right)
    draw.ellipse([93, 60, 113, 80], fill=white, outline=black, width=2)

    # Foot (left)
    draw.ellipse([40, 95, 55, 110], fill=white, outline=black, width=2)

    # Foot (right)
    draw.ellipse([73, 95, 88, 110], fill=white, outline=black, width=2)

    # Add small circles as decoration (sparkle effect)
    sparkle_color = (255, 223, 0, 180)
    # Top left
    draw.ellipse([18, 28, 24, 34], fill=sparkle_color)
    # Top right
    draw.ellipse([105, 38, 111, 44], fill=sparkle_color)
    # Bottom left
    draw.ellipse([22, 85, 28, 91], fill=sparkle_color)

    # Save image
    logo_path = os.path.join(os.path.dirname(__file__), "logo.png")
    img.save(logo_path)
    print(f"귀여운 캐릭터 로고가 생성되었습니다: {logo_path}")
    return logo_path

if __name__ == "__main__":
    create_cute_character_logo()
    print("\n로고가 성공적으로 생성되었습니다!")
    print("이제 알림에 귀여운 캐릭터가 표시됩니다.")
