import menusystem
"""A simple example of a Menu System which has some depth

Selecting the first menu will progress up and down by one level.  Selecting
the second menu will progress down by one and when it hits the bottom will
go back to the root.

In addition, this demonstrates a fix which allows the selector to be a
non-integer value in XML.

Contributed by Peter Wicks Stringfield 3/2/2011
"""
def main():
    f = open("menu.xml", "r")
    genie = menusystem.XMLMenuGenie(f, "example_case")
    menu = genie.load()
    f.close()

    special_choice = menusystem.Choice(selector="1337 selector",
                                       description="Special choice",
                                       value=0,
                                       handler=special,
                                       subMenu=None)
    menu.choices.append(special_choice)

    menu.waitForInput()

def special(value):
    print("Special choice selected")
    return True

def foo(value):
    print("Foo")
    return False

def up_level(value):
    return False

if __name__ == "__main__":
    main()
    
