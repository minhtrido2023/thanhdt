from hyperopt import hp
from hyperopt.pyll.base import scope

from tuning.buy_pattern.hyo_tuning_manager import run_multiple_patterns

Init = "(time>='2014-01-01') & (time<='2025-01-01') "
# sell_patterns_v3 = {
#     "~MA21": "(MA20/MA50<1.04) & (MA20_T1/MA50_T1>0.96)  &  (D_RSI/D_RSI_T1W < 1.21) & (Close < 0.81*VAP1M)  & (D_MACDdiff< 7.0) & (Close/Close_T1W < 0.95)",
#     "~MA31": "(MA10/MA200<1) & (MA10_T1/MA200_T1>1) & (Close < 0.98*VAP3M)  & (Close/Close_T1W < 0.95)&   (D_RSI/D_RSI_T1W < 0.95) & (D_RSI < 0.5) & (D_MACDdiff< 0)",
#     "~MA41": "(Close > 1.5*MA200) & (NP_P0/NP_P1 < 0.88) & (Volume>0.9*Volume_3M_P50)  & (Close/Close_T1W < 0.94) & (Close < 1.01*VAP1M)",
#     "~S13": "(C_L1W>=1.29) & (D_CMB_Peak_T1>1.09*D_CMB) & (Close>1.12*MA10) & (D_CMB_XFast<7.0)",
#     "~SellLowGrowth": "(NP_P0/NP_P4 < 1.2) & (ID_Current -  ID_Release <= 10)",
#     "~SellBV": "(Close > 1.85*BVPS) & (NP_P0 /NP_P1 < 0.91) &(Close < 0.97*VAP1M) & (Close_T1W > 0.92*VAP1M) & (Volume > 0.95* Volume_3M_P50) & (ICB_Code != 8633)",
#     "~SellBV2": "(PB > 1.23*PB_MA5Y + 0.84*PB_SD5Y) & (NP_P0 /NP_P1 < 0.62)  & (Close < 0.99*VAP1M) & (Close_T1W > 0.8*VAP1M)  & (D_RSI > 0.28) & (Volume > 1.01*Volume_3M_P50)",
#     "~SellPE": "(PE >= 1.29*PE_MA5Y  + 0.91*PE_SD5Y) & (NP_P0 /NP_P1 < 0.95)  & (Close < 1.02*VAP3M) & (Close_T1W > 0.9*VAP3M)  & (Close/Close_T1W < 0.97)  & (Volume > 1.01*Volume_3M_P50)",
#     "~SellResistance": "(Open/Close< 0.95)  & (Close  <  0.89*Res_1Y)  & (Close/LO_3M_T1 > 1.22) & (Volume > 2.08*Volume_3M_P50)",
#     "~SellResistance1M": "(ID_XVAP3M_Down_P0 - ID_XVAP1M_Down_P2 <= 15.0) & (Close < 0.97*VAP1M) & (Close_T1 >  1.0*VAP1M) & (Volume > 1.01* Volume_3M_P50)& (D_RSI > 0.33)",
#     "~SellResistance1Y": "(PB > 1.23*PB_MA5Y + 0.93*PB_SD5Y) & (NP_P0 /NP_P1 < 0.8)  &  (Close < 0.94*Res_1Y)  & (Volume  > 1.25*Volume_3M_P50)  & (Close_T1W > 0.86*VAP1M)  & (D_RSI > 0.43)",
#     "~BearDvg2": "(D_RSI_Max1W/D_RSI > 0.82)  & (D_RSI_Max3M/D_RSI_Max1W > 1)  & (D_RSI_Max3M > 0.54)& (D_RSI_Max1W < 0.7)& (D_RSI_Max1W >0.59) & (D_RSI_Max1W_Close/D_RSI_Max3M_Close > 1.16) & (D_RSI_Max3M_MACD/D_RSI_Max1W_MACD > 1.28)  & (D_RSI_T1/D_RSI > 0.99) & (Volume > 1.13*Volume_1M)",
#     "~SellVolMax": "(Close/Volume_MaxTop5_2Y_Close < 0.8) & (ID_Current - Volume_MaxTop5_2Y_ID <=150.0) & (Close < 1.13*VAP1W) & (D_RSI > 0.49)  & (Close/Close_T1 < 1.08) & (D_RSI/D_RSI_T1W < 1.1) & (Close_T1/LO_3M_T1 > 1.35)"
# }
sell_patterns = {
    "~MA21": "(MA20/MA50<1.3) & (MA20_T1/MA50_T1>1.23) & (D_RSI/D_RSI_T1W < 0.9) & (Close < 1.25*VAP1M) & (D_MACDdiff< -1) & (Close/Close_T1W < 1.09)",
    "~MA31": "(MA10/MA200<1.05) & (MA10_T1/MA200_T1>1.05) & (Close < 1.12*VAP3M) & (Close/Close_T1W < 1.03)& (D_RSI/D_RSI_T1W < 0.9) & (D_RSI < 0.62) & (D_MACDdiff< -1.0)& (NP_P0/NP_P1 < 1.08) & (Volume>0.99*Volume_3M_P50)",
    "~MA41": "(Close > 1.55*MA200) & (NP_P0/NP_P1 < 0.92) & (Volume>1.17*Volume_3M_P50) & (Close/Close_T1W < 1.0) & (Close < 1.05*VAP1M)",
    "~S13": "(C_L1W>=1.15) & (D_CMB_Peak_T1>0.89*D_CMB) & (Close>1.15*MA10) & (D_CMB_XFast<3.0)",
    "~SellLowGrowth": "(NP_P0/NP_P4 < 1.2) & (ID_Current -  ID_Release <= 10)",
    "~SellBV": "(Close > 1.85*BVPS) & (NP_P0 /NP_P1 < 0.91) &(Close < 0.97*VAP1M) & (Close_T1W > 0.92*VAP1M) & (Volume > 0.95* Volume_3M_P50) & (ICB_Code != 8633)",
    "~SellBV2": "(PB > 1.23*PB_MA5Y + 0.84*PB_SD5Y) & (NP_P0 /NP_P1 < 0.62)  & (Close < 0.99*VAP1M) & (Close_T1W > 0.8*VAP1M)  & (D_RSI > 0.28) & (Volume > 1.01*Volume_3M_P50)",
    "~SellPE": "{Init} &(PE >= 1.25*PE_MA5Y  + 1.23*PE_SD5Y) & (NP_P0 /NP_P1 < 1.01) & (Close < 0.98*VAP3M) & (Close_T1W > 0.89*VAP3M) & (Close/Close_T1W < 1.29) & (Volume > 1.24*Volume_3M_P50)",
    "~SellResistance": "(Open/Close< 0.95) & (Close  <  0.8*Res_1Y) & (Close/LO_3M_T1 > 1.58) & (Volume > 2.47*Volume_3M_P50)",
    "~SellResistance1M": "(ID_XVAP3M_Down_P0 - ID_XVAP1M_Down_P2 <= 25.0) & (Close < 0.94*VAP1M) & (Close_T1 >  0.96*VAP1M) & (Volume > 1.04* Volume_3M_P50) & (D_RSI > 0.4)",
    "~SellResistance1Y": "(PB > 1.23*PB_MA5Y + 0.93*PB_SD5Y) & (NP_P0 /NP_P1 < 0.8)  &  (Close < 0.94*Res_1Y)  & (Volume  > 1.25*Volume_3M_P50)  & (Close_T1W > 0.86*VAP1M)  & (D_RSI > 0.43)",
    "~BearDvg2": " (D_RSI_Max1W/D_RSI > 0.88) & (D_RSI_T1/D_RSI > 1.11) & (D_RSI_Max3M > 0.66) & (D_RSI_Max1W < 0.76) & (D_RSI_Max1W >0.57) & (D_RSI_Max1W_Close/D_RSI_Max3M_Close > 1.12) & (D_RSI_Max3M_MACD/D_RSI_Max1W_MACD > 1.29) & (Volume > 1.11*Volume_1M)& (D_RSI_Max3M/D_RSI_Max1W > 1.21)",
    "~SellVolMax": "(Close/Volume_MaxTop5_2Y_Close < 0.84) & (ID_Current - Volume_MaxTop5_2Y_ID <=128.0) & (Close < 1.17*VAP1W) & (D_RSI < 0.55) & (Close/Close_T1 < 1.1) & (D_RSI/D_RSI_T1W < 1.03) & (Close_T1/LO_3M_T1 > 1.59)"
}

