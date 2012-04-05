"""Wrapper module which provides iterable object with infix style method chain.  

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

@author: Keita Oouchi
@email : keita.oouchi@gmail.com
"""

import itertools
import functools
import collections

__all__ = ["react"]

import sys
if sys.version < '3.0.0':
    #In py3.x, iterator's "next" method was changed to "__next__".
    _ITER_NEXT = "next"
    _MAP = itertools.imap
    _FILTER = itertools.ifilter
else:
    _ITER_NEXT = "__next__"
    _MAP = map
    _FILTER = filter

def react(iterable):
    """Factory function creating Chainable object.

    If iterable supports iterator or sequencial access protocol,
    wrap it with Chainable class and provide some chaining style method.
    """
    if isinstance(iterable, collections.Iterable):
        if isinstance(iterable, Chainable):
            return iterable
        elif isinstance(iterable, collections.Iterator):
            return IterChain(iterable)
        elif hasattr(iterable, "__getitem__"):
            #isinstance(bytearray(), collections.Sequence) => True if py3.x else False
            if isinstance(iterable, (str, bytes, bytearray)):
                return StrChain(iterable)
            elif isinstance(iterable, collections.Mapping):
                return DictChain(iterable)
            else:
                return SeqChain(iterable)
        elif isinstance(iterable, collections.Set):
            return SetChain(iterable)
        else:
            return Chainable(iterable)
    else:
        template = "Chainable does not support {0}. given argument:{1}:{0}"
        raise AttributeError(template.format(type(iterable), iterable))

"""
def react(iterable):
    if isinstance(iterable, collections.Iterable):
        if isinstance(iterable, Chainable):
            return iterable
        elif isinstance(iterable, collections.Iterator):
            return IterChain(iterable)
        elif issubclass(type(iterable), (str, bytes, bytearray)):
            return StrChain(iterable)
        elif isinstance(iterable, collections.Sequence):
            return SeqChain(iterable)
        elif isinstance(iterable, collections.Mapping):
            return DictChain(iterable)
        elif isinstance(iterable, collections.Set):
            return SetChain(iterable)
        else:
            return Chainable(iterable)
    else:
        template = "Chainable does not support {0}. given argument:{1}:{0}"
        raise AttributeError(template.format(type(iterable), iterable))
"""

def _chainreact(__getattr__):
    """Decorator function used in Chainable's __getattr__ method.
    
    Chainable object support methods of its wrapped objects, and try to keep
    its return value also chainable.
    """
    def containment(*methodname):
        self, methodobj = __getattr__(*methodname)
        def reaction(*realargs):
            result = methodobj(*realargs)
            result = result if result else self
            return react(result)
        return reaction
    return containment


class Chainable(object):
    """ This class is a base class provides chainable interface.
    
    Iterator object would be wrapped with this class.
    """

    def __init__(self, iterable):
        #reference duplication!
        self._iterable = iterable
        self.type = type(iterable)

    def __getattribute__(self, name):
        #Support 'for' statement.
        if name == _ITER_NEXT:
            next = getattr(self._iterator, _ITER_NEXT)
            return next(name)
        else:
            return object.__getattribute__(self, name)

    @_chainreact
    def __getattr__(self, name):
        """Wrap return value using '_chanreact'."""
        return self._iterable, getattr(self._iterable, name)

    def __repr__(self):
        return "'{0}':{1}".format(self.unwrap, type(self).__name__)

    def _constract(self, iterable):
        """This method would be called when other methods, excluding methods of
        wrapped object, was called and wrap their return value if possible.
        """
        try:
            if self.isiterator:
                result = iterable
            else:
                result = self.type(iterable)
        except TypeError:
            result = iterable
        finally:
            return result

    def __enter__(self):
        result = self._iterable.__enter__()
        if result:
            return self

    def __exit__(self, *args):
        result = self._iterable.__exit__(args)
        if result:
            return result

    def __iter__(self):
        return iter(self._iterator)

    @property
    def isiterator(self):
        """Check whether given iterable is iterator object."""
        return isinstance(self._iterable, collections.Iterator)

    @property
    def unwrap(self):
        """Return wrapped object."""
        return self._iterable

    @property
    def dump(self):
        dump_template = "[Dumped Information]\n{type}\n{iterable}\n{tostring}"
        dumped_self = {"type":type(self).__name__,
                       "iterable":self.type.__name__,
                       "tostring":self.tostring}
        return dump_template.format(**dumped_self)

    @property
    def _iterator(self):
        """If wrapped obj was subclass of dict, this would return
        self._iterable.items()."""
        return self._iterable

    @property
    def tostring(self):
        return "".join((str(x) for x in self._iterator))

    def foreach(self, f):
        for x in self._iterator:
            f(x)

    def filter(self, pred):
        result = _FILTER(pred, self._iterator)
        return react(self._constract(result))

    def map(self, f):
        result = _MAP(f, self._iterator)
        return react(self._constract(result))

    def forall(self, pred):
        """True if whole elements satisfy a given predicate."""
        for x in self._iterator:
            if not pred(x):
                return False
        return True

    def forany(self, pred):
        """True if any elements satisfy a given predicate."""
        for x in self._iterator:
            if pred(x):
                return True
        return False

    def dropwhile(self, pred):
        """Drops longest prefix of elements that satisfy a given predicate."""
        result = itertools.dropwhile(pred, self._iterator)
        return react(self._constract(result))

    def dropright(self, pred):
        """Drops longest suffix of elements that satisfy a given predicate."""
        lis = [x for x in self._iterator]
        size = len(lis)
        passed = size
        tf = True
        while tf and passed > 0:
            passed -= 1
            tf = pred(lis[passed])
        result = iter(lis[0:passed + 1])
        return react(self._constract(result))

    def takewhile(self, pred):
        """Takes longest prefix of elements that satisfy a given predicate."""
        result = itertools.takewhile(pred, self._iterator)
        return react(self._constract(result))

    def takeright(self, pred):
        """Takes longest suffix of elements that satisfy a given predicate."""
        lis = [x for x in self._iterator]
        size = len(lis)
        passed = size
        tf = True
        while tf and passed > 0:
            passed -= 1
            tf = pred(lis[passed])
        result = iter(lis[passed + 1:size])
        return react(self._constract(result))

    def mkstring(self, joiner=""):
        """Returns wrapped str object using a joiner string."""
        strlist = (str(x) for x in self._iterator)
        return react(joiner.join(strlist))

    def counts(self, pred=lambda x: True):
        """Counts the number of elements that satisfy a given predicate."""
        result = 0
        for x in self._iterator:
            if pred(x):
                result += 1
        return result

    def contains(self, key):
        """Tests whether this wrapped object contains a given key as an element."""
        return key in self._iterator

    def reduce(self, f):
        """End of chain reaction"""
        return functools.reduce(f, self._iterator)

