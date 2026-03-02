#!/bin/bash
source /mnt/c/Users/DELL/Saas_Project/.venv/bin/activate
cd saas_app
nohup celery -A saas_app worker -l info > celery.log 2>&1 &
nohup celery -A saas_app flower > flower.log 2>&1 &