s_sell_patterns = {
    '~BearDvgVNI1~': "(VNINDEX_RSI_Max1W/VNINDEX_RSI > 1.044)  & (VNINDEX_RSI_Max3M > 0.74) & (VNINDEX_RSI_Max1W < 0.72) & (VNINDEX_RSI_Max1W>0.61) & (VNINDEX_RSI_Max1W_Close/VNINDEX_RSI_Max3M_Close > 1.028) & (VNINDEX_RSI_Max3M_MACD/VNINDEX_RSI_Max1W_MACD>1.11) & (VNINDEX_MACDdiff < 0)  & ( Close/VNINDEX_RSI_Max3M_Close > 0.96) & (VNINDEX_RSI_MinT3 > 0.43) & (VNINDEX_CMF < 0.13)",
    '~BearDvgVNI2~': "(VNINDEX_RSI_Max1W/VNINDEX_RSI > 1.016)  & (VNINDEX_RSI_Max3M > 0.77) & (VNINDEX_RSI_Max1W < 0.79) & (VNINDEX_RSI_Max1W>0.6) & (VNINDEX_RSI_Max1W_Close/VNINDEX_RSI_Max3M_Close > 1.008) & (VNINDEX_RSI_Max3M_MACD/VNINDEX_RSI_Max1W_MACD>1.1) & (VNINDEX_MACDdiff < 0)  & ( Close/VNINDEX_RSI_Max3M_Close > 0.97) & (VNINDEX_RSI_MinT3 > 0.5) & (VNINDEX_CMF < 0.15)"
}

sell_config = {
    'sell_filters': sell_patterns,
    'sell_mapping': {
        f'w_{k.lower()[1:]}': k[1:] for k in sell_patterns.keys()
    },

    'sell_search_space': {
        k: hp.quniform(k, 0, 1, 1) for k in [f"w_{k.lower()[1:]}" for k in sell_patterns.keys()]
    },

    'sell_init_vals': {
        'w_ma21': 1,
        'w_ma31': 0,
        'w_ma41': 1,
        'w_s13': 1,
        'w_selllowgrowth': 0,
        'w_sellresistance1y': 1,
        'w_sellresistance1m': 1,
        'w_sellresistance': 1,
        'w_sellbv': 1,
        'w_sellbv2': 1,
        'w_sellpe': 1,
        'w_sellvolmax': 1,
        'w_beardvg2': 1,
    }
}
# sell_config['sell_filters'].update(s_sell_patterns)
technical_extend_config = {
    'pattern_name': 'Technical_Extend',
    'utilize_percent': 1,
    'cutloss': 0.15,
    'search_space': {
        "w_te0": hp.quniform('w_te0', 0.5, 1.5, 0.02),
        "w_te1": hp.quniform('w_te1', 0.3, 1.5, 0.02),
        "w_te2": hp.quniform('w_te2', 0.5, 1.5, 0.02),
        "w_te3": hp.quniform('w_te3', 0.5, 2.0, 0.02),
        "w_te4": hp.quniform('w_te4', 0.5, 1, 0.02),
        "w_te4_1": hp.quniform('w_te4_1', 1, 1.7, 0.02),
        "w_te5": hp.quniform('w_te5', 0.5, 1.5, 0.02),
        "w_te6": hp.quniform('w_te6', 0.0, 1.5, 0.02),
        "w_te7": hp.quniform('w_te7', 0, 0.1, 0.002),
    },
    'init_vals': {
        "w_te0": 0.5,
        "w_te1": 0.3,
        "w_te2": 0.5,
        "w_te3": 0.5,
        "w_te4": 0.5,
        "w_te4_1": 1.4,
        "w_te5": 0.5,
        "w_te6": 0.3,
        "w_te7": 0.002,
    },
    'filter_template': "(D_RSI/D_RSI_T1W > {w_te0}) "
                       "& (Close/VAP1W > {w_te1}) "
                       "& (D_MFI/D_MFI_T1W > {w_te2}) "
                       "& (D_MACD/D_MACD_T1W > {w_te3}) "
                       "& (Close/LO_3M_T1 > {w_te4}) "
                       "& (Close/LO_3M_T1 < {w_te4_1}) "
                       "& (Volume/Volume_1M > {w_te5}) "
                       "& (D_RSI_Max1W/D_RSI_Max3M > {w_te6}) "
                       "& (Trading_Value_1M_P50/Trading_Session > {w_te7}) ",

}

bulldvg_config = {
    'pattern_name': 'BullDvg',
    'utilize_percent': 1,
    'cutloss': 0.15,
    'search_space': {
        'w00': scope.int(hp.quniform('w00', 1, 6, 1)),
        'w0': hp.quniform('w0', 8e+8, 40e+8, 2e+8),
        'w1': hp.quniform('w1', 0.6, 0.95, 0.02),
        'w2': hp.quniform('w2', 0.3, 0.6, 0.02),
        'w3': hp.quniform('w3', 0.6, 0.7, 0.02),
        'w4': hp.quniform('w4', 0.2, 0.5, 0.02),
        'w5': hp.quniform('w5', 0.01, 0.15, 0.01),
        'w6': hp.quniform('w6', 1.0, 1.34, 0.02),
        'w7': hp.quniform('w7', 0.8, 1.4, 0.05),
        'w8': hp.quniform('w8', 1, 8, 1),
        'w9': hp.quniform('w9', 8, 15, 0.2),
        'w10': hp.quniform('w10', 2, 6, 0.2),
        'w11': hp.quniform('w11', 3, 8, 0.1),
        'w11_1': hp.quniform('w11_1', 0, 3, 0.1),
        'w12': hp.quniform('w12', 0.02, 0.1, 0.005),
        'w13': hp.quniform('w13', 20, 40, 0.5),
        'w14': hp.quniform('w14', 0.5, 5, 0.5),
        'w15': hp.quniform('w15', 0.03, 0.15, 0.01),
        'w16': hp.quniform('w16', 3, 10, 0.5),
        'w17': hp.quniform('w17', 4600, 10000, 200),
        'w18': hp.quniform('w18', 1.0, 1.5, 0.05),
        'w19': hp.quniform('w19', 0.6, 0.85, 0.05),
    },
    'init_vals': {
        'w00': 3.0,
        'w0': 10e+8,
        'w1': 0.8,
        'w2': 0.46,
        'w3': 0.86,
        'w4': 0.44,
        'w5': 0.08,
        'w6': 1.08,
        'w7': 1.8,
        'w8': 4.0,
        'w9': 11.8,
        'w10': 3.4,
        'w11': 3.1,
        'w11_1': 0.0,
        'w12': 0.025,
        'w13': 22.5,
        'w14': 1.0,
        'w15': 0.064,
        'w16': 7.0,
        'w17': 7800.0,
        'w18': 1.3,
        'w19': 0.6,
    },
    'filter_template': "((Volume_3M_P50*Price/Inflation_7)>{w0}) "
                       "& (Risk_Rating <= {w00}) "
                       "& (D_RSI / D_RSI_T1 > {w1}) & (D_RSI > {w2}) & (D_RSI < {w3}) "
                       "& (D_RSI_Min3M < {w4}) & (D_RSI_Min1W > {w5}) "
                       "& (D_RSI_Min1W/D_RSI_Min3M > {w6}) & (D_RSI_Min1W_Close/D_RSI_Min3M_Close < {w7}) "
                       "& (FSCORE > {w8})"
                       "& (PE< {w9}) & (PE>{w10}) "
                       "& (PB < {w11}) & (PB > {w11_1}) "
                       "& (ROE_Min5Y > {w12}) "
                       "& (PCF <{w13}) & (PCF>{w14}) "
                       "& (((CF_OA_3Y/3)/ (LtDebt_P0+1) > {w15})|(abs(IntCov_P0) > {w16})) "
                       "& ((CF_OA_5Y/OShares)> {w17}) "
                       "& (NP_P0/NP_P4 >={w18})"
                       "& (Close/PC_6M >={w19})"
}

