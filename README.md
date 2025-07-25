#Normal execution
source venv/bin/activate  # or ./venv/bin/activate
pip install python-dotenv
pip show python-dotenv
pytest tests/


#HTML report execution
pytest tests/ --html=reports/report.html --self-contained-html

#Allure execution
pytest --alluredir=allure-results
allure generate allure-results --clean -o allure-report
allure open allure-report


#clears data from ids.txt file and runs new test
echo "=== New Test Run ===" > output/ids.txt && pytest tests/ --html=reports/report.html --self-contained-html
