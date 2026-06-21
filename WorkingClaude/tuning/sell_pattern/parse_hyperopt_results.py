import glob
import json
import os
import sys
from typing import Dict, List, Any

import pandas as pd

current_dir = os.path.dirname(os.path.abspath(__file__))
current_dir = current_dir.replace("/tuning/sell_pattern", "")
os.chdir(current_dir)
sys.path.insert(0, current_dir)

# Import pattern configs from hyo_tuning_manager - single source of truth
from tuning.sell_pattern import hyo_tuning_manager

# Định nghĩa các pattern và path tương ứng
PATH = "tuning/parallel/final_result/sell"
RESULT_PATH = "tuning/results"
INIT_ASSETS = 50.0
INIT_SLOTS = 25
SI_TYPE = "Cash allocation"

KEY_MAPPING = {
    'w_ma21': 'MA21',
    'w_ma31': 'MA31',
    'w_ma41': 'MA41',
    'w_s13': 'S13',
    'w_selllowgrowth': 'SellLowGrowth',
    'w_sellresistance1y': 'SellResistance1Y',
    'w_sellresistance1m': 'SellResistance1M',
    'w_sellresistance': 'SellResistance',
    'w_sellbv': 'SellBV',
    'w_sellbv2': 'SellBV2',
    'w_sellpe': 'SellPE',
    'w_sellvolmax': 'SellVolMax',
    'w_beardvg2': 'BearDvg2'
}

INIT_FILTER = {
    "Init": "(Volume*Price/Inflation_7>10e+8) & (time>='2014-01-01') & (time<='2026-01-01') & (Price > 10000)",
    "_PS1": "Price < 0",

}

# Pattern configs - now importing from hyo_tuning_manager.py (single source of truth)
# Strip Init filter prefix to match the format expected by parse_hyperopt_results
PATTERN_CONFIGS = {
    'MA21': {
        'checkpoint_path': f'{PATH}/trials_MA21.pkl',
        'log_path': f'{PATH}/trials_MA21.csv',
        'pattern_template': hyo_tuning_manager.ma21_config.get('filter_template').replace(
            f"{hyo_tuning_manager.Init}& ", "")
    },
    'MA31': {
        'checkpoint_path': f'{PATH}/trials_MA31.pkl',
        'log_path': f'{PATH}/trials_MA31.csv',
        'pattern_template': hyo_tuning_manager.ma31_config.get('filter_template').replace(
            f"{hyo_tuning_manager.Init}& ", "")
    },
    'MA41': {
        'checkpoint_path': f'{PATH}/trials_MA41.pkl',
        'log_path': f'{PATH}/trials_MA41.csv',
        'pattern_template': hyo_tuning_manager.ma41_config.get('filter_template').replace(
            f"{hyo_tuning_manager.Init}& ", "")
    },
    'S13': {
        'checkpoint_path': f'{PATH}/trials_S13.pkl',
        'log_path': f'{PATH}/trials_S13.csv',
        'pattern_template': hyo_tuning_manager.s13_config.get('filter_template').replace(f"{hyo_tuning_manager.Init}& ",
                                                                                         "")
    },
    'SellBV': {
        'checkpoint_path': f'{PATH}/trials_SellBV.pkl',
        'log_path': f'{PATH}/trials_SellBV.csv',
        'pattern_template': hyo_tuning_manager.sellbv_config.get('filter_template').replace(
            f"{hyo_tuning_manager.Init}& ", "")
    },
    'SellBV2': {
        'checkpoint_path': f'{PATH}/trials_SellBV2.pkl',
        'log_path': f'{PATH}/trials_SellBV2.csv',
        'pattern_template': hyo_tuning_manager.sellbv2_config.get('filter_template').replace(
            f"{hyo_tuning_manager.Init}& ", "")
    },
    'SellPE': {
        'checkpoint_path': f'{PATH}/trials_SellPE.pkl',
        'log_path': f'{PATH}/trials_SellPE.csv',
        'pattern_template': hyo_tuning_manager.sellpe_config.get('filter_template').replace(
            f"{hyo_tuning_manager.Init}& ", "")
    },
    'SellResistance': {
        'checkpoint_path': f'{PATH}/trials_SellResistance.pkl',
        'log_path': f'{PATH}/trials_SellResistance.csv',
        'pattern_template': hyo_tuning_manager.sellresistance_config.get('filter_template').replace(
            f"{hyo_tuning_manager.Init}& ", "")
    },
    'SellResistance1M': {
        'checkpoint_path': f'{PATH}/trials_SellResistance1M.pkl',
        'log_path': f'{PATH}/trials_SellResistance1M.csv',
        'pattern_template': hyo_tuning_manager.sellresistance1m_config.get('filter_template').replace(
            f"{hyo_tuning_manager.Init}& ", "")
    },
    'SellResistance1Y': {
        'checkpoint_path': f'{PATH}/trials_SellResistance1Y.pkl',
        'log_path': f'{PATH}/trials_SellResistance1Y.csv',
        'pattern_template': hyo_tuning_manager.sellresistance1y_config.get('filter_template').replace(
            f"{hyo_tuning_manager.Init}& ", "")
    },
    'BearDvg2': {
        'checkpoint_path': f'{PATH}/trials_BearDvg2.pkl',
        'log_path': f'{PATH}/trials_BearDvg2.csv',
        'pattern_template': hyo_tuning_manager.beardvg2_config.get('filter_template').replace(
            f"{hyo_tuning_manager.Init}& ", "")
    },
    'SellVolMax': {
        'checkpoint_path': f'{PATH}/trials_SellVolMax.pkl',
        'log_path': f'{PATH}/trials_SellVolMax.csv',
        'pattern_template': hyo_tuning_manager.sellvolmax_config.get('filter_template').replace(
            f"{hyo_tuning_manager.Init}& ", "")
    },
    'BearDvgVNI': {
        'checkpoint_path': f'{PATH}/trials_BearDvgVNI.pkl',
        'log_path': f'{PATH}/trials_BearDvgVNI.csv',
        # BearDvgVNI has its own time filter, so we don't strip Init
        'pattern_template': hyo_tuning_manager.beardvgvni_config.get('filter_template')
    }
}