buysupport_config = {
    'pattern_name': 'BuySupport',
    'utilize_percent': 1,
    'cutloss': 0.15,
    'search_space': {
        'w00': scope.int(hp.quniform('w00', 1, 6, 1)),
        'w0': hp.quniform('w0', 8e+8, 40e+8, 2e+8),
        'w1': hp.quniform('w1', 0.8, 1, 0.02),
        'w2': hp.quniform('w2', 1, 1.2, 0.01),
        'w3': hp.quniform('w3', 1.2, 1.6, 0.01),
        'w4': hp.quniform('w4', 5, 20, 0.5),
        'w4_1': hp.quniform('w4_1', 0, 5, 0.5),
        'w5': hp.quniform('w5', 0.2, 5, 0.05),
        'w5_1': hp.quniform('w5_1', 0, 0.5, 0.01),
        'w6': hp.quniform('w6', 25, 35, 0.2),
        'w7': hp.quniform('w7', 0, 5, 0.2),
        'w8': hp.quniform('w8', 0.03, 0.15, 0.01),
        'w9': hp.quniform('w9', 1, 10, 0.5),
        'w10': hp.quniform('w10', 3000, 12000, 200),
        'w11': hp.quniform('w11', 0, 0.35, 0.005),
        'w12': hp.quniform('w12', 1.2, 2, 0.05),
    },
    'init_vals': {
        'w00': 3.0,
        'w0': 10e+8,
        'w1': 0.8,  # Hệ số nhân của Sup_1Y
        'w2': 1.2,  # Hệ số nhân của Sup_1Y cho LO_3M_T1
        'w3': 1.25,  # Hệ số nhân của LO_3M_T1
        'w4': 8.0,  # Ngưỡng tối đa của PE
        'w4_1': 3.0,  # Ngưỡng tối thiểu của PE
        'w5': 4.6,  # Ngưỡng tối đa của PB
        'w5_1': 0.5,  # Ngưỡng tối thiểu của PB
        'w6': 30.2,  # Ngưỡng tối đa của PCF
        'w7': 0.6,  # Ngưỡng tối thiểu của PCF
        'w8': 0.015,  # Điều kiện tối thiểu cho (CF_OA_3Y/3) / (LtDebt_P0+1)
        'w9': 7.0,  # Ngưỡng cho IntCov_P0
        'w10': 8000.0,  # Điều kiện tối thiểu cho CF_OA_5Y / OShares
        'w11': 0.105,  # Ngưỡng tối thiểu của ROE_Min5Y
        'w12': 1.2
    },
    'filter_template': "((Volume_3M_P50*Price/Inflation_7)>{w0}) "
                       "& (Risk_Rating <= {w00}) "
                       "& (Close >{w1}* Sup_1Y) & (Close < {w2}*Sup_1Y) & (Res_1Y > {w3}* Sup_1Y)"
                       "& (Volume > {w12}*Volume_3M_P50)"
                       "& (PE < {w4}) & (PE>{w4_1}) "
                       "& (PB <{w5}) & (PB>{w5_1}) "
                       "& (PCF <{w6}) & (PCF >{w7})  "
                       "&  (((CF_OA_3Y/3)/ (LtDebt_P0+1) > {w8})|abs(IntCov_P0 > {w9})) "
                       "& ((CF_OA_5Y/OShares)> {w10}) "
                       "& (ROE_Min5Y > {w11}) "
                       "& (ICB_Code != 2353)",
}

conservative_config = {
    'pattern_name': 'Conservative',
    'utilize_percent': 1,
    'cutloss': 0.15,
    'search_space': {
        'w00': scope.int(hp.quniform('w00', 1, 6, 1)),
        'w0': hp.quniform('w0', 3e+8, 30e+8, 2e+8),
        'w1': hp.quniform('w1', 0.03, 0.1, 0.005),
        'w2': hp.quniform('w2', 0.05, 0.2, 0.01),
        'w3': hp.quniform('w3', 0.05, 0.1, 0.005),

        # (abs(IntCov_P0) > {w4}))
        'w4': hp.quniform('w4', 3.0, 10.0, 0.2),
        # (NP_P0 / NP_P1 > {w5})
        # 'w5': hp.quniform('w5', 1.0, 1.6, 0.02),
        # (PE > {w6})
        'w6': hp.quniform('w6', 1, 6, 0.2),
        # (ROE_Min3Y > {w7})
        'w7': hp.quniform('w7', 0.0, 0.1, 0.005),
        # (PE < {w8})
        'w8': hp.quniform('w8', 20, 35, 1),
        # (NP_P0 / NP_P4 > {w9})
        'w9': hp.quniform('w9', 1.0, 1.5, 0.05),
    },
    'init_vals': {
        'w00': 3.0,
        'w0': 3e+8,
        'w1': 0.045,  # Tỷ lệ dòng tiền hoạt động và đầu tư trung bình trên vốn
        'w2': 0.11,  # Tỷ lệ dòng tiền trong 4 quys gần nhất trên vốn
        # Tỷ lệ dòng tiền trong 4 quys gần nhất trên vốn trừ đi trung bình dòng tiền hoạt động và đầu tư trên vốn
        'w3': 0.1,  # Tỷ lệ tiền mặt trên nợ dài hạn
        'w4': 6.0,  # Độ bao phủ lãi suất tối thiểu
        # 'w5': 1.1,  # Tỷ lệ lợi nhuận hiện tại trên năm trước
        'w6': 1.2,  # PE tối thiểu
        'w7': 0.09,  # ROE trung bình 3 năm tối thiểu
        'w8': 21.0,  # PE tối đa
        'w9': 1.05,
    },
    'filter_template': "((Volume_3M_P50*Price/Inflation_7)>{w0}) "
                       "& (Risk_Rating <= {w00}) "
                       "&(((CF_OA_5Y + CF_Invest_5Y )/5)/(OShares*Price + LtDebt_P0) > {w1}) "
                       "& ((CF_OA_P0+CF_OA_P1+CF_OA_P2+CF_OA_P3 + CF_Invest_P0 + CF_Invest_P1+ CF_Invest_P2+CF_Invest_P3)"
                       "/(OShares*Price + LtDebt_P0)>{w2}) "
                       "& ((CF_OA_P0+CF_OA_P1+CF_OA_P2+CF_OA_P3 + CF_Invest_P0 + CF_Invest_P1+ CF_Invest_P2+CF_Invest_P3) - ((CF_OA_5Y + CF_Invest_5Y )/5)) / (OShares*Price + LtDebt_P0) < {w3} "
                       "& (abs(IntCov_P0) > {w4}) "
    # "& (NP_P0 /NP_P1> {w5}) & (NP_P1>0) "
                       "& (NP_P0>0) & (NP_P1>0) & (NP_P2>0) & (NP_P3>0) & (NP_P4>0)"
                       "& (PE >{w6}) & (PE < {w8}) "
                       "& (ROE_Min3Y > {w7}) "
                       "& (NP_P0/NP_P4 > {w9})",
}

