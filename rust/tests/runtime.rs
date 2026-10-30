use ronin_core::{Agent, Params, System};
use ronin_core::solver::solve;
use ronin_core::simulator::{project_simplex, simulate};
use ronin_core::diagnose::diagnose;

fn machine() -> System {
    System {
        name: "Maquinas".into(), parts: 2, resource: 100.0,
        agents: vec![
            Agent { phi: 0.8, psi: 1.0, frequency: 0.6, metadata: Default::default() },
            Agent { phi: 0.5, psi: 1.0, frequency: 0.4, metadata: Default::default() },
        ],
        params: Params {
            alpha: 1.0, gamma: 0.4, sigma: 0.1, model: "pusfre".into(),
            lambda: 0.0, k: f64::INFINITY, alpha_h: 1.0, memory_order: 1,
            coexistence_delta: 0.05, memory_weights: None, degeneracy_check: false, omega_range_report: false,
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
    system.agents[0] = Agent { phi: 0.8, psi: 1.0, frequency: 1.0, metadata: Default::default() };
    system.agents[1] = Agent { phi: 0.5, psi: 1.0, frequency: 0.0, metadata: Default::default() };
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

#[test]
fn parser_preserves_nested_agent_metadata_and_optional_parameters() {
    use ronin_core::parser::parse;
    use ronin_core::Value;
    let source = r#"
      system Fishery = {
        parts: 2, resource: 100,
        agents: [
          { phi: 0.6, psi: 0.9, frequency: 0.5,
            niche: [0.1, 0.3, 0.5], tools: ["longline", "hook"],
            protocol: "artisanal", enabled: true, notes: null },
          { phi: 0.5, psi: 0.8, frequency: 0.5 }
        ],
        params: { memory_weights: [0.6, 0.3, 0.1],
          degeneracy_check: true, omega_range_report: false }
      }
    "#;
    let systems = parse(source).unwrap();
    let system = &systems[0];
    assert_eq!(system.agents[0].metadata.get("protocol"), Some(&Value::String("artisanal".into())));
    assert_eq!(system.agents[0].metadata.get("enabled"), Some(&Value::Bool(true)));
    assert_eq!(system.agents[0].metadata.get("notes"), Some(&Value::Null));
    assert_eq!(system.agents[0].metadata.get("niche"),
      Some(&Value::Array(vec![Value::Number(0.1), Value::Number(0.3), Value::Number(0.5)])));
    assert_eq!(system.params.memory_weights, Some(vec![0.6, 0.3, 0.1]));
    assert!(system.params.degeneracy_check);
    assert!(!system.params.omega_range_report);
}

#[test]
fn parser_rejects_invalid_optional_parameter_types() {
    use ronin_core::parser::parse;
    let source = r#"system S = { parts: 2, resource: 1,
      agents: [{phi: 1, psi: 1, frequency: 0.5}, {phi: 1, psi: 1, frequency: 0.5}],
      params: { degeneracy_check: "yes" } }"#;
    assert!(parse(source).unwrap_err().contains("degeneracy_check must be boolean"));
}
