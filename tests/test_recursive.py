from src.core.algorithms import quick_sort_gen, merge_sort_gen, heap_sort_gen

steps = list(quick_sort_gen([8, 3, 1, 7, 0, 10, 2]))
print(f"QS: {len(steps)} steps")
for s in steps[:3]:
    print(f"  {s.type}: extra={s.extra}")

steps = list(merge_sort_gen([38, 27, 43, 3]))
print(f"MS: {len(steps)} steps")
for s in steps[:3]:
    print(f"  {s.type}: extra={s.extra}")

steps = list(heap_sort_gen([4, 10, 3]))
print(f"HS: {len(steps)} steps, extra={steps[0].extra}")