surpriseearning_config = {
    'pattern_name': 'SurpriseEarning',
    'utilize_percent': 1,
    'cutloss': 0.15,
    'search_space': {
        'w00': scope.int(hp.quniform('w00', 1, 6, 1)),
        'w0': hp.quniform('w0', 8e+8, 40e+8, 2e+8),
        'w1': hp.quniform('w1', 5, 20, 0.5),  # PE < w1
        'w1_1': hp.quniform('w1_1', 0.5, 5, 0.5),  # PE > w1_1
        'w2': hp.quniform('w2', 3, 4, 0.05),  # PB < w2
        'w2_1': hp.quniform('w2_1', 0.2, 1, 0.01),  # PB > w2_1
        'w3': hp.quniform('w3', 0.03, 0.1, 0.01),  # ROE_Min5Y > w3
        'w4': hp.quniform('w4', 1.2, 2, 0.02),  # (NP_P0/NP_P4) > {w4})
        'w5': hp.quniform('w5', 1.15, 2, 0.02),  # NP_P0 / NP_P1 > w5
        'w7': hp.quniform('w7', 0, 5, 0.5),  # PCF > w7
        'w8': hp.quniform('w8', 20, 30, 0.5),  # PCF < w8
        'w9': hp.quniform('w9', 1000, 10000, 500),  # CF_OA_5Y / OShares > w9
        'w10': hp.quniform('w10', 0.03, 0.15, 0.01),  # (CF_OA_3Y/3) / (LtDebt_P0+1) > w10
        'w11': hp.quniform('w11', 3, 10, 0.5),  # abs(IntCov_P0) > w11
    },
    'init_vals': {
        'w00': 3.0,
        'w0': 10e+8,
        'w1': 11.5,  # PE < 10
        'w1_1': 3.0,  # PE > 3
        'w2': 1.9,  # PB < 1
        'w2_1': 0.5,  # PB > 0.5
        'w3': 0.01,  # ROE_Min5Y > 0.05
        'w4': 0.18,  # (NP_P0 - NP_P4)/NP_P4 > 0.22
        'w5': 1.4,  # NP_P0 / NP_P1 > 1.2
        'w7': 1.0,  # PCF > 0
        'w8': 16.0,  # PCF < 25
        'w9': 9500.0,  # CF_OA_5Y / OShares > 5000
        'w10': 0.01,  # (CF_OA_3Y/3) / (LtDebt_P0+1) > 0.01
        'w11': 1.0,  # abs(IntCov_P0) > 3
    },
    'filter_template': "((Volume_3M_P50*Price/Inflation_7)>{w0}) "
                       "& (Risk_Rating <= {w00}) "
                       "& (PE < {w1}) & (PE > {w1_1}) "
                       "& (PB < {w2}) & (PB > {w2_1}) "
                       "& (ROE_Min5Y > {w3}) "
                       "& (NP_P0/NP_P4) > {w4}) "
                       "& (NP_P0/NP_P1> {w5}) & (NP_P1 > 0) "
                       "& (PCF > {w7}) & (PCF < {w8}) "
                       "& (CF_OA_5Y/OShares > {w9}) "
                       "& (((CF_OA_3Y/3)/(LtDebt_P0+1) >{w10})|(abs(IntCov_P0) > {w11}))",
}

supergrowth_config = {
    'pattern_name': 'SuperGrowth',
    'utilize_percent': 1,
    'cutloss': 0.15,
    'search_space': {
        'w00': scope.int(hp.quniform('w00', 1, 6, 1)),
        'w0': hp.quniform('w0', 8e+8, 40e+8, 2e+8),
        # (PE/((NP_P0/NP_P4 -1)*100) < {w1})
        'w1': hp.quniform('w1', 0.5, 1, 0.01),
        # (ROE_Min5Y > {w2})
        'w2': hp.quniform('w2', 0.05, 0.2, 0.005),
        # (FSCORE >= {w3})
        'w3': scope.int(hp.quniform('w3', 1, 9, 1)),
        # (NP_P0/NP_P4 > {w4})
        'w4': hp.quniform('w4', 1.2, 2, 0.01),
        # (PCF > {w5})
        'w5': hp.quniform('w5', 0, 5, 0.5),
        # (PCF < {w6})
        'w6': hp.quniform('w6', 20, 30, 0.5),
        # (CF_OA_5Y/OShares > {w7})
        'w7': hp.quniform('w7', 1000, 10000, 500),
        # (ID_Current -  ID_Release <= {w8})
        'w8': hp.quniform('w8', 10, 66, 2),
    },
    'init_vals': {
        'w00': 6.0,
        'w0': 1800000000,
        'w1': 1.09,  # PE/((NP_P0/NP_P4 -1)*100) < 1
        'w2': 0.05,  # ROE_Min5Y > 0.1
        'w3': 1.0,  # FSCORE >= 4
        'w4': 1.09,  # NP_P0/NP_P4 > 1.2
        'w5': 0.3,  # PCF > 0
        'w6': 20.0,  # PCF < 25
        'w7': 6500.0,  # CF_OA_5Y/OShares > 5000
        'w8': 12.0,
    },
    'filter_template': "((Volume_3M_P50*Price/Inflation_7)>{w0}) "
                       "& (Risk_Rating <= {w00}) "
                       "& (PE/((NP_P0/NP_P4 -1)*100) < {w1}) "
                       "& (ROE_Min5Y > {w2}) "
                       "&  ((FSCORE>={w3})) "
                       "& (NP_P0/NP_P4 > {w4})  & (NP_P4 >= 0)  "
                       "& (PCF > {w5}) & (PCF < {w6}) "
                       "& (CF_OA_5Y/OShares > {w7}) "
                       "& (ID_Current -  ID_Release <= {w8})",
}

trendinggrowth_config = {
    'pattern_name': 'TrendingGrowth',
    'utilize_percent': 1,
    'cutloss': 0.15,
    'search_space': {
        'w00': scope.int(hp.quniform('w00', 1, 6, 1)),
        'w0': hp.quniform('w0', 8e+8, 40e+8, 2e+8),
        # (Close > {w1} * Volume_Max5Y_High)
        # 'w1': hp.quniform('w1', 0.98, 1.15, 0.01),
        # (ROE_Min5Y > {w2})
        'w2': hp.quniform('w2', 0.02, 0.1, 0.005),
        # (PE <= {w3})
        'w3': hp.quniform('w3', 5, 15, 0.2),
        # (NP_P0 > {w4} * NP_P1)
        'w4': hp.quniform('w4', 1.2, 1.6, 0.05),
        # (NP_P1 > {w7} * NP_P2)
        'w7': hp.quniform('w7', 1.1, 1.5, 0.05),
        # (PE > {w5})
        'w5': hp.quniform('w5', 0, 5, 0.2),
        # (HI_3M_T1/LO_3M_T1 < {w6})
        # 'w6': hp.quniform('w6', 1.5, 3.0, 0.05),
        'w1': hp.quniform('w1', 3, 4, 0.05),  # PB < w1
        'w1_1': hp.quniform('w1_1', 0.2, 1, 0.01),  # PB > w1_1
        'w8': hp.quniform('w8', 0, 5, 0.5),  # PCF > w8
        'w9': hp.quniform('w9', 20, 30, 0.5),  # PCF < w9
    },
    'init_vals': {
        'w00': 3.0,
        'w0': 10e+8,
        # 'w1': 1.0,  # Close > 1.05 * Volume_Max5Y_High
        'w2': 0.04,  # ROE_Min5Y > 0.05
        'w3': 10.2,  # PE <= 10
        'w4': 1.15,  # NP_P0 > 1.2 * NP_P1
        'w5': 2.4,  # PE > 0
        # 'w6': 2.2,  # HI_3M_T1/LO_3M_T1 < 1.95
        'w7': 1.15,  # NP_P1 > 1.2 * NP_P2
        'w1': 3.0,  # PB < w1
        'w1_1': 0.2,  # PB > w1_1
        'w8': 0,  # PCF > w8
        'w9': 20,  # PCF < w9
    },
    'filter_template': "((Volume_3M_P50*Price/Inflation_7)>{w0}) "
                       "& (Risk_Rating <= {w00}) "
    # "& (Close> {w1}*Volume_Max5Y_High) "
                       "& (ROE_Min5Y > {w2})"
                       "& (PE<={w3}) & (PE >{w5}) "
                       "& (NP_P0 > {w4}*NP_P1) & (NP_P1 > {w7}*NP_P2)"
    # "& (HI_3M_T1/LO_3M_T1<{w6})"
                       "& (PB < {w1}) & (PB > {w1_1}) "
                       "& (PCF > {w8}) & (PCF < {w9}) "

}

