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
    person = getPerson(text)
    first_name = person[0]
    last_name = person[1]
    email = person[2]
    subject = getSubject(text)
    timeAndDate = getTimeAndDate(text)
    day = timeAndDate[0]
    date = timeAndDate[1]
    time = timeAndDate[2]
    timezone = timeAndDate[3]
    distribution = getDistribution(text)
    organization = getOrganization(text)
    numberOfLines = getNumberOfLines(text)
    summary = getSummary(text)

    # ontology
    # News = Author + Time_and_Date + Newsgroup + Data
    # Author = Person + Organization
    # Time_and_Date = Time + Date
    # Newsgroup = newsgroups
    # Data = summary + subject + numberOfLines
    # Time = time + timezone
    # Date = day + date
    # Person = first_name + last_name + email
    # Organization = organization





