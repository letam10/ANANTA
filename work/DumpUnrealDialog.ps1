Add-Type -AssemblyName UIAutomationClient
Add-Type -AssemblyName UIAutomationTypes
$root=[System.Windows.Automation.AutomationElement]::RootElement
$ws=$root.FindAll([System.Windows.Automation.TreeScope]::Children,[System.Windows.Automation.Condition]::TrueCondition)
for($i=0;$i -lt $ws.Count;$i++){
  $w=$ws.Item($i); if($w.Current.Name -like '*Revision Control*' -or $w.Current.Name -like '*Restore Packages*'){
    $r=$w.Current.BoundingRectangle
    Write-Output ("WINDOW="+$w.Current.Name+" RECT="+$r.X+","+$r.Y+","+$r.Width+","+$r.Height)
    $all=$w.FindAll([System.Windows.Automation.TreeScope]::Descendants,[System.Windows.Automation.Condition]::TrueCondition)
    for($j=0;$j -lt $all.Count;$j++){
      $e=$all.Item($j)
      $patterns=$e.GetSupportedPatterns() | ForEach-Object { $_.ProgrammaticName }
      $er=$e.Current.BoundingRectangle
      Write-Output (("TYPE="+$e.Current.ControlType.ProgrammaticName+" NAME="+$e.Current.Name+" RECT="+$er.X+","+$er.Y+","+$er.Width+","+$er.Height+" ENABLED="+$e.Current.IsEnabled+" OFFSCREEN="+$e.Current.IsOffscreen+" PATTERNS="+($patterns -join ',')))
    }
  }
}
