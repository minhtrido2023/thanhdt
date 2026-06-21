import os
import sys
import pickle
import json
import pandas as pd
from typing import Dict, List, Any
import glob
import run_tuning

# Đường dẫn và biến toàn cục
current_dir = os.path.dirname(os.path.abspath(__file__))
current_dir = current_dir.replace("/tuning/buy_pattern", "")
os.chdir(current_dir)
sys.path.insert(0, current_dir)

# Định nghĩa các pattern và path tương ứng
PATH = "tuning/parallel/final_result/buy"
RESULT_PATH = "tuning/results"
INIT_ASSETS = 50.0
INIT_SLOTS = 10
SI_TYPE = "Cash allocation"

KEY_MAPPING = {
    f'w_{k.lower()[1:]}': k[1:] for k in run_tuning.sell_patterns.keys()
}

INIT_FILTER = {
    "Init": run_tuning.Init,
    **run_tuning.sell_patterns,
    **run_tuning.s_sell_patterns,
}

PATTERN_CONFIGS = {
    'BullDvg': {
        'checkpoint_path': f'{PATH}/trials_BullDvg.pkl',
        'log_path': f'{PATH}/trials_BullDvg.csv',
        'pattern_template': run_tuning.bulldvg_config.get('filter_template').replace(f"{run_tuning.Init}&", "")
        # 'pattern_template': "((Volume_1M_P50*Price/Inflation_7)>{w0}) & (D_RSI / D_RSI_T1 > {w1}) & (D_RSI > {w2}) & (D_RSI < {w3}) & (D_RSI_Min3M < {w4}) & (D_RSI_Min1W > {w5}) & (D_RSI_Min1W/D_RSI_Min3M > {w6}) & (D_RSI_Min1W_Close/D_RSI_Min3M_Close < {w7}) & (FSCORE > {w8}) & (PE< {w9}) & (PE>{w10}) & (PB < {w11}) & (ROE_Min5Y > {w12}) & (PCF <{w13}) & (PCF>{w14}) & ((Cash_P0/ (LtDebt_P0+1) > {w15})|(abs(IntCov_P0) > {w16})) & ((CF_OA_5Y/OShares)> {w17}) & (NP_P0/NP_P4 >={w18})"
    },
    'BuySupport': {
        'checkpoint_path': f'{PATH}/trials_BuySupport.pkl',
        'log_path': f'{PATH}/trials_BuySupport.csv',
        'pattern_template': run_tuning.buysupport_config.get('filter_template').replace(f"{run_tuning.Init}&", "")
        # 'pattern_template': "((Volume_1M_P50*Price/Inflation_7)>{w0}) & (Close >{w1}* Sup_1Y) & (LO_3M_T1 < {w2}*Sup_1Y) &( Close < {w3}*LO_3M_T1)  & (PE < {w4}) & (PB <{w5}) & (PCF <{w6}) & (PCF >{w7})  &  ((Cash_P0/ (LtDebt_P0+1) > {w8})|abs(IntCov_P0 > {w9})) & ((CF_OA_5Y/OShares)> {w10}) & (ROE_Min5Y > {w11}) & (ICB_Code != 2353)"
    },
    'Conservative': {
        'checkpoint_path': f'{PATH}/trials_Conservative.pkl',
        'log_path': f'{PATH}/trials_Conservative.csv',
        'pattern_template': run_tuning.conservative_config.get('filter_template').replace(f"{run_tuning.Init}&", "")
        # 'pattern_template': "((Volume_1M_P50*Price/Inflation_7)>{w0}) & (((CF_OA_5Y + CF_Invest_5Y )/5)/(OShares*Price + LtDebt_P0) > {w1}) & ((CF_OA_P0+CF_OA_P1+CF_OA_P2+CF_OA_P3 + CF_Invest_P0 + CF_Invest_P1+ CF_Invest_P2+CF_Invest_P3)/(OShares*Price + LtDebt_P0)>{w2}) & ((Cash_P0/ (LtDebt_P0+1) > {w3})|(abs(IntCov_P0) > {w4}))  & (NP_P0 /NP_P1> {w5}) & (NP_P1>0) & (PE >{w6}) & (ROE_Min3Y > {w7}) & (PE < {w8}) & (NP_P0/NP_P4 > {w9})"
    },
    'SurpriseEarning': {
        'checkpoint_path': f'{PATH}/trials_SurpriseEarning.pkl',
        'log_path': f'{PATH}/trials_SurpriseEarning.csv',
        'pattern_template': run_tuning.surpriseearning_config.get('filter_template').replace(f"{run_tuning.Init}&", "")
        # 'pattern_template': "((Volume_1M_P50*Price/Inflation_7)>{w0}) & (PE < {w1}) & (PB < {w2}) & (ROE_Min5Y > {w3}) & ((NP_P0 - NP_P4)/abs(NP_P4) > {w4}) & (NP_P0/NP_P1> {w5}) & (NP_P1 > 0) & (PCF > {w7}) & (PCF < {w8}) & (CF_OA_5Y/OShares > {w9}) & ((Cash_P0/ (LtDebt_P0+1) >{w10})|(abs(IntCov_P0) > {w11}))"
    },
    'SuperGrowth': {
        'checkpoint_path': f'{PATH}/trials_SuperGrowth.pkl',
        'log_path': f'{PATH}/trials_SuperGrowth.csv',
        'pattern_template': run_tuning.supergrowth_config.get('filter_template').replace(f"{run_tuning.Init}&", "")
        # 'pattern_template': "((Volume_1M_P50*Price/Inflation_7)>{w0}) & (PE/((NP_P0/NP_P4 -1)*100) < {w1}) & (ROE_Min5Y > {w2}) &  ((FSCORE>={w3})) & (NP_P0/NP_P4 > {w4})  & (NP_P4 >= 0)  & (PCF > {w5}) & (PCF < {w6}) & (CF_OA_5Y/OShares > {w7}) & (ID_Current -  ID_Release <= 10)"
    },
    'TrendingGrowth': {
        'checkpoint_path': f'{PATH}/trials_TrendingGrowth.pkl',
        'log_path': f'{PATH}/trials_TrendingGrowth.csv',
        'pattern_template': run_tuning.trendinggrowth_config.get('filter_template').replace(f"{run_tuning.Init}&", "")
        # 'pattern_template': "((Volume_1M_P50*Price/Inflation_7)>{w0}) & (Close> {w1}*Volume_Max5Y_High) & (ROE_Min5Y > {w2})&(PE<={w3})& (NP_P0 > {w4}*NP_P1) & (NP_P1 > NP_P2) & (PE >{w5})& (HI_3M_T1/LO_3M_T1<{w6})"
    },
    'TL3M': {
        'checkpoint_path': f'{PATH}/trials_TL3M.pkl',
        'log_path': f'{PATH}/trials_TL3M.csv',
        'pattern_template': run_tuning.tl3m_config.get('filter_template').replace(f"{run_tuning.Init}&", "")
        # 'pattern_template': "((Volume_1M_P50*Price/Inflation_7)>{w0}) & (HI_3M_T1/LO_3M_T1<{w1}) & (Volume > {w2}*Volume_3M_P90)& (ROE5Y>{w3}) & (PE<{w4}) & (PB < {w5}) & (FSCORE > {w6}) & (NP_P0 > {w7}*NP_P1) & (PCF>{w8}) & (NP_P1 > 0) & (PE >{w9})"
    },
    'BKMA200': {
        'checkpoint_path': f'{PATH}/trials_BKMA200.pkl',
        'log_path': f'{PATH}/trials_BKMA200.csv',
        'pattern_template': run_tuning.bkma200_config.get('filter_template').replace(f"{run_tuning.Init}&", "")
        # 'pattern_template': "((Volume_1M_P50*Price/Inflation_7)>{w0}) & ((ID_LO_3Y-ID_HI_3Y)>{w1}) & (MA50/MA200>{w2}) & (MA10/MA200<{w3}) & (ROE5Y >{w4}) & (PE <{w5}) & (NP_P0 > {w6}*NP_P1) & (NP_P1 > 0) & (HI_3M_T1/LO_3M_T1<{w7}) & (ROE_Min3Y >{w8})"
    },
    'UnderBV': {
        'checkpoint_path': f'{PATH}/trials_UnderBV.pkl',
        'log_path': f'{PATH}/trials_UnderBV.csv',
        'pattern_template': run_tuning.underbv_config.get('filter_template').replace(f"{run_tuning.Init}&", "")
        # 'pattern_template': "((Volume_1M_P50*Price/Inflation_7)>{w0}) & (PB < {w1}) & (FSCORE >= {w2}) & (NP_P0 > {w3}*NP_P1)  & (PCF>{w4})  & (PE >{w5})  & (PCF < {w6})  & ((NP_P0+NP_P1+NP_P2+NP_P3)/OShares > {w7}) & (NP_P0/NP_P4 > {w8})"
    },
    'RSILow30': {
        'checkpoint_path': f'{PATH}/trials_RSILow30.pkl',
        'log_path': f'{PATH}/trials_RSILow30.csv',
        'pattern_template': run_tuning.rsilow30_config.get('filter_template').replace(f"{run_tuning.Init}&", "")
        # 'pattern_template': "((Volume_1M_P50*Price/Inflation_7)>{w0}) & (D_RSI < {w1})  & (PE < {w2})  & (PE>{w3}) & (ROE_Min3Y > {w4}) & (PB < {w5}*PB_MA5Y - {w6}*PB_SD5Y) & (PCF > {w7}) & (PCF <{w8}) & ((Cash_P0/ (LtDebt_P0+1) > {w9})|(abs(IntCov_P0) > {w10})) & (NP_P0 > 0)"
    },
    'VolMax1Y': {
        'checkpoint_path': f'{PATH}/trials_VolMax1Y.pkl',
        'log_path': f'{PATH}/trials_VolMax1Y.csv',
        'pattern_template': run_tuning.volmax1y_config.get('filter_template').replace(f"{run_tuning.Init}&", "")
        # 'pattern_template': "((Volume_1M_P50*Price/Inflation_7)>{w0}) & (Close > {w1}*Volume_Max1Y_High) & (Close_T1W < {w2}*Volume_Max1Y_High) & (Volume > {w3}*Volume_3M_P50) & (PE >{w4}) & (PE < {w5}) & (PB<{w6}) & (PCF > {w7}) & (((NP_P0 > {w8}*NP_P1)& (PCF < {w9}) & (ROE_Min3Y > {w10})) | ((((NP_P0 - NP_P4)/abs(NP_P4) > {w11})) & (PCF < {w12})))  & (ID_Current-Volume_Max1Y_ID<={w13})  & (Volume_Max1Y_High/LO_3M_T1 < {w14}) & (FSCORE > {w15})"
    },
    'T3P4': {
        'checkpoint_path': f'{PATH}/trials_T3P4.pkl',
        'log_path': f'{PATH}/trials_T3P4.csv',
        'pattern_template': run_tuning.t3p4_config.get('filter_template').replace(f"{run_tuning.Init}&", "")
        # 'pattern_template': "((Volume_1M_P50*Price/Inflation_7)>{w0}) & ((((W_CMB_Step>{w1}) & (W_CMB_LEN>={w2}) & (W_CMB_LAG>{w3})& (W_CMB_LAG<={w4})) | ((M_CMB_Step>{w5}) & (M_CMB_LEN>={w6}) & (M_CMB_LAG >{w7}) & (M_CMB_LAG <={w8})))) & (ROE5Y>={w9})&(ROE5Y<={w10})& (NP_P0>{w11}*NP_P4) & (NP_P4>0) & (PE<{w12})&(C_H2Y>{w13}) & (C_H2Y<{w14}) & (ROE_Min5Y > {w15})"
    },
    'DividendYield': {
        'checkpoint_path': f'{PATH}/trials_DividendYield.pkl',
        'log_path': f'{PATH}/trials_DividendYield.csv',
        'pattern_template': run_tuning.dy_config.get('filter_template').replace(f"{run_tuning.Init}&", "")
        # 'pattern_template': "(Volume_1M_P50*Price/Inflation_7>{w0}) & (PCF>{w1}) & (PCF < {w2}) & (NP_P0 > 0) & (NP_P0/NP_P1>{w3}) & (PE>{w4}) & (PE < {w5}) & ((CF_OA_5Y/OShares)> {w6}) & (abs(Dividend_Min3Y)/Price >{w7})"
    },
    'CashCowStock': {
        'checkpoint_path': f'{PATH}/trials_CashCowStock.pkl',
        'log_path': f'{PATH}/trials_CashCowStock.csv',
        'pattern_template': run_tuning.strongcashstock_config.get('filter_template').replace(f"{run_tuning.Init}&", "")
        # 'pattern_template': "((Volume_3M_P50*Price/Inflation_7)>{w0})"
        #                     "& ((CF_OA_P0+CF_OA_P1+CF_OA_P2+CF_OA_P3 + CF_Invest_P0 + CF_Invest_P1+ CF_Invest_P2+CF_Invest_P3)/(OShares*Price + LtDebt_P0) > {w1}) "
        #                     "& ((Cash_P0  + LtInvest_P0 + AR_P0 + Inventory_P0 - StLiab_P0  -  LtDebt_P0 )/(OShares*Price) > {w2}) "
        #                     "& (abs(IntCov_P0) > {w3}) "
        #                     "& (NP_P0 > 0) & (NP_P1 > 0) "
        #                     "& (PE > {w4}) & (PE < {w5}) "
        #                     "& (Trading_Value /Trading_Value_1M_P50 > {w6}) "
        #                     "& (DY > {w7})"
    },
    'TradingValueMax': {
        'checkpoint_path': f'{PATH}/trials_TradingValueMax.pkl',
        'log_path': f'{PATH}/trials_TradingValueMax.csv',
        'pattern_template': run_tuning.tradingvaluemax_config.get('filter_template').replace(f"{run_tuning.Init}&", "")
        # 'pattern_template': "((Volume_3M_P50*Price/Inflation_7) > {w0})"
        #                     "& (Trading_Value_Total_1W >= {w5} * Trading_Value_Total_1W_Max6M) "
        #                     "& (Volume >= {w6} * Volume_Max1Y) "
        #                     "& (PE > 0) "
        #                     "& (PB < {w1}) "
        #                     "& (Close < {w2} * Close_2Y_P90) "
        #                     "& (D_RSI < {w3}) "
        #                     "& (FSCORE > {w4})"
    },
    'AccSup': {
        'checkpoint_path': f'{PATH}/trials_AccSup.pkl',
        'log_path': f'{PATH}/trials_AccSup.csv',
        'pattern_template': run_tuning.accsup_config.get('filter_template').replace(f"{run_tuning.Init}&", "")
    },
}


