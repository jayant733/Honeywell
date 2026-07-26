"""Comfort Debt Ledger."""

class ComfortDebtLedger:
    def __init__(self, optimal_band: tuple = (21.0, 24.0)):
        self.optimal_band = optimal_band
        self.debt = 0.0

    def update(self, temperature: float, is_occupied: bool) -> float:
        """
        Calculates comfort debt. 
        Only adds debt if the zone is occupied and outside the optimal band.
        Slowly decays debt over time when conditions are optimal.
        """
        if not is_occupied:
            # Decay debt slowly when unoccupied
            self.debt = max(0.0, self.debt - 0.1)
            return self.debt
            
        if temperature < self.optimal_band[0]:
            violation = self.optimal_band[0] - temperature
            self.debt += violation
        elif temperature > self.optimal_band[1]:
            violation = temperature - self.optimal_band[1]
            self.debt += violation
        else:
            # Decay debt quickly when occupied and comfortable
            self.debt = max(0.0, self.debt - 0.5)
            
        return self.debt
