import os
import sys


def main():
    # 告訴 Django 使用 website_configs/settings.py 作為設定檔
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'website_configs.settings')

    try:
        from django.core.management import execute_from_command_line
    #  若果沒有安裝 Django，則會引發 ImportError
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
