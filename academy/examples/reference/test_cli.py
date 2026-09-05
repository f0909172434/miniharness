"""示範可收集的五個案例；學習者需替换成自己 CLI 的實際行為測試。"""
import unittest
from wordcount import word_counts

class WordCountsTests(unittest.TestCase):
    def test_empty(self): self.assertEqual(word_counts(''), [])
    def test_case(self): self.assertEqual(word_counts('A a'), [('a',2)])
    def test_tie(self): self.assertEqual(word_counts('b a'), [('a',1),('b',1)])
    def test_space(self): self.assertEqual(word_counts('a\n\ta'), [('a',2)])
    def test_punctuation(self): self.assertEqual(word_counts('a! a'), [('a',1),('a!',1)])
