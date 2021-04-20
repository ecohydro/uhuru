import numpy as np
from PIL import Image
import math
import sys

def optimize_rotation(image, max_angle=30, step=0.01):
    """ Determines the optimal rotation angle for an image to make it as square as possible.

    Parameters
    ==========

    max_angle = 30
    step = 0.01

    """
    n_zeros = 1e20
    delta_n = -1e20
    for angle in np.arange(0, 20, 0.01):
        im = crop(scale_and_rotate_image(image, 1, 1, angle, mode='I;16'))
        fit = np.sum(np.array(im) == 0)
        delta_n = fit - n_zeros
        #print("DEBUG",angle,delta_n,n_zeros,fit)
        if delta_n > 4000:
            im_final = crop(scale_and_rotate_image(image, 1, 1, optimal_angle, mode='I;16'))
            print("Found optimum angle, {angle}.".format(angle=optimal_angle))
            return im_final
        if fit < n_zeros:
            n_zeros = fit
            optimal_angle = angle    
    raise ValueError("max_angle ({angle}) too low. No optimum angle found".format(angle=max_angle))

def crop(image=None):
    data = np.asarray(image)

    non_empty_columns = np.where(data.max(axis=0)>0)[0]
    non_empty_rows = np.where(data.max(axis=1)>0)[0]

    cropBox = (min(non_empty_rows), max(non_empty_rows), min(non_empty_columns), max(non_empty_columns))

    data_crop = data[cropBox[0]:cropBox[1]+1, cropBox[2]:cropBox[3]+1]
    
    return Image.fromarray(data_crop)

def scale_and_rotate_image(im, sx, sy, deg_ccw, mode='RGBA', color=None):
    im_orig = im
    im = Image.new(mode, im_orig.size, color)
    im.paste(im_orig)

    w, h = im.size
    angle = math.radians(-deg_ccw)

    cos_theta = math.cos(angle)
    sin_theta = math.sin(angle)

    scaled_w, scaled_h = w * sx, h * sy

    new_w = int(math.ceil(math.fabs(cos_theta * scaled_w) + math.fabs(sin_theta * scaled_h)))
    new_h = int(math.ceil(math.fabs(sin_theta * scaled_w) + math.fabs(cos_theta * scaled_h)))

    cx = w / 2.
    cy = h / 2.
    tx = new_w / 2.
    ty = new_h / 2.

    a = cos_theta / sx
    b = sin_theta / sx
    c = cx - tx * a - ty * b
    d = -sin_theta / sy
    e = cos_theta / sy
    f = cy - tx * d - ty * e

    return im.transform(
        (new_w, new_h),
        Image.AFFINE,
        (a, b, c, d, e, f),
        resample=Image.NEAREST
    )

def rescale(image, zero_val=9999):
    data = np.array(image)
    if np.sum(data == 0) > 0:
        data[data == 0] = zero_val
    data = (data / np.max(data)) * 255
    return Image.fromarray(data)


if __name__ == "__main__":
    in_file = sys.argv[1]
    out_file = sys.argv[2]
    zero_val=sys.argv[3]
    im = crop(Image.open(in_file))
    optimized = optimize_rotation(im)
    optimized.save(out_file)
