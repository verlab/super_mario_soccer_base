class PlayerType(object):
    """
    Player type that is created by the server at the beginning. Eg
    '(player_type (id 3)(player_speed_max 1.05)(stamina_inc_max 45.2417)
     (player_decay 0.411652)(inertia_moment 5.29131)(dash_power_rate 0.00595971)
     (player_size 0.3)(kickable_margin 0.648323)(kick_rand 0.0483225)
     (extra_stamina 93.7022)(effort_max 0.825191)(effort_min 0.425191))
    """

    def __init__(self):
        self.id = None
        self.player_speed_max = None
        self.stamina_inc_max = None
        self.player_decay = None
        self.inertia_moment = None
        self.dash_power_rate = None
        self.player_size = None
        self.kickable_margin = None
        self.kick_rand = None
        self.extra_stamina = None
        self.effort_max = None
        self.effort_min = None