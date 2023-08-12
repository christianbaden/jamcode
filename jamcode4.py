#!/usr/bin/env python
# -*- coding: utf-8 -*-

###########################################################################
#                                                                         #
#                           (c) Christian Baden                           #
#             The Hebrew University of Jerusalem, Israel, 2023            #
#                                                                         #
# Please cite as:                                                         #
#        Baden, Christian (2023). Jamcode: A syntax and Python script for #
#        syntax-sensitive, context-disambiguated, dictionary-based        #
#        textual analysis. Available Online:                              #
#        https://github.com/christianbaden/jamcode                        #
#                                                                         #
# This script is built for use in conjunction with the AmCAT free & open  #
# source infrastructure for large-scale text analysis for the social      #
# sciences & humanities https://amcat.nl, and specifially, the Jerusalem  #
# AmCAT Server http://jamcat.mscc.huji.ac.il                              #
#                                                                         #
# JAMCODE is the JAmCAT library operated by the coding script JCODE.      #
# It interacts with the JAmCAT server using the AmCAT API.                #
#                                                                         #
# JAmCAT and the JCODE/JAMCODE coding script have been developed by       #
# INFOCORE (In)Forming Conflict Prevention, Response and Resolution:      #
#        The Role of Media in Violent Conflict                            #
#        Funded by the European Union FP7 (Cooperation), Grant Nr. 613308 #
#        http://www.infocore.eu/                                          #
# and                                                                     #
# RECORD Frame Justification and Resonance in Conflict-Related Discourse  #
#        Funded by the European Union FP7 (Marie Curie), Grant Nr. 627682 #
#        http://www.frame-resonance.eu/                                   #
#                                                                         #
# For an example of a dictionary that can be applied using Jamcode,       #
# please see the INFOCORE Dictionary, a multilingual dictionary for       #
# automatically analyzing conflict-related discourse:                     #
#        Baden, Christian, Jungblut, Marc, Micevski, Igor, Stalpouskaya,  #
#        Katsiaryna, Tenenboim-Weinblatt, Keren, Berganza Conde, Rosa,    #
#        Dimitrakopoulou, Dimitra, & Fröhlich, Romy (2018). The INFOCORE  #
#        Dictionary. Available Online:                                    #
#        https://osf.io/f5u8h/                                            #
#        https://github.com/christianbaden/INFOCORE                       #
#                                                                         #
# Jamcode is free and open software: you can redistribute it and/or       #
# modify it under the terms of the GNU Lesser General Public License as   #
# published by the Free Software Foundation, either version 3 of the      #
# License, or (at your option) any later version.                         #
#                                                                         #
# It is distributed in the hope that it will be useful, but WITHOUT       #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or   #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public     #
# License for more details.                                               #
#                                                                         #
###########################################################################

# GETTEXTS obtains a ordered list of text and metadata from the AmCAT server.
# It requires the AmCAT library <amcat4py>, which defines the AmCAT API
def gettexts(index,fromnr):
	from amcat4py import AmcatClient
	import html
	texts=[]
	conn=AmcatClient('PLEASE ENTER ADDRESS OF AMCAT SERVER HERE')
	n=0
	xid='id'
	try: # On JAmCAT, some batches were uploaded using 'id' as identifiers, others with '_id'.
		list(conn.query(index,fields=None))[0]['id']
	except:
		xid='_id'
	for a in conn.query(index,fields=None): # retrieves all fields; if only specific known fields are needed, list them here
		id=a[xid]
		medium=a['medium']
		date=a['date'].strftime("%Y-%m-%dT%H:%M:%S")
		title=html.unescape(a['headline'].lower())
		subtitle=''
		if a['byline']:
			subtitle=html.unescape(a['byline'].lower())
		else:
			subtitle=''
		text=html.unescape(a['text'].lower())
		article=[id,medium,date,title,subtitle,text]
		if int(id)>=fromnr:
			n=n+1
			texts.append(article)
			if n==500:
				print('.', end=" ",flush=True)
				n=0
	print(len(texts),'texts retrieved...')
	return texts