# def parse_hyperopt_results(pattern_name: str, top_n: int = 30) -> List[Dict[str, Any]]:
#     if pattern_name not in PATTERN_CONFIGS:
#         raise ValueError(f"Pattern {pattern_name} không tồn tại trong cấu hình")
#
#     config = PATTERN_CONFIGS[pattern_name]
#     checkpoint_path = config['checkpoint_path']
#     pattern_template = config['pattern_template']
#
#     if not os.path.exists(checkpoint_path):
#         raise FileNotFoundError(f"Không tìm thấy file checkpoint tại {checkpoint_path}")
#
#     # Đọc trials từ file pickle
#     trials = pickle.load(open(checkpoint_path, "rb"))
#
#     # Lấy các trial có loss tốt nhất
#     sorted_trials = sorted(trials.trials, key=lambda x: x['result']['loss'])[:top_n]
#
#     results = []
#     for i, trial in enumerate(sorted_trials):
#         # Lấy các tham số từ trial
#         params = {k: v[0] for k, v in trial['misc']['vals'].items()}
#
#         # Tạo pattern string từ template và params
#         pattern = pattern_template.format(**params)
#
#         result = {
#             'rank': i + 1,
#             'iteration': trial['tid'],
#             'loss': trial['result']['loss'],
#             'params': params,
#             'pattern': pattern,
#             'pattern_name': pattern_name
#         }
#
#         # Thêm các metrics khác nếu có
#         if 'metrics' in trial['result']:
#             result.update(trial['result']['metrics'])
#
#         results.append(result)
#
#     return results


