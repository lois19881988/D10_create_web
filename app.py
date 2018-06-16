from flask import Flask, render_template, request
import os as os
import quandl
import pandas as pd
from bokeh.plotting import ColumnDataSource, Figure
from bokeh.embed import components

# Defaults
ticker_default = 'GOOGL'
end_date_year_default = '2017'
end_date_month_default = '12'
end_date_day_default = '31'
days_track_default = '365'

def gen_plot(ticker, features, 
    end_date_year, end_date_month, end_date_day, days_track):
    quandl.ApiConfig.api_key = '7JbKcz5VsYWrmjocYMsx'
    
    stock_indices = {'Open':['Opening Price', '#440154'],
                     'Close':['Closing Price', '#30678D'],
                     'High':['Daily High', '#35B778'],
                     'Low': ['Daily Low', '#0A333D']}
    
    end_date_list = [end_date_year, end_date_month, end_date_day]
    end_date = '-'.join(end_date_list)
    start_date = (pd.to_datetime(end_date) - pd.DateOffset(days = int(days_track))).strftime('%Y-%m-%d')    
    
    mydata = pd.DataFrame(quandl.get('WIKI/' + ticker, 
                                     start_date = start_date, 
                                     end_date = end_date)).reset_index()
    mydata['Date'] = pd.to_datetime(mydata['Date'])
    mydata = mydata[['Date',*features]]
    
    data = {'xs': [mydata['Date'] for col in features],
            'ys': [mydata[col] for col in features],
            'labels': [stock_indices[col][0] for col in features],
            'colors': [stock_indices[col][1] for col in features]}
    
    source = ColumnDataSource(data)
    
    
    p = Figure(plot_width=800, plot_height=500, x_axis_type="datetime",
               x_axis_label = 'Initial', title = 'Initial')   
    p.multi_line(xs='xs', ys='ys', legend='labels', color = 'colors', source = source)
    p.yaxis.axis_label = ticker
    p.xaxis.axis_label = 'Time'
    p.title.text = 'Different indices of ' + ticker + ': '\
                   + start_date + ' to ' + end_date  
    
    return p

app = Flask(__name__)

'''
@app.route('/')
def index():
  return render_template('index.html')
'''
@app.route('/about')
def about():
  return render_template('about.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        return render_template('userinfo.html', 
                               ticker_default=ticker_default, 
                               end_date_year_default=end_date_year_default, 
                               end_date_month_default=end_date_month_default, 
                               end_date_day_default=end_date_day_default, 
                               days_track_default=days_track_default)
    else:       
        ticker = request.form['ticker'] if request.form['ticker'] else ticker_default
        end_date_year = request.form['end_year'] if request.form['end_year'] else end_date_year_default
        end_date_month = request.form['end_month'] if request.form['end_month'] else end_date_month_default
        end_date_day = request.form['end_day'] if request.form['end_day'] else end_date_day_default
        days_track = request.form['days_track'] if request.form['days_track'] else days_track_default
        features = request.form.getlist('features')
        
        p = gen_plot(ticker, features, end_date_year, end_date_month, end_date_day, days_track)
        script, div = components(p)
        report_html = render_template('user_report.html', script=script, div=div)
        
        return report_html

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