# IMPORTDICT imports a dictionary file named DICT_<name>.txt, using the JAMCODE Query Syntax:
# Every line defines a separate query, which is structured as follows:
# <concept id>	<concept name>	<time range>	<search phrases>
# <concept id> specifies a unique number, which will be used as identifier for
# recognized concepts.
# <concept name> provides a string as label for the concept.
# <time range> specifies a date range (format: dd/mm/yy-dd/mm/yy).
# If left empty, the query is applied to all documents.
# If specified, only documents dated within the specified time range are coded using
# the following search phrases.
# <search phrases> are Boolean, distance-sensitive queries.
# Multiple search phrases are separated by a space character.
# Each search phrase requires a keyword, whose position will be recorded for
# recognized concepts. Keywords are not case sensitive. They allow UNICODE, but
# only alphanumerical characters. Keywords can be truncated (*) at the beginning and
# at the end (so *foo* will match all words that contain the string 'foo').
# Search phrases can be further specified by adding five kinds of additional criteria.
# Boolean proximity queries:
#  _y(<words>~$)   specifies words that must be found within a distance of $ words for
#                  the keyword to be coded.
#  _n(<words>~$)   specifies words that must not be found within a distance of $ words
#                  for the keyword to be coded.
#     <words>      can be one word (which can be truncated again) or multiple words
#                  separated by & (AND) or | (OR). For complex queries, rounded brackets
#                  organize the Boolean query. Within one bracket, only one kind of
#                  operator is allowed. Brackets must contain more than one word. The
#                  current code supports only up to five levels of nested brackets.
#                  EXAMPLES:
#                  _y(*foo~5) is satisfied if a word ending with 'foo' is found within 5 words distance
#                  _y(foo&*bar~10) is satisfied if the word 'foo' and a word ending with 'bar' must be found within 10 words distance
#                  _y(foo*|bar~2) is satisfied if either a word starting with 'foo' or the word 'bar' are found within 2 words distance
#                  _y(foo&(bar|xyz)~7) is satisfied if the word 'foo' as well as either 'bar' or 'xyz' are found within 7 words distance
#                  _y(foo&bar|xyz~7) is an ILLEGAL query: different operators within the same bracket
#                  _y(foo|(bar)|xyz~5) is an ILLEGAL query: only one word within the included bracket
#                  _n(*foo~5) is satisfied if NO word ending with 'foo' is found within 5 words distance
# Every search phrase can have multiple Boolean criteria of the same type:
# <keyword>_y(foo|bar~10)_y(xyz~30)_n(abc~12)
# Other criteria:
# Note: Unlike Boolean criteria, each search phrase can contain only one criterion
# of each of the following types:
# _t(<time range>) specifies a time range within which a specific search phrase is 
#                  applied. Unlike the <time range> in the third column (above),
#                  which applies to all search phrases in this line, _t() applies only
#                  to those search phrases to which it is appended. The format is the
#                  same: _t(dd/mm/yy-dd/mm/yy)
# _s(<characters>) specifies character sequences that are NOT permitted as suffixes.
#                  It constrains the suffix truncation. If the characters following a
#                  truncation (*) of a keyword match a specified character sequence,
#                  the word is NOT coded.
#                  multiple sequences are separated by |
#                  EXAMPLES:
#                  _s(s) is satisfied if <word>* does not match <word>s (e.g., aid*_s(s) matches 'aid', 'aiding', 'aided', but not 'aids')
#                  _s(s|ing) is satisfied if <word>* matches neither <word>s nor <word>ing
# Each search phrase is thus a sequence beginning with the keyword and, optionally,
# a number of additional criteria. The next space character begins the next search
# phrase for the same concept. A concept is coded if any of the listed search phrases
# matches a word in the text.
# EXAMPLE:
# 101	Word		word*_s(ing) expression_n(free*~5) term_n(first|second|third|another~5) term*_y(technical~3)
# ...codes concept #101 ('Word') in 'words', 'expression', 'technical terminology' BUT NOT 'wording', 'freedom of expression', or 'second term'
# The dictionary file can contain any number of concepts, each in a separate line (line separator \r\n, column separator \t, search phrases separated by a single space character)
#
# SPECIFIC FOR ARABIC/HEBREW LANGUAGE QUERIES
# Hebrew and Arabic language words are recognized by their word root, which is often
# pre- or suffixed with specific characters (e.g., the prefix 'ו' in Hebrew is
# equivalent to the word 'and'; the suffix 'ים' specifies the masculine plural form).
# The coding function below specifies several such prefixes and suffixes that are
# permitted, so the keyword can match the entire word, or the word with specified
# prefix or suffix (so, for instance, the word 'וחברים' matches the search phrase 
# 'חבר'. Permitted prefixes and suffixes are listed by the list objects mypref1,
# mypref2 and mysuf (below). In Arabic and Hebrew language, the _s and _p (below)
# criteria override this general license for prefixes and suffixes.
# _s(<characters>) specifies character sequences that are NOT permitted as suffixes,
#                  even if they are generally permitted.
# _p(<characters>) specifies character sequences that are NOT permitted as prefixes,
#                  even if they are generally permitted.
#
def importdict(dictionary):
	import codecs
	import re
	import datetime
	dict_file='DICT_'+dictionary+'.txt'
	if len(dictionary)>2:
		language=dictionary[-2:]
	di=codecs.open(dict_file,encoding='utf-8')
	dict=[]
	n=1
	for line in di:
		n=n+1
		line=line.replace('\n','').replace('\r','')
		line=line.strip()
		id, name, time, searchphrase = line.split('\t')
		if not time=='':
			time=time.split('-')
			timefrom=time[0].split('/')
			timefrom=datetime.date(int('20'+timefrom[2]),int(timefrom[1]),int(timefrom[0])).isoformat()
			timeto=time[1].split('/')
			timeto=datetime.date(int('20'+timeto[2]),int(timeto[1]),int(timeto[0])).isoformat()
			time=[timefrom,timeto]
		if language=='MA': # brings all spellings into one character space
			searchphrase=re.sub(r'c(?!h)','ts',searchphrase)
			searchphrase=searchphrase.replace('č','ch').replace('dzh','dj').replace('ẑ','dz').replace('ž','zh').replace('ǵ','gj').replace('đ','gj').replace('ǰ','j').replace('ḱ','kj').replace('ć','kj').replace('dž','dj').replace('š','sh')
			searchphrase=searchphrase.replace('а','a').replace('б','b').replace('в','v').replace('г','g').replace('д','d').replace('ѓ','gj').replace('е','e').replace('ж','zh').replace('з','z').replace('ѕ','dz').replace('и','i').replace('ј','j').replace('к','k').replace('л','l').replace('љ','lj').replace('м','m').replace('н','n').replace('њ','nj').replace('о','o').replace('п','p').replace('р','r').replace('с','s').replace('т','t').replace('ќ','kj').replace('у','u').replace('ф','f').replace('х','h').replace('ц','ts').replace('ч','ch').replace('џ','dj').replace('ш','sh')
		elif language=='SR': # brings all spellings into one character space
			searchphrase=re.sub(r'c(?!h)','ts',searchphrase)
			searchphrase=searchphrase.replace('č','ch').replace('ž','zh').replace('ć','kj').replace('đ','dj').replace('dž','dj').replace('š','sh')
			searchphrase=searchphrase.replace('а','a').replace('б','b').replace('в','v').replace('г','g').replace('д','d').replace('ђ','gj').replace('е','e').replace('ж','zh').replace('з','z').replace('и','i').replace('ј','j').replace('к','k').replace('л','l').replace('љ','lj').replace('м','m').replace('н','n').replace('њ','nj').replace('о','o').replace('п','p').replace('р','r').replace('с','s').replace('т','t').replace('ћ','kj').replace('у','u').replace('ф','f').replace('х','h').replace('ц','ts').replace('ч','č').replace('џ','dj').replace('ш','sh')
		elif language=='FR': # does NOT strip special characters and accents
			searchphrase=searchphrase.lower().replace('œ','oe').replace('æ','ae').replace('ï','i').replace('ü','u').replace('ÿ','y')
		elif language=='AL': # strips special characters and accents
			searchphrase=searchphrase.replace('ë','e#')
			searchphrase=searchphrase.replace('e#','ë')
		elif language=='AR' or language=='HE':
			searchphrase=searchphrase.replace('\"','"').replace('\'','"').replace('أ','ا').replace('إ','ا').replace('آ','اا')
			if language=='AR':
				searchphrase=searchphrase.replace('١','1').replace('٢','2').replace('٣','3').replace('٤','4').replace('٥','5').replace('٦','6').replace('٧','7').replace('٨','8').replace('٩','9').replace('٠','0')
		searchphrase=searchphrase.lower()
		searchphrase=searchphrase.replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ').replace('  ',' ')
		queries=searchphrase.strip().split(' ')
		for query in queries:
			stime=''
			notpref=''
			notsuf=''
			if not '_' in query:
				kw=' '+query+' '
				kw=kw.replace('* ','').replace(' *','')
				cr=[]
			else:
				kw=' '+query[:query.find('_')]+' '
				kw=kw.replace('* ','').replace(' *','')
				cr=[]
				criteria=query[query.find('_')+1:].split('_')
				for crit in criteria:
					if crit.startswith('t('):
						stime=crit[2:-1]
						stime=stime.split('-')
						timefrom=stime[0].split('/')
						timefrom=datetime.date(int('20'+timefrom[2]),int(timefrom[1]),int(timefrom[0])).isoformat()
						timeto=stime[1].split('/')
						timeto=datetime.date(int('20'+timeto[2]),int(timeto[1]),int(timeto[0])).isoformat()
						stime=[timefrom,timeto]
					elif crit.startswith('p('):
						notpref=crit[2:-1]
						notpref=notpref.split('|')
					elif crit.startswith('s('):
						notsuf=crit[2:-1]
						notsuf=notsuf.split('|')
					else:
						d=int(crit[crit.rindex('~')+1:crit.rindex(')')])
						if crit.startswith('y('):
							yes=1
						elif crit.startswith('n('):
							yes=0
						else:
							print('error in query phrase',id)
						qp=crit[2:crit.rindex('~')]
						el=[]
						c=0
						while r'(' in qp:
							e1=qp[:qp.rindex(r'(')]
							e2=qp[qp.rindex(r'(')+1:]
							e3=e2[e2.find(r')')+1:]
							e2=e2[:e2.find(r')')]
							if r'&' in e2:
								if not r'|' in e2:
									e2=[1]+e2.split(r'&')
								else:
									e2=e2.split(r'|')
									e2e=[0]
									for e in e2:
										if r'&' in e:
											e2e.append([1]+e.split(r'&'))
										else:
											e2e.append(e)
									e2=e2e
							elif r'|' in e2:
								e2=[0]+e2.split(r'|')
							else:
								print('error in query phrase',id)
							el.append(e2)
							qp=e1+'#'+str(c)+'#'+e3
							c=c+1
							
						if r'&' in qp:
							if not r'|' in qp:
								qp=[1]+qp.split(r'&')
							else:
								qp=qp.split(r'|')
								qp2=[0]
								for e in qp:
									if r'&' in e:
										qp2.append([1]+e.split(r'&'))
									else:
										qp.append(e)
								qp=qp2
						elif r'|' in qp:
							qp=[0]+qp.split(r'|')
						else:
							qp=[0,qp]
						
						el.append(qp)
						for e in range(len(el)):
							for f in range(len(el[e])-1):
								if re.match(r'#\d+#',el[e][f+1]):
									i=int(el[e][f+1].replace('#',''))
									el[e][f+1]=el[i]
								else:
									el[e][f+1]=' '+el[e][f+1]+' '
									el[e][f+1]=el[e][f+1].replace('* ','').replace(' *','')
						criterion=[yes,d,el.pop()]
						cr.append(criterion)
			if not time=='':
				dict.append([id,name,kw,time,cr,[notpref,notsuf]])
			elif not stime=='':
				dict.append([id,name,kw,stime,cr,[notpref,notsuf]])
			else:
				dict.append([id,name,kw,[],cr,[notpref,notsuf]])
	'''
	DICT STRUCTURE:
	[<concept id>, <concept name>, <keyword>, <time>, [([<presence/absence1>, <distance1>, [criterion1]], [<presence/absence2>, <distance2>, [criterion2]]...)]]
	concept id		:	dict[0]
	concept name	:	dict[1]
	keyword			:	dict[2]
	time			:	dict[3]
	Boolean criteria:	dict[4]
	absence/presence:	dict[4][n][0]
	distance		:	dict[4][n][1]
	criterion		:	dict[4][n][2]
	excluded prefix	:	dict[5][0]
	excluded suffix	:	dict[5][1]
	'''
	di.close()
	print(len(dict), 'codephrases read in successfully...')
	return dict

