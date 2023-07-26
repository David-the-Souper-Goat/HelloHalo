'''
Version: 20230719

Interface:
\tAPI = {'touchkeys', 'lcd_7seg'}

Python Ver.:
3.11.1 64-bit

Library Ver.:
Pillow - 9.4.0
controller_backend - 20230704
'''

import tkinter as tk
from PIL import Image, ImageTk
from math import sin, cos, pi
from display_7seg import SevenSeg
import controller_backend as BE
from functools import partial
import scenerio_simulator as ss
from time import process_time



#API DEFINITION

"""
TOUCHKEYS ARE THE KEYS SURROUND THE DISPLAY
NAME THE UPPER-LEFT MOST KEY AS 0
COUNT CCW AS [0,1,2,...,6] (TOTALLY 7 KEYS)
EACH KEY CAN BE REPRESENTED BY 1 OR 0
COMBINE EVERY 1/0 FROM RIGHT TO LEFT

"""



# ALIGN ALL TOUCHKEYS ONTO A CIRCLE
HEIGHT_PANEL = 300
DIMENTION_WINDOW = (HEIGHT_PANEL+50,
                    HEIGHT_PANEL+150)
CENTER_WINDOW = (DIMENTION_WINDOW[0]>>1,
                 DIMENTION_WINDOW[1]>>1)
RADIUS_TOUCHKEYS = 95


root = tk.Toplevel(ss.env_window)
root.geometry(f'{DIMENTION_WINDOW[0]}x{DIMENTION_WINDOW[1]}+50+50')
root.title('HALO CONTROLLER')
root.resizable(0,0)


# CREATE THE BASE CIRCLE
canvas = tk.Canvas(root,
                   height=HEIGHT_PANEL+4,
                   width=HEIGHT_PANEL+4,
                   bd=0)


canvas.place(x=CENTER_WINDOW[0],
             y=CENTER_WINDOW[1]-50,
             anchor='center')

CENTER_PANEL = ((HEIGHT_PANEL>>1)+2, (HEIGHT_PANEL>>1)+2)







#-------------------
# IMPORT BACKGROUND IMAGE
#-------------------

bg_circle_raw = Image.open('con_pic\\bg_circle.png').resize((HEIGHT_PANEL,HEIGHT_PANEL))

# EXTRACT THE EXACT BG COLOR
bg_circle_raw = bg_circle_raw.convert('RGBA')
rgba = bg_circle_raw.getpixel((150,150))
bg_color = '#' + hex(rgba[0])[2:] + hex(rgba[1])[2:] + hex(rgba[2])[2:]

bg_circle = ImageTk.PhotoImage(bg_circle_raw)
canvas.create_image(2,
                    2,
                    anchor='nw',
                    image=bg_circle)
canvas.bg_circle = bg_circle



















# ------------------
# TOUCHKEY PLACEMENT
# TOUCHKEY = [[KEY, ANGLE_ON_CIRCLE],...]
# ------------------

TOUCHKEY_ANGLE = [
    ['auto_switch', pi*5/4],
    ['CCT', pi*3/2],
    ['my_fav', pi*7/4],
    ['onoff', 0],
    ['forback', pi/4],
    ['level', pi/2],
    ['auto_dimming', pi*3/4]
]






# ---------------------
# IMPORT ICONS AROUND THE PANEL
# ---------------------

PERCENTAGE_RESIZE = 28      # RESIZE EVERY ICON WITH SPECIFIC PERCENTAGE

x_origin, y_origin = (HEIGHT_PANEL>>1), (HEIGHT_PANEL>>1)
img_touchkey = []
touchkeys: list[tk.Button] = []

