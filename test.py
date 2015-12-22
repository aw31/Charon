"""Tests Charon with two concurrent submissions."""
from charon import Charon

def output(submission_id, result):
    """Dummy callback function."""
    print(submission_id, result)

def main():
    charon = Charon()

    url = 'http://codeforces.com/contest/504/submit'
    problem = 'E'
    language = 'GNU G++11 5.1.0'
    code = open('test/504E.cpp').readlines()
    charon.submit((url, problem, language, code), output)

    url = 'http://codeforces.com/contest/202/submit'
    problem = 'A'
    language = 'Python 3.5.1'
    code = open('test/202A.py').readlines()
    charon.submit((url, problem, language, code), output)

if __name__ == '__main__':
    main()