# TOWORDS transforms a raw unicode text string (title, subtitle, text) into a
# tuple of words.
# At the same time, it cleans up many special characters, depending on the language:
# - Cyrillic Serbian (language='SR') or Macedonian ('MA') is transliterated into Roman
#   characters.
# TOWORDS also recognizes sentence and paragraph syntax and replaces it by words. 
# This serves to introduce a penalty toward the coding algorithm: Additional words
# specified in the Boolean queries must be closer if they are located in different
# syntactical units than if they are in the same clause, sentence, or paragraph.
# Comma, Colon and Semicolon are treated as one word each.
# Period, Exclamation Mark, and Question Mark are treated as three words each.
# Paragraph breaks are treated as five words each.
# Dashes, Quotation marks and other punctuation is removed.
# This excludes punctuation that is not used as punctuation: For instance, periods
# within numbers are preserved. In Arabic (language='AR') and Hebrew ('HE'), acronyms
# (\w+\"\w or \w\'\w) are preserved. In English ('EN') and French ('FR'), in-word
# apostrophes are replaced by spaces, so 'I'm' becomes 'I m', or ['I', 'm'] as tuple.
#
def towords(text,language):
	import re
	if text==None:
		text=''
	text=text.lower()+''
	text=text.replace("’","'").replace("‘","'").replace("´","'").replace("`","'")
	text=re.sub('´',"'",text)
	text=text.replace('“','"').replace('”','"').replace('« ','"').replace(' »','"').replace('«','"').replace('»','"')
	text=text.replace('%',' % ').replace('$',' $ ').replace('€',' € ').replace('&',' & ').replace('@',' @ ').replace('#',' # ').replace('*',' * ').replace('(',' ( ').replace(')',' ) ').replace('[',' [ ').replace(']',' ] ').replace('{',' { ').replace('}',' } ')
	text=text.replace('  ',' ').replace('  ',' ').replace('  ',' ')
	text=text.strip()
	if language=='AR': # brings all spellings into one character space
		text=text.replace('ـ','').replace('ס','').replace('؛','').replace('ً','').replace('ٌ','').replace('ٍ','').replace('َ','').replace('ُ','').replace('ِ','').replace('ّ','').replace('ْ','').replace('٠','0').replace('١','1').replace('٢','2').replace('٣','3').replace('٤','4').replace('٥','5').replace('٦','6').replace('٧','7').replace('٨','8').replace('٩','9').replace('ی','ى').replace('پ','ب').replace('چ','غ').replace('ڤ','و').replace('گ','ج').replace('ۆ','و').replace('إ','ا').replace('أ','ا').replace('آ','اا')
		apo=re.compile(r'(?<=\w)[\'\"](?=\w)')
		text=apo.sub('XXACRONYMXX',text)
	elif language=='HE': # brings all spellings into one character space
		apo=re.compile(r'(?<=\w)[\'\"]+(?=\w)')
		text=apo.sub('XXACRONYMXX',text)
	elif language=='MA': # brings all spellings into one character space
		text=re.sub(r'c(?!h)','ts',text)
		text=text.replace('č','ch').replace('dzh','dj').replace('ẑ','dz').replace('ž','zh').replace('ǵ','gj').replace('đ','gj').replace('ǰ','j').replace('ḱ','kj').replace('ć','kj').replace('dž','dj').replace('š','sh')
		text=text.replace('а','a').replace('б','b').replace('в','v').replace('г','g').replace('д','d').replace('ѓ','gj').replace('е','e').replace('ж','zh').replace('з','z').replace('ѕ','dz').replace('и','i').replace('ј','j').replace('к','k').replace('л','l').replace('љ','lj').replace('м','m').replace('н','n').replace('њ','nj').replace('о','o').replace('п','p').replace('р','r').replace('с','s').replace('т','t').replace('ќ','kj').replace('у','u').replace('ф','f').replace('х','h').replace('ц','ts').replace('ч','ch').replace('џ','dj').replace('ш','sh')
