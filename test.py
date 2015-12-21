import time
import charon
from charon import Charon

def output(submission_id, result):
    print(submission_id, result)

c = Charon()

time.sleep(1)

url = 'http://codeforces.com/contest/504/submit'
problem = 'E'
language = 'GNU G++11 5.1.0'
code = open('test/504E.cpp').readlines()
c.submit(url, problem, language, code, output)

url = 'http://codeforces.com/contest/202/submit'
problem = 'A'
language = 'Python 3.5.1'
code = open('test/202A.py').readlines()
c.submit(url, problem, language, code, output)
