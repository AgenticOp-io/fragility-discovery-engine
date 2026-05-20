from coupled_institution.replay import REPLAY_SCHEMA_VERSION
from coupled_institution.rollout import random_schedule, rollout_coupled
from coupled_institution.types import ExogenousEvent
from coupled_institution.world import CoupledInstitutionWorld, coupled_rollout_snapshot


def test_coupled_rollout_deterministic():
    a = coupled_rollout_snapshot(steps=5, seed=1)
    b = coupled_rollout_snapshot(steps=5, seed=1)
    assert a == b
    assert a["simulation_mode"] == "coupled_institution_v1"
    assert a["schema_version"] == REPLAY_SCHEMA_VERSION


def test_coupled_world_step():
    w = CoupledInstitutionWorld(coupling_strength=0.3)
    w.reset()
    row = w.step_shocks(reserve_loss=0.5, rumor=0.1)
    assert "instability" in row


def test_rollout_events_lane():
    w = CoupledInstitutionWorld()
    sched = [
        (ExogenousEvent("reserve_loss", 0.4),),
        (),
        (ExogenousEvent("rumor", 0.2),),
    ]
    r = rollout_coupled(w, sched, seed=7)
    assert len(r.trajectory) == 3
    replay = r.to_replay_dict()
    assert replay["simulation_mode"] == "coupled_institution_v1"


def test_random_schedule_rollout():
    w = CoupledInstitutionWorld(coupling_strength=0.2)
    sched = random_schedule(6, seed=3)
    r = rollout_coupled(w, sched, seed=3)
    assert r.integral_instability >= 0.0
