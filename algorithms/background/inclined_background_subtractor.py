#
# dials.algorithms.background.curved_subtractor.py
#
#  Copyright (C) 2013 Diamond Light Source
#
#  Author: Luis Fuentes-Montero (luiso) & James Parkhurst
#
#  This code is distributed under the BSD license, a copy of which is
#  included in the root directory of this package.

from __future__ import division

class InclinedSubtractor(object):
  ''' The Flat background subtractor '''

  def __init__(self, **kwargs):
    pass

  def __call__(self, reflections):

    layering_and_background_plane(reflections)

    return reflections

def layering_and_background_plane(reflections):
  from dials.algorithms.background \
   import get_plane_background_syml_sys_2d, variance_n_background_from_plane
  from scitbx.array_family import flex

  from dials.util.command_line import ProgressBar
  bar_siz = len(reflections['shoebox'])
  p_bar = ProgressBar(title = 'Performing Inclined background plane calculation')
  tbl_prgr = 0

  plane_constants = []
  shoeboxes = reflections['shoebox']
  for shoebox in shoeboxes:

    #if ref.is_valid():
      p_bar.update(tbl_prgr * 100.0 / bar_siz)
      tbl_prgr += 1

      data = shoebox.data
      mask = shoebox.mask
      background = shoebox.background
      tot_sigma = 0.0
      for i in range(data.all()[0]):
        data2d = data[i:i + 1, :, :]
        mask2d = mask[i:i + 1, :, :]
        background2d = background[i:i + 1, :, :]

        data2d.reshape(flex.grid(data.all()[1:]))
        mask2d.reshape(flex.grid(data.all()[1:]))
        background2d.reshape(flex.grid(background2d.all()[1:]))

        a_mat_flx = flex.double(flex.grid(3, 3))
        b_vec_flx = flex.double(flex.grid(3, 1))
        ok_logic = get_plane_background_syml_sys_2d \
                    (data2d, mask2d, a_mat_flx, b_vec_flx)

        if ok_logic == 0:
          a_mat = a_mat_flx.as_scitbx_matrix()
          b_mat = b_vec_flx.as_scitbx_matrix()

          try:
            x_mat = a_mat.inverse() * b_mat
            abc_plane = x_mat.as_flex_double_matrix()
          except:
            abc_plane = flex.double(flex.grid(3, 1))
            abc_plane[0, 0] = 0
            abc_plane[1, 0] = 0
            abc_plane[2, 0] = 0
        else:
          abc_plane = flex.double(flex.grid(3, 1))
          abc_plane[0, 0] = 0
          abc_plane[1, 0] = 0
          abc_plane[2, 0] = 0

        variance = variance_n_background_from_plane \
                    (data2d, mask2d, abc_plane, background2d)
        plane_constants.append(abc_plane)
        #tot_sigma += variance
        background2d.reshape(flex.grid(1, background2d.all()[0], \
                                          background2d.all()[1]))
        background[i:i + 1, :, :] = background2d.as_double()
      #ref.intensity_variance = tot_sigma

  p_bar.finished('Done %d inclined background planes' % bar_siz)

  return reflections
