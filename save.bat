@echo off
pip freeze > requirements.txt
git add .
git commit -m %1
git push https://github.com/Felifelps/Biblioteca