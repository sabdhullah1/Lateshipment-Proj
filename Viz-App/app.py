import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
from matplotlib.pyplot import cm
import plotly.figure_factory as ff
import plotly.graph_objs as go
import MySQLdb

db=MySQLdb.connect(user="root",passwd="",db="test")
cursor = db.cursor()
cursor.execute("select year(birthdate) yr, sex, count(id) cnt from table1 group by yr,sex")
birth_df=pd.DataFrame(list(cursor.fetchall()),columns=["yr","sex","cnt"])
print('Birth Success!!!!')
cursor.execute("select year(deathdate) yr, sex, count(id) cnt from table1 group by yr,sex")
death_df=pd.DataFrame(list(cursor.fetchall()),columns=["yr","sex","cnt"])
print('Death Success!!!!')
cursor.execute("select birthdate,count(id) from table1 group by birthdate ")
df1=pd.DataFrame(list(cursor.fetchall()),columns=["birthdate","birthcount"])
print('DF1 Success!!!!')
cursor.execute("select deathdate,count(id) from table1 group by deathdate ")
df2=pd.DataFrame(list(cursor.fetchall()),columns=["deathdate","deathcount"])
print('DF2 Success!!!!')
population_df=pd.DataFrame({"date":pd.date_range("1900-01-01","1999-12-31")})
population_df=pd.merge(left=population_df,right=df1,left_on="date",right_on="birthdate",how="left")
population_df=pd.merge(left=population_df,right=df2,left_on="date",right_on="deathdate",how="left")
population_df=population_df[["date","birthcount","deathcount"]]

population_df=population_df.fillna(0)
population_df["population"]=population_df["birthcount"]-population_df["deathcount"]
population_df["population"]=np.cumsum(population_df["population"])
print(population_df[:5])

app=dash.Dash()
app.layout=html.Div([
                        html.Div([html.H1('Births and Deaths Visualiation by Year')],style={'display':'inline-block','marginLeft':400}),
                        html.Div([
                                    html.Div([
                                                html.H4('Display By: '),
                                                dcc.Dropdown(id='display-param',
                                                             options=[{'label':'Birth','value':'birth'},{'label':'Death','value':'death'},{'label':'Population','value':'population'}],
                                                             value='birth')
                                    ], style={'display':'inline-block','width':'16%','marginTop':30,'marginLeft':25}),
                                    html.Div([
                                                dcc.Graph(id='time-series'),
                                                dcc.Graph(id='bar-chart')
                                    ], style={'display':'inline-block','width':'80%','float':'right'})
                        ])
                    ])

def get_population_series():
    global population_df
    print (population_df[:5])
    maxi = np.max(population_df['population'])
    maxi_date = np.where(population_df==maxi)[0]
    print ('#'*100, maxi_date)
    print('Max Population on ', population_df['date'].iloc[maxi_date], '  ---->  ',str(population_df['date'].iloc[maxi_date]))
    return go.Figure(data=[go.Scatter(x=list(population_df['date']),
                                      y=list(population_df['population']),
                                      mode='lines+markers')],
                     layout=go.Layout(title='Highest Population is '+str(maxi)+' on '+ str(population_df['date'].iloc[maxi_date[0]])[:10]
                                      # , xaxis=dict(
                                      #           rangeselector=dict(
                                      #               buttons=list([
                                      #                   dict(count=1,
                                      #                        label='1m',
                                      #                        step='month',
                                      #                        stepmode='backward'),
                                      #                   dict(count=6,
                                      #                        label='6m',
                                      #                        step='month',
                                      #                        stepmode='backward'),
                                      #                   dict(count=1,
                                      #                       label='YTD',
                                      #                       step='year',
                                      #                       stepmode='todate'),
                                      #                   dict(count=1,
                                      #                       label='1y',
                                      #                       step='year',
                                      #                       stepmode='backward'),
                                      #                   dict(step='all')
                                      #               ])
                                      #           ),
                                      #           rangeslider=dict(),
                                      #           type='date')
                                    ))

@app.callback(
    dash.dependencies.Output('time-series','figure'),
    [dash.dependencies.Input('display-param','value')])
def get_time_series(type):
    global birth_df, death_df, population_df
    if type == 'birth':
        df = birth_df
    elif type=='death':
        df = death_df
    else:
        return get_population_series()
        # df = population_df
    agg_df = df.groupby('yr').agg({'cnt':{'cnt':np.sum}}).reset_index()
    agg_df.columns = ['yr','cnt']
    print (agg_df)
    return go.Figure(data=[go.Scatter(x=list(agg_df['yr']),
                                      y=list(agg_df['cnt']),
                                      mode='lines+markers')],
                    layout=go.Layout(title=type.title()+'s by Year'))
@app.callback(
    dash.dependencies.Output('bar-chart','figure'),
    [dash.dependencies.Input('display-param','value'),
    dash.dependencies.Input('time-series','hoverData')
    ])
def get_bar_chart(type,hover_data):
    print (hover_data)
    global cursor
    yr = hover_data['points'][-1]['x']
    if type=="birth":
        cursor.execute("select month(T1.birthdate) mth, T1.sex, count(T1.id) from (select * from table1  where year(birthdate)="+str(yr)+") T1 group by mth, sex")
    elif type=="death" :
        cursor.execute("select month(T1.birthdate) mth, T1.sex, count(T1.id) from (select * from table1  where year(deathdate)="+str(yr)+") T1 group by mth, sex")
    else:
        return get_population_chart(yr)
    df = pd.DataFrame(list(cursor.fetchall()),columns=["month","sex","count"])
    df = df.pivot('month','sex').reset_index()
    df.columns = ['month','F','M']
    return go.Figure(data= [go.Bar(x=df['month'],
                                  y =df['F'],
                                  name='Female'),
                            go.Bar(x=df['month'],
                                  y =df['M'],
                                  name='Male')],
                    layout = go.Layout(title='Distribution across Month and Sex for Year '+str(yr),
                                        barmode='stack'))

def get_population_chart(date):
    global population_df
    date=pd.to_datetime(date)
    df = population_df[population_df['date']<=date]
    births = np.sum(df['birthcount'])
    deaths = np.sum(df['deathcount'])
    date = str(date)[:10]
    return go.Figure(data=[go.Bar(x=['Births','Deaths'],
                                  y=[births, deaths])],
                    layout=go.Layout(title='Births and Deaths till '+date))


if __name__ == '__main__':
    print ('*'*100)
    print ('In Main Fn!!')
    app.run_server()
