'''
Version: 20230719

Interface:
\tAPI = {'touchkeys', 'displays', 'lcd_7seg'}
'''


API = {
    'touchkeys':[0,0,0,0,0,1,0],
    'lcd_7seg':{'back':100, 'front': 85, 'CCT':4000},
    'panel_stat':{'wake':0, 'last_touch':None}
}

my_fav = {
    'back': 100,
    'front': 85,
    'CCT': 2700
}


touchkey = ['auto_switch',
            'CCT',
            'my_fav',
            'onoff',
            'forback',
            'level',
            'auto_dimming']


BOUND_CCT = [2700, 6500]
BOUND_LVL = [0, 100]


index = dict()
for i in range(len(touchkey)):
    index[touchkey[i]] = i


#建立前後光同時調整時的資訊
def build_follow_map() -> list:
    follow, lead = sorted([(API['lcd_7seg']['back'], 'back'), (API['lcd_7seg']['front'], 'front')])
    f_max = int(round(100 * follow[0] / lead[0]))
    return [lead[1], follow[1], f_max]
    


#前後光同時調整用的數值紀錄器
class FollowMap:

    def __init__(self,data:list[str,str,int]):
        self.lead = data[0]
        self.follow = data[1]
        self.f_max = data[2]

    def new_data(self, data:list[str,str,int]):
        self.lead = data[0]
        self.follow = data[1]
        self.f_max = data[2]
        return
    
    def export(self):
        return [self.lead, self.follow, self.f_max]

FM = FollowMap(build_follow_map())

#---------------------------
#每個按鍵的主要程式
#---------------------------



#亮度色溫切換
LVLorCCT = [0]            # 亮度與色溫狀態：0是亮度，1是色溫

def func_lvl_cct_toggle():

    #切換至亮度模式
    LVLorCCT[0] ^= 1

    #更新面板
    API['touchkeys'][index['level']] ^= 1
    API['touchkeys'][index['CCT']] ^= 1

    return


#前後光切換
FORBACK = [1]           # 1是前光，2是後光，3是前後光

def func_for_back():

    # 關閉我的最愛
    turn_off_my_fav()

    # 關閉自動模式
    if FORBACK[0] == 1: turn_off_auto_dimming()

    # 輪轉模式
    FORBACK[0] += 1
    if FORBACK[0] == 4: FORBACK[0] = 1

    # 如果變成前後光，則建立較小值的map
    if FORBACK[0] == 3:
        FM.new_data(build_follow_map())

    # 從記憶體中讀出亮度並顯示

    return


#入席偵測切換

def func_auto_switch():

    API['touchkeys'][index['auto_switch']] ^= 1

    return


#自動調光開啟
def func_auto_dimming():

    if FORBACK[0] == 2: return
    API['touchkeys'][index['auto_dimming']] = 1

    auto_dimming()


#我的最愛開啟

def func_my_fav():

    API['touchkeys'][index['my_fav']] = 1


ONOFF = [1]
#一般開關鍵
def func_on_off():

    ONOFF[0] ^= 1

    return




#旋鈕調整

def knob(direction: str):


    turn_off_my_fav()


    sign = 1 if direction == 'INC' else -1
    trigger = 1

    if LVLorCCT[0]:

        API['lcd_7seg']['CCT'] = bound_CCT(API['lcd_7seg']['CCT'] + sign * 100)

    else:
        
        if FORBACK[0] == 1:
            API['lcd_7seg']['front'] = bound_lvl(API['lcd_7seg']['front'] + sign)
        elif FORBACK[0] == 2:
            trigger = 0
            API['lcd_7seg']['back'] = bound_lvl(API['lcd_7seg']['back'] + sign)
        else:
            forback_level_together(sign)
    
    if trigger: turn_off_auto_dimming()

    return


#--------
# 副程式
#--------

#關閉我的最愛按鍵

def turn_off_my_fav():

    API['touchkeys'][index['my_fav']] = 0

    return


#關閉自動模式

def turn_off_auto_dimming():

    API['touchkeys'][index['auto_dimming']] = 0

    return


#限縮旋鈕輸入值，避免超過BOUND
def bound_CCT(num: int):
    if num > BOUND_CCT[1]: return BOUND_CCT[1]
    if num < BOUND_CCT[0]: return BOUND_CCT[0]
    return num

def bound_lvl(num: int):
    if num > BOUND_LVL[1]: return BOUND_LVL[1]
    if num < BOUND_LVL[0]: return BOUND_LVL[0]
    return num


#當前後光模式時的前後光調整邏輯
def forback_level_together(val: int):
    '''
    val:int - 旋鈕增減的量，是一個帶正負號的整數
    '''

    # 我先做了一個class叫做FollowMap @ line 48
    # 當切換到前後光模式時，會使用build_follow_map這個函數 @ line 40
    # build_follow_map先找出前後光中較高和較低的值，分別命名為lead和follow
    # 我假設 follow 會跟 lead **等比例變化**
    # 並且假定lead到100%時，follow就不能再繼續增加
    # 可以得到以此換算出當lead 100%時，follow的最大值
    # 儲存此最大值，並儲存lead和follow分別是前光還是後光


    #取出FollowMap中的lead, follow 和 follow的理論最大值
    lead, follow, f_max = FM.export()

    #讀取目前lead的數值
    val_lead = API['lcd_7seg'][lead]

    #將旋鈕增減量加到目前的lead的數值上
    val_lead += val

    #限制增加後的數值不能超過規定的範圍 BOUND_LVL @ line 32
    val = bound_lvl(val_lead)

    #利用follow的理論最大值，以及增加後的lead的值，內插出理論的follow值
    new_value_follow = f_max * val // 100


    #寫入API中
    API['lcd_7seg'][lead] = val
    API['lcd_7seg'][follow] = new_value_follow

    return


#自動調光運作
sensor_value = [0]
diff_integral = [0]
def auto_dimming():

    SENSOR_TARGET = 95

    #使用 PI control, P control係數為gain, I control係數為i_control
    gain = 0.04
    i_control = 2000

    API['lcd_7seg']['CCT'] = 4000

    now_sensor = sensor_value[0]

    if now_sensor == SENSOR_TARGET: return

    diff = SENSOR_TARGET - now_sensor
    control_value = (diff * gain) + (diff_integral[0] / i_control)

    diff_integral[0] += diff

    if round(control_value) == 0: return
    
    increment = int(round(control_value))

    res = API['lcd_7seg']['front'] + increment
    API['lcd_7seg']['front'] = bound_lvl(res)

    return