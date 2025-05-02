import pandas as pd
import os
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.shortcuts import render
import ast  # 將字串轉為 list of tuple

# 首頁 HTML


def home(request):
    return render(request, 'app_top_voice/home.html')


@csrf_exempt
def api_cate_topvoice(request):
    if request.method == "POST":
        keyword = request.POST.get("keyword", "").strip()

        if not keyword:
            return JsonResponse({"status": "error", "message": "請輸入關鍵字"})

        try:
            # CSV 路徑
            base_dir = os.path.dirname(os.path.abspath(__file__))
            csv_path = os.path.join(
                base_dir, 'dataset', 'cna_news_preprocessed.csv')

            # 讀取資料
            df = pd.read_csv(csv_path)

            count = 0  # 出現的新聞筆數
            total_freq = 0  # 該詞總出現次數
            max_freq = 0  # 單篇新聞中最高出現次數
            photo_link = None
            news_link = None  # 新增的新聞連結

            for _, row in df.iterrows():
                top_key_freq = row.get('top_key_freq')
                if pd.isna(top_key_freq):
                    continue

                try:
                    freq_list = ast.literal_eval(top_key_freq)
                    for word, freq in freq_list:
                        if word == keyword:
                            count += 1
                            total_freq += freq
                            if freq > max_freq:
                                max_freq = freq
                                photo_link = row.get('photo_link')  # 找出圖片
                                news_link = row.get('link')         # 找出連結
                            break
                except:
                    continue

            if count == 0:
                return JsonResponse({
                    "status": "error",
                    "message": f"關鍵字「{keyword}」未出現在資料中"
                })

            return JsonResponse({
                "status": "success",
                "keyword": keyword,
                "count": count,
                "frequency": total_freq,
                "photo_link": photo_link,
                "link": news_link
            })

        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})

    return JsonResponse({"status": "error", "message": "請使用 POST 方法"})


@csrf_exempt
def api_news_volume_data(request):
    try:
        keyword = request.POST.get("keyword", "").strip()

        base_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(base_dir, 'dataset',
                                'cna_news_preprocessed.csv')
        df = pd.read_csv(csv_path)

        if keyword:
            def contains_keyword(freq_list_str):
                try:
                    freq_list = ast.literal_eval(freq_list_str)
                    return any(word == keyword for word, _ in freq_list)
                except:
                    return False

            df = df[df['top_key_freq'].apply(contains_keyword)]

        category_count = df['category'].value_counts().to_dict()
        date_count = df['date'].value_counts().sort_index().to_dict()

        return JsonResponse({
            'status': 'success',
            'category_count': category_count,
            'date_count': date_count
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


print("app_top_voice--XXX聲量載入成功!")
