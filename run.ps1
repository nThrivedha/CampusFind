# UniTrace — Root PowerShell Launcher
$ErrorActionPreference = "Stop"
Set-Location -Path (Join-Path $PSScriptRoot "campus_lost_found")
& .\run.ps1
