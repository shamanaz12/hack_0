@echo off
echo Checking if environment variables are accessible to Python...

python -c "
import os
print('Current environment variables for SMTP:')
print(f'SMTP_HOST: {os.getenv(\"SMTP_HOST\", \"Not set\")}')
print(f'SMTP_PORT: {os.getenv(\"SMTP_PORT\", \"Not set\")}')
print(f'SMTP_USERNAME: {os.getenv(\"SMTP_USERNAME\", \"Not set\")}')
print(f'SMTP_PASSWORD: {os.getenv(\"SMTP_PASSWORD\", \"Not set\")}')
print(f'SMTP_USE_TLS: {os.getenv(\"SMTP_USE_TLS\", \"Not set\")}')
"