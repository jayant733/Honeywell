"""Tests for Comfort Debt Ledger."""

from packages.state_engine.comfort_debt import ComfortDebtLedger

def test_debt_accrues_only_when_occupied():
    ledger = ComfortDebtLedger(optimal_band=(21.0, 24.0))
    
    # Unoccupied and cold -> No debt
    ledger.update(18.0, is_occupied=False)
    assert ledger.debt == 0.0
    
    # Occupied and cold -> Accrue debt
    ledger.update(18.0, is_occupied=True)
    assert ledger.debt == 3.0
    
    # Unoccupied and cold -> Decay debt slowly
    ledger.update(18.0, is_occupied=False)
    assert ledger.debt == 2.9
    
    # Occupied and optimal -> Decay debt quickly
    ledger.update(22.0, is_occupied=True)
    assert ledger.debt == 2.4
