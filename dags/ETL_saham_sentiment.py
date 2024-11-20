import os
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.hooks.postgres_hook import PostgresHook
from datetime import datetime, timedelta
import pandas as pd
import requests
from dotenv import load_dotenv

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'stock_news_sentiment_etl',
    default_args=default_args,
    description='ETL DAG for stock and news data',
    schedule_interval='0 */7 * * *',
    catchup=False,
    tags=['stock', 'news', 'sentiment'],
)

ticker = 'NVDA'
range_days = 20
time_from = datetime.strftime(datetime.now(),'%Y%m%d') + 'T0000'
time_to = datetime.strftime(datetime.now(), '%Y%m%d') + 'T2359'

def extract_task(**kwargs):
    load_dotenv()
    alpha_vantage_api_key = os.getenv('ALPHA_VANTAGE_API_KEY')
    output_size = 'compact'
    
    url_stock = f'https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={ticker}&outputsize={output_size}&apikey={alpha_vantage_api_key}'
    url_news = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers={ticker}&time_from={time_from}&time_to={time_to}&limit=1000&apikey={alpha_vantage_api_key}'
    
    response_news= requests.get(url_news)
    data_news = response_news.json()
    
    response_stock = requests.get(url_stock)
    data_stock = response_stock.json()

    kwargs['ti'].xcom_push(key='stock_data', value=data_stock)
    kwargs['ti'].xcom_push(key='news_data', value=data_news)

def transform_task(**kwargs):
    ti = kwargs['ti']
    data_stock = ti.xcom_pull(key='stock_data', task_ids='extract_task')
    data_news = ti.xcom_pull(key='news_data', task_ids='extract_task')

    # Process stock data
    df_stock = pd.DataFrame.from_dict(data_stock['Time Series (Daily)'], orient='index')
    df_stock.index = pd.to_datetime(df_stock.index)
    df_stock.columns = ['open', 'high', 'low', 'close', 'volume']
    stock_display = df_stock.reset_index()
    stock_display.columns = ['date', 'open', 'high', 'low', 'close', 'volume']
    stock_display['date'] = stock_display['date'].dt.date

    # Process news data
    news_data = []
    for item in data_news.get('feed', []):  # Menggunakan data_news langsung
        for ticker_sent in item.get('ticker_sentiment', []):
            if ticker_sent['ticker'] == ticker and float(ticker_sent['relevance_score']) > 0.25:
                news_data.append({
                    'date': datetime.strptime(item['time_published'], '%Y%m%dT%H%M%S').date(),
                    'title': item['title'],
                    'relevance_score': float(ticker_sent['relevance_score']),
                    'sentiment_score': float(ticker_sent['ticker_sentiment_score']),
                    'sentiment_label': ticker_sent['ticker_sentiment_label']
                })

    news_df = pd.DataFrame(news_data)

    # Aggregate sentiment scores
    sentiment_agg = news_df.groupby('date')['sentiment_score'].mean().reset_index()

    # Merge with stock data where sentiment_score is not null
    final_df = pd.merge(stock_display[['date', 'close']], sentiment_agg, on='date', how='inner')
    final_df = final_df.groupby('date').agg({
        'close': 'last',  # mengambil nilai terakhir untuk close
        'sentiment_score': 'mean'  # mengambil rata-rata untuk sentiment
    }).reset_index()

    # Push data to XCom
    ti.xcom_push(key='df_stock', value=stock_display.to_dict())
    ti.xcom_push(key='df_news', value=news_df.to_dict())
    ti.xcom_push(key='df_final', value=final_df.to_dict())
    ti.xcom_push(key='sentiment_agg', value=sentiment_agg.to_dict())




def load_task(**kwargs):
    ti = kwargs['ti']
    df_stock = pd.DataFrame.from_dict(ti.xcom_pull(key='df_stock', task_ids='transform_task'))
    df_news = pd.DataFrame.from_dict(ti.xcom_pull(key='df_news', task_ids='transform_task'))
    df_final = pd.DataFrame.from_dict(ti.xcom_pull(key='df_final', task_ids='transform_task'))
    df_sentiment_agg = pd.DataFrame.from_dict(ti.xcom_pull(key='sentiment_agg', task_ids='transform_task'))
    
    hook = PostgresHook(postgres_conn_id='stock_market_connection')
    engine = hook.get_sqlalchemy_engine()
    
    df_stock.to_sql('stock_data_10', engine, if_exists='append', index=False)
    df_news.to_sql('news_data_10', engine, if_exists='append', index=False)
    df_final.to_sql('final_data_10', engine, if_exists='append', index=False)
    df_sentiment_agg.to_sql('sentiment_agg_data_10', engine, if_exists='append', index=False)

extract = PythonOperator(
    task_id='extract_task',
    python_callable=extract_task,
    provide_context=True,
    dag=dag
)

transform = PythonOperator(
    task_id='transform_task',
    python_callable=transform_task,
    provide_context=True,
    dag=dag
)

load = PythonOperator(
    task_id='load_task',
    python_callable=load_task,
    provide_context=True,
    dag=dag
)

extract >> transform >> load
