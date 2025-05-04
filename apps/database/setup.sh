#!/bin/bash
set -e

echo "********** `/bin/date` Starting MySQL setup **********"

MYSQL_PWD=$(cat /run/secrets/mysql_root_password) mysql -u root <<EOF
CREATE USER IF NOT EXISTS '$DB_USER'@'%' IDENTIFIED WITH caching_sha2_password BY '$DB_PASSWORD';
GRANT SELECT, INSERT, UPDATE, DELETE ON voice_assistant.* TO '$DB_USER'@'%';
FLUSH PRIVILEGES;
EOF

echo "********** `/bin/date` Finished **********"