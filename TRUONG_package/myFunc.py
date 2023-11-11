import plotly.graph_objects as go
import plotly.express as px
import datetime
import numpy as np

def add_line(fig, start_date, end_date, start_price, end_price, name='', color='black', dash='solid'):
    converted_start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    converted_end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    dates= [converted_start_date, converted_end_date]
    
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=[start_price,end_price],
            mode="lines",
            name=name,
            line=go.scatter.Line(color=color, dash=dash),
        )
    )

def add_parallel_line(fig, start_date, end_date, start_price, end_price, height_price, name='', color='rgba(119, 67, 219, 0.4)'):
    converted_start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d')
    converted_end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d')
    dates= [converted_start_date, converted_end_date]
    line = dict(width=0.1, color='black', dash='solid')
    fig.add_trace(
        go.Scatter(
            x=dates,
            y=[start_price, end_price],
            mode="lines",
            line=line,
            legendgroup=name,
            showlegend=False,
        )
    )

    fig.add_trace(
        go.Scatter(
            x=dates,
            y=[start_price-height_price, end_price-height_price],
            mode="lines",
            name=name,
            legendgroup=name,
            line=line,
            fill='tonexty',
            fillcolor=color
        )
    )

def add_SL_or_TP(fig, start_date, end_date, price, take_profit_price, stop_loss_price):
    range_profit = take_profit_price - price
    percent_profit = round(take_profit_price/price*100-100,2)
    
    add_parallel_line(fig, start_date=start_date, end_date=end_date,
                    start_price=price+range_profit, end_price=price+range_profit,
                    height_price=range_profit, name=f'Take Profit: +{percent_profit}%',
                    color='rgba(166, 207, 152, 0.4)')
    
    range_stop_loss = price - stop_loss_price
    percent_loss = round(stop_loss_price/price*100-100,2)
    
    add_parallel_line(fig, start_date=start_date, end_date=end_date,
               start_price=price, end_price=price, height_price=range_stop_loss,
                      name=f'Stop loss: {percent_loss}%', color='rgba(250, 112, 112, 0.4)')

def add_text(fig, date, price, text='', color='black', direction='down'):
    converted_date = datetime.datetime.strptime(date, '%Y-%m-%d')
    fig.add_trace(
        go.Scatter(
            x=[converted_date],
            y=[price],
            mode="markers+text",
            marker_symbol= f'triangle-{direction}',
            marker=dict(
                color=color,
                size=9,
                line=dict(
                    color=color,
                    width=1
                )
            ),
            name= text,
        )
    )

def volume_chart(df, text= 'Khối lượng'):
    fig = px.bar(df, x='time', y='volume')
    fig.update_traces(marker_color='#C70039')
    fig.update_layout(
        title=dict(text=text, font=dict(size=30)),
        height=400,
        )
    return fig

def SMA_cal(df, n, name='SMA', reference='close'):
    sma_name = f'{name}({n})'
    df[sma_name] = df[reference].rolling(n).mean()

def EMA_cal(df, n, name='EMA', first_value='SMA', reference='close'):
    ema_name = f'{name}({n})'
    sma_name = f'{first_value}({n})'
    df[ema_name] = None
    isStart = False
    for i in range(len(df)):
        if not isStart and not np.isnan(df.loc[i,sma_name]):
            df.loc[i,ema_name] = df.loc[i, f'{first_value}({n})']
            isStart = True
        elif isStart == True:
            close = df.loc[i, f'{reference}']
            k = 2/(n+1)
            df.loc[i,ema_name] = close*k + df.loc[i-1,ema_name]*(1-k)
    

def MACD_cal(df):
    SMA_cal(df, 12)
    EMA_cal(df, 12)
    SMA_cal(df, 26)
    EMA_cal(df, 26)
    df['MACD'] = df['EMA(12)'] - df['EMA(26)']
    SMA_cal(df, 9, name='SMA_of_MACD', reference='MACD')
    EMA_cal(df, 9, name='EMA_of_MACD',first_value='SMA_of_MACD', reference='SMA_of_MACD(9)')

def MACD_chart(df):
    MACD_cal(df)
    fig = go.Figure()
    
    macd_trace = go.Scatter(
        x=df['time'],
        y=df['MACD'],
        mode='lines',
        name='MACD'
        )
    fig.add_trace(macd_trace)

    signal_trace = go.Scatter(
        x=df['time'],
        y=df['EMA_of_MACD(9)'],
        mode='lines',
        name='Signal'
        )
    fig.add_trace(signal_trace)

    signal_trace = go.Bar(
        x=df['time'],
        y=df['MACD']-df['EMA_of_MACD(9)'],
        showlegend=False,
        marker_color=('red'),
        name='Histogram'
        )
    fig.add_trace(signal_trace)

    fig.update_layout(
        title=dict(text='Chỉ báo MACD', font=dict(size=30)),
        # height=500,
        )
    return fig