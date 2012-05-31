'''
Created on 2011/07/11

@author: Keita Oouchi
'''
import sys, os

sys.path.append("./src")

import unittest
from chainreaction.reactor import react, Chainable
from sys import getrefcount as ref

class TestReactor(unittest.TestCase):
    def setUp(self):
        self.ispy3 = True if sys.version >= '3.0' else False

    def iterref(self, obj):
        #alignment
        startref = ref(obj)
        wrap = react(obj)
        self.assertEqual(ref(obj), startref + 1)

        #iter(wrap) => wrap.__iter__ => iter(wrap._iterable)
        itered = iter(wrap)
        self.assertEqual(ref(obj), startref + 2)
        itered = None
        self.assertEqual(ref(obj), startref + 1)

        #'for' statement use __iter__, __iter__ calls iter(self._iterable).
        for temp in wrap:
            self.assertEqual(ref(obj), startref + 2)
        self.assertEqual(ref(obj), startref + 1)
        self.assertEqual(ref(wrap), 2)

    def dictiterref(self, obj):
        self.assertTrue(issubclass(obj.__class__, dict))
        #alignment
        startref = ref(obj)
        wrap = react(obj)
        self.assertEqual(ref(obj), startref + 1)
        """
        In python3.x, 'obj.items()' returns 'dict_items' object.
        By contrast, python2.x returns 'list' object.
        'dict_items' object is a 'view' object, and this is nearly iterator,
        This iterator holds a reference to obj, so reference count is incremented.
        """
        itered = iter(wrap)
        self.assertFalse(issubclass(itered.__class__, Chainable))
        expect = 2 if self.ispy3 else 1
        self.assertEqual(ref(obj), startref + expect)
        itered = None
        self.assertEqual(ref(obj), startref + 1)

        #'for' statement use __iter__, __iter__ calls iter(self._iterator).
        for temp in wrap:
            self.assertEqual(ref(obj), startref + expect)
        self.assertEqual(ref(obj), startref + 1)
        self.assertEqual(ref(wrap), 2)

    def testStr(self):
        teststr = "reftest"
        self.iterref(teststr)
        startref = ref(teststr)
        wrap = react(teststr)
        self.assertEqual(ref(teststr), startref + 1)
        #filter, takewhile, dropwhile, etc refer to new string.
        refalign = 1
        filtered = wrap.filter(lambda c: ord(c) > 0)
        self.assertEqual(ref(teststr), startref + refalign)
        taken = wrap.takewhile(lambda c: ord(c) > 0)
        self.assertEqual(ref(teststr), startref + refalign)
        dropped = wrap.dropwhile(lambda c: ord(c) < 0)
        self.assertEqual(ref(teststr), startref + refalign)
        tr = wrap.takeright(lambda c: ord(c) > 0)
        self.assertEqual(ref(teststr), startref + refalign)

        #map refer to iterator-like
        mapped = wrap.map(lambda c: chr(ord(c) + 1))
        refalign += 1
        self.assertEqual(ref(teststr), startref + refalign)
        self.assertEqual(ref(wrap), 2)
        self.assertEqual(ref(filtered.unwrap), 2)
        self.assertEqual(ref(mapped.unwrap), 2)
        self.assertEqual(ref(taken.unwrap), 2)

        upped = wrap.upper()
        self.assertEqual(ref(teststr), startref + refalign)
        self.assertEqual(ref(wrap), 2)

        wrap = wrap.reverse
        refalign -= 1
        self.assertEqual(ref(teststr), startref + refalign)
        self.assertEqual(ref(wrap.unwrap), 2)

        mapped = None
        self.assertEqual(ref(teststr), startref)

    def testSeq(self):
        testseq = [1, 2, 3]
        self.iterref(testseq)
        startref = ref(testseq)
        wrap = react(testseq)
        self.assertEqual(ref(testseq), startref + 1)
        #filter, map, takewhile, etc... refer to new seq.
        filted = wrap.filter(lambda i: i > 0)
        self.assertEqual(filted.unwrap.__class__, list)
        mapped = wrap.map(lambda i: i + 1)
        taken = wrap.takewhile(lambda i: i > 0)
        self.assertEqual(ref(testseq), startref + 1)
        self.assertEqual(ref(wrap), 2)
        self.assertEqual(ref(filted.unwrap), 2) #passed to ref and filted internal.
        self.assertEqual(ref(mapped.unwrap), 2)
        self.assertEqual(ref(taken.unwrap), 2)

        appended = wrap.append(4)
        self.assertEqual(ref(testseq), startref + 2) #wrap, appended

        sortedwrap = wrap.sort
        self.assertEqual(ref(testseq), startref + 2) #wrap, appended
        self.assertEqual(ref(wrap), 2)

        wrap = wrap.reverse
        self.assertEqual(ref(testseq), startref + 1) #appended
        self.assertEqual(ref(wrap.unwrap), 2)

        appended = None
        self.assertEqual(ref(testseq), startref)

    def testSet(self):
        testset = set([1, 2, 3])
        self.iterref(testset)
        startref = ref(testset)
        wrap = react(testset)
        self.assertEqual(ref(testset), startref + 1)
        #filter, map, takewhile, etc... refer to new set.
        filted = wrap.filter(lambda i: i > 0)
        mapped = wrap.map(lambda i: i + 1)
        taken = wrap.takewhile(lambda i: i > 0)
        self.assertEqual(ref(testset), startref + 1)
        self.assertEqual(ref(wrap), 2)
        self.assertEqual(ref(filted.unwrap), 2) #passed to ref and filted internal.
        self.assertEqual(ref(mapped.unwrap), 2)
        self.assertEqual(ref(taken.unwrap), 2)

        unionized = wrap.union(set([4, 5, 6]))
        self.assertEqual(ref(testset), startref + 1)
        self.assertEqual(ref(wrap), 2)

        wrap = wrap.union(set([4, 5, 6]))
        self.assertEqual(ref(testset), startref)
        self.assertEqual(ref(wrap.unwrap), 2)

    def testDict(self):
        testdict = {"k1":"v1", "k2":""}
        self.dictiterref(testdict)
        startref = ref(testdict)
        wrap = react(testdict)
        self.assertEqual(ref(testdict), startref + 1)
        #filter, map, takewhile, etc... refer to new dict.
        filted = wrap.filter(lambda t: t[1])
        mapped = wrap.map(lambda t: (t[0], t[0] + "=" + t[1]))
        taken = wrap.takewhile(lambda t: t[1])
        self.assertEqual(ref(testdict), startref + 1)
        self.assertEqual(ref(wrap), 2)
        self.assertEqual(ref(filted.unwrap), 2) #passed to ref and filted internal.
        self.assertEqual(ref(mapped.unwrap), 2)
        self.assertEqual(ref(taken.unwrap), 2)

        updated = wrap.update(("k3", "v3"))
        self.assertEqual(ref(testdict), startref + 2) #wrap, updated
        self.assertEqual(ref(wrap), 2)
        self.assertEqual(updated.unwrap, testdict)

        wrap = wrap.update(("k3", "v3"))
        self.assertEqual(ref(testdict), startref + 2)
        self.assertEqual(ref(wrap.unwrap), startref + 2)

    def testIter(self):
        testseq = [1, 2, 3]
        testit = iter(testseq)
        self.iterref(testit)
        startref = ref(testit)
        wrap = react(testit)
        self.assertEqual(ref(testit), startref + 1)
        base = startref + 1
        refalign = 0
        #filter, map, takewhile, dropwhile returns IterChain.
        filted = wrap.filter(lambda i: i > 0)
        refalign += 1
        self.assertEqual(ref(testit), base + refalign)
        mapped = wrap.map(lambda i: i + 1)
        refalign += 1
        self.assertEqual(ref(testit), base + refalign)
        taken = wrap.takewhile(lambda i: i > 0)
        refalign += 1
        self.assertEqual(ref(testit), base + refalign)
        droped = wrap.dropwhile(lambda i: i < 0)
        refalign += 1
        self.assertEqual(ref(testit), base + refalign)

        #takeright, dropright returns SeqChain.
        tr = wrap.takeright(lambda i: i > 0)
        dr = wrap.dropright(lambda i: i < 0)
        self.assertEqual(ref(testit), base + refalign)

        taken = None
        refalign -= 1
        self.assertEqual(ref(testit), base + refalign)
        right = wrap.takeright(lambda i: i < 0)
        self.assertEqual(ref(testit), base + refalign)
        self.assertEqual(ref(wrap), 2)

def suite():
  suite = unittest.TestSuite()
  suite.addTests(unittest.makeSuite(TestReactor))
  return suite

if __name__ == "__main__":
    try:
        from sys import getrefcount
        suite()
    except:
        pass
