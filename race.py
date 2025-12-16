from OpenGL.GL import *
from OpenGL.GLUT import *
import OpenGL.GLUT as GLUTmod
from OpenGL.GLU import *
import math
import random
import sys
import time

# Game state variables
game_over = False
game_paused = False
laps_completed = 0
score = 0
crash_count = 0

# Level/timer variables
current_level = 1
level_start_time = time.time()
level_durations = {1: 45, 2: 60, 3: 75, 4: 90, 5: 120}  # seconds - more reasonable durations
fifteen_sec_boost_applied = False
level_banner_until = 0.0
win_message = None

# Rain system variables (screen-space overlay)
rain_enabled = False
rain_drops = []
rain_dx = 0.0
rain_dy = -6.0
last_rain_tick = 0.0
rain_interval = 0.03
RAIN_COUNT = 300

# Player car variables
player_car_pos = [0, -200, 0]  # Start at bottom of track
player_car_lane = 0  # 0 = center, -1 = left, 1 = right
player_speed = 0.45  # Slower base speed for better competition

# Opponent cars
opponent_cars = []
opponent_count = 2  # Reduced for performance

# Track variables
track_width = 150
track_length = 400
track_curvature = 0.015
# Endless road rendering window and segment size
view_distance = 600
lane_segment = 40

# Obstacles
obstacles = []
obstacle_count = 3  # Fewer obstacles for less frequent encounters

# Camera variables
camera_angle = 0

# Game variables
fovY = 60  # Reduced FOV for performance

def _draw_wheel_3d(tire_color=(0.05, 0.05, 0.05), rim_color=(0.9, 0.9, 0.9)):
    """Realistic 3D wheel design with proper size."""
    glPushMatrix()
    
    # Tire (outer ring) - smaller and more realistic
    glColor3f(*tire_color)
    GLUTmod.glutSolidTorus(1.0, 6, 16, 32)  # Smaller tire, fewer segments
    
    # Rim (inner ring) - smaller and more realistic
    glColor3f(*rim_color)
    GLUTmod.glutSolidTorus(0.6, 5, 12, 24)
    
    # Spokes - 3D rectangular prisms (smaller)
    glColor3f(0.4, 0.4, 0.4)
    for a in range(0, 360, 60):
        rad = math.radians(a)
        glPushMatrix()
        glRotatef(a, 0, 0, 1)  # Rotate to spoke position
        glTranslatef(3.5, 0, 0)  # Move to rim position
        
        # Draw 3D spoke as a rectangular prism (smaller)
        glBegin(GL_QUADS)
        # Front face
        glVertex3f(-0.4, -0.4, 0.8)
        glVertex3f(0.4, -0.4, 0.8)
        glVertex3f(0.4, 0.4, 0.8)
        glVertex3f(-0.4, 0.4, 0.8)
        # Back face
        glVertex3f(-0.4, -0.4, -0.8)
        glVertex3f(0.4, -0.4, -0.8)
        glVertex3f(0.4, 0.4, -0.8)
        glVertex3f(-0.4, 0.4, -0.8)
        # Left face
        glVertex3f(-0.4, -0.4, -0.8)
        glVertex3f(-0.4, -0.4, 0.8)
        glVertex3f(-0.4, 0.4, 0.8)
        glVertex3f(-0.4, 0.4, -0.8)
        # Right face
        glVertex3f(0.4, -0.4, -0.8)
        glVertex3f(0.4, -0.4, 0.8)
        glVertex3f(0.4, 0.4, 0.8)
        glVertex3f(0.4, 0.4, -0.8)
        # Top face
        glVertex3f(-0.4, 0.4, -0.8)
        glVertex3f(0.4, 0.4, -0.8)
        glVertex3f(0.4, 0.4, 0.8)
        glVertex3f(-0.4, 0.4, 0.8)
        # Bottom face
        glVertex3f(-0.4, -0.4, -0.8)
        glVertex3f(0.4, -0.4, -0.8)
        glVertex3f(0.4, -0.4, 0.8)
        glVertex3f(-0.4, -0.4, 0.8)
        glEnd()
        glPopMatrix()
    
    # Center hub - 3D cylinder (smaller)
    glColor3f(0.6, 0.6, 0.6)
    GLUTmod.glutSolidCylinder(1.5, 1, 12, 6)  # Radius 1.5, height 1
    
    # Center bolt - 3D cylinder (smaller)
    glColor3f(0.3, 0.3, 0.3)
    GLUTmod.glutSolidCylinder(0.5, 1.5, 8, 4)  # Radius 0.5, height 1.5
    
    glPopMatrix()