#		text=unidecode(unicode(text))
	elif language=='SR': # brings all spellings into one character space
		text=re.sub(r'c(?!h)','ts',text)
		text=text.replace('č','ch').replace('ž','zh').replace('ć','kj').replace('đ','dj').replace('dž','dj').replace('š','sh')
		text=text.replace('а','a').replace('б','b').replace('в','v').replace('г','g').replace('д','d').replace('ђ','gj').replace('е','e').replace('ж','zh').replace('з','z').replace('и','i').replace('ј','j').replace('к','k').replace('л','l').replace('љ','lj').replace('м','m').replace('н','n').replace('њ','nj').replace('о','o').replace('п','p').replace('р','r').replace('с','s').replace('т','t').replace('ћ','kj').replace('у','u').replace('ф','f').replace('х','h').replace('ц','ts').replace('ч','č').replace('џ','dj').replace('ш','sh')
	elif language=='EN': # strips special characters and accents
		text=re.sub('\'s ',' ',text)
		text=re.sub('(?<=\w)\'(?=\w)',' ',text)
	elif language=='FR': # does NOT strip special characters and accents
		text=text.replace('œ','oe').replace('æ','ae').replace('ï','i').replace('ü','u').replace('ÿ','y')
		ap=re.finditer('(?<=\w)\'(?=\w)',text)
		for apo in ap:
			text=text[:apo.start()]+' '+text[apo.start()+1:]
	elif language=='AL': # strips special characters and accents
		text=re.sub('\'s ',' ',text)
		text=re.sub('(?<=\w)\'(?=\w)',' ',text)
		text=text.replace('ë','e#')
		text=text.replace('e#','ë')
	text=re.sub('(?<=[\s\n\r\t])"(?=\w)',' xxlqu ',text)
	text=re.sub('(?<=[\w\d\.\!\?\:\;\,])"(?=[\s\.\!\?\:\;\,])',' xxrqu ',text)
	text=re.sub('(?<=\A)"(?=\w)',' xxlqu ',text)
	text=re.sub('(?<=[\w\d\.\!\?\:\;\,])"(?=\Z)',' xxrqu ',text)
	text=text+' '
	text=text.replace('\n \n','\n').replace('\n\n','\n').replace('\n\n','\n').replace('\n',' xxpar xxx xxx xxx xxx ').replace('\'',' xxapo ').replace('-',' xxdash ').replace('. ',' xxdot xxx xxx ').replace('! ',' xxexc xxx xxx ').replace('? ',' xxque xxx xxx ').replace(', ',' xxcom ').replace(': ',' xxcol ').replace('; ',' xxsem ')
	text=text.replace('xxcol xxpar','xxcolpar xxpar')
	text=text.strip()
	text=re.sub('\s+',' ',text)
	words=re.compile('\s+').split(text)
	if language=='AR' or language=='HE':
		for wd in range(len(words)):
			words[wd]=words[wd].replace('XXACRONYMXX','"')
	return words
	
