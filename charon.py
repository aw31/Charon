import time
import json
import requests
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import ui
from selenium.webdriver.support.ui import Select

LOGIN_URL = 'http://codeforces.com/enter'
SUBMISSIONS_URL = 'http://codeforces.com/submissions/%s'
SUBMISSIONS_API_URL = 'http://codeforces.com/api/user.status?handle=%s&from=1&count=10'
USERNAME = 'Charon'
LANGUAGE_MAP = {
    'Python 3.5.1' : '31',
    'GNU C++ 5.1.0' : '1',
    'Java 1.8.0_66' : '36'
}
LIMIT = 60

def get_password():
    return open('password.txt').read()[:-1]

class Charon:
    def __init__(self):
        self.driver = webdriver.PhantomJS()
        # self.driver = webdriver.Firefox()

    def login(self):
        self.driver.get(LOGIN_URL)
        handle = self.driver.find_element_by_id('handle')
        handle.send_keys(USERNAME)
        password = self.driver.find_element_by_id('password')
        password.send_keys(get_password())
        password.send_keys(Keys.RETURN)
        wait = ui.WebDriverWait(self.driver, 10)
        wait.until(lambda driver : driver.find_elements_by_class_name('current'))

    def submit(self, url, problem, language, submission):
        self.driver.get(url)
        problems = Select(self.driver.find_element_by_name('submittedProblemIndex'))
        problems.select_by_value(problem)
        languages = Select(self.driver.find_element_by_name('programTypeId'))
        languages.select_by_value(LANGUAGE_MAP[language])
        text_area = self.driver.find_element_by_id('sourceCodeTextarea')
        text_area.send_keys(submission)
        self.driver.find_element_by_class_name('submit').submit()

        self.driver.get(SUBMISSIONS_URL % USERNAME)
        last_submit = self.driver.find_elements_by_class_name('view-source')[0]
        return last_submit.get_attribute('submissionid')

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.driver.close()

def get_result(submission_id):
    for i in range(LIMIT):
        response = requests.get(SUBMISSIONS_API_URL % USERNAME)
        submissions = json.loads(response.content.decode('utf-8'))
        if 'result' in submissions:
            submissions = submissions['result']
        for submission in submissions:
            if str(submission['id']) == submission_id:
                verdict = submission['verdict']
                if verdict != 'TESTING':
                    return verdict
        time.sleep(5)
    return 'TESTING'
