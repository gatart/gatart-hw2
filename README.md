# Blogicum
### Author: gatart
Портал для личных блогов

---

## Установка модуля

```bash
git clone git@github.com:gatart/django_sprint1.git
pip install -r requirements.txt
```

## Запуск модуля
```bash
python blogicum/manage.py migrate
python blogicum/manage.py loaddata db.json
python blogicum/manage.py runserver
```

In this project I implemented:
1) Mixins for GenericViews
2) ModelForms for Post requests
3) Admin Panel
4) Confirmation code by mail