# JCODE is the main coding script, which applies the criteria laid down in the
# dictionary to the tuples of words obtained from TOWORDS.
# It returns a list of all found concepts, and their word position within the text.
# JCODE handles all languages except Arabic ('AR') and Hebrew ('HE').
def jcode(words,dict,date,adjacent=0):
	import codecs
	import re
	import copy
	import datetime
	suf=[]
	prec=[]
	basestring=str
	found=[]	#This list collects all matched words and entities
	lastfound=''
	lastpos=-1
	classifier=[]
	for w in range(len(words)):
		if not 'xx' in words[w]:
			sw=' '+words[w]+' '
			for q in dict:
				current=q[0]
				if lastfound!=current or lastpos+5<w or adjacent==1:
					if not q[3]==[]:
						fromdate=q[3][0]
						todate=q[3][1]
						if '2099' in q[3][0]:
							if q[3][0]<q[3][1]:
								fromdate=date[:4]+q[3][0][4:]
								todate=date[:4]+q[3][1][4:]
							elif date[:4]+q[3][0][4:]>date:
								fromdate=str(int(date[:4])-1)+q[3][0][4:]
								todate=date[:4]+q[3][1][4:]
							else:
								fromdate=date[:4]+q[3][0][4:]
								todate=str(int(date[:4])+1)+q[3][1][4:]
					itsamatch=0
					nomatch=0
					if q[3]==[] or fromdate<=date<=todate:
						if q[2] in sw:
							myprec=prec
							if not q[5][0]=='':
								for yp in q[5][0]:
									yp=' '+yp+' '
									yp=yp.replace('* ','').replace(' *','')
									myprec=myprec+[yp]
							mysuf=suf
							if not q[5][1]=='':
								for ns in q[5][1]:
									ns=ns+' '
									ns=ns.replace('* ','')
									mysuf=mysuf+[ns]
							if len(mysuf)!=0:
								swtemp=sw[sw.find(q[2])+len(q[2]):]
								for ns in mysuf:
									if swtemp.startswith(ns):
										nomatch=1
							if len(myprec)!=0 and nomatch==0:
								pok=0
								previous=words[w-1]
								for yp in myprec:
									if yp in previous:
										pok=1
								if not pok==1:
									nomatch=1
							if nomatch==0:
								itsamatch=1
						elif q[2][:-1]+'s ' in sw:
							myprec=prec
							if not q[5][0]=='':
								for yp in q[5][0]:
									yp=' '+yp+' '
									yp=yp.replace('* ','').replace(' *','')
									myprec=myprec+[yp]
							mysuf=suf
							if not q[5][1]=='':
								for ns in q[5][1]:
									ns=ns+' '
									ns=ns.replace('* ','')
									mysuf=mysuf+[ns]
							if q[2][-1]==' ' and not 's ' in mysuf:
								if len(myprec)!=0 and nomatch==0:
									pok=0
									previous=words[w-1]
									for yp in myprec:
										if yp in previous:
											pok=1
									if not pok==1:
										nomatch=1
								if nomatch==0:
									itsamatch=1
								
					if itsamatch==1:
						qp=copy.deepcopy(q)
						no=0
						while no==0 and len(qp[4])>0:
							crit=qp[4].pop(0)
							context=''
							if crit[1]>w:
								a=0
							else:
								a=w-crit[1]
							if crit[1]>len(words)-w-1:
								o=len(words)
							else:
								o=w+crit[1]+1
							for p in range(o-a):
								if not p+a==w:
									context=context+' '+words[p+a]
							context=' '+context+' '
							c0=crit[2]
							ok0=0
							no0=0
							while ok0==0 and no0==0 and len(c0)>1:
								c1=c0.pop(1)
								if isinstance(c1,basestring):
									if c0[0]==0:
										if re.search(re.escape(c1),context):
											ok0=1	#WHICH MEANS THAT THE 'OR' CRITERION IS MATCHED
									elif c0[0]==1:
										if not re.search(re.escape(c1),context):
											no0=1	#WHICH MEANS THAT THE 'AND' CRITERION IS NOT MATCHED
								else:
									ok1=0
									no1=0
									while ok1==0 and no1==0 and len(c1)>1:
										c2=c1.pop(1)
										if isinstance(c2,basestring):
											if c1[0]==0:
												if re.search(re.escape(c2),context):
													ok1=1	#WHICH MEANS THAT THE 'OR' CRITERION IS MATCHED
											elif c1[0]==1:
												if not re.search(re.escape(c2),context):
													no1=1	#WHICH MEANS THAT THE 'AND' CRITERION NOT IS MATCHED
										else:
											ok2=0
											no2=0
											while ok2==0 and no2==0 and len(c2)>1:
												c3=c2.pop(1)
												if isinstance(c3,basestring):
													if c2[0]==0:
														if re.search(re.escape(c3),context):
															ok2=1	#WHICH MEANS THAT THE 'OR' CRITERION IS MATCHED
													elif c2[0]==1:
														if not re.search(re.escape(c3),context):
															no2=1	#WHICH MEANS THAT THE 'AND' CRITERION NOT IS MATCHED
												else:
													ok3=0
													no3=0
													while ok3==0 and no3==0 and len(c3)>1:
														c4=c3.pop(1)
														if isinstance(c4,basestring):
															if c3[0]==0:
																if re.search(re.escape(c4),context):
																	ok3=1	#WHICH MEANS THAT THE 'OR' CRITERION IS MATCHED
															elif c3[0]==1:
																if not re.search(re.escape(c4),context):
																	no3=1	#WHICH MEANS THAT THE 'AND' CRITERION NOT IS MATCHED
														else:
															ok4=0
															no4=0
															while ok4==0 and no4==0 and len(c4)>1:
																c5=c4.pop(1)
																if isinstance(c5,basestring):
																	if c4[0]==0:
																		if re.search(re.escape(c5),context):
																			ok4=1	#WHICH MEANS THAT THE 'OR' CRITERION IS MATCHED
																	if c4[0]==1:
																		if not re.search(re.escape(c5),context):
																			no4=1	#WHICH MEANS THAT THE 'AND' CRITERION NOT IS MATCHED
																else:
																	print('too many brackets')
															if c4[0]==1 and not no4==1:
																ok4=1
															if c4[0]==0 and not ok4==1:
																no4=1
															if c3[0]==0 and ok4==1:
																ok3=1
															elif c3[0]==1 and no4==1:
																no3=1
													if c3[0]==1 and not no3==1:
														ok3=1
													if c3[0]==0 and not ok3==1:
														no3=1
													if c2[0]==0 and ok3==1:
														ok2=1
													elif c2[0]==1 and no3==1:
														no2=1
											if c2[0]==1 and not no2==1:
												ok2=1
											if c2[0]==0 and not ok2==1:
												no2=1
											if c1[0]==0 and ok2==1:
												ok1=1
											elif c1[0]==1 and no2==1:
												no1=1
									if c1[0]==1 and not no1==1:
										ok1=1
									if c1[0]==0 and not ok1==1:
										no1=1
									if c0[0]==0 and ok1==1:
										ok0=1
									elif c0[0]==1 and no1==1:
										no0=1
							if c0[0]==1 and not no0==1:
								ok0=1
							if c0[0]==0 and not ok0==1:
								no0=1
							if c0[0]==0 and ok0==1: #OR CRITERION MATCHED
								critok=1
							elif c0[0]==1 and no0==0: #AND CRITERION MATCHED
								critok=1
							else:
								critok=0
							if critok==1 and crit[0]==0:	#IF THIS WAS AN ABSENCE CRITERION
								no=1	#TERMINATES THE LOOP WITHOUT CODING
							elif critok==0 and crit[0]==1:	#IF THIS WAS A PRESENCE CRITERION
								no=1	#TERMINATES THE LOOP WITHOUT CODING
								#ELSE, THIS WAS A MATCHED PRESENCE CRITERION OR AN UNMATCHED ABSENCE CRITERION, AND THE LOOP JUST CONTINUES TO THE NEXT CRITERION
						if len(qp[4])==0 and no==0:	#IF IT GETS TO HERE, ALL CRITERIA ARE MATCHED
							found.append([w,qp[0]])	#LISTS THE WORD POSITION AND ENTITY ID
							lastfound=qp[0]
							lastpos=w
	return found
