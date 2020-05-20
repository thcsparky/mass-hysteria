import os
import requests
import socket
import re
import json
welcomemsg = 'Here it is. type -readme to load the readme file\n\n'
helpmsg = '-file (filename in this dir to start) -folder (subfolder of this dir to which all files will be opened and set for processing)'
helpmsg += '\n-rematch simply prints a list of all the IPS in a file'
saveparse = 1

def processCommand(cmd): ##for anything with additional arguments this strips the - from the command, returns that, along with a list of all the args parsed by space. It should be noted you need to strip newlines for poper feeedback.
    options = ['-help', '-file', '-folder', '-readme', '-rematch']
    index = -1
    try:
        if cmd.find(' ') > -1:
            index = options.index(cmd.split(' ')[0])
            if cmd.split(' ')[1].startswith('/'):
                listreturn = [options[index].replace('-', ''), os.getcwd() + cmd.split(' ')[1]]
            else:
                listreturn = [options[index].replace('-', ''), os.getcwd() + '/' + cmd.split(' ')[1]]
            return(listreturn)

        else:
            index = options.index(cmd)
            return(options[index].replace('-', ''))
    except Exception as e:
        print(e)
        return(0)

def start(mode, path):
    try:
        listsnoop = []
        dictVars = {}

        if mode == 'file':
            rema = rematch(path) ##this should work there shouldnt be any prblem joining two empty lists
            for x in rema:
                try:
                    if x not in listsnoop:
                        listsnoop.append(x)
                except:
                    continue

        elif mode == 'folder':
            filestoload = os.listdir(path)
            if filestoload is not None:
                for x in filestoload:
                    try:
                        a = os.listdir(path + '/' + x)
                        continue
                    except:
                        rema = rematch(path + '/' + x)
                        try:
                            for y in rema:
                                if y not in listsnoop:
                                    listsnoop.append(y)
                        except:
                            continue

        ##initiate the loop:
        print('Gather data on: \n')
        print(listsnoop)
        print ('\n\n')
        if len(listsnoop) > 0:
            for x in listsnoop:
                try:
                    resultfind = testIP(x)
                    if type(resultfind) == str:
                        print(resultfind)
                        continue

                    if len(resultfind) > 0:
                        endpoint = len(dictVars)
                        dictVars[str(endpoint)] = resultfind
                except:
                    continue
            return(dictVars)
        else:      ##this will automatically handle the error reporting in testIP
            return('no ips found')

        if len(dictVars) > 0:
            return(dictVars)
        else:
            return('Error compiling dictionary')
    except Exception as e:
        print(e)

def testIP(ip): #will return a dict you can add to another dict for js0n
    global saveparse #enabling this to 1 instead of 0 will give you a feedback of parse points for each var

    baseurl = 'https://tools.wmflabs.org/whois/gateway.py?lookup=true&ip='
    found = requests.get(baseurl + ip, verify=True, timeout=120)
    ##be more verbose
    print('Searching: ' + ip + '...\n')
    if found.ok:
        foundpage = found.text
        print('OK status for data on: ' + ip + '...\n')
        findpos = 0
        dictData = {}
        ##get all the other info from th and td tags:
        if foundpage.find('<th>') > -1 and foundpage.find('<td>') > -1:
            tablehead = foundpage.split('<tr>')
            curpos = 0
            dictMore = {}
            for x in tablehead:
                try:
                    tablerow = x.split('</tr>')[0]
                    tablehead = tablerow.split('<th>')[1]
                    tableheadfinal = tablehead.split('</th>')[0]
                    tableitem = tablerow.split('<td>')[1]
                    if tableitem.find('<a href="') > -1:
                        tableitemfinal = tableitem.split('"')[1]
                    elif tableitem.find('<div') > -1:
                        continue
                    else:
                        tableitemfinal = tableitem.split('</td>')[0]

                    dictMore = {'ipvar': ip, tableheadfinal: tableitemfinal}
                    dictData.update(dictMore)
                except Exception as sube:
                    continue

        return(dictData)
    else:
        return('Error : '  + str(found.status_code))

def rematch(file):
    try:
        fileio = open(file)
        filein = fileio.read()
        fileio.close()
        test = findips(filein)
        return(test)
    except Exception as o:
        return(o)

def writefile(file, content):
    if file.find(os.getcwd() + '/') == -1:
        out = os.getcwd() + '/' + file
    else:
        out = file

    try:
        fileio = open(out, 'w')
        fileio.write(content)
        fileio.close()
        return('Saved to: ' + out + '\n')
    except Exception as e:
        return(e)

def findips(bulktext):
    ips = []
    z = re.findall(r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}", bulktext) ##\b in the regex anchors the beginning and end from going over 3.

    for x in z:
        try:
            ips.append(x)
        except Exception as i:
            print (i)
            continue

    return (ips)

def main():
    inp = input('').rstrip()
    prc = processCommand(inp)
    if type(prc) is int:
        print('Invalid command\n')
    if type(prc) is str:
        if prc == 'help':
            print(helpmsg)
        if prc == 'readme':
            print('go open it')
    if type(prc) is list:
        if prc[0] == 'file':
            doit = start('file', prc[1])
        if prc[0] == 'folder':
            doit = start('folder', prc[1])
        if prc[0] == 'rematch':
            doit = rematch(prc[1])

        if doit is not None:
            out = json.dumps(doit)
            msg = writefile('json.json', out)
            print(msg)
            print(doit)

if __name__ == '__main__':
    print(welcomemsg)
    main()
