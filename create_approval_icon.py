"""
Generate the approval icon - recreates the provided cute character
"""
from PIL import Image, ImageDraw, ImageFont
import os

def create_approval_icon():
    """Generate an icon similar to the provided cute character"""
    # 128x128 transparent-background image
    img = Image.new('RGBA', (128, 128), (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)

    # Color definitions
    black = (50, 50, 50, 255)
    white = (255, 255, 255, 255)
    pink = (255, 192, 203, 255)  # pink cheeks

    # Head/face (rounded-rectangle-like)
    # Head outline
    head_top = 25
    head_bottom = 75
    head_left = 35
    head_right = 93

    # Draw the head (rounded shape)
    draw.ellipse([head_left, head_top, head_right, head_bottom],
                 fill=white, outline=black, width=3)

    # Left ear (rounded shape)
    ear_left_x = head_left + 5
    ear_left_y = head_top - 5
    draw.ellipse([ear_left_x, ear_left_y, ear_left_x + 20, ear_left_y + 25],
                 fill=white, outline=black, width=3)

    # Right ear
    ear_right_x = head_right - 25
    ear_right_y = head_top - 5
    draw.ellipse([ear_right_x, ear_right_y, ear_right_x + 20, ear_right_y + 25],
                 fill=white, outline=black, width=3)

    # Eyes (small black dots)
    eye_y = head_top + 20
    # Left eye
    draw.ellipse([head_left + 18, eye_y, head_left + 25, eye_y + 7], fill=black)
    # Right eye
    draw.ellipse([head_right - 25, eye_y, head_right - 18, eye_y + 7], fill=black)

    # Pink cheeks
    cheek_y = eye_y + 10
    # Left cheek
    draw.ellipse([head_left + 10, cheek_y, head_left + 25, cheek_y + 12],
                 fill=pink, outline=None)
    # Right cheek
    draw.ellipse([head_right - 25, cheek_y, head_right - 10, cheek_y + 12],
                 fill=pink, outline=None)

    # Nose and mouth (w shape)
    nose_x = 64
    nose_y = eye_y + 12
    # Small nose
    draw.ellipse([nose_x - 2, nose_y, nose_x + 2, nose_y + 3], fill=black)
    # W-shaped mouth
    draw.arc([nose_x - 8, nose_y + 2, nose_x - 2, nose_y + 8],
             start=0, end=180, fill=black, width=2)
    draw.arc([nose_x + 2, nose_y + 2, nose_x + 8, nose_y + 8],
             start=0, end=180, fill=black, width=2)

    # Body (square clothing/poncho shape)
    body_top = head_bottom - 10
    body_bottom = 100
    body_left = head_left - 10
    body_right = head_right + 10

    # Draw the body (rectangular clothing shape)
    points = [
        (body_left, body_top),
        (body_right, body_top),
        (body_right + 5, body_bottom),
        (body_left - 5, body_bottom)
    ]
    draw.polygon(points, fill=white, outline=black, width=3)

    # Left arm (raised arm)
    arm_left_x = body_left - 8
    arm_left_y = body_top - 10
    draw.ellipse([arm_left_x - 12, arm_left_y - 5, arm_left_x + 5, arm_left_y + 15],
                 fill=white, outline=black, width=2)

    # Right arm
    arm_right_x = body_right + 8
    arm_right_y = body_top + 5
    draw.ellipse([arm_right_x - 5, arm_right_y, arm_right_x + 12, arm_right_y + 20],
                 fill=white, outline=black, width=2)

    # Legs/feet
    # Left leg
    leg_left_x = head_left + 15
    draw.ellipse([leg_left_x, body_bottom - 5, leg_left_x + 12, body_bottom + 10],
                 fill=white, outline=black, width=2)

    # Right leg
    leg_right_x = head_right - 27
    draw.ellipse([leg_right_x, body_bottom - 5, leg_right_x + 12, body_bottom + 10],
                 fill=white, outline=black, width=2)

    # Sparkle effect (small circle and lines)
    # Top-left sparkle
    sparkle_x = arm_left_x - 10
    sparkle_y = arm_left_y - 10
    # Small circle
    draw.ellipse([sparkle_x - 3, sparkle_y - 3, sparkle_x + 3, sparkle_y + 3],
                 fill=(255, 220, 0, 200))
    # Cross-shaped sparkle
    draw.line([(sparkle_x - 6, sparkle_y), (sparkle_x + 6, sparkle_y)],
              fill=(255, 220, 0, 150), width=1)
    draw.line([(sparkle_x, sparkle_y - 6), (sparkle_x, sparkle_y + 6)],
              fill=(255, 220, 0, 150), width=1)

    # Save the image
    icon_path = os.path.join(os.path.dirname(__file__), "approval_icon.png")
    img.save(icon_path)
    print(f"승인 아이콘이 생성되었습니다: {icon_path}")
    return icon_path

if __name__ == "__main__":
    create_approval_icon()
    print("\napproval_icon.png가 성공적으로 생성되었습니다!")
    print("이제 알림에 귀여운 캐릭터 아이콘이 표시됩니다.")