'''
no# REMAINS 0 IF A BRACKET WAS 'OR' OR IF AN 'AND' BRACKET HAS BEEN MATCHED, HENCE c#[0]*(1-no4)=1
ok# BECOMES 1 IF AN 'OR' BRACKET HAS BEEN MATCHED, HENCE (1-c#[0])*ok=1
FOR ALL 'OR' BRACKETS, c#[0]*(1-no4) REMAINS ZERO BECAUSE c#[0] IS ZERO
FOR ALL 'AND' BRACKETS, (1-c#[0])*ok REMAINS ZERO BECAUSE c#[1] IS ONE
IF no# IS 0 AND ok# IS 1, THEREFORE, THE CRITERION OF THE NEXT HIGHER BRACKED IS MATCHED
IF THE NEXT HIGHER BRACKET IS AN 'OR' BRACKET, ANY MATCHED COMPONENT MATCHES THE BRACKET
IF IT WAS AN 'AND' BRACKET, THE no# CRITERION IS KEPT AT ZERO AND THE TEST CONTINUES
'''

# JCODE_HA is a variant of the main coding script, which applies the criteria laid
# down in the dictionary to the tuples of words obtained from TOWORDS.
# It returns a list of all found concepts, and their word position within the text.
# JCODE handles the languages Arabic ('AR') and Hebrew ('HE').
# The main difference is that these two languages use prefixes to express many
# conjunctions and articles, so the algorithm allows for certain prefixes to appear
# before the keyword. It also allows specific regular suffixes. Both are defined as
# mypref1 (one-character prefixes), mypref2 (multi-character prefixes), and mysuf (suffixes).
# mypreq specifies those prefixes allowed for terms within the Boolean query, which
# is more restrictive than the list of keyword prefixes.
def jcode_ha(words,dict,date,lang,adjacent=0):
	import codecs
	import re
	import copy
	import datetime
	basestring=str
	found=[]	#This file collects all matched words and entities
	lastfound=''
	classifier=[]
	for w in range(len(words)):
		if not 'xx' in words[w]:
			sw=' '+words[w]+' ' ## ' searchword '
			for q in dict:
				current=q[0]
				if lastfound!=current or lastpos+5<w or adjacent==1:
					if not q[3]==[]:
						fromdate=q[3][0]
						todate=q[3][1]
						if '2099' in q[3][0]:
							if q[3][0]<q[3][1]:
								fromdate=date[:4]+q[3][0][4:]
								todate=date[:4]+q[3][1][4:]
							elif date[:4]+q[3][0][4:]>date:
								fromdate=str(int(date[:4])-1)+q[3][0][4:]
								todate=date[:4]+q[3][1][4:]
							else:
								fromdate=date[:4]+q[3][0][4:]
								todate=str(int(date[:4])+1)+q[3][1][4:]
					if lang=='AR':
						mypref1='فمكبولتينل'
						mypref2=['ال','لل','فال'] #بال
						mysuf=['ان ','ين ','ية ','ة ','كن ','ها ','هم ','ه ','ك ','كم ','ي ','وا ','ن ','ت ','تم ','تن ','نا ','ون ','ا']
						mypreq='(?:[فمكبولتينل])?(?:ال)?(?:لل)?'
					elif lang=='HE':
						mypref1='ובכלמהשאיתנ'
						mypref2=['מה']
						mysuf=['ים ','ות ','י ','כ ','ו ','נו ','הם ','הן ','כם ','כן ','ה ','תי ','תם ','תן ','ת ','ך ','ן ','ם ','ית ']
						mypreq='(?:[וש])?(?:[בכלמהאיתנ])?'
					notpref=''
					if q[5][0]=='*':
						mypref1=''
						mypref2=''
						notpref='غظضذخثتشرقصفعسنملكيطحزوهدجباאבגדהוזחטיכךלמםנןסעפףצץקרשת'
					elif not q[5][0]=='':
						for nop in q[5][0]:
							notpref=notpref+nop
							mypref1=mypref1.replace(nop,'')
							pl=len(mypref2)
							for pp in range(pl):
								if nop in mypref2[pl-pp-1]:
									mypref2.pop(pl-pp-1)
					notsuf=''
					if q[5][1]=='*':
						mysuf=''
						notsuf='غظضذخثتشرقصفعسنملكيطحزوهدجباאבגדהוזחטיכךלמםנןסעפףצץקרשת'
					if not q[5][1]=='':
						for nos in q[5][1]:
							notsuf=notsuf+nos
							sl=len(mysuf)
							for ss in range(sl):
								if mysuf[sl-ss-1]==nos:
									mysuf.pop(sl-ss-1)
					
					itsamatch=0
					if q[3]==[] or fromdate<=date<=todate:
						if q[2].strip() in sw:
							if q[2] in sw:
								itsamatch=1	# REGISTERS IF KEYWORD = SEARCHWORD OR IF KEYW* => SEARCHWORD
							elif q[2] in ' '+sw[2:]:
								if sw[1] in mypref1:
									itsamatch=1	# REGISTERS IF 1-LETTER-PREFIX+KEYWORD = SEARCHWORD OR IF 1-LETTER-PREFIX+KEYW => SEARCHWORD
							elif q[2] in ' '+sw[3:]:
								for prf2 in mypref2:
									if len(prf2)==2:
										if sw[1:3]==prf2:
											itsamatch=1	# REGISTERS IF DOUBLEPREFIX+KEYWORD = SEARCHWORD OR IF DOUBLEPREFIX+KEYW => SEARCHWORD
								if itsamatch==0:
									if sw[1] in 'וש':
										if sw[2] in mypref1.replace('ש','').replace('ו',''):
											itsamatch=1	# REGISTERS IF DOUBLEPREFIX+KEYWORD = SEARCHWORD OR IF DOUBLEPREFIX+KEYW => SEARCHWORD
							elif q[2] in ' '+sw[4:]:
								for prf2 in mypref2:
									if len(prf2)==3:
										if sw[1:4]==prf2:
											itsamatch=1	# REGISTERS IF DOUBLEPREFIX+KEYWORD = SEARCHWORD OR IF DOUBLEPREFIX+KEYW => SEARCHWORD
							elif q[2][:-1] in sw: 
								if sw[sw.find(q[2][:-1])+len(q[2][:-1]):] in mysuf:
									if not sw[sw.find(q[2][:-1])+len(q[2][:-1]):] in notsuf:
										itsamatch=1	# REGISTERS IF KEYWORD+SUFFIX = SEARCHWORD OR IF *KEYWORD+SUFFIX => SEARCHWORD
							elif q[2][:-1] in ' '+sw[2:]:
								if sw[1] in mypref1:
									if sw[sw.find(q[2][:-1])+len(q[2][:-1]):] in mysuf:
										if not sw[sw.find(q[2][:-1])+len(q[2][:-1]):] in notsuf:
											itsamatch=1	# REGISTERS IF PREFIX+KEYWORD+SUFFIX = SEARCHWORD
							elif q[2][:-1] in ' '+sw[3:]:
								for prf2 in mypref2:
									if sw[1:3]==prf2:
										if len(prf2)==2:
											if sw[sw.find(q[2][:-1])+len(q[2][:-1]):] in mysuf:
												if not sw[sw.find(q[2][:-1])+len(q[2][:-1]):] in notsuf:
													itsamatch=1	# REGISTERS IF DOUBLEPREFIX+KEYWORD+SUFFIX = SEARCHWORD
								if itsamatch==0:
									if sw[1] in 'וש':
										if sw[2] in mypref1.replace('ש','').replace('ו',''):
											if sw[sw.find(q[2][:-1])+len(q[2][:-1]):] in mysuf:
												if not sw[sw.find(q[2][:-1])+len(q[2][:-1]):] in notsuf:
													itsamatch=1	# REGISTERS IF DOUBLEPREFIX+KEYWORD+SUFFIX = SEARCHWORD
							elif q[2][:-1] in ' '+sw[4:]:
								for prf2 in mypref2:
									if len(prf2)==3:
										if sw[1:3]==prf2:
											if sw[sw.find(q[2][:-1])+len(q[2][:-1]):] in mysuf:
												if not sw[sw.find(q[2][:-1])+len(q[2][:-1]):] in notsuf:
													itsamatch=1	# REGISTERS IF DOUBLEPREFIX+KEYWORD+SUFFIX = SEARCHWORD
					if itsamatch==1:
						qp=copy.deepcopy(q)
						no=0
						while no==0 and len(qp[4])>0:
							crit=qp[4].pop(0)
							context=''
							if crit[1]>w:
								a=0
							else:
								a=w-crit[1]
							if crit[1]>len(words)-w:
								o=len(words)
							else:
								o=w+crit[1]
							for p in range(o-a):
								if not p+a==w:
									context=context+' '+words[p+a]
							context=' '+context+' '
							c0=crit[2]
							ok0=0
							no0=0
							while ok0==0 and no0==0 and len(c0)>1:
								c1=c0.pop(1)
								if isinstance(c1,basestring):
									if c0[0]==0:
										if re.search(r' '+mypreq+re.escape(c1.strip()),context):
											ok0=1	#WHICH MEANS THAT THE 'OR' CRITERION IS MATCHED
									elif c0[0]==1:
										if not re.search(r' '+mypreq+re.escape(c1.strip()),context):
											no0=1	#WHICH MEANS THAT THE 'AND' CRITERION IS NOT MATCHED
								else:
									ok1=0
									no1=0
									while ok1==0 and no1==0 and len(c1)>1:
										c2=c1.pop(1)
										if isinstance(c2,basestring):
											if c1[0]==0:
												if re.search(r' '+mypreq+re.escape(c2.strip()),context):
													ok1=1	#WHICH MEANS THAT THE 'OR' CRITERION IS MATCHED
											elif c1[0]==1:
												if not re.search(r' '+mypreq+re.escape(c2.strip()),context):
													no1=1	#WHICH MEANS THAT THE 'AND' CRITERION NOT IS MATCHED
										else:
											ok2=0
											no2=0
											while ok2==0 and no2==0 and len(c2)>1:
												c3=c2.pop(1)
												if isinstance(c3,basestring):
													if c2[0]==0:
														if re.search(r' '+mypreq+re.escape(c3.strip()),context):
															ok2=1	#WHICH MEANS THAT THE 'OR' CRITERION IS MATCHED
													elif c2[0]==1:
														if not re.search(r' '+mypreq+re.escape(c3.strip()),context):
															no2=1	#WHICH MEANS THAT THE 'AND' CRITERION NOT IS MATCHED
												else:
													ok3=0
													no3=0
													while ok3==0 and no3==0 and len(c3)>1:
														c4=c3.pop(1)
														if isinstance(c4,basestring):
															if c3[0]==0:
																if re.search(r' '+mypreq+re.escape(c4.strip()),context):
																	ok3=1	#WHICH MEANS THAT THE 'OR' CRITERION IS MATCHED
															elif c3[0]==1:
																if not re.search(r' '+mypreq+re.escape(c4.strip()),context):
																	no3=1	#WHICH MEANS THAT THE 'AND' CRITERION NOT IS MATCHED
														else:
															ok4=0
															no4=0
															while ok4==0 and no4==0 and len(c4)>1:
																c5=c4.pop(1)
																if isinstance(c5,basestring):
																	if c4[0]==0:
																		if re.search(r' '+mypreq+re.escape(c5.strip()),context):
																			ok4=1	#WHICH MEANS THAT THE 'OR' CRITERION IS MATCHED
																	if c4[0]==1:
																		if not re.search(r' '+mypreq+re.escape(c5.strip()),context):
																			no4=1	#WHICH MEANS THAT THE 'AND' CRITERION NOT IS MATCHED
																else:
																	print('too many brackets')
															if c4[0]==1 and not no4==1:
																ok4=1
															if c4[0]==0 and not ok4==1:
																no4=1
															if c3[0]==0 and ok4==1:
																ok3=1
															elif c3[0]==1 and no4==1:
																no3=1
													if c3[0]==1 and not no3==1:
														ok3=1
													if c3[0]==0 and not ok3==1:
														no3=1
													if c2[0]==0 and ok3==1:
														ok2=1
													elif c2[0]==1 and no3==1:
														no2=1
											if c2[0]==1 and not no2==1:
												ok2=1
											if c2[0]==0 and not ok2==1:
												no2=1
											if c1[0]==0 and ok2==1:
												ok1=1
											elif c1[0]==1 and no2==1:
												no1=1
									if c1[0]==1 and not no1==1:
										ok1=1
									if c1[0]==0 and not ok1==1:
										no1=1
									if c0[0]==0 and ok1==1:
										ok0=1
									elif c0[0]==1 and no1==1:
										no0=1
							if c0[0]==1 and not no0==1:
								ok0=1
							if c0[0]==0 and not ok0==1:
								no0=1
							if c0[0]==0 and ok0==1: #OR CRITERION MATCHED
								critok=1
							elif c0[0]==1 and no0==0: #AND CRITERION MATCHED
								critok=1
							else:
								critok=0
							if critok==1 and crit[0]==0:	#IF THIS WAS AN ABSENCE CRITERION
								no=1	#TERMINATES THE LOOP WITHOUT CODING
							elif critok==0 and crit[0]==1:	#IF THIS WAS A PRESENCE CRITERION
								no=1	#TERMINATES THE LOOP WITHOUT CODING
								#ELSE, THIS WAS A MATCHED PRESENCE CRITERION OR AN UNMATCHED ABSENCE CRITERION, AND THE LOOP JUST CONTINUES TO THE NEXT CRITERION
						if len(qp[4])==0 and no==0:	#IF IT GETS TO HERE, ALL CRITERIA ARE MATCHED
							found.append([w,qp[0]])	#LISTS THE WORD POSITION AND ENTITY ID
							lastfound=qp[0]
	return found
