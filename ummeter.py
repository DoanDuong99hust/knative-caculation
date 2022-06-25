import subprocess
import os
import process_data_to_result.getfiles as getfiles
import time
def start_ummeter(minutes: int):
    '''
    minutes parameter tells how long the un meter should collect data [minutes]
    '''
    #starts clicking script
    subprocess.run('/home/fil/hanoi/code/click.sh %s' % (str(minutes*60)), stdout=subprocess.PIPE).stdout.decode('utf-8')
    
 