import pygame as pg
from itertools import combinations
from datetime import datetime


class Body:
    def __init__(self, pos, veloc, mass, color='#F2cb05'):
        self.pos = pg.Vector2(pos)          # body position
        self.veloc = pg.Vector2(veloc)      # body velocity
        self.mass = mass                    # body mass
        self.rad = (mass / pi) ** (1/3)     # body radius
        self.trace = [pos]                  # body traces
        self.color = color
        self.initialized = False
    
    def update_pos(self):
        self.pos += self.veloc / FPS                        # update position depending on FPS 
        self.trace.append(self.pos.xy)                      # add traces
        if len(self.trace) > trace_len: self.trace.pop(0)   # delete older traces
    
    def update_radius(self):
        self.rad = (self.mass / pi) ** (1/3)

    def gravitation(self, other):
        distance = pg.math.Vector2.distance_to(self.pos, other.pos)     # calculate distance
        v_direction = pg.math.Vector2.normalize(other.pos - self.pos)   # calculate directon vector
        if distance > (self.rad + other.rad):                           # if not collision
            F = G * (self.mass * other.mass) / distance**2              # calculate Forces
            self.veloc += F * v_direction / self.mass / FPS             # update velocities
            other.veloc += F * -v_direction / other.mass / FPS          # update velocities
        else:                 # collision
            total_mass = self.mass + other.mass     # calc new total mass
            self.veloc = (self.veloc * self.mass + other.veloc * other.mass) / total_mass   # calc new total velocity
            self.pos = (self.pos * self.mass + other.pos * other.mass) / total_mass         # calc new total position
            self.mass, other.mass = total_mass, 0                                           # set new mass
            self.update_radius()                                                            # update new total radius



pg.init()
screen_b, screen_h = 1920,1080                          # set screen size
screen = pg.display.set_mode((screen_b, screen_h))      # init screen
center = (screen_b / 2, screen_h / 2)                   # calculate center

clock = pg.time.Clock()                                 # init clock
FPS = 60                                                # set FPS
trace_len = 500                                         # set trace length
G = 200                                                 # set gravitational constance
pi = 3.14159                                            # set pi
standard_mass = 1_000                                   # set standard mass
charging_factor = 3                                     # set charging factor

bodies = [Body(pos=center, veloc=(0,0), mass=200_000)]  # init first body
buffer = None

while True:
    clock.tick(FPS)
    for ereignis in pg.event.get():
        if ereignis.type == pg.QUIT: quit() # guit screen

        if ereignis.type == pg.MOUSEBUTTONDOWN:
            pos1 = pg.Vector2(pg.mouse.get_pos())
            time1 = datetime.now()
            buffer = Body(pos = pos1, veloc = (0,0), mass=standard_mass )   # create buffer
            
            if ereignis.button == 3:                                        # if right mouse
                m, i = max([(k.mass, i) for i, k in enumerate(bodies)])     # get body with biggest mass
                bodies[i].pos = pos1                                        # set to new position
                bodies[i].veloc= pg.Vector2(0,0)                            # set velocity to 0
        
        if ereignis.type == pg.MOUSEBUTTONUP and ereignis.button == 1:      # if mouse up
            pos2 = pg.Vector2(pg.mouse.get_pos())
            time2 = datetime.now()                                          # get time
            time_diff = time2 - time1                                       # calulate charging time
            veloc = pos1 - pos2                                             # calculate velocity 
            buffer.mass = standard_mass + standard_mass * time_diff.seconds * charging_factor# calculate charged mass
            buffer.veloc = veloc
            buffer.update_radius()                                          # update charged radius
            bodies.append(buffer)                                           # initialise buffer to bodies
            buffer = None                                                   # delete buffer

    for b1, b2 in combinations(bodies, 2):          # get all combinations of bodies
        if b1.mass == 0 or b2.mass == 0: continue   # skip mass==0 bodies
        b1.gravitation(b2)                          # apply gravitation

    bodies = [b for b in bodies if b.mass > 0]      # delete mass = 0 bodies

    screen.fill('#000000')                          # fill background

    for body in bodies:                             # iterate all bodies
        body.update_pos()                           # update bodies position
        pg.draw.circle(screen, body.color, body.pos, body.rad)          # draw bodies
        if len(body.trace) > 2:                                         # check wether a trace exists 
            pg.draw.lines(screen, '#303AF2', False, body.trace, 2)      # draw trace

    if buffer != None:                                                  # check wether buffer exists
        pg.draw.circle(screen, buffer.color, buffer.pos, buffer.rad)    # draw buffer

    if pg.mouse.get_pressed()[0]:                       # if left mouse is pressed (charging new body)
        pos2 = pg.Vector2(pg.mouse.get_pos())           # get mouse position
        pg.draw.line(screen, '#419fd9', pos1, pos2, 1)  # draw direction/velocity vector
        time2 = datetime.now()                          # get time
        time_diff = time2 - time1                       # calculate charging time
        buffer.mass = standard_mass + standard_mass * time_diff.seconds * charging_factor # calculate new charged mass
        buffer.update_radius()                          # update radius

    pg.display.flip()