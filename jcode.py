#!/usr/bin/env python
# -*- coding: utf-8 -*-

###########################################################################
#                                                                         #
#                           (c) Christian Baden                           #
#             The Hebrew University of Jerusalem, Israel, 2016            #
#                                                                         #
# Please cite as:                                                         #
#        Baden, Christian & Stalpouskaya, Katsiaryna (2015). Common       #
#        methodological framework: Content analysis. A mixed-methods      #
#        strategy for comparatively, diachronically analyzing conflict    #
#        discourse. INFOCORE Working Paper 2015/10.                       #
#        http://www.infocore.eu/results/                                  #
#                                                                         #
# This file is part of JAmCAT, the Jerusalem AmCAT Server:                #
#        http://jamcat.mscc.huji.ac.il                                    #
#                                                                         #
# JCODE is the JAmCAT coding script, which requires the library JAMCODE.  #
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
# JAmCAT and AmCAT are free software: you can redistribute it and/or      #
# modify it under the terms of the GNU Lesser General Public License as   #
# published by the Free Software Foundation, either version 3 of the      #
# License, or (at your option) any later version.                         #
#                                                                         #
# Both are distributed in the hope that it will be useful, but WITHOUT    #
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or   #
# FITNESS FOR A PARTICULAR PURPOSE. See the GNU Affero General Public     #
# License for more details.                                               #
#                                                                         #
###########################################################################

# JCODE accesses the JAmCAT server to obtain a set of document, loads one or multiple
# dictionaries called DICT_<name>.txt containing complex Boolean search phrases,
# codes the obtained texts according to the dictionaries, and exports the recognized
# concepts into a results file, a term document matrix, and several optional 
# additional files.
#
# CALL AS:
# jcode.py <JAmCAT project id> <set id> <dictionary name> <user id> <password> <options>
#
# Where:
# <JAmCAT project id> and <set id> specify a document set stored on the JAmCAT server
# <dictionary name> is the <name> of the dictionary file DICT_<name>.txt containing
#   the coding instructions (see JAMCODE for details)
#   <name> can be any name given to the dictionary file; BUT as JAMCODE already
#   includes several cleanup procedures for text in English ('EN'), French ('FR'),
#   German ('DE'), Albanian ('AL'), Serbian ('SR'), Macedonian ('MA'), Arabic ('AR')
#   and Hebrew ('HE'), these procedures are only applied if the dictionary name is
#   EN, FR, DE, AL, SR, MA, AR, or HE, respectively.
#   In any case, one specified dictionary is applied to all texts in the set.
#   Alternatively, you can also state INDEX as dictionary. In this case, JCODE
#   searches for a file called 'lang_index_<JAmCAT project id>_<set id>.csv'
#   in the python folder, wherein each line <document id>,<dictionary name> specifies
#   which out of multiple dictionaries is to be used for each document.
# <user id> and <password> are the JAmCAT user credentials
# <options> are:
# s OR e (required): style of the term document matrix:
#                    s=simple: first row states concept ids, not names; first column states document ids
#                    e=extended: first two rows state concept ids and concept names; first columns state the document id, date, and medium
# a (optional): a=annotated, generates an optional additional output file, which contains each raw text annotated for all recognized concept names (see JAMCODE for details; warning, slows down the script considerably and generates big files)
# r (optional): r=replaced, generates an optional additional output file, which contains, for each document, one line stating the document id followed by the sequence of all concept ids recognized in this document (see JAMCODE for details)
# k (optional): k=keywords-in-context, generates an optional additional output file, which lists, for each concept, all found instances within their original context
# from<document id> (optional): commences the coding not from the first document in the set, but the first with an id larger than the specified number.
#
# OUTPUT:
# results_<JAmCAT project id>_<set id>.txt
# file contents: <document id>,<word position>,<concept id>
# where word positions are prefixed 't' for title, 's' for subtitle, 'a' for article
# td_<JAmCAT project id>_<set id>.txt
# (term document matrix)