def parse_logging_results(pattern_name: str, log_path: str, top_n: int = 50) -> List[Dict[str, Any]]:
    if pattern_name not in PATTERN_CONFIGS:
        raise ValueError(f"Pattern {pattern_name} không tồn tại trong cấu hình")

    config = PATTERN_CONFIGS[pattern_name]
    # log_path = config['log_path']
    pattern_template = config['pattern_template']

    if not os.path.exists(log_path):
        raise FileNotFoundError(f"Không tìm thấy file log tại {log_path}")

    data = pd.read_csv(log_path)
    data = data[data['loss'] != float('inf')]

    # Tính toán ranking
    data['ranking'] = 0.4 * data['si_return'] + \
                      0.3 * data['win_deal'] + \
                      0.15 * data['win_quarter'] + \
                      0.1 * data['winblock_20quarters'] + \
                      0.05 * data['winblock_24months']
    # 0.1 * data['deal'] / data['deal'].max() * 100

    top_data = data.nlargest(top_n, 'loss').copy()
    # Tạo cột filter
    top_data['filter'] = top_data.apply(lambda row: pattern_template.format(**row.to_dict()), axis=1)
    # top_data['filter'] = top_data['pattern_formula']

    # top_data.sort_values(by='ranking', ascending=False, inplace=True)

    results = top_data.to_dict('records')

    # Thêm thông tin về pattern_name và rank
    for i, result in enumerate(results):
        result['pattern_name'] = pattern_name
        result['rank'] = i + 1

    return results


