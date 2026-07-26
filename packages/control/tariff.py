"""Time of Use (TOU) Tariff Pricing."""

class TariffEngine:
    def get_price(self, hour: int) -> float:
        """Returns the price per kWh in USD."""
        # Peak hours 14:00 - 19:00
        if 14 <= hour <= 19:
            return 0.45
        # Partial peak 10:00 - 14:00, 19:00 - 21:00
        if (10 <= hour < 14) or (19 < hour <= 21):
            return 0.25
        # Off-peak
        return 0.12
