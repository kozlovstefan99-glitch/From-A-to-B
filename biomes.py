from ursina import *
from perlin_noise import PerlinNoise

class BiomeGenerator:
    def __init__(self, size=100, scale=0.02, seed=42, road_width=20, roads=1, road_seg_min=2, road_seg_max=2, vilage_pos=(0,0), castle_pos=(0,0)):
        self.size = size
        self.scale = scale
        self.seed = seed
        self.road_width = road_width
        self.village_pos = vilage_pos
        self.castle_pos = castle_pos
        self.terrain_entity = None
        # self.dots = [(0, 0, -50, 50), (-50, 50, -50, 100)]
        self.dots = []
        for _ in range(roads):
            self.road_segments(road_seg_min, road_seg_max)
        # print(self.dots)
        # self.village(self.vilage_pos)

    def road_segments(self, road_seg_min=2, road_seg_max=4):
        xa, za = self.village_pos[0], self.village_pos[1]
        for _ in range(random.randint(road_seg_min, road_seg_max)):
            xb, zb = random.randint(-50, 50), random.randint(-50, 50)
            self.dots.append((xa, za, xb, zb))
            xa, za = xb, zb
        self.dots.append((xa, za, self.castle_pos[0], self.castle_pos[1]))

    def get_biome_type(self, x, z):
        pn_biome = PerlinNoise(octaves=4, seed=self.seed)
        biome_noise = pn_biome.noise([x * self.scale * 0.5, z * self.scale * 0.5])

        biome_normalized = (biome_noise + 1) / 2
        if biome_normalized < 0.35:
            return "desert"
        elif biome_normalized < 0.55:
            return "plains"
        elif biome_normalized < 0.67:
            return "ice_biome"
        else:
            return "mountain"
    def get_terrain_color(self, biome, height):
        if biome == "desert":
            return lerp(color.yellow, color.yellow, height)
        elif biome == "plains":
            return lerp(color.rgb(0.3, 0.6, 0.3), color.rgb(0.3, 0.7, 0.3), height)
        elif biome == "ice_biome":
            return lerp(color.rgba(0.4, 0.4, 0.7, 0.97), color.rgba(0.3, 0.3, 0.4, 0.99), height)
        else:
            return lerp(color.gray, color.white, height)

    def dist_to_segment(self, px, pz, ax, az, bx, bz):
        dx, dz = bx - ax, bz - az
        seg_len2 = dx * dx + dz * dz

        t = max(0.0, min(1.0, ((px - ax) * dx + (pz - az) * dz) / seg_len2))
        cx = ax + t * dx
        cz = az + t * dz

        # добавь здесь переменную dist, которая считает расстояние от точки (x, z) до отрезка (0, 0)
        # формула евклидова расстояния
        # нужно чтобы функция возвращала dist

        dist = math.sqrt((px - cx) ** 2 + (pz - cz) ** 2)

        return dist

    def get_height(self, x, z, perlin):
        n = perlin
        h = n([x*self.scale, z*self.scale])
        road_paint = False
        for ax, az, bx, bz in self.dots:
            # изменить на dist
            dist = self.dist_to_segment(x, z, ax, az, bx, bz)
            # изменить проверку, чтобы она учитывала ширину дороги
            if dist < self.road_width / 2:
                road_paint = True
        return h, road_paint



    def generate(self):
        verts = []
        tris = []
        colors = []

        resolution = 100
        step = self.size/resolution

        for z in range(resolution + 1):
            for x in range(resolution + 1):
                wx, wz = x * step - self.size / 2, z * step - self.size / 2

                biome = self.get_biome_type(wx, wz)

                if biome == "desert":
                    octaves = 6
                    height_mult = 5
                elif biome == "plains":
                    octaves = 6
                    height_mult = 10
                elif biome == "ice_biome":
                    octaves = 6
                    height_mult = 6
                else:
                    octaves = 8
                    height_mult = 20

                pn = PerlinNoise(octaves=octaves, seed=self.seed)

                noise_value, road_paint = self.get_height(wx, wz, perlin=pn)
                # noise_value = pn([wx*self.scale, wz*self.scale])
                y = (noise_value + 1) / 2 * height_mult
                if math.sqrt((wx - self.village_pos[0]) ** 2 + (wz - self.village_pos[2]) ** 2) < 30:
                    y = self.village_pos[1]
                verts.append((wx, y, wz))
                if road_paint:
                    if biome == "mountain":
                        colors.append(color.rgb(0.6499999761581421, 0.6000000238418579, 0.4749999940395355))
                    else:
                        colors.append(color.rgb(0.55, 0.45, 0.2))
                else:
                    colors.append(self.get_terrain_color(biome, y / height_mult))

        for z in range(resolution):
            for x in range(resolution):
                i = x + (resolution + 1) * z
                tris.append((i, i + 1, i + resolution + 1))
                tris.append((i + 1, i + resolution + 2, i + resolution + 1))

        if self.terrain_entity:
            destroy(self.terrain_entity)

        self.terrain_entity = Entity(model=Mesh(vertices=verts, triangles=tris, colors=colors), collider="mesh",)

        return self.terrain_entity
    #
    # def house(self, position, width=3, depth=4, wall_h=2.5,
    #                  roof_h=1.5, wall_color=None, roof_color=None):
    #     wall_colors = [
    #         color.rgb(220 / 255, 200 / 255, 170 / 255),
    #         color.rgb(200 / 255, 190 / 255, 175 / 255),
    #         color.rgb(240 / 255, 225 / 255, 200 / 255),
    #         color.rgb(180 / 255, 170 / 255, 160 / 255),
    #     ]
    #     roof_colors = [
    #         color.rgb(140 / 255, 50 / 255, 40 / 255),
    #         color.rgb(90 / 255, 60 / 255, 40 / 255),
    #         color.rgb(70 / 255, 70 / 255, 80 / 255),
    #         color.rgb(110 / 255, 80 / 255, 60 / 255),
    #     ]
    #     wc = wall_color or random.choice(wall_colors)
    #     rc = roof_color or random.choice(roof_colors)
    #
    #     wall = Entity(model='cube', color=wc,
    #             scale=(width, wall_h, depth),
    #             position=(position[0], position[1] + wall_h / 2, position[2]),
    #             collider='box')
    #
    #     roof = Entity(model='cube', color=rc,
    #            scale=(width * 1.1, roof_h, depth * 1.1),
    #            position=(position[0], position[1] + wall_h + roof_h / 2, position[2]),
    #            rotation=(0, 45, 0))
    #
    #     door_w, door_h = 0.7, 1.4
    #     door = Entity(model='cube', color=color.rgb(80 / 255, 50 / 255, 30 / 255),
    #            scale=(door_w, door_h, 0.1),
    #             position=(position[0] - width * 0.1,
    #                      position[1] + door_h / 2,
    #                      position[2] + depth / 2 + 0.05))
    #     return wall, roof, door
    # КЛАСС VILLAGE
    def village(self, center=(0, 0), rows=4, cols=4, spacing=12, y=0):
        villager_houses = []
        offset_x = (cols - 1) * spacing / 2
        offset_z = (rows - 1) * spacing / 2

        for row in range(rows):
            for col in range(cols):
                gx = center[0] - offset_x + col * spacing
                gz = center[1] - offset_z + row * spacing
                gx += random.uniform(-2.0, 2.0)
                gz += random.uniform(-2.0, 2.0)
                #
                # biome = self.get_biome_type(gx, gz)
                #
                # if biome == "desert":
                #     octaves = 6
                #     height_mult = 5.0
                # elif biome == "plains":
                #     octaves = 6
                #     height_mult = 10.0
                # elif biome == "ice_biome":
                #     octaves = 6
                #     height_mult = 6.0
                # else:
                #     octaves = 8
                #     height_mult = 20.0
                #
                # noise_value, road = self.get_height(gx, gz, PerlinNoise(octaves=octaves, seed=self.seed))
                #
                # y = (noise_value + 1) / 2 * height_mult + 0.5

                    # Пропускаем если место неровное или стоит прямо на дороге

                roof_h = random.uniform(1.0, 2.0)

                w = random.uniform(2.5, 4.0)
                d = random.uniform(3.0, 5.0)
                h = random.uniform(2.0, 3.5)

                wall_colors = [
                    color.rgb(220 / 255, 200 / 255, 170 / 255),
                    color.rgb(200 / 255, 190 / 255, 175 / 255),
                    color.rgb(240 / 255, 225 / 255, 200 / 255),
                    color.rgb(180 / 255, 170 / 255, 160 / 255),
                ]
                roof_colors = [
                    color.rgb(140 / 255, 50 / 255, 40 / 255),
                    color.rgb(90 / 255, 60 / 255, 40 / 255),
                    color.rgb(70 / 255, 70 / 255, 80 / 255),
                    color.rgb(110 / 255, 80 / 255, 60 / 255),
                ]
                wc = random.choice(wall_colors)
                rc = random.choice(roof_colors)

                wall = Entity(model='cube', color=wc,
                              scale=(w, h, d),
                              position=(gx, y + h / 2, gz),
                              collider='box')

                roof = Entity(model='cube', color=rc,
                              scale=(w * 1.1, roof_h, d * 1.1),
                              position=(gx, y + h + roof_h / 2, gz),
                              rotation=(0, 45, 0))

                door_w, door_h = 0.7, 1.4
                door = Entity(model='cube', color=color.rgb(80 / 255, 50 / 255, 30 / 255),
                              scale=(door_w, door_h, 0.1),
                              position=(gx - w * 0.1,
                                        y + door_h / 2,
                                        gz + d / 2 + 0.05))

                villager_houses.append(wall)
                villager_houses.append(roof)
                villager_houses.append(door)

                # villager_houses.append(
                #     self.house(position=(gx, y, gz), width=w, depth=d,
                #             wall_h=h, roof_h=random.uniform(1.0, 2.0))
                # )
        return villager_houses
