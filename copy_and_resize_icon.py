"""
OneDrive의 실제 이미지를 approval_icon.png로 복사 및 리사이즈
"""
from PIL import Image
import shutil
import os

def copy_and_resize_icon():
    """실제 이미지 파일을 복사하고 리사이즈"""

    # 원본 이미지 경로
    source_path = r"C:\Users\Jahyun\OneDrive - 호서대학교\바탕 화면 [Labtop]\9dc14126ee3e2d16b00d0a503b592cbb8b566dca82634c93f811198148a26065.png"

    # 대상 경로
    target_path = os.path.join(os.path.dirname(__file__), "approval_icon.png")
    target_path_128 = os.path.join(os.path.dirname(__file__), "approval_icon_128.png")
    target_path_64 = os.path.join(os.path.dirname(__file__), "approval_icon_64.png")

    try:
        # 원본 파일 확인
        if not os.path.exists(source_path):
            print(f"원본 파일을 찾을 수 없습니다: {source_path}")
            return False

        print(f"원본 파일 발견: {source_path}")

        # 1. 원본 그대로 복사
        shutil.copy2(source_path, target_path)
        print(f"[OK] 원본 크기로 복사 완료: {target_path}")

        # 2. 이미지 열기
        img = Image.open(source_path)
        print(f"  원본 크기: {img.size}")

        # 투명 배경 처리를 위해 RGBA로 변환
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # 3. 128x128 크기로 리사이즈 (알림용)
        img_128 = img.resize((128, 128), Image.Resampling.LANCZOS)
        img_128.save(target_path_128)
        print(f"[OK] 128x128 리사이즈 완료: {target_path_128}")

        # 4. 64x64 크기로 리사이즈 (작은 아이콘용)
        img_64 = img.resize((64, 64), Image.Resampling.LANCZOS)
        img_64.save(target_path_64)
        print(f"[OK] 64x64 리사이즈 완료: {target_path_64}")

        # 5. 메인 approval_icon.png를 128x128 버전으로 교체
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