'''
no# REMAINS 0 IF A BRACKET WAS 'OR' OR IF AN 'AND' BRACKET HAS BEEN MATCHED, HENCE c#[0]*(1-no4)=1
ok# BECOMES 1 IF AN 'OR' BRACKET HAS BEEN MATCHED, HENCE (1-c#[0])*ok=1
FOR ALL 'OR' BRACKETS, c#[0]*(1-no4) REMAINS ZERO BECAUSE c#[0] IS ZERO
FOR ALL 'AND' BRACKETS, (1-c#[0])*ok REMAINS ZERO BECAUSE c#[1] IS ONE
IF no# IS 0 AND ok# IS 1, THEREFORE, THE CRITERION OF THE NEXT HIGHER BRACKED IS MATCHED
IF THE NEXT HIGHER BRACKET IS AN 'OR' BRACKET, ANY MATCHED COMPONENT MATCHES THE BRACKET
IF IT WAS AN 'AND' BRACKET, THE no# CRITERION IS KEPT AT ZERO AND THE TEST CONTINUES
'''

# The following functions operate on the list of recognized concepts, and serve to
# generate specific kinds of output.

# E_ANNOTATE uses the tuple of words obtained from TOWORDS, the list of recognized
# concepts obtained from JCODE/JCODE_HA, and the concept names and ids obtained from
# IMPORTDICT to return a string wherein each recognized word is appended a bracket
# specifying which concept has been recognized.
# EXAMPLE:
# from the text 'I think, therefore I am confused.', represented as ['I','think','xxcom','therefore','I','am', 'confused', 'xxdot', 'xxx', 'xxx']
# the query '101	Think		think*_n(pad~2)\r\n102	Myself		I'
# JCODE will return three hits [[0,'102'],[1,'101'],[4,'102']]
# resulting in the text 'I(Myself) think(Think), therefore I(Myself) am confused.'.
def e_annotate(words,found,dict):
	import re
	text=''
	for w in range(len(words)):
		word=words[w]+' '
		for hit in found:
			if hit[0]==w:
				word=word[:-1]+'('+dict[hit[1]]+') '
		text=text+word
	text=text.replace('xxx','').replace(' yydot ','. ').replace('yyy','').replace(' xxpar ','\n').replace(' xxdot ','. ').replace(' xxexc ','! ').replace(' xxque ','? ').replace(' xxcom ',', ').replace(' xxcol ',': ').replace('xxcolpar',': ').replace(' xxsem ','; ').replace(' xxquot ',' " ').replace(' xxapo ',"'").replace(' xxdash ',' - ')
	text=text.replace('xxx','').replace(' yydot ','. ').replace('yyy','').replace(' xxpar ','\n').replace('yypar','|').replace(' xxdot ','. ').replace(' xxexc ','! ').replace(' xxque ','? ').replace(' xxcom ',', ').replace(' xxcol ',': ').replace(' xxsem ','; ').replace('xxapo',"'").replace(' xxdash ',' - ').replace(' xxlqu ','“')
	text=text.replace('xxrqu','”')
	text=text.replace('“ ','“').replace(' ”','”')
	text=text.replace('“ ','“').replace(' ”','”')
	text=text.replace('“|','|“').replace('|”','”|')
	text=text.replace('“>>>','>>> “').replace('<<<”','” <<<').replace('“<<<','<<< “').replace('>>>”','” >>>')
	text=text.replace('“ ','“').replace(' ”','”')
	text=re.sub(r'\s+',' ',text)
	text=text.strip()
	return text

