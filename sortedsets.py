import random
import reprlib
from collections import namedtuple, MutableMapping
from itertools import islice


empty = object()


class Pointer:
    __slots__ = ('forward', 'span')

    def __init__(self, forward=None, span=0):
        self.forward = forward
        self.span = span

    def __repr__(self):
        if self.forward:
            return '<P {} {!r}>'.format(self.span, self.forward.key)
        else:
            # assert self.span == 0
            return '<P>'


class Item:
    __slots__ = ('key', 'score', 'pointers', 'backward')

    def __init__(self, key, score):
        self.key = key
        self.score = score
        self.pointers = []
        self.backward = None

    def __getitem__(self, i):
        if i == len(self.pointers):
            self.pointers.append(Pointer())
        elif i > len(self.pointers):
            raise RuntimeError("One level at a time required")
        return self.pointers[i]

    def __lt__(self, other):
        return (self.score < other.score or
                self.score == other.score and hash(self.key) < hash(other.key))

    def __le__(self, other):
        return (self.score < other.score or
                self.score == other.score and
                (hash(self.key) < hash(other.key) or self.key == other.key))

    def __repr__(self):
        return '<sortedsets.Item {!r} {!r} {!r}>'.format(
            self.key, self.score, self.pointers)

    def _iter_to(self, stop_item):
        item = self
        while item != stop_item:
            assert item is not None
            yield item
            item = item[0].forward

    def _iter_backwards_to(self, stop_item):
        item = self
        while item != stop_item:
            assert item is not None
            yield item
            item = item.backward


class RankView:
    __slots__ = ('_set',)

    def __init__(self, set):
        self._set = set

    def __getitem__(self, key):
        if isinstance(key, slice):
            set_len = len(self._set)
            start, stop, step = key.indices(set_len)

            if step <= 0:
                raise ValueError("Negative step is useless")
            if stop <= start:
                return self._set.__class__()  # empty set

            startitem = self._set._item_by_index(start)
            stop -= start

            return self._set._from_items(
                islice(startitem._iter_to(None), 0, stop, step))
        else:
            item = self._set._item_by_index(key)
            return item.key

    def __delitem__(self, key):
        if isinstance(key, slice):
            set_len = len(self._set)
            start, stop, step = key.indices(set_len)

            if step != 1:
                raise ValueError("Step is not suported for item deletion")
            if stop <= start:
                return  # nothing to delete

            next, update = self._set._item_and_pointers_by_index(start)
            stop -= start
            for i in range(stop):
                item = next
                next = item[0].forward
                del self._set._mapping[item.key]
                self._set._delete_node(item, update)
        else:
            item, update = self._set._item_and_pointers_by_index(key)
            self._set._delete_node(item, update)


class ScoreView:
    __slots__ = ('_set',)

    def __init__(self, set):
        self._set = set

    def __getitem__(self, key):
        if isinstance(key, slice):
            if key.step != None:
                raise ValueError("Step must be None")
            if(key.start is not None and key.stop is not None and
               key.start >= key.stop) or not len(self._set):
                return self._set.__class__()

            startitem = self._set._header[0].forward
            if key.start is not None:
                if startitem.score < key.start:
                    startitem = self._set._item_by_score_left_incl(key.start)
                    if startitem is None:
                        # means key.start is greater than max score in set
                        return self._set.__class__()

            if key.stop is None:
                return self._set._from_items(startitem._iter_to(None))

            result = self._set.__class__()
            for item in startitem._iter_to(None):
                if item.score >= key.stop:
                    break
                result[item.key] = item.score
            return result
        else:
            raise NotImplementedError('Only slicing by score supported')

    def __delitem__(self, key):
        if isinstance(key, slice):
            if key.step != None:
                raise ValueError("Step must be None")
            if(key.start is not None and key.stop is not None and
               key.start >= key.stop) or not len(self._set):
                return  # nothing to delete

            if key.start is None:
                key.start = self._set._header[0].forward.score
            next, update = self._set._item_and_pointers_by_score_left_incl(
                key.start)
            if next is None:
                # means key.start is greater than max score in set
                return  # nothing to delete

            if key.stop:
                while next and next.score <= key.stop:
                    item = next
                    next = item[0].forward
                    del self._set._mapping[item.key]
                    self._set._delete_node(item, update)
            else:
                while next:
                    item = next
                    next = item[0].forward
                    del self._set._mapping[item.key]
                    self._set._delete_node(item, update)
        else:
            raise NotImplementedError('Only slicing by score supported')


def _random_level():
    """Returns a random level for the new skiplist node

    The return value of this function is between 1 and ZSKIPLIST_MAXLEVEL
    (both inclusive), with a powerlaw-alike distribution where higher
    levels are less likely to be returned.
    """
    level = 1
    while random.random() < 0.25:
        level += 1
    return level