tl3m_config = {
    'pattern_name': 'TL3M',
    'utilize_percent': 1,
    'cutloss': 0.15,
    'search_space': {
        'w00': scope.int(hp.quniform('w00', 1, 6, 1)),
        'w0': hp.quniform('w0', 8e+8, 40e+8, 2e+8),
        # (HI_3M_T1/LO_3M_T1 < {w1})
        'w1': hp.quniform('w1', 1, 1.5, 0.02),
        # (Volume > {w2} * Volume_3M_P90)
        'w2': hp.quniform('w2', 1, 2, 0.01),
        # (ROE5Y > {w3})
        'w3': hp.quniform('w3', 0.02, 0.2, 0.005),
        # (PE < {w4})
        'w4': hp.quniform('w4', 5, 25, 1),
        # (PB < {w5})
        'w5': hp.quniform('w5', 3, 4, 0.05),
        'w5_1': hp.quniform('w5_1', 0.5, 1, 0.05),
        # (FSCORE > {w6})
        'w6': hp.quniform('w6', 1, 8, 1),
        # # (NP_P0 > {w7} * NP_P1)
        # 'w7': hp.quniform('w7', 1.1, 1.4, 0.02),
        # (PCF > {w8})
        'w8': hp.quniform('w8', 0, 5, 0.2),
        # (PCF < {w8_1})
        'w8_1': hp.quniform('w8_1', 20, 30, 0.5),
        # (PE > {w9})
        'w9': hp.quniform('w9', 0, 5, 0.05),
    },
    'init_vals': {
        'w00': 3.0,
        'w0': 10e+8,
        'w1': 1.36,  # HI_3M_T1/LO_3M_T1 < 1.28
        'w2': 1.23,  # Volume > 1.16 * Volume_3M_P90
        'w3': 0.07,  # ROE5Y > 0.135
        'w4': 10.0,  # PE < 20
        'w5': 1.9,  # PB < 1.97
        'w5_1': 0.0,  # PB < 1.97
        'w6': 1.0,  # FSCORE > 4
        # 'w7': 1.2,  # NP_P0 > 1.16 * NP_P1
        'w8': 0.4,  # PCF > 0
        'w8_1': 10.0,  # PCF < 10
        'w9': 3.0,  # PE > 0
    },
    'filter_template': "((Volume_3M_P50*Price/Inflation_7)>{w0}) "
                       "& (Risk_Rating <= {w00}) "
                       "& (HI_3M_T1/LO_3M_T1<{w1}) "
                       "& (Volume > {w2}*Volume_3M_P90)"
                       "& (ROE5Y>{w3}) "
                       "& (PE<{w4})  & (PE >{w9})"
                       "& (PB < {w5}) & (PB >{w5_1})"
                       "& (FSCORE > {w6}) "
                       "& (NP_P0>0) & (NP_P1>0) & (NP_P2>0) & (NP_P3>0)"
                       "& (PCF>{w8}) & (PCF<{w8_1})",
}

bkma200_config = {
    'pattern_name': 'BKMA200',
    'utilize_percent': 1,
    'cutloss': 0.15,
    'search_space': {
        'w00': scope.int(hp.quniform('w00', 1, 6, 1)),
        'w0': hp.quniform('w0', 8e+8, 40e+8, 2e+8),
        # ((ID_LO_3Y - ID_HI_3Y) > {w1})
        'w1': hp.quniform('w1', 200, 350, 5),
        # (MA50/MA200 > {w2})
        'w2': hp.quniform('w2', 0.75, 1.0, 0.01),
        # (MA10/MA200 < {w3})
        'w3': hp.quniform('w3', 1, 1.4, 0.01),
        # (ROE5Y > {w4})
        'w4': hp.quniform('w4', 0.02, 0.1, 0.005),
        # (PE < {w5})
        'w5': hp.quniform('w5', 20, 30, 0.5),
        'w5_1': hp.quniform('w5_1', 0, 5, 0.5),
        # (NP_P0 > {w6} * NP_P1)
        'w6': hp.quniform('w6', 1.0, 1.5, 0.02),
        # (HI_3M_T1 / LO_3M_T1 < {w7})
        'w7': hp.quniform('w7', 1.1, 2, 0.05),
        # 'w8': hp.quniform('w8', 0, 0.1, 0.005),

    },
    'init_vals': {
        'w00': 3.0,
        'w0': 8e+8,
        'w1': 210.0,  # ID_LO_3Y - ID_HI_3Y > 293
        'w2': 0.96,  # MA50/MA200 > 0.86
        'w3': 1.53,  # MA10/MA200 < 1.37
        'w4': 0.07,  # ROE5Y > 0.09
        'w5': 14.5,  # PE < 20
        'w5_1': 0.0,  # PE < 20
        'w6': 1.14,  # NP_P0 > 1.2 * NP_P1
        'w7': 1.9,  # HI_3M_T1 / LO_3M_T1 < 1.958
        # 'w8': 0.065,  # ROE_Min3Y > 0.05
    },
    'filter_template': "((Volume_3M_P50*Price/Inflation_7)>{w0}) "
                       "& (Risk_Rating <= {w00}) "
                       "& ((ID_LO_3Y-ID_HI_3Y)>{w1}) "
                       "& (MA50/MA200>{w2}) & (MA10/MA200<{w3}) "
                       "& (ROE5Y >{w4}) "
                       "& (PE <{w5}) & (PE >{w5_1})"
                       "& (NP_P0 > {w6}*NP_P1) & (NP_P1 > 0) "
                       "& (HI_3M_T1/LO_3M_T1<{w7}) "
    # "& (ROE_Min3Y >{w8})",
}

underbv_config = {
    'pattern_name': 'UnderBV',
    'utilize_percent': 1,
    'cutloss': 0.15,
    'search_space': {
        'w00': scope.int(hp.quniform('w00', 1, 6, 1)),
        'w0': hp.quniform('w0', 8e+8, 40e+8, 2e+8),
        # (PB < {w1}) & (PB > {w1_1})
        'w1': hp.quniform('w1', 0.5, 2, 0.02),
        'w1_1': hp.quniform('w1_1', 0.2, 0.5, 0.02),
        # (FSCORE >= {w2})
        'w2': hp.quniform('w2', 1, 8, 1),
        # (NP_P0 > {w3} * NP_P1)
        'w3': hp.quniform('w3', 0.85, 1.5, 0.02),
        # (PCF > {w4})
        'w4': hp.quniform('w4', 1, 4, 0.2),
        # (PE > {w5})
        'w5': hp.quniform('w5', 0, 5, 0.2),
        'w5_1': hp.quniform('w5_1', 7, 20, 0.5),
        # (PCF < {w6})
        'w6': hp.quniform('w6', 20, 30, 1),
        # ((NP_P0 + NP_P1 + NP_P2 + NP_P3) / OShares > {w7})
        'w7': hp.quniform('w7', 500, 2500, 100),
        # (NP_P0 / NP_P4 > {w8})
        'w8': hp.quniform('w8', 1, 1.6, 0.05),
    },
    'init_vals': {
        'w00': 3.0,
        'w0': 10e+8,
        'w1': 1.2,  # PB < 0.9
        'w1_1': 0.5,  # PB > 0.5
        'w2': 1.0,  # FSCORE >= 4
        'w3': 1.32,  # NP_P0 > 0.90 * NP_P1
        'w4': 1.0,  # PCF > 2
        'w5': 0.0,  # PE > 0
        'w5_1': 10.0,  # PE < 10
        'w6': 23.0,  # PCF < 25
        'w7': 1750.0,  # (NP_P0 + NP_P1 + NP_P2 + NP_P3) / OShares > 500
        'w8': 1.15,  # NP_P0 / NP_P4 > 1.15
    },
    'filter_template': "((Volume_3M_P50*Price/Inflation_7)>{w0}) "
                       "& (Risk_Rating <= {w00}) "
                       "& (PB < {w1}) & (PB > {w1_1}) "
                       "& (FSCORE >= {w2}) "
                       "& (NP_P0 > {w3}*NP_P1)  "
                       "& (PCF>{w4}) & (PCF<{w6})"
                       "& (PE >{w5}) & (PE<{w5_1}) "
                       "& ((NP_P0+NP_P1+NP_P2+NP_P3)/OShares > {w7}) "
                       "& (NP_P0/NP_P4 > {w8})"
                       "& (NP_P0>0) & (NP_P2>0) & (NP_P3>0)",
}

