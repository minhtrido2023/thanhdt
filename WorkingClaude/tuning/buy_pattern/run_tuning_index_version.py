from tuning.buy_pattern.hyo_tuning_manager import PatternTuningManager, run_multiple_patterns
from hyperopt import hp
from hyperopt.pyll.base import scope

# sell_patterns = {
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
    '~BearDvgVNI2': " (D_RSI_Max1W/D_RSI > 1.016)  & (D_RSI_Max3M > 0.77) & (D_RSI_Max1W < 0.79) & (D_RSI_Max1W>0.6) & (D_RSI_Max1W_Close/D_RSI_Max3M_Close > 1.008) & (D_RSI_Max3M_MACD/D_RSI_Max1W_MACD>1.1) & (D_MACDdiff < 0)  & ( Close/D_RSI_Max3M_Close > 0.97) & (D_RSI_MinT3 > 0.5) & (D_CMF < 0.15)"
}
# s_sell_patterns = {
#     '~BearDvgVNI1~': "(VNINDEX_RSI_Max1W/VNINDEX_RSI > 1.044)  & (VNINDEX_RSI_Max3M > 0.74) & (VNINDEX_RSI_Max1W < 0.72) & (VNINDEX_RSI_Max1W>0.61) & (VNINDEX_RSI_Max1W_Close/VNINDEX_RSI_Max3M_Close > 1.028) & (VNINDEX_RSI_Max3M_MACD/VNINDEX_RSI_Max1W_MACD>1.11) & (VNINDEX_MACDdiff < 0)  & ( Close/VNINDEX_RSI_Max3M_Close > 0.96) & (VNINDEX_RSI_MinT3 > 0.43) & (VNINDEX_CMF < 0.13)",
#     '~BearDvgVNI2~': "(VNINDEX_RSI_Max1W/VNINDEX_RSI > 1.016)  & (VNINDEX_RSI_Max3M > 0.77) & (VNINDEX_RSI_Max1W < 0.79) & (VNINDEX_RSI_Max1W>0.6) & (VNINDEX_RSI_Max1W_Close/VNINDEX_RSI_Max3M_Close > 1.008) & (VNINDEX_RSI_Max3M_MACD/VNINDEX_RSI_Max1W_MACD>1.1) & (VNINDEX_MACDdiff < 0)  & ( Close/VNINDEX_RSI_Max3M_Close > 0.97) & (VNINDEX_RSI_MinT3 > 0.5) & (VNINDEX_CMF < 0.15)"
# }

sell_config = {
    'sell_filters': sell_patterns,
    'sell_mapping': {
        f'w_{k.lower()[1:]}': k[1:] for k in sell_patterns.keys()
    },

    # 'sell_search_space': {
    #     k: hp.quniform(k, 0, 1, 1) for k in [f"w_{k.lower()[1:]}" for k in sell_patterns.keys()]
    # },

    'sell_init_vals': {
        f'w_{k.lower()[1:]}': 1 for k in sell_patterns.keys()
    },
    # 'sell_mapping': {
    #     'w_ma21': 'MA21',
    #     'w_ma31': 'MA31',
    #     'w_ma41': 'MA41',
    #     'w_s13': 'S13',
    #     'w_selllowgrowth': 'SellLowGrowth',
    #     'w_sellresistance1y': 'SellResistance1Y',
    #     'w_sellresistance1m': 'SellResistance1M',
    #     'w_sellresistance': 'SellResistance',
    #     'w_sellbv': 'SellBV',
    #     'w_sellbv2': 'SellBV2',
    #     'w_sellpe': 'SellPE',
    #     'w_sellvolmax': 'SellVolMax',
    #     'w_beardvg2': 'BearDvg2'
    # },

    'sell_search_space': {
        'w_beardvgvni2': hp.choice('w_beardvgvni2', [1]),
        },
    #     'w_ma31': hp.quniform('w_ma31', 0, 1, 1),
    #     'w_ma41': hp.quniform('w_ma41', 0, 1, 1),
    #     'w_s13': hp.quniform('w_s13', 0, 1, 1),
    #     'w_selllowgrowth': hp.quniform('w_selllowgrowth', 0, 1, 1),
    #     'w_sellresistance1y': hp.quniform('w_sellresistance1y', 0, 1, 1),
    #     'w_sellresistance1m': hp.quniform('w_sellresistance1m', 0, 1, 1),
    #     'w_sellresistance': hp.quniform('w_sellresistance', 0, 1, 1),
    #     'w_sellbv': hp.quniform('w_sellbv', 0, 1, 1),
    #     'w_sellbv2': hp.quniform('w_sellbv2', 0, 1, 1),
    #     'w_sellpe': hp.quniform('w_sellpe', 0, 1, 1),
    #     'w_sellvolmax': hp.quniform('w_sellvolmax', 0, 1, 1),
    #     'w_beardvg2': hp.quniform('w_beardvg2', 0, 1, 1),
    # },

    # 'sell_init_vals': {
    #     'w_ma21': 1,
    #     'w_ma31': 1,
    #     'w_ma41': 1,
    #     'w_s13': 1,
    #     'w_selllowgrowth': 0,
    #     'w_sellresistance1y': 1,
    #     'w_sellresistance1m': 1,
    #     'w_sellresistance': 1,
    #     'w_sellbv': 1,
    #     'w_sellbv2': 1,
    #     'w_sellpe': 1,
    #     'w_sellvolmax': 1,
    #     'w_beardvg2': 1,
    #     'BearDvgVNI2': 1,
    # }
}
# sell_config['sell_filters'].update(s_sell_patterns)

