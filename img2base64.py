#!/Library/Frameworks/Python.framework/Versions/3.6/bin/python3
#coding:utf-8 

import re, getopt, sys, base64
import os.path
import os
import urllib.request
import markdown
import subprocess

#config
webServerPath = '/Library/WebServer/Documents'
scriptPath = os.path.expanduser('~') +'/MyScript'
styleSheet = '/Users/XuXiaotian/MyScript/style.css'

#tmp val
browseInBrowser = True
markdownFile = False
filePathGiven = ''

# unicode invalid characters    
def main(args):
    try:
        opts, args = getopt.getopt(args, 'hf:wm', ['help', 'file=', 'webfile', 'markdown'])
        if len(args)>0:
                print(args[0])
                handle_file(args[0])
        for opt, arg in opts:
            if opt in('-h', '--help'):
                print('-f, --f filePath: choose the file to be handled')
            elif opt in('-f', '--file'):
                filePathGiven = arg
            elif opt in('-w', '--webfile'):
                browseInBrowser = False
            elif opt in('-m', '--markdown'):
                markdownFile = True

        if filePathGiven != '':
            handle_file(filePathGiven)


    except getopt.GetoptError as e:
        sys.exit()


def handle_file(filePath):
    #get the file info
    tmpString = []
    basePath = os.path.dirname(filePath)
    baseName = os.path.basename(filePath)
    print(basePath)

    #change the img path to base64
    with open(filePath, 'r') as file:
        for line in file.readlines():
            tmpString.append(handle_src_path(line, basePath))

    #whether to generate a markdown file
    if markdownFile == True:
        #found a file under the path
        mdFileName = basePath + '/' + baseName + '_base64.md'
    else:
        #use the tmp file
        if scriptPath != '' and os.path.exists(scriptPath):
            if not os.path.exists(scriptPath+ '/img2base64'):
                os.mkdir(scriptPath+ '/img2base64')
            mdFileName = scriptPath+ '/img2base64/tmp.md'
        else:
            if not os.path.exists(os.path.expanduser('~') + '/.img2base64'):
                os.mkdir(os.path.expanduser('~') + '/.img2base64')
            mdFileName = os.path.expanduser('~') + '/.img2base64/tmp.md'

    #write the new data to a html file
    with open( mdFileName, 'w') as mdFile:
        mdFile.writelines(tmpString)
    
    #whether to save the file to the webserver
    if browseInBrowser == False:
        htmlName = basePath + '/' + baseName + '.html'
    else: 
        htmlName = webServerPath + '/' + 'tmp.html'

    
    #transfer md to html
    htmlContent = """<html>
    <head>
        <meta charset="utf-8">
        <style type="text/css">
    """

    if styleSheet != '':
        with open(styleSheet, 'r') as styleFile:
            htmlContent += styleFile.read()
    
    htmlContent += """
        </style>
    </head>

    <body>
    """

    htmlContent += markdown.markdown('\n'.join(tmpString), encoding = 'utf-8',
                                extensions = ['markdown.extensions.extra', 
                                                'markdown.extensions.meta',
                                                'markdown.extensions.nl2br',
                                                'markdown.extensions.sane_lists',
                                                'markdown.extensions.toc'])
    
    htmlContent +="""
    </body>
    </html>
    """

    #write the content to the html file
    with open(htmlName, 'w') as htmlFile:
        htmlFile.write(htmlContent)
    
    # open the html file
    subprocess.call(["open", htmlName])


def handle_src_path(fileLine, basePath):
    #reg for <img ... src = 'srcPath' ...>
    RE_SRC = '<img[^\n^>]*src[\s]*=[\s]*[\'\"]([^\n\>]+)[\'\"][^>]*>'
    
    tmpLine = fileLine
    #find the src of images
    for srcPath in re.findall(RE_SRC, fileLine):
        #handle the path
        base64SRC = ''
        realPath = ''
        if re.match('/', srcPath):
            #this is a absolute path
            realPath = srcPath
        elif re.search('://', srcPath):
            #this is a web protocol
            download_web_file(srcPath)
            realPath = 'tmp.txt'
        else:
            #this is a relative path
            realPath = basePath + '/' + srcPath
        try:
            with open(realPath, 'rb') as imgFile:
                code = base64.b64encode(imgFile.read())
                base64SRC = 'data:image/jpg;base64,' + code.decode('utf8') 
                tmpLine = re.sub(srcPath,base64SRC,tmpLine)
            
        except FileNotFoundError:
            print('file "%s" not found'%srcPath)
    
    #return the modified fileLine
    return tmpLine


def download_web_file(url):
    #download and save as tmp.txt
    with urllib.request.urlopen(url) as originFile:
        data = originFile.read()
        with open('tmp.txt', 'wb') as tmpFile:
            tmpFile.write(data)


if __name__ == '__main__':
    main(sys.argv[1:])