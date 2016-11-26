from fabric.api import local

def test():
	local("python ./test_group.py")

def run():
	local("python ./run.py")