bulldvg_config = {
    'pattern_name': 'BullDvg',
    'utilize_percent': 1,
    'cutloss': 0.15,
    'search_space': {
        'w0': hp.quniform('w0', 8e+8, 40e+8, 2e+8),
        'w1': hp.quniform('w1', 0.6, 0.95, 0.02),
        'w2': hp.quniform('w2', 0.25, 0.6, 0.02),
        'w3': hp.quniform('w3', 0.6, 1, 0.02),
        'w4': hp.quniform('w4', 0.3, 0.6, 0.02),
        'w5': hp.quniform('w5', 0.01, 0.15, 0.01),
        'w6': hp.quniform('w6', 1.0, 1.34, 0.02),
        'w7': hp.quniform('w7', 1.3, 2.5, 0.05),
        'w8': hp.quniform('w8', 1, 8, 1),
        'w9': hp.quniform('w9', 8, 15, 0.2),
        'w10': hp.quniform('w10', 2, 6, 0.2),
        'w11': hp.quniform('w11', 3, 7, 0.1),
        'w12': hp.quniform('w12', 0.02, 0.1, 0.005),
        'w13': hp.quniform('w13', 20, 40, 0.5),
        'w14': hp.quniform('w14', 0.5, 5, 0.5),
        'w15': hp.quniform('w15', 0.01, 0.08, 0.002),
        'w16': hp.quniform('w16', 3, 10, 0.5),
        'w17': hp.quniform('w17', 4600, 10000, 200),
        'w18': hp.quniform('w18', 1.1, 1.6, 0.05),
    },
    'init_vals': {
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
        'w12': 0.025,
        'w13': 22.5,
        'w14': 1.0,
        'w15': 0.064,
        'w16': 7,
        'w17': 7800,
        'w18': 1.3,
    },
    'filter_template': "((Volume_1M_P50*Price/Inflation_7)>{w0}) & (time>='2014-01-01') & (time<='2026-01-01')  "
                       "& (D_RSI / D_RSI_T1 > {w1}) & (D_RSI > {w2}) & (D_RSI < {w3}) "
                       "& (D_RSI_Min3M < {w4}) & (D_RSI_Min1W > {w5}) "
                       "& (D_RSI_Min1W/D_RSI_Min3M > {w6}) & (D_RSI_Min1W_Close/D_RSI_Min3M_Close < {w7}) "
                       "& (FSCORE > {w8})"
                       "& (PE< {w9}) & (PE>{w10}) "
                       "& (PB < {w11}) "
                       "& (ROE_Min5Y > {w12}) "
                       "& (PCF <{w13}) & (PCF>{w14}) "
                       "& ((Cash_P0/ (LtDebt_P0+1) > {w15})|(abs(IntCov_P0) > {w16})) "
                       "& ((CF_OA_5Y/OShares)> {w17}) "
                       "& (NP_P0/NP_P4 >={w18})",
}

buysupport_config = {
    'pattern_name': 'BuySupport',
    'utilize_percent': 1,
    'cutloss': 0.15,
    'search_space': {
        'w0': hp.quniform('w0', 8e+8, 40e+8, 2e+8),
        'w1': hp.quniform('w1', 0.8, 1.5, 0.01),
        'w2': hp.quniform('w2', 0.9, 1.6, 0.01),
        'w3': hp.quniform('w3', 1, 1.6, 0.01),
        'w4': hp.quniform('w4', 4, 20, 0.5),
        'w5': hp.quniform('w5', 1, 7, 0.2),
        'w6': scope.int(hp.quniform('w6', 25, 35, 0.2)),
        'w7': scope.int(hp.quniform('w7', 0, 5, 0.2)),
        'w8': hp.quniform('w8', 0, 0.2, 0.005),
        'w9': hp.quniform('w9', 1, 10, 0.2),
        'w10': hp.quniform('w10', 3000, 12000, 200),
        'w11': hp.quniform('w11', 0, 0.35, 0.005),
    },
    'init_vals': {
        'w0': 10e+8,
        'w1': 1.13,  # Hệ số nhân của Sup_1Y
        'w2': 1.42,  # Hệ số nhân của Sup_1Y cho LO_3M_T1
        'w3': 1.25,  # Hệ số nhân của LO_3M_T1
        'w4': 8,  # Ngưỡng tối đa của PE
        'w5': 4.6,  # Ngưỡng tối đa của PB
        'w6': 30.2,  # Ngưỡng tối đa của PCF
        'w7': 0.6,  # Ngưỡng tối thiểu của PCF
        'w8': 0.015,  # Điều kiện tối thiểu cho Cash_P0 / (LtDebt_P0+1)
        'w9': 7.0,  # Ngưỡng cho IntCov_P0
        'w10': 8000,  # Điều kiện tối thiểu cho CF_OA_5Y / OShares
        'w11': 0.105,  # Ngưỡng tối thiểu của ROE_Min5Y
    },
    'filter_template': "((Volume_1M_P50*Price/Inflation_7)>{w0}) & (time>='2014-01-01') & (time<='2026-01-01')  "
                       "& (Close >{w1}* Sup_1Y) & (LO_3M_T1 < {w2}*Sup_1Y) &( Close < {w3}*LO_3M_T1)  "
                       "& (PE < {w4}) & (PB <{w5}) "
                       "& (PCF <{w6}) & (PCF >{w7})  "
                       "&  ((Cash_P0/ (LtDebt_P0+1) > {w8})|abs(IntCov_P0 > {w9})) "
                       "& ((CF_OA_5Y/OShares)> {w10}) "
                       "& (ROE_Min5Y > {w11}) "
                       "& (ICB_Code != 2353)",
}

