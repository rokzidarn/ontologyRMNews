import nltk
import re
import os

def fileRead(filename):
    with open("news/"+filename, 'r') as text:
        text = text.read()
    return text

def filterText(text):
    regex = "((<.*?>)|(<\\.*?>))"
    filtered = re.sub(regex, "", text)
    return filtered

def getNewsgroups(text):
    regex = "Newsgroups: .*"
    pattern = re.compile(regex)
    match = pattern.search(text)  # matches = re.finditer(regex, text)
    if(match != None):
        match = match.group(0)[12:].split(',')
    else:
        match = "Unknown"
    return match

def getPerson(text):
    regex = "From: .*"
    pattern = re.compile(regex)
    match = pattern.search(text)
    if(match != None):
        match = match.group(0)[5:]
    else:
        return ["Unknown", "Unknown", "Unknown"]

    regexEmail = "[a-zA-Z0-9]*@[a-zA-Z.0-9]*"
    pattern = re.compile(regexEmail)
    email = pattern.search(match)
    if(email != None):
        email = email.group(0)
    else:
        email = "Unknown"

    regexName = "\(.*\)"
    pattern = re.compile(regexName)
    name = pattern.search(match)
    if(name != None):
        name = name.group(0)
        name = name[1:len(name)-1]
        first_name = name.split(' ', 1)[0]
        last_name = name.split(' ', 1)[1]
    else:
        first_name = "Unknown"
        last_name = "Unknown"

    return [first_name, last_name, email]

def getSubject(text):
    regex = "Subject: .*"
    pattern = re.compile(regex)
    match = pattern.search(text)
    if(match != None):
        match = match.group(0)[9:]
    else:
        match = "Unknown"
    return match

def getDistribution(text):
    regex = "Distribution: .*"
    pattern = re.compile(regex)
    match = pattern.search(text)
    if(match != None):
        match = match.group(0)[13:]  # print(match)
    else:
        match = "Unknown"
    return match

def getOrganization(text):
    regex = "Organization: .*"
    pattern = re.compile(regex)
    match = pattern.search(text)
    if(match != None):
        match = match.group(0)[14:]
    else:
        match = "Unknown"
    return match

def getNumberOfLines(text):
    regex = "Lines: \d*"
    pattern = re.compile(regex)
    match = pattern.search(text)
    if(match != None):
        match = match.group(0)[7:]
    else:
        match = 0
    return match

def getTimeAndDate(text):
    # regexTime = "(\d{1,2}:\d{1,2})|((\d{1,2}:\d{1,2})\s(PM|p.m))"
    regex = "Date: .*"
    timePattern = re.compile(regex)
    match = timePattern.search(text)
    if(match != None):
        match = match.group(0)[6:]
        splitted = match.split(",")
    else:
        return ["Unkown", "Unkown", "Unkown", "Unkown"]

    if(len(splitted) == 2):
        day = splitted[0]
        splitted = str(splitted[1][1:])
    else:
        splitted = str(splitted[0])
        day = "Unknown"

    dateTime = splitted.split(" ", 3)
    if(dateTime != None):
        date = dateTime[0]+" "+dateTime[1]+" "+dateTime[2]
        timeAndZone = dateTime[3].split(" ")
        time = timeAndZone[0]
        timezone = timeAndZone[1]
    else:
        date = "Unknown"
        time = "Unknown"
        timezone = "Unknown"

    return [day, date, time, timezone]

def getSummary(text):
    regex = "Summary: .*"
    pattern = re.compile(regex)
    match = pattern.search(text)
    if(match != None):
        match = match.group(0)[9:]
    else:
        match = "Unknown"
    return match

def insertPerson(updateGraph, person_class, first_name, last_name, email):
    first_name = "\"" + first_name + "\""
    last_name = "\"" + last_name + "\""
    email = "\"" + email + "\""

    query = """
       PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
       PREFIX owl: <http://www.w3.org/2002/07/owl#>
       PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
       PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
       PREFIX rm: <http://www.semanticweb.org/2016/ontology/rm#>
       INSERT DATA {
           rm:""" + person_class + """ rdf:type rm:Person .
           rm:""" + person_class + """ rm:first_name """ + first_name + """ .
           rm:""" + person_class + """ rm:last_name """ + last_name + """ .
           rm:""" + person_class + """ rm:email """ + email + """  .}"""

    updateGraph.update(query)

def insertOrganization(updateGraph, organization_class, organization_name, distribution):
    organization_name = "\"" + organization_name + "\""
    distribution = "\"" + distribution + "\""

    query = """
       PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
       PREFIX owl: <http://www.w3.org/2002/07/owl#>
       PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
       PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
       PREFIX rm: <http://www.semanticweb.org/2016/ontology/rm#>
       INSERT DATA {
           rm:""" + organization_class + """ rdf:type rm:Organization .
           rm:""" + organization_class + """ rm:name """ + organization_name + """ .
           rm:""" + organization_class + """ rm:distribution """ + distribution + """ .}"""

    updateGraph.update(query)

