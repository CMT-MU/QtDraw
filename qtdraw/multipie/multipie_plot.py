        wp = self.group_combo_vc_wyckoff.currentText()
        bond = self.group_edit_vc_neighbor.text()
        self._virtual_cluster_dialog = show_virtual_cluster(self.plugin._point_group, wp, self)