def draw_car(x, y, z, color=(0.95, 0.9, 0.2), is_opponent=False):
    """Realistic 3D car design with proper proportions."""
    glPushMatrix()
    glTranslatef(x, y, z)

    # Choose palette
    if is_opponent:
        body_color = (0.9, 0.1, 0.1)  # Red for opponents
        window_color = (0.8, 0.8, 0.8)
        tire_color = (0.1, 0.1, 0.1)
        rim_color = (0.7, 0.7, 0.7)
        accent_color = (0.7, 0.0, 0.0)
    else:
        body_color = (0.2, 0.4, 0.8)  # Blue for player
        window_color = (0.6, 0.8, 1.0)
        tire_color = (0.1, 0.1, 0.1)
        rim_color = (0.5, 0.5, 0.5)
        accent_color = (0.1, 0.2, 0.6)

    # Wheels (4 wheels - front and back) - much smaller
    glPushMatrix(); glTranslatef(-8, -2, 0); _draw_wheel_3d(tire_color, rim_color); glPopMatrix()
    glPushMatrix(); glTranslatef(8, -2, 0); _draw_wheel_3d(tire_color, rim_color); glPopMatrix()
    glPushMatrix(); glTranslatef(-8, 2, 0); _draw_wheel_3d(tire_color, rim_color); glPopMatrix()
    glPushMatrix(); glTranslatef(8, 2, 0); _draw_wheel_3d(tire_color, rim_color); glPopMatrix()

    # Car body - realistic proportions
    glColor3f(*body_color)
    glBegin(GL_QUADS)
    
    # Main body (lower section) - much smaller
    glVertex3f(-10, -2, 0)
    glVertex3f(10, -2, 0)
    glVertex3f(10, 1.5, 0)
    glVertex3f(-10, 1.5, 0)
    
    # Upper body (cabin area) - smaller and more realistic
    glVertex3f(-6, 1.5, 0)
    glVertex3f(6, 1.5, 0)
    glVertex3f(6, 5, 0)
    glVertex3f(-6, 5, 0)
    
    # Hood (front) - realistic slope
    glVertex3f(6, -2, 0)
    glVertex3f(10, -2, 0)
    glVertex3f(10, 0.5, 0)
    glVertex3f(6, 1.5, 0)
    
    # Trunk (back) - realistic slope
    glVertex3f(-10, -2, 0)
    glVertex3f(-6, -2, 0)
    glVertex3f(-6, 1.5, 0)
    glVertex3f(-10, 0.5, 0)
    glEnd()

    # Windows - realistic design
    glColor3f(*window_color)
    glBegin(GL_QUADS)
    # Front windshield (angled)
    glVertex3f(5, 1.5, 0)
    glVertex3f(6, 1.5, 0)
    glVertex3f(6, 4.5, 0)
    glVertex3f(5, 4.5, 0)
    
    # Rear windshield (angled)
    glVertex3f(-6, 1.5, 0)
    glVertex3f(-5, 1.5, 0)
    glVertex3f(-5, 4.5, 0)
    glVertex3f(-6, 4.5, 0)
    
    # Side windows (realistic size)
    glVertex3f(-5, 1.5, 0)
    glVertex3f(5, 1.5, 0)
    glVertex3f(5, 4.5, 0)
    glVertex3f(-5, 4.5, 0)
    glEnd()

    # Headlights - realistic size
    glColor3f(1.0, 1.0, 0.9)
    glBegin(GL_QUADS)
    # Left headlight
    glVertex3f(9, -1.5, 0)
    glVertex3f(10, -1.5, 0)
    glVertex3f(10, -0.5, 0)
    glVertex3f(9, -0.5, 0)
    # Right headlight
    glVertex3f(9, -0.5, 0)
    glVertex3f(10, -0.5, 0)
    glVertex3f(10, 0.5, 0)
    glVertex3f(9, 0.5, 0)
    glEnd()

    # Taillights - realistic size
    glColor3f(1.0, 0.2, 0.2)
    glBegin(GL_QUADS)
    # Left taillight
    glVertex3f(-10, -1.5, 0)
    glVertex3f(-9, -1.5, 0)
    glVertex3f(-9, -0.5, 0)
    glVertex3f(-10, -0.5, 0)
    # Right taillight
    glVertex3f(-10, -0.5, 0)
    glVertex3f(-9, -0.5, 0)
    glVertex3f(-9, 0.5, 0)
    glVertex3f(-10, 0.5, 0)
    glEnd()

    # Side mirrors - realistic size
    glColor3f(*accent_color)
    glBegin(GL_QUADS)
    # Left mirror
    glVertex3f(-6, 3, 0)
    glVertex3f(-5, 3, 0)
    glVertex3f(-5, 4, 0)
    glVertex3f(-6, 4, 0)
    # Right mirror
    glVertex3f(5, 3, 0)
    glVertex3f(6, 3, 0)
    glVertex3f(6, 4, 0)
    glVertex3f(5, 4, 0)
    glEnd()

    # Bumpers - realistic size
    glColor3f(0.2, 0.2, 0.2)
    glBegin(GL_QUADS)
    # Front bumper
    glVertex3f(9, -2, 0)
    glVertex3f(10, -2, 0)
    glVertex3f(10, -1.5, 0)
    glVertex3f(9, -1.5, 0)
    # Rear bumper
    glVertex3f(-10, -2, 0)
    glVertex3f(-9, -2, 0)
    glVertex3f(-9, -1.5, 0)
    glVertex3f(-10, -1.5, 0)
    glEnd()

    # Door lines - realistic size
    glColor3f(0.1, 0.1, 0.1)
    glBegin(GL_LINES)
    glVertex3f(-2, -2, 0)
    glVertex3f(-2, 5, 0)
    glVertex3f(2, -2, 0)
    glVertex3f(2, 5, 0)
    glEnd()

    # Grille (front) - realistic size
    glColor3f(0.3, 0.3, 0.3)
    glBegin(GL_QUADS)
    glVertex3f(8, -1.5, 0)
    glVertex3f(9, -1.5, 0)
    glVertex3f(9, -1, 0)
    glVertex3f(8, -1, 0)
    glEnd()

    # Exhaust pipes (back) - realistic size
    glColor3f(0.4, 0.4, 0.4)
    glBegin(GL_QUADS)
    glVertex3f(-9, -2, 0)
    glVertex3f(-8, -2, 0)
    glVertex3f(-8, -1.5, 0)
    glVertex3f(-9, -1.5, 0)
    glEnd()
    
    glPopMatrix()

