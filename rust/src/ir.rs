use crate::ast::{Agent, Params, System, Value};
use std::collections::BTreeMap;

#[derive(Clone, Debug, PartialEq)]
pub struct AgentIr {
    pub phi: f64,
    pub psi: f64,
    pub frequency: f64,
    pub metadata: BTreeMap<String, Value>,
}

#[derive(Clone, Debug, PartialEq)]
pub struct SystemIr {
    pub name: String,
    pub parts: usize,
    pub resource: f64,
    pub agents: Vec<AgentIr>,
    pub params: Params,
}

impl From<&Agent> for AgentIr {
    fn from(agent: &Agent) -> Self {
        Self {
            phi: agent.phi,
            psi: agent.psi,
            frequency: agent.frequency,
            metadata: agent.metadata.clone(),
        }
    }
}

pub fn lower_system(system: &System) -> SystemIr {
    SystemIr {
        name: system.name.clone(),
        parts: system.parts,
        resource: system.resource,
        agents: system.agents.iter().map(AgentIr::from).collect(),
        params: system.params.clone(),
    }
}

fn json_string(value: &str) -> String {
    let mut out = String::from("\"");
    for ch in value.chars() {
        match ch {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\u{08}' => out.push_str("\\b"),
            '\u{0c}' => out.push_str("\\f"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            c if (c as u32) < 0x20 => out.push_str(&format!("\\u{:04x}", c as u32)),
            c => out.push(c),
        }
    }
    out.push('"');
    out
}

fn json_number(value: f64) -> String {
    if value.is_nan() {
        json_string("nan")
    } else if value == f64::INFINITY {
        json_string("inf")
    } else if value == f64::NEG_INFINITY {
        json_string("-inf")
    } else {
        format!("{:?}", value)
    }
}

fn json_value(value: &Value) -> String {
    match value {
        Value::Null => "null".into(),
        Value::Bool(value) => value.to_string(),
        Value::Number(value) => json_number(*value),
        Value::String(value) => json_string(value),
        Value::Array(values) => {
            let items: Vec<String> = values.iter().map(json_value).collect();
            format!("[{}]", items.join(","))
        }
        Value::Object(values) => {
            let items: Vec<String> = values
                .iter()
                .map(|(key, value)| format!("{}:{}", json_string(key), json_value(value)))
                .collect();
            format!("{{{}}}", items.join(","))
        }
    }
}

fn json_metadata(metadata: &BTreeMap<String, Value>) -> String {
    let items: Vec<String> = metadata
        .iter()
        .map(|(key, value)| format!("{}:{}", json_string(key), json_value(value)))
        .collect();
    format!("{{{}}}", items.join(","))
}

fn json_memory_weights(weights: &Option<Vec<f64>>) -> String {
    match weights {
        None => "null".into(),
        Some(values) => {
            let items: Vec<String> = values.iter().map(|value| json_number(*value)).collect();
            format!("[{}]", items.join(","))
        }
    }
}

fn system_ir_json(system: &SystemIr) -> String {
    let agents: Vec<String> = system
        .agents
        .iter()
        .map(|agent| {
            let mut out = String::from("{\"phi\":");
            out.push_str(&json_number(agent.phi));
            out.push_str(",\"psi\":");
            out.push_str(&json_number(agent.psi));
            out.push_str(",\"frequency\":");
            out.push_str(&json_number(agent.frequency));
            out.push_str(",\"metadata\":");
            out.push_str(&json_metadata(&agent.metadata));
            out.push('}');
            out
        })
        .collect();

    let params = &system.params;
    let mut out = String::from("{\"name\":");
    out.push_str(&json_string(&system.name));
    out.push_str(",\"parts\":");
    out.push_str(&system.parts.to_string());
    out.push_str(",\"resource\":");
    out.push_str(&json_number(system.resource));
    out.push_str(",\"agents\":[");
    out.push_str(&agents.join(","));
    out.push_str("],\"params\":{");
    out.push_str("\"alpha\":");
    out.push_str(&json_number(params.alpha));
    out.push_str(",\"gamma\":");
    out.push_str(&json_number(params.gamma));
    out.push_str(",\"sigma\":");
    out.push_str(&json_number(params.sigma));
    out.push_str(",\"coexistence_delta\":");
    out.push_str(&json_number(params.coexistence_delta));
    out.push_str(",\"model\":");
    out.push_str(&json_string(&params.model));
    out.push_str(",\"lambda\":");
    out.push_str(&json_number(params.lambda));
    out.push_str(",\"K\":");
    out.push_str(&json_number(params.k));
    out.push_str(",\"alpha_h\":");
    out.push_str(&json_number(params.alpha_h));
    out.push_str(",\"memory_order\":");
    out.push_str(&params.memory_order.to_string());
    out.push_str(",\"memory_weights\":");
    out.push_str(&json_memory_weights(&params.memory_weights));
    out.push_str(",\"degeneracy_check\":");
    out.push_str(&params.degeneracy_check.to_string());
    out.push_str(",\"omega_range_report\":");
    out.push_str(&params.omega_range_report.to_string());
    out.push_str("}}");
    out
}

/// Validate every system and emit the same versioned JSON IR shape as Python.
pub fn compile_program(systems: &[System]) -> Result<String, String> {
    for system in systems {
        crate::solver::validate_system(system)?;
    }
    let compiled: Vec<String> = systems
        .iter()
        .map(|system| system_ir_json(&lower_system(system)))
        .collect();
    Ok(format!(
        "{{\"format\":\"ronin-ir\",\"ir_version\":1,\"systems\":[{}]}}",
        compiled.join(",")
    ))
}

#[cfg(test)]
mod tests {
    use super::{compile_program, lower_system};
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
        assert_eq!(lowered.name, "Coast");
        assert_eq!(lowered.parts, 2);
        assert_eq!(lowered.resource, 100.0);
        assert_eq!(lowered.agents[0].frequency, 0.5);
        assert_eq!(lowered.params.memory_weights, Some(vec![0.7, 0.3]));
        assert!(lowered.params.degeneracy_check);
        assert!(lowered.params.omega_range_report);
    }

    #[test]
    fn compile_emits_versioned_json_ir_and_infinite_values_as_strings() {
        let systems = parse(include_str!("../../examples/maquinas.ronin")).unwrap();
        let output = compile_program(&systems).unwrap();
        assert!(output.starts_with("{\"format\":\"ronin-ir\",\"ir_version\":1"));
        assert!(output.contains("\"name\":\"Maquinas\""));
        assert!(output.contains("\"lambda\":0.0"));
        assert!(output.contains("\"K\":\"inf\""));
        assert!(output.contains("\"memory_weights\":null"));
    }

    #[test]
    fn compile_preserves_nested_metadata_and_json_escapes() {
        let source = r#"
            system Metadata = {
                parts: 2, resource: 10,
                agents: [
                    { phi: 0.6, psi: 0.7, frequency: 0.5,
                      note: "line\nquote\" slash\\",
                      profile: { enabled: true, region: "north", empty: null, tiny: 1e-300 } },
                    { phi: 0.5, psi: 0.8, frequency: 0.5 }
                ]
            }
        "#;
        let output = compile_program(&parse(source).unwrap()).unwrap();
        assert!(output.contains("\"note\":\"line\\nquote\\\" slash\\\\\""));
        assert!(output.contains("\"profile\":{\"empty\":null,\"enabled\":true,\"region\":\"north\",\"tiny\":1e-300}"));
    }

    #[test]
    fn compile_validates_all_systems_before_emitting_ir() {
        let source = r#"
            system Valid = {
                parts: 2, resource: 10,
                agents: [{phi: 0.5, psi: 0.5, frequency: 0.5},
                         {phi: 0.5, psi: 0.5, frequency: 0.5}]
            }
            system Invalid = {
                parts: 2, resource: 10,
                agents: [{phi: 0.5, psi: 0.5, frequency: 0.4},
                         {phi: 0.5, psi: 0.5, frequency: 0.5}]
            }
        "#;
        let systems = parse(source).unwrap();
        assert!(compile_program(&systems).unwrap_err().contains("frequencies must sum to 1"));
    }
}
