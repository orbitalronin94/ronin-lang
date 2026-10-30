#[derive(Clone, Debug, PartialEq)]
pub struct Agent {
    pub phi: f64,
    pub psi: f64,
    pub frequency: f64,
}

#[derive(Clone, Debug, PartialEq)]
pub struct Params {
    pub alpha: f64,
    pub gamma: f64,
    pub sigma: f64,
    pub model: String,
    pub lambda: f64,
    pub k: f64,
    pub alpha_h: f64,
    pub memory_order: usize,
}

#[derive(Clone, Debug, PartialEq)]
pub struct System {
    pub name: String,
    pub parts: usize,
    pub resource: f64,
    pub agents: Vec<Agent>,
    pub params: Params,
}

#[derive(Clone, Debug, PartialEq)]
pub struct Solution {
    pub allocation: Vec<f64>,
    pub fitness: Vec<f64>,
    pub coexistence: Option<bool>,
    pub k_min: Option<f64>,
    pub model_used: String,
    pub lambda_used: f64,
    pub k_used: f64,
    pub alpha_h_used: f64,
    pub omega_range_orders: f64,
    pub degeneracy: String,
}

#[derive(Clone, Debug, PartialEq)]
pub struct Simulation {
    pub history: Vec<Vec<f64>>,
    pub final_state: Vec<f64>,
    pub steps: usize,
    pub seed: Option<u64>,
    pub extinction_events: Vec<usize>,
    pub survivability: f64,
}

#[derive(Clone, Debug, PartialEq)]
pub struct DegeneracyReport {
    pub omega_range_orders: f64,
    pub degeneracy: String,
    pub lambda_identifiable: bool,
    pub k_identifiable: bool,
    pub alpha_h_identifiable: bool,
    pub recommendation: String,
}