rsilow30_config = {
    'pattern_name': 'RSILow30',
    'utilize_percent': 1,
    'cutloss': 0.15,
    'search_space': {
        'w00': scope.int(hp.quniform('w00', 1, 6, 1)),
        'w0': hp.quniform('w0', 8e+8, 40e+8, 2e+8),
        # (D_RSI < {w1})
        'w1': hp.quniform('w1', 0.1, 0.3, 0.01),
        # (PE < {w2})
        'w2': hp.quniform('w2', 5, 15, 0.2),
        # (PE > {w3})
        'w3': hp.quniform('w3', 0, 5, 0.2),
        # (ROE_Min3Y > {w4})
        'w4': hp.quniform('w4', 0.01, 0.1, 0.005),
        # (PB < {w5}*PB_MA5Y - {w6}*PB_SD5Y)
        'w5': hp.quniform('w5', 0.5, 1.5, 0.1),
        'w6': hp.quniform('w6', 0.2, 1.5, 0.1),
        # (PCF > {w7})
        'w7': hp.quniform('w7', 0, 5, 0.2),
        # (PCF < {w8})
        'w8': hp.quniform('w8', 20, 30, 0.5),
        # (((CF_OA_3Y/3)/ (LtDebt_P0+1) > {w9}) | (abs(IntCov_P0) > {w10}))
        'w9': hp.quniform('w9', 0.03, 0.15, 0.01),
        # Giá trị tham chiếu: w10 = 3, tìm trong khoảng [1, 10]
        'w10': hp.quniform('w10', 3, 10, 0.5),
    },
    'init_vals': {
        'w00': 3.0,
        'w0': 10e+8,
        'w1': 0.3,  # D_RSI < 0.3
        'w2': 7.4,  # PE < 9
        'w3': 3.8,  # PE > 0
        'w4': 0.05,  # ROE_Min3Y > 0.035
        'w5': 0.85,  # PB_MA5Y coefficient
        'w6': 0.55,  # PB_SD5Y coefficient
        'w7': 2.4,  # PCF > 0
        'w8': 27.0,  # PCF < 25
        'w9': 0.06,  # (CF_OA_3Y/3) / (LtDebt_P0 + 1) > 0.02
        'w10': 3.4,  # abs(IntCov_P0) > 3
    },
    'filter_template': "((Volume_3M_P50*Price/Inflation_7)>{w0}) "
                       "& (Risk_Rating <= {w00}) "
                       "& (D_RSI < {w1})  "
                       "& (PE < {w2})  & (PE>{w3}) "
                       "& (ROE_Min3Y > {w4}) "
                       "& (PB < {w5}*PB_MA5Y - {w6}*PB_SD5Y) "
                       "& (PCF > {w7}) & (PCF <{w8}) "
                       "& (((CF_OA_3Y/3)/ (LtDebt_P0+1) > {w9})|(abs(IntCov_P0) > {w10})) "
                       "& (NP_P0 > 0)",
}

volmax1y_config = {
    'pattern_name': 'VolMax1Y',
    'utilize_percent': 1,
    'cutloss': 0.15,
    'search_space': {
        'w00': scope.int(hp.quniform('w00', 1, 6, 1)),
        'w0': hp.quniform('w0', 8e+8, 40e+8, 2e+8),
        # (Close > {w1}*Volume_Max1Y_High)
        'w1': hp.quniform('w1', 1.0, 1.2, 0.01),
        # (Close_T1W < {w2}*Volume_Max1Y_High)
        'w2': hp.quniform('w2', 0.8, 1, 0.01),
        # (Volume > {w3}*Volume_3M_P50)
        'w3': hp.quniform('w3', 0.9, 2, 0.1),
        # (PE > {w4})
        'w4': hp.quniform('w4', 0, 4, 0.2),
        # (PE < {w5})
        'w5': hp.quniform('w5', 10, 20, 0.2),
        # (PB < {w6})
        'w6': hp.quniform('w6', 2, 5, 0.1),
        # (PB > {w6_1})
        'w6_1': hp.quniform('w6_1', 0.5, 2, 0.05),
        # (PCF > {w7})
        'w7': hp.quniform('w7', 0.0, 5.0, 0.2),
        # ((NP_P0 > {w8}*NP_P1) | ((NP_P0 - NP_P4)/abs(NP_P4) > {w11}))
        'w8': hp.quniform('w8', 0.5, 1.5, 0.05),
        'w11': hp.quniform('w11', 0.1, 2, 0.1),
        # (PCF < {w9})
        'w9': hp.quniform('w9', 12, 30, 0.5),
        # (ROE_Min3Y > {w10})
        'w10': hp.quniform('w10', 0.01, 0.05, 0.005),

        # # (PCF < {w12})
        # 'w12': hp.quniform('w12', 10, 20, 0.2),
        # (ID_Current - Volume_Max1Y_ID <= {w13})
        'w13': hp.quniform('w13', 50, 220, 5),
        # (Volume_Max1Y_High / LO_3M_T1 < {w14})
        'w14': hp.quniform('w14', 1.1, 1.8, 0.05),
        # (FSCORE > {w15})
        'w15': hp.quniform('w15', 1, 8, 1),
    },
    'init_vals': {
        'w00': 3.0,
        'w0': 10e+8,
        'w1': 1.01,  # Close > 1.02 * Volume_Max1Y_High
        'w2': 1.08,  # Close_T1W < Volume_Max1Y_High
        'w3': 0.85,  # Volume > Volume_3M_P50
        'w4': 1.0,  # PE > 0
        'w5': 10.8,  # PE < 16
        'w6': 4.0,  # PB < 3.5
        'w6_1': 1.0,  # PB > 1
        'w7': 1.0,  # PCF > 0
        'w8': 1.15,  # NP_P0 > 1.2 * NP_P1
        'w9': 15.8,  # PCF < 25
        'w10': 0.025,  # ROE_Min2Y > 0.03
        'w11': 1.1,  # (NP_P0 - NP_P4)/abs(NP_P4) > 1
        'w12': 11.4,  # PCF < 15
        'w13': 150.0,  # ID_Current - Volume_Max1Y_ID <= 120
        'w14': 1.45,  # Volume_Max1Y_High / LO_3M_T1 < 1.3
        'w15': 3.0,  # FSCORE > 3
    },
    'filter_template': "((Volume_3M_P50*Price/Inflation_7)>{w0}) "
                       "& (Risk_Rating <= {w00}) "
                       "& (Close > {w1}*Volume_Max1Y_High) & (Close_T1W < {w2}*Volume_Max1Y_High) "
                       "& (Volume > {w3}*Volume_3M_P50) "
                       "& (PE >{w4}) & (PE < {w5}) "
                       "& (PB<{w6}) & (PB > {w6_1}) "
                       "& ((NP_P0 > {w8}*NP_P1) | ((NP_P0 - NP_P4)/abs(NP_P4) > {w11})) "
                       "& (PCF > {w7}) "
                       "& (PCF < {w9})"
                       "& (ROE_Min3Y > {w10})"
                       "& (ID_Current-Volume_Max1Y_ID<={w13})  "
                       "& (Volume_Max1Y_High/LO_3M_T1 < {w14}) "
                       "& (FSCORE > {w15})",
}

