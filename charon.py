import time
import json
import requests
import threading
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait

LOGIN_URL = 'http://codeforces.com/enter'
SUBMISSIONS_URL = 'http://codeforces.com/submissions/%s'
SUBMISSIONS_API_URL = 'http://codeforces.com/api/user.status?handle=%s&from=1&count=10'
USERNAME = 'Charon'
LANGUAGE_MAP = {
    'Python 3.5.1' : '31',
    'GNU G++11 5.1.0' : '42',
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
        self.driver.find_element_by_class_name('submit').submit()
        WebDriverWait(self.driver, 10).until(expected_conditions.title_is('Codeforces'))

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

    def get_status(self, submission_id):
        self.driver.get(SUBMISSIONS_URL % USERNAME)
        try:
            submission_url = self.driver.find_element_by_link_text(submission_id)
        except:
            return ('WAITING', None, None)
        else:
            submission = submission_url.find_element_by_xpath('../..')
            status = submission.find_element_by_xpath('./td[@submissionid="%s"]' % submission_id)
            if status.get_attribute('waiting') == 'false':
                verdict = status.find_element_by_xpath('./span')
                time = submission.find_element_by_class_name('time-consumed-cell').text
                memory = submission.find_element_by_class_name('memory-consumed-cell').text
                return (verdict.get_attribute('submissionverdict'), time, memory)
            else:
                return ('WAITING', None, None)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.driver.close()

class Submitter:
    def __init__(self, callback, lock):
        self.callback = callback
        self.lock = lock

    def make_submission(self, url, problem, language, submission):
        with Charon() as c:
            c.login()
            self.lock.acquire()
            submission_id = c.submit(url, problem, language, submission)
            self.lock.release()
            for i in range(LIMIT):
                verdict = c.get_status(submission_id)
                if verdict[0] != 'WAITING':
                    self.callback(submission_id, verdict)
                    return
                time.sleep(5)
            self.callback(submission_id, ('UNKNOWN'))