class SortedSet(MutableMapping):
    __slots__ = ('_level', '_mapping', '_header', '_tail',
                 'by_score', 'by_index')

    def __init__(self, source=None):
        self._level = 1
        self._mapping = {}
        self._header = Item(empty, empty)
        self._tail = None
        self.by_index = RankView(self)
        self.by_score = ScoreView(self)
        if source is not None:
            self.update(source)

    @classmethod
    def _from_items(cls, items):
        """Generates a new set from iterator over Item objects

        Usually used to make a new set from ``item._iter_to(other_item)``
        """
        self = cls()
        for item in items:
            self[item.key] = item.score
        return self

    def __iter__(self):
        start = self._header[0].forward  # header is always empty
        if not start:
            return iter(())
        return (item.key for item in start._iter_to(None))

    def __reversed__(self):
        start = self._tail
        if not start:
            return iter(())
        return (item.key for item in start._iter_backwards_to(None))

    def __len__(self):
        return len(self._mapping)


    def __setitem__(self, key, score):
        if key in self:
            del self[key]
            # TODO probably optimize changing a value
        item = Item(key, score)
        self._mapping[key] = item

        rank = [None] * self._level
        update = [None] * self._level
        x = self._header
        for i in range(self._level-1, -1, -1):
            # store rank that is crossed to reach the insert position
            rank[i] = 0 if i == self._level-1 else rank[i+1]
            while x[i].forward and x[i].forward < item:
                rank[i] += x[i].span
                x = x[i].forward
            update[i] = x

        level = _random_level()
        if level > self._level:
            for i in range(self._level, level):
                assert len(rank) == i
                rank.append(0)
                assert len(update) == i
                update.append(self._header)
                update[i][i].span = len(self)
            self._level = level

        x = item
        for i in range(level):
            x[i].forward = update[i][i].forward
            update[i][i].forward = x

            # update span covered by update[i] as x is inserted here
            x[i].span = update[i][i].span - (rank[0] - rank[i])
            update[i][i].span = (rank[0] - rank[i]) + 1

        # increment span for untouched levels
        for i in range(level, self._level):
            update[i][i].span += 1

        x.backward = None if update[0] == self._header else update[0]
        if x[0].forward:
            x[0].forward.backward = x
        else:
            self._tail = x

    def __getitem__(self, key):
        return self._mapping[key].score

    def __delitem__(self, key):
        item = self._mapping.pop(key)
        update = [None] * self._level

        x = self._header
        for i in range(self._level-1, -1, -1):
            while x[i].forward and x[i].forward < item:
                x = x[i].forward
            update[i] = x

        assert item == x[0].forward
        self._delete_node(item, update)

    def _delete_node(self, x, update):
        for i in range(self._level):
            if update[i][i].forward == x:
                update[i][i].span += x[i].span - 1
                update[i][i].forward = x[i].forward
            else:
                update[i][i].span -= 1
            assert update[i][i].span > 0 or not update[i][i].forward, update
        if x[0].forward:
            x[0].forward.backward = x.backward
        else:
            self._tail = x.backward
        while self._level > 1 and not self._header[self._level-1].forward:
            self._level -= 1

    def index(self, key):
        x = self._header
        rank = -1  # first key is always a header (Empty key)
        item = self._mapping[key]
        for i in range(self._level-1, -1, -1):
            while x[i].forward and x[i].forward <= item:
                rank += x[i].span
                x = x[i].forward
            if x.key == key:
                return rank
        raise KeyError(key, score)

    def _item_by_index(self, rank):
        if rank < 0:
            raise IndexError(rank)
        x = self._header
        traversed = -1  # first key is always a header (Empty key)
        for i in range(self._level-1, -1, -1):
            while x[i].forward and x[i].span + traversed <= rank:
                traversed += x[i].span
                x = x[i].forward
            if traversed == rank:
                return x
        raise IndexError(rank)

    def _item_and_pointers_by_index(self, rank):
        if rank < 0:
            raise IndexError(rank)
        x = self._header
        update = [None] * self._level
        traversed = -1  # first key is always a header (Empty key)
        for i in range(self._level-1, -1, -1):
            while x[i].forward and x[i].span + traversed < rank:
                traversed += x[i].span
                x = x[i].forward
            update[i] = x
        x = x[0].forward
        return x, update

    def _item_by_score_left_incl(self, score):
        """Returns left most item scored up to `score` inclusive"""
        # "left" name is analogy to bisect_left
        x = self._header
        for i in range(self._level-1, -1, -1):
            while x[i].forward and x[i].forward.score < score:
                x = x[i].forward
        x = x[0].forward
        return x

    def _item_and_pointers_by_score_left_incl(self, score):
        """Returns left most item scored up to `score` inclusive

        This one returns also ``update`` array to assist in item deletion
        """
        x = self._header
        update = [None] * self._level
        for i in range(self._level-1, -1, -1):
            while x[i].forward and x[i].forward.score < score:
                x = x[i].forward
            update[i] = x
        x = x[0].forward
        return x, update

    def __repr__(self):
        return '<SortedSet {}>'.format(reprlib.Repr().repr_dict(self, 1))


