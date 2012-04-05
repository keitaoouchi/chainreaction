About this module
-----------------
Wrapper module which provides iterable object with infix style method chaining.  

Unreadble::

    >>> filter(lambda y: y % 2, map(lambda x: x + 1, iterable))

Readable::

    >>> iterable = react(iterable)
    >>> iterable.map(lambda x: x + 1).filter(lambda y: y % 2)

How to install
--------------
Requires python2.6 or later (include python3.x).
You need *pip* or *distribute* or *setuptools*::

    $ pip install chainreaction

or use easy_install::

    $ easy_install chainreaction
    
Recent changed
--------------
0.2.0
^^^^^
* Supported python2.6 .
* Changed to use itertools in 'Chainable.filter/map' methods in python2.x .

0.1.2
^^^^^
* Supported 'for' statement.

How to use
----------
The simplest and an only way to use this module is to call the **react** function.  
**react** is a factory function which looks up *'__iter__'* / *'__getitem__'* 
from an given iterable, and returns wrapped object.

Example to use::

    >>> from chainreaction.reactor import react
    >>> react("hello")
    >>> react([1, 2, 3])
    >>> react(iter([1, 2, 3])
    >>> class DictLike(dict):pass
    >>> react(DictLike())

Chainable object support any methods of its wrapped object,
and try to wrap their return value.  
By convention, side effective methods return nothing, but chainable object
returns its side affected object wrapped with appropriate wrappper.  
If iterator was passed into **react**, it would be consumed when it called
any iterative methods.

Example to use::

    >>> tobewrapped = "hello"
    >>> wrapped = react(tobewrapped)
    >>> wrapped = wrapped.upper().map(lambda c: ord(c))
    >>> [chr(c) for c in wrapped.unwrap] = [c for c in tobewrapped.upper()]
    True
    >>> tobewrapped = [1, 2, 3]
    >>> wrapped = react(tobewrapped)
    >>> wrapped.append(4).count()
    4
    >>> len(tobewrapped)
    4

If an iterator was given, this iterator would be consumed
when it called any method::

    >>> tobewrapped = iter([1,2,3])
    >>> wrapped = react(tobewrapped)
    >>> wrapped.count()
    4
    >>> len(list(tobewrapped))
    0
    
Tiny percent encoding implementation example::

    >>> test = bytes("hello world-._~", encoding="UTF-8")
    >>> wrapped = react(test)
    >>> safe = set()
    >>> react("0123456789").foreach(lambda c: safe.add(ord(c)))
    >>> react(range(ord('a'), ord('z') + 1)).foreach(lambda b: safe.add(b))
    >>> react(range(ord('A'), ord('Z') + 1)).foreach(lambda b: safe.add(b))
    >>> react("-._~").foreach(lambda c: safe.add(ord(c)))
    >>> test = wrapped.map(lambda b: b if b > 0 else 256 + b)
    >>> test = test.map(lambda i: '+' if chr(i).isspace() else chr(i) if i in safe else "%{0:x}".format(i))
    >>> test.tostring == "hello+world-._~"
    True
    
Basic API
---------
* unwrap
    Retrieves iterable from wrapped object.
* dump
    Elements dump.
* isiterator
    True if wrapped object is iterator.
* tostring
    Returns almost same with "".join((str(x) for x in iterable)). This method always returns str object. str wrapped returns unwrapped, bytes or bytearray wrapped returns str converted, dict wrapped returns "key=value" pairs joined with "&".
* foreach(f)
    Applies a given f to all elements.
* filter(pred)
    Selects all elements which satisfy a given predicate.
* map(f)
    Builds a new collection by applying a given f.
* forall(pred)
    True if all elements satisfy a given predicate.
* forany(pred)
    True if any elements satisfy a given predicate.
* dropwhile(pred)
    Drops longest prefix of elements that satisfy a given predicate.
* dropright(pred)
    Drops longest suffix of elements that satisfy a given predicate.
* takwhile(pred)
    Takes longest prefix of elements that satisfy a given predicate.
* takeright(pred)
    Takes longest suffix of elements that satisfy a given predicate.
* mkstring(joiner="")
    Returns wrapped str object using a joiner string.
* counts(pred=lambda x: True)
    Counts the number of elements that satisfy a given predicate.
* contains(key)
    Tests whether this wrapped object contains a given key as an element.
* reduce(f)
    Returns a value(not wrapped) using a given f.
    
iterator specific API
^^^^^^^^^^^^^^^^^^^^^
* tolist
    Returns a new list wrapped.
* totuple
    Returns a new tuple wrapped.
* toset
    Returns a new set wrapped.
    
str, bytes, bytearray specific API
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
* reverse
    Returns a new reversed str wrapped.

seq specific API
^^^^^^^^^^^^^^^^
* accumulate(f)
    Returns a seq of accumulated value.
* reverse
    Returns a new reversed seq wrapped.
* sort
    Returns a new sorted seq wrapped.
* toset
    Returns a new set wrapped.

set specific API
^^^^^^^^^^^^^^^^
* min
    Returns a minimum value.
* max
    Returns a maximum value.