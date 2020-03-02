def foo(func):
    def wrap(s): # I'd call this 'self' instead of 's' to remind us it's a reference to an instance

        func(s) # This is a function, not a method yet - so we need to pass in the reference

        s.ma() # This is a method, because you use attribute lookup on the object s to get it
    return wrap

class A:
    def ma(self):
        print("this is ma")

    @foo     # if the way foo wraps mb doesn't depend on some arg, don't use args here
    def mb(self):
        print("this is mb")


a =A()

a.mb()

d = [1,24,4]

dd = [str(x) for x in d]
print(dd)