from flask import Flask, render_template, request, redirect
import datetime
import requests
import pandas as pd
import sys
if sys.version_info[0] < 3: 
    from StringIO import StringIO
else:
    from io import StringIO
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.palettes import Viridis4
import os

checks = ('Open','Close','Adj. Open','Adj. Close')
line_dash = ('','',(4,4),(4,4))
OneMonth = 31

app = Flask(__name__)

@app.route('/')
def main():
    return redirect('/index')

@app.route('/index',methods=['GET','POST'])
def index():
    if request.method == 'GET':
        return render_template('index.html')
    elif request.method == 'POST':
        # If we are in here, we have requested a figure. Process the input.
        reqmultidict = request.form
        # I am not comfortable with this multidict, so take the values out
        stock = reqmultidict.get('stock',default='')
        featuresSelected = any([i for i in checks if i in reqmultidict])
        err = ''
        if not stock:
            err = 'Error: you must choose a stock'
        if not featuresSelected:
            if err:
                err += ' and at least one feature'
            else:
                err += 'Error: you must choose at least one feature'
        if err:
            # Direct back to index with an error message.
            return render_template('index.html',errormessage=err+'<br>')
        # If we get here we build a URL for our request
        now = datetime.datetime.now().strftime('%Y-%m-%d')
        then = (datetime.datetime.now() - datetime.timedelta(days=OneMonth)).strftime('%Y-%m-%d')
        URL = 'https://www.quandl.com/api/v3/datasets/WIKI/'+stock.upper()+'/data.csv?api_key=xwHMQV1h7w9Pimp2_9vR'+ \
            '&start_date='+then+'&end_date='+now+'&qopts.columns='
        # Append the columns we want
        for i in checks:
            if i in reqmultidict:
                URL += i+','
        URL += 'date'
        # URL is constructed, fetch the data
        r = requests.get(URL)
        if r.status_code != 200:
            err = 'Could not find stock "'+stock.upper()+'"'
            return render_template('index.html',errormessage=err+'<br>')
        df = pd.read_csv(StringIO(r.text))
        # Generate Bokeh plot
        plot = figure(x_axis_type='datetime')
        x = pd.to_datetime(df['Date'])
        print(Viridis4)
        for (Idx,i) in enumerate(checks):
            if i in reqmultidict:
                plot.line(x,df[i],color=Viridis4[Idx],legend=i,line_width=4,line_dash=line_dash[Idx])
        plot.legend.location = 'top_left'
        script,div = components(plot)
        title = 'Showing data for '+stock.upper()
        return render_template('figure.html',title=title,figurescript=script,figurediv=div)

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 33507))
    app.run(host='0.0.0.0', port=port)
