"""
Python에서 Windows Toast 알림 테스트
"""
import subprocess
import time

def test_notification():
    print("Python에서 Windows Toast 알림을 표시합니다...")

    title = "Python Test"
    message = "이 알림이 보이나요?"

    # XML escape
    title_escaped = title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    message_escaped = message.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    # PowerShell 스크립트
    ps_script = f'''
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

$APP_ID = '{{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}}\\WindowsPowerShell\\v1.0\\powershell.exe'

$template = @"
<toast>
    <visual>
        <binding template='ToastGeneric'>
            <text>{title_escaped}</text>
            <text>{message_escaped}</text>
        </binding>
    </visual>
</toast>
"@

$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml($template)
$toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($APP_ID).Show($toast)
'''

    try:
        # PowerShell 실행
        result = subprocess.run(
            ['powershell', '-WindowStyle', 'Hidden', '-Command', ps_script],
            capture_output=True,
            text=True,
            timeout=5
        )

        print(f"PowerShell 실행 완료!")
        if result.returncode == 0:
            print("✓ 성공! 우측 하단을 확인하세요.")
        else:
            print(f"✗ 오류 발생:")
            print(result.stderr)

    except Exception as e:
        print(f"✗ 예외 발생: {e}")

if __name__ == "__main__":
    test_notification()
    print("\n5초 대기 중...")
    time.sleep(5)
    print("테스트 완료!")