import sys
from jamcode import *
import codecs
from unidecode import unidecode
import string

reload(sys)
sys.setdefaultencoding('utf-8')

projectid=sys.argv[1]
setid=sys.argv[2]
dictionary=sys.argv[3]
user=sys.argv[4]
pw=sys.argv[5]
options=sys.argv[6:]

startfrom=0
for option in options:
	if option.startswith('from'):
		startfrom=int(option[4:])

annotation=0
replaced=0
simpletd=0
elaboratetd=0
kwics=0
if 'a' in options:
	annotation=1
if 'r' in options:
	replaced=1
if 'k' in options:
	kwics=1
if 's' in options:
	simpletd=1
elif 'e' in options:
	elaboratetd=1

b=5	# bandwidth parameter for the Keywords-in-Context output file, if selected: number of words left and right of the recognized concept
	
texts=gettexts(projectid,setid,user,pw,startfrom)

languages=[]
if dictionary=='INDEX':
	print 'reading index file...'
	lang_index={}
	li=codecs.open('lang_index_'+str(projectid)+'_'+str(setid)+'.csv')
	for line in li:
		artid,language=string.split(string.strip(line),',')
		lang_index[artid]=language
		if language in languages:
			continue
		else:
			languages.append(language)
	li.close()
else:
	languages.append(dictionary)

dicts=[]
for language in languages:
	dict=importdict(language)
	dicts.append(dict)

dc={}
dl=[]
for d in dicts[0]:
	if d[0] in dl:
		continue
	else:
		dl.append(d[0])
		dc[d[0]]=d[1]
dl.sort()

rl=codecs.open('results_'+str(projectid)+'_'+str(setid)+'.txt','wb')
if annotation==1:
	ea=codecs.open('annotated_'+str(projectid)+'_'+str(setid)+'.txt','wb')
if replaced==1:
	er=codecs.open('replaced_'+str(projectid)+'_'+str(setid)+'.txt','wb')
if kwics==1:
	kw=codecs.open('kwic_'+str(projectid)+'_'+str(setid)+'_.txt','wb')
if simpletd==1 or elaboratetd==1:
	td=codecs.open('td_'+str(projectid)+'_'+str(setid)+'.txt','wb')

	if simpletd==1:
		tdhead='id,'
		for item in dl:
			tdhead=tdhead+item+','
		td.write(tdhead[:-1]+'\n')

	if elaboratetd==1:
		tdhead1=',,,'
		tdhead2='id,medium,date,'
		for item in dl:
			tdhead1=tdhead1+dc[item].replace(',',' ')+','
			tdhead2=tdhead2+item+','
		td.write(tdhead1[:-1]+'\n'+tdhead2[:-1]+'\n')