conservative_config = {
    'pattern_name': 'Conservative',
    'utilize_percent': 1,
    'cutloss': 0.15,
    'search_space': {
        'w0': hp.quniform('w0', 3e+8, 30e+8, 2e+8),
        'w1': hp.quniform('w1', 0.03, 0.2, 0.005),
        'w2': hp.quniform('w2', 0.1, 0.3, 0.01),
        # ((Cash_P0/ (LtDebt_P0+1) > {w3}) | (abs(IntCov_P0) > {w4}))
        'w3': hp.quniform('w3', 0.02, 0.1, 0.002),
        'w4': hp.quniform('w4', 3.0, 10.0, 0.2),
        # (NP_P0 / NP_P1 > {w5})
        'w5': hp.quniform('w5', 1.0, 1.6, 0.02),
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
        'w0': 3e+8,
        'w1': 0.045,  # Tỷ lệ dòng tiền hoạt động và đầu tư trung bình trên vốn
        'w2': 0.11,  # Tỷ lệ dòng tiền trong 4 năm gần nhất trên vốn
        'w3': 0.098,  # Tỷ lệ tiền mặt trên nợ dài hạn
        'w4': 6,  # Độ bao phủ lãi suất tối thiểu
        'w5': 1.1,  # Tỷ lệ lợi nhuận hiện tại trên năm trước
        'w6': 1.2,  # PE tối thiểu
        'w7': 0.09,  # ROE trung bình 3 năm tối thiểu
        'w8': 21,  # PE tối đa
        'w9': 1.05,
    },
    'filter_template': "((Volume_1M_P50*Price/Inflation_7)>{w0}) & (time>='2014-01-01') & (time<='2026-01-01')  "
                       "&(((CF_OA_5Y + CF_Invest_5Y )/5)/(OShares*Price + LtDebt_P0) > {w1}) "
                       "& ((CF_OA_P0+CF_OA_P1+CF_OA_P2+CF_OA_P3 + CF_Invest_P0 + CF_Invest_P1+ CF_Invest_P2+CF_Invest_P3)"
                       "/(OShares*Price + LtDebt_P0)>{w2}) "
                       "& ((Cash_P0/ (LtDebt_P0+1) > {w3})|(abs(IntCov_P0) > {w4}))  "
                       "& (NP_P0 /NP_P1> {w5}) & (NP_P1>0) "
                       "& (PE >{w6}) & (PE < {w8}) "
                       "& (ROE_Min3Y > {w7}) "
                       "& (NP_P0/NP_P4 > {w9})",
}

surpriseearning_config = {
    'pattern_name': 'SurpriseEarning',
    'utilize_percent': 1,
    'cutloss': 0.15,
    'search_space': {
        'w0': hp.quniform('w0', 8e+8, 40e+8, 2e+8),
        'w1': hp.quniform('w1', 5, 20, 0.5),  # PE < w1
        'w2': hp.quniform('w2', 0.2, 3, 0.1),  # PB < w2
        'w3': hp.quniform('w3', 0.01, 0.2, 0.01),  # ROE_Min5Y > w3
        'w4': hp.quniform('w4', 0.1, 0.4, 0.02),  # (NP_P0 - NP_P4)/abs(NP_P4) > w4
        'w5': hp.quniform('w5', 1.1, 2, 0.05),  # NP_P0 / NP_P1 > w5
        'w7': hp.quniform('w7', 0, 7, 0.5),  # PCF > w7
        'w8': hp.quniform('w8', 15, 30, 1),  # PCF < w8
        'w9': hp.quniform('w9', 4000, 12000, 500),  # CF_OA_5Y / OShares > w9
        'w10': hp.quniform('w10', 0, 0.08, 0.005),  # Cash_P0 / (LtDebt_P0+1) > w10
        'w11': hp.quniform('w11', 1, 7, 0.5),  # abs(IntCov_P0) > w11
    },
    'init_vals': {
        'w0': 10e+8,
        'w1': 11.5,  # PE < 10
        'w2': 1.9,  # PB < 1
        'w3': 0.01,  # ROE_Min5Y > 0.05
        'w4': 0.18,  # (NP_P0 - NP_P4)/abs(NP_P4) > 0.22
        'w5': 1.4,  # NP_P0 / NP_P1 > 1.2
        'w7': 1.0,  # PCF > 0
        'w8': 16.0,  # PCF < 25
        'w9': 9500.0,  # CF_OA_5Y / OShares > 5000
        'w10': 0.04,  # Cash_P0 / (LtDebt_P0+1) > 0.01
        'w11': 1.0,  # abs(IntCov_P0) > 3
    },
    'filter_template': "((Volume_1M_P50*Price/Inflation_7)>{w0}) & (time>='2014-01-01') & (time<='2026-01-01')  "
                       "& (PE < {w1}) "
                       "& (PB < {w2}) "
                       "& (ROE_Min5Y > {w3}) "
                       "& ((NP_P0 - NP_P4)/abs(NP_P4) > {w4}) "
                       "& (NP_P0/NP_P1> {w5}) & (NP_P1 > 0) "
                       "& (PCF > {w7}) & (PCF < {w8}) "
                       "& (CF_OA_5Y/OShares > {w9}) "
                       "& ((Cash_P0/ (LtDebt_P0+1) >{w10})|(abs(IntCov_P0) > {w11}))",
}

