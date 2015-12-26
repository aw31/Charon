"""Uses Selenium to login and submit solutions on Codeforces."""
from time import sleep
from functools import wraps
from threading import Thread, Lock
from selenium import webdriver
from selenium.webdriver.support.ui import Select
from xvfbwrapper import Xvfb

LOGIN_URL = 'http://codeforces.com/enter'
SUBMISSIONS_URL = 'http://codeforces.com/submissions/'

REFRESH_LIMIT = 60

def synchronized(f):
    """Decorator for methods that cannot execute simultaneously."""
    @wraps(f)
    def inner(*args, **kwargs):
        args[0].lock.acquire()
        try:
            return f(*args, **kwargs)
        finally:
            args[0].lock.release()
    return inner

def run_asynchronously(f):
    """Decorator that runs method asynchronously in new thread."""
    @wraps(f)
    def inner(*args, **kwargs):
        Thread(target=f, args=args, kwargs=kwargs).start()
    return inner

class Charon(object):
    """Provides interface that submits solutions and retrieves results."""
    def __init__(self, handle, password):
        self.handle = handle
        self.password = password
        self.lock = Lock() # manages access to Selenium
        self.lock.acquire() # acquires lock until logged in
        self.vdisplay = Xvfb()
        self.vdisplay.start()
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(10)
        self._login()

    @run_asynchronously
    def _login(self):
        self.driver.get(LOGIN_URL)
        handle = self.driver.find_element_by_id('handle')
        password = self.driver.find_element_by_id('password')
        remember = self.driver.find_element_by_id('remember')
        submit = self.driver.find_element_by_class_name('submit')
        handle.send_keys(self.handle)
        password.send_keys(self.password)
        remember.click()
        submit.submit()
        self.driver.find_element_by_id('sidebar')
        self.lock.release() # releases lock after log in

    @synchronized
    def _submit(self, url, index, language, code):
        self.driver.get(url)
        indices = Select(self.driver.find_element_by_name('submittedProblemIndex'))
        languages = Select(self.driver.find_element_by_name('programTypeId'))
        checkbox = self.driver.find_element_by_id(
            'edit_area_toggle_checkbox_sourceCodeTextarea')
        text_area = self.driver.find_element_by_id('sourceCodeTextarea')
        submit = self.driver.find_element_by_class_name('submit')
        if checkbox.is_selected():
            checkbox.click()
        indices.select_by_value(index)
        languages.select_by_visible_text(language)
        text_area.send_keys(code.replace('\t', '    '))
        submit.submit()
        # TODO: handle 'You have submitted exactly the same code before'
        sleep(1) # wait for Codeforces
        self.driver.get(SUBMISSIONS_URL + self.handle)
        last_submit = self.driver.find_elements_by_class_name('view-source')[0]
        return last_submit.get_attribute('submissionid')

    @synchronized
    def _status(self, submission_id):
        self.driver.get(SUBMISSIONS_URL + self.handle)
        status_xpath = '//td[@submissionid="%s"]' % submission_id
        status = self.driver.find_element_by_xpath(status_xpath)
        if status.get_attribute('waiting') == 'false':
            row_xpath = '//tr[@data-submission-id="%s"]' % submission_id
            row = self.driver.find_element_by_xpath(row_xpath)
            verdict = status.find_element_by_xpath('.//span').get_attribute('submissionverdict')
            runtime = row.find_element_by_class_name('time-consumed-cell').text
            memory = row.find_element_by_class_name('memory-consumed-cell').text
            return (verdict, runtime, memory)
        else:
            return ('JUDGING', None, None)

    @run_asynchronously
    def submit(self, submission, callback):
        """Submits to Codeforces and calls callback with results."""
        submission_id = self._submit(*submission)
        for i in range(REFRESH_LIMIT):
            result = self._status(submission_id)
            if result[0] != 'JUDGING':
                callback(submission_id, result)
                return
            sleep(5)
        callback(submission_id, ('ERROR', None, None))
