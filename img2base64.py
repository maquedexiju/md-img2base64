import re, getopt, sys, base64
import os.path
import urllib.request
import markdown
import subprocess

# unicode invalid characters    
def main(args):
    try:
        opts, args = getopt.getopt(args, 'hf:', ['help', 'file='])
        for opt, arg in opts:
            if opt in('-h', '--help'):
                print('-f, --f filePath: choose the file to be handled')
            elif opt in('-f', '--file'):
                handle_file(arg)
            elif args[0]:
                handle_file(args[0])

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

    #write the new data to a html file
    with open('tmp.md', 'w') as mdFile:
        mdFile.writelines(tmpString)
    
    #transfer md to html
    htmlName = basePath + '/' + baseName + '.html'
    markdown.markdownFromFile(input = 'tmp.md', output = htmlName, encoding = 'utf-8',
                                extensions = ['markdown.extensions.extra', 
                                                'markdown.extensions.meta',
                                                'markdown.extensions.nl2br',
                                                'markdown.extensions.sane_lists',
                                                'markdown.extensions.toc'])
    
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