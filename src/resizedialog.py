#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# This file is part of pdf-tools
#
# Copyright (C) 2012-2016 Lorenzo Carbonell
# lorenzo.carbonell.cerezo@gmail.com
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import gi
try:
    gi.require_version('Gtk', '3.0')
except Exception as e:
    print(e)
    exit(1)
from gi.repository import Gtk
import tools
import comun
from comun import _


class ResizeDialog(Gtk.Dialog):
    def __init__(self, title, afile):
        Gtk.Dialog.__init__(
            self,
            title,
            None,
            Gtk.DialogFlags.MODAL |
            Gtk.DialogFlags.DESTROY_WITH_PARENT,
            (Gtk.STOCK_OK, Gtk.ResponseType.ACCEPT,
             Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL))
        self.set_size_request(350, 150)
        self.set_resizable(False)
        self.set_icon_from_file(comun.ICON)
        self.connect('destroy', self.close_application)
        vbox0 = Gtk.VBox(spacing=5)
        vbox0.set_border_width(5)
        self.get_content_area().add(vbox0)
        notebook = Gtk.Notebook()
        vbox0.add(notebook)
        frame1 = Gtk.Frame()
        notebook.append_page(frame1, tab_label=Gtk.Label(_('Pages')))
        table1 = Gtk.Table(rows=3, columns=2, homogeneous=False)
        table1.set_border_width(5)
        table1.set_col_spacings(5)
        table1.set_row_spacings(5)
        frame1.add(table1)
        #
        label1 = Gtk.Label(_('Paper size')+':')
        label1.set_tooltip_text(_('Select the size of the output file'))
        label1.set_alignment(0, 0.5)
        table1.attach(label1, 0, 1, 0, 1,
                      xoptions=Gtk.AttachOptions.FILL,
                      yoptions=Gtk.AttachOptions.SHRINK)
        #
        label2 = Gtk.Label(_('Orientation')+':')
        label2.set_tooltip_text(_('Select the orientation of the page'))
        label2.set_alignment(0, .5)
        table1.attach(label2, 0, 1, 1, 2,
                      xoptions=Gtk.AttachOptions.FILL,
                      yoptions=Gtk.AttachOptions.SHRINK)
        #
        label3 = Gtk.Label(_('Output file')+':')
        label3.set_tooltip_text(_('Select the output file'))
        label3.set_alignment(0, .5)
        table1.attach(label3, 0, 1, 2, 3,
                      xoptions=Gtk.AttachOptions.FILL,
                      yoptions=Gtk.AttachOptions.SHRINK)
        #
        liststore = Gtk.ListStore(str, float, float)
        liststore.append([_('A0'), 2383.9, 3370.4])
        liststore.append([_('A1'), 1683.8, 2383.9])
        liststore.append([_('A2'), 1190.6, 1683.8])
        liststore.append([_('A3'), 841.9, 1190.6])
        liststore.append([_('A4'), 595.3, 841.9])
        liststore.append([_('A5'), 419.5, 595.3])
        liststore.append([_('A6'), 297.6, 419.5])
        liststore.append([_('A7'), 209.8, 297.6])
        liststore.append([_('A8'), 147.4, 209.8])
        liststore.append([_('A9'), 104.9, 147.4])
        liststore.append([_('A10'), 73.7, 104.9])
        liststore.append([_('B0'), 2834.6, 73.7])
        liststore.append([_('B1'), 2004.1, 2834.6])
        liststore.append([_('B2'), 1417.3, 2004.1])
        liststore.append([_('B3'), 1000.6, 1417.3])
        liststore.append([_('B4'), 708.7, 1000.6])
        liststore.append([_('B5'), 498.9, 708.7])
        liststore.append([_('B6'), 354.3, 498.9])
        liststore.append([_('B7'), 249.4, 354.3])
        liststore.append([_('B8'), 175.7, 249.4])
        liststore.append([_('B9'), 124.7, 175.7])
        liststore.append([_('B10'), 87.9, 124.7])
        liststore.append([_('Letter (8 1/2x11)'), 612.0, 792.0])
        liststore.append([_('Note (8 1/2x11)'), 612.0, 792.0])
        liststore.append([_('Legal (8 1/2x14)'), 612.0, 1008.0])
        liststore.append([_('Executive (8 1/4x10 1/2)'), 522.0, 756.0])
        liststore.append([_('Halfetter (5 1/2x8 1/2)'), 396.0, 612.0])
        liststore.append([_('Halfexecutive (5 1/4x7 1/4)'), 378.0, 522.0])
        liststore.append([_('11x17 (11x17)'), 792.0, 1224.0])
        liststore.append([_('Statement (5 1/2x8 1/2)'), 396.0, 612.0])
        liststore.append([_('Folio (8 1/2x13)'), 612.0, 936.0])
        liststore.append([_('10x14 (10x14)'), 720.0, 1008.0])
        liststore.append([_('Ledger (17x11)'), 1224.0, 792.0])
        liststore.append([_('Tabloid (11x17)'), 792.0, 1224.0])
        self.entry1 = Gtk.ComboBox.new_with_model(model=liststore)
        renderer_text = Gtk.CellRendererText()
        self.entry1.pack_start(renderer_text, True)
        self.entry1.add_attribute(renderer_text, "text", 0)
        self.entry1.set_active(0)
        table1.attach(self.entry1, 1, 2, 0, 1,
                      xoptions=Gtk.AttachOptions.FILL,
                      yoptions=Gtk.AttachOptions.SHRINK)
        liststore = Gtk.ListStore(str)
        liststore.append([_('Vertical')])
        liststore.append([_('Horizontal')])
        self.entry2 = Gtk.ComboBox.new_with_model(model=liststore)
        renderer_text = Gtk.CellRendererText()
        self.entry2.pack_start(renderer_text, True)
        self.entry2.add_attribute(renderer_text, "text", 0)
        self.entry2.set_active(0)
        table1.attach(self.entry2, 1, 2, 1, 2,
                      xoptions=Gtk.AttachOptions.FILL,
                      yoptions=Gtk.AttachOptions.SHRINK)
        self.output_file = Gtk.Button.new_with_label(afile)
        self.output_file.connect('clicked', self.on_button_output_file_clicked)
        table1.attach(self.output_file, 1, 2, 2, 3,
                      xoptions=Gtk.AttachOptions.FILL,
                      yoptions=Gtk.AttachOptions.SHRINK)
        self.show_all()

    def on_button_output_file_clicked(self, widget):
        file_out = tools.dialog_save_as(
            _('Select file to save new file'), self.output_file.get_label())
        if file_out:
            self.output_file.set_label(file_out)

    def get_file_out(self):
        return self.output_file.get_label()

    def get_size(self):
        tree_iter = self.entry1.get_active_iter()
        if tree_iter is not None:
            model = self.entry1.get_model()
            w = model[tree_iter][1]
            h = model[tree_iter][2]
            return w, h
        return None

    def is_vertical(self):
        tree_iter = self.entry2.get_active_iter()
        if tree_iter is not None:
            model = self.entry2.get_model()
            vertical = model[tree_iter][0]
            if vertical == _('Vertical'):
                return True
        return False

    def close_application(self, widget):
        self.hide()

if __name__ == '__main__':
    dialog = ResizeDialog('Test', 'afile')
    dialog.run()
