#!/usr/bin/env python
#! -*- coding:utf-8 -*-

import sys, re

labelinfo = {}
papersize = None
imageable = None

def read_labelinfos (filename):
   data = file (filename).read()

   ar = re.findall ('(?ims)^\\*ImageableArea ([^"]*): "([0-9. ]*)"', data)
   ar = [(key, tuple ([float (f) for f in val.split()])) for key, val in ar]
   ar = dict (ar)
   ps = re.findall ('(?ims)^\\*PaperDimension ([^"]*): "([0-9. ]*)"', data)
   ps = [(key, tuple ([float (f) for f in val.split()])) for key, val in ps]
   ps = dict (ps)
   if set (ar.keys()) != set (ps.keys()):
      raise Exception, "unsymmetric keys for ImageableArea and PaperDimension"

   for k in ar.keys():
      labelinfo[k] = (ps[k], ar[k])
    # print "\"%s\"" % k, labelinfo[k][0], labelinfo[k][1]


def set_labelinfo (key):
   global labelinfo, papersize, imageable

   keys = [ k for k in labelinfo.keys() if re.search (key, k) ]

   if len (keys) == 0:
      raise Exception, "unknown label format \"%s\"" % key
   if len (keys) > 1:
      raise Exception, "ambigous label format \"%s\" (matching: %s)" % (key, keys)

   key = keys[0]

   papersize = [float(i) for i in labelinfo[key][0]]
   imageable = [float(i) for i in labelinfo[key][1]]

   print papersize, imageable
   print "PWidth:  %.2f" % (papersize[0] / 72.0 * 25.4)
   print "PHeight: %.2f" % (papersize[1] / 72.0 * 25.4)
   print "x0:      %.2f" % (imageable[0] / 72.0 * 25.4)
   print "x1:      %.2f" % (imageable[1] / 72.0 * 25.4)
   print "Width:   %.2f (%d)" % ((imageable[2] - imageable[0]) / 72.0 * 25.4,
                                 (imageable[2] - imageable[0]) / 72.0 * 300)
   print "Height:  %.2f (%d)" % ((imageable[3] - imageable[1]) / 72.0 * 25.4,
                                 (imageable[3] - imageable[1]) / 72.0 * 300)


def import_ppm (filename):
   f = file (filename)

   format = f.read (2)

   if format != "P4":
      raise Exception, "Can only handle binary bitmap PBMs"

   c = f.read (1)
   while c.isspace ():
      c = f.read (1)

   have_data = False
   width = 0
   while c.isdigit ():
      width = width * 10 + int (c)
      c = f.read (1)
      have_data = True

   if not have_data:
      raise Exception, "missing width data in bitmap PBM"

   while c.isspace ():
      c = f.read (1)

   have_data = False
   height = 0
   while c.isdigit ():
      height = height * 10 + int (c)
      c = f.read (1)
      have_data = True

   if not have_data:
      raise Exception, "missing height data in bitmap PBM"

   if not c.isspace ():
      raise Exception, "missing whitespace after height data in PBM"

   imgdata = f.read()

   return (width, height, imgdata)


def do_print (filename):

   width, height, data = import_ppm (filename)

   if (width != int ((imageable[2] - imageable[0]) / 72.0 * 300) or
       height != int ((imageable[3] - imageable[1]) / 72.0 * 300)):
      raise Exception, "Invalid bitmap format for label size"

   bytes = (width + 7) // 8

   sys.stdout.write ("%c*" % (27, ))          # Restore defaults
   sys.stdout.write ("%cB%c" % (27, 0))       # dot tab 0
   sys.stdout.write ("%cD%c" % (27, bytes))   # Bytes per line
   sys.stdout.write ("%ch" % (27, ))          # Text mode

   # label length - should be longer than actual length (syncs to hole then)
   formlen = int (height)
   sys.stdout.write ("%cL%c%c" % (27, formlen // 256, formlen % 256))

   for i in range (height):
      if data:
         line = data[:bytes]
         data = data[bytes:]
      sys.stdout.write (chr (0x16) + line)

   sys.stdout.write ("%cE" % (27, ))  # Form feed


if __name__=='__main__':
   read_labelinfos ("static/ppd/lw450.ppd")
   set_labelinfo ("11355")

   do_print (sys.argv[1])

