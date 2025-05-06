from django.db.models import Max
from datetime import timedelta
from app_user_keyword_db.models import NewsData
from collections import Counter
from .models import TopPerson
import ast
import numpy as np  # ← 加入 np 的 import
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib import messages

allowedNE = ['name']
news_categories = ['政治', '社會地方', '財經', '運動', '娛樂影劇', '科技', '全部']


def home(request):
    return render(request, 'app_top_person_db/home.html')


@csrf_exempt
def api_get_topPerson(request):
    cate = request.POST.get('news_category')
    topk = request.POST.get('topk')
    topk = int(topk)

    chart_data, wf_pairs = get_category_topPerson_db(cate, topk)
    print("wf_pairs:", wf_pairs)

    if not wf_pairs:
        return JsonResponse({'error': 'No data found for the specified category.'})

    return JsonResponse({
        'chart_data': chart_data,
        'wf_pairs': wf_pairs
    })


def get_category_topPerson_db(cate, topk):
    queryset = TopPerson.objects.filter(category=cate).values('top_keys')
    if queryset.exists():
        try:
            top_keys_str = queryset[0]['top_keys']
            wf_pairs = ast.literal_eval(top_keys_str)[0:topk]
        except Exception as e:
            print("解析 top_keys 時發生錯誤：", e)
            wf_pairs = []
    else:
        wf_pairs = []

    try:
        words = [w for w, f in wf_pairs]
        freqs = [f for w, f in wf_pairs]
    except Exception as e:
        print("組合 chart_data 時出錯：", e)
        words, freqs = [], []

    chart_data = {
        "category": cate,
        "labels": words,
        "values": freqs
    }
    return chart_data, wf_pairs


def calculate_top_person(request):
    latest_date = NewsData.objects.aggregate(max_date=Max('date'))['max_date']
    start_date = latest_date - timedelta(weeks=4)

    top_cate_ner_words = {}
    words_all = []

    for category in news_categories:
        entities_list = list(
            NewsData.objects.filter(category=category)
            .filter(date__gte=start_date, date__lte=latest_date)
            .values_list('entities', flat=True)
        )

        words_group = []
        for entities in entities_list:
            try:
                parsed = eval(entities)  # 或 ast.literal_eval(entities)
                for item in parsed:
                    words_group.append(item)
            except Exception as e:
                print("entities eval 錯誤：", entities, e)

        words_all += words_group
        topwords = ne_word_frequency(words_group)
        top_cate_ner_words[category] = topwords

    topwords_all = ne_word_frequency(words_all)
    top_cate_ner_words['全部'] = topwords_all

    for category, top_ners in top_cate_ner_words.items():
        top_keys_str = str(top_ners)
        try:
            obj = TopPerson.objects.get(category=category)
            obj.top_keys = top_keys_str
            obj.save()
        except TopPerson.DoesNotExist:
            TopPerson.objects.create(category=category, top_keys=top_keys_str)

    messages.success(request, "Top person calculated and saved successfully")
    return redirect("app_top_person_db:home")


def ne_word_frequency(a_news_ne):
    filtered_words = []
    for item in a_news_ne:
        try:
            if isinstance(item, dict):  # ✅ 正確處理 dict 結構
                ner = item.get('entity_group')
                word = item.get('word')
            elif isinstance(item, (list, tuple)):
                ner, word = item
            else:
                continue

            if (len(word) >= 2) and (ner in allowedNE):
                filtered_words.append(word)
        except Exception as e:
            print("ne_word_frequency unpack error：", item, e)

    counter = Counter(filtered_words)
    return counter.most_common(20)


def NerToken(word, ner, idx):
    return ner, word


print("app_news_analysis--類別熱門人物db載入成功!")