class IterChain(Chainable):

    def _constract(self, iterable):
        return iterable

    @property
    def tolist(self):
        return react(list(self._iterable))

    @property
    def totuple(self):
        return react(tuple(self._iterable))

    @property
    def toset(self):
        return react(set(self._iterable))

class StrChain(Chainable):

    def __getitem__(self, key):
        return react(self._iterable[key])

    def _constract(self, iterable):
        return "".join((str(x) for x in iterable))

    @property
    def reverse(self):
        result = reversed(self._iterable)
        return react(self._constract(result))

    @property
    def tostring(self):
        if self.type == str:
            return self._iterable
        else:
            temp = self._iterable.decode()
            if type(temp) == str:
                return temp
            else:
                return temp.encode()

    def map(self, f):
        """Returns IterChain or SeqChain(in python2.x)"""
        result = _MAP(f, self._iterable)
        return react(result)

    def mkstring(self, joiner=""):
        return react(joiner.join(self._iterable))

class SeqChain(Chainable):

    def __getitem__(self, key):
        """a[i:j] => a.__getitem__(slice(i,j))"""
        item = self._iterable[key]
        try:
            result = react(item)
        except AttributeError:
            result = item
        finally:
            return result

    @property
    def reverse(self):
        result = reversed(self._iterable)
        return react(self._constract(result))

    @property
    def sort(self):
        result = sorted(self._iterable)
        return react(self._constract(result))

    @property
    def toset(self):
        return react(set(self._iterable))

    def accumulate(self, f):
        """Returns a seq of accumulated value."""
        def inner():
            it = iter(self._iterable)
            total = next(it)
            yield total
            for elem in it:
                total = f(total, elem)
                yield total
        return react(self._constract(inner()))

class SetChain(Chainable):

    @property
    def min(self):
        return min(self._iterable)

    @property
    def max(self):
        return max(self._iterable)

class DictChain(Chainable):

    def __init__(self, iterable):
        """DictChain internally uses list of tuple(key,value) as its iterator.
        [example]
        >>> dictchain.map(lambda t: (t[0], t[1] * 2))
        """
        self._iterable = iterable
        self.type = type(iterable)

    @property
    def _iterator(self):
        return self._iterable.items()

    def __getitem__(self, key):
        item = self._iterable[key]
        try:
            result = react(item)
        except AttributeError:
            result = item
        finally:
            return result

    @property
    def tostring(self):
        key_value_pairs = ("{0}={1}".format(str(t[0]), str(t[1])) for t in self._iterator)
        return "&".join(key_value_pairs)

    def mkstring(self, joiner="&"):
        key_value_pairs = ("{0}={1}".format(str(t[0]), str(t[1])) for t in self._iterator)
        return react(joiner.join(key_value_pairs))
