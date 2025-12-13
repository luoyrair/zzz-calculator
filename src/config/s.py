class DisplayConfig:
    RARITY_COLOR_MAPPING = {
        4: "#B28BEA", 5: "#FFD700"
    }

    def get_rarity_color(self, rarity: int) -> str:
        return self.RARITY_COLOR_MAPPING.get(rarity, "#000000")