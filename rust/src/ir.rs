use crate::ast::{Agent, Params, System, Value};
use std::collections::BTreeMap;

#[derive(Clone, Debug, PartialEq)]
pub struct AgentIr {
    pub phi: f64,
    pub psi: f64,
    pub omega: f64,
    pub metadata: BTreeMap<String, Value>,
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
        Self {
            phi: agent.phi,
            psi: agent.psi,
            omega: agent.frequency,
            metadata: agent.metadata.clone(),
        }
    }
}

pub fn lower_system(system: &System) -> SystemIr {
    SystemIr {
        name: system.name.clone(),
        resource: system.resource,
        agents: system.agents.iter().map(AgentIr::from).collect(),
        params: system.params.clone(),
    }
}

#[cfg(test)]
mod tests {
    use super::lower_system;
    use crate::ast::Value;
    use crate::parser::parse;

    #[test]
    fn lowering_preserves_agent_metadata_and_extended_params() {
        let source = r#"
            system Coast = {
                parts: 2, resource: 100,
                agents: [
                    { phi: 0.6, psi: 0.9, frequency: 0.5,
                      niche: [0.2, 0.4], protocol: "artisanal" },
                    { phi: 0.5, psi: 0.8, frequency: 0.5 }
                ],
                params: { memory_weights: [0.7, 0.3],
                          degeneracy_check: true, omega_range_report: true }
            }
        "#;
        let systems = parse(source).unwrap();
        let lowered = lower_system(&systems[0]);
        assert_eq!(
            lowered.agents[0].metadata.get("protocol"),
            Some(&Value::String("artisanal".into()))
        );
        assert_eq!(
            lowered.agents[0].metadata.get("niche"),
            Some(&Value::Array(vec![Value::Number(0.2), Value::Number(0.4)]))
        );
        assert_eq!(lowered.params.memory_weights, Some(vec![0.7, 0.3]));
        assert!(lowered.params.degeneracy_check);
        assert!(lowered.params.omega_range_report);
    }
}
