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
    gi.require_version('Poppler', '0.18')
except Exception as e:
    print(e)
    exit(1)
from gi.repository import GObject
from gi.repository import Gtk
from gi.repository import Gdk
from gi.repository import GdkPixbuf
from gi.repository import Poppler
from comun import ROTATE_000, ROTATE_090, ROTATE_180, ROTATE_270
from comun import MIMETYPES_PDF, MIMETYPES_PNG
from comun import MMTOPNG, MMTOPIXEL
from comun import _
import os
import shutil
import cairo
import tempfile
import mimetypes
import shlex
import subprocess
from urllib import unquote_plus

mimetypes.init()


def get_pages_from_ranges(ranges):
    pages = []
    for rang in ranges:
        if len(rang) > 1:
            for i in range(rang[0], rang[1]+1):
                if i not in pages:
                    pages.append(i)
        else:
            if not rang[0] in pages:
                pages.append(rang[0])
    return pages


def create_temp_file():
    return tempfile.mkstemp(prefix='tmp_filemanager_pdf_tools_')[1]


def dialog_save_as_image(title, original_file):
    dialog = Gtk.FileChooserDialog(title,
                                   None,
                                   Gtk.FileChooserAction.SAVE,
                                   (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                    Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
    dialog.set_default_response(Gtk.ResponseType.OK)
    dialog.set_current_folder(os.path.dirname(original_file))
    dialog.set_filename(original_file)
    for aMimetype in MIMETYPES_IMAGE.keys():
        filter = Gtk.FileFilter()
        filter.set_name(aMimetype)
        for mime_type in MIMETYPES_IMAGE[aMimetype]['mimetypes']:
            filter.add_mime_type(mime_type)
        for pattern in MIMETYPES_IMAGE[aMimetype]['patterns']:
            filter.add_pattern(pattern)
        dialog.add_filter(filter)
    if dialog.run() == Gtk.ResponseType.OK:
        filename = dialog.get_filename()
    else:
        filename = None
    dialog.destroy()
    return filename


def dialog_save_as(title, original_file):
    dialog = Gtk.FileChooserDialog(title,
                                   None,
                                   Gtk.FileChooserAction.SAVE,
                                   (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                    Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
    dialog.set_default_response(Gtk.ResponseType.OK)
    dialog.set_current_folder(os.path.dirname(original_file))
    dialog.set_filename(original_file)
    for mimetype in MIMETYPES_PDF:
        filter = Gtk.FileFilter()
        filter.set_name(_('Pdf files'))
        filter.add_mime_type(mimetype)
        for pattern in mimetypes.guess_all_extensions(mimetype):
            filter.add_pattern('*'+pattern)
        dialog.add_filter(filter)
    if dialog.run() == Gtk.ResponseType.OK:
        filename = dialog.get_filename()
        if not filename.endswith('.pdf'):
            filename += '.pdf'
    else:
        filename = None
    dialog.destroy()
    return filename


def dialog_save_as_text(title, original_file):
    dialog = Gtk.FileChooserDialog(title,
                                   None,
                                   Gtk.FileChooserAction.SAVE,
                                   (Gtk.STOCK_CANCEL, Gtk.ResponseType.CANCEL,
                                    Gtk.STOCK_OPEN, Gtk.ResponseType.OK))
    dialog.set_default_response(Gtk.ResponseType.OK)
    dialog.set_current_folder(os.path.dirname(original_file))
    dialog.set_filename(original_file)
    filter = Gtk.FileFilter()
    filter.set_name(_('Text file'))
    filter.add_mime_type('text/plain')
    filter.add_pattern('*.txt')
    dialog.add_filter(filter)
    dialog.set_filter(filter)
    if dialog.run() == Gtk.ResponseType.OK:
        filename = dialog.get_filename()
        if not filename.endswith('.txt'):
            filename += '.txt'
    else:
        filename = None
    dialog.destroy()
    return filename


def create_image_surface_from_file(filename, zoom=1.0):
    pixbuf = GdkPixbuf.Pixbuf.new_from_file(filename)
    return create_image_surface_from_pixbuf(pixbuf, zoom)


def create_image_surface_from_pixbuf(pixbuf, zoom=1.0):
    surface = cairo.ImageSurface(
        cairo.FORMAT_ARGB32, pixbuf.get_width(), pixbuf.get_height())
    context = cairo.Context(surface)
    context.save()
    context.scale(zoom, zoom)
    Gdk.cairo_set_source_pixbuf(context, pixbuf, 0, 0)
    context.paint()
    context.restore()
    return surface


def convert_pdf_to_png(file_in):
    document = Poppler.Document.new_from_file('file://' + file_in, None)
    number_of_pages = document.get_n_pages()
    if number_of_pages > 0:
        file_out, ext = os.path.splitext(file_in)
        for i in range(0, number_of_pages):
            current_page = document.get_page(i)
            pdf_width, pdf_height = current_page.get_size()
            file_out_i = '%s_%s%s' % (file_out, i+1, '.png')
            pngsurface = cairo.ImageSurface(
                cairo.FORMAT_ARGB32,
                int(pdf_width * MMTOPNG),
                int(pdf_height * MMTOPNG))
            context = cairo.Context(pngsurface)
            context.save()
            context.scale(1.0*MMTOPNG, 1.0*MMTOPNG)
            current_page.render(context)
            context.restore()
            pngsurface.flush()
            pngsurface.write_to_png(file_out_i)
            pngsurface.finish()


def create_from_images(file_out, images, width=1189, height=1682, margin=0):
    temp_pdf = create_temp_file()
    temp_png = None
    pdfsurface = cairo.PDFSurface(temp_pdf, width, height)
    context = cairo.Context(pdfsurface)
    for image in images:
        basename, extension = os.path.splitext(image)
        if mimetypes.guess_type(image)[0] in MIMETYPES_PNG:
            imagesurface = cairo.ImageSurface.create_from_png(image)
        else:
            imagesurface = create_image_surface_from_file(image)
        imagesurface_width = imagesurface.get_width()
        imagesurface_height = imagesurface.get_height()
        scale_x = (imagesurface_width/MMTOPIXEL)/width
        scale_y = (imagesurface_height/MMTOPIXEL)/height
        if scale_x > scale_y:
            scale = scale_x
        else:
            scale = scale_y
        if margin == 1:
            scale = scale * 1.05
        elif margin == 2:
            scale = scale * 1.15
        x = (width - imagesurface_width/MMTOPIXEL/scale)/2
        y = (height - imagesurface_height/MMTOPIXEL/scale)/2
        context.save()
        context.translate(x, y)
        context.scale(1.0/MMTOPIXEL/scale, 1.0/MMTOPIXEL/scale)
        context.set_source_surface(imagesurface)
        context.paint()
        context.restore()
        context.show_page()
    pdfsurface.flush()
    pdfsurface.finish()
    shutil.copy(temp_pdf, file_out)
    os.remove(temp_pdf)


def reduce_pdf(file_in):
    file_out = get_output_filename(file_in, 'reduced')
    rutine = 'ghostscript -q  -dNOPAUSE -dBATCH -dSAFER \
    -sDEVICE=pdfwrite \
    -dCompatibilityLevel=1.4 \
    -dPDFSETTINGS=/screen \
    -dEmbedAllFonts=true \
    -dSubsetFonts=true \
    -dDownsampleColorImages=true \
    -dColorImageResolution=100 \
    -dColorImageDownsampleType=/Bicubic \
    -dColorImageResolution=72 \
    -dGrayImageDownsampleType=/Bicubic \
    -dGrayImageResolution=72 \
    -dMonoImageDownsampleType=/Bicubic \
    -dMonoImageResolution=72 \
    -sOutputFile=%s %s' % (file_out, file_in)
    args = shlex.split(rutine)
    p = subprocess.Popen(args, stdout=subprocess.PIPE)
    out, err = p.communicate()


def convert2png(file_in, file_out):
    im = Image.open(file_in)
    im.save(file_out)


def get_output_filename(file_in, modificator):
    if os.path.exists(file_in) and os.path.isfile(file_in):
        head, tail = os.path.split(file_in)
        root, ext = os.path.splitext(tail)
        file_out = os.path.join(head, root+'_'+modificator+ext)
        return file_out
    return None


def get_files(files_in):
    files = []
    for file_in in files_in:
        file_in = unquote_plus(file_in.get_uri()[7:])
        if os.path.isfile(file_in):
            files.append(file_in)
    if len(files) > 0:
        return files
    return None


def get_num(chain):
    try:
        chain = chain.strip()  # removing spaces
        return int(float(chain))
    except:
        return None


def get_ranges(chain):
    ranges = []
    if chain.find(',') > -1:
        for part in chain.split(','):
            if part.find('-') > -1:
                parts = part.split('-')
                if len(parts) > 1:
                    f = get_num(parts[0])
                    t = get_num(parts[1])
                    if f is not None and t is not None:
                        ranges.append([f, t])
            else:
                el = get_num(part)
                if el:
                    ranges.append([el])
    elif chain.find('-') > -1:
        parts = chain.split('-')
        if len(parts) > 1:
            f = get_num(parts[0])
            t = get_num(parts[1])
            if f is not None and t is not None:
                ranges.append([f, t])
    else:
        el = get_num(chain)
        if el:
            ranges.append([el])
    return ranges


def all_files_are_pdf(items):
    for item in items:
        fileName, fileExtension = os.path.splitext(
            unquote_plus(item.get_uri()[7:]))
        if fileExtension != '.pdf':
            return False
    return True


def all_files_are_images(items):
    for item in items:
        fileName, fileExtension = os.path.splitext(
            unquote_plus(item.get_uri()[7:]))
        if fileExtension.lower() in EXTENSIONS_FROM:
            return True
    return False