# def save_results_to_config_pattern(results: List[Dict[str, Any]], pattern_name: str):
#     filters = INIT_FILTER.copy()
#
#     map = ""
#     for result in results:
#         for key, value in result['params'].items():
#             if key.startswith('w_') and value > 0:
#                 map += f"{KEY_MAPPING[key]}, "
#
#         filters[f'$Buy{result["iteration"]}'] = map[:-2]
#         filters[f'_Buy{result["iteration"]}'] = "{Init} & " + result['pattern']
#
#     new_filter = {
#         "filter": json.dumps(filters),
#         "weight": '{}',
#         "params": {
#             'cutloss': 15,
#             'si_type': SI_TYPE,
#             'si_slot': INIT_SLOTS,
#             'si_asset': INIT_ASSETS,
#             'w_lookback': 10,
#             'w_thres_buy': 1.0,
#             'w_thres_sell': -1.0,
#             'w_k_exp': 0.0,
#             'co_rank': "ranking_point",
#
#         },
#         "combine": {}
#
#     }
#
#     output_path = f'{RESULT_PATH}/config_results.json'
#     os.makedirs(os.path.dirname(output_path), exist_ok=True)
#
#     if os.path.exists(output_path):
#         with open(output_path, 'r') as f:
#             existing_data = json.load(f)
#         existing_data[pattern_name] = new_filter
#         with open(output_path, 'w') as f:
#             json.dump(existing_data, f, indent=4)
#     else:
#         with open(output_path, 'w') as f:
#             json.dump({pattern_name: new_filter}, f, indent=4)