def draw_track():
    """Draw the racing track with an endless effect around the player.
    Each lane is colored; background has a dark gradient aesthetic."""
    player_y = player_car_pos[1]
    start_y = int((player_y - view_distance) // lane_segment * lane_segment)
    end_y = int((player_y + view_distance) // lane_segment * lane_segment)

    # Base road with slight gradient
    glBegin(GL_QUADS)
    glColor3f(0.02, 0.02, 0.02)
    glVertex3f(-track_width, player_y - view_distance, -1)
    glColor3f(0.06, 0.06, 0.06)
    glVertex3f(track_width, player_y - view_distance, -1)
    glColor3f(0.12, 0.12, 0.12)
    glVertex3f(track_width, player_y + view_distance, -1)
    glColor3f(0.06, 0.06, 0.06)
    glVertex3f(-track_width, player_y + view_distance, -1)
    glEnd()

    # Black palette stripes like screenshot (teal to black)
    palette = [
        (0.60, 0.75, 0.80),  # light slate
        (0.45, 0.60, 0.65),
        (0.15, 0.35, 0.42),
        (0.05, 0.18, 0.22),
        (0.0, 0.0, 0.0)
    ]
    # Colored lane strips
    lane_colors = [palette[0], palette[2], palette[4]]
    for lane_idx, x_center in enumerate([-track_width/3, 0, track_width/3]):
        half = track_width/3 - 10
        glColor4f(lane_colors[lane_idx][0], lane_colors[lane_idx][1], lane_colors[lane_idx][2], 0.35)
        glBegin(GL_QUADS)
        glVertex3f(x_center - half, player_y - view_distance, 0)
        glVertex3f(x_center + half, player_y - view_distance, 0)
        glVertex3f(x_center + half, player_y + view_distance, 0)
        glVertex3f(x_center - half, player_y + view_distance, 0)
        glEnd()

    # Track boundaries (white)
    glColor3f(1.0, 1.0, 1.0)
    for i in range(start_y, end_y, lane_segment):
        x_offset = math.sin(i * track_curvature) * 30
        glBegin(GL_LINES)
        # Left boundary
        glVertex3f(-track_width + x_offset, i, 0)
        glVertex3f(-track_width + x_offset, i + lane_segment, 0)
        # Right boundary
        glVertex3f(track_width + x_offset, i, 0)
        glVertex3f(track_width + x_offset, i + lane_segment, 0)
        glEnd()

    # Lane dividers (yellow, dashed every 2 segments)
    glColor3f(1.0, 1.0, 0.0)
    for i in range(start_y, end_y, lane_segment * 2):
        x_offset = math.sin(i * track_curvature) * 30
        glBegin(GL_LINES)
        # Left lane divider
        glVertex3f(-track_width/3 + x_offset, i, 0)
        glVertex3f(-track_width/3 + x_offset, i + lane_segment, 0)
        # Right lane divider
        glVertex3f(track_width/3 + x_offset, i, 0)
        glVertex3f(track_width/3 + x_offset, i + lane_segment, 0)
        glEnd()

def draw_obstacles():
    """Draw obstacles on the track"""
    for obstacle in obstacles:
        glPushMatrix()
        glTranslatef(obstacle['pos'][0], obstacle['pos'][1], obstacle['pos'][2])
        
        # Draw obstacle as a red cube
        glColor3f(1.0, 0.0, 0.0)
        glBegin(GL_QUADS)
        # Front face
        glVertex3f(-8, -8, 0)
        glVertex3f(8, -8, 0)
        glVertex3f(8, 8, 0)
        glVertex3f(-8, 8, 0)
        # Back face
        glVertex3f(-8, -8, 15)
        glVertex3f(8, -8, 15)
        glVertex3f(8, 8, 15)
        glVertex3f(-8, 8, 15)
        # Left face
        glVertex3f(-8, -8, 0)
        glVertex3f(-8, -8, 15)
        glVertex3f(-8, 8, 15)
        glVertex3f(-8, 8, 0)
        # Right face
        glVertex3f(8, -8, 0)
        glVertex3f(8, -8, 15)
        glVertex3f(8, 8, 15)
        glVertex3f(8, 8, 0)
        # Top face
        glVertex3f(-8, -8, 15)
        glVertex3f(8, -8, 15)
        glVertex3f(8, 8, 15)
        glVertex3f(-8, 8, 15)
        # Bottom face
        glVertex3f(-8, -8, 0)
        glVertex3f(8, -8, 0)
        glVertex3f(8, 8, 0)
        glVertex3f(-8, 8, 0)
        glEnd()
        
        glPopMatrix()

def draw_text(x, y, text, font=None):
    if font is None:
        font = GLUTmod.GLUT_BITMAP_HELVETICA_12
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 800, 0, 600)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def _draw_rain_overlay():
    if not rain_enabled:
        return
    global last_rain_tick, rain_drops
    now = time.time()
    if now - last_rain_tick > rain_interval:
        # Update rain
        for drop in rain_drops:
            drop[0] += rain_dx
            drop[1] += rain_dy
            if drop[1] < 0 or drop[0] < -10 or drop[0] > 810:
                drop[0] = random.randint(-10, 810)
                drop[1] = 600
        last_rain_tick = now

    # Draw in screen space
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 800, 0, 600)
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    glBegin(GL_LINES)
    for idx, drop in enumerate(rain_drops):
        if idx % 2 == 0:
            glColor3f(0.5, 0.7, 1.0)
        else:
            glColor3f(0.8, 0.9, 1.0)
        glVertex2f(drop[0], drop[1])
        glVertex2f(drop[0] + 3, drop[1] - 12)
    glEnd()
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)



