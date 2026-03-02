# Reset and reseed Django database with clean fixture

Write-Host "🔄 Flushing database..."
python manage.py flush --no-input

Write-Host "🌱 Seeding database with sample data..."
python seed_data.py

Write-Host "💾 Dumping seeded data into fixture..."
python manage.py dumpdata core.CustomUser core.SMEProfile core.Tenant core.TenantUser --indent 2 | Out-File -Encoding utf8 core/fixtures/initial_data.json

Write-Host "🧹 Stripping BOM (forcing UTF-8 without BOM)..."
Get-Content core/fixtures/initial_data.json | Out-File -Encoding utf8 core/fixtures/initial_data.json

Write-Host "📥 Reloading fixture..."
python manage.py loaddata core/fixtures/initial_data.json

Write-Host "✅ Done! Database reset, seeded, and fixture reloaded successfully."
