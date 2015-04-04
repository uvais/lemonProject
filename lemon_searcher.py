import mysql.connector

ignore_words = ["what", "where", "how", "to", "from", "is", "was", "the", "this", "do", "does", "did", "will", "which", "why", "when"]

class Searcher:

	def __init__(self):
		self.connection = mysql.connector.connect(host="localhost", database="testDb", password="root", user="root")
		self.cursor = self.connection.cursor()


	def query(self, word):
		tokens = word.split()
		temp = [x for x in tokens]
		print tokens
		for t in tokens:
			if t in ignore_words:
				temp.remove(t)

	
		self.cursor.execute("select * from lemon4 where word='"+temp[0]+"'")
		row = self.cursor.fetchone()
		urls = []
		while row is not None:
			urls.append((row[2], row[0]))
			row = self.cursor.fetchone()
		results = sorted(urls, reverse=1)
		return results

#------------------------Added code

	def login(self, uname, password):
		self.cursor.execute("select name, pass from admindet")
		row = self.cursor.fetchone()
		dbuname = row[0];
		dbpass = row[1];
		print dbuname;
		print dbpass;
		if dbuname != uname:
			return 1
		elif dbpass != password:
			return 1
		else:
			return 0
#----------------------------------------

if __name__ == "__main__":
	#app.debug = True
	#app.run()
	searcher = Searcher()
	value = searcher.login("admin","admin")
	print value
