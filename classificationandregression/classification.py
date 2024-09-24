import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import f1_score, precision_recall_fscore_support, confusion_matrix
import matplotlib.pyplot as plt

def convert_to_class(y, threshold):
	neg_count=0
	pos_count=0
	plt.hist(y, bins=100)
	plt.show()
	for i in range(y.shape[0]):
		if y[i] <= threshold:
			y[i] = 0
			neg_count += 1
		elif y[i] > threshold:
			y[i] = 1
			pos_count += 1
		else:
			print('wrong label')
	print('{} pos, {} neg'.format(pos_count, neg_count))
	return y


def load_process_data(cfg):
    #load for don classification
	df_train = pd.read_csv(cfg['train'])
	data_train = df_train.to_numpy().astype(np.float32)
	data_train = data_train[:,1:]
	X_train = data_train[:,1:]
	y_train = data_train[:,0]
	y_train = convert_to_class(y_train)
	
	df_test = pd.read_csv(cfg['test'])
	data_test = df_test.to_numpy().astype(np.float32)
	data_test = data_test[:,1:]
	X_test = data_test[:,1:]
	y_test = data_test[:,0]
	y_test = convert_to_class(y_test)
	print(X_train.shape, y_train.shape,X_test.shape, y_test.shape)
	scaler = StandardScaler()
	X_train = scaler.fit_transform(X_train)
	X_test = scaler.transform(X_test)
	#X_train, X_test, y_train, y_test = train_test_split(X_train, y_train, test_size=0.33, random_state=42)
	
	return X_train, y_train, X_test, y_test


def classification(X_train, y_train, X_test, y_test, cfg):
	if cfg['cls'] == 'svm':
		model = GridSearchCV(SVC(), param_grid=cfg['gridsearch'], refit = True, verbose = 3)
        #model = SVC()
		
	model.fit(X_train, y_train)
	acc = model.score(X_test, y_test)
	print(model.best_params_)
	print(acc)
	pred = model.predict(X_test)
	f1 = f1_score(y_test, pred)
	p, r, f, _ = precision_recall_fscore_support(y_test, pred)
	cm = confusion_matrix(y_test, pred)
	print(f1)
	print('p {}, r {}, f {}'.format(p,r,f))
	print(cm)
def convert_label(label):
    for i in range(label.shape[0]):
        if label[i] == 0:
            label[i] = 0
        elif label[i]==1:
            label[i] = 0
        elif label[i] == 2:
            label[i] = 1
        elif label[i] == 3:
            label[i] = 2
        else:
            print('wrong label')
    return label

def remove_label3_convert(df_input,df_label):
    df_label = np.expand_dims(df_label,1)
    print('..', df_input.shape, df_label.shape)
    all_data = np.concatenate((df_label, df_input), axis=1)
    print(all_data.shape)
    new_data = []
    for i in range(df_label.shape[0]):
        if all_data[i,0] != 3:
            new_data.append(all_data[i,:])
    new_data = np.asarray(new_data)
    spec_data = new_data[:,1:]
    label_data = new_data[:,0]
    print(spec_data.shape, label_data.shape)
    label_data = convert_label(label_data)
    return spec_data, label_data


def thresholdforalllabel(df, threshold):
	#to get a label based on level of four fungi
    all_label = df.iloc[:,1:5]
    print(all_label.head())
    all_label = all_label.to_numpy().astype(np.float32)
    new_label = np.zeros(all_label.shape[0])
    for i in range(all_label.shape[0]):
        if (all_label[i,0] < threshold and all_label[i,1] < threshold) and (all_label[i,2] < threshold):
            new_label[i] = 0
        elif (all_label[i,0] > threshold or all_label[i,1] > threshold) and (all_label[i,2] < threshold):
            new_label[i] = 1
        elif (all_label[i,0] < threshold and all_label[i,1] < threshold) and (all_label[i,2] > threshold):
            new_label[i] = 2
        elif (all_label[i,0] > threshold or all_label[i,1] > threshold) and (all_label[i,2] > threshold):
            new_label[i] = 3
        else:
            print(all_label[i,:])
            print('wrong label')
        
    print(new_label.shape)
    print(new_label[:5])
    return new_label
    
            

	
def load_fungi_data(cfg):
    df = pd.read_excel(cfg['cls_data'])
    df_spec = df.iloc[:,7:]
    ori_label = df.iloc[:,6]
    e1_label = df.iloc[:,1]
    e2_label = df.iloc[:,2]
    f1_label = df.iloc[:,3]
    f2_label = df.iloc[:,4]   
    
    spec_data = df_spec.to_numpy().astype(np.float32)
    all_label = thresholdforalllabel(df, cfg['threshold'])
    
    
    label = f1_label.to_numpy().astype(np.float32)
    print('f1 label', label)
    
    label = convert_to_class(label, cfg['threshold'])
    
    #ori_label = ori_label.to_numpy().astype(int)
    #spec_data, ori_label = remove_label3_convert(spec_data, ori_label)
    #ori_label = convert_label(ori_label)
    #ori_label = ori_label.squeeze()
    
    #print(spec_data.shape, ori_label.shape)
    
    X_train, X_test, y_train, y_test = train_test_split(spec_data, label, test_size=0.33, random_state=42, stratify=None)
    print(X_train.shape, y_train.shape,X_test.shape, y_test.shape)
    scaler = StandardScaler()
    X_train = scaler.fit_transform(X_train)
    X_test = scaler.transform(X_test)
    
    return X_train, y_train, X_test, y_test
    
	



if __name__ == '__main__':
	cfg = {'train':'/home/jing/projects/hsi iman/backgroudremovalandtrain/augmentdata/5h/train_all.csv',
	'test':'/home/jing/projects/hsi iman/backgroudremovalandtrain/augmentdata/5h/test_all.csv',
    'cls_data':'/home/jing/projects/hsi iman/backgroudremovalandtrain/exel_data/cls_data/All in one-Normalised Spectrum.xlsx',
	'cls':'svm',
    'threshold':25,
	'gridsearch':{'kernel':('linear', 'rbf'), 'C':[0.1, 1, 10, 100], 'gamma':[1, 0.1, 0.01, 0.001]}}
	X_train, y_train, X_test, y_test = load_fungi_data(cfg)
	classification(X_train, y_train, X_test, y_test, cfg)
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