t3p4_config = {
    'pattern_name': 'T3P4',
    'utilize_percent': 1,
    'cutloss': 0.15,
    'search_space': {
        'w00': scope.int(hp.quniform('w00', 1, 6, 1)),
        'w0': hp.quniform('w0', 8e+8, 40e+8, 2e+8),

        # W_CMB (Weekly Combine Momentum)
        # ((((W_CMB_Step>{w1}) & (W_CMB_LEN>={w2}) & (W_CMB_LAG>{w3})& (W_CMB_LAG<={w4}))
        'w1': hp.quniform('w1', 0, 0.1, 0.005),  # Step
        'w2': hp.quniform('w2', 1, 5, 1),  # LEN
        'w3': hp.quniform('w3', 0, 3, 1),  # LAG lower
        'w4': hp.quniform('w4', 3, 7, 1),  # LAG upper
        # M_CMB (Monthly Combine Momentum)
        # | ((M_CMB_Step>{w5}) & (M_CMB_LEN>={w6}) & (M_CMB_LAG >{w7}) & (M_CMB_LAG <={w8}))))
        'w5': hp.quniform('w5', 0, 0.1, 0.005),  # Step
        'w6': hp.quniform('w6', 1, 6, 1),  # LEN
        'w7': hp.quniform('w7', 0, 2, 1),  # LAG lower
        'w8': hp.quniform('w8', 2, 6, 1),  # LAG upper
        # (ROE5Y>={w9}) & (ROE5Y<={w10})"
        'w9': hp.quniform('w9', 0.04, 0.1, 0.01),  # Lower
        'w10': hp.quniform('w10', 0.1, 0.3, 0.01),  # Upper
        # (NP_P0>{w11}*NP_P4) & (NP_P4 > 0) "
        'w11': hp.quniform('w11', 1.0, 1.3, 0.05),
        # (PE<{w12}) & (PE > {w12_1}) "
        'w12': hp.quniform('w12', 10, 20, 0.2),
        'w12_1': hp.quniform('w12_1', 0, 5, 0.2),
        # (C_H2Y>{w13}) & (C_H2Y<{w14}) "
        'w13': hp.quniform('w13', 0.2, 0.7, 0.05),  # Lower bound
        'w14': hp.quniform('w14', 0.7, 0.9, 0.02),  # Upper bound
        # FSCORE > w15
        'w15': hp.quniform('w15', 1, 8, 1),

    },
    'init_vals': {
        'w00': 3.0,
        'w0': 10e+8,
        'w1': 0.025,  # W_CMB_Step > 0.025
        'w2': 2.0,  # W_CMB_LEN >= 2
        'w3': 0.0,  # W_CMB_LAG > 0
        'w4': 3.0,  # W_CMB_LAG <= 3

        'w5': 0.025,  # M_CMB_Step > 0.025
        'w6': 2.0,  # M_CMB_LEN >= 2
        'w7': 1.0,  # M_CMB_LAG >= 1
        'w8': 4.0,  # M_CMB_LAG <= 4

        'w9': 0.13,  # ROE5Y >= 0.13
        'w10': 0.2,  # ROE5Y <= 0.2

        'w11': 1.17,  # NP_P0 > 1.17 * NP_P4
        'w12': 10.0,  # PE < 10
        'w12_1': 4.0,  # PE > 4

        'w13': 0.3,  # C_H2Y > 0.3
        'w14': 0.84,  # C_H2Y < 0.84
        'w15': 3,  # FSCORE > 3
    },
    'filter_template': "((Volume_3M_P50*Price/Inflation_7)>{w0}) "
                       "& (Risk_Rating <= {w00}) "
                       "& ((((W_CMB_Step>{w1}) & (W_CMB_LEN>={w2}) & (W_CMB_LAG>{w3})& (W_CMB_LAG<={w4})) "
                       "| ((M_CMB_Step>{w5}) & (M_CMB_LEN>={w6}) & (M_CMB_LAG >{w7}) & (M_CMB_LAG <={w8})))) "
                       "& (ROE5Y>={w9}) & (ROE5Y<={w10})"
                       "& (NP_P0>{w11}*NP_P4) & (NP_P4 > 0) "
                       "& (PE<{w12}) & (PE > {w12_1}) "
                       "& (C_H2Y>{w13}) & (C_H2Y<{w14}) "
                       "& (FSCORE > {w15})"

}

dy_config = {
    'pattern_name': 'DividendYield',
    'utilize_percent': 1,
    'cutloss': 0.2,
    'search_space': {
        'w00': scope.int(hp.quniform('w00', 1, 6, 1)),
        'w0': hp.quniform('w0', 8e+8, 40e+8, 2e+8),
        # (PCF>{w1}) & (PCF < {w2})
        'w1': hp.quniform('w1', 0, 5, 0.5),  # PCF lower
        'w2': hp.quniform('w2', 10, 30, 1),  # PCF upper
        'w3': hp.quniform('w3', 1, 1.5, 0.02),  # NP_P0/NP_P1 > w3
        'w4': hp.quniform('w4', 0, 5, 0.5),  # PE > w4
        'w5': hp.quniform('w5', 10, 20, 0.5),  # PE < w5
        'w6': hp.quniform('w6', 1000, 10000, 500),  # CF_OA_5Y / OShares > w6
        'w7': hp.quniform('w7', 0.02, 0.12, 0.01),  # (abs(Dividend_Min3Y)/Price >{w7})

    },
    'init_vals': {
        'w00': 3.0,
        'w0': 10e+8,
        'w1': 0.0,  # PCF > 0
        'w2': 30.0,  # PCF < 30
        'w3': 1.0,  # NP_P0/NP_P1 < 1
        'w4': 0.0,  # PE > 0
        'w5': 18.0,  # PE < 18
        'w6': 5000.0,  # CF_OA_5Y / OShares > 5000
        'w7': 0.05,  # abs(Dividend_Min3Y / Price) > 0.04
    },
    'filter_template': "((Volume_3M_P50*Price/Inflation_7)>{w0}) "
                       "& (Risk_Rating <= {w00}) "
                       "& (PCF>{w1}) & (PCF < {w2}) "
                       "& (NP_P0 > 0) & (NP_P0/NP_P1>{w3}) "
                       "& (PE>{w4}) & (PE < {w5}) "
                       "& ((CF_OA_5Y/OShares)> {w6}) "
                       "& (abs(Dividend_Min3Y)/Price >{w7})",
}

strongcashstock_config = {
    'pattern_name': 'CashCowStock',
    'utilize_percent': 1,
    'cutloss': 0.15,
    'search_space': {
        'w00': scope.int(hp.quniform('w00', 1, 6, 1)),

        # (Volume_1M_P50 * Price / Inflation_7) > w0
        'w0': hp.quniform('w0', 8e+8, 40e+8, 2e+8),

        # (CF_OA_P0+...+CF_Invest_P3)/(OShares*Price + LtDebt_P0) > w1
        'w1': hp.quniform('w1', 0.05, 0.2, 0.005),

        # (Cash_P0 + LtInvest_P0 + AR_P0 + Inventory_P0 - StLiab_P0 - LtLiab_P0)/(OShares*Price) > w2
        'w2': hp.quniform('w2', 0.02, 0.3, 0.01),

        # abs(IntCov_P0) > w3
        'w3': hp.quniform('w3', 1, 10, 0.5),

        # PE lower bound
        'w4': hp.quniform('w4', 0, 5, 0.2),

        # PE upper bound
        'w5': hp.quniform('w5', 10, 30, 0.5),

        # (Trading_Value /Trading_Value_1M_P50 > {w6})
        'w6': hp.quniform('w6', 0.8, 2, 0.05),

        # DY > w7
        'w7': hp.quniform('w7', 0.01, 0.05, 0.002),
    },
    'init_vals': {
        'w00': 3.0,
        'w0': 10e+8,
        'w1': 0.1,
        'w2': 0.2,
        'w3': 3.0,
        'w4': 1.2,
        'w5': 20.0,
        'w6': 1.2,
        'w7': 0.02,
    },
    'filter_template': "((Volume_3M_P50*Price/Inflation_7)>{w0}) "
                       "& (Risk_Rating <= {w00}) "
                       "& ((CF_OA_P0+CF_OA_P1+CF_OA_P2+CF_OA_P3 + CF_Invest_P0 + CF_Invest_P1+ CF_Invest_P2+CF_Invest_P3)/(OShares*Price + LtDebt_P0) > {w1}) "
                       "& ((Cash_P0  + LtInvest_P0 + AR_P0 + Inventory_P0 - StLiab_P0  -  LtDebt_P0 )/(OShares*Price) > {w2}) "
                       "& (abs(IntCov_P0) > {w3}) "
                       "& (NP_P0 > 0) & (NP_P1 > 0) "
                       "& (PE > {w4}) & (PE < {w5}) "
                       "& (Trading_Value /Trading_Value_1M_P50 > {w6}) "
                       "& (DY > {w7})",
}

