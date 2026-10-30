use ronin_core::{Agent, Params, System};
use ronin_core::solver::solve;
use ronin_core::simulator::{project_simplex, simulate};
use ronin_core::diagnose::diagnose;

fn machine() -> System {
    System {
        name: "Maquinas".into(), parts: 2, resource: 100.0,
        agents: vec![
            Agent { phi: 0.8, psi: 1.0, frequency: 0.6 },
            Agent { phi: 0.5, psi: 1.0, frequency: 0.4 },
        ],
        params: Params {
            alpha: 1.0, gamma: 0.4, sigma: 0.1, model: "pusfre".into(),
            lambda: 0.0, k: f64::INFINITY, alpha_h: 1.0, memory_order: 1,
            coexistence_delta: 0.05,
        },
    }
}

#[test]
fn legacy_machine_matches_reference_values() {
    let result = solve(&machine(), 0.05).unwrap();
    assert!((result.fitness[0] - 0.48).abs() < 1e-12);
    assert!((result.fitness[1] - 0.20).abs() < 1e-12);
    assert!((result.allocation[0] - 70.58823529411765).abs() < 1e-9);
    assert!((result.allocation[1] - 29.41176470588235).abs() < 1e-9);
}

#[test]
fn simplex_projection_is_normalized() {
    let projected = project_simplex(&[-1.0, 2.0, 2.0]);
    assert!(projected.iter().all(|x| *x >= 0.0));
    assert!((projected.iter().sum::<f64>() - 1.0).abs() < 1e-12);
}

#[test]
fn seeded_simulation_is_reproducible() {
    let a = simulate(&machine(), 20, Some(42)).unwrap();
    let b = simulate(&machine(), 20, Some(42)).unwrap();
    assert_eq!(a.history, b.history);
    assert_eq!(a.final_state, b.final_state);
}

#[test]
fn diagnose_reports_unknown_with_one_positive_omega() {
    let mut system = machine();
    system.agents[0] = Agent { phi: 0.8, psi: 1.0, frequency: 1.0 };
    system.agents[1] = Agent { phi: 0.5, psi: 1.0, frequency: 0.0 };
    let report = diagnose(&system, 0).unwrap();
    assert_eq!(report.degeneracy, "unknown");
}

#[test]
fn temporal_memory_is_rejected_until_implemented() {
    let mut system = machine();
    system.params.model = "full".into();
    system.params.lambda = 0.5;
    system.params.k = 1.0;
    system.params.memory_order = 2;
    assert!(solve(&system, 0.05).unwrap_err().contains("temporal-memory"));
}
