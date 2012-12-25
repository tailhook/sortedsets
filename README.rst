==========
SortedSets
==========


Sorted set is data structure that maps unique keys to scores. The following
operations are allowed on sorted set:

* Iteration in order or scores (both ascending and descending)
* Get score for key (same performance as for dict)
* Get index for key (O(log n), n is sizeof the set)
* Get key for index (O(log n))
* Slicing by index (O(m + log n), m is length of slice)
* Slicing by score (O(m + log n), m is length of slice)
* Item/slice deletion by index and score (same performance as for slicing)
* Insertion with any score has O(log n) performance too

The data structure is modelled closely after Redis' sorted sets. Internally it
consists of a mapping between keys and scores, and a skiplist for scores.

The use cases for SortedSets are following:

* Leaderboard for a game
* Priority queue (that support task deletion)
* Timer list (supports deletion too)
* Caches with TTL-based, LFU or LRU eviction
* Search databases with relevance scores
* Statistics
* Replacement for ``collections.Counter`` with faster ``most_common()``


Example Code
============

Let's model a leaderboard::

    >>> from sortedsets import SortedSet
    >>> ss = SortedSet()

Insert some players into sortedset (with some strange made up scores)::

    >>> for i in range(1, 1000):
    ...    ss['player' + str(i)] = i*10 if i % 2 else i*i
    ...

Let's find out score for player::

    >>> ss['player20'], ss['player21']
    (400, 210)

Let's find out their rating positions::

    >>> ss.index('player20'), ss.index('player21')
    (29, 17)

Let's find out players that have score similar to one's::

    >>> ss['player49']
    490
    >>> ss.by_score[470:511]
    <SortedSet {'player22': 484, 'player47': 470, 'player49': 490, 'player51': 510}>
    >>> for k, v in _.items():
    ...   print(k, v)
    ...
    player47 470
    player22 484
    player49 490
    player51 510

Let's find out players on the rating page 25::

    >>> page, pagesize = 25, 10
    >>> ss.by_index[page*pagesize:page*pagesize + pagesize]
    <SortedSet {'player437': 4370, 'player439': 4390, 'player441': 4410, 'player443': 4430, ...}>
    >>> len(_)
    10