def init_obstacles():
    """Initialize obstacles at random positions ahead of the player."""
    global obstacles
    obstacles = []
    base_y = player_car_pos[1]
    for i in range(obstacle_count):
        x = random.uniform(-track_width + 40, track_width - 40)
        # Place obstacles further apart
        y = base_y + random.uniform(220, view_distance)
        obstacles.append({
            'pos': [x, y, 0],
            'active': True
        })

def init_opponents():
    """Initialize opponent cars"""
    global opponent_cars
    opponent_cars = []
    for i in range(opponent_count):
        lane = random.choice([-1, 0, 1])
        y_pos = random.uniform(-track_length + 100, track_length - 100)
        opponent_cars.append({
            'pos': [lane * track_width/3, y_pos, 0],
            'speed': max(0.35, min(0.6, player_speed * random.uniform(0.85, 1.15))),
            'lane': lane
        })

def reset_game():
    """Reset game to initial state"""
    global game_over, game_paused, laps_completed, score, crash_count
    global player_car_pos, player_car_lane, player_speed
    global current_level, level_start_time, fifteen_sec_boost_applied, level_banner_until, win_message
    
    game_over = False
    game_paused = False
    laps_completed = 0
    score = 0
    crash_count = 0
    player_car_pos = [0, -200, 0]
    player_car_lane = 0
    # Base speed scales with level
    base_speed = 0.4 + 0.05 * (current_level - 1)
    player_speed = base_speed
    level_start_time = time.time()
    fifteen_sec_boost_applied = False
    level_banner_until = time.time() + 2.0
    win_message = None
    
    init_obstacles()
    init_opponents()
    
    print("=== CAR RACING GAME RESET ===")
    print(f"Level: {current_level}")
    print(f"Laps Completed: {laps_completed}")
    print(f"Score: {score}")
    print(f"Crashes: {crash_count}")

