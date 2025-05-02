from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import pandas as pd
from datetime import datetime, timedelta

# === 載入資料集並處理 ===
df = pd.read_csv(
    'app_user_keyword_sentiment/dataset/cna_news_200_preprocessed.csv', sep=',')
df['date'] = pd.to_datetime(df['date'])

# 將 sentiment 分數轉為分類：正面 / 負面 / 中立


def classify_sentiment(score):
    try:
        score = float(score)
        if score > 0.6:
            return '正面'
        elif score < 0.4:
            return '負面'
        else:
            return '中立'
    except:
        return '中立'


df['sentiment_class'] = df['sentiment'].apply(classify_sentiment)

# === 首頁 ===


def home(request):
    return render(request, 'app_user_keyword_sentiment/home.html')


# === API：處理 AJAX 查詢 ===
@csrf_exempt
def api_get_userkey_sentiment(request):
    if request.method == 'POST':
        userkey = request.POST.get('userkey', '')
        cate = request.POST.get('cate', '全部')
        cond = request.POST.get('cond', 'and')
        weeks = int(request.POST.get('weeks', 2))

        if len(userkey.strip()) < 2:
            return JsonResponse({'error': '請輸入至少兩個字的關鍵字'})

        # Step 1: 篩選日期
        max_date = df['date'].max()
        min_date = max_date - timedelta(weeks=weeks)
        df_filtered = df[df['date'] >= min_date]

        # Step 2: 篩選分類
        if cate != '全部':
            df_filtered = df_filtered[df_filtered['category'] == cate]

        # Step 3: 篩選關鍵字
        keywords = userkey.strip().split()
        if cond == 'and':
            for kw in keywords:
                df_filtered = df_filtered[df_filtered['content'].str.contains(
                    kw, na=False)]
        else:  # or
            pattern = '|'.join(keywords)
            df_filtered = df_filtered[df_filtered['content'].str.contains(
                pattern, na=False)]

        # Step 4: 情緒統計數量
        sentiCount = df_filtered['sentiment_class'].value_counts().to_dict()
        sentiCount = {
            'Positive': sentiCount.get('正面', 0),
            'Negative': sentiCount.get('負面', 0),
            'Neutral': sentiCount.get('中立', 0),
        }

        # Step 5: 折線圖資料
        df_filtered['day'] = df_filtered['date'].dt.date

        data_pos = df_filtered[df_filtered['sentiment_class'] == '正面'].groupby(
            'day').size().reset_index(name='count')
        data_neg = df_filtered[df_filtered['sentiment_class'] == '負面'].groupby(
            'day').size().reset_index(name='count')

        # Step 6: 格式轉為 JS 可讀
        data_pos_list = [{'t': date.strftime(
            '%Y-%m-%d'), 'y': count} for date, count in zip(data_pos['day'], data_pos['count'])]
        data_neg_list = [{'t': date.strftime(
            '%Y-%m-%d'), 'y': count} for date, count in zip(data_neg['day'], data_neg['count'])]

        return JsonResponse({
            'sentiCount': sentiCount,
            'data_pos': data_pos_list,
            'data_neg': data_neg_list,
        })

    return JsonResponse({'error': 'Only POST allowed'})
