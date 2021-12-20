import json


def revenue_class(revenue):
    if revenue <= 1000000:
        return 0
    elif 1000000 < revenue <= 5000000:
        return 1
    elif 5000000 < revenue <= 10000000:
        return 2
    elif 10000000 < revenue <= 100000000:
        return 3
    elif 100000000 < revenue:
        return 4
    
def reverse_class_revenue(class_):
    if class_ == 0:
        return '< 1M'       # 83,39%
    elif class_ == 1:
        return '1M - 5M'    # 10,79%
    elif class_ == 2:
        return '5M - 10M'   # 2,33%
    elif class_ == 3:
        return '10M - 100M' # 3,06%
    elif class_ == 4:
        return '> 100M'     # 0.40%
    

def employee_class(employee):
    if employee <= 100:
        return 0
    elif 100 < employee <= 300:
        return 1
    elif 300 < employee <= 500:
        return 2
    elif 500 < employee <= 700:
        return 3
    elif 700 < employee:
        return 4


def reverse_class_employee(class_):
    if class_ == 0:
        return '<= 100'       # 83,39%
    elif class_ == 1:
        return '100 - 300'    # 10,79%
    elif class_ == 2:
        return '300 - 500'   # 2,33%
    elif class_ == 3:
        return '500 - 700' # 3,06%
    elif class_ == 4:
        return '> 700'     # 0.40%