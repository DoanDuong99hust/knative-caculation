import os
import shutil

default_dest = '{}{}'.format(os.getcwd(),'/data')

def getSrc():
    try:
    #find path to phone directory
        files=os.listdir('/run/user/1000/gvfs/')
        for device in files: 
            #checking if path to phone is found
            if 'SAMSUNG_SAMSUNG_Android' in device: 
                return '/run/user/1000/gvfs/{}/Phone'.format(device)
    except:
        print("Problem to find path to connected device!")


def copyFilesToPc(target_pods:int, src: str = None, dest: str = None):
    if src is None:
        src=getSrc()

    if dest is None:
        dest = default_dest

    files=[f for f in os.listdir(src)]
    if not files: 
        print('List is empty')
        return

    for file in files:
        print(file)
        if file.endswith(".xls"): 
            full_path="{}/{}".format(src, file)
            shutil.copy(full_path, dest+"/data_prometheus_{}.xlsx".format(target_pods))
            os.remove(full_path)
        else: continue
