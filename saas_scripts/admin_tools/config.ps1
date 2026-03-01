# config.ps1
$BasePath = "C:\users\dell\saas_scripts\admin_tools"

$Scripts = @{
    "ResetDB"       = "$BasePath\resetdb.bat"
    "SeedDB"        = "$BasePath\seed.bat"
    "DumpDB"        = "$BasePath\dump.bat"
    "LoadDB"        = "$BasePath\load.bat"
    "ResetSeed"     = "$BasePath\reset_seed.bat"
    "ResetAndSeed"  = "$BasePath\reset_and_seed.bat"
}