supergrowth_config = {
    'pattern_name': 'SuperGrowth',
    'utilize_percent': 1,
    'cutloss': 0.15,
    'search_space': {
        'w0': hp.quniform('w0', 8e+8, 40e+8, 2e+8),
        # (PE/((NP_P0/NP_P4 -1)*100) < {w1})
        'w1': hp.quniform('w1', 0.5, 1.5, 0.01),
        # (ROE_Min5Y > {w2})
        'w2': hp.quniform('w2', 0.05, 0.2, 0.005),
        # (FSCORE >= {w3})
        'w3': scope.int(hp.quniform('w3', 1, 9, 1)),
        # (NP_P0/NP_P4 > {w4})
        'w4': hp.quniform('w4', 1, 2, 0.01),
        # (PCF > {w5})
        'w5': hp.quniform('w5', 0, 4, 0.1),
        # (PCF < {w6})
        'w6': hp.quniform('w6', 10, 30, 1),
        # (CF_OA_5Y/OShares > {w7})
        'w7': hp.quniform('w7', 3000, 12000, 500),
        'w8': hp.quniform('w8', 10, 66, 2),
    },
    'init_vals': {
        'w0': 10e+8,
        'w1': 0.93,  # PE/((NP_P0/NP_P4 -1)*100) < 1
        'w2': 0.035,  # ROE_Min5Y > 0.1
        'w3': 6,  # FSCORE >= 4
        'w4': 1.31,  # NP_P0/NP_P4 > 1.2
        'w5': 0.9,  # PCF > 0
        'w6': 14.0,  # PCF < 25
        'w7': 8000.0,  # CF_OA_5Y/OShares > 5000
        'w8': 10,
    },
    'filter_template': "((Volume_1M_P50*Price/Inflation_7)>{w0}) & (time>='2014-01-01') & (time<='2026-01-01')  "
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
        'w0': hp.quniform('w0', 8e+8, 40e+8, 2e+8),
        # (Close > {w1} * Volume_Max5Y_High)
        'w1': hp.quniform('w1', 0.98, 1.15, 0.01),
        # (ROE_Min5Y > {w2})
        'w2': hp.quniform('w2', 0.02, 0.1, 0.005),
        # (PE <= {w3})
        'w3': hp.quniform('w3', 5, 15, 0.2),
        # (NP_P0 > {w4} * NP_P1)
        'w4': hp.quniform('w4', 1, 1.6, 0.05),
        # (PE > {w5})
        'w5': hp.quniform('w5', 0, 5, 0.2),
        # (HI_3M_T1/LO_3M_T1 < {w6})
        'w6': hp.quniform('w6', 1.5, 3.0, 0.05),
    },
    'init_vals': {
        'w0': 10e+8,
        'w1': 1.0,  # Close > 1.05 * Volume_Max5Y_High
        'w2': 0.04,  # ROE_Min5Y > 0.05
        'w3': 10.2,  # PE <= 10
        'w4': 1.15,  # NP_P0 > 1.2 * NP_P1
        'w5': 2.4,  # PE > 0
        'w6': 2.2,  # HI_3M_T1/LO_3M_T1 < 1.95
    },
    'filter_template': "((Volume_1M_P50*Price/Inflation_7)>{w0}) & (time>='2014-01-01') & (time<='2026-01-01')  "
                       "& (Close> {w1}*Volume_Max5Y_High) "
                       "& (ROE_Min5Y > {w2})&(PE<={w3})"
                       "& (NP_P0 > {w4}*NP_P1) & (NP_P1 > NP_P2)"
                       "& (PE >{w5})"
                       "& (HI_3M_T1/LO_3M_T1<{w6})",
}

