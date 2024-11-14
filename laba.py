from PIL import Image

# import numpy as np
# def norm_area(x,y,w,h):
#     xx = (2*x)/w-1
#     yy = (2*x)/h-1
#     return np.array([xx,yy])

# def norm_coordination(xmin,ymin,xmax,ymax,w,h):
#     t_left = norm_area(xmin,ymin,w,h)
#     t_right = norm_area(xmax,ymin,w,h)
#     b_left = norm_area(xmin,ymax,w,h)
#     b_right = norm_area(xmax,ymax,w,h)

#     return np.stack([t_left,t_right,b_left,b_right])

# w,h = 1920,1080
# xmin,ymin = 500, 300
# xmax,ymax = 700, 500

# norm_norm = norm_coordination(xmin,ymin,xmax,ymax,w,h)
# print(norm_norm)


image = Image.open("img.jpg")
conv_image = image.convert('L')
conv_image.show()