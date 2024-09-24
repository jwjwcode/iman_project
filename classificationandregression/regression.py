import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.cross_decomposition import PLSRegression
from sklearn.linear_model import LinearRegression, Ridge, Lasso, BayesianRidge
from sklearn.svm import SVR
from sklearn.metrics import mean_squared_error, r2_score
import matplotlib.pyplot as plt

def load_process_data(cfg):
	df_train = pd.read_excel(cfg['train'])
	data_train = df_train.to_numpy().astype(np.float32)
	data_train = data_train[:,1:]
	X_train = data_train[:,1:]
	y_train = data_train[:,0]
	
	plt.hist(y_train)
	#plt.show()

	
	df_test = pd.read_excel(cfg['test'])
	data_test = df_test.to_numpy().astype(np.float32)
	data_test = data_test[:,1:]
	X_test = data_test[:,1:]
	y_test = data_test[:,0]
	plt.hist(y_test)
	#plt.show()
	print(X_train.shape, y_train.shape,X_test.shape, y_test.shape)
	scaler = StandardScaler()
	X_train = scaler.fit_transform(X_train)
	X_test = scaler.transform(X_test)
	X_train, X_test, y_train, y_test = train_test_split(X_train, y_train, test_size=0.33, random_state=42)
	
	return X_train, y_train, X_test, y_test


def regression(X_train, y_train, X_test, y_test, cfg):
	if cfg['regressor'] == 'plsr':
		model = PLSRegression(n_components=12)
	elif cfg['regressor'] == 'lr':
		model = LinearRegression()
	elif cfg['regressor'] == 'ridge':
		model = Ridge(alpha=1.0)
	elif cfg['regressor'] == 'lasso':
		model = Lasso(alpha=0.1)
	elif cfg['regressor'] == 'svr':
		model = SVR()
	elif cfg['regressor'] == 'br':
		model = BayesianRidge()
		
	model.fit(X_train, y_train)
	R2 = model.score(X_test, y_test)
	print(R2)
	
	
	



if __name__ == '__main__':
	cfg = {'train':'/media/jing/GRDC-A/Excel files/Ave-Resonon nd Hyspex 5 nd 40g.xlsx',
	'test':'/media/jing/GRDC-A/Excel files/Ave-Resonon nd Hyspex 5 nd 40g.xlsx',
	'regressor':'br'}
	X_train, y_train, X_test, y_test = load_process_data(cfg)
	regression(X_train, y_train, X_test, y_test, cfg)

