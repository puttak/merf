from math import sqrt
from pathlib import Path

import matplotlib.pyplot as plt
import numpy
import numpy as np
from skimage import color, morphology
from skimage.draw import circle_perimeter
from skimage.feature import canny, blob_dog, blob_log, blob_doh
from skimage.filters import sobel, gaussian, threshold_otsu
from skimage.io import imread
from skimage.transform import hough_circle, hough_circle_peaks

# Load picture and detect edges
from sk_image.enhance_contrast import stretch_composite_histogram
from simulation.simulate import create_circular_mask


def circle(image):
    edges = canny(image, sigma=3, low_threshold=10, high_threshold=50)

    # Detect two radii
    hough_radii = np.arange(20, 35, 2)
    hough_res = hough_circle(edges, hough_radii)

    # Select the most prominent 3 circles
    accums, cx, cy, radii = hough_circle_peaks(
        hough_res, hough_radii, total_num_peaks=3
    )

    # Draw them
    fig, ax = plt.subplots(ncols=1, nrows=1, figsize=(10, 4))
    image = color.gray2rgb(image)
    for center_y, center_x, radius in zip(cy, cx, radii):
        circy, circx = circle_perimeter(center_y, center_x, radius, shape=image.shape)
        image[circy, circx] = (220, 20, 20)

    ax.imshow(image, cmap=plt.cm.gray)
    plt.show()


def segmentation(image):
    elevation_map = sobel(image)

    fig, ax = plt.subplots(figsize=(4, 3))
    ax.imshow(elevation_map, cmap=plt.cm.gray)
    ax.set_title("elevation map")
    ax.axis("off")
    plt.show()
    markers = np.zeros_like(image)
    markers[image < 30] = 1
    markers[image > 150] = 2

    fig, ax = plt.subplots(figsize=(4 * 4, 3 * 4))
    ax.imshow(markers, cmap=plt.cm.nipy_spectral)
    ax.set_title("markers")
    ax.axis("off")
    plt.show()
    segmentation = morphology.watershed(elevation_map, markers)

    fig, ax = plt.subplots(figsize=(4 * 4, 3 * 4))
    ax.imshow(segmentation, cmap=plt.cm.gray)
    ax.set_title("segmentation")
    ax.axis("off")
    plt.show()

    return segmentation


def dog(image):
    blobs = blob_dog(image, max_sigma=10, min_sigma=1, threshold=0.005, overlap=0.8)
    blobs[:, 2] = blobs[:, 2] * sqrt(2)
    return blobs


def log(image):
    blobs_log = blob_log(image, max_sigma=10, min_sigma=5, threshold=0.02, overlap=0.9)
    blobs_log[:, 2] = blobs_log[:, 2] * sqrt(2)
    return blobs_log


def doh(image):
    blobs_doh = blob_doh(image, max_sigma=30, threshold=0.01)
    return blobs_doh


def make_circles_fig(image, blobs, title=None, dpi=96):
    px, py = image.shape
    fig = plt.figure(figsize=(py / numpy.float(dpi), px / numpy.float(dpi)))
    if title is None:
        dims = [0.0, 0.0, 1.0, 1.0]
    else:
        dims = [0.0, 0.0, 1.0, 0.95]
    ax = fig.add_axes(dims, yticks=[], xticks=[], frame_on=False)
    ax.imshow(image, cmap="gray")
    ax.set_title(title, fontsize=50)
    for y, x, r in blobs:
        c = plt.Circle((x, y), r, color="red", linewidth=0.5, fill=False)
        ax.add_patch(c)
    return fig


def hough(img):
    pass


def area(img, blob):
    h, w = img.shape
    y, x, r = blob
    blob_mask = create_circular_mask(h, w, (x, y), r)
    img = img.copy()
    img[~blob_mask] = 0
    thresh = threshold_otsu(img)
    img[img >= thresh] = 1
    img[img <= thresh] = 0
    return np.sum(img)


def main():
    data_pth = Path("RawData/")
    image_fn = Path("R-233_5-8-6_000110.T000.D000.P000.H000.PLIF1.TIF")
    image_pth = data_pth / image_fn

    img_orig = imread(image_pth)
    filtered_img = gaussian(img_orig, sigma=1)
    s2 = stretch_composite_histogram(filtered_img)

    blobs = blob_dog(
        s2, max_sigma=10, min_sigma=1, threshold=0.001, overlap=0.8, sigma_ratio=1.05
    )
    blobs[:, 2] = blobs[:, 2] * sqrt(2)

    # make_circles_fig(s2, blobs).show()

    # plt.hist([r for (_,_,r) in blobs], bins=256)
    # plt.show()
    # areas = []
    # for blob in blobs:
    #     areas.append(area(s2, blob))
    #
    # plt.hist(areas, bins=256)
    # plt.show()


if __name__ == "__main__":
    main()