Add-Type @"
using System;
using System.Runtime.InteropServices;
public static class NativeMouse {
    [DllImport("user32.dll")] public static extern bool SetCursorPos(int X, int Y);
    [DllImport("user32.dll")] public static extern IntPtr GetForegroundWindow();
    [DllImport("user32.dll")] public static extern int GetWindowText(IntPtr hWnd, System.Text.StringBuilder text, int count);
    [DllImport("user32.dll")] public static extern void mouse_event(uint flags, uint dx, uint dy, uint data, UIntPtr extra);
}
"@

# Resolve the exact Slate pane every run; do not click an arbitrary screen coordinate.
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$shell = New-Object -ComObject WScript.Shell
$root=[System.Windows.Automation.AutomationElement]::RootElement
$ws=$root.FindAll([System.Windows.Automation.TreeScope]::Children,[System.Windows.Automation.Condition]::TrueCondition)
$dialog=$null
for($i=0;$i -lt $ws.Count;$i++){
    $candidate=$ws.Item($i)
    if($candidate.Current.Name -eq 'Unable to Check Out From Revision Control!' -or $candidate.Current.Name -eq 'Restore Packages'){$dialog=$candidate;break}
}
if(-not $dialog){Write-Output 'Recovery dialog not found';exit 2}
$shell.AppActivate($dialog.Current.Name) | Out-Null
Start-Sleep -Milliseconds 200
$sb=New-Object System.Text.StringBuilder 256
[NativeMouse]::GetWindowText([NativeMouse]::GetForegroundWindow(),$sb,$sb.Capacity) | Out-Null
if($sb.ToString() -ne $dialog.Current.Name){Write-Output "Foreground is '$($sb.ToString())'; unlock Windows before clicking";exit 4}
$all=$dialog.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.Condition]::TrueCondition)
$target=$null
for($i=0;$i -lt $all.Count;$i++){
    $candidate=$all.Item($i)
    if($candidate.Current.Name -eq 'OK' -or $candidate.Current.Name -eq 'Restore Selected'){$target=$candidate;break}
}
if(-not $target){Write-Output 'Recovery button not found';exit 3}
$rect=$target.Current.BoundingRectangle
$x=[int]($rect.X+$rect.Width/2)
$y=[int]($rect.Y+$rect.Height/2)
[NativeMouse]::SetCursorPos($x, $y) | Out-Null
Start-Sleep -Milliseconds 150
[NativeMouse]::mouse_event(0x0002, 0, 0, 0, [UIntPtr]::Zero)
[NativeMouse]::mouse_event(0x0004, 0, 0, 0, [UIntPtr]::Zero)
$sb=New-Object System.Text.StringBuilder 256
[NativeMouse]::GetWindowText([NativeMouse]::GetForegroundWindow(),$sb,$sb.Capacity) | Out-Null
Write-Output "Clicked verified Unreal OK pane at $x,$y; foreground=$($sb.ToString())"
