import re, getopt, sys, base64
# unicode invalid characters    
def main(args):
    try:
        opts, args = getopt.getopt(args, 'hf:', ['help', 'file='])
        for opt, arg in opts:
            if opt in('-h', '--help'):
                print('-f, --f filePath: choose the file to be handled')
            elif opt in('-f', '--file'):
                handle_ctrl_char(arg)
            elif args[0]:
                handle_ctrl_char(args[0])

    except getopt.GetoptError as e:
        sys.exit()
        
def handle_ctrl_char(filePath):
    '''
    RE_XML_ILLEGAL = u'([\u0000-\u0008\u000b-\u000c\u000e-\u001f\ufffe-\uffff])' + \  
                    u'|' + \  
                    u'([%s-%s][^%s-%s])|([^%s-%s][%s-%s])|([%s-%s]$)|(^[%s-%s])' % \  
                    (unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),    
                        unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),    
                        unichr(0xd800),unichr(0xdbff),unichr(0xdc00),unichr(0xdfff),    
                        )   
    '''
    RE_SRC = '<img[^\n^>]*src[\s]*=[\s]*[\'\"]([^\n\>]+)[\'\"][^>]*>'
    tmpString = []
    with open(filePath, 'r') as file:
        for line in file.readlines():
            tmpLine = line
            for srcPath in re.findall(RE_SRC, line):
                base64SRC=''
                try:
                    with open(srcPath, 'rb') as imgFile:
                        code = base64.b64encode(imgFile.read())
                        base64SRC = 'data:image/jpg;base64,' + code.decode('utf8') 
                        tmpLine = re.sub(srcPath,base64SRC,tmpLine)
                except FileNotFoundError:
                    pass
            tmpString.append(tmpLine)
    #print(tmpString)
    with open(filePath, 'w') as file:
        file.writelines(tmpString)



if __name__ == '__main__':
    main(sys.argv[1:])