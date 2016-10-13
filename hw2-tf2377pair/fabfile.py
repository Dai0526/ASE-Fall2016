from fabric.api import local

def test():
	local("python ./test_groupwise.py")
#	local("./groupwise.py")


def run():
	local("python ./groupwise.py")


#def commit():
#	local("git add -p && git commit")

#def push()
#	local("git push")

""" After we decoded the server to hold our code, we will add it
def prepare_deploy():
	test()
	commit()
	push()

"""
