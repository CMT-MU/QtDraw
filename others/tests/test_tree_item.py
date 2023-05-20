from qtdraw.core.tree_item import TreeItem

data1 = [["a", ["b", "c"]], ["d"], ["e", "f"]]
data2 = [[2, 3], [0, 1]]
data3 = [[0]]

for data in [data1, data2, data3]:
    root = TreeItem.create(data)
    print(root.dump())
    print("-----")