tradingvaluemax_config = {
    'pattern_name': 'TradingValueMax',
    'utilize_percent': 1,
    'cutloss': 0.15,
    'search_space': {
        'w00': scope.int(hp.quniform('w00', 1, 6, 1)),

        # Init: Volume * Price filter
        'w0': hp.quniform('w0', 10e+8, 40e+8, 1e+8),

        #  (PB < {w1}) & (PB > {w1_1})
        'w1': hp.quniform('w1', 2, 5, 0.2),
        'w1_1': hp.quniform('w1_1', 0.5, 2, 0.1),

        # Close < w2 *Close_2Y_P90
        'w2': hp.quniform('w2', 0.74, 1.1, 0.02),

        # D_RSI < w3
        'w3': hp.quniform('w3', 60, 85, 1),

        # FSCORE > w4
        'w4': hp.quniform('w4', 2, 7, 1),

        # (Trading_Value_Total_1W >= {w5} * Trading_Value_Total_1W_Max6M)
        'w5': hp.quniform('w5', 0.8, 1.2, 0.05),

        # Volume >= w6 * Volume_Max1Y
        'w6': hp.quniform('w6', 0.8, 1.2, 0.05),
        # PE < w7
        'w7': hp.quniform('w7', 10, 50, 1),
        # PE > w7_1
        'w7_1': hp.quniform('w7_1', 0, 5, 0.5),
        # ((C_L2Y/C_H2Y) > {w8})"
        'w8': hp.quniform('w8', 0.2, 0.7, 0.05),
        # ((ID_LO_2Y - ID_HI_2Y) > {w9})"
        'w9': hp.quniform('w9', 60, 480, 5),

    },
    'init_vals': {
        'w00': 3.0,
        'w0': 2e+9,
        'w1': 4.0,
        'w1_1': 0.0,
        'w2': 1.0,
        'w3': 78.0,
        'w4': 3.0,
        'w5': 1.0,
        'w6': 1.0,
        'w7': 20.0,
        'w7_1': 0.0,
        'w8': 0.5,
        'w9': 480,
    },
    'filter_template': "((Volume_3M_P50*Price/Inflation_7)>{w0}) "
                       "& (Risk_Rating <= {w00}) "
                       "& (Trading_Value_Total_1W >= {w5} * Trading_Value_Total_1W_Max6M) "
                       "& (Volume >= {w6} * Volume_Max1Y) "
                       "& (PE > {w7_1}) & (PE < {w7}) "
                       "& (PB < {w1}) & (PB > {w1_1}) "
                       "& (Close < {w2} * Close_2Y_P90) "
                       "& (D_RSI < {w3}) "
                       "& (FSCORE > {w4})"
                       "& ((C_L2Y/C_H2Y) > {w8})"
                       "& ((ID_LO_2Y - ID_HI_2Y) > {w9})"
}

accsup_config = {
    'pattern_name': 'AccSup',
    'utilize_percent': 1,
    'cutloss': 0.15,
    'search_space': {
        'w00': scope.int(hp.quniform('w00', 1, 6, 1)),  # Risk_Rating
        'w0': hp.quniform('w0', 10e+8, 40e+8, 1e+8),
        'w7': hp.quniform('w7', 0.4, 0.8, 0.01),  # (Close_Min1Y/Close_Max1Y < {w7})
        'w8': hp.quniform('w8', 0.8, 1.2, 0.01),  # (Volume > {w8}*Volume_3M_P90)
        'w1': hp.quniform('w1', 40, 100, 2),  # (Close_Min1Y_ID > Close_Max1Y_ID + {w1})
        'w2': hp.quniform('w2', 0.8, 1.5, 0.02),  # (Volume_1M < Volume_1M_1Y_P20*{w2})
        'w3': hp.quniform('w3', 10, 20, 0.5),  # PE max
        'w3_1': hp.quniform('w3_1', 0, 5, 0.5),  # PE min
        'w4': hp.quniform('w4', 2, 5, 0.2),  # PB max
        'w4_1': hp.quniform('w4_1', 0.5, 2, 0.1),  # PB min
        'w5': hp.quniform('w5', 2, 7, 1),  # FSCORE min
        'w6': hp.quniform('w6', 0.2, 5.0, 0.05),  # PCF min
        'w6_1': hp.quniform('w6_1', 10, 30, 1),  # PCF max
    },
    'init_vals': {
        'w00': 4.0,  # Risk_Rating < 5
        'w0': 10e+8,  # Risk_Rating < 5
        'w7': 0.7,  # Giá hiện tại đang thấp so với đỉnh 1Y
        'w1': 66.0,  # Đáy cách đỉnh đủ xa (theo thời gian)
        'w2': 0.8,  # Thanh khoản hiện tại suy kiệt
        'w3': 20.0,  # PE tối đa
        'w3_1': 0.0,  # PE tối thiểu
        'w4': 5.0,  # PB tối đa
        'w4_1': 0.0,  # PB tối thiểu
        'w5': 3.0,  # FSCORE tối thiểu
        'w6': 0.4,  # PCF tối thiểu
        'w6_1': 25.0,  # PCF tối đa
        'w8': 1.0,  # PCF tối đa
    },
    'filter_template': "((Volume_3M_P50*Price/Inflation_7)>{w0}) "
                       "& (Risk_Rating <= {w00})"
                       "& (Volume > {w8}*Volume_3M_P90) "
                       "& (Close_Min1Y/Close_Max1Y < {w7}) "
                       "& (Close_Min1Y_ID > Close_Max1Y_ID + {w1}) "
                       "& (Volume_1M < Volume_1M_1Y_P20*{w2}) "
                       "& (PE < {w3}) & (PE > {w3_1}) "
                       "& (PB < {w4}) & (PB > {w4_1}) "
                       "& (FSCORE > {w5}) "
                       "& (PCF > {w6}) & (PCF < {w6_1})",
}

vnindexbulldvg_config = {
    'pattern_name': 'VNINDEX_BullDvg',
    'utilize_percent': 1,
    'cutloss': 1,
    'search_space': {
        'w0': hp.quniform('w0', 1.0, 1.4, 0.02),  # D_RSI_Min1W / D_RSI_Min3M > w0
        'w1': hp.quniform('w1', 0.2, 0.6, 0.02),  # D_RSI_Min1W < w1
        'w2': hp.quniform('w2', 0.1, 0.4, 0.02),  # D_RSI_Min3M < w2
        'w3': hp.quniform('w3', 0.9, 1.17, 0.01),  # D_RSI_Min1W_Close/D_RSI_Min3M_Close < w3
        # 'w4': hp.quniform('w4', 0, 0.5, 0.05),  # D_MACDdiff > w4
        'w5': hp.quniform('w5', 0.3, 0.7, 0.02),  # D_RSI_MinT3 < w5
        'w6': hp.quniform('w6', 0.3, 0.7, 0.02),  # D_RSI_Max1W < w6
        'w7': hp.quniform('w7', 1.0, 1.3, 0.02),  # D_RSI/D_RSI_T1W > w7
        # 'w8': hp.quniform('w8', 0, 0.5, 0.05),  # D_CMF > w8
        'w9': hp.quniform('w9', 0.9, 1.3, 0.01),  # C_L1M < w9
        'w10': hp.quniform('w10', 0.9, 1.15, 0.005),  # C_L1W < w10
    },
    'init_vals': {
        'w0': 1.0,
        'w1': 0.45,
        'w2': 0.3,
        'w3': 1.06,
        'w4': 0.0,
        'w5': 0.5,
        'w6': 0.5,
        'w7': 1.1,
        'w8': 0.0,
        'w9': 1.09,
        'w10': 1.065,
    },
    'filter_template': "(time>='2000-01-01') & (time<='2025-01-01') & (ticker=='VNINDEX') "
                       "& (D_RSI_Min1W / D_RSI_Min3M > {w0}) "
                       "& (D_RSI_Min1W < {w1}) "
                       "& (D_RSI_Min3M < {w2}) "
                       "& (D_RSI_Min1W_Close / D_RSI_Min3M_Close < {w3}) "
                       "& (D_MACDdiff > 0) "
                       "& (D_RSI_MinT3 < {w5}) "
                       "& (D_RSI_Max1W < {w6}) "
                       "& (D_RSI / D_RSI_T1W > {w7}) "
                       "& (D_CMF > 0)"
                       "& (C_L1M < {w9}) "
                       "& (C_L1W < {w10})",
}
if __name__ == "__main__":
    # manager = PatternTuningManager(**t3p4_config, **sell_config)
    # best_params = manager.run_tuning(max_evals=2000)
    # print(f"Best parameters for BullDvg: {best_params}")

    pattern_configs = [bkma200_config, bulldvg_config, buysupport_config, conservative_config, dy_config,
                       rsilow30_config, supergrowth_config, surpriseearning_config, t3p4_config, tl3m_config,
                       trendinggrowth_config, underbv_config, volmax1y_config, strongcashstock_config,
                       tradingvaluemax_config, accsup_config]
    # pattern_configs = [buysupport_config, conservative_config, rsilow30_config, tl3m_config]
    # technical_extend
    # pattern_configs = [supergrowth_config, tl3m_config, tradingvaluemax_config, accsup_config, trendinggrowth_config,
    #                    surpriseearning_config, volmax1y_config]

    # pattern_configs = [accsup_config]
    # pattern_configs = [bkma200_config, bulldvg_config]

    results = run_multiple_patterns(pattern_configs, sell_config, technical_extend_config, max_evals=1000)
    print(f"Results for all patterns: {results}")
