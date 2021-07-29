#coding:utf8
from flask_restful import Resource,request,reqparse 
from flask import Flask, jsonify,session,abort
from config import db   
import time  
from sqlalchemy import func,and_             
from apps.utils.telnet import TelnetClient,WriteLog,getversion,logininfo 
from apps.utils.common import sqlexec,parsealchemy,getnowtime       
from apps.utils.models import Blade,Board
#获取主板列表
class boardlist(Resource):
  def post(self):
    params = request.get_json()
    limit= params['limit']          #每页多少行
    page=params['page']  
    id=params['id']                 #主板ID
    res = db.session.query(Board).filter(Board.id.like('%'+id)).order_by(Board.id).paginate(page,limit)
    dic = parsealchemy(res,True)
    return dic

#获取卡条列表
class bladelist(Resource):
  def post(self):
    params = request.get_json()
    limit= params['limit']          #每页多少行
    page=params['page']  
    id=params['id']                 #主板ID
    res = db.session.query(Blade).filter(and_(Blade.board_id.like('%'+id),Blade.state==1)).paginate(page,limit)
    dic = parsealchemy(res,True)
    return dic

#从board_sn获取board信息
class getboardinfo(Resource):
  def get(self):
    sn = request.args.get('board_sn')
    res = db.session.query(Board).filter(Board.sn==sn).all()
    res = parsealchemy(res)['result']
    return res

#检测重新获取主机板和卡条的信息
class checkall(Resource):   
  def post(self):     
    timestart=time.time()
    username= logininfo()['username']
    password= logininfo()['password']
    params = request.get_json()
    ip=params['ip']     
    mode=params['mode']
    if(mode=='all' and not ip):                                 #全量IP
      iplist=sqlexec("select ip_address from sc_board")    
    elif(mode=='one' and ip):                                   #单一IP
      iplist=[{'ip_address':ip}]
    else:
      return {"code":403,"msg":"传参有误，请检查"}
    for line in iplist:       
      nowtime=getnowtime('datetime')
      host_ip=line['ip_address']                  #get ip addr       
      tc=TelnetClient()       
      tc.login_host(host_ip,username,password)    #login
      #获取board_version       
      res1=tc.exec_cmd('')
      res1=res1.split('\n')[0].split()[-1].replace('!','')       
      if('nios' in res1):
        board_version=res1                        #获取SN码
      res2=tc.exec_cmd('sn -g')       
      sn=res2.split()[0].split(':')[-1]
      #更新       
      sql="update sc_board set board_version='{}',sn='{}',updated_date='{}' where ip_address='{}'".format(board_version,sn,nowtime,host_ip)      
      db.session.execute(sql)                              
      #获取id
      sql="select id from sc_board where sn='{}'".format(sn)
      board_id=sqlexec(sql)[0]['id']    
      #获取sticks       
      res3=tc.exec_cmd('ls')
      bladelist=res3.split('sticks:')[1].split()[:-1]
      for blade in bladelist:
        stick_id=blade.split('(')[0]    #识别blade id  就是logic_addr字段
        if(not stick_id.isdigit()):     #排除不是id的
          continue
        res=tc.exec_cmd('cd '+ stick_id)       #进入blade
        stick_version=res.split('\n')[0].split()[-1].replace('!','')
        sql="select * from sc_blade where board_sn='{}' and logic_addr='{}'".format(sn,stick_id)
        res10=sqlexec(sql)
        if(not res10):                   #没有卡条记录就添加
          sql="insert into sc_blade(board_sn,board_addr,logic_addr,blade_version,updated_date) values ('{}','{}','{}','{}','{}')".format(sn,board_id,stick_id,stick_version,nowtime)
        else:
          sql="update sc_blade set board_addr='{}',blade_version='{}',updated_date='{}' where board_sn='{}' and logic_addr='{}'".format(board_id,stick_version,nowtime,sn,stick_id)
        db.session.execute(sql)
        tc.exec_cmd('cd ..')
      db.session.commit()
      timeend=time.time()
      return {"code":200,"msg":"更新完成,耗时{}秒".format(timeend-timestart)}

