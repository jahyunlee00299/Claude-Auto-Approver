#!/usr/bin/env python3
"""
Test script to show approval notification
"""
import time
import subprocess

def show_approval_notification():
    """
    Show an approval notification using PowerShell toast
    """
    try:
        # Add timestamp
        timestamp = time.strftime('%H:%M:%S')
        title = f"자동 승인 완료 [{timestamp}]"
        message = "Claude Code 승인 요청이 자동으로 처리되었습니다"

        print(f"[INFO] 알림 표시 중: {title}")

        # PowerShell script for Windows Toast
        ps_script = f'''
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

$APP_ID = '{{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}}\\\\WindowsPowerShell\\\\v1.0\\\\powershell.exe'

$template = @"
<toast>
    <visual>
        <binding template='ToastGeneric'>
            <text>{title}</text>
            <text>{message}</text>
        </binding>
    </visual>
    <audio src='ms-winsoundevent:Notification.Default'/>
</toast>
"@

$xml = New-Object Windows.Data.Xml.Dom.XmlDocument
$xml.LoadXml($template)
$toast = [Windows.UI.Notifications.ToastNotification]::new($xml)
[Windows.UI.Notifications.ToastNotificationManager]::CreateToastNotifier($APP_ID).Show($toast)
'''

        # Execute PowerShell
        result = subprocess.run(
            ['powershell', '-ExecutionPolicy', 'Bypass', '-Command', ps_script],
            capture_output=True,
            text=True
        )

        if result.returncode == 0:
            print(f"[SUCCESS] 승인 알림이 표시되었습니다!")
            print(f"           제목: {title}")
            print(f"           메시지: {message}")
        else:
            print(f"[ERROR] PowerShell 실행 오류: {result.stderr}")

    except Exception as e:
        print(f"[ERROR] 알림 표시 실패: {e}")

if __name__ == "__main__":
    print("=" * 60)
    print("승인 메시지 테스트")
    print("=" * 60)
    print()

    show_approval_notification()

    print("\n[INFO] Windows 알림 센터를 확인해보세요!")
    print("[INFO] 알림이 표시되지 않으면 Windows 알림 설정을 확인하세요.")