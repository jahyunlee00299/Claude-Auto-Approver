"""
Copy and resize the original image to approval_icon.png
"""
from PIL import Image
import shutil
import os
import sys

def copy_and_resize_icon():
    """Copy the actual image file and resize it"""

    # Original image path: determined by CLI arg > env var > default (local icon.png)
    source_path = (
        sys.argv[1] if len(sys.argv) > 1
        else os.environ.get("ICON_SOURCE_PATH", os.path.join(os.path.dirname(__file__), "icon.png"))
    )

    # Target paths
    target_path = os.path.join(os.path.dirname(__file__), "approval_icon.png")
    target_path_128 = os.path.join(os.path.dirname(__file__), "approval_icon_128.png")
    target_path_64 = os.path.join(os.path.dirname(__file__), "approval_icon_64.png")

    try:
        # Check the source file
        if not os.path.exists(source_path):
            print(f"원본 파일을 찾을 수 없습니다: {source_path}")
            return False

        print(f"원본 파일 발견: {source_path}")

        # 1. Copy the original as-is
        shutil.copy2(source_path, target_path)
        print(f"[OK] 원본 크기로 복사 완료: {target_path}")

        # 2. Open the image
        img = Image.open(source_path)
        print(f"  원본 크기: {img.size}")

        # Convert to RGBA to handle transparent background
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # 3. Resize to 128x128 (for notifications)
        img_128 = img.resize((128, 128), Image.Resampling.LANCZOS)
        img_128.save(target_path_128)
        print(f"[OK] 128x128 리사이즈 완료: {target_path_128}")

        # 4. Resize to 64x64 (for the small icon)
        img_64 = img.resize((64, 64), Image.Resampling.LANCZOS)
        img_64.save(target_path_64)
        print(f"[OK] 64x64 리사이즈 완료: {target_path_64}")

        # 5. Replace the main approval_icon.png with the 128x128 version
        img_128.save(target_path)
        print(f"[OK] 메인 아이콘을 128x128 버전으로 업데이트: {target_path}")

        print("\n성공적으로 완료되었습니다!")
        print("귀여운 캐릭터 아이콘이 준비되었습니다.")

        return True

    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = copy_and_resize_icon()
    if success:
        print("\n이제 알림에 실제 귀여운 캐릭터가 표시됩니다!")
    else:
        print("\n이미지 복사 중 문제가 발생했습니다.")