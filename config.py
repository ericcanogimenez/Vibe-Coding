"""
Configuración del juego Mini Street Fighter
Parámetros ajustables para balance y dificultad
"""

# Configuración de pantalla
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 600
FPS = 60

# Configuración de colores
COLORS = {
    'BLACK': (0, 0, 0),
    'WHITE': (255, 255, 255),
    'RED': (255, 0, 0),
    'GREEN': (0, 255, 0),
    'BLUE': (0, 0, 255),
    'YELLOW': (255, 255, 0),
    'GRAY': (128, 128, 128),
    'DARK_GRAY': (64, 64, 64),
    'LIGHT_BLUE': (100, 150, 255),
    'LIGHT_RED': (255, 100, 100),
}

# Configuración del jugador
PLAYER_CONFIG = {
    'max_health': 100,
    'speed': 5,
    'attack_damage': 15,
    'attack_range': 80,
    'attack_cooldown': 30,
    'jump_power': 15,
    'width': 50,
    'height': 100,
}

# Configuración del enemigo
ENEMY_CONFIG = {
    'max_health': 100,
    'speed': 3.5,  # Ligeramente más lento que el jugador
    'attack_damage': 15,
    'attack_range': 80,
    'attack_cooldown': 30,
    'jump_power': 15,
    'width': 50,
    'height': 100,
    'ai_attack_probability': 0.02,  # 2% por frame
    'ai_jump_probability': 0.01,    # 1% por frame
}

# Configuración de física
PHYSICS_CONFIG = {
    'gravity': 0.5,
    'knockback_duration': 5,
    'knockback_force': 3,
}

# Configuración de IA
AI_CONFIG = {
    'follow_distance': 300,  # Distancia a la que el enemigo comienza a perseguir
    'attack_distance': 80,   # Distancia a la que el enemigo intenta atacar
    'difficulty_multiplier': 1.0,  # 1.0 = normal, 1.5 = difícil
}