def distance(pos1, pos2):
    """Calculate distance between two 3D points"""
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2 + (pos1[2] - pos2[2])**2)

def check_collision(car_pos, obstacle_pos, radius=15):
    """Check collision between car and obstacle"""
    return distance(car_pos, obstacle_pos) < radius

def check_lap_completion():
    """Deprecated for endless road. Kept for compatibility."""
    return

def update_player_car():
    """Update player car position"""
    global player_car_pos, player_car_lane
    
    # Move forward automatically
    player_car_pos[1] += player_speed
    
    # Increment score over distance
    global score
    score += 1
    
    # Apply track curvature
    x_offset = math.sin(player_car_pos[1] * track_curvature) * 30
    player_car_pos[0] = player_car_lane * track_width/3 + x_offset
    
    # No lap completion for endless mode
    
    # Check collision with obstacles
    for obstacle in obstacles:
        if obstacle['active'] and check_collision(player_car_pos, obstacle['pos']):
            handle_crash()

    # Check collision with opponents
    for opponent in opponent_cars:
        if check_collision(player_car_pos, opponent['pos'], radius=18):
            handle_crash()

def update_opponent_cars():
    """Update opponent car positions and recycle them ahead for endless mode."""
    global opponent_cars
    player_y = player_car_pos[1]
    
    for opponent in opponent_cars:
        # Move forward
        opponent['pos'][1] += opponent['speed']
        
        # Apply track curvature
        x_offset = math.sin(opponent['pos'][1] * track_curvature) * 30
        opponent['pos'][0] = opponent['lane'] * track_width/3 + x_offset
        
        # If far behind the player, recycle ahead
        if opponent['pos'][1] < player_y - 100:
            opponent['pos'][1] = player_y + view_distance + random.uniform(50, 300)
            opponent['lane'] = random.choice([-1, 0, 1])

def update_obstacles():
    """Recycle obstacles for endless mode when they fall behind the player."""
    global obstacles
    player_y = player_car_pos[1]
    for obstacle in obstacles:
        if obstacle['pos'][1] < player_y - 50:
            obstacle['pos'][0] = random.uniform(-track_width + 40, track_width - 40)
            # Respawn further ahead to reduce frequency
            obstacle['pos'][1] = player_y + view_distance + random.uniform(220, 520)
            obstacle['active'] = True

def handle_crash():
    """Handle car crash"""
    global crash_count, player_car_pos, player_car_lane, game_over, opponent_cars
    
    crash_count += 1
    print(f"CRASH! Total crashes: {crash_count}")
    
    # Reset car position
    player_car_pos = [0, -200, 0]
    player_car_lane = 0
    
    # Reposition opponents ahead to keep them visible after crash
    base_y = player_car_pos[1]
    for opponent in opponent_cars:
        opponent['lane'] = random.choice([-1, 0, 1])
        opponent['pos'][1] = base_y + random.uniform(140, 460)
        x_offset = math.sin(opponent['pos'][1] * track_curvature) * 30
        opponent['pos'][0] = opponent['lane'] * track_width/3 + x_offset
    
    if crash_count >= 5:
        game_over = True
        print("GAME OVER - Too many crashes!")