tl3m_config = {
    'pattern_name': 'TL3M',
    'utilize_percent': 1,
    'cutloss': 0.15,
    'search_space': {
        'w0': hp.quniform('w0', 8e+8, 40e+8, 2e+8),
        # (HI_3M_T1/LO_3M_T1 < {w1})
        'w1': hp.quniform('w1', 1.1, 1.5, 0.01),
        # (Volume > {w2} * Volume_3M_P90)
        'w2': hp.quniform('w2', 1.05, 1.4, 0.01),
        # (ROE5Y > {w3})
        'w3': hp.quniform('w3', 0.02, 0.2, 0.005),
        # (PE < {w4})
        'w4': hp.quniform('w4', 5, 25, 0.5),
        # (PB < {w5})
        'w5': hp.quniform('w5', 1.3, 3, 0.05),
        # (FSCORE > {w6})
        'w6': hp.quniform('w6', 1, 8, 1),
        # (NP_P0 > {w7} * NP_P1)
        'w7': hp.quniform('w7', 1.1, 1.4, 0.02),
        # (PCF > {w8})
        'w8': hp.quniform('w8', 0, 5, 0.2),
        # (PE > {w9})
        'w9': hp.quniform('w9', 0, 5, 0.2),
    },
    'init_vals': {
        'w0': 10e+8,
        'w1': 1.36,  # HI_3M_T1/LO_3M_T1 < 1.28
        'w2': 1.23,  # Volume > 1.16 * Volume_3M_P90
        'w3': 0.07,  # ROE5Y > 0.135
        'w4': 10,  # PE < 20
        'w5': 1.9,  # PB < 1.97
        'w6': 1.0,  # FSCORE > 4
        'w7': 1.2,  # NP_P0 > 1.16 * NP_P1
        'w8': 0.4,  # PCF > 0
        'w9': 3.0,  # PE > 0
    },
    'filter_template': "((Volume_1M_P50*Price/Inflation_7)>{w0}) & (time>='2014-01-01') & (time<='2026-01-01')  "
                       "& (HI_3M_T1/LO_3M_T1<{w1}) "
                       "& (Volume > {w2}*Volume_3M_P90)"
                       "& (ROE5Y>{w3}) "
                       "& (PE<{w4})  & (PE >{w9})"
                       "& (PB < {w5}) "
                       "& (FSCORE > {w6}) "
                       "& (NP_P0 > {w7}*NP_P1) & (NP_P1 > 0)"
                       "& (PCF>{w8})",
}

bkma200_config = {
    'pattern_name': 'BKMA200',
    'utilize_percent': 1,
    'cutloss': 0.15,
    'search_space': {
        'w0': hp.quniform('w0', 8e+8, 40e+8, 2e+8),
        # ((ID_LO_3Y - ID_HI_3Y) > {w1})
        'w1': hp.quniform('w1', 200, 350, 5),
        # (MA50/MA200 > {w2})
        'w2': hp.quniform('w2', 0.75, 1.0, 0.01),
        # (MA10/MA200 < {w3})
        'w3': hp.quniform('w3', 1.1, 1.6, 0.01),
        # (ROE5Y > {w4})
        'w4': hp.quniform('w4', 0.03, 0.2, 0.005),
        # (PE < {w5})
        'w5': hp.quniform('w5', 10, 30, 0.5),
        # (NP_P0 > {w6} * NP_P1)
        'w6': hp.quniform('w6', 1.0, 1.5, 0.02),
        # (HI_3M_T1 / LO_3M_T1 < {w7})
        'w7': hp.quniform('w7', 1.2, 2.7, 0.05),
        'w8': hp.quniform('w8', 0.0, 0.1, 0.005),

    },
    'init_vals': {
        'w0': 8e+8,
        'w1': 210,  # ID_LO_3Y - ID_HI_3Y > 293
        'w2': 0.96,  # MA50/MA200 > 0.86
        'w3': 1.53,  # MA10/MA200 < 1.37
        'w4': 0.07,  # ROE5Y > 0.09
        'w5': 14.5,  # PE < 20
        'w6': 1.14,  # NP_P0 > 1.2 * NP_P1
        'w7': 1.9,  # HI_3M_T1 / LO_3M_T1 < 1.958
        'w8': 0.065,  # ROE_Min3Y > 0.05
    },
    'filter_template': "((Volume_1M_P50*Price/Inflation_7)>{w0}) & (time>='2014-01-01') & (time<='2026-01-01')  "
                       "& ((ID_LO_3Y-ID_HI_3Y)>{w1}) "
                       "& (MA50/MA200>{w2}) & (MA10/MA200<{w3}) "
                       "& (ROE5Y >{w4}) "
                       "& (PE <{w5}) "
                       "& (NP_P0 > {w6}*NP_P1) & (NP_P1 > 0) "
                       "& (HI_3M_T1/LO_3M_T1<{w7}) "
                       "& (ROE_Min3Y >{w8})",
}

underbv_config = {
    'pattern_name': 'UnderBV',
    'utilize_percent': 1,
    'cutloss': 0.15,
    'search_space': {
        'w0': hp.quniform('w0', 8e+8, 40e+8, 2e+8),
        'w1': hp.quniform('w1', 0.5, 1.2, 0.02),
        # (FSCORE >= {w2})
        'w2': hp.quniform('w2', 1, 8, 1),
        # (NP_P0 > {w3} * NP_P1)
        'w3': hp.quniform('w3', 0.85, 1.5, 0.02),
        # (PCF > {w4})
        'w4': hp.quniform('w4', 0.6, 4, 0.2),
        # (PE > {w5})
        'w5': hp.quniform('w5', 0, 7, 0.2),
        # (PCF < {w6})
        'w6': hp.quniform('w6', 15, 30, 1),
        # ((NP_P0 + NP_P1 + NP_P2 + NP_P3) / OShares > {w7})
        'w7': hp.quniform('w7', 500, 2500, 100),
        # (NP_P0 / NP_P4 > {w8})
        'w8': hp.quniform('w8', 1, 1.6, 0.05),
    },
    'init_vals': {
        'w0': 10e+8,
        'w1': 1.2,  # PB < 0.9
        'w2': 1.0,  # FSCORE >= 4
        'w3': 1.32,  # NP_P0 > 0.90 * NP_P1
        'w4': 1.0,  # PCF > 2
        'w5': 0,  # PE > 0
        'w6': 23.0,  # PCF < 25
        'w7': 1750.0,  # (NP_P0 + NP_P1 + NP_P2 + NP_P3) / OShares > 500
        'w8': 1.15,  # NP_P0 / NP_P4 > 1.15
    },
    'filter_template': "((Volume_1M_P50*Price/Inflation_7)>{w0}) & (time>='2014-01-01') & (time<='2026-01-01') "
                       "& (PB < {w1}) "
                       "& (FSCORE >= {w2}) "
                       "& (NP_P0 > {w3}*NP_P1)  "
                       "& (PCF>{w4})  & (PCF<{w6})"
                       "& (PE >{w5})  "
                       "& ((NP_P0+NP_P1+NP_P2+NP_P3)/OShares > {w7}) & (NP_P0/NP_P4 > {w8})",
}

