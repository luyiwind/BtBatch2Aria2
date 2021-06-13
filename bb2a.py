import xmlrpc.client
import xmlrpc
import os
import argparse

def handle(s, btFile, secret):
    print('handle bittorrent file: ', str(btFile))
    ret=s.aria2.addTorrent('token:'+secret, xmlrpc.client.Binary(open(btFile, mode='rb').read()),[],{'pause':'true'})
    print("add bt: ",str(ret))
    waiting = s.aria2.tellWaiting('token:'+secret, 0, 1000,
                              ["gid", "totalLength", "completedLength", "uploadSpeed", "downloadSpeed", "connections",
                               "numSeeders", "seeder", "status", "errorCode", "verifiedLength",
                               "verifyIntegrityPending", "files", "bittorrent", "infoHash"])
    for w in waiting:
        gid=w['gid']
        if gid!=ret:
            continue
        #print(w['gid'],w['files'])
        # max-selection strategy
        maxLen=0
        maxFPath=''
        maxFIndex='0'
        for f in w['files']:
            print(f['length'],f['path'])
            if int(f['length'])>maxLen:
                maxLen=int(f['length'])
                maxFPath=f['path']
                maxFIndex=f['index']
        print('max file: ',str(maxLen),maxFIndex,str(maxFPath))
        # max-selection strategy end
        cret=s.aria2.changeOption('token:'+secret, gid,{'select-file':maxFIndex})# select multiple files example: 'select-file':'5,6,7,8'
        print('select file: ',cret)
        tret=s.aria2.tellStatus('token:'+secret, gid)
        print('after selection: ', tret['files'][int(maxFIndex)-1])
        uret=s.aria2.unpause('token:'+secret, gid)
        print('unpause: ',uret)
    print('over: ',str(btFile))
    os.remove(btFile)

def handleMag(s, mgFile, secret):
    print('handle mag file: ', str(mgFile))
    if os.path.getsize(mgFile):
        ret=s.aria2.addUri('token:'+secret, [xmlrpc.client.Binary(open(mgFile, mode='rb').read())])
        print("add mag: ",str(ret))
        print("remove mag file: ",str(mgFile))
    os.remove(mgFile)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.description = 'bt批量导入aria2，并选择文件大小最大的文件进行下载'
    parser.add_argument("num", help="the num to be added once", type=int)
    parser.add_argument("server", help="like: http://192.168.3.99:6800/", type=str)
    parser.add_argument("dir", help="the dir of your bittorrents", type=str)
    parser.add_argument("mgdir", help="the dir of your magnets", type=str)
    parser.add_argument("secret", help="secrets", type=str)
    parser.add_argument("name", help="mag name", type=str)
    args = parser.parse_args()
    s = xmlrpc.client.ServerProxy(args.server+"rpc")
    flist=os.listdir(args.dir)
    count = 0
    name = args.name
    for i in range(0, len(flist)):
        if flist[i].endswith(".torrent"):
            btFile = os.path.join(args.dir, flist[i])
            if os.path.isfile(btFile):
                handle(s,btFile,args.secret)
            
    for root, dirs, files in os.walk(args.mgdir):
        for file in files:
            if name != "any" and root.lower().replace('-','').find(name.lower().replace('-','')) == -1:
                continue
            if file.endswith(".txt"):
                count += 1
                if count > args.num:
                    continue
                mgFile = os.path.join(root, file)
                print("path:"root)
                handleMag(s,mgFile,args.secret)
                    
    print("Add magnets to air2 Done")