#检测卡条的信息
class checkblade(Resource):   
  def post(self):     
    username= logininfo()['username']
    password= logininfo()['password']
    params = request.get_json()
    board_id=params['board_id']     
    stick_id=params['stick_id']
    host_ip = sqlexec("select ip_address from sc_board where id={}".format(board_id))[0]['ip_address']
    nowtime=getnowtime('datetime')
    tc=TelnetClient()       
    tc.login_host(host_ip,username,password)    #login
    #获取sticks       
    res=tc.exec_cmd('cd '+ str(stick_id))       #进入blade
    if('input valid stick' in res):
      return {"code":404,"msg":"指定位置的卡条不存在或者在启动中"}
    stick_version=res.split('\n')[0].split()[-1].replace('!','')    
    sql="update sc_blade set blade_version='{}',updated_date='{}' where board_addr='{}' and logic_addr='{}'".format(stick_version,nowtime,board_id,stick_id)
    db.session.execute(sql)
    tc.exec_cmd('cd ..')
    tc.logout_host()
    db.session.commit()
    return {"code":200,"msg":"卡条版本更新完成"}

#全量升级主机板
class upgradeall(Resource):   
  def post(self):     
    timestart=time.time()
    username= logininfo()['username']
    password= logininfo()['password']
    params = request.get_json()
    method=params['method']     #升级还是降级
    iplist=params['iplist']
    if(not iplist):
      return {"code":403,"msg":"IP列表为空"}
    #升级降级对应的版本
    versiondic=getversion()
    #逐个IP遍历
    iplists=iplist.split()
    for host_ip in iplists:           
      tc=TelnetClient()       
      tc.login_host(host_ip,username,password)    #login
      #升级board 然后登出    
      tc.exec_cmd('update -f')    #free space
      outlet=tc.exec_cmd('update -u ' + versiondic[method]['board'],'update','board')   #update board
      tc.logout_host()
      print(host_ip,"board升级完成,登出等待重启")
      if('the same' in outlet): #如果不需要升级
        time.sleep(2)
      else:
        time.sleep(25)    #测试重启需要24秒
      print('重新登入',host_ip)
      while True:   #多次尝试登入直到成功
        try:
          tc = TelnetClient()
          tc.login_host(host_ip,username,password)
          tc.exec_cmd('sn -g')
        except Exception as e:
          print(e)
          time.sleep(2)
        else:
          break     
      time.sleep(2)
      tc.exec_cmd('update -u ' + versiondic[method]['blade'],'update','board')    #update blade version
      #识别blade
      bladelist=tc.exec_cmd('ls')
      bladelist=bladelist.split('sticks:')[1].split()
      #升级blade
      for blade in bladelist:
        stick_id=blade.split('(')[0]    #识别blade id  就是logic_addr字段
        if(not stick_id.isdigit()):     #排除不是id的
          continue
        tc.exec_cmd('cd '+ stick_id)       #进入blade
        time.sleep(1)
        tc.exec_cmd('update -u ' + versiondic[method]['blade'],'update','blade')  #update blade 经常卡壳
        print("要退出blade",stick_id) 
        tc.exec_cmd("cd ..\n")    #退出本blade回到board界面
        time.sleep(2)
      tc.logout_host()
    time.sleep(30)
    timeend=time.time()
    return {"code":200,"msg":"升级完成,耗时{}秒".format(timeend-timestart)}

#单一升级卡条
class upgradeone(Resource):   
  def post(self):     
    timestart=time.time()
    username=logininfo()['username']
    password=logininfo()['password']
    params = request.get_json()
    board_id = params['board_id']
    stick_id = params['stick_id']   
    method = params['method']     #升级还是降级
    host_ip = sqlexec("select ip_address from sc_board where id={}".format(board_id))[0]['ip_address']
    #升级降级对应的版本
    versiondic=getversion()
    tc=TelnetClient()
    tc.login_host(host_ip,username,password)    #login
    #升级board的stick_verson   
    #tc.exec_cmd('update -f')    #free space
    tc.exec_cmd('update -u ' + versiondic[method]['blade'],'update','board')    #update blade version
    #升级stick
    tc.exec_cmd('cd '+ str(stick_id))       #进入blade
    time.sleep(1)
    tc.exec_cmd('update -u ' + versiondic[method]['blade'],'update','blade')  #update blade 经常卡壳
    print("要退出blade",str(stick_id)) 
    tc.exec_cmd("cd ..\n")    #退出本blade回到board界面
    time.sleep(10)
    tc.logout_host()
    time.sleep(30)
    timeend=time.time()
    return {"code":200,"msg":"升级完成,耗时{}秒".format(timeend-timestart)}