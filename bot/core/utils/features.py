import datetime
import matplotlib.pyplot as plt

# HOUR DISTRIBUTION COEF
def form_timelist():
    # задаем начальную точку
    current_time = datetime.time(0, 0)

    timestamps = []
    periods = 0

    # каждые полчаса записываем в список 
    while periods < 48:
        timestamps.append(current_time.strftime('%H:%M'))
        current_time = (datetime.datetime.combine(datetime.date(1, 1, 1), current_time) + datetime.timedelta(minutes=30)).time()
        periods+=1

    return timestamps

def fill_plot_values():
    
    work = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 44000, 62000, 115000, 161000, 245000, 250000, 185000, 175000, 130000, 125000, 105000, 100000, 101000, 102000, 102000, 101000, 107000, 112000, 122000, 126000, 140000, 154000, 185000, 215000, 255000, 237000, 173000, 145000, 125000, 100000, 86000, 72000, 62000, 48000, 35000, 0, 0, 0]
    rest = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 30000, 40000, 50000, 55000, 72000, 82000, 85000, 95000, 80000, 95000, 80000, 95000, 100000, 105000, 107000, 115000, 118000, 122000, 125000, 130000, 123000, 121000, 123000, 125000, 125000, 120000, 105000, 102000, 100000, 92000, 86000, 75000, 80000, 60000, 50000, 0, 0, 0]
    
    return work, rest

def get_day_plot():

    pred = 80000

    date = datetime.datetime.strptime("2024-04-04", '%Y-%m-%d')
    
    timestamps = form_timelist()
    workday, weekday = fill_plot_values()

    if date.weekday in (5, 6): 
        x = [i / sum(workday) * pred for i in weekday] 
    else:
        x = [i / sum(workday) * pred for i in workday] 
    
    
    plt.figure(figsize=(15, 6))
    plt.plot(timestamps, x, color='b', marker='o')
    plt.xlabel('Время')
    plt.ylabel('Количество пассажиров')
    plt.title('Пассажиропоток')
    plt.legend()
    plt.xticks(rotation=45)
    plt.grid(True)
    plt.savefig('docs/day_plot.png')

    return 'docs/day_plot.png'