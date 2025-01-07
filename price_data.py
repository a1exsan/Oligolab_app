import pandas as pd

def get_price_tab(scale):
    unit_list = ['simple N', 'BHQ1', 'BHQ2', 'LNA', 'FAM', 'HEX', 'SIMA', 'R6G', 'ROX', 'TAMRA', 'Cy5', 'Cy3', 'HPLC']
    price_1_3_list = [30, 600, 600, 700, 1000, 1500, 1500, 1800, 1000, 1000, 1000, 1000, 1300]
    price_3_10_list = [40, 1000, 1000, 1200, 1800, 2000, 2000, 2200, 1800, 1800, 1800, 1800, 1300]
    price_10_15_list = [45, 1700, 1700, 2300, 2700, 3000, 3000, 3200, 2700, 2700, 2700, 2700, 1300]

    price_df = pd.DataFrame({'Unit': unit_list})
    if scale == '1-3':
        price_df['Price, RUB'] = price_1_3_list
    elif scale == '3-10':
        price_df['Price, RUB'] = price_3_10_list
    else:
        price_df['Price, RUB'] = price_10_15_list

    price_df['Number'] = [0 for i in range(price_df.shape[0])]
    price_df['Sum, RUB'] = [0 for i in range(price_df.shape[0])]
    return price_df