progress=0
for article in texts:
	progress=progress+1
	id,medium,date,title,subtitle,text=article
	if id==startfrom:
		startfrom=0
	elif startfrom==0:
		if dictionary=='INDEX':
			art_lang=lang_index[str(id)]
			art_dict=dicts[languages.index(art_lang)]
		else:
			art_lang=dictionary
			art_dict=dicts[0]
		
		tfound=[]
		sfound=[]
		afound=[]
		print str(progress*100/len(texts))+'%', id, art_lang,
		
		if art_lang=='AR' or art_lang=='HE':
			twords=towords(title,art_lang)
			tfound=jcode_ha(twords,art_dict,date,art_lang)
			print 'found in title:', str(len(tfound))+'/'+str(len(twords))+',',
			swords=towords(subtitle,art_lang)
			sfound=jcode_ha(swords,art_dict,date,art_lang)
			print 'in sub:', str(len(sfound))+'/'+str(len(swords))+',',
			awords=towords(text,art_lang)
			afound=jcode_ha(awords,art_dict,date,art_lang)
			print 'in text:', str(len(afound))+'/'+str(len(awords))+'.'
		else:
			twords=towords(title,art_lang)
			tfound=jcode(twords,art_dict,date)
			print 'found in title:', str(len(tfound))+'/'+str(len(twords))+',',
			swords=towords(subtitle,art_lang)
			sfound=jcode(swords,art_dict,date)
			print 'in sub:', str(len(sfound))+'/'+str(len(swords))+',',
			awords=towords(text,art_lang)
			afound=jcode(awords,art_dict,date)
			print 'in text:', str(len(afound))+'/'+str(len(awords))+'.'

		#EXPORT AS RESULTS LIST
		for f in range(len(tfound)):
			rl.write(str(id)+',t'+str(tfound[f][0])+','+tfound[f][1]+'\n')
		for f in range(len(sfound)):
			rl.write(str(id)+',s'+str(sfound[f][0])+','+sfound[f][1]+'\n')
		for f in range(len(afound)):
			rl.write(str(id)+',a'+str(afound[f][0])+','+afound[f][1]+'\n')
		
		#EXPORT AS ANNOTATED ARTICLES
		if annotation==1:
			ea.write(str(id)+'\t')
			ea.write(e_annotate(twords,tfound,dc)+'\t')
			ea.write(e_annotate(swords,sfound,dc)+'\n')
			ea.write(e_annotate(awords,afound,dc)+'\n\n')

		#EXPORT AS REPLACED TEXTS CONTAINING ONLY THE RECOGNIZED CONCEPT IDS
		if replaced==1:
			er.write(str(id)+'\t')
			er.write(e_replace(tfound)+'\t')
			er.write(e_replace(sfound)+'\t')
			er.write(e_replace(afound)+'\n')
			
		#EXPORT AS KWIC
		if kwics==1:
			instances=[]
			for item in dl:
				instances.append([])

			for tf in tfound:
				kwic=e_kwic(tf,b,twords,dc)
				instances[dl.index(tf[1])].append(kwic)
			for sf in sfound:
				kwic=e_kwic(sf,b,swords,dc)
				instances[dl.index(sf[1])].append(kwic)
			for af in afound:
				kwic=e_kwic(af,b,awords,dc)
				instances[dl.index(af[1])].append(kwic)
			for i in range(len(instances)):
				if instances[i]==[]:
					kw.write(dl[i]+','+dc[dl[i]]+',,,\n')
				else:
					for inst in instances[i]:
						kw.write(inst[0]+','+inst[1]+','+inst[2]+','+inst[3]+','+inst[4]+'\n')
			
		#EXPORT AS TD MATRIX
		if simpletd==1 or elaboratetd==1:
			vector=[]
			for item in dl:
				vector.append(0)
			for tf in tfound:
				vector[dl.index(tf[1])]=vector[dl.index(tf[1])]+1
			for sf in sfound:
				vector[dl.index(sf[1])]=vector[dl.index(sf[1])]+1
			for af in afound:
				vector[dl.index(af[1])]=vector[dl.index(af[1])]+1
			if simpletd==1:
				tdline=str(id)+','
				for v in vector:
					tdline=tdline+str(v)+','
				td.write(tdline[:-1]+'\n')
			if elaboratetd==1:
				tdline=str(id)+','+medium.replace(',',' ')+','+date+','
				for v in vector:
					tdline=tdline+str(v)+','
				td.write(tdline[:-1]+'\n')

rl.close()
if annotation==1:
	ea.close()
if replaced==1:
	er.close()
if kwics==1:
	kw.close()
	kwi=codecs.open('kwic_'+str(projectid)+'_'+str(setid)+'_.txt')
	kwis=[]
	for line in kwi:
		kwis.append(string.strip(line))
	kwi.close()
	kwis.sort()
	kwo=codecs.open('kwic_'+str(projectid)+'_'+str(setid)+'.txt','wb')
	for line in kwis:
		kwo.write(line+'\n')
	kwo.close()
if simpletd==1 or elaboratetd==1:
	td.close()
