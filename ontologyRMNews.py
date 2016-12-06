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

# ------------------------------------------------ MAIN

for f in os.listdir(os.getcwd()+"/news"):
    text = fileRead(f)

    filename = f

    newsgroups = getNewsgroups(text)  # list: multiple newsgroups
    newsgroup = newsgroups[0]

    person = getPerson(text)
    first_name = person[0]
    last_name = person[1]
    email = person[2]
    person_name = first_name+"_"+last_name
    distribution = getDistribution(text)
    organization = getOrganization(text)
    author = person_name+"_"+organization

    subject = getSubject(text)
    numberOfLines = str(getNumberOfLines(text))
    summary = getSummary(text)
    data = numberOfLines+"_"+subject

    timeAndDate = getTimeAndDate(text)
    day = timeAndDate[0]
    date = timeAndDate[1]
    time = timeAndDate[2]
    timezone = timeAndDate[3]
    time_timezone = time+"_"+timezone
    date_and_time = date+"_"+time_timezone

    # FUSEKI
    from rdflib.plugins.stores.sparqlstore import SPARQLStore, SPARQLUpdateStore
    from rdflib.graph import ConjunctiveGraph

    iri = "http://www.semanticweb.org/2016/ontology/rm"
    store = SPARQLStore("http://localhost:3030/RM/query")  # queries
    graph = ConjunctiveGraph(store=store)

    updateStore = SPARQLUpdateStore("http://localhost:3030/RM/update")  # insertion
    updateGraph = ConjunctiveGraph(store=updateStore)

    updateGraph.update("""
        PREFIX rm: <http://www.semanticweb.org/2016/ontology/rm#>
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
        PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

        INSERT DATA {
            rm:"""+person_name+""""" rdf:type rm:Person .
            rm:"""+person_name+""""" rm:first_name """+first_name+"""""+^^xsd:string
            rm:"""+person_name+""""" rm:last_name """+last_name+"""""+^^xsd:string
            rm:"""+person_name+""""" rm:email """+email+"""""+^^xsd:string

            rm:"""+organization+""""" rdf:type rm:Organization .
            rm:"""+organization+""""" rm:name """+organization+"""""+^^xsd:string .
            rm:"""+organization+""""" rm:distribution """+distribution+"""""+^^xsd:string .

            rm:"""+time_timezone+""""" rdf:type rm:Time .
            rm:"""+time_timezone+""""" rm:time """+time+"""""+^^xsd:string .
            rm:"""+time_timezone+""""" rm:timezone """+timezone+"""""+^^xsd:string .

            rm:"""+date+""""" rdf:type rm:Date .
            rm:"""+date+""""" rm:date """+date+"""""+^^xsd:string .
            rm:"""+date+""""" rm:day """+day+"""""+^^xsd:string .

            rm:"""+newsgroup+""""" rdf:type rm:Newsgroup .
            rm:"""+newsgroup+""""" rm:name """+newsgroup+"""""+^^xsd:string .

            rm:"""+data+""""" rdf:type rm:Data .
            rm:"""+data+""""" rm:summary """+summary+"""""+^^xsd:string .
            rm:"""+data+""""" rm:subject """+subject+"""""+^^xsd:string .
            rm:"""+data+""""" rm:number_of_lines """+numberOfLines+"""""+^^xsd:integer .

            rm:"""+author+""""" rdf:type rm:Author .
            rm:"""+author+""""" rm:is rm:"""+person_name+""""" .
            rm:"""+author+""""" rm:works_for rm:"""+organization+""""" .

            rm:"""+date_and_time+""""" rdf:type rm:Time_and_Date .
            rm:"""+date_and_time+""""" rm:at rm:"""+time_timezone+""""" .
            rm:"""+date_and_time+""""" rm:on rm:"""+date+""""" .

            rm:"""+filename+""""" rdf:type rm:News .
            rm:"""+filename+""""" rm:posted_on rm:"""+date_and_time+""""" .
            rm:"""+filename+""""" rm:posted_by rm:"""+author+""""" .
            rm:"""+filename+""""" rm:has rm:"""+data+""""" .
            rm:"""+filename+""""" rm:part_of rm:"""+newsgroup+""""" .
        }
    """)

