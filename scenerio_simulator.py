'''
Version: 20230629

Pictures:
Front light: front+.png
Back light: back+.png
Background: base.png

Interface:
\tparas: [frontlight, backlight, CCT]
\trecreate_img: update the image with the latest parameters
'''

from PIL import Image, ImageTk
import tkinter as tk
import json


# IMPORT JSON FILE -- CCT_table_inRGB.json
with open('CCT_table_inRGB.json','r') as openedfile:
    CCT_table = json.load(openedfile)



# RESIZE PICTURES AND WINDOWS AS WELL
picture_size = (5168>>2, 2912>>2)

MAIN = Image.open('front+.png').resize(picture_size)
BACK = Image.eval(Image.open('back+.png').resize(picture_size), lambda i:i*5//4)
BASE = Image.open('base.png').resize(picture_size)

size_env_window = (MAIN.width+10, MAIN.height+10)


LIGHT_SENSING_POINT = [(2600>>2, 2560>>2)]
sensor_value = [0]


# PARAMETERS FOR API
paras = [100, 100, 4000]
# [FRONT, BACK, CCT]



# CALL WINDOWS
env_window = tk.Tk()

win_top = (env_window.winfo_screenheight() - size_env_window[1])//2
win_left = (env_window.winfo_screenwidth() - size_env_window[0])//2

env_window.geometry(f'{size_env_window[0]}x{size_env_window[1]}+{win_left}+{win_top}')
env_window.title('Aloha Hola Halo!')
env_window.resizable(0,0)


env_adjust = tk.Toplevel(env_window)
env_adjust.geometry('200x200-50-50')
env_adjust.title('Environment Adjustment')
env_adjust.resizable(0,0)



# CREATE A CANVAS IN ENV_WINDOW
mycanvas = tk.Canvas( env_window,
                    width=MAIN.width,
                    height=MAIN.height)
mycanvas.place(x=5,
               y=5)


def recreate_img():

    def color_adjust(img: Image):
        
        if paras[2] == '-': return img

        #SPLIT IMAGE INTO CHANNELS
        r, g, b = img.split()

        #IMPORT RGB VALUE AT TARGET CCT(tRGB) AND AT REFERENCE CCT(refRGB, normally 4000K)
        tRGB = CCT_table[str(paras[2])]
        refRGB = CCT_table['4300']


        r = r.point(lambda i: i * tRGB[0] * 2 // refRGB[0] )
        g = g.point(lambda i: i * tRGB[1] * 2 // refRGB[1] )
        b = b.point(lambda i: i * tRGB[2] * 2 // refRGB[2] )
        return Image.merge('RGB', (r,g,b))



    #ADJUST THE FRONT LIGHT
    _main = Image.eval(MAIN, lambda i: i * paras[0] // 50)

    #ADJUST THE BACK LIGHT
    _back = Image.eval(BACK, lambda i: i * paras[1] // 50)

    #COMBINE FRONT AND BACK LIGHTS
    res = Image.blend(_main, _back, 0.5)

    #ADJUST CCT
    res = color_adjust(res)

    #CHANGE BACKGROUND LIGHT LVL
    _base = Image.eval(BASE, lambda i: i * env_scale.get() // 50)

    #MIX BASE AND LIGHTS
    res = Image.blend(res,_base,0.5)

    #LIGHT SENSING
    r,g,b = res.getpixel(LIGHT_SENSING_POINT[0])
    sensor_value[0] = (r*299 + g*587 + b*114) // 1000
    str_sensor_value.set(create_sensor_value(sensor_value[0]))

    #COMBINE THE LIGHT FROM LAMP WITH BACKGROUND
    output = ImageTk.PhotoImage(res)

    #SHOW THE IMAGE ON THE CANVAS
    mycanvas.create_image(0,0,anchor='nw',image=output)
    mycanvas.output = output
    return


#CREATE A LABEL AND SCALE IN ENV_ADJUST

def change_lvl_env(e):
    lvl_env.set(f'{env_scale.get()} %')
    recreate_img()
    return


lvl_env = tk.StringVar(env_adjust, '100 %')
tk.Label(env_adjust,
         textvariable=lvl_env,
         font=('System', 30),
         relief='flat').pack()

env_scale = tk.Scale(env_adjust,
         from_=0,
         to=100,
         orient='horizontal',
         command=change_lvl_env)

env_scale.pack()

env_scale.set(100)



def create_sensor_value(val:int) -> str:
    return f'Sensor Now: {val}'

str_sensor_value = tk.StringVar(env_adjust, create_sensor_value(sensor_value[0]))

display_sensor = tk.Label(env_adjust,
                          font=('System', 5),
                          textvariable=str_sensor_value)

display_sensor.pack()


def close_all_windows():
    env_window.destroy()


destroy_button = tk.Button(env_adjust,
                           font=('System', 20),
                           text='Exit All',
                           command=close_all_windows)
destroy_button.pack()



recreate_img()