import time
import random
from flask import Flask, render_template, abort
import cat_database


cat_database.create()

rows = 10
cols = 20
cats = cat_database.read()
coin = None


def find_free_cell():
    positions = []
    for row in range(int(rows)):
        for col in range(int(cols)):
            is_free = True
            for _, cat in cats.items():
                if cat['row'] == row and cat['col'] == col:
                    is_free = False
            if is_free:
                positions.append((row, col))
    return list(random.choice(positions))


coin = find_free_cell()

app = Flask('cats')


@app.route('/')
def route():
    return 'приложение Flask'


@app.route('/get_field_size')
def get_field_size():
    return [rows, cols]


@app.route('/get_cats')
def get_cats():
    return cats


@app.route('/get_state/<name>')
def get_state(name):
    if cats.get(name) is not None:
        res = cats[name]['state']
        return res
    else:
        abort(400, 'The cat is not found')


@app.route('/get_coins/<name>')
def get_coins(name):
    if cats.get(name) is not None:
        return str(cats[name]['coins'])
    else:
        abort(400, 'The cat is not found')


@app.route('/get_coin_position')
def get_coin_position():
    return list(coin)


@app.route('/stand/<name>')
def stand(name):
    if cats.get(name) is not None:
        cats[name]['state'] = 'stand'
        return 'ok', 200
    else:
        abort(400, 'The cat is not found')


@app.route('/set_pos/<name>/<x>/<y>/<row>/<col>')
def set_pos(name, x, y, row, col):
    if cats.get(name) is not None:
        cats[name]['x'] = int(x)
        cats[name]['y'] = int(y)
        cats[name]['row'] = int(row)
        cats[name]['col'] = int(col)
        return 'ok', 200
    else:
        abort(400, 'The cat is not found')


@app.route('/inc_coins/<name>')
def inc_coins(name):
    if cats.get(name) is not None:
        cats[name]['coins'] += 1
        return 'ok', 200
    else:
        abort(400, 'The cat is not found')


@app.route('/move/<name>/<direction>')
def move(name, direction):
    exists = cats.get(name) is not None
    direction_is_valid = direction in ['left', 'right', 'up', 'down']
    if exists and direction_is_valid:
        cats[name]['state'] = direction
        return 'ok', 200
    else:
        abort(400, 'The command is not found')


@app.route('/join/<name>')
def join(name):
    if cats.get(name) is None:
        cats[name] = {
            'name':        name,
            'row':         0,
            'col':         0,
            'x':           0,
            'y':           0,
            'time_adding': time.time(),
            'coins':       0,
            'state':       'stand',
        }
        return 'Котенок создан :)'
    else:
        return 'Котенок уже существует.'


@app.route('/update_coin')
def update_coin():
    coin = find_free_cell()
    return list(coin)


def seconds_to_date(seconds):
    days = seconds // (24 * 60 * 60)
    seconds %= (24 * 60 * 60)

    hours = seconds // (60 * 60)
    seconds %= (60 * 60)

    minutes = seconds // 60
    seconds %= 60

    return f'{days} дней {hours} часов {minutes} минут {seconds} секунд'


@app.route('/leaderboard')
def leaderboard():
    sorted_cats = [cat for _, cat in cats.items()]
    sorted_cats.sort(key=lambda cat: cat['coins'], reverse=True)

    durations = []
    current_time = time.time()
    for cat in sorted_cats:
        durations.append(
            seconds_to_date(int(current_time - cat['time_adding'])))

    return render_template('leaderboard.html',
                           cats=sorted_cats,
                           durations=durations,
                           zip=zip)


@app.route('/my_skils_in_AI')
def my_skils():
    return render_template('skils.html')


app.run()
cat_database.write(cats)
