from coupled_institution.world import CoupledInstitutionWorld, coupled_rollout_snapshot


def test_coupled_rollout_deterministic():
    a = coupled_rollout_snapshot(steps=5, seed=1)
    b = coupled_rollout_snapshot(steps=5, seed=1)
    assert a == b
    assert a["simulation_mode"] == "coupled_institution_v0"


def test_coupled_world_step():
    w = CoupledInstitutionWorld(coupling_strength=0.3)
    w.reset()
    row = w.step_shocks(reserve_loss=0.5, rumor=0.1)
    assert "instability" in row
