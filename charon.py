import time
from threading import Thread, Lock
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select

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

def synchronized(f):
    def inner(*args, **kwargs):
        args[0].lock.acquire()
        try:
            return f(*args, **kwargs)
        finally:
            args[0].lock.release()
    return inner

def run_asynchronously(f):
    def inner(*args, **kwargs):
        t = Thread(target=f, args=args, kwargs=kwargs)
        t.start()
    return inner

class Charon:
    def __init__(self):
        self.lock = Lock()
        self.lock.acquire()
        self.driver = webdriver.PhantomJS()
        # self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(10)
        self._login()

    @run_asynchronously
    def _login(self):
        self.driver.get(LOGIN_URL)
        handle = self.driver.find_element_by_id('handle')
        handle.send_keys(USERNAME)
        password = self.driver.find_element_by_id('password')
        password.send_keys(get_password())
        self.driver.find_element_by_id('remember').click()
        self.driver.find_element_by_class_name('submit').submit()
        self.driver.find_element_by_id('sidebar')
        self.lock.release()

    @synchronized
    def _submit(self, url, index, language, code):
        self.driver.get(url)
        indices = Select(self.driver.find_element_by_name('submittedProblemIndex'))
        indices.select_by_value(index)
        languages = Select(self.driver.find_element_by_name('programTypeId'))
        languages.select_by_value(LANGUAGE_MAP[language])
        text_area = self.driver.find_element_by_id('sourceCodeTextarea')
        text_area.send_keys(code)
        self.driver.find_element_by_class_name('submit').submit()
        # TODO: handle 'You have submitted exactly the same code before'
        time.sleep(1) # wait for Codeforces
        self.driver.get(SUBMISSIONS_URL % USERNAME)
        last_submit = self.driver.find_elements_by_class_name('view-source')[0]
        return last_submit.get_attribute('submissionid')

    @synchronized
    def _status(self, submission_id):
        self.driver.get(SUBMISSIONS_URL % USERNAME)
        submission_url = self.driver.find_element_by_link_text(submission_id)
        submission = submission_url.find_element_by_xpath('../..')
        status = submission.find_element_by_xpath('./td[@submissionid="%s"]' % submission_id)
        if status.get_attribute('waiting') == 'false':
            verdict = status.find_element_by_xpath('./span')
            time = submission.find_element_by_class_name('time-consumed-cell').text
            memory = submission.find_element_by_class_name('memory-consumed-cell').text
            return (verdict.get_attribute('submissionverdict'), time, memory)
        else:
            return ('WAITING', None, None)

    @run_asynchronously
    def submit(self, url, index, language, code, callback):
        submission_id = self._submit(url, index, language, code)
        for i in range(LIMIT):
            result = self._status(submission_id)
            if result[0] != 'WAITING':
                callback(submission_id, result)
                return
            time.sleep(5)
        callback(submission_id, ('UNKNOWN', None, None))
