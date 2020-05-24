from flask import Flask, request
from flask_cors import CORS, cross_origin
import pandas as pd

app = Flask(__name__)
CORS(app)

@app.route('/get_expert', methods = ['GET','POST'])
@cross_origin(origin='*',headers=['Content-Type','Authorization'])

def get_expert():

	# get keywords from the url request
	keywords = request.args['keywords']
	print('Here in get_expert.py file')
	print(keywords)

	# get topic users
	user_name_list = ['zamorajandrew','eduardo.garcia','aaron','viljami.virolainen']
	df_msgs_replies = pd.read_csv('ecv_analytics_scanning_data.csv')
	print('File read')

	expert_users = []
	for user_name in user_name_list:
		list_sent = df_msgs_replies[df_msgs_replies['user']==user_name]['text'].values
		all_words = []
		for sent in list_sent:
			if type(sent)==str:
				all_words.extend(sent.split(' '))

		if keywords in all_words:
			expert_users.append(user_name)

	print('Users: ',expert_users)
	
	return ','.join(expert_users)

if __name__ == "__main__":
	app.run(debug=True, host='0.0.0.0', port=8000)