def insertData(updateGraph, data_class, subject, summary, numberOfLines):
    subject = "\"" + subject + "\""
    summary = "\"" + summary + "\""
    numberOfLines = "\"" + numberOfLines + "\""

    query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX rm: <http://www.semanticweb.org/2016/ontology/rm#>
        INSERT DATA {
            rm:""" + data_class + """ rdf:type rm:Data .
            rm:""" + data_class + """ rm:subject """ + subject + """ .
            rm:""" + data_class + """ rm:summary """ + summary + """ .
            rm:""" + data_class + """ rm:number_of_lines """ + numberOfLines + """ .}"""

    updateGraph.update(query)

def insertNewsgroup(updateGraph, newsgroup_class, newsgroup_name):
    newsgroup_name = "\"" + newsgroup_name + "\""

    query = """
       PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
       PREFIX owl: <http://www.w3.org/2002/07/owl#>
       PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
       PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
       PREFIX rm: <http://www.semanticweb.org/2016/ontology/rm#>
       INSERT DATA {
          rm:""" + newsgroup_class + """ rdf:type rm:Newsgroup .
          rm:""" + newsgroup_class + """ rm:name """ + newsgroup_name + """ .}"""

    updateGraph.update(query)

def insertDate(updateGraph, date_class, date, day):
    date = "\"" + date + "\""
    day = "\"" + day + "\""

    query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX rm: <http://www.semanticweb.org/2016/ontology/rm#>
        INSERT DATA {
            rm:""" + date_class + """ rdf:type rm:Date .
            rm:""" + date_class + """ rm:date """ + date + """ .
            rm:""" + date_class + """ rm:day """ + day + """ .}"""

    updateGraph.update(query)

def insertTime(updateGraph, time_class, time, timezone):
    time = "\"" + time + "\""
    timezone = "\"" + timezone + "\""

    query = """
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
        PREFIX rm: <http://www.semanticweb.org/2016/ontology/rm#>
        INSERT DATA {
            rm:""" + time_class + """ rdf:type rm:Time .
            rm:""" + time_class + """ rm:time """ + time + """ .
            rm:""" + time_class + """ rm:timezone """ + timezone + """ .}"""

    updateGraph.update(query)

def createNews(updateGraph, news_class, newsgroup_class, person_class, organization_class, author_class, data_class, date_class, time_class, date_and_time_class):
    query = """
           PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
           PREFIX owl: <http://www.w3.org/2002/07/owl#>
           PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
           PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
           PREFIX rm: <http://www.semanticweb.org/2016/ontology/rm#>
           INSERT DATA {
               rm:""" + author_class + """ rdf:type rm:Author .
               rm:""" + author_class + """ rm:is rm:""" + person_class + """ .
               rm:""" + author_class + """ rm:works_for rm:""" + organization_class + """ .

               rm:""" + date_and_time_class + """ rdf:type rm:Time_and_Date .
               rm:""" + date_and_time_class + """ rm:at rm:""" + time_class + """ .
               rm:""" + date_and_time_class + """ rm:on rm:""" + date_class + """ .

               rm:""" + news_class + """ rdf:type rm:News .
               rm:""" + news_class + """ rm:posted_on rm:""" + date_and_time_class + """ .
               rm:""" + news_class + """ rm:posted_by rm:""" + author_class + """ .
               rm:""" + news_class + """ rm:has rm:""" + data_class + """ .
               rm:""" + news_class + """ rm:part_of rm:""" + newsgroup_class + """ .}"""

    #print(query)
    updateGraph.update(query)

# ------------------------------------------------ MAIN

for f in os.listdir(os.getcwd()+"/news"):
    text = fileRead(f)

    news_class = f
    newsgroup_name = getNewsgroups(text)[0]
    newsgroup_class = newsgroup_name.replace(".", "_")

    person = getPerson(text)
    first_name = person[0]
    last_name = person[1]
    email = person[2]
    person_class = first_name.replace(" ", "_").replace(".", "_").replace("-", "_")+"_"+last_name.replace(" ", "_").replace(".", "")
    distribution = getDistribution(text)
    organization_name = getOrganization(text)
    organization_class = "".join(e for e in organization_name if e.isalnum())
    author_class = person_class+"_"+organization_class

    subject = getSubject(text)
    numberOfLines = str(getNumberOfLines(text))
    summary = getSummary(text)
    data_class = "".join(e for e in (numberOfLines+"_"+subject) if e.isalnum())

    timeAndDate = getTimeAndDate(text)
    day = timeAndDate[0]
    date = timeAndDate[1]
    date_class = date.replace(" ", "_")
    time = timeAndDate[2]
    timezone = timeAndDate[3]
    time_class = time.replace(":", "_")
    date_and_time_class = date_class+"_"+time_class

    # FUSEKI
    from rdflib.plugins.stores.sparqlstore import SPARQLUpdateStore
    from rdflib.graph import ConjunctiveGraph

    updateStore = SPARQLUpdateStore("http://localhost:3030/RM/update")
    # updateStore = SPARQLUpdateStore("http://localhost:3030/store/update")
    updateGraph = ConjunctiveGraph(store=updateStore)

    insertPerson(updateGraph, person_class, first_name, last_name, email)
    insertOrganization(updateGraph, organization_class, organization_name, distribution)
    insertData(updateGraph, data_class, subject, summary, numberOfLines)
    insertNewsgroup(updateGraph, newsgroup_class, newsgroup_name)
    insertDate(updateGraph, date_class, date, day)
    insertTime(updateGraph, time_class, time, timezone)
    createNews(updateGraph, news_class, newsgroup_class, person_class, organization_class, author_class, data_class, date_class, time_class, date_and_time_class)
