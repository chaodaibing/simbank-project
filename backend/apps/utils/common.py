import datetime,time
from config import db
import json,os,sys,logging,re
import configparser
import pymysql,requests
import pandas as pd

#写日志用
def writefile(str,filename,type='w'):
  #不存在日志所在路径就创建之
  if not os.path.isdir(os.path.dirname(filename)):
    os.makedirs(os.path.dirname(filename))
  f = open(filename,type)   
  f.write(str)
  f.close()

#返回把字典replaceinto某表的SQL
def sqlreplace(tablename,data):
  seglist= list(data.keys())                          #字段列表
  valuelist = list(data.values())
  valuelist = list(map(str,valuelist))            #列表字符串化
  columns = '`' + '`, `'.join(seglist)+'`'
  values = "'"+ "','".join(valuelist) +"'"
  sql = "replace into " + tablename + "(%s)" + " values(%s)"
  sql = sql %(columns,values)                                  
  return sql

#返回把字典insert某表的SQL
def sqlinsert(tablename,data):
  seglist= list(data.keys())                          #字段列表
  valuelist = list(data.values())
  valuelist = list(map(str,valuelist))            #列表字符串化
  columns = '`' + '`, `'.join(seglist)+'`'
  values = "'"+ "','".join(valuelist) +"'"
  sql = "insert into " + tablename + "(%s)" + " values(%s)"
  sql = sql %(columns,values)                                  
  return sql

#读取SQL文件
def readsqlstr(sqlfilename):
  filename = sqlfilename+'.sql'
  sqlfilepath='sqls'+os.sep+filename
  f = open(sqlfilepath, 'r')
  sql = f.read()
  f.close()
  return sql   

#连接mysql的函数(pands有用)
def con_mysql():
  return db.engine

#通过Pandas查询sql返回json
def sqlpds(sql):
  dbc=con_mysql()
  data = pd.read_sql(sql, con=dbc)
  header=list(data)
  content=data.to_dict(orient='records')
  return {'header':header,'content':content}
    
#导出SQL执行结果到excel
def dumpexcel(sql,sheetname,filename):
  dbc=con_mysql()
  writer=pd.ExcelWriter(filename)
  data = pd.read_sql(sql, con=dbc)
  data.to_excel(writer,sheetname,index=False)
  writer.save()
  result = filename + "成功导出\n"
  print(result)

#导出SQL执行结果到csv
def dumpcsv(sql,filename):
  dbc=con_mysql()
  data = pd.read_sql(sql, con=dbc)
  data.to_csv(filename,encoding="utf_8_sig",float_format='%.2f',index=False)
  result = filename + "成功导出\n"
  print(result)

#读取excel文件
def readexcel(filename):
  data = pd.read_excel(filename)
  return data.to_dict(orient='records')  

#读取excel写入mysql
def excel2db(filename,tablename):
  res=readexcel(filename)
  for line in res:
    sql=sqlreplace(tablename,line)
    db.session.execute(sql)
  db.session.commit() 
  
#普通查询SQL返回字典组成的列表 
def sqlexec(sql,page=1,limit=1):
  res=db.session.execute(sql)
  result=[]
  for line in res:
    dic=dict(line)
    for item in dic:      
      if(isinstance(dic[item],datetime.datetime)):  #如果字段的值是时间格式的 转换成字符串
        dic[item]=dic[item].strftime("%Y-%m-%d %H:%M:%S")
      elif(isinstance(dic[item],datetime.date)):
        dic[item]=dic[item].strftime("%Y-%m-%d")
    result.append(dic)
  return result

#pymysql原始查询SQL
def rawexec(dbc,sql,close=True):
  cursor=dbc.cursor()
  cursor.execute(sql)
  res=cursor.fetchall()
  if(close):
    dbc.close()
  return res

#解析sqlalchemy的查询结果
def parsealchemy(res,pagination=False):
  result = []
  if pagination:                                    #分页的情况
    for line in res.items:
      dic = line.to_json()
      for item in dic:      
        if(isinstance(dic[item],datetime.datetime)):  #如果字段的值是时间格式的 转换成字符串
          dic[item]=dic[item].strftime("%Y-%m-%d %H:%M:%S")
        elif(isinstance(dic[item],datetime.date)):
          dic[item]=dic[item].strftime("%Y-%m-%d")
      result.append(dic)
    dic = {'total':res.total,'result':result}
  else:                                             #不分页的情况
    for line in res:
      dic = line.to_json()
      for item in dic:      
        if(isinstance(dic[item],datetime.datetime)):  #如果字段的值是时间格式的 转换成字符串
          dic[item]=dic[item].strftime("%Y-%m-%d %H:%M:%S")
        elif(isinstance(dic[item],datetime.date)):
          dic[item]=dic[item].strftime("%Y-%m-%d")
      result.append(dic)
    dic={'total':len(res),'result':result}
  return dic

#获取现在的时刻
def getnowtime(args):
  dic={}
  dic['date'] = time.strftime("%Y-%m-%d",time.localtime())
  dic['time'] = time.strftime("%H:%M:%S",time.localtime())
  dic['datetime'] = time.strftime("%Y-%m-%d %H:%M:%S",time.localtime())
  return dic[args]

#获取易读的时间格式
def getformattime(args):
  if(len(args)==14):
    timestamp = datetime.datetime.strptime(args,"%Y%m%d%H%M%S")
    return timestamp.strftime("%Y-%m-%d %H:%M:%S")
  elif(len(args)==8):
    timestamp = datetime.datetime.strptime(args,"%Y%m%d")
    return timestamp.strftime("%Y-%m-%d")

#字符串过滤
def strfilter(str):
  grep = "'|echo|passwd|ping|etc|and|or|from|exec|1=1|#|drop|insert|by|order|select|delete|update|count|like|$|&|*|%|?|chr|mid|master|truncate|char|declare|;|+|--|,"
  match = grep.split('|') 
  for item in match:
    if(item in str or item.upper() in str):      #匹配上敏感字符的返回为空
      return 'forbidden'
  return str

#字典过滤
def dicfilter(dic):
  for ele in dic.values():
    if(strfilter(ele)=='forbidden'):            #如果有一个值为空 则警报
      return ""
  return dic

#把结果集的每一行的特定字段的值用逗号拼接起来
def one2many(reslist,item):
  itemlist=[]
  for i in reslist:
    itemlist.append(i[item])
  return ','.join(itemlist)

#解析比较复杂的sql文件返回SQL组成的列表
def parse_sql(filename):
    data = open('sqls'+os.sep+filename+'.sql', 'r').readlines()
    stmts = []
    DELIMITER = ';'
    stmt = ''
    for lineno, line in enumerate(data):
        if not line.strip():
            continue
        if line.startswith('--'):
            continue
        if 'DELIMITER' in line:
            DELIMITER = line.split()[1]
            continue
        if (DELIMITER not in line):
            stmt += line.replace(DELIMITER, ';')
            continue
        if stmt:
            stmt += line
            stmts.append(stmt.strip())
            stmt = ''
        else:
            stmts.append(line.strip())
    return stmts