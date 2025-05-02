# app_Criminal_Information/models.py
from django.db import models


class CriminalCase(models.Model):
    case_type = models.CharField(max_length=100)           # 案類
    year = models.IntegerField()                            # 發生年度
    date = models.DateField()                               # 發生日期
    city = models.CharField(max_length=50)                  # 發生縣市
    district = models.CharField(max_length=50)              # 發生鄉鎮市區

    def __str__(self):
        return f"{self.case_type} - {self.city} {self.district} ({self.date})"
