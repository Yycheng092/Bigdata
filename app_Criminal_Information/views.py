import csv
import io
from datetime import datetime
from django.shortcuts import render, redirect
from .forms import UploadCSVForm
from .models import CriminalCase


def upload_csv(request):
    if request.method == 'POST':
        form = UploadCSVForm(request.POST, request.FILES)
        if form.is_valid():
            csv_file = request.FILES['file']
            if not csv_file.name.endswith('.csv'):
                return render(request, 'upload_csv.html', {'form': form, 'error': '請上傳 CSV 檔案'})
            data = csv_file.read().decode('utf-8-sig')
            io_string = io.StringIO(data)
            reader = csv.reader(io_string)
            next(reader)  # 跳過標題
            for row in reader:
                CriminalCase.objects.create(
                    case_type=row[0],
                    year=int(row[1]),
                    date=datetime.strptime(row[2], '%Y/%m/%d').date(),
                    city=row[3],
                    district=row[4]
                )
            return redirect('upload_success')
    else:
        form = UploadCSVForm()
    return render(request, 'upload_csv.html', {'form': form})
