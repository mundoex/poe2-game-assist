MANA_POS_X_OFFSET_1920 = 123

MANA_POS_Y_100_1080 = 888
MANA_POS_Y_90_1080  = 905
MANA_POS_Y_80_1080  = 922
MANA_POS_Y_70_1080  = 939
MANA_POS_Y_60_1080  = 956
MANA_POS_Y_50_1080  = 972
MANA_POS_Y_40_1080  = 989
MANA_POS_Y_30_1080  = 1006
MANA_POS_Y_20_1080  = 1023
MANA_POS_Y_10_1080  = 1040
MANA_POS_Y_0_1080   = 1057

MANA_POS_Y_1080 = {
    100: MANA_POS_Y_100_1080,
    90:  MANA_POS_Y_90_1080,
    80:  MANA_POS_Y_80_1080,
    70:  MANA_POS_Y_70_1080,
    60:  MANA_POS_Y_60_1080,
    50:  MANA_POS_Y_50_1080,
    40:  MANA_POS_Y_40_1080,
    30:  MANA_POS_Y_30_1080,
    20:  MANA_POS_Y_20_1080,
    10:  MANA_POS_Y_10_1080,
    0:   MANA_POS_Y_0_1080,
}

MANA_POS_Y_1440 = {
    100: MANA_POS_Y_100_1080,
    90:  MANA_POS_Y_90_1080,
    80:  MANA_POS_Y_80_1080,
    70:  MANA_POS_Y_70_1080,
    60:  MANA_POS_Y_60_1080,
    50:  MANA_POS_Y_50_1080,
    40:  MANA_POS_Y_40_1080,
    30:  MANA_POS_Y_30_1080,
    20:  MANA_POS_Y_20_1080,
    10:  MANA_POS_Y_10_1080,
    0:   MANA_POS_Y_0_1080,
}

MANA_POS_Y_OFFSET = 10

def mana_x_offset(w, w_offset=0):
    return ( (w + w_offset) * MANA_POS_X_OFFSET_1920) / 1920

def mana_x_center(w, w_offset=0):
    return w-mana_x_offset(w, w_offset)
    
def get_mana_pos_y_dic(h):
    if h == 1080:
        return MANA_POS_Y_1080
    else:
        new_dic = {}
        for key, value in MANA_POS_Y_1080.items():
            new_value = (h * value) / 1080
            new_dic[key] = new_value
        return new_dic 

