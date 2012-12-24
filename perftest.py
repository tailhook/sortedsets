import resource
from time import clock

from sortedsets import SortedSet

def test(size):
    tm = clock()
    ss = SortedSet((str(i), i*10) for i in range(size))
    create_time = clock() - tm
    print("SORTED SET WITH", size, "ELEMENTS", ss._level, "LEVELS")
    print("Memory usage", resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    print("Creation time  ", format(create_time, '10.2f'), "s")
    num = 1000
    step = size // (num + 2)
    items = []
    for i in range(step, size-step, step):
        items.append((str(i), i*10))
    tm = clock()
    for k, v in items:
        del ss[k]
    del_time = num/(clock() - tm)
    tm = clock()
    for k, v in items:
        ss[k] = v
    ins_time = num/(clock() - tm)
    print("Insertion speed", format(ins_time, '10.2f'), "ins/s")
    print("Deletion speed ", format(del_time, '10.2f'), "del/s")

for size in (10000, 100000, 1000000, 10000000):
    test(size)

