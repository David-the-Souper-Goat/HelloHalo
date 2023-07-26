'''
Version: 20230703

Pictures:
seg_bar_on.png
seg_bar_off.png
seg_rod_on.png
seg_rod_off.png

bars are horizontal lines / rods are vertical lines

Interface:
show(digit: str) - digit can be special icon only if the icon had been well-defined before.
                   if the special icon doesn't exist, the display wouldn't change.
'''

from PIL import Image, ImageTk
import tkinter as tk


# IMPORT IMAGES OF BAR IN SPECIFIC POSITION
bar = [[] for _ in range(7)]
for i in range(7):
    bar[i].append(Image.open(f'con_pic\\{i}_off.png'))
    bar[i].append(Image.open(f'con_pic\\{i}_on.png'))

ratio = (3, 5)  # ratio = (width, height)


num = {
    '-1':0,
    '-':int('1000000',2),
    'F':int('1100011',2),
    '0':int('111111',2),
    '1':int('1100',2),
    '2':int('1110110',2),
    '3':int('1011110',2),
    '4':int('1001101',2),
    '5':int('1011011',2),
    '6':int('1111011',2),
    '7':int('1110',2),
    '8':int('1111111',2),
    '9':int('1011111',2)
}



class SevenSeg:
    '''
    CLASS FOR 7 SEGMENT DISPLAY IN CR23.
    Qisda Corp. all reserved.'''

    def __init__(self,
                 root: tk.Tk,
                 center: tuple[int, int],
                 bg_color: str = '#000000',
                 height: int = 25):
        '''
        root: ROOT OBJECT for 7-segment display.\n
        ^ \n
        ^      . 1\n
        ^      0   2\n
        height   6\n
        ^      5   3\n
        ^        4\n
        '''
        self.height = height
        self.width = height * ratio[0] // ratio[1]

        self.canvas = tk.Canvas(root,
                                height=self.height,
                                width=self.width,
                                bg=bg_color,
                                highlightthickness=0)
        self.canvas.place(x=center[0],
                          y=center[1],
                          anchor='center')

        self.determine_bar_size()
        self.show('-1')

    def determine_bar_size(self):
        height = self.height
        # A CONSTANT TO ADJUST THE RESIZE RATIO: THE BIGGER C IS, THE SMALLER THE RESULT WILL BE
        c = 730
        l, h, w = 286, 284, 137
        bar_size = [
            (w*height//c,   h*height//c),
            (l*height//c,   w*height//c),
            (w*height//c,   h*height//c),
            (w*height//c,   h*height//c),
            (l*height//c,   w*height//c),
            (w*height//c,   h*height//c),
            (l*height//c,   w*height//c)
        ]
        self.customize_bar(bar_size)

        return


    def customize_bar(self, bs: list):
        #bs as bar_size
        self.bar = [[] for _ in range(7)]
        for i in range(7):
            self.bar[i].extend([ImageTk.PhotoImage(bar[i][0].resize(bs[i])),
                                ImageTk.PhotoImage(bar[i][1].resize(bs[i]))])

        h, w = self.height, self.width
        #x0, y0 = 
        self.bar_pos = [
            (0,     h*29//100,'w'),
            (w>>1,  0,  'n'),
            (w,     h*29//100,'e'),
            (w,     h*71//100,'e'),
            (w>>1,  h,'s'),
            (0,     h*71//100,'w'),
            (w>>1,  h>>1,   'center')
        ]

        return
    

    def show(self, digit: str) -> None:
        if digit not in num: return
        mycanvas: tk.Canvas = self.canvas
        mycanvas.delete('all')
        code = num[digit]
        for i in range(7):
            bar_pos_now = self.bar_pos[i]
            bar_now = self.bar[i]
            decode = (code>>i)&1
            mycanvas.create_image(bar_pos_now[0],
                                  bar_pos_now[1],
                                  anchor=bar_pos_now[2],
                                  image=bar_now[decode])
            #mycanvas.bar_now[decode] = bar_now[decode]
        
        return



# DEBUGGING

if __name__ == '__main__':
    
    root = tk.Tk()
    h = [SevenSeg(root,
                 (37+45*i,37),
                 '#000000',
                 70) for i in range(3)]
    for i in range(3):
        h[i].show('-1')

    def show_scale(e):
        n = myscale.get()
        if n == -1:
            for i in range(3):
                h[i].show('-1')
            return
        for i in range(3):
            if n == 0:
                h[-1-i].show('-1')
                continue
            rem = n % 10
            h[-1-i].show(str(rem))
            n //= 10
        return

    myscale = tk.Scale(root,
                       from_=-1,
                       to=999,
                       orient='horizontal',
                       command=show_scale)
    myscale.set(-1)
    myscale.place(x=100,
                  y=100)
    
    root.mainloop()