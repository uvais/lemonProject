from flask import *
from lemon_searcher import *

lemon = Searcher()

app = Flask(__name__)

@app.route('/')
def home():
	return render_template('index.html')

@app.route('/query', methods=['GET', 'POST'])
def query():
	if request.method == 'POST':
		q = request.form['q']
		result = lemon.query(q)
	return render_template('results.html', result=result)

#--------Added code--------------------------

@app.route('/admin', methods=['GET', 'POST'])
def admhome():
	return render_template('admin.html')

@app.route('/admincheck', methods=['POST'])
def admlogin():
	if request.method == 'POST':
		u = request.form['uname']
		p = request.form['pass']
		result = lemon.login(u,p)
	
		if result == 1:
			return render_template('error.html')
		elif result == 0:
			return render_template('adminhome.html')

#-----------------------added code---------------------

if __name__ == '__main__':
	app.run()
