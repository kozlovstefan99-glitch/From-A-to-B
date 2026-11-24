from test import BiomeGeneratorTest, Castle
from ursina import *
import sys
from ursina.prefabs.first_person_controller import FirstPersonController
from perlin_noise import PerlinNoise

app = Ursina()

sky = Sky()

dificulty = int(sys.argv[1])
fog = int(sys.argv[2])
seed = int(sys.argv[3])
size = int(sys.argv[4])
mode = int(sys.argv[5])

DirectionalLight(color=color.black, position=(-100, 100, 0), rotation=(60, 0, 0))

player_HP = 100
max_HP = 100
camera.clip_plane_far = 100

castle_pos = (random.uniform(-(size//2 - 50), -(size//2 - 20)), 5, random.randint(-(size//2 - 20), size//2 - 20))

if mode == 2:
    sky.color = color.black
    player_HP = 100
    max_HP = 100
    camera.clip_plane_far = 50
if mode == 3:
    sky.color = color.red
    player_HP = 1
    max_HP = 50
    camera.clip_plane_far = 50


generator = BiomeGeneratorTest(seed=seed, size=size, castle_pos=(castle_pos[0], castle_pos[2]), roads=4, road_width=12)

village_pos = (random.randint(size//2 - 50, size//2 - 20), random.randint(-(size//2 - 20), size//2 - 20))
b_village = generator.get_biome_type(village_pos[0], village_pos[1])
while b_village == "mountain":
    b_village = generator.get_biome_type(village_pos[0], village_pos[1])
    village_pos = (random.randint(250, 280), random.randint(-280, 280))
village_y = 10

generator.village_pos = (village_pos[0], village_y, village_pos[1])

village = generator.village(village_pos, 4, 3, 8, village_y)
castle = Castle(castle_pos)
terrain = generator.generate()

player = FirstPersonController(position=(castle_pos[0], 100, castle_pos[2]), collider="box")
player_model = Entity(model="cube", scale=(1, 2, 1), position=(castle_pos[0], 100, castle_pos[2]), color=color.blue, parent=player)

if not fog == 0:
    scene.fog_density = fog / 10
    scene.fog_color = color.gray
def create_enemies():
    enemies = []
    pos = (random.randint(-(size//2), size//2), 0, random.randint(-(size//2), size//2))
    for i in range(10):
        offset = (random.uniform(-5, 5), 0, random.uniform(-5, 5))
        enemy = Entity(model="cube", scale=(1, 2, 1), position=pos + offset, collider="box", color=color.red)
        enemies.append(enemy)
    return enemies

def create_enemies_to_village():
    enemies_to_village = []
    pos = (castle_pos[0], 0, castle_pos[2] - 20)
    for i in range(10):
        offset = (random.uniform(-5, 5), 0, random.uniform(-5, 5))
        enemy = Entity(model="cube", scale=(1, 2, 1), position=pos + offset, collider="box", color=color.violet)
        enemies_to_village.append(enemy)
    return enemies_to_village

def enemy_move(enemy):
    biomee = generator.get_biome_type(enemy.x, enemy.z)
    if biomee == "desert":
        octaves = 6
        height_mult = 5
    elif biomee == "plains":
        octaves = 6
        height_mult = 10
    elif biomee == "ice_biome":
        octaves = 6
        height_mult = 6
    else:
        octaves = 8
        height_mult = 20
    pn = PerlinNoise(octaves=octaves, seed=seed)
    noise = generator.get_height(enemy.x, enemy.z, pn)[0]
    enemy.y = ((noise + 1) / 2 * height_mult) + 0.7


    if math.sqrt((player.x - enemy.x) ** 2 + (player.z - enemy.z) ** 2) < 20 and not enemy.intersects(player).hit:
        offset_x, offset_z = enemy.x - player.x, enemy.z - player.z
        if not offset_x > 0.1:
            enemy.x += time.dt * 6

        if not offset_x < -0.1:
            enemy.x -= time.dt * 6

        if not offset_z > 0.1:
            enemy.z += time.dt * 6

        if not offset_z < -0.1:
            enemy.z -= time.dt * 6

def create_villagers():
    villagers = []
    pos = (village_pos[0], 0, village_pos[1])
    while len(villagers) < 10:
        d_v = False
        offset = (random.uniform(-10, 10), 0, random.uniform(-10, 10))
        villager = Entity(model="cube", scale=(1, 200, 1), position=pos + offset, collider="box", color=color.blue)
        for house in village:
            if villager.intersects(house).hit:
                d_v = True
        if d_v:
            destroy(villager)
            continue
        villager.scale_y = 2
        villagers.append(villager)
    return villagers

villagers = create_villagers()

for villager in villagers:
    pos_x, pos_z = villager.x, villager.z
    patrol = [(pos_x, village_y + 1, pos_z)]
    for i in range(3):
        npos_x, npos_z = patrol[i][0] + random.uniform(-10, 10), patrol[i][2] + random.uniform(-10, 10)

        while not math.sqrt((npos_x - village_pos[0]) ** 2 + (npos_z - village_pos[1]) ** 2) < 25:
            npos_x, npos_z = pos_x + random.uniform(-10, 10), pos_z + random.uniform(-10, 10)
        patrol.append((npos_x, village_y + 1, npos_z))


    patrol_sequence = Sequence(
        Func(villager.animate_position, patrol[0], duration=2, curve=curve.in_out_sine),
        Wait(4),
        Func(villager.animate_position, patrol[1], duration=2, curve=curve.in_out_sine),
        Wait(4),
        Func(villager.animate_position, patrol[2], duration=2, curve=curve.in_out_sine),
        Wait(4),
        Func(villager.animate_position, patrol[3], duration=2, curve=curve.in_out_sine),
        Wait(4),
        loop=True
    ).start()





if dificulty == 1:
    duration = 180
elif dificulty == 2:
    duration = 160
else:
    duration = 140

start_time = time.time()

# текст на экране
timer_text = Text(text=str(duration),position=(-0.65,-0.40),origin=(0,0), scale=2, color=color.white)


# health_text = Text(text=f"Здоровье:{player_HP}",position=(-0.60,0.40),origin=(0,0), scale=2.5, color=color.green)
coordinates = Text(text="0, 0",position=(-0.60,0.40),origin=(0,0), scale=2.5, color=color.green)

health_bar_bg = Entity(
    parent=player,
    model='quad',
    color=color.black,
    scale=(2, 0.2),
    position=(0, 3.4, 2.5),
    billboard=True
)

health_bar = Entity(
    parent=player,
    model='quad',
    color=color.green,
    scale=(1.8, 0.15),
    position=(0, 3.375, 2.45),
    billboard=True
)

HP_timer = 0
end = "время вышло ¯\_(0-0)_/¯"
lose = False
win = False
all_enemies = []
for i in range(10):
    enemies = create_enemies()
    all_enemies.append(enemies)

enemies_to_village = create_enemies_to_village()
for enemy in enemies_to_village:
    enemy.animate("x", village_pos[0], duration=duration, curve=curve.linear)
    enemy.animate("z", village_pos[1], duration=duration, curve=curve.linear)
# player_model.y = player.y - 3

def update():
    global player, player_HP, HP_timer, lose, end, enemies, villagers, win
    biome = generator.get_biome_type(player.x, player.z)

    for villager in villagers:
        villager.y = village_y + 1

    for enemies in all_enemies:
        for enemy in enemies:
            if math.sqrt((player.x - enemy.x) ** 2 + (player.z - enemy.z) ** 2) < 50:
                enemy_move(enemy)

            if player.intersects(enemy).hit:
                player_HP -= 5 * time.dt
                HP_timer = 10
    for enemy in enemies_to_village:

        biomee = generator.get_biome_type(enemy.x, enemy.z)
        if biomee == "desert":
            octaves = 6
            height_mult = 5
        elif biomee == "plains":
            octaves = 6
            height_mult = 10
        elif biomee == "ice_biome":
            octaves = 6
            height_mult = 6
        else:
            octaves = 8
            height_mult = 20
        pn = PerlinNoise(octaves=octaves, seed=seed)
        noise = generator.get_height(enemy.x, enemy.z, pn)[0]
        enemy.y = ((noise + 1) / 2 * height_mult) + 0.7



        if player.intersects(enemy).hit:
            player_HP -= 5 * time.dt
            HP_timer = 10
    if biome == "desert":
        if mode == 1:
            player.speed = 3.0
        else:
            player.speed = 1.5
    elif biome == "plains":
        player.speed = 7
    elif biome == "ice_biome":
        if mode == 3:
            player.speed = 8.5
        else:
            player.speed = 10.0
    elif biome == "mountain":
        if player.y > 10 and player_HP >= 0:
            player_HP -= 5 * time.dt
            HP_timer = 10


    health_bar.scale = (player_HP/(max_HP//2 + 3), 0.15)
    health_bar.color = lerp(color.red, color.rgb(0.3, 0.7, 0.3), player_HP/max_HP)


    HP_timer -= 1 * time.dt

    if HP_timer < 0 and player_HP < max_HP:
        player_HP += 5 * time.dt
    if int(player_HP) <= 0:
        end = "you are loooser"
        lose = True

    if lose or win:
        Sequence(Wait(10), Func(application.quit)).start()

    if not lose or not win:
        elapsed = time.time() - start_time
        remaining = max(0, int(duration - elapsed))

        timer_text.text = str(remaining) + "s remaining"

    if remaining <= 0:
        lose = True
    if math.sqrt((player.x - village_pos[0]) ** 2 + (player.z - village_pos[1]) ** 2) < 20:
        win = True

    if win:
        timer_text.text = "you win YAAAY!!!"
        timer_text.position = (0, 0)
        sky.color = color.green

    if lose:
        timer_text.text = end
        timer_text.position = (0, 0)
        sky.color = color.red


    coordinates.text = (int(player.x), int(player.y), int(player.z), biome)

def input(key):
    if key == 'escape':
        mouse.locked = not mouse.locked
        window.cursor_hidden = not window.cursor_hidden
    if key == 'r':
        application.quit()



if __name__ == '__main__':
    app.run()