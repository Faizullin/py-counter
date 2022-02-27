import sys;
def die(text,is_exit=False):
	print("ERROR:",text)
	if is_exit:
		sys.exit()
def tr(func,is_die=False,is_exit=False):
	try:
		func();
		return True
	except Exception as err:
		if is_die:
			die(err,is_exit);
		else:
			print("ERROR:",err)
		return False