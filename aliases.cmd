@echo off

REM This script sets up aliases (doskeys) for running Python scripts within a pipenv virtual environment.

doskey prd=pipenv run python producer.py
doskey ce=pipenv run python consumer_email.py
doskey cs=pipenv run python consumer_sms.py