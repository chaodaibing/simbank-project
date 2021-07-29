#coding:utf-8
import telnetlib
import time,os
from datetime import datetime
import configparser

def getcurtime():
  return datetime.now().strftime('%Y-%m-%d_%H:%M:%S')

def getversion():
  config = configparser.ConfigParser()
  config.read('config.ini')
  stage='version'
  high_board_version=config[stage]['high_board_version']
  high_blade_version=config[stage]['high_blade_version']
  low_board_version=config[stage]['low_board_version']
  low_blade_version=config[stage]['low_blade_version']
  versioninfo={}
  versioninfo['upgrade']={'board':high_board_version,'blade':high_blade_version}
  versioninfo['degrade']={'board':low_board_version,'blade':low_blade_version}
  return versioninfo

def logininfo():
  config = configparser.ConfigParser()
  config.read('config.ini')
  stage='login'
  username=config[stage]['username']
  password=config[stage]['password']
  return {"username":username,"password":password}

def WriteLog(msg):
  logdir=os.path.join(os.getcwd(),'logs')
  if(not os.path.isdir(logdir)):
    os.mkdir(logdir)
  logfile=os.path.join(logdir,'update.log')
  with open(logfile,'a') as f:
    f.write(msg + "\n")

class TelnetClient():
  def __init__(self):
    self.tn = telnetlib.Telnet()

  def login_host(self,host_ip,username,password):
    host_ip=host_ip.encode('utf-8')
    username=username.encode('utf-8')
    password=password.encode('utf-8')
    try:
      self.tn.open(host_ip,port=23)
    except:
      print('登入失败')
      return False
    self.tn.read_until(b'username:',timeout=3)
    self.tn.write(username+ b'\n')
    self.tn.read_until(b'password:',timeout=3)
    self.tn.write(password + b'\n')
    time.sleep(1)
    WriteLog(self.tn.read_very_lazy().decode('utf-8'))

  def exec_cmd(self,command,type1='other',type2='other'):
    print("*************",command,"***************************\n")
    command=command.encode('utf-8')
    self.tn.write(command + b'\n')
    a=[]
    typemap={"board":"%100","blade":"%60"}   #升级board和blade标准不一样
    break_siglist=['space full','same','fixed version','failed','already exist','No new version']
    if(type1=='update'):
      break_siglist.append(typemap[type2])
    d='strs'
    #持续循环监控屏幕输出
    time.sleep(1)
    while True:
      if(d):
        empty=0
      b,c,d=self.tn.expect(a,timeout=2)   #期待返回结果
      d=d.decode('utf-8').replace("#","\n") #返回结果
      print(d + "\n")             #打印返回结果
      if(not d):                  #持续20秒都没有内容就跳出
        empty+=1
        print(empty)
        if(empty>20):
          self.tn.write(b'\n')
          time.sleep(1)
          break
      if(type1=='update'):          #更新版本的命令
        ifbreak=False
        for sig in break_siglist:   #有结果信息，就跳出
          if(sig in d):
            ifbreak=True
        if(ifbreak):
          self.tn.write(b'\n')
          time.sleep(1)
          break
        else:
          continue
      else:
        if(b==0):
          self.tn.write(r' ')     #没有结束就回车
        else:
          break
    WriteLog(d + "\n")         #打印最后的显示结果
    return d                   #返回最后的显示结果
 
  def logout_host(self):
    self.tn.write(b"exit\n")



    versiondic={}
    versiondic['upgrade']={'board':'SIMBOARD.nios-32.2.13.24.20190213171311.Beta','blade':'SIMSTICK.nios-32.2.13.24.20190213171233.Beta'}
    versiondic['degrade']={'board':'SIMBOARD.nios-32.2.9.9.20150115164802.Beta','blade':'SIMSTICK.nios-32.2.11.16.20151025100514.Beta'}


