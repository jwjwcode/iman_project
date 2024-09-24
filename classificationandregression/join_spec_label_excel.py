import pandas as pd


def read_combine_df(cfg):
    meta_data_xls = pd.ExcelFile(cfg['meta'])

    meta_data_df = pd.read_excel(meta_data_xls, '5-g samples')

    print(meta_data_df.tail())
    label_df = pd.concat([meta_data_df['DAF Sample-ID'], meta_data_df['DON (μg/kg)']], axis=1)
    
    print(label_df.tail())

    spec_df = pd.read_csv(cfg['spec'])

    print(spec_df)
    name_list = []
    for i in range(spec_df.shape[0]):
        name = spec_df.iloc[i][0] 
        name = name[3:-4]
        name_list.append(name)
        #print(name)
    spec_df.insert(1,'ind', name_list)
    spec_df = spec_df.iloc[:,1:]
        
    print(spec_df.head)
    
    dataset_df = spec_df.join(label_df)
    
    print(dataset_df)
    
    
  
    


















if __name__ == '__main__':
    cfg = {
        'meta' : '/home/jing/projects/hsi iman/backgroudremovalandtrain/output_bg_remove/DON MODELING Data 24 Jul 2024.xlsx',
        'spec' : '/home/jing/projects/hsi iman/backgroudremovalandtrain/output_bg_remove/5h.csv',
        
        }
    
    read_combine_df(cfg)