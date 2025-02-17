import pygame
import psutil
import random
import time
import math

class SystemRPG:
    def __init__(self):
        pygame.init()
        self.screen_width, self.screen_height = 800, 450
        self.screen = pygame.display.set_mode((self.screen_width, self.screen_height))
        pygame.display.set_caption("Advanced System RPG Dashboard")
        self.clock = pygame.time.Clock()
        
        # Fonts for text display.
        self.font = pygame.font.SysFont("Arial", 20)
        self.title_font = pygame.font.SysFont("Arial", 32, bold=True)
        self.warning_font = pygame.font.SysFont("Arial", 40, bold=True)
        
        # Variables for healing bonus, level, and particle effects.
        self.heal_bonus = 0
        self.start_time = time.time()
        self.level = 1
        
        # List to store recent CPU usage (for the graph).
        self.cpu_usage_history = []
        
        # Particle list for heal effect
        self.particles = []
        
        # Initialize sound mixer and try to load sound files.
        pygame.mixer.init()
        try:
            self.heal_sound = pygame.mixer.Sound("heal.wav")
        except Exception as e:
            print("Healing sound not found:", e)
            self.heal_sound = None
        try:
            self.warning_sound = pygame.mixer.Sound("warning.wav")
        except Exception as e:
            print("Warning sound not found:", e)
            self.warning_sound = None

        # For screen shake effect.
        self.shake_offset = (0, 0)
        self.shake_duration = 0

    def update_stats(self):
        # CPU usage update.
        self.cpu = psutil.cpu_percent(interval=None)
        # Increase difficulty with level.
        difficulty_factor = 1 + (self.level - 1) * 0.05
        self.health = max(0, 100 - self.cpu * difficulty_factor + self.heal_bonus)
        self.health = min(self.health, 100)
        
        # Memory stat.
        mem = psutil.virtual_memory().percent
        self.memory = max(0, 100 - mem)
        
        # Simulate a "stamina" stat (you could replace this with actual disk I/O stats).
        self.stamina = random.randint(70, 100)
        
        # Battery stat (if available)
        battery = psutil.sensors_battery()
        self.battery = battery.percent if battery is not None else 100
        
        # Level progression: level up every 15 seconds.
        elapsed = time.time() - self.start_time
        self.level = 1 + int(elapsed // 15)
        
        # Record CPU usage for graph (limit history).
        self.cpu_usage_history.append(self.cpu)
        if len(self.cpu_usage_history) > 50:
            self.cpu_usage_history.pop(0)
        
        # Trigger screen shake if health is critical.
        if self.health < 20:
            self.shake_duration = 10  # frames of shake

    def update_particles(self):
        # Update existing particles: move them and fade them out.
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            particle['life'] -= 1
        # Remove dead particles.
        self.particles = [p for p in self.particles if p['life'] > 0]

    def create_heal_particles(self, x, y, count=30):
        for _ in range(count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(1, 3)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'life': random.randint(20, 40),
                'color': (0, 255, 0)
            })

    def draw_bar(self, screen, x, y, width, height, percentage, bar_color, border_color=(255,255,255)):
        pygame.draw.rect(screen, border_color, (x-2, y-2, width+4, height+4), 2)
        pygame.draw.rect(screen, (150, 0, 0), (x, y, width, height))
        fill_width = int(width * (percentage / 100))
        pygame.draw.rect(screen, bar_color, (x, y, fill_width, height))

    def draw_cpu_graph(self, screen, x, y, width, height):
        pygame.draw.rect(screen, (255,255,255), (x, y, width, height), 2)
        if len(self.cpu_usage_history) < 2:
            return
        graph_points = []
        step = width / (len(self.cpu_usage_history) - 1)
        for i, usage in enumerate(self.cpu_usage_history):
            graph_x = x + i * step
            graph_y = y + height - (usage / 100 * height)
            graph_points.append((graph_x, graph_y))
        pygame.draw.lines(screen, (0,255,0), False, graph_points, 2)

    def draw_dashboard(self):
        # Animate background color based on CPU usage (higher usage gives a reddish tint).
        red_intensity = int(min(255, self.cpu * 2))
        blue_intensity = 255 - red_intensity
        bg_color = (red_intensity // 2, 0, blue_intensity // 2)
        self.screen.fill(bg_color)
        
        # Apply screen shake offset if active.
        shake_x, shake_y = 0, 0
        if self.shake_duration > 0:
            shake_x = random.randint(-5, 5)
            shake_y = random.randint(-5, 5)
            self.shake_duration -= 1
        self.shake_offset = (shake_x, shake_y)
        
        # Draw dashboard elements using the shake offset.
        offset_surface = pygame.Surface((self.screen_width, self.screen_height), pygame.SRCALPHA)
        
        # Title.
        title_text = self.title_font.render("ADVANCED SYSTEM RPG", True, (255,255,0))
        offset_surface.blit(title_text, ((self.screen_width - title_text.get_width()) // 2, 10))
        
        # Level indicator.
        level_text = self.font.render(f"Level: {self.level}", True, (255,255,255))
        offset_surface.blit(level_text, (650, 10))
        
        # Health bar.
        self.draw_bar(offset_surface, 50, 70, 400, 30, self.health, (0,255,0))
        health_text = self.font.render(f"Health (100 - CPU%): {self.health:.1f}%", True, (255,255,255))
        offset_surface.blit(health_text, (50, 105))
        
        # Memory bar.
        self.draw_bar(offset_surface, 50, 140, 400, 30, self.memory, (0,0,255))
        memory_text = self.font.render(f"Memory Available: {self.memory:.1f}%", True, (255,255,255))
        offset_surface.blit(memory_text, (50, 175))
        
        # Stamina bar.
        self.draw_bar(offset_surface, 50, 210, 400, 30, self.stamina, (255,165,0))
        stamina_text = self.font.render(f"Stamina (Disk I/O): {self.stamina}%", True, (255,255,255))
        offset_surface.blit(stamina_text, (50, 245))
        
        # Battery stat.
        self.draw_bar(offset_surface, 50, 280, 400, 30, self.battery, (0,255,255))
        battery_text = self.font.render(f"Battery: {self.battery:.1f}%", True, (255,255,255))
        offset_surface.blit(battery_text, (50, 315))
        
        # CPU history graph.
        self.draw_cpu_graph(offset_surface, 500, 70, 250, 150)
        cpu_graph_label = self.font.render("CPU History", True, (255,255,255))
        offset_surface.blit(cpu_graph_label, (500, 230))
        
        # Draw instructions.
        instr_text = self.font.render("Press SPACE to heal; ESC to exit.", True, (200,200,200))
        offset_surface.blit(instr_text, (50, 370))
        
        # Draw warning if health is very low.
        if self.health < 20:
            warning_text = self.warning_font.render("WARNING: LOW HEALTH!", True, (255,0,0))
            offset_surface.blit(warning_text, ((self.screen_width - warning_text.get_width()) // 2, 350))
            # Play warning sound if available (only play once every few frames).
            if self.warning_sound and pygame.time.get_ticks() % 30 < 5:
                self.warning_sound.play()
        
        # Blit the offset surface with shake applied.
        self.screen.blit(offset_surface, self.shake_offset)
        
        # Draw particles (for heal effect).
        for particle in self.particles:
            pygame.draw.circle(self.screen, particle['color'], (int(particle['x']), int(particle['y'])), 3)

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    elif event.key == pygame.K_SPACE:
                        self.heal_bonus = 15
                        # Create heal particles at the center of the health bar.
                        self.create_heal_particles(250, 85)
                        if self.heal_sound:
                            self.heal_sound.play()
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_SPACE:
                        self.heal_bonus = 0
            
            self.update_stats()
            self.update_particles()
            self.draw_dashboard()
            
            pygame.display.update()
            self.clock.tick(60)
            
        pygame.quit()

if __name__ == "__main__":
    game = SystemRPG()
    game.run()
