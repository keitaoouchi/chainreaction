'''
Created on 2011/07/11

@author: Keita Oouchi
'''
import sys, os

sys.path.append("./src")

import unittest
from chainreaction.reactor import react, SeqChain, SetChain, StrChain, Chainable, DictChain, IterChain
try:
    from collections import OrderedDict
except ImportError:
    from utils import OrderedDict

class TestReactor(unittest.TestCase):

    def setUp(self):
        self.ispy3 = True if sys.version >= '3.0' else False
        self.ispy26 = True if sys.version < '2.7' else False

    def assertType(self, obj, cls):
        if self.ispy26:
            self.assertTrue(isinstance(obj, cls))
        else:
            self.assertIsInstance(obj, cls)

    def testAttrError(self):
        targets = []
        targets.append(1)
        targets.append(True)
        targets.append(False)
        targets.append(None)
        targets.append(object)
        for elem in targets:
            self.assertRaises(AttributeError, react, elem)

    def testAttrAcceptable(self):
        targets = []
        targets.append(str())
        targets.append("")
        targets.append("123")
        targets.append(list())
        targets.append([])
        targets.append([1, 2, 3])
        targets.append(tuple())
        targets.append(())
        targets.append((1, 2, 3))
        targets.append(set())
        targets.append({})
        targets.append(set([1, 2, 3]))
        targets.append(dict())
        targets.append({"1":1, "2":2, "3":3})
        targets.append(bytes())
        targets.append(b"123")
        class StrChild(str):pass
        class ListChild(list):pass
        class TupleChild(tuple):pass
        class SetChild(set):pass
        class DictChild(set):pass
        targets.append(StrChild())
        targets.append(ListChild())
        targets.append(SetChild())
        targets.append(DictChild())
        for elem in targets:
            target = react(elem)
            self.assertTrue(issubclass(type(target), Chainable))
            self.assertEqual(type(elem), target.type)

    def testStr(self):
        original = "hello world"
        wrapped = react(original)

        #for expression
        self.assertEqual(wrapped.unwrap, "".join([c for c in wrapped]))

        #__repr__
        self.assertEqual(str(wrapped), "'hello world':StrChain")

        #__getitem__
        self.assertEqual(wrapped[0].type, str)
        self.assertEqual(wrapped[0].unwrap, "h")

        #tostring & mkstring
        self.assertTrue(wrapped.tostring is original)
        self.assertEqual(wrapped.mkstring(",").unwrap, "h,e,l,l,o, ,w,o,r,l,d")

        #dump
        self.assertEqual(wrapped.dump, "[Dumped Information]\nStrChain\nstr\nhello world")

        #forall
        forall = wrapped.forall(lambda c: ord(c) >= ord(" "))
        self.assertTrue(forall)
        forall = wrapped.forall(lambda c: ord(c) != ord(" "))
        self.assertFalse(forall)

        #forany
        forany = wrapped.forany(lambda c: ord(c) == ord(" "))
        self.assertTrue(forany)
        forany = wrapped.forany(lambda c: ord(c) == ord("?"))
        self.assertFalse(forany)

        #filter returns str wrapped obj.
        filtered = wrapped.filter(lambda x: ord(x) > ord('l'))
        self.assertEqual(filtered.type, str)
        self.assertType(filtered, StrChain)
        self.assertEqual(filtered.counts(), 4)

        #map returns map wrapped obj.
        mapped = wrapped.map(lambda x: ord(x))
        self.assertTrue(mapped.isiterator)
        self.assertType(mapped, IterChain)
        self.assertEqual(mapped.counts(), 11)

        #take returns str wrapped obj.
        taken = wrapped.takewhile(lambda x: x > ' ')
        self.assertEqual(taken.type, str)
        self.assertType(taken, StrChain)
        self.assertEqual(taken.counts(), 5)

        #takeright
        taken = wrapped.takeright(lambda x: x > ' ')
        self.assertEqual(taken.type, str)
        self.assertType(taken, StrChain)
        self.assertEqual(taken.unwrap, "world")

        #drop returns str wrapped obj.
        dropped = wrapped.dropright(lambda x: x > ' ')
        self.assertEqual(dropped.type, str)
        self.assertType(dropped, StrChain)
        self.assertEqual(dropped.counts(), 6)

        #dropwhile
        dropped = wrapped.dropwhile(lambda c: c != ' ')
        self.assertEqual(dropped.type, str)
        self.assertType(dropped, StrChain)
        self.assertEqual(dropped.unwrap, " world")

        #contains returns true or false
        self.assertTrue(wrapped.contains(" "))
        self.assertFalse(wrapped.contains("?"))

        #counts returns int
        self.assertEqual(wrapped.counts(lambda c: c.isspace()), 1)

        #reverse returns str wrapped obj.
        reversed = wrapped.reverse
        self.assertEqual(reversed.type, str)
        self.assertType(dropped, StrChain)
        self.assertEqual(reversed.unwrap, "dlrow olleh")

        #original method's of wrapped obj returns its type of return value wrapped.
        splitted = wrapped.split(" ")
        self.assertEqual(splitted.type, list)
        self.assertType(splitted, SeqChain)
        self.assertEqual(splitted.counts(), 2)
        self.assertEqual(splitted.mkstring().unwrap, "helloworld")

        tobewrapped = "hello"
        wrapped = react(tobewrapped)
        wrapped = wrapped.upper().map(lambda c: ord(c))
        self.assertEqual([chr(c) for c in wrapped.unwrap],
                         [c for c in tobewrapped.upper()])

        tobewrapped = "hello"
        wrapped = react(bytearray(tobewrapped, encoding="UTF-8"))
        self.assertEqual(wrapped.tostring, tobewrapped)

    def testDict(self):
        original = OrderedDict()
        original["k1"] = "v1"
        original["k2"] = "v2"
        wrapped = react(original)

        self.assertEqual(wrapped.mkstring("&").unwrap, "k1=v1&k2=v2")
        self.assertEqual(wrapped.tostring, "k1=v1&k2=v2")

        #for statement
        expect = ["{0}={1}".format(k, v) for k, v in wrapped]
        self.assertEqual("&".join(expect), "k1=v1&k2=v2")

        #__getitem__
        gotten = wrapped["k1"]
        self.assertEqual(gotten.type, str)
        self.assertTrue(issubclass(gotten.__class__, StrChain))
        self.assertEqual(gotten.unwrap, "v1")
        wrapped2 = react({"k":1})
        self.assertEqual(wrapped2["k"], 1)

        #filter
        filtered = wrapped.filter(lambda t: t[1] == "v1")
        self.assertEqual(filtered.type, OrderedDict)
        self.assertTrue(issubclass(filtered.__class__, DictChain))
        self.assertEqual(filtered.mkstring().unwrap, "k1=v1")

        #map
        mapped = wrapped.map(lambda t: (t[0], " "))
        self.assertEqual(mapped.type, OrderedDict)
        self.assertTrue(issubclass(mapped.__class__, DictChain))
        self.assertEqual(mapped.mkstring().unwrap, "k1= &k2= ")
        self.assertEqual(mapped.tostring, "k1= &k2= ")

        #takewhile
        taken = wrapped.takewhile(lambda t: t[1] != "v2")
        self.assertEqual(taken.type, OrderedDict)
        self.assertType(taken, DictChain)
        self.assertEqual(taken.mkstring().unwrap, "k1=v1")

        #takeright
        taken = wrapped.takeright(lambda t: t[1] == "v2")
        self.assertEqual(taken.type, OrderedDict)
        self.assertType(taken, DictChain)
        self.assertEqual(taken.mkstring().unwrap, "k2=v2")

        #dropwhile
        taken = wrapped.dropwhile(lambda t: t[1] == "v1")
        self.assertEqual(taken.type, OrderedDict)
        self.assertType(taken, DictChain)
        self.assertEqual(taken.mkstring().unwrap, "k2=v2")

        #dropright
        taken = wrapped.dropright(lambda t: t[1] == "v2")
        self.assertEqual(taken.type, OrderedDict)
        self.assertType(taken, DictChain)
        self.assertEqual(taken.mkstring().unwrap, "k1=v1")

        cleared = wrapped.clear()
        self.assertEqual(cleared.type, OrderedDict)
        self.assertType(cleared, DictChain)
        self.assertEqual(cleared.counts(), 0)

        original = {"k1": 1, "k2": 2, "k3": 3}
        #forall
        tf = react(original).forall(lambda t: t[1] > 0)
        self.assertTrue(tf)
        #forany
        tf = react(original).forany(lambda t: t[1] == 2)
        self.assertTrue(tf)
        #contains
        tf = react(original).contains(("k2", 2))
        self.assertTrue(tf)
        #counts
        count = react(original).counts(lambda t: t[1] % 2)
        self.assertEqual(count, 2)
        #iter returns iter(self._iterable)
        it = iter(react(original))
        self.assertFalse(issubclass(it.__class__, Chainable))

    def testSet(self):
        original = set([1, 2, 3])
        wrapped = react(original)

        self.assertEqual(wrapped.type, set)
        self.assertType(wrapped, SetChain)

        #for statement
        expect = set([x for x in wrapped])
        self.assertEqual(expect, wrapped.unwrap)

        #filter
        filtered = wrapped.filter(lambda x: x > 2)
        self.assertEqual(filtered.type, set)
        self.assertType(filtered, SetChain)
        self.assertEqual(filtered.counts(), 1)

        #map
        mapped = wrapped.map(lambda x: x * 2)
        self.assertEqual(mapped.type, set)
        self.assertType(mapped, SetChain)
        self.assertEqual(mapped.reduce(lambda x, y: x + y), 12)

        #takewhile
        taken = wrapped.takewhile(lambda x: x < 2)
        self.assertEqual(taken.type, set)
        self.assertType(taken, SetChain)
        self.assertEqual(taken.counts(), 1)

        #takeright
        taken = wrapped.takeright(lambda x: x > 2)
        self.assertEqual(taken.type, set)
        self.assertType(taken, SetChain)
        self.assertEqual(taken.counts(), 1)

        #dropwhile
        dropped = wrapped.dropwhile(lambda x: x < 2)
        self.assertEqual(dropped.type, set)
        self.assertType(dropped, SetChain)
        self.assertEqual(dropped.counts(), 2)

        #dropright
        dropped = wrapped.dropright(lambda x: x > 2)
        self.assertEqual(dropped.type, set)
        self.assertType(dropped, SetChain)
        self.assertEqual(dropped.counts(), 2)

        unionized = wrapped.union(set([4, 5, 6]))
        self.assertEqual(unionized.type, set)
        self.assertType(unionized, SetChain)
        self.assertEqual(unionized.unwrap, set([1, 2, 3, 4, 5, 6]))

        self.assertEqual(len(wrapped.tostring), len(original))

        #min & max
        self.assertEqual(wrapped.min, 1)
        self.assertEqual(wrapped.max, 3)

        #forall
        tf = react(original).forall(lambda x: x > 0)
        self.assertTrue(tf)
        #forany
        tf = react(original).forany(lambda x: x == 2)
        self.assertTrue(tf)
        #contains
        tf = react(original).contains(2)
        self.assertTrue(tf)
        #counts
        count = react(original).counts(lambda x: x % 2)
        self.assertEqual(count, 2)
        #mkstring
        string = react(original).mkstring(",")
        self.assertEqual(string.unwrap, "1,2,3")
        #iter returns iter(self._iterable)
        it = iter(react(original))
        self.assertFalse(issubclass(it.__class__, Chainable))

    def testSeq(self):
        original = [1, 2, 3]
        wrapped = react(original)

        #for statement
        self.assertEqual(wrapped.unwrap, [i for i in wrapped])

        #__getitem__
        self.assertType(wrapped[0], int)

        #filter
        filtered = wrapped.filter(lambda x: x > 2)
        self.assertEqual(filtered.type, list)
        self.assertType(filtered, SeqChain)
        self.assertEqual(filtered.counts(), 1)

        #map
        mapped = wrapped.map(lambda x: x * 2)
        self.assertEqual(mapped.type, list)
        self.assertType(mapped, SeqChain)
        self.assertEqual(mapped.reduce(lambda x, y: x + y), 12)

        #takewhile
        taken = wrapped.takewhile(lambda x: x < 2)
        self.assertEqual(taken.type, list)
        self.assertType(taken, SeqChain)
        self.assertEqual(taken.counts(), 1)

        #takeright
        taken = wrapped.takeright(lambda x: x > 2)
        self.assertEqual(taken.type, list)
        self.assertType(taken, SeqChain)
        self.assertEqual(taken.counts(), 1)

        #dropwhile
        dropped = wrapped.dropwhile(lambda x: x < 2)
        self.assertEqual(taken.type, list)
        self.assertType(taken, SeqChain)
        self.assertEqual(taken.counts(), 1)

        #dropright
        dropped = wrapped.dropright(lambda x: x > 2)
        self.assertEqual(taken.type, list)
        self.assertType(taken, SeqChain)
        self.assertEqual(taken.counts(), 1)

        #list.append
        appended = wrapped.append(4)
        self.assertEqual(appended.type, list)
        self.assertType(appended, SeqChain)
        self.assertEqual(appended.counts(), 4)
        self.assertEqual(wrapped.counts(), 4)

        #list to set
        converted = wrapped.toset
        self.assertEqual(converted.type, set)
        self.assertType(converted, SetChain)

        #sort
        sorted = react([3, 2, 1]).sort
        self.assertEqual(sorted.type, list)
        self.assertType(sorted, SeqChain)
        self.assertEqual(sorted.unwrap, [1, 2, 3])

        #reverse
        reversed = react([1, 2, 3]).reverse
        self.assertEqual(reversed.type, list)
        self.assertType(reversed, SeqChain)
        self.assertEqual(reversed.unwrap, [3, 2, 1])

        #accumulate
        accumed = react([1, 2, 3]).accumulate(lambda x, y: x * y)
        self.assertEqual(accumed.type, list)
        self.assertType(accumed, SeqChain)
        self.assertEqual(accumed.unwrap, [1, 2, 6])

        #forall
        tf = react([1, 2, 3]).forall(lambda x: x > 0)
        self.assertTrue(tf)
        #forany
        tf = react([1, 2, 3]).forany(lambda x: x == 2)
        self.assertTrue(tf)
        #contains
        tf = react([1, 2, 3]).contains(2)
        self.assertTrue(tf)
        #counts
        count = react([1, 2, 3]).counts(lambda x: x % 2)
        self.assertEqual(count, 2)
        #mkstring
        string = react([1, 2, 3]).mkstring(",")
        self.assertEqual(string.unwrap, "1,2,3")
        #iter returns iter(self._iterable)
        it = iter(react([1, 2, 3]))
        self.assertFalse(issubclass(it.__class__, Chainable))

    def testIter(self):
        original = iter([1, 2, 3])
        wrapped = react(original)
        expect = "__next__" if self.ispy3 else "next"
        #__next__:py3.x, next:py2.x
        self.assertTrue(hasattr(wrapped._iterator, expect))
        self.assertType(wrapped, IterChain)

        #iterator was consumed.
        self.assertEqual(wrapped.counts(), 3)
        itercount = 0
        for x in original:
            itercount += 1
        self.assertEqual(itercount, 0)

        #for statement
        wrapped = react(iter([1, 2, 3]))
        self.assertEqual([i for i in wrapped], [1, 2, 3])

        #map,filter returns IterChain.
        wrapped = react(iter([1, 2, 3]))
        mapped = wrapped.map(lambda x: x * 2)
        self.assertType(mapped, IterChain)
        self.assertTrue(mapped.isiterator)
        self.assertEqual(mapped.reduce(lambda x, y:x + y), 12)

        wrapped = react(iter([1, 2, 3]))
        filtered = wrapped.filter(lambda x: x >= 2)
        self.assertType(filtered, IterChain)
        self.assertTrue(filtered.isiterator)
        self.assertEqual(filtered.reduce(lambda x, y: x + y), 5)

        #takewhile, takeright returns IterChain.
        wrapped = react(iter([1, 2, 3]))
        taken = wrapped.takewhile(lambda x: x < 2)
        self.assertTrue(taken.isiterator)
        self.assertType(taken, IterChain)
        self.assertEqual(taken.counts(), 1)
        wrapped = react(iter([1, 2, 3]))
        taken = wrapped.takeright(lambda x: x >= 2)
        self.assertTrue(taken.isiterator)
        self.assertType(taken, IterChain)
        self.assertEqual(taken.counts(), 2)

        #dropwhile, dropright also returns IterChain
        wrapped = react(iter([1, 2, 3]))
        dropped = wrapped.dropwhile(lambda x: x <= 2)
        self.assertTrue(dropped.isiterator)
        self.assertType(dropped, IterChain)
        self.assertEqual(dropped.counts(), 1)
        wrapped = react(iter([1, 2, 3]))
        dropped = wrapped.dropright(lambda x: x >= 2)
        self.assertTrue(dropped.isiterator)
        self.assertType(dropped, IterChain)
        self.assertEqual(dropped.counts(), 1)

        #type converting
        wrapped = react(iter([1, 2, 3]))
        listed = wrapped.tolist
        self.assertEqual(listed.type, list)
        self.assertType(listed, SeqChain)

        wrapped = react(iter([1, 2, 3]))
        tupled = wrapped.totuple
        self.assertEqual(tupled.type, tuple)
        self.assertType(tupled, SeqChain)

        wrapped = react(iter([1, 2, 3]))
        setted = wrapped.toset
        self.assertEqual(setted.type, set)
        self.assertType(setted, SetChain)

        #forall
        tf = react(iter([1, 2, 3])).forall(lambda x: x > 0)
        self.assertTrue(tf)
        #forany
        tf = react(iter([1, 2, 3])).forany(lambda x: x == 2)
        self.assertTrue(tf)
        #contains
        tf = react(iter([1, 2, 3])).contains(2)
        self.assertTrue(tf)
        #counts
        count = react(iter([1, 2, 3])).counts(lambda x: x % 2)
        self.assertEqual(count, 2)
        #mkstring
        string = react(iter([1, 2, 3])).mkstring(",")
        self.assertEqual(string.unwrap, "1,2,3")
        #iter returns iter(self._iterable), iterator itself.
        it = iter(react(iter([1, 2, 3])))
        self.assertFalse(issubclass(it.__class__, Chainable))

    def testFile(self):
        #file iteration
        src1 = "used_in_test.data"
        src2 = os.path.join("test", src1)
        src = src1 if os.path.exists(src1) else src2
        if os.path.exists(src):
            f = open(src)
            filechain = react(f)
            self.assertType(filechain, Chainable)
            self.assertEqual(filechain.counts(), 9)
            filechain.close()
            self.assertRaises(ValueError, filechain.read)
            self.assertTrue(f.closed)

            f = open(src)
            result = []
            with react(f) as filechain:
                filechain.foreach(lambda ln: result.append(ln))
            self.assertTrue(f.closed)
            self.assertEqual(len(result), 9)

            with open(src) as f:
                wrapped = react(f)
                contents = [ln for ln in wrapped]
                self.assertEqual("".join(contents).replace("\n", ""), "123456789")
                self.assertFalse(f.closed)
            self.assertTrue(f)
            self.assertTrue(wrapped.unwrap.closed)

            f = open(src)
            with react(f) as fc:
                filtered = fc.filter(lambda c: int(c) % 2 == 0)
                self.assertTrue(filtered.isiterator)
                self.assertType(filtered, IterChain)
                self.assertEqual(filtered.mkstring().unwrap.replace("\n", ""), "2468")

            f = open(src)
            with react(f) as fc:
                mapped = fc.map(lambda c: c.replace("\n", ""))
                self.assertTrue(mapped.isiterator)
                self.assertType(mapped, IterChain)
                self.assertEqual(mapped.mkstring().unwrap, "123456789")

            f = open(src)
            with react(f) as fc:
                taken = fc.takewhile(lambda c: int(c) < 5)
                self.assertTrue(taken.isiterator)
                self.assertType(taken, IterChain)
                self.assertEqual(taken.mkstring().unwrap.replace("\n", ""), "1234")

            f = open(src)
            with react(f) as fc:
                taken = fc.takeright(lambda c: int(c) > 5)
                self.assertTrue(taken.isiterator)
                self.assertType(taken, IterChain)
                self.assertEqual(taken.mkstring().unwrap.replace("\n", ""), "6789")

            f = open(src)
            with react(f) as fc:
                dropped = fc.dropwhile(lambda c: int(c) < 5)
                self.assertTrue(dropped.isiterator)
                self.assertType(dropped, IterChain)
                self.assertEqual(dropped.mkstring().unwrap.replace("\n", ""), "56789")

            f = open(src)
            with react(f) as fc:
                dropped = fc.dropright(lambda c: int(c) > 5)
                self.assertTrue(dropped.isiterator)
                self.assertType(dropped, IterChain)
                self.assertEqual(dropped.mkstring().unwrap.replace("\n", ""), "12345")

            #forall
            with open(src) as f:
                tf = react(f).forall(lambda c: int(c) > 0)
                self.assertTrue(tf)
            #forany
            with open(src) as f:
                tf = react(f).forany(lambda c: int(c) == 2)
                self.assertTrue(tf)
            #contains
            with open(src) as f:
                tf = react(f).contains("2\n")
                self.assertTrue(tf)
            #counts
            with open(src) as f:
                count = react(f).counts(lambda c: int(c) < 5)
                self.assertEqual(count, 4)
            #mkstring
            with open(src) as f:
                string = react(f).mkstring().replace("\n", "")
                self.assertEqual(string.unwrap, "123456789")
            #iter returns iter(self._iterable), iterator itself.
            with open(src) as f:
                wrap = react(f)
                it = iter(wrap)
                self.assertEqual(it.__class__, f.__class__)
                self.assertFalse(issubclass(it.__class__, Chainable))

    def testPercentEncoding(self):
        test = bytearray("hello world-._~", encoding="UTF-8")
        wrapped = react(test)
        safe = set()
        react("0123456789").foreach(lambda c: safe.add(ord(c)))
        react(range(ord('a'), ord('z') + 1)).foreach(lambda b: safe.add(b))
        react(range(ord('A'), ord('Z') + 1)).foreach(lambda b: safe.add(b))
        react("-._~").foreach(lambda c: safe.add(ord(c)))
        test = wrapped.map(
            lambda b: b if b > 0 else 256 + b).map(
            lambda i: '+' if chr(i).isspace() else chr(i) if i in safe else "%{0:x}".format(i))
        self.assertEqual(test.mkstring().unwrap, "hello+world-._~")

def suite():
  suite = unittest.TestSuite()
  suite.addTests(unittest.makeSuite(TestReactor))
  return suite

if __name__ == "__main__":
    suite()