rsilow30_config = {
    'pattern_name': 'RSILow30',
    'utilize_percent': 1,
    'cutloss': 0.15,
    'search_space': {
        'w0': hp.quniform('w0', 8e+8, 40e+8, 2e+8),
        # (D_RSI < {w1})
        'w1': hp.quniform('w1', 0.1, 0.3, 0.01),
        # (PE < {w2})
        'w2': hp.quniform('w2', 5, 15, 0.2),
        # (PE > {w3})
        'w3': hp.quniform('w3', 0, 5, 0.2),
        # (ROE_Min3Y > {w4})
        'w4': hp.quniform('w4', 0.01, 0.12, 0.005),
        # (PB < {w5}*PB_MA5Y - {w6}*PB_SD5Y)
        'w5': hp.quniform('w5', 0.5, 1.2, 0.05),
        'w6': hp.quniform('w6', 0.3, 1.2, 0.05),
        # (PCF > {w7})
        'w7': hp.quniform('w7', 0, 5, 0.2),
        # (PCF < {w8})
        'w8': hp.quniform('w8', 15, 40, 1),
        # ((Cash_P0/ (LtDebt_P0+1) > {w9}) | (abs(IntCov_P0) > {w10}))
        'w9': hp.quniform('w9', 0.05, 0.1, 0.005),
        # Giá trị tham chiếu: w10 = 3, tìm trong khoảng [1, 6]
        'w10': hp.quniform('w10', 1, 6, 0.2),
    },
    'init_vals': {
        'w0': 10e+8,
        'w1': 0.3,  # D_RSI < 0.3
        'w2': 7.4,  # PE < 9
        'w3': 3.8,  # PE > 0
        'w4': 0.05,  # ROE_Min3Y > 0.035
        'w5': 0.85,  # PB_MA5Y coefficient
        'w6': 0.55,  # PB_SD5Y coefficient
        'w7': 2.4,  # PCF > 0
        'w8': 27.0,  # PCF < 25
        'w9': 0.06,  # Cash_P0 / (LtDebt_P0 + 1) > 0.02
        'w10': 3.4,  # abs(IntCov_P0) > 3
    },
    'filter_template': "((Volume_1M_P50*Price/Inflation_7)>{w0}) & (time>='2014-01-01') & (time<='2026-01-01')  "
                       "& (D_RSI < {w1})  "
                       "& (PE < {w2})  & (PE>{w3}) "
                       "& (ROE_Min3Y > {w4}) "
                       "& (PB < {w5}*PB_MA5Y - {w6}*PB_SD5Y) "
                       "& (PCF > {w7}) & (PCF <{w8}) "
                       "& ((Cash_P0/ (LtDebt_P0+1) > {w9})|(abs(IntCov_P0) > {w10})) "
                       "& (NP_P0 > 0)",
}

