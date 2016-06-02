import menusystem
"""A simple example of the Menu System in action

   Author: Daniel Mikusa <dan@trz.cc>
Copyright: July 9, 2006
"""

# Handler functions
def save_name(data):
	print('Name: %s' % data)

def save_phone(data):
	print('Phone: %s' % data)

def save_street(data):
	print('Street: %s' % data)

def save_city(data):
	print('Phone: %s' % data)

def save_state(data):
	print('Phone: %s' % data)

def save_zip(data):
	print('Phone: %s' % data)

def done(value):
	return False

# Create Sub Menu
lst = []
lst.append(menusystem.Choice(selector=1, value=1, handler=save_street, description='Edit Street Address'))
lst.append(menusystem.Choice(selector=2, value=2, handler=save_city, description='Edit City'))
lst.append(menusystem.Choice(selector=3, value=3, handler=save_state, description='Edit State'))
lst.append(menusystem.Choice(selector=4, value=4, handler=save_zip, description='Edit Zip Code'))
lst.append(menusystem.Choice(selector=0, value=0, handler=done, description='Return to Main Menu'))
address = menusystem.Menu(title='Address Editor', choice_list=lst, prompt='What do you want to do? ')

name = menusystem.DataMenu(title='Name Editor', prompt='Enter your name. > ')
phone = menusystem.DataMenu(title='Phone Number Editor', prompt='Enter your phone number. > ')

# Create Some Choices
lst = []
lst.append(menusystem.Choice(selector=1, value=1, handler=save_name, description='Edit Name', subMenu=name))
lst.append(menusystem.Choice(selector=2, value=2, handler=None, description='Edit Address', subMenu=address))
lst.append(menusystem.Choice(selector=3, value=3, handler=save_phone, description='Edit Phone Number', subMenu=phone))
lst.append(menusystem.Choice(selector=0, value=0, handler=done, description='Exit'))

# Creat Menu & Begin Execution
head = menusystem.Menu(title='Information Editor', choice_list=lst, prompt='What do you want to do? ')
	
if __name__ == '__main__':
	"""If your menu functions are in the same file you must use the if __name__ check
	or it will appear that you menus are executed twice"""
	head.waitForInput()
	
	"""Save Menu To XML"""
	# Save Menu
	xml = menusystem.XMLMenuGenie('save.xml', 'example')
	xml.save(head)

	head2 = xml.load()
	head2.waitForInput()