def save_results_to_final_profile(results: list, pattern_name: str = None):
    filters = INIT_FILTER.copy()

    for id, result in enumerate(results):
        map = ""
        for key, value in result.items():
            if key.startswith('w_') and value > 0:
                map += f"{KEY_MAPPING[key]}, "

        if pattern_name:
            filters[f'${result["pattern"]}_{id}'] = map[:-2]
            filters[f'_{result["pattern"]}_{id}'] = "{Init} & " + result['filter']

        else:

            filters[f'${result["pattern"]}'] = map[:-2]
            filters[f'_{result["pattern"]}'] = "{Init} & " + result['filter']

    new_filter = {
        "filter": json.dumps(filters),
        "weight": '{}',
        "params": {
            'cutloss': 15,
            'si_type': SI_TYPE,
            'si_slot': INIT_SLOTS,
            'si_asset': INIT_ASSETS,
            'w_lookback': 10,
            'w_thres_buy': 1.0,
            'w_thres_sell': -1.0,
            'w_k_exp': 0.0,
            'co_rank': "ranking_point",

        },
        "combine": {}

    }

    output_path = f'{RESULT_PATH}/config_results.json'
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    if pattern_name:
        try:
            if os.path.exists(output_path):
                with open(output_path, 'r') as f:
                    existing_data = json.load(f)
                existing_data[f"hyperopt_{pattern_name}"] = new_filter
                with open(output_path, 'w') as f:
                    json.dump(existing_data, f, indent=4)
            else:
                with open(output_path, 'w') as f:
                    json.dump({f"hyperopt_{pattern_name}": new_filter}, f, indent=4)
        except Exception as e:
            with open(output_path, 'w') as f:
                json.dump({f"hyperopt_{pattern_name}": new_filter}, f, indent=4)

    else:
        try:
            df_r = pd.DataFrame(results)
            df_r.to_csv(f'{RESULT_PATH}/df_buy_picked.csv', index=False)
            if os.path.exists(output_path):
                with open(output_path, 'r') as f:
                    existing_data = json.load(f)
                existing_data['buy_selected'] = new_filter
                with open(output_path, 'w') as f:
                    json.dump(existing_data, f, indent=4)
            else:
                with open(output_path, 'w') as f:
                    json.dump({'buy_selected': new_filter}, f, indent=4)
        except Exception as e:
            with open(output_path, 'w') as f:
                json.dump({'buy_selected': new_filter}, f, indent=4)


