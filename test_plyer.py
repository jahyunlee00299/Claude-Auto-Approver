"""
PowerShell로 Windows 알림 테스트
"""
import subprocess
import time

print("PowerShell로 Windows Toast 알림 표시 중...")
print("우측 하단을 확인하세요!")

try:
    title = "Test Notification"
    message = "Windows Toast notification test!"

    # Escape XML special characters
    title_escaped = title.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    message_escaped = message.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

    # PowerShell script
    ps_script = f'''
[Windows.UI.Notifications.ToastNotificationManager, Windows.UI.Notifications, ContentType = WindowsRuntime] | Out-Null
[Windows.Data.Xml.Dom.XmlDocument, Windows.Data.Xml.Dom.XmlDocument, ContentType = WindowsRuntime] | Out-Null

$APP_ID = '{{1AC14E77-02E7-4E5D-B744-2EB1AE5198B7}}\\\\WindowsPowerShell\\\\v1.0\\\\powershell.exe'

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

    # Execute PowerShell
    result = subprocess.run(
        ['powershell', '-WindowStyle', 'Hidden', '-Command', ps_script],
        capture_output=True,
        text=True,
        timeout=5
    )

    if result.returncode == 0:
        print("[OK] Notification displayed!")
    else:
        print(f"[WARNING] PowerShell returned code {result.returncode}")
        if result.stderr:
            print(f"Error: {result.stderr}")

    print("Waiting 5 seconds...")
    time.sleep(5)
    print("Test complete!")

except Exception as e:
    print(f"[ERROR] Failed: {e}")
    import traceback
    traceback.print_exc()
