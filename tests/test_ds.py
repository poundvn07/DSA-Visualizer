from src.core.data_structures import run_ds_operations

# Test Stack
steps = list(run_ds_operations("stack", [{"op":"push","value":10},{"op":"push","value":20},{"op":"pop"}]))
print(f"Stack: {len(steps)} steps, last: {steps[-1].description}")

# Test Queue
steps = list(run_ds_operations("queue", [{"op":"enqueue","value":1},{"op":"enqueue","value":2},{"op":"dequeue"}]))
print(f"Queue: {len(steps)} steps, last: {steps[-1].description}")

# Test LinkedList
steps = list(run_ds_operations("linkedlist", [{"op":"insert_head","value":10},{"op":"insert_tail","value":30},{"op":"search","value":30}]))
print(f"LL: {len(steps)} steps, last: {steps[-1].description}")

# Test BST
steps = list(run_ds_operations("bst", [{"op":"insert","value":50},{"op":"insert","value":30},{"op":"insert","value":70},{"op":"search","value":30}]))
print(f"BST: {len(steps)} steps, last: {steps[-1].description}")
print(f"BST extra keys: {list(steps[-1].extra.keys())}")
