"""
Resize the icon larger
"""
from PIL import Image
import os
import sys

def resize_icon_larger():
    """Resize the icon to a larger size"""

    # Source image path: determined by CLI arg > env var > default (local icon.png)
    source_path = (
        sys.argv[1] if len(sys.argv) > 1
        else os.environ.get("ICON_SOURCE_PATH", os.path.join(os.path.dirname(__file__), "icon.png"))
    )

    # Target paths
    target_path = os.path.join(os.path.dirname(__file__), "approval_icon.png")
    target_path_256 = os.path.join(os.path.dirname(__file__), "approval_icon_256.png")
    target_path_512 = os.path.join(os.path.dirname(__file__), "approval_icon_512.png")

    try:
        # Check source file
        if not os.path.exists(source_path):
            print(f"원본 파일을 찾을 수 없습니다: {source_path}")
            return False

        print(f"원본 파일 발견: {source_path}")

        # Open image
        img = Image.open(source_path)
        print(f"  원본 크기: {img.size}")

        # Convert to RGBA for transparent background handling
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # 1. Resize to 256x256 (for large notifications)
        img_256 = img.resize((256, 256), Image.Resampling.LANCZOS)
        img_256.save(target_path_256)
        print(f"[OK] 256x256 리사이즈 완료: {target_path_256}")

        # 2. Resize to 512x512 (for very large notifications)
        img_512 = img.resize((512, 512), Image.Resampling.LANCZOS)
        img_512.save(target_path_512)
        print(f"[OK] 512x512 리사이즈 완료: {target_path_512}")

        # 3. Replace the main approval_icon.png with the 256x256 version
        img_256.save(target_path)
        print(f"[OK] 메인 아이콘을 256x256 버전으로 업데이트: {target_path}")

        print("\n성공적으로 완료되었습니다!")
        print("아이콘이 더 크게 표시됩니다.")

        return True

    except Exception as e:
        print(f"오류 발생: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = resize_icon_larger()
    if success:
        print("\n이제 알림에 더 큰 아이콘이 표시됩니다!")
    else:
        print("\n이미지 리사이즈 중 문제가 발생했습니다.")