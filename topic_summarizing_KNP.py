#! /usr/bin/python
# -*- coding: utf-8 -*-
#
#
#
#
#
# 2015-09-11 tauchi
import json
import codecs
import re
import csv
import os
import sys
import pyknp

title = sys.argv[1]

#ff = codecs.open("fuman_a201508.json","r","utf-8")
ff = codecs.open(title+".json","r","utf-8")
topic_json = json.loads(ff.read().encode("utf-8"))
ff.close()

stop_words = [u"の", u"こと"] # for temporary

knp = pyknp.KNP()

extracted_result = [] #{topicID,topicParameter,sentence,exracted,tokenized}
for topics in topic_json:
    ## マッチした場合のスコア作成
    word_match_score = {}
    for tt in range(0,len(topics[u"wordsInTopic"])):
        if topics[u"wordsInTopic"][tt] not in stop_words:
            word_match_score[topics[u"wordsInTopic"][tt]] = len(topics[u"wordsInTopic"])-tt
    ##
    for sentences in topics[u"sentences"]:
        for ss in re.split("\n|。|！|？|!|\?", sentences.encode('utf-8')):
            ss = unicode(ss,'utf-8')
            try:
                kres = knp.parse(ss.replace(' ',''))
                print "sentence: "+ss
                ii = 0
                for bnst_obj in kres:
                    if bnst_obj.children == []:
                        tmp_res = {}
                        tmp_res[u"topicID"] = topics[u"topicID"]
                        tmp_res[u"topicParameter"] = topics[u"topicParameter"]
                        tmp_res[u"sentence"] = ss
                        tmp_res[u"extracted"] = ""
                        tmp_res[u"tokenized"] = []
                        tmp_res[u"tokenScore"] = 0
                        tmp_res[u"wordsInTopic"] = topics[u"wordsInTopic"]
                        bb = bnst_obj
                        ii += 1
                        while True:
                            rep = ""
                            for mm in bb._mrph_list:
                                tmp_res[u"extracted"] = tmp_res[u"extracted"] + mm.genkei
                                if mm.repname != "":
                                    rep = rep + mm.genkei
                                    tmp_res[u"tokenized"].append(rep)
                            #if word_match_score.has_key(rep):
                            #    tmp_res[u"tokenScore"] = tmp_res[u"tokenScore"]+word_match_score[rep]
                            if bb.parent is None:
                                break
                            bb = bb.parent
                        for ws in word_match_score:
                            if re.search(ws, tmp_res[u"extracted"]):
                                tmp_res[u"tokenScore"] = tmp_res[u"tokenScore"]+word_match_score[ws]
                        extracted_result.append(tmp_res)
            except:
                pass

##
ff = open(title+'_topic_sort_result.csv','wb')
ff.write(','.join(["topicID","topicParameter","sentence","extracted","tokenized","tokenScore","wordsInTopic"]))
ff.write('\n')
for ee in extracted_result:
    ff.write(','.join([str(ee[u"topicID"]),str(ee[u"topicParameter"]),ee[u"sentence"].encode('utf-8'),ee[u"extracted"].encode('utf-8'),' '.join(ee[u"tokenized"]).encode('utf-8'),str(ee[u"tokenScore"]),' '.join(ee[u"wordsInTopic"]).encode('utf-8')]))
    ff.write('\n')

ff.close()
os.system('nkf -s '+title+'_topic_sort_result.csv > '+title+'_topic_sort_result_s.csv')
