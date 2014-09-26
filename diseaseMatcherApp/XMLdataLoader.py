__author__ = 'Doug'

'''
This program takes the "gold standard" XML file - abstracts and the "correct" answers for disease matches - and loads
then into a local database.
'''

'''
Workplan:
1) build tables to hold "gold standard" answers in models.py
2) syncdb
3) load data from XML to file.
4) Loop on abstracts, populating Abstract object (can I access models.py from here?  I guess if I import it?)
5) In same loop (if possible), populate new answer models.
6) output count of records successfully entered.  Confirm data manually with HeidiSQL.

'''

#import _mysql
import xml.etree.ElementTree as xml
import time
import datetime



import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'diseaseMatcher.settings'


from diseaseMatcherApp.models import Abstract, GoldStandardMatch


#my_conn = _mysql.connect(host="localhost", user="root", passwd="t0blaive", db="diseasematcherdb")

tree = xml.parse("D:/Python27/diseaseMatcher/diseaseMatcher/Aug15_ncbi_dev_bioc.xml")

root = tree.getroot()
abstract_count = 0;

abstract_list = root.findall('document')

#This just cannot be the best way to work with dates, but for now, we got there
pub_date_timeobj = time.strptime(root.find('date').text, "%b. %d %Y")
pub_date = datetime.date(pub_date_timeobj.tm_year, pub_date_timeobj.tm_mon, pub_date_timeobj.tm_mday)


for abstract in abstract_list:

    passages = abstract.findall('passage')

    abstract_id = abstract.find('id').text

    title = "temp title"
    abstract_text = "temp text"
    annotation_list_title = []
    annotation_text_list = []


    for passage in passages:
        if passage.find('infon').text == 'title':
            #we're in the title field
            title = passage.find('text').text
            annotation_list_title = passage.findall('annotation')

        elif passage.find('infon').text == 'abstract':
            #we're in the abstract text
            abstract_text = passage.find('text').text
            annotation_text_list = passage.findall('annotation')

        else:
            #PROBLEM!  But this does not seem to ever happen, so we're doing OK.
            print('Error!  This is not a title or a text.')

    #TODO: Consider get_or_create
    curr_abstract = Abstract.objects.create(abstract_id=abstract_id, abstract_text=abstract_text,
                                            title=title, pub_date=pub_date)
    abstract_count += 1

    for annotation in annotation_list_title:
        #Match in title, MatchLocationsObject pk=1
        annotation_id = annotation.get('id')
        offset = annotation.find('location').get('offset')
        length = annotation.find('location').get('length')
        match_text = annotation.find('text').text
        GoldStandardMatch.objects.create(abstract=curr_abstract, text_matched=match_text, annotation_id=annotation_id,
                                         match_location=1, match_offset=offset,
                                         match_length=length)

    for annotation in annotation_text_list:
        #Match in abstract text, MatchLocationsObject pk=2

        annotation_id = annotation.get('id')
        offset = annotation.find('location').get('offset')
        length = annotation.find('location').get('length')
        match_text = annotation.find('text').text
        GoldStandardMatch.objects.create(abstract=curr_abstract, text_matched=match_text, annotation_id=annotation_id,
                                         match_location=2, match_offset=offset,
                                         match_length=length)