def keyboardListener(key, x, y):
    """Handle keyboard inputs"""
    global player_car_lane, game_over, game_paused
    global rain_enabled
    
    if game_over:
        if key == b'r':
            reset_game()
        return
    
    if game_paused:
        # Only allow continue, restart, quit while paused
        if key == b'c' and not game_over:
            _advance_level()
        elif key == b'r':
            reset_game()
        elif key == b'q':
            print("Quitting game...")
            glutLeaveMainLoop()
        return
    
    # Move lanes (changed to J/L to free A/B for rain)
    if key == b'j':
        if player_car_lane > -1:
            player_car_lane -= 1
            print("Moved to left lane")
    if key == b'l':
        if player_car_lane < 1:
            player_car_lane += 1
            print("Moved to right lane")
    
    # Reset game (R key)
    if key == b'r':
        reset_game()
    
    # Quit game (Q key)
    if key == b'q':
        print("Quitting game...")
        glutLeaveMainLoop()
        return

    # Rain toggles
    if key == b'a':
        rain_enabled = True
        print("Rain started")
    if key == b'b':
        rain_enabled = False
        print("Rain stopped")

    # Continue to next level (if not paused between levels, ignore)
    if key == b'c' and not game_over and not game_paused:
        _advance_level()

def _advance_level():
    global current_level, game_paused, level_start_time, fifteen_sec_boost_applied
    global obstacle_count, opponent_count, player_speed, win_message
    if current_level >= 5:
        return
    current_level += 1
    # Increase difficulty per level
    obstacle_count = min(obstacle_count + 1, 9)
    opponent_count = min(opponent_count + 1, 7)
    player_speed = min(player_speed + 0.05, 1.3)
    fifteen_sec_boost_applied = False
    game_paused = False
    level_start_time = time.time()
    global level_banner_until
    level_banner_until = time.time() + 2.0
    win_message = None  # Clear any previous win message
    init_obstacles()
    init_opponents()
    print(f"=== ADVANCED TO LEVEL {current_level} ===")
    print(f"Obstacles: {obstacle_count}, Opponents: {opponent_count}, Speed: {player_speed:.2f}")

def specialKeyListener(key, x, y):
    """Handle special key inputs"""
    global camera_angle
    global player_speed
    
    # Rotate camera left (LEFT arrow key)
    if key == GLUT_KEY_LEFT:
        camera_angle += 3
    
    # Rotate camera right (RIGHT arrow key)
    if key == GLUT_KEY_RIGHT:
        camera_angle -= 3

    # Speed control
    if key == GLUT_KEY_UP:
        player_speed = min(player_speed + 0.05, 1.5)
    if key == GLUT_KEY_DOWN:
        player_speed = max(player_speed - 0.05, 0.1)

def setupCamera():
    """Configure camera settings"""
    global camera_angle, player_car_pos
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.0, 0.1, 800)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    # Follow player car
    camera_x = player_car_pos[0] + 80 * math.cos(math.radians(camera_angle))
    camera_y = player_car_pos[1] - 120
    camera_z = 100
    
    look_x = player_car_pos[0]
    look_y = player_car_pos[1] + 60
    look_z = player_car_pos[2]
    
    gluLookAt(camera_x, camera_y, camera_z,  # Camera position
              look_x, look_y, look_z,         # Look-at target
              0, 0, 1)                        # Up vector

def idle():
    """Idle function for game updates"""
    global game_over, game_paused
    global level_start_time, fifteen_sec_boost_applied, current_level
    global obstacle_count, opponent_count, player_speed
    
    if not game_over and not game_paused:
        update_player_car()
        update_opponent_cars()
        update_obstacles()
        # Timed difficulty and level progression
        elapsed = time.time() - level_start_time
        if elapsed > 15 and not fifteen_sec_boost_applied:
            player_speed = min(player_speed + 0.1, 1.2)
            obstacle_count = min(obstacle_count + 1, 7)
            opponent_count = min(opponent_count + 1, 6)
            fifteen_sec_boost_applied = True
            init_obstacles()
            init_opponents()
        # Level completion check
        if elapsed >= level_durations.get(current_level, 30):
            if current_level < 5:
                game_paused = True
                print(f"Level {current_level} complete! Press C to continue.")
            else:
                global win_message
                win_message = "WINNER! You finished the battle run."
                game_paused = True
    
    glutPostRedisplay()

