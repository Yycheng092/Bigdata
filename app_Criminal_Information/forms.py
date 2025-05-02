from django import forms


class UploadCSVForm(forms.Form):
    file = forms.FileField(label="選擇 CSV 檔案")
