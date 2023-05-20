# ==================================================
class TreeItem(object):
    """
    tree item.
    """

    # ==================================================
    def __init__(self, data=None, parent=None):
        """
        initialize the class.

        Args:
            data (Any, optional): item data for each row.
            parent (TreeItem, optional): parent item.
        """
        self.pitem = parent  # parent item
        self.idata = data  # item data
        self.citem = []  # list of child item

    # ==================================================
    def __str__(self):
        return f"{self.idata} ({self.n_child()})"

    # ==================================================
    def level(self):
        """
        find item level.

        Returns:
            int: level of item (top is 0).
        """
        l = 0
        p = self.parent()
        while p is not None:
            l += 1
            p = p.parent()
        return l

    # ==================================================
    def parent(self):
        """
        parent item.

        Returns:
            TreeItem: parent item.
        """
        return self.pitem

    # ==================================================
    def data(self):
        """
        item data.

        Returns:
            Any: item data.
        """
        return self.idata

    # ==================================================
    def setData(self, data):
        """
        set item data.

        Args:
            data (Any): item data.
        """
        self.idata = data

    # ==================================================
    def n_child(self):
        """
        number of child items.

        Returns:
            int: number of child items.
        """
        return len(self.citem)

    # ==================================================
    def append(self, item):
        """
        append child.

        Args:
            item (TreeItem): item.
        """
        self.citem.append(item)

    # ==================================================
    def remove(self, row):
        """
        remove child.

        Args:
            row (int): row to remove.

        Returns:
            bool: True if remove is success.
        """
        if row < 0 or row >= self.n_child():
            return False
        del self.citem[row]
        return True

    # ==================================================
    def child(self, row):
        """
        child item of given row.

        Args:
            row (int): row of child item from 0.

        Returns:
            TreeItem: child item.
        """
        if row < 0 or row >= len(self.citem):
            return None
        return self.citem[row]

    # ==================================================
    def row(self):
        """
        row of item in parent item.

        Returns:
            int: row of item.
        """
        if self.pitem:
            return self.pitem.citem.index(self)
        return 0

    # ==================================================
    def dump(self, indent=4, cr="\n"):
        """
        dump tree.

        Args:
            indent (int, optional): indent.
            cr (str, optional): string for new line.
        """

        def write(top):
            spc = " " * indent * top.level()
            s = spc + str(top) + cr
            for i in range(top.n_child()):
                s += write(top.child(i))
            return s

        s = write(self).strip(" " + cr)
        return s

    # ==================================================
    def add_tree(self, tree):
        """
        add tree data.

        Args:
            tree (list): tree data.
        """
        level = self.level()
        if level == 0 or (type(tree) == list and len(tree) > 1):
            for row, data in enumerate(tree):
                item = TreeItem(None, self)
                self.append(item)
                self.child(row).add_tree(data)
        else:
            if type(tree) == list:
                self.setData(tree[0])
            else:
                self.setData(tree)

    # ==================================================
    @classmethod
    def create(cls, tree):
        """
        create item tree.

        Args:
            tree (list): tree data.

        Returns:
            TreeItem: root item.
        """
        root = TreeItem()
        root.add_tree(tree)

        return root
