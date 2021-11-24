#!/usr/bin/env python3

import os
from PIL import Image
from json import load as json_load
from math import gcd

file_path = os.path.dirname(os.path.realpath(__file__))
gifs_path = os.path.join(file_path,'gifs')
with open(os.path.join(file_path, 'gif_params.json')) as gifs_json:
    gif_params = json_load(gifs_json)

def get_nof(PIL_Image_object):
    """ Returns the number of frames in a PIL Image object """
    try:
        PIL_Image_object.seek(0)
        nof = 0
        while True:
            try:
                nof += 1
                PIL_Image_object.seek(PIL_Image_object.tell() + 1)
            except EOFError:
                return nof
    except:
        print('Not a PIL Image object')
    return None

def lcm(numbers):
    """ Returns the least common multiple of numbers in a list """
    lcm = 1
    for num in numbers:
        lcm = lcm*num // gcd(lcm, num)
    return lcm

# GIF merger mode
desc = 'Enter the GIF merger mode (1, 2, 3 or 4):\n' + \
       '  1 -> Duration of the merged GIF will equal the maximum duration among the individual GIFs,' + \
       ' where the individual GIFs of lower duration are stopped until the end of the longest individual' + \
       ' GIF within the merged GIF is reached\n' + \
       '  2 -> Duration of the merged GIF will equal the maximum duration among the individual GIFs,' + \
       ' where individual GIFs of lower duration are looped until the end of the longest individual GIF' + \
       ' within the merged GIF is reached\n' + \
       '  3 -> Duration of the merged GIF will equal the least common multiple of individual GIFs\' durations,' + \
       ' so that the individual GIFs within the merged GIF have seamless loops (pick with caution, can result in' + \
       ' memory leak or very big merged GIF size)\n' # + \
       # '  (not implemented) 4 -> Duration of the merged GIF will equal the specified value in ms, where individual GIFs within' + \
       # ' the merged GIF are looped until the end of the merged GIF duration is reached\n'
while True:
    try:
        gm_mode = int(input(desc))
        if gm_mode not in [1,2,3]:
            print('Not a valid number')
        else:
            break
    except:
        print('Not a valid input')

# Merged GIF duration
# if gm_mode == 4:
    # desc = 'Enter the merged GIF duration in ms (10+):\n'
    # while True:
        # try:
            # dm = int(input(desc))
            # if dm < 10:
                # print('Not a valid number')
            # else:
                # break
        # except:
            # print('Not a valid input')

# Merged GIF number of loops
desc = 'Enter the number of times the merged GIF should loop (0 - infinite, 1+ - exact number of loops):\n'
while True:
    try:
        l_mode = input(desc)
        if not l_mode:
            l_mode = 0
        l_mode = int(l_mode)
        if l_mode < 0:
            print('Not a valid number')
        else:
            break
    except:
        print('Not a valid input')
print()

# Number of frames in input GIFs
print('Number of frames in input GIFs:')
nofspi = []
for i in range(len(gif_params['gifs'])):
    filename = os.path.join(gifs_path,gif_params['gifs'][i]['filename'])
    with Image.open(filename) as img:
        nofspi.append(get_nof(img))
    print(f'{os.path.split(filename)[-1]} -> {nofspi[i]} {"frames" if nofspi[i]>1 else "frame"}')
print()

# Duration of each frame (ms) in input GIFs and the total duration of each GIF
print('Duration of frames in input GIFs and their total durations in ms:')
fdi=[] # Frame durations in input GIFs
tdi=[] # Total duration of input GIFs
for i in range(len(gif_params['gifs'])):
    fdi.append([])
    filename = os.path.join(gifs_path,gif_params['gifs'][i]['filename'])
    with Image.open(filename) as img:
        for j in range(nofspi[i]):
            img.seek(j)
            fdi[i].append(img.info['duration'])
    tdi.append(sum(fdi[i]))
    print(f'{os.path.split(filename)[-1]} -> {fdi[i]} = {tdi[i]} ms total')
print()

# Total duration of the merged GIF, its frame duration and number of frames
fdm = gcd(*[x for y in fdi for x in y])
if gm_mode in [1,2]:
    tdm = max(tdi)
elif gm_mode == 3:
    tdm = lcm(tdi)
nofsm = tdm//fdm
print(f'Merged GIF frame duration: {fdm} ms')
print(f'Merged GIF total duration: {tdm} ms')
print(f'Merged GIF number of frames: {nofsm} {"frames" if nofsm>1 else "frame"}')
print()

# Number of times each frame in the input GIFs repeats in regard to the merged GIF frame duration
frsi=[] # frame repeats input
for i in range(len(gif_params['gifs'])):
    frsi.append([fd//fdm for fd in fdi[i]])

# Opening GIFs and calculating merged GIF canvas size
gifs = []
canvas_size = [0,0]
for i in range(len(gif_params['gifs'])):
    gifs.append([])
    filename = os.path.join(gifs_path,gif_params['gifs'][i]['filename'])
    h_offset = gif_params['gifs'][i]['h_offset']
    v_offset = gif_params['gifs'][i]['v_offset']
    rotation_angle = gif_params['gifs'][i]['rotation_angle']
    with Image.open(fp=filename) as img:
        # Calculating canvas size
        rotated_img = img.rotate(rotation_angle,expand=True)
        if (h_offset+rotated_img.size[0]) > canvas_size[0]:
            canvas_size[0] = (h_offset+rotated_img.size[0])
        if (v_offset+rotated_img.size[1]) > canvas_size[1]:
            canvas_size[1] = (v_offset+rotated_img.size[1])
        # Populating gifs list
        for j in range(nofspi[i]):
            img.seek(j)
            rgba_img = img.convert(mode='RGBA')
            rotated_img = rgba_img.rotate(angle=rotation_angle, resample=Image.BICUBIC, expand=True, fillcolor=(255,255,255,0))
            gifs[i].append(rotated_img)
canvas_size = (canvas_size[0], canvas_size[1])

# Merging GIFs
print('Merging GIFs ...')
gifm = []
try:
    for i in range(nofsm):
        gifm.append(Image.new(mode='RGBA', size=canvas_size, color=(255,255,255,0)))
except:
    print('Memory leak')
else:
    cnt = [0]*len(gif_params['gifs'])
    for i in range(len(gif_params['gifs'])):
        h_offset = gif_params['gifs'][i]['h_offset']
        v_offset = gif_params['gifs'][i]['v_offset']
        if gm_mode == 1:
            for j in range(len(frsi[i])):
                for k in range(frsi[i][j]):
                    gifm[sum(frsi[i][:j])+k].paste(im=gifs[i][j], box=(h_offset,v_offset))
        elif gm_mode in [2,3]:
            cnt = 0
            while cnt < nofsm:
                for j in range(len(frsi[i])):
                    for k in range(frsi[i][j]):
                        gifm[cnt].paste(im=gifs[i][j], box=(h_offset,v_offset))
                        cnt+=1
                        if cnt >= nofsm:
                            break
                    if cnt >= nofsm:
                            break
        # elif gm_mode == 4:
    # Saving the merged GIF
    print('Saving to merged.gif ...')
    gifm[0].save(fp=os.path.join(gifs_path,'merged.gif'), save_all=True, append_images=gifm[1:], interlace=False, duration=10, transparency=0, loop=l_mode)