# E_REPLACE uses the list of recognized in a text to simply list all recognized concept ids, separated by spaces.
# EXAMPLE:
# the above example will return '102 101 102'	
def e_replace(found):
	import re
	text=''
	for hit in found:
		text=text+hit[1]+' '
	text=re.sub(r'\s+',' ',text)
	return text

# E_KWIC uses the tuple of words obtained from TOWORDS, the id and position of a
# recognized concept obtained from JCODE/JCODE_HA, and the concept names and ids
# obtained from IMPORTDICT to return a sequence of string of the recognized keyword
# in context (of b words before and after).
# EXAMPLE:
# for b=2, the above example will return
# ['102', 'Myself', '', 'I', 'think,'] for the first hit (note, the comma counts as one word)
# ['101', 'Think', 'I', 'think', ', therefore'] for the second hit
# ['102', 'Myself', ', therefore', 'I', 'am confused'] for the third hit.
def e_kwic(hit,b,words,dict):
	kw=words[hit[0]]
	if hit[0]<b:
		a=0
	else:
		a=hit[0]-b
	before=''
	for p in range(hit[0]-a):
		before=before+words[a+p]+' '
	if hit[0]+b+1>len(words):
		o=len(words)-2
	else:
		o=hit[0]+b
	after=''
	for p in range(o-hit[0]):
		after=after+words[hit[0]+p+1]+' '
	kwic=[hit[1],dict[hit[1]],before,kw,after]
	return kwic