import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from classification import convert_to_class
import random


def generate_sample_reg(X_train):
	rand1 = np.random.randint(0,X_train.shape[0])
	rand2 = np.random.randint(0,X_train.shape[0])
	rand3 = np.random.randint(0,X_train.shape[0])
	if rand1 != rand2:
		s1 = X_train[rand1,:]
		s2 = X_train[rand2,:]
		#print('check', s1[0], s1[1])
		s_aug = (s1*s1[0] + s2*s2[0]) / (s1[0] + s2[0]) + np.random.normal(loc=0., scale=0.000001, size=s1.shape)
		s_aug[1] = (s1[1] + s2[1]) / 2
	elif rand1 != rand3:	
		s1 = X_train[rand1,:]
		s2 = X_train[rand2,:]
		s3 = X_train[rand3,:]
		s_aug = (s1*s1[0] + s2*s2[0] + s3*s3[0]) / (s1[0] + s2[0] + s3[0]) +  np.random.normal(loc=0., scale=0.000001, size=s1.shape)
		s_aug[1] = (s1[1] + s2[1] + s3[1]) / 3
	else:
		s_aug = np.zeros(X_train.shape[1])
	
	return s_aug
	
def read_data_single_sheet(cfg):
	xls = pd.ExcelFile(cfg['input_file'])
	df = pd.read_excel(xls, 'Sheet1')
	df = df.iloc[:,13:]
	df = df.sort_values(by=['DON-average'])
	df = df.iloc[:-4,:]
	print(df.tail())
	data = df.to_numpy(dtype=np.float32)
	print(data.shape)	
	plt.hist(data[:,1], bins=100)
	plt.show()
	X = data
	y = data[:,1]
	return X, y


def randomsplit_data_aug_cls(cfg):
    X, y = read_data_single_sheet(cfg)
    X[:,1] = convert_to_class(X[:,1])
    y = X[:,1] 
    print(y)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    if cfg['augment'] == False:
        return X_train, X_test
    elif cfg['augment'] == True:
        augumented_data = []
        print(np.amax(y))
        for i in range(int(np.amax(y)) + 1):
            print(i)
            current_cls_rows = []
            current_cls_aug = []
            for j in range(X_train.shape[0]):
                if X_train[j,1] == i:
                    current_cls_rows.append(j)
                    current_cls_aug.append(X_train[j])
            while (len(current_cls_aug) < 500):
                rand1 = random.choice(current_cls_rows)
                rand2 = random.choice(current_cls_rows)
                s1 = X_train[rand1,:]
                s2 = X_train[rand2,:]
                s_aug = (s1*s1[0] + s2*s2[0]) / (s1[0] + s2[0]) + np.random.normal(loc=0., scale=0.000001, size=s1.shape)
                s_aug[1] = s1[1]
                current_cls_aug.append(s_aug)
            augumented_data.extend(current_cls_aug)
        print('len od cls aug', len(augumented_data))
    return augumented_data, X_test

def randomsplit_data_aug_reg(cfg):

    X, y = read_data_single_sheet(cfg)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        	
    start=0
    end = 50
    interval = []
    for i in range(100):	
        interval.append([start,end])
        start = end
        end = end +50
	
    augumented_data = []
    for inte in interval:
        inte_count = 0		
        for i in range(X_train.shape[0]):
            if X_train[i][1] >=inte[0] and X_train[i][1] < inte[1]:
                augumented_data.append(X_train[i])
                inte_count += 1
        while inte_count < 20:
            aug_sample = generate_sample_reg(X_train)
            if np.sum(aug_sample) != 0 and aug_sample[1] >=inte[0] and aug_sample[1] < inte[1]:
                augumented_data.append(aug_sample)
                inte_count += 1
            print('interval {}, count {}'.format(inte[0], len(augumented_data)))
        if inte[0] > 4200:
            break
	#add larger than 4300 data		
    for i in range(X_train.shape[0]):
        if X_train[i][1] > 4300:
            augumented_data.append(X_train[i])
    return augumented_data, X_test

