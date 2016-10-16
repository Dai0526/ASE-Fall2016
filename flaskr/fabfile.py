from fabric.api import local

def test():
	local("python ./test_flaskr.py")

def run():
	local("python ./flaskr.py")


