$DB_NAME = "callbot_db"
$DB_USER = "callbot"
$DB_PASS = "123"

$env:PGPASSWORD = $DB_PASS

psql -U postgres -c "DROP DATABASE IF EXISTS $DB_NAME;"
psql -U postgres -c "DROP ROLE IF EXISTS $DB_USER;"
psql -U postgres -c "CREATE ROLE $DB_USER WITH LOGIN PASSWORD '$DB_PASS';"
psql -U postgres -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

psql -U $DB_USER -d $DB_NAME -f "$PSScriptRoot\seed.sql"

Write-Host "Database recreated and seeded."