STONE = color.rgb(0.55, 0.52, 0.48)
STONE_DARK = color.rgb(0.38, 0.35, 0.32)
STONE_LIGHT = color.rgb(0.68, 0.65, 0.60)
GATE_COLOR = color.rgb(0.15, 0.10, 0.08)

class Castle:
        def __init__(self, position=(-55, 5, -20), size=10, face_south=False):
            cx, cy, cz = position
            s = size
            fs = -1 if face_south else 1  # знак: -1 разворачивает ворота на юг

            # ДВОР
            Entity(model='cube', color=STONE,
                   scale=(s * 2, 1, s * 2),
                   position=(cx, cy - 0.25, cz),
                   collider='box')

            # СТЕНЫ
            wall_h = 4.0
            wall_thick = 1.0
            gate_w = 3.0
            gate_h = 2.5
            pylon_w = 1.2

            # Передняя стена (с воротами) — по стороне fs*s
            front_z = cz + fs * s
            left_len = s - gate_w / 2
            right_len = s - gate_w / 2
            left_cx = cx - s + left_len / 2
            right_cx = cx + s - right_len / 2

            Entity(model='cube', color=STONE, collider='box',
                   scale=(left_len, wall_h, wall_thick),
                   position=(left_cx, cy + wall_h / 2, front_z))
            Entity(model='cube', color=STONE, collider='box',
                   scale=(right_len, wall_h, wall_thick),
                   position=(right_cx, cy + wall_h / 2, front_z))

            # Задняя стена
            back_z = cz - fs * s
            Entity(model='cube', color=STONE, collider='box',
                   scale=(s * 2, wall_h, wall_thick),
                   position=(cx, cy + wall_h / 2, back_z))

            # Боковые стены
            Entity(model='cube', color=STONE, collider='box',
                   scale=(wall_thick, wall_h, s * 2),
                   position=(cx - s, cy + wall_h / 2, cz))
            Entity(model='cube', color=STONE, collider='box',
                   scale=(wall_thick, wall_h, s * 2),
                   position=(cx + s, cy + wall_h / 2, cz))

            # ---- 3. УГЛОВЫЕ БАШНИ -----------------------------------------
            tower_w = 3.0
            tower_h = 7.0
            corners = [(+s, +s), (-s, +s), (+s, -s), (-s, -s)]
            for (tx, tz) in corners:
                Entity(model='cube', color=STONE_DARK, collider='box',
                       scale=(tower_w, tower_h, tower_w),
                       position=(cx + tx, cy + tower_h / 2, cz + tz))
                self._battlement_ring(cx + tx, cy + tower_h, cz + tz, tower_w, count=4)

            # ---- 4. ЗУБЦЫ НА СТЕНАХ ---------------------------------------
            self._wall_battlements(cx, cy + wall_h, cz, s)

            # ---- 5. ВОРОТА ------------------------------------------------
            Entity(model='cube', color=color.rgb(0.5, 0.5, 0.5), collider='box',
                   scale=(pylon_w, wall_h + 3, wall_thick + 0.2),
                   position=(cx - gate_w / 2 - pylon_w / 2, cy + wall_h / 2, front_z))
            Entity(model='cube', color=color.rgb(0.5, 0.5, 0.5), collider='box',
                   scale=(pylon_w, wall_h + 3, wall_thick + 0.2),
                   position=(cx + gate_w / 2 + pylon_w / 2, cy + wall_h / 2, front_z))

            lintel_h = wall_h - gate_h
            Entity(model='cube', color=color.rgb(0.5, 0.5, 0.5), collider='box',
                   scale=(gate_w, lintel_h, wall_thick),
                   position=(cx, cy + gate_h + lintel_h / 2, front_z))
            Entity(model='cube', color=GATE_COLOR,
                   scale=(gate_w, gate_h, 0.3),
                   position=(cx, cy + gate_h / 2, front_z + 0.01))

            # ---- 6. ДОНЖОН -----------------------------------------------
            keep_w = 5.0
            keep_h = 12.0
            Entity(model='cube', color=STONE_DARK, collider='box',
                   scale=(keep_w, keep_h, keep_w),
                   position=(cx, cy + keep_h / 2, cz))
            self._battlement_ring(cx, cy + keep_h, cz, keep_w, count=5)
            Entity(model='cube', color=GATE_COLOR,
                   scale=(0.8, 1.0, 0.1),
                   position=(cx, cy + keep_h * 0.6, cz + keep_w / 2 + 0.05))

        def _battlement_ring(self, cx, top_y, cz, tower_w, count=4):
            r = tower_w * 0.55
            bw, bh = 0.7, 0.9
            for i in range(count):
                angle = (i / count) * 2 * math.pi
                Entity(model='cube', color=STONE_LIGHT,
                       scale=(bw, bh, bw),
                       position=(cx + math.cos(angle) * r, top_y + bh / 2,
                                 cz + math.sin(angle) * r))

        def _wall_battlements(self, cx, top_y, cz, s):
            bw, bh, step, offset = 0.8, 0.7, 2.0, 2.0
            for wz in [cz + s, cz - s]:
                x = cx - s + offset
                while x < cx + s - offset:
                    Entity(model='cube', color=STONE_LIGHT,
                           scale=(bw, bh, bw),
                           position=(x, top_y + bh / 2, wz))
                    x += step
            for wx in [cx - s, cx + s]:
                z = cz - s + offset
                while z < cz + s - offset:
                    Entity(model='cube', color=STONE_LIGHT,
                           scale=(bw, bh, bw),
                           position=(wx, top_y + bh / 2, z))
                    z += step