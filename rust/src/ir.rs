use crate::ast::{Agent, Params, System};

#[derive(Clone, Debug, PartialEq)]
pub struct AgentIr {
    pub phi: f64,
    pub psi: f64,
    pub omega: f64,
}

#[derive(Clone, Debug, PartialEq)]
pub struct SystemIr {
    pub name: String,
    pub resource: f64,
    pub agents: Vec<AgentIr>,
    pub params: Params,
}

impl From<&Agent> for AgentIr {
    fn from(agent: &Agent) -> Self {
        Self { phi: agent.phi, psi: agent.psi, omega: agent.frequency }
    }
}

pub fn lower_system(system: &System) -> SystemIr {
    todo!("Implementar lowering AST -> IR según Parte IV")
}
