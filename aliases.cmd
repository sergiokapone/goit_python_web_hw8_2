@echo off
doskey prd=pipenv run python producer.py
doskey ce=pipenv run python consumer_email.py
doskey cs=pipenv run python consumer_sms.py