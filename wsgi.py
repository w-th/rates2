#!/usr/bin/env python
import os
import re, urllib.request, datetime, json, urllib, pdb

#other_url = "http://traderoom.cnyes.com/global/forex.aspx"
index_url = "http://traderoom.cnyes.com/global/provider.aspx"
usindex = "http://www.cnyes.com/forex/"
arg = 'act=qp&sort=FOrd&adesc=asc&rows=2254&type=X&market=FX&page={0}&rpp=20'
linespat = "fccode=DX&rate=exchange"
splitpat = "width='11%' class='rt'>"

money = {'CNH':0.0,'EUR':0.0,'AUD':0.0,'TWD':0.0,'KRW':0.0,'CHF':0.0,'CAD':0.0,'GBP':0.0,'JPY':0.0,'SGD':0.0,'USDIDX':0.0}
pnt = {'CNH':0,'EUR':0,'AUD':0,'TWD':0,'KRW':0,'CHF':0,'CAD':0,'GBP':0,'JPY':0,'SGD':0}
seq = ["USDIDX", "JPY", "EUR", "GBP", "CHF", "CAD", "AUD", "TWD", "CNH",
    "KRW","SGD"]

res = {}
table = """<!doctype html>
<head>
<title>rates</title>
<meta http-equiv="Content-Type" content="text/html; charset=utf-8" />
</head>
<body>
<table border="1">
<tr><th>主要貨幣</th><th>匯率</th></tr>
{0}
</table>
</body>
</html>
"""
templ = "<tr><td>{0}</td><td>{1}</td></tr>"

def format_number(a,b):
  e = '.'
  def norm_(a, b):
    c = pow(10, b)
    return round(a * c) / c
  #c = (norm_(a, b)).split(e)
  return norm_(a,b)

def get_us_index():
  global money
  response = urllib.request.urlopen(usindex)
  html = response.read().decode('utf-8').split('\r\n')
  lines = [i for i in html if i.find(linespat) != -1 and i.find(splitpat) != -1]
  l = lines[0].split(splitpat)[1].split("</td>")[0]
  money['USDIDX'] = float(l)

def parse():
  global money
  get_us_index()
  #params = urllib.parse.urlencode()
  response = urllib.request.urlopen(index_url,data=arg.format(1).encode('utf-8'))
  html = response.read()
  a = json.loads(html.decode('utf-8'))
  # CNH
  money['CNH'] = [float(i['FC']) for i in a['quotes'] if i['FSymbol2']=='USDCNH'][0]
  pnt['CNH'] = [int(i['FDPnt']) for i in a['quotes'] if i['FSymbol2']=='USDCNH'][0]
  # EUR
  money['EUR'] = [float(i['FC']) for i in a['quotes'] if i['FSymbol2']=='EURUSD'][0]
  pnt['EUR'] = [int(i['FDPnt']) for i in a['quotes'] if i['FSymbol2']=='EURUSD'][0]
  # AUD
  money['AUD'] = [float(i['FC']) for i in a['quotes'] if i['FSymbol2']=='AUDUSD'][0]
  pnt['AUD'] = [int(i['FDPnt']) for i in a['quotes'] if i['FSymbol2']=='AUDUSD'][0]
  # TWD
  money['TWD'] = [float(i['FC']) for i in a['quotes'] if i['FSymbol2']=='USDTWD'][0]
  pnt['TWD'] = [int(i['FDPnt']) for i in a['quotes'] if i['FSymbol2']=='USDTWD'][0]
  # KRW
  money['KRW'] = [float(i['FC']) for i in a['quotes'] if i['FSymbol2']=='USDKRW'][0]
  pnt['KRW'] = [int(i['FDPnt']) for i in a['quotes'] if i['FSymbol2']=='USDKRW'][0]
  # CHF
  money['CHF'] = [float(i['FC']) for i in a['quotes'] if i['FSymbol2']=='USDCHF'][0]
  pnt['CHF'] = [int(i['FDPnt']) for i in a['quotes'] if i['FSymbol2']=='USDCHF'][0]
  # CAD
  money['CAD'] = [float(i['FC']) for i in a['quotes'] if i['FSymbol2']=='USDCAD'][0]
  pnt['CAD'] = [int(i['FDPnt']) for i in a['quotes'] if i['FSymbol2']=='USDCAD'][0]
  # GBP
  money['GBP'] = [float(i['FC']) for i in a['quotes'] if i['FSymbol2']=='GBPUSD'][0]
  pnt['GBP'] = [int(i['FDPnt']) for i in a['quotes'] if i['FSymbol2']=='GBPUSD'][0]
  # JPY
  money['JPY'] = [float(i['FC']) for i in a['quotes'] if i['FSymbol2']=='USDJPY'][0]
  pnt['JPY'] = [int(i['FDPnt']) for i in a['quotes'] if i['FSymbol2']=='USDJPY'][0]
  #pdb.set_trace()

  # SGD in page 2
  response = urllib.request.urlopen(index_url,data=arg.format(2).encode('utf-8'))
  html = response.read()
  a = json.loads(html.decode('utf-8'))
  money['SGD'] = [float(i['FC']) for i in a['quotes'] if i['FSymbol2']=='USDSGD'][0]
  pnt['SGD'] = [int(i['FDPnt']) for i in a['quotes'] if i['FSymbol2']=='USDSGD'][0]

  res['USDIDX'] = money['USDIDX']
  #[print("{0} = {1}".format(i, money[i])) for i in money if i != 'USDIDX']
  [res.setdefault(i,format_number(money[i],pnt[i])) for i in money if i != 'USDIDX']
  output = table.format("\n".join([templ.format(i, res[i]) for i in seq]))
  return output

#from app import app as application

def application(environ, start_response):
    ctype = 'text/plain'
    if environ['PATH_INFO'] == '/health':
        response_body = "1"
    elif environ['PATH_INFO'] == '/env':
        response_body = ['%s: %s' % (key, value)
                    for key, value in sorted(environ.items())]
        response_body = '\n'.join(response_body)
    else:
        ctype = 'text/html'
        response_body = parse()

    status = '200 OK'
    response_headers = [('Content-Type', ctype), ('Content-Length', str(len(response_body)))]
    #
    start_response(status, response_headers)
    return [response_body.encode('utf-8') ]

#
# Below for testing only
#
if __name__ == '__main__':
    from wsgiref.simple_server import make_server
    httpd = make_server('localhost', 8051, application)
    # Wait for a single request, serve it and quit.
    httpd.handle_request()