#---------------------
# IMPORT BENQ LOGO
# PUT IT INTO A LABEL
#---------------------
BenQ_img = Image.open('con_pic\\BenQ.png')
h, w = BenQ_img.height, BenQ_img.width
BenQ_img = ImageTk.PhotoImage(BenQ_img.resize((w*PERCENTAGE_RESIZE//100,
                            h*PERCENTAGE_RESIZE//100)))
BenQ_LOGO = tk.Label(canvas,
         padx=0,
         pady=0,
         bd=0,
         relief='flat',
         bg=bg_color,
         image=BenQ_img)
BenQ_LOGO.BenQ_img=BenQ_img
BenQ_LOGO.place(x=x_origin+4,
               y=y_origin-RADIUS_TOUCHKEYS,
               anchor='center')





#------------------------
# FUNCTIONS OF TOUCHKEYS
#------------------------
def func_touchkey(key:str):

    # Activate 'CCT' button after checking if 'CCT' is already on
    if key == 'CCT' and not BE.LVLorCCT[0]:
        BE.func_lvl_cct_toggle()
    

    # Activate 'level' button after checking if 'level' is already on
    if key == 'level' and BE.LVLorCCT[0]:
        BE.func_lvl_cct_toggle()
    

    # Activate 'forback'
    if key == 'forback':
        BE.func_for_back()


    # Activate 'onoff'
    if key == 'onoff':
        BE.func_on_off()

        if BE.ONOFF[0]:
            for tk_now in touchkeys:
                tk_now.configure(state=tk.NORMAL)
        else:

            # Turn off all icons and then disable them
            i_onoff = BE.index['onoff']
            for i in range(len(touchkeys)):
                if i == i_onoff: continue
                touchkeys[i].configure(state=tk.DISABLED)



    if key == 'auto_switch':
        BE.func_auto_switch()


    if key == 'auto_dimming':
        light_sensor()
        BE.func_auto_dimming()


    if key == 'my_fav':
        BE.func_my_fav()

    BE.API['panel_stat']['last_touch'] = process_time()
    BE.API['panel_stat']['wake'] = 1

    update_panel()

    return





#----------------------
# IMPORT TOUCHKEY ICONS
#----------------------
for key, angle in TOUCHKEY_ANGLE:
    img_touchkey.append([])
    for suffix in  ('off','on'):
        img_now = Image.open(f'con_pic\\{key}_{suffix}.png')
        h, w = img_now.height, img_now.width
        img_now = img_now.resize((w*PERCENTAGE_RESIZE//100,
                                  h*PERCENTAGE_RESIZE//100))
        img_touchkey[-1].append(ImageTk.PhotoImage(img_now))


    # PLACE BUTTONS
    tk_now = tk.Button(canvas,
                       padx=0,
                       pady=0,
                       bg=bg_color,
                       relief='flat',
                       image=img_touchkey[-1][0],
                       command=partial(func_touchkey,key))
    tk_now.place(x=x_origin+RADIUS_TOUCHKEYS*sin(angle),
                 y=y_origin+RADIUS_TOUCHKEYS*cos(angle),
                 anchor='center')
    touchkeys.append(tk_now)





















# --------------------
# DISPLAY PLACEMENT
# --------------------
HEIGHT_7SEG = 27
PITCH_7SEG = 20
LINE_SPACING_7SEG = 6
HEIGHT_UNIT = 13
OFFSET_UNIT = 20


display_img = {
    '%':[],
    'K':[]
}


for key in display_img:
    for stat in ('off', 'on'):
        pic_now = Image.open(f'con_pic\\{key}_{stat}.png')
        w, h = pic_now.width, pic_now.height
        pic_now = pic_now.resize((w*HEIGHT_UNIT//h,
                                  HEIGHT_UNIT))
        display_img[key].append(ImageTk.PhotoImage(pic_now))



display_pos = {
    'digit_back':[ (CENTER_PANEL[0]-PITCH_7SEG,  CENTER_PANEL[1]-HEIGHT_7SEG - LINE_SPACING_7SEG),
                   (CENTER_PANEL[0],      CENTER_PANEL[1]-HEIGHT_7SEG - LINE_SPACING_7SEG),
                   (CENTER_PANEL[0]+PITCH_7SEG,      CENTER_PANEL[1]-HEIGHT_7SEG - LINE_SPACING_7SEG)],
    'digit_CCT': [ (CENTER_PANEL[0]-((PITCH_7SEG*3)>>1),  CENTER_PANEL[1]),
                   (CENTER_PANEL[0]-((PITCH_7SEG)>>1),    CENTER_PANEL[1]),
                   (CENTER_PANEL[0]+((PITCH_7SEG)>>1),    CENTER_PANEL[1]),
                   (CENTER_PANEL[0]+((PITCH_7SEG*3)>>1),  CENTER_PANEL[1])],
    'digit_front':[(CENTER_PANEL[0]-PITCH_7SEG,  CENTER_PANEL[1]+HEIGHT_7SEG + LINE_SPACING_7SEG),
                   (CENTER_PANEL[0],      CENTER_PANEL[1]+HEIGHT_7SEG + LINE_SPACING_7SEG),
                   (CENTER_PANEL[0]+PITCH_7SEG,      CENTER_PANEL[1]+HEIGHT_7SEG + LINE_SPACING_7SEG)]
}

unit_pos = {
    'back': [display_pos['digit_back'][-1][0]+OFFSET_UNIT,   display_pos['digit_back'][0][1],   '%'],
    'CCT':  [display_pos['digit_CCT'][-1][0]+OFFSET_UNIT,   display_pos['digit_CCT'][0][1],     'K'],
    'front':[display_pos['digit_front'][-1][0]+OFFSET_UNIT,   display_pos['digit_front'][0][1], '%']
}


display_7seg = {
    'digit_back':[SevenSeg(canvas,
                           display_pos['digit_back'][_],
                           bg_color,
                           HEIGHT_7SEG) for _ in range(3)],
    'digit_CCT': [SevenSeg(canvas,
                           display_pos['digit_CCT'][_],
                           bg_color,
                           HEIGHT_7SEG) for _ in range(4)],
    'digit_front':[SevenSeg(canvas,
                           display_pos['digit_front'][_],
                           bg_color,
                           HEIGHT_7SEG) for _ in range(3)]
}


unit: dict[tk.Label] = dict()
for key in unit_pos:
    unit[key] = tk.Label(canvas,
                         padx=0,
                         pady=0,
                         relief='flat',
                         bd=0,
                         bg=bg_color,
                         image=display_img[unit_pos[key][2]][0])
    unit[key].place(x=unit_pos[key][0],
                    y=unit_pos[key][1],
                    anchor='center')





















# FUNCTIONS


def update_panel():

    def set_image(item: tk.Button | tk.Label, img: ImageTk.PhotoImage):
        item.configure(image=img)
        return
    

    def number_to_7seg(array: list[SevenSeg], num: str) ->  None:
        if num == '-1':
            for i in range(len(array)):
                array[i].show('-1')
            return

        if num == '-':
            for i in range(len(array)):
                array[i].show('-')
            return
        
        if num == '0':
            for i in range(len(array)-1):
                array[i].show('-1')
            array[-1].show('0')
            return
        
        if num == '--':
            for i, x in enumerate(['-1','-','-1']):
                array[i].show(x)
            return

        for i in range(len(array)):
            if i >= len(num): rem = '-1'
            else: rem = num[-i-1]
            array[-i-1].show(rem)
        
        return

    def make(lcd:str, op:str) -> None:
        SevenSeg_array = display_7seg[f'digit_{lcd}']

        def turn_unit(c:str) -> None:
            unit_now = unit[lcd]
            i = 1 if c == 'on' else 0
            _icon = display_img[unit_pos[lcd][2]][i]
            set_image(unit_now, _icon)

            return


        if op == 'close':
            number_to_7seg(SevenSeg_array, '-1')
            turn_unit('off')
            return
        
        
        if op == 'show':
            cmd = BE.API['lcd_7seg'][lcd]
            number_to_7seg(SevenSeg_array, str(cmd))
            turn_unit('on')
            return

        if op == 'bar':
            number_to_7seg(SevenSeg_array, '-')
            turn_unit('off')
            return
        
        if op == 'midbar':
            number_to_7seg(SevenSeg_array, '--')
            turn_unit('off')
            return

    # UPDATE ALL KEYS' IMAGE
    for i in range(len(touchkeys)):
        onoff = BE.API['touchkeys'][i] if BE.ONOFF[0] and BE.API['panel_stat']['wake'] else 0
        img_cmd = img_touchkey[i][onoff]
        set_image(touchkeys[i], img_cmd)

    _cmd = {'front':'close', 'back':'close', 'CCT':'bar'}

    # UPDATE DIGIT ARRAYS
    if not BE.API['panel_stat']['wake']:
        _cmd['CCT'] = 'close'
    elif BE.ONOFF[0]:
        if BE.LVLorCCT[0]:
            _cmd['CCT'] = 'show'
            if (BE.FORBACK[0]>>1)&1:    _cmd['back'] = 'midbar'
            if BE.FORBACK[0]&1:         _cmd['front'] = 'midbar'
        else:
            if (BE.FORBACK[0]>>1)&1:    _cmd['back'] = 'show'
            if BE.FORBACK[0]&1:         _cmd['front'] = 'show'
            if BE.FORBACK[0] == 3:      _cmd['CCT'] = 'bar'

    for this_digit_array in _cmd:
        make(this_digit_array, _cmd[this_digit_array])

    
    return






update_panel()







#---------------------
#FUNCTION OF KNOB
#---------------------

KNOB_STAT = [None, None, None]

def func_knob(INCorDEC:str, event):
    if not BE.API['panel_stat']['wake']: return
    KNOB_STAT[0] = INCorDEC
    KNOB_STAT[1] = process_time()
    KNOB_STAT[2] = KNOB_STAT[1]
    BE.knob(INCorDEC)
    update_panel()

    return

def func_knob_release(event):

    KNOB_STAT[0] = None
    BE.API['panel_stat']['last_touch'] = process_time()

    return



font_size = 20

inc_btn = tk.Button(
    root,
    text='+',
    font=('System', font_size)
)

inc_btn.bind("<Button-1>", partial(func_knob, ('INC')))
inc_btn.bind("<ButtonRelease-1>", func_knob_release)

dec_btn = tk.Button(
    root,
    text='-',
    font=('System', font_size)
)


dec_btn.bind("<Button-1>", partial(func_knob, ('DEC')))
dec_btn.bind("<ButtonRelease-1>", func_knob_release)

inc_btn.place(
    x=CENTER_WINDOW[0] + 100,
    y=400,
    anchor='e'
)

dec_btn.place(
    x=CENTER_WINDOW[1] - 100,
    y=400,
    anchor='e'
)










time_span = [10]     #ms


def dimming(i:int, cmd:int | str) -> None:
    if cmd == -1 or cmd == '':
        cmd = 0

    last = ss.paras[i]
    if last == cmd: return
    
    # INVERSE OF APPROACHING SPEED
    r = 8

    ss.paras[i] = (last * r + cmd) // (r + 1) if abs(cmd-last)>3 else cmd

    return




def light_sensor() -> None:
    BE.sensor_value[0] = ss.sensor_value[0]
    return


BE.API['panel_stat']['last_touch'] = process_time()

def update():
    API = BE.API['lcd_7seg']


    # REFLECT CCT
    if API['CCT'] != -1 and API['CCT'] != '':
        ss.paras[2] = API['CCT']

    # REFLECT DIMMING
    onoff = {
        'front': BE.FORBACK[0]&1,
        'back': (BE.FORBACK[0]>>1)&1
    }
    for i, key in enumerate(['front', 'back']):
        if BE.ONOFF[0] and onoff[key]:
            dimming(i, API[key])
        else:
            dimming(i, 0)

    # AUTO DIMMING
    if BE.API['touchkeys'][BE.index['auto_dimming']]:
        light_sensor()
        BE.auto_dimming()
        update_panel()

    # KNOB FUNCTION
    if KNOB_STAT[0] and BE.API['panel_stat']['wake']:
        timer_now = process_time()
        total_press_time = timer_now - KNOB_STAT[1]
        from_last_tick = timer_now - KNOB_STAT[2]
        
        if total_press_time > 0.8:
            if from_last_tick > 0.02:
                BE.knob(KNOB_STAT[0])
                KNOB_STAT[2] = timer_now
                update_panel()
        elif from_last_tick > 0.1:
            BE.knob(KNOB_STAT[0])
            KNOB_STAT[2] = timer_now
            update_panel()

    # AUTO SLEEP
    if BE.API['panel_stat']['wake']:
        if (process_time() - BE.API['panel_stat']['last_touch']) > 5 and not KNOB_STAT[0]:
            BE.API['panel_stat']['wake'] = 0
            update_panel()


    ss.recreate_img()
    ss.env_window.after(time_span[0], update)

update()

ss.env_window.mainloop()