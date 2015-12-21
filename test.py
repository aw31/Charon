import charon
from charon import Charon

def output(submission_id, result):
    print(submission_id, result)

c = Charon(output)

url = 'http://codeforces.com/contest/504/submit'
problem = 'E'
language = 'GNU G++11 5.1.0'
submission = open('test/504E.cpp').readlines()

c.submit(url, problem, language, submission)

url = 'http://codeforces.com/contest/202/submit'
problem = 'A'
language = 'Python 3.5.1'
submission = open('test/202A.py').readlines()

c.submit(url, problem, language, submission)

for t in charon.threads:
    t.join()

c.driver.quit()
