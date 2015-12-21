import time
from threading import Thread, Lock
from charon import Submitter

def output(submission_id, verdict):
    print(submission_id, verdict)

s = Submitter(output, Lock())

url = 'http://codeforces.com/contest/504/submit'
problem = 'E'
language = 'GNU G++11 5.1.0'
submission = open('504E.cpp').readlines()

Thread(target=s.make_submission, args=(url, problem, language, submission)).start()

url = 'http://codeforces.com/contest/202/submit'
problem = 'A'
language = 'Python 3.5.1'
submission = open('202A.py').readlines()

Thread(target=s.make_submission, args=(url, problem, language, submission)).start()
