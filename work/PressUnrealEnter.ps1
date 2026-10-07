Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$shell = New-Object -ComObject WScript.Shell
$title = 'Unable to Check Out From Revision Control!'
$root=[System.Windows.Automation.AutomationElement]::RootElement
$ws=$root.FindAll([System.Windows.Automation.TreeScope]::Children,[System.Windows.Automation.Condition]::TrueCondition)
$target=$null
for($i=0;$i -lt $ws.Count;$i++){if($ws.Item($i).Current.Name -eq $title -or $ws.Item($i).Current.Name -eq 'Restore Packages'){$target=$ws.Item($i);break}}
if(-not $target){Write-Output 'Target dialog not found';exit 2}
$target.SetFocus()
$all=$target.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.Condition]::TrueCondition)
for($i=0;$i -lt $all.Count;$i++){if($all.Item($i).Current.Name -eq 'OK'){$all.Item($i).SetFocus();break}}
Start-Sleep -Milliseconds 250
[System.Windows.Forms.SendKeys]::SendWait('{ENTER}')
Write-Output 'Sent ENTER to active Unreal dialog'
