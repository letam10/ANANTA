Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes

$root = [System.Windows.Automation.AutomationElement]::RootElement
$windows = $root.FindAll(
    [System.Windows.Automation.TreeScope]::Children,
    [System.Windows.Automation.Condition]::TrueCondition
)

for ($i = 0; $i -lt $windows.Count; $i++) {
    $window = $windows.Item($i)
    $title = $window.Current.Name
    if ($title -notlike '*Restore Packages*' -and $title -notlike '*Unable to Check Out From Revision Control*') {
        continue
    }

    Write-Output "Found window: $title"
    $all = $window.FindAll(
        [System.Windows.Automation.TreeScope]::Descendants,
        [System.Windows.Automation.Condition]::TrueCondition
    )

    for ($j = 0; $j -lt $all.Count; $j++) {
        $element = $all.Item($j)
        $controlType = $element.Current.ControlType.ProgrammaticName
        $name = $element.Current.Name
        if ($controlType -eq 'ControlType.Button' -and $name -eq 'OK') {
            $pattern = $element.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
            $pattern.Invoke()
            Write-Output 'Invoked OK'
            exit 0
        }
    }

    if ($title -like '*Restore Packages*') {
        for ($j = 0; $j -lt $all.Count; $j++) {
            $element = $all.Item($j)
            $controlType = $element.Current.ControlType.ProgrammaticName
            $name = $element.Current.Name
            if ($controlType -eq 'ControlType.CheckBox' -and $element.Current.IsEnabled -and $element.Current.IsOffscreen -eq $false) {
                try {
                    $toggle = $element.GetCurrentPattern([System.Windows.Automation.TogglePattern]::Pattern)
                    if ($toggle.Current.ToggleState -ne [System.Windows.Automation.ToggleState]::On) {
                        $toggle.Toggle()
                        Write-Output "Checked: $name"
                    }
                } catch {}
            }
        }
        for ($j = 0; $j -lt $all.Count; $j++) {
            $element = $all.Item($j)
            if ($element.Current.ControlType.ProgrammaticName -eq 'ControlType.Button' -and $element.Current.Name -eq 'Restore Selected') {
                $pattern = $element.GetCurrentPattern([System.Windows.Automation.InvokePattern]::Pattern)
                $pattern.Invoke()
                Write-Output 'Invoked Restore Selected'
                exit 0
            }
        }
    }
}

Write-Output 'Recovery dialog not found'
exit 2
