import charon
from charon import Charon

with Charon() as c:
    c.login()
    url = 'http://codeforces.com/contest/202/submit'
    problem = 'A'
    language = 'Python 3.5.1'
    submission = open('202A.py').readlines()
    submission_id = c.submit(url, problem, language, submission)
    print(submission_id)
    print(charon.get_result(submission_id))
