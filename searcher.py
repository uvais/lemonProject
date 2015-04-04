import mysql.connector
from bson.objectid import ObjectId
from nltk.corpus import stopwords

ignorewords = stopwords.words("english")

class Searcher:
	def __init__(self, dbname):
		client = MongoClient("localhost", 27017)
		db = client[dbname]
		self.wordlocation = db.wordlocation
		self.urllist = db.urllist
		self.wordlist = db.wordlist
		self.link = db.link
		self.linkwords = db.linkwords
		
	def getmatchrows(self, q):
		# Strings to build the query
		urls = []
		wordids = []
		words = q.split()
		for word in words: 
			if word in ignorewords: words.remove(word)
		for word in words:
			w = self.wordlist.find_one({"word": word.lower()})
			wordids.append(w['_id'])

		wordid = self.wordlist.find_one({"word": words[0]})
		del(words[0])
		length = 2
		urls = self.wordlocation.find({"wordid": ObjectId(wordid['_id'])})
		rows = [ [i['urlid'], i['location']] for i in urls]	
		for word in words:
			wordid = self.wordlist.find_one({"word": word})
			urls = self.wordlocation.find({"wordid": ObjectId(wordid['_id'])})
			for url in urls:
				for r in rows:
					if url['urlid'] == r[0] and url['location'] not in r and len(r)<=length:
						x = [ n for n in r]
						x.append(url['location'])
						rows.append(x)
			length += 1
		rows = [ tuple(x) for x in rows if len(x) == len(words)+2 ]

		return rows, wordids

	def getscoredlist(self, rows, wordids):
		totalscores = dict([ (row[0],0) for row in rows ])

		# Scores
		weights = [ (1.0, self.frequencyscore(rows)), 
					(1.0, self.locationscore(rows)), 
					(1.0, self.distancescore(rows)),
					(1.0, self.inboundlinkscore(rows))
					]

		for (weight, scores) in weights:
			for url in totalscores:
				totalscores[url] += weight*scores[url]

		return totalscores

	def geturlname(self, id):
		url = self.urllist.find_one({"_id": id })
		return url['url']

	def frequencyscore(self, rows):
		counts = dict([(row[0], 0) for row in rows])
		for row in rows: counts[row[0]] += 1
		return self.normalizescores(counts)

	def locationscore(self, rows):
		locations = dict([(row[0], 1000000) for row in rows])
		for row in rows:
			loc = sum(row[1:])
			if loc < locations[row[0]]: locations[row[0]] = loc

		return self.normalizescores(locations, smallIsBetter=1)

	def distancescore(self, rows):
		# if there's only one word, everyone wins!
		if len(rows[0])<=2: return dict([(rows[0], 1.0) for row in rows])

		# initialize the dictionary with large values
		mindistance = dict([(row[0], 1000000) for row in rows])

		for row in rows:
			dist = sum([abs(row[i]-row[i-1]) for i in range(2, len(row))])
			if dist<mindistance[row[0]]: mindistance[row[0]]=dist
		return self.normalizescores(mindistance, smallIsBetter=1)

	def inboundlinkscore(self, rows):
		uniqueurls = set([row[0] for row in rows])
		inbouncount = dict([ (u, self.link.find({"toid": u}).count())
				for u in uniqueurls
			])
		return self.normalizescores(inbouncount)

	def normalizescores(self, scores, smallIsBetter=0):
		vsmall = 0.00001 	# Avoid division by zero errors
		if smallIsBetter:
			minscore = min(scores.values())
			return dict([(u, float(minscore)/max(vsmall, l)) for (u, l) in scores.items()])
		else:
			maxscore = max(scores.values())
			if maxscore == 0: maxscore = vsmall
			return dict([(u, float(c)/maxscore) for (u,c) in scores.items()])

	def query(self, q):
		result = []
		rows, wordids = self.getmatchrows(q)
		scores = self.getscoredlist(rows,wordids)
		rankedscores = sorted([(score, url) for (url, score) in scores.items()], reverse=1)
		for (score, urlid) in rankedscores[:10]:
			result.append((score, self.geturlname(urlid)))
		return result

if __name__ == "__main__":
	searcher = Searcher("swan")
	searcher.query("india father")

