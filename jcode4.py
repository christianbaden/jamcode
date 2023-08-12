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

# JCODE accesses the JAmCAT server to obtain a set of document, loads one or multiple
# dictionaries called DICT_<name>.txt containing complex Boolean search phrases,
# codes the obtained texts according to the dictionaries, and exports the recognized
# concepts into a results file, a term document matrix, and several optional 
# additional files.
#
# CALL AS:
# jcode.py <index> <dictionary name> <options>
#
# Where:
# <index> specifies a document set stored on the AmCAT server
# <dictionary name> is the <name> of the dictionary file DICT_<name>.txt containing
#   the coding instructions (see JAMCODE for details)
#   <name> can be any name given to the dictionary file; BUT as JAMCODE already
#   includes several cleanup procedures for text in English ('EN'), French ('FR'),
#   German ('DE'), Albanian ('AL'), Serbian ('SR'), Macedonian ('MA'), Arabic ('AR')
#   and Hebrew ('HE'), these procedures are only applied if the dictionary name is
#   EN, FR, DE, AL, SR, MA, AR, or HE, respectively.
#   In any case, one specified dictionary is applied to all texts in the set.
#   Alternatively, you can also state INDEX as dictionary. In this case, JCODE
#   searches for a file called 'lang_index_<index>.csv'
#   in the python folder, wherein each line <document id>,<dictionary name> specifies
#   which out of multiple dictionaries is to be used for each document.
# <options> are:
# s OR e (required): style of the term document matrix:
#                    s=simple: first row states concept ids, not names; first column states document ids
#                    e=extended: first two rows state concept ids and concept names; first columns state the document id, date, and medium
# a (optional): a=annotated, generates an optional additional output file, which contains each raw text annotated for all recognized concept names (see JAMCODE for details; warning, slows down the script considerably and generates big files)
# r (optional): r=replaced, generates an optional additional output file, which contains, for each document, one line stating the document id followed by the sequence of all concept ids recognized in this document (see JAMCODE for details)
# k (optional): k=keywords-in-context, generates an optional additional output file, which lists, for each concept, all found instances within their original context
#               PLEASE NOTE: By default, this option includes up to five words before and after a coded concept. If the option k is followed by a number, that word distance will be used instead (e.g., "k 10" will use a word distance of 10)
# j (optional): j=adjacent codes permitted: By default, JCODE only records successive instances of the same code if these are separated either by at least five words, or a different code. This is to prevent overlapping coding criteria from registering multiple matches in multi-word expressions multiple times.
#               The option switches off this restraint, such that all matching instances are recorded even if they are adjacent.
# from<document id> (optional): commences the coding not from the first document in the set, but the first with an id larger than the specified number.
#
# OUTPUT:
# results_<index>_<dictionary name>.txt
# file contents: <document id>,<word position>,<concept id>
# where word positions are prefixed 't' for title, 's' for subtitle, 'a' for article

import sys
from jamcode4 import *
import codecs

index=sys.argv[1]
dictionary=sys.argv[2]
options=sys.argv[3:]

startfrom=0
for option in options:
	if option.startswith('from'):
		startfrom=int(option[4:])

annotation=0
replaced=0
simpletd=0
elaboratetd=0
kwics=0
adjacent=0
b=5	# bandwidth parameter for the Keywords-in-Context output file, if selected: number of words left and right of the recognized concept
if 'a' in options:
	annotation=1
if 'r' in options:
	replaced=1
if 'k' in options:
	kwics=1
	if len(options)>options.index('k')+1:
		try:
			b=int(options[options.index('k')+1])
		except:
			print("")
if 's' in options:
	simpletd=1
elif 'e' in options:
	elaboratetd=1
if 'j' in options:
	adjacent=1
	
texts=gettexts(index,startfrom)

languages=[]
if dictionary=='INDEX':
	print('reading index file...')
	lang_index={}
	li=codecs.open('lang_index_'+index+'.csv')
	for line in li:
		artid,language=line.strip().split(',')
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

rl=codecs.open('results_'+index+'_'+str(dictionary)+'.txt',mode='w',encoding='utf-8')
if annotation==1:
	ea=codecs.open('annotated_'+index+'_'+str(dictionary)+'.txt',mode='w',encoding='utf-8')
if replaced==1:
	er=codecs.open('replaced_'+index+'_'+str(dictionary)+'.txt',mode='w',encoding='utf-8')
if kwics==1:
	kw=codecs.open('kwic_'+index+'_'+str(dictionary)+'.txt',mode='w',encoding='utf-8')
if simpletd==1 or elaboratetd==1:
	td=codecs.open('td_'+index+'_'+str(dictionary)+'.txt',mode='w',encoding='utf-8')

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
	if dictionary=='INDEX':
		art_lang=lang_index[str(id)]
		art_dict=dicts[languages.index(art_lang)]
	else:
		art_lang=dictionary
		art_dict=dicts[0]
	
	tfound=[]
	sfound=[]
	afound=[]
	print(str(round(progress*100/len(texts),1))+'%', id, art_lang, end=" ")
	
	if art_lang.endswith('AR') or art_lang.endswith('HE'):
		twords=towords(title,art_lang[-2:])
		tfound=jcode_ha(twords,art_dict,date,art_lang[-2:],adjacent)
		print('found in title:', str(len(tfound))+'/'+str(len(twords))+',', end=" ")
		swords=towords(subtitle,art_lang[-2:])
		sfound=jcode_ha(swords,art_dict,date,art_lang[-2:],adjacent)
		print('in sub:', str(len(sfound))+'/'+str(len(swords))+',', end=" ")
		awords=towords(text,art_lang[-2:])
		afound=jcode_ha(awords,art_dict,date,art_lang[-2:],adjacent)
		print('in text:', str(len(afound))+'/'+str(len(awords))+'.')
	else:
		twords=towords(title,art_lang[-2:])
		tfound=jcode(twords,art_dict,date,adjacent)
		print('found in title:', str(len(tfound))+'/'+str(len(twords))+',', end=" ")
		swords=towords(subtitle,art_lang[-2:])
		sfound=jcode(swords,art_dict,date,adjacent)
		print('in sub:', str(len(sfound))+'/'+str(len(swords))+',', end=" ")
		awords=towords(text,art_lang[-2:])
		afound=jcode(awords,art_dict,date,adjacent)
		print('in text:', str(len(afound))+'/'+str(len(awords))+'.')

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
	kwi=codecs.open('kwic_'+index+'_'+str(dictionary)+'.txt',encoding='utf-8')
	kwis=[]
	for line in kwi:
		kwis.append(line.strip())
	kwi.close()
	kwis.sort()
	kwo=codecs.open('kwic_'+index+'_'+str(dictionary)+'.txt','w',encoding='utf-8')
	for line in kwis:
		kwo.write(line+'\n')
	kwo.close()
if simpletd==1 or elaboratetd==1:
	td.close()