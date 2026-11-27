param(
  [Parameter(Mandatory=$true)][string]$ArduinoCliPath,
  [Parameter(Mandatory=$true)][string]$ConfigFile,
  [Parameter(Mandatory=$true)][string]$LibraryPath,
  [Parameter(Mandatory=$true)][string]$IdeLibrariesPath,
  [Parameter(Mandatory=$true)][string]$BuildRoot
)
$ErrorActionPreference = 'Stop'
$libraryRoot = (Resolve-Path -LiteralPath $LibraryPath).Path
$ideLibraries = (Resolve-Path -LiteralPath $IdeLibrariesPath).Path
$buildRootResolved = [System.IO.Path]::GetFullPath($BuildRoot)
New-Item -ItemType Directory -Force -Path $buildRootResolved | Out-Null
$cases = @(
  @{ Sketch = (Join-Path $PSScriptRoot 'StaticSocketSmoke'); Name = 'static_socket' },
  @{ Sketch = (Join-Path $PSScriptRoot 'GeneratedTemplateSmoke'); Name = 'generated_dhcp' }
)
$boards = @(
  @{ Fqbn = 'arduino:avr:uno'; Name = 'uno' },
  @{ Fqbn = 'arduino:avr:nano:cpu=atmega328old'; Name = 'nano328old' },
  @{ Fqbn = 'arduino:avr:mega'; Name = 'mega_control' }
)
foreach ($case in $cases) {
  foreach ($board in $boards) {
    $out = Join-Path $buildRootResolved ($case.Name + '_' + $board.Name)
    & $ArduinoCliPath --config-file $ConfigFile compile --fqbn $board.Fqbn --library $libraryRoot --libraries $ideLibraries --build-path $out $case.Sketch
    if ($LASTEXITCODE -ne 0) { throw "Build failed: $($case.Name) for $($board.Fqbn)" }
  }
}
