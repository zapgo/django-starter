$PackageName = 'miniconda'
$InstallerType = 'EXE'
$Url = 'https://repo.continuum.io/miniconda/Miniconda-latest-Windows-x86.exe'
$Url64 = 'https://repo.continuum.io/miniconda/Miniconda-latest-Windows-x86_64.exe'
$Args = "/InstallationType=AllUsers /S"
$ValidExitCodes = @(0)

Install-ChocolateyPackage "$PackageName" "$InstallerType" "$Args" "$Url" "$Url64"  -validExitCodes $ValidExitCodes