def showScreen():
    """Display function to render the game scene"""
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    
    setupCamera()
    
    # Draw game elements
    draw_track()
    draw_obstacles()
    
    # Draw player car (blue)
    draw_car(player_car_pos[0], player_car_pos[1], player_car_pos[2], None, is_opponent=False)
    
    # Draw opponent cars
    for opponent in opponent_cars:
        draw_car(opponent['pos'][0], opponent['pos'][1], opponent['pos'][2], None, is_opponent=True)
    
    # Draw UI text
    draw_text(10, 570, f"Level: {current_level}")
    draw_text(10, 550, f"Score: {score}")
    draw_text(10, 530, f"Crashes: {crash_count}")
    draw_text(10, 510, f"Speed: {player_speed:.1f}")
    
    # Show level timer
    if not game_over and not game_paused:
        elapsed = time.time() - level_start_time
        level_duration = level_durations.get(current_level, 60)
        time_left = max(0, level_duration - elapsed)
        draw_text(10, 470, f"Time Left: {time_left:.0f}s")
    
    # Rain overlay and messages
    _draw_rain_overlay()
    
    # Game control instructions
    draw_text(10, 490, "Controls: J/L - Lanes, Arrows - Camera & Speed, A/B Rain, C Continue")

    # Show level banner briefly after reset/advance
    if time.time() < level_banner_until:
        draw_text(300, 560, f"Level {current_level} | Score: {score}")
    
    if game_paused:
        if win_message is not None:
            draw_text(180, 300, f"{win_message} Press R to restart.")
        elif current_level < 5:
            draw_text(220, 320, f"Level {current_level} Complete! Press C to continue to Level {current_level + 1}")
            draw_text(260, 300, f"Score: {score}")
    
    if game_over:
        draw_text(300, 250, "GAME OVER - Press R to Restart", GLUTmod.GLUT_BITMAP_HELVETICA_12)
    
    glutSwapBuffers()

def init():
    """Initialize OpenGL settings"""
    glClearColor(0.0, 0.0, 0.0, 1.0)  # Black background
    glPointSize(2.0)
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_BLEND)
    glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
    
    # Setup lighting for 3D wheels
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glEnable(GL_COLOR_MATERIAL)
    
    # Set up light position and properties
    light_position = [100.0, 100.0, 100.0, 1.0]
    light_ambient = [0.2, 0.2, 0.2, 1.0]
    light_diffuse = [0.8, 0.8, 0.8, 1.0]
    light_specular = [1.0, 1.0, 1.0, 1.0]
    
    glLightfv(GL_LIGHT0, GL_POSITION, light_position)
    glLightfv(GL_LIGHT0, GL_AMBIENT, light_ambient)
    glLightfv(GL_LIGHT0, GL_DIFFUSE, light_diffuse)
    glLightfv(GL_LIGHT0, GL_SPECULAR, light_specular)
    
    # Initialize game
    reset_game()

    # Seed rain positions
    global rain_drops
    rain_drops = []
    for _ in range(RAIN_COUNT):
        rain_drops.append([random.randint(0, 800), random.randint(0, 600)])

def main():
    try:
        glutInit()
        glutInitDisplayMode(GLUT_RGBA | GLUT_DOUBLE | GLUT_DEPTH)
        glutInitWindowSize(800, 600)
        glutInitWindowPosition(100, 100)
        wind = glutCreateWindow(b"3D Car Racing Game")
        
        glutDisplayFunc(showScreen)
        glutIdleFunc(idle)
        glutSpecialFunc(specialKeyListener)
        glutMouseFunc(lambda *args: None)  # No mouse needed
        glutKeyboardFunc(keyboardListener)
        
        init()
        
        print("=== 3D CAR RACING GAME STARTED ===")
        print("Controls:")
        print("J/L - Change lanes | A - Rain ON | B - Rain OFF")
        print("Arrow Keys: LEFT/RIGHT camera, UP/DOWN speed")
        print("R - Restart | Q - Quit | C - Continue (between levels)")
        print("Goal: Survive levels, avoid obstacles and opponents, finish Level 5 to win")
        
        glutMainLoop()
    except Exception as e:
        print(f"Error starting game: {e}")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()