volmax1y_config = {
    'pattern_name': 'VolMax1Y',
    'utilize_percent': 1,
    'cutloss': 0.15,
    'search_space': {
        'w0': hp.quniform('w0', 8e+8, 40e+8, 2e+8),
        'w1': hp.quniform('w1', 1.0, 1.2, 0.01),
        # (Close_T1W < {w2}*Volume_Max1Y_High)
        'w2': hp.quniform('w2', 0.8, 1.3, 0.01),
        # (Volume > {w3}*Volume_3M_P50)
        'w3': hp.quniform('w3', 0.8, 1.2, 0.05),
        # (PE > {w4})
        'w4': hp.quniform('w4', 0, 4, 0.2),
        # (PE < {w5})
        'w5': hp.quniform('w5', 7, 20, 0.2),
        # (PB < {w6})
        'w6': hp.quniform('w6', 2, 6, 0.1),
        # (PCF > {w7})
        'w7': hp.quniform('w7', 0, 5, 0.2),
        # (NP_P0 > {w8}*NP_P1)
        'w8': hp.quniform('w8', 1.0, 1.5, 0.05),
        # (PCF < {w9})
        'w9': hp.quniform('w9', 12, 25, 0.2),
        # (ROE_Min3Y > {w10})
        'w10': hp.quniform('w10', 0.01, 0.05, 0.005),
        # ((NP_P0 - NP_P4)/abs(NP_P4) > {w11})
        'w11': hp.quniform('w11', 0.1, 1.5, 0.1),
        # (PCF < {w12})
        'w12': hp.quniform('w12', 10, 20, 0.2),
        # (ID_Current - Volume_Max1Y_ID <= {w13})
        'w13': hp.quniform('w13', 100, 220, 5),
        # (Volume_Max1Y_High / LO_3M_T1 < {w14})
        'w14': hp.quniform('w14', 1.1, 1.8, 0.05),
        # (FSCORE > {w15})
        'w15': hp.quniform('w15', 1, 8, 1),
    },
    'init_vals': {
        'w0': 10e+8,
        'w1': 1.01,  # Close > 1.02 * Volume_Max1Y_High
        'w2': 1.08,  # Close_T1W < Volume_Max1Y_High
        'w3': 0.85,  # Volume > Volume_3M_P50
        'w4': 1.0,  # PE > 0
        'w5': 10.8,  # PE < 16
        'w6': 4.0,  # PB < 3.5
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
    'filter_template': "((Volume_1M_P50*Price/Inflation_7)>{w0}) & (time>='2014-01-01') & (time<='2026-01-01')  "
                       "& (Close > {w1}*Volume_Max1Y_High) & (Close_T1W < {w2}*Volume_Max1Y_High) "
                       "& (Volume > {w3}*Volume_3M_P50) "
                       "& (PE >{w4}) & (PE < {w5}) "
                       "& (PB<{w6}) "
                       "& (((NP_P0 > {w8}*NP_P1)& (PCF < {w9}) "
                       "& (ROE_Min3Y > {w10})) | ((((NP_P0 - NP_P4)/abs(NP_P4) > {w11})) "
                       "& (PCF < {w12}))) & (PCF > {w7}) "
                       "& (ID_Current-Volume_Max1Y_ID<={w13})  "
                       "& (Volume_Max1Y_High/LO_3M_T1 < {w14}) "
                       "& (FSCORE > {w15})",
}

t3p4_config = {
    'pattern_name': 'T3P4',
    'utilize_percent': 1,
    'cutloss': 0.15,
    'search_space': {
        'w0': hp.quniform('w0', 8e+8, 40e+8, 2e+8),

        # W_CMB (Weekly Combine Momentum)
        'w1': hp.quniform('w1', 0, 0.1, 0.005),  # Step
        'w2': hp.quniform('w2', 1, 5, 1),  # LEN
        'w3': hp.quniform('w3', 0, 3, 1),  # LAG lower
        'w4': hp.quniform('w4', 3, 7, 1),  # LAG upper

        # M_CMB (Monthly Combine Momentum)
        'w5': hp.quniform('w5', 0, 0.1, 0.005),  # Step
        'w6': hp.quniform('w6', 1, 6, 1),  # LEN
        'w7': hp.quniform('w7', 0, 2, 1),  # LAG lower
        'w8': hp.quniform('w8', 2, 6, 1),  # LAG upper

        # ROE 5Y
        'w9': hp.quniform('w9', 0.04, 0.1, 0.01),  # Lower
        'w10': hp.quniform('w10', 0.1, 0.2, 0.01),  # Upper

        # NP_P0 / NP_P4 ratio
        'w11': hp.quniform('w11', 1.0, 1.3, 0.05),

        # PE
        'w12': hp.quniform('w12', 7, 12, 0.2),

        # C_H2Y range
        'w13': hp.quniform('w13', 0.2, 0.7, 0.05),  # Lower bound
        'w14': hp.quniform('w14', 0.7, 0.9, 0.02),  # Upper bound
        'w15': hp.quniform('w15', 0, 0.05, 0.005),

    },
    'init_vals': {
        'w0': 10e+8,
        'w1': 0.025,  # W_CMB_Step > 0.025
        'w2': 2,  # W_CMB_LEN >= 2
        'w3': 0,  # W_CMB_LAG > 0
        'w4': 3,  # W_CMB_LAG <= 3

        'w5': 0.025,  # M_CMB_Step > 0.025
        'w6': 2,  # M_CMB_LEN >= 2
        'w7': 1,  # M_CMB_LAG >= 1
        'w8': 4,  # M_CMB_LAG <= 4

        'w9': 0.13,  # ROE5Y >= 0.13
        'w10': 0.2,  # ROE5Y <= 0.2

        'w11': 1.17,  # NP_P0 > 1.17 * NP_P4
        'w12': 10,  # PE < 10

        'w13': 0.3,  # C_H2Y > 0.3
        'w14': 0.84,  # C_H2Y < 0.84
        'w15': 0.01,  # ROE_Min5Y > 3
    },
    'filter_template': "((Volume_1M_P50*Price/Inflation_7)>{w0}) & (time>='2014-01-01') & (time<='2026-01-01') "
                       "& ((((W_CMB_Step>{w1}) & (W_CMB_LEN>={w2}) & (W_CMB_LAG>{w3})& (W_CMB_LAG<={w4})) "
                       "| ((M_CMB_Step>{w5}) & (M_CMB_LEN>={w6}) & (M_CMB_LAG >{w7}) & (M_CMB_LAG <={w8})))) "
                       "& (ROE5Y>={w9}) & (ROE5Y<={w10})"
                       "& (NP_P0>{w11}*NP_P4) & (NP_P4 > 0) "
                       "& (PE<{w12}) "
                       "& (C_H2Y>{w13}) & (C_H2Y<{w14}) "
                       "& (ROE_Min5Y > {w15})",
}

dy_config = {
    'pattern_name': 'DividendYield',
    'utilize_percent': 1,
    'cutloss': 0.2,
    'search_space': {
        'w0': hp.quniform('w0', 8e+8, 40e+8, 2e+8),
        'w1': hp.quniform('w1', 0, 10, 0.5),  # PCF lower
        'w2': hp.quniform('w2', 10, 40, 1),  # PCF upper
        'w3': hp.quniform('w3', 0.9, 1.5, 0.02),  # NP_P0/NP_P1 > w3
        'w4': hp.quniform('w4', 0, 10, 0.5),  # PE > w4
        'w5': hp.quniform('w5', 11, 25, 0.5),  # PE < w5
        'w6': hp.quniform('w6', 3000, 10000, 200),  # CF_OA_5Y / OShares > w6
        'w7': hp.quniform('w7', 0.02, 0.12, 0.005),  # abs(Dividend_Min3Y / Price)

    },
    'init_vals': {
        'w0': 10e+8,
        'w1': 0,  # PCF > 0
        'w2': 30,  # PCF < 30
        'w3': 1,  # NP_P0/NP_P1 < 1
        'w4': 0,  # PE > 0
        'w5': 18,  # PE < 18
        'w6': 5000,  # CF_OA_5Y / OShares > 5000
        'w7': 0.05,  # abs(Dividend_Min3Y / Price) > 0.04
    },
    'filter_template': "((Volume_1M_P50*Price/Inflation_7>{w0}) & (time>='2014-01-01') & (time<='2026-01-01')) "
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
        # (Volume_1M_P50 * Price / Inflation_7) > w0
        'w0': hp.quniform('w0', 8e+8, 40e+8, 2e+8),

        # (CF_OA_P0+...+CF_Invest_P3)/(OShares*Price + LtDebt_P0) > w1
        'w1': hp.quniform('w1', 0.05, 0.2, 0.005),

        # (Cash_P0 + LtInvest_P0 + AR_P0 + Inventory_P0 - StLiab_P0 - LtLiab_P0)/(OShares*Price) > w2
        'w2': hp.quniform('w2', 0.1, 0.3, 0.01),

        # abs(IntCov_P0) > w3
        'w3': hp.quniform('w3', 1, 5, 0.5),

        # PE lower bound
        'w4': hp.quniform('w4', 1.2, 10, 0.2),

        # PE upper bound
        'w5': hp.quniform('w5', 10, 25, 0.5),

        # Volume/Volume_1M > w6
        'w6': hp.quniform('w6', 1.1, 2, 0.05),

        # DY > w7
        'w7': hp.quniform('w7', 0.015, 0.05, 0.002),
    },

    'init_vals': {
        'w0': 10e+8,
        'w1': 0.1,
        'w2': 0.2,
        'w3': 3.0,
        'w4': 1.2,
        'w5': 20,
        'w6': 1.2,
        'w7': 0.02,
    },
    'filter_template': "((Volume_3M_P50*Price/Inflation_7)>{w0}) & (time>='2014-01-01') & (time<='2026-01-01') "
                       "& ((CF_OA_P0+CF_OA_P1+CF_OA_P2+CF_OA_P3 + CF_Invest_P0 + CF_Invest_P1+ CF_Invest_P2+CF_Invest_P3)/(OShares*Price + LtDebt_P0) > {w1}) "
                       "& ((Cash_P0  + LtInvest_P0 + AR_P0 + Inventory_P0 - StLiab_P0  -  LtDebt_P0 )/(OShares*Price) > {w2}) "
                       "& (abs(IntCov_P0) > {w3}) "
                       "& (NP_P0 > 0) & (NP_P1 > 0) "
                       "& (PE > {w4}) & (PE < {w5}) "
                       "& (Trading_Value /Trading_Value_1M_P50 > {w6}) "
                       "& (DY > {w7})",
}

