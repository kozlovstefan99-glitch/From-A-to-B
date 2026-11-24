from ursina import *
import subprocess


app = Ursina()

music = Audio(
    'src/classic_music.mp3',
    loop=True,
    autoplay=True
)

def show_menu():
    # показать кнопки
    menu_text.enabled = True
    play_button2.enabled = True
    settings_button.enabled = True
    exit_button.enabled = True


def hide_menu():
    # спрятать кнопки
    menu_text.enabled = False
    play_button2.enabled = False
    settings_button.enabled = False
    exit_button.enabled = False


# def start_game():
#     print("Запуск игры...")
#     # запускаем отдельный файл game.py
#     subprocess.Popen([sys.executable, "game_for 5 lesson.py"])
#     # application.quit()

def start_runer():
    print("Запуск игры...")
    # запускаем отдельный файл game.py

    subprocess.Popen([sys.executable, "src/main.py", str(slider_2.value), str(slider_3.value),
                      str(seed_input.text), str(size_slider.value), str(mode_slider.value)]
                     )
    # application.quit()



def close_settings():
    settings_panel.enabled = False
    show_menu()
# Окно настроек (по умолчанию скрыто)


# settings_panel = WindowPanel(
#     title='Настройки',
#     content=(
#         Text('скорость игрока'),
#         slider_,
#         Button(text='Закрыть', on_click=close_settings),
#     ),
#     enabled=False
# )
slider_ = Slider(min=0, max=10, default=3, step=1)
slider_2 = Slider(min=1, max=3, default=1, step=1, y=2)
slider_3 = Slider(min=0, max=10, default=5, step=1, y=3)

rs = random.randint(1, 100000)

seed_input = InputField(default_value=f"{rs}", limit_content_to="0123456789", character_limit=30)
size_slider = Slider(min=700, max=1000, default=800, step=100, y=5)
mode_slider = Slider(min=1, max=3, default=1, step=1, y=6)


seed_input.text_field.scale *= 0.8

settings_panel = WindowPanel(
    title='Настройки',
    y=0.5,
    content=(
        Text('гомкость'),
        slider_,
        Text('сложность'),
        slider_2,
        Text('туман'),
        slider_3,
        Text('seed'),
        seed_input,
        Text('size'),
        size_slider,
        Text('mode'),
        mode_slider,
        Button(text='Закрыть', on_click=close_settings),
    ),
    enabled=False
)

# Кнопка открытия настроек
def open_settings():
    settings_panel.enabled = True
    hide_menu()

settings_button = Button(
    text='Настройки',
    scale=(0.3, 0.1),
    y=-0.2,
    on_click=open_settings
)

def update():
    music.volume = slider_.value * 0.1

def quit_game():
    application.quit()

def create_menu():
    # Меню
    menu_text = Text("Главное меню", scale=2, y=0.4, position=(-0.2, 0.35, 0))
    # play_button = Button(text="Играть", scale=(0.3, 0.1), y=0.2, color=color.azure)
    play_button2 = Button(text="Играть в Побег", scale=(0.3, 0.1), y=0, color=color.azure)
    # settings_button = Button(text="Настройки", scale=(0.3, 0.1), y=-0.2, color=color.orange)
    exit_button = Button(text="Выход", scale=(0.3, 0.1), y=-0.4, color=color.red)

    # Привязка функций
    # play_button.on_click = start_game
    play_button2.on_click = start_runer
    settings_button.on_click = open_settings
    exit_button.on_click = quit_game
    return menu_text, play_button2, exit_button
# Функции для меню
menu_text, play_button2, exit_button = create_menu()

# if open_settings():
#     difficulty = Text("сложность:легкая", scale=2, y=0.4, position=(-0.2, 0.35, 0))
#     player_speed = Text("скорость игрока:1", scale=2, y=0.2, position=(-0.2, 0.35, 0))
#     enemy_speed = Text("скорость врагов:1.5", scale=2, y=0, position=(-0.2, 0.35, 0))
if __name__ == '__main__':
    show_menu()
    app.run()
