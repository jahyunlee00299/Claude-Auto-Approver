"""
아이콘을 더 크게 리사이즈
"""
from PIL import Image
import os

def resize_icon_larger():
    """아이콘을 더 큰 크기로 리사이즈"""

    # 원본 이미지 경로
    source_path = r"C:\Users\Jahyun\OneDrive - 호서대학교\바탕 화면 [Labtop]\9dc14126ee3e2d16b00d0a503b592cbb8b566dca82634c93f811198148a26065.png"

    # 대상 경로
    target_path = os.path.join(os.path.dirname(__file__), "approval_icon.png")
    target_path_256 = os.path.join(os.path.dirname(__file__), "approval_icon_256.png")
    target_path_512 = os.path.join(os.path.dirname(__file__), "approval_icon_512.png")

    try:
        # 원본 파일 확인
        if not os.path.exists(source_path):
            print(f"원본 파일을 찾을 수 없습니다: {source_path}")
            return False

        print(f"원본 파일 발견: {source_path}")

        # 이미지 열기
        img = Image.open(source_path)
        print(f"  원본 크기: {img.size}")

        # 투명 배경 처리를 위해 RGBA로 변환
        if img.mode != 'RGBA':
            img = img.convert('RGBA')

        # 1. 256x256 크기로 리사이즈 (큰 알림용)
        img_256 = img.resize((256, 256), Image.Resampling.LANCZOS)
        img_256.save(target_path_256)
        print(f"[OK] 256x256 리사이즈 완료: {target_path_256}")

        # 2. 512x512 크기로 리사이즈 (매우 큰 알림용)
        img_512 = img.resize((512, 512), Image.Resampling.LANCZOS)
        img_512.save(target_path_512)
        print(f"[OK] 512x512 리사이즈 완료: {target_path_512}")

        # 3. 메인 approval_icon.png를 256x256 버전으로 교체
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