vnindexbulldvg_config = {
    'pattern_name': 'VNINDEX_BullDvg',
    'utilize_percent': 1,
    'cutloss': 1,
    'search_space': {
        'w0': hp.quniform('w0', 0.9, 1.2, 0.02),  # D_RSI_Min1W / D_RSI_Min3M > w0
        'w1': hp.quniform('w1', 0.2, 0.6, 0.02),  # D_RSI_Min1W < w1
        'w2': hp.quniform('w2', 0.1, 0.4, 0.02),  # D_RSI_Min3M < w2
        'w3': hp.quniform('w3', 1.0, 1.17, 0.01),  # D_RSI_Min1W_Close/D_RSI_Min3M_Close < w3
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
    'filter_template': "(time>='2000-01-01') & (time<='2026-01-01') & (ticker=='VNINDEX') "
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

    # pattern_configs = [bkma200_config, bulldvg_config, buysupport_config, conservative_config, dy_config,
    #                    rsilow30_config, supergrowth_config, surpriseearning_config, t3p4_config, tl3m_config,
    #                    trendinggrowth_config, underbv_config, volmax1y_config]
    pattern_configs = [vnindexbulldvg_config]

    results = run_multiple_patterns(pattern_configs, sell_config, max_evals=2000)
    print(f"Results for all patterns: {results}")