# def save_results_to_json(results: List[Dict[str, Any]], pattern_name: str):
#     output_path = f'{RESULT_PATH}/{pattern_name}_results.json'
#     os.makedirs(os.path.dirname(output_path), exist_ok=True)
#
#     with open(output_path, 'w') as f:
#         json.dump(results, f, indent=2)


# def save_results_to_csv(results: List[Dict[str, Any]], pattern_name: str):
#     output_path = f'{RESULT_PATH}/{pattern_name}_results.csv'
#     os.makedirs(os.path.dirname(output_path), exist_ok=True)
#
#     # Chuyển đổi list dict thành DataFrame
#     df = pd.DataFrame(results)
#
#     # Tách params thành các cột riêng
#     params_df = pd.DataFrame([r['params'] for r in results])
#     df = pd.concat([df.drop('params', axis=1), params_df], axis=1)
#
#     df.to_csv(output_path, index=False)


# def create_list_pattern_profiles_from_checkpoint(all_patterns_pkl_path):
#     for pattern in all_patterns_pkl_path:
#         pattern_name = pattern.split("/")[-1].split("_")[1].split(".")[0]
#
#         results = parse_hyperopt_results(pattern_name)
#         save_results_to_config_pattern(results, pattern_name)
#         save_results_to_csv(results, pattern_name)
#
#         # print result
#         print(f"\nTop {len(results)} kết quả tốt nhất cho pattern {pattern_name}:")
#         for result in results:
#             print(f"\nRank {result['rank']}:")
#             print(f"Loss: {result['loss']}")
#             print("Parameters:")
#             for param, value in result['params'].items():
#                 print(f"  {param}: {value}")
#             print(f"Pattern: {result['pattern']}")


def create_synthetic_profile_from_log(all_patterns_csv_path):
    results = []
    for path in all_patterns_csv_path:
        pattern_name = path.split("/")[-1].split("_")[2].split(".")[0]
        print(pattern_name)
        result = parse_logging_results(pattern_name, path)
        results.append(result[0])

    save_results_to_final_profile(results)


def create_each_pattern_profile_from_log(all_patterns_csv_path):
    for path in all_patterns_csv_path:
        pattern_name = path.split("/")[-1].split("_")[2].split(".")[0]
        print(pattern_name)
        result = parse_logging_results(pattern_name, path, top_n=30)
        save_results_to_final_profile(result, pattern_name)


if __name__ == "__main__":
    results = []
    # all_pattern = glob.glob(f'{PATH}/*.csv')
    # if same file. concat
    path_result = 'tuning/parallel/final_result/buy/31-03-26'
    path_list_ = glob.glob(f'{path_result}/**/*.csv', recursive=True)
    os.makedirs(f'{path_result}/output', exist_ok=True)

    for path in path_list_:
        df = pd.read_csv(path)
        results.append(df)
    df = pd.concat(results, axis=0).reset_index(drop=True)
    df = df[df['loss'] != float('inf')]
    df['ranking_spec'] = 0.4 * df['profit_median'] + \
                         0.4 * df['win_deal'] + \
                         0.2 * df['profit_median'] / df['holding_period_median']

    df['ranking_spec_val'] = 0.4 * df['profit_median_validate'] + \
                         0.4 * df['win_deal_validate'] + \
                         0.2 * df['profit_median_validate'] / df['holding_period_median_validate']

    filters = df['pattern'].unique().tolist()
    for f in filters:
        df_ = df.query(f'pattern == "{f}"').copy()
        df_['loss'] = df_['loss'].astype(float)
        df_ = df_.sort_values('loss', ascending=False).reset_index(drop=True)

        df_.to_csv(f'{path_result}/output/trials_buy_phase2__{f}.csv', index=False)
        # df_.to_csv(f'{path_result}/output/trials_buy_{f}.csv', index=False)

    # all_pattern = ['tuning/parallel/final_result/buy/trials_buy_TL3M_v0_292025:1.csv']
    # all_pattern = glob.glob('tuning/parallel/final_result/buy/09-01-26/output/*.csv', recursive=True)
    # all_pattern = ['tuning/parallel/final_result/buy/trials_buy_CashCowStock_v2.csv']
    # create_synthetic_profile_from_log(all_pattern)
    # create_each_pattern_profile_from_log(all_pattern)
    #
    # all_pattern = glob.glob(f'{PATH}/*.pkl')
    # create_list_pattern_profiles_from_checkpoint(all_pattern)