def parse_logging_results(pattern_name: str, log_path: str, top_n: int = 50) -> List[Dict[str, Any]]:
    if pattern_name not in PATTERN_CONFIGS:
        raise ValueError(f"Pattern {pattern_name} không tồn tại trong cấu hình")

    config = PATTERN_CONFIGS[pattern_name]
    # log_path = config['log_path']
    pattern_template = config['pattern_template']

    if not os.path.exists(log_path):
        raise FileNotFoundError(f"Không tìm thấy file log tại {log_path}")

    # Đọc dữ liệu từ file log
    data = pd.read_csv(log_path)
    data = data[data['loss'] != float('inf')]

    # # Tính toán ranking
    # data['ranking'] = 0.4 * data['si_return'] + \
    #                   0.3 * data['win_deal'] + \
    #                   0.15 * data['win_quarter'] + \
    #                   0.1 * data['winblock_20quarters'] + \
    #                   0.05 * data['winblock_24months']
    #                   # 0.1 * data['deal'] / data['deal'].max() * 100

    # Lấy top_n kết quả tốt nhất
    top_data = data.nlargest(top_n, 'loss').copy()
    # Tạo cột filter
    top_data['filter'] = top_data.apply(lambda row: pattern_template.format(**row.to_dict()), axis=1)

    # Sắp xếp theo ranking
    # top_data.sort_values(by='ranking', ascending=False, inplace=True)

    # Chuyển đổi DataFrame thành list of dictionaries
    results = top_data.to_dict('records')

    # Thêm thông tin về pattern_name và rank
    for i, result in enumerate(results):
        result['pattern_name'] = pattern_name
        result['rank'] = i + 1

    return results


def save_results_to_final_profile(results):
    filters = INIT_FILTER.copy()

    for result in results:
        filters[f'~{result["pattern"]}'] = "{Init} & " + result['filter']

    new_filter = {
        "filter": json.dumps(filters),
        "weight": '{}',
        "params": {
            'cutloss': 100,
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

    df_r = pd.DataFrame(results)
    df_r.to_csv(f'{RESULT_PATH}/df_sell_picked.csv', index=False)
    if os.path.exists(output_path):
        with open(output_path, 'r') as f:
            existing_data = json.load(f)
        existing_data['sell_selected'] = new_filter
        with open(output_path, 'w') as f:
            json.dump(existing_data, f, indent=4)
    else:
        with open(output_path, 'w') as f:
            json.dump({'sell_selected': new_filter}, f, indent=4)


def create_synthetic_profile_from_log(all_patterns_csv_path):
    results = []
    for path in all_patterns_csv_path:
        pattern_name = path.split("/")[-1].split("_")[2].split(".")[0]
        print(pattern_name)
        result = parse_logging_results(pattern_name, path)
        results.append(result[0])

    save_results_to_final_profile(results)


if __name__ == "__main__":
    results = []
    # if same file. concat
    path_result = 'tuning/parallel/final_result/sell/2026-03-13'
    path_list_ = glob.glob(f'{path_result}/**/*.csv', recursive=True)
    for path in path_list_:
        df = pd.read_csv(path)
        results.append(df)
    df = pd.concat(results, axis=0).reset_index(drop=True)
    df = df[df['loss'] != float('inf')]
    df = df[df['original_loss'] != float('inf')]

    filters = df['pattern'].unique().tolist()
    for f in filters:
        df_ = df.query(f'pattern == "{f}"').copy()
        df_['loss'] = df_['loss'].astype(float)
        df_['original_loss'] = df_['original_loss'].astype(float)
        df_ = df_.drop_duplicates(subset=['original_loss'], keep='first')
        df_ = df_.sort_values('original_loss', ascending=False).reset_index(drop=True)
        df_.to_csv(f'{path_result}/output/trials_sell_{f}.csv', index=False)

    ##############################################
    # results = []
    # all_pattern = glob.glob(f'{PATH}/*.csv')
    # all_pattern = glob.glob(f'{path_result}/output/*.csv')
    # create_synthetic_profile_from_log(all_pattern)