def preprocess_augreg_multi_sheet(df):
	"train test split, hist, augment"
	df_train = df.loc[df['Cal-Test'] == 'Cal']
	df_test = df.loc[df['Cal-Test'] == 'Test']
	df_train = df_train.iloc[:,14:]
	df_test = df_test.iloc[:,14:]
	df_train = df_train.sort_values(by=['DON-average'])
	df_test = df_test.sort_values(by=['DON-average'])
	#print(df_train.head())
	#print(df_test.head())
	data_train = df_train.to_numpy(dtype=np.float32)
	data_test = df_test.to_numpy(dtype=np.float32)
	print('before aug train',data_train.shape)
	print('test', data_test.shape)
	
	if cfg['augment'] == True:
		augment_data = []
		aug_num = 3*data_train.shape[0]
		for i in range(aug_num):
			aug_sample = generate_sample_reg(data_train)
			if np.sum(aug_sample) != 0:
				augment_data.append(aug_sample)
		augment_data = np.asarray(augment_data)
	
		print('augment', augment_data.shape)
		data_train = np.concatenate((data_train, augment_data), axis=0)
		print('after aug', data_train.shape)
		
		
	#plt.hist(data_train[:,1])
	#plt.show()
	#plt.hist(data_test[:,1])
	#plt.show()
	return data_train, data_test	
	
def split_on_variety_aug_reg(cfg):

	xls = pd.ExcelFile(cfg['input_file'])
	df1 = pd.read_excel(xls, 'Calibre')
	df2 = pd.read_excel(xls, 'Hellfire')
	df3 = pd.read_excel(xls, 'Lancer')
	df4 = pd.read_excel(xls, 'Scepter')
	df5 = pd.read_excel(xls, 'Sunmax')
	df_all = [df1, df2,df3,df4,df5]
	
	train_all = []
	test_all = []
	for ele in df_all:
		data_train, data_test = preprocess_augreg_multi_sheet(ele)
		train_all.append(data_train)
		test_all.append(data_test)
	train_all = np.concatenate(train_all, axis=0)
	test_all = np.concatenate(test_all, axis=0)
	
	print('train_all',train_all.shape)
	print('test_all',test_all.shape)
	train_all = train_all[:,1:]
	train_all_df = pd.DataFrame(train_all)
	train_all_df.to_csv(cfg['out_train'])
	
	test_all = test_all[:,1:]
	test_all_df = pd.DataFrame(test_all)
	test_all_df.to_csv(cfg['out_test'])
	
		
	

	
			

if __name__ == '__main__':

    cfg = {'input_file': '/home/jing/projects/hsi iman/backgroudremovalandtrain/exel_data/Ave-5g Hyspex-Pixels.xlsx',
	'data_type':'raw',
	'augment':False,
    'task': 'reg',
    'out_train':'train.csv',
    'out_test':'test.csv'}
	
    if cfg['data_type'] == 'raw':
        print('..')
        if cfg['task'] == 'reg':
            augumented_data, X_test = randomsplit_data_aug_reg(cfg)
        elif cfg['task'] == 'cls':
            augumented_data, X_test = randomsplit_data_aug_cls(cfg)
	 	
		
        print('final number', len(augumented_data))
	
        augumented_data = np.asarray(augumented_data)
        print(augumented_data.shape)	
        augumented_data = augumented_data[:,1:]
        print(augumented_data.shape)
	
        augmented_df = pd.DataFrame(augumented_data)	
        augmented_df.to_csv(cfg['out_train'])
	
        X_test = X_test[:,1:]
        X_test_df = pd.DataFrame(X_test)
        X_test_df.to_csv(cfg['out_test'])
		
    elif cfg['data_type'] == 'byvariety':
        split_on_variety_aug_reg(cfg)
	
	
	
	 

