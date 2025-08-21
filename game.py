import pgzrun
import requests
from random import randrange


def clamp(x, left, right):
    return min(max(left, x), right)


class Cat:

    def __init__(self, name, pos, images):

        self.name = name

        self.images = images
        self.current_image = 0
        self.actor = Actor(self.images[self.current_image])

        self.direction = (0, 0)
        self.speed = 1
        self.switch_factor = 0
        self.switch_speed = 0.2

        self.start_pos = pos
        self.pos = pos
        self.running = False

    def draw(self):
        self.actor.image = self.images[self.current_image]
        self.actor.pos = self.pos
        self.actor.draw()
        text_pos = (self.pos[0], self.pos[1] - 32)
        screen.draw.text(
            self.name, center=text_pos, color='black', fontsize=25)

    def next_image(self):
        self.switch_factor += self.switch_speed
        if self.switch_factor >= 1:
            self.switch_factor = 0
            self.current_image = \
                (self.current_image + 1) % (len(self.images) - 1)

    def start(self, animation_images, stop_image, direction):
        self.images = animation_images + [stop_image]
        self.current_image = 0
        self.direction = direction
        self.start_pos = self.pos
        self.running = True

    def move(self):
        prev_pos = self.pos
        self.pos = (self.pos[0] + self.direction[0] * self.speed,
                    self.pos[1] + self.direction[1] * self.speed)
        self.pos = (clamp(self.pos[0], 16, WIDTH - 16),
                    clamp(self.pos[1], 16, HEIGHT - 16))
        if self.pos[0] == prev_pos[0] and self.pos[1] == prev_pos[1]:
            self.stop()
            return None

        self.next_image()

        space_x = abs(self.start_pos[0] - self.pos[0])
        space_y = abs(self.start_pos[1] - self.pos[1])
        if space_x > 32 or space_y > 32:
            self.pos = (
                self.start_pos[0] + self.direction[0] * 32,
                self.start_pos[1] + self.direction[1] * 32)
            self.stop()

    def stop(self):
        self.running = False
        self.images = [self.images[-1]]
        self.current_image = 0
        requests.get(f'http://{host}:{port}/stand/{self.name}')
        x = self.pos[0]
        y = self.pos[1]
        row = (x - 16) // 32
        col = (y - 16) // 32
        requests.get(
            f'http://{host}:{port}/set_pos/{self.name}/{x}/{y}/{row}/{col}')

    def colliderect(self, other):
        self.actor.pos = self.pos
        return self.actor.colliderect(other)


def init_field_size():
    global WIDTH, HEIGHT
    size = requests.get(f'http://{host}:{port}/get_field_size')
    rows, cols = eval(size.text)
    WIDTH = 32 * cols
    HEIGHT = 32 * rows


def init_coin():
    pos = requests.get(f'http://{host}:{port}/get_coin_position')
    row, col = eval(pos.text)
    coin.x = 16 + 32 * col
    coin.y = 16 + 32 * row


def update_coin():
    pos = requests.get(f'http://{host}:{port}/update_coin')
    row, col = eval(pos.text)
    coin.x = 16 + 32 * col
    coin.y = 16 + 32 * row


def update_cat_dict():
    update_cats = requests.get(f'http://{host}:{port}/get_cats')
    update_cats = eval(update_cats.text)
    for k, v in update_cats.items():
        if cats.get(k) is None:
            x = 16 + 32 * v['row']
            y = 16 + 32 * v['col']
            cats[k] = Cat(k, (x, y), ['wait_down/0'])


def draw():
    screen.fill((255, 255, 255))
    coin.draw()
    for _, cat in cats.items():
        cat.draw()


def update():

    update_cat_dict()

    for _, cat in cats.items():
        if not cat.running:

            # Этот request слишком часто вызвается, поэтому может обратиться
            # к серверу по сокету, который уже используется (во всяком случае
            # у меня была подобная ошибка), поэтому выставляем
            # timeout в 1.
            state = requests.get(
                f'http://{host}:{port}/get_state/{cat.name}', timeout=1)

            if state.text != 'stand':
                direction = {
                    'left':  (-1, 0),
                    'right': (1, 0),
                    'up':    (0, -1),
                    'down':  (0, 1)
                }
                cat.start([f'walk_{state.text}/{i}' for i in range(4)],
                          f'wait_{state.text}/0',
                          direction[state.text])
        else:
            cat.move()

        if cat.colliderect(coin):
            requests.get(f'http://{host}:{port}/inc_coins/{cat.name}')
            update_coin()


host = None
port = None
coin = Actor("coin.png")
cats = {}

with open('settings.txt') as file:
    settings = eval(file.read())
    host = settings['host']
    port = settings['port']

try:
    init_field_size()
    init_coin()
except requests.exceptions.RequestException:
    print('Неудалось подключиться к серверу. Возможно он не запущен.')
    exit()

pgzrun.go()
