use ronin_core::{diagnose, ir, parser, solver};
use std::env;
use std::fs;

fn json_string(value: &str) -> String {
    let mut out = String::from("\"");
    for ch in value.chars() {
        match ch {
            '"' => out.push_str("\\\""),
            '\\' => out.push_str("\\\\"),
            '\n' => out.push_str("\\n"),
            '\r' => out.push_str("\\r"),
            '\t' => out.push_str("\\t"),
            c if c.is_control() => out.push_str(&format!("\\u{:04x}", c as u32)),
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

fn json_option_number(value: Option<f64>) -> String {
    value.map(json_number).unwrap_or_else(|| "null".into())
}

fn json_option_bool(value: Option<bool>) -> String {
    value.map(|item| item.to_string()).unwrap_or_else(|| "null".into())
}

fn json_numbers(values: &[f64]) -> String {
    let items: Vec<String> = values.iter().map(|value| {
        if value.is_finite() {
            json_number(*value)
        } else if value.is_sign_positive() {
            "\"inf\"".into()
        } else {
            "\"-inf\"".into()
        }
    }).collect();
    format!("[{}]", items.join(","))
}

fn parse_args(
    args: &[String],
) -> Result<(String, String, Option<String>, Option<f64>, Option<String>, Option<usize>), String> {
    if args.len() < 2 {
        return Err(
            "usage: ronin-core <list|check|solve|run|compile> FILE [--system NAME] [--delta VALUE] [-o PATH]".into()
        );
    }
    let command = args[0].clone();
    if !["list", "check", "solve", "run", "compile", "diagnose"].contains(&command.as_str()) {
        return Err(format!("unknown command: {}", command));
    }
    let file = args[1].clone();
    let mut system = None;
    let mut delta = None;
    let mut output = None;
    let mut bootstrap = None;
    let mut index = 2;
    while index < args.len() {
        match args[index].as_str() {
            "--system" => {
                index += 1;
                if index >= args.len() {
                    return Err("--system requires a name".into());
                }
                system = Some(args[index].clone());
            }
            "--delta" => {
                index += 1;
                if index >= args.len() {
                    return Err("--delta requires a number".into());
                }
                delta = Some(
                    args[index]
                        .parse::<f64>()
                        .map_err(|_| "--delta must be numeric".to_string())?
                );
            }
            "--bootstrap" => {
                index += 1;
                if index >= args.len() {
                    return Err("--bootstrap requires an integer".into());
                }
                bootstrap = Some(
                    args[index]
                        .parse::<usize>()
                        .map_err(|_| "--bootstrap must be a non-negative integer".to_string())?
                );
            }
            "-o" | "--output" => {
                index += 1;
                if index >= args.len() {
                    return Err("--output requires a path".into());
                }
                output = Some(args[index].clone());
            }
            option => return Err(format!("unknown option: {}", option)),
        }
        index += 1;
    }
    if output.is_some() && command != "compile" {
        return Err("--output is only supported by compile".into());
    }
    if bootstrap.is_some() && command != "diagnose" {
        return Err("--bootstrap is only supported by diagnose".into());
    }
    if system.is_some() && command == "compile" {
        return Err("--system is not supported by compile; all systems are compiled".into());
    }
    Ok((command, file, system, delta, output, bootstrap))
}

pub fn execute(args: &[String]) -> Result<String, String> {
    let (command, file, selected, delta, output_path, bootstrap) = parse_args(args)?;
    let source = fs::read_to_string(&file)
        .map_err(|error| format!("cannot read {}: {}", file, error))?;
    let systems = parser::parse(&source)?;
    if systems.is_empty() {
        return Err("project contains no systems".into());
    }

    if command == "compile" {
        let output = ir::compile_program(&systems)?;
        if let Some(path) = output_path {
            fs::write(&path, format!("{}\n", output))
                .map_err(|error| format!("cannot write {}: {}", path, error))?;
            return Ok(String::new());
        }
        return Ok(output);
    }

    let chosen: Vec<_> = systems.iter().filter(|system| {
        selected.as_ref().map_or(true, |name| &system.name == name)
    }).collect();
    if let Some(name) = selected.as_ref() {
        if chosen.is_empty() {
            return Err(format!("unknown system: {}", name));
        }
    }

    if command == "list" {
        return Ok(chosen.iter().map(|system| system.name.as_str()).collect::<Vec<_>>().join("\n"));
    }

    if command == "diagnose" {
        let system = chosen.first().ok_or_else(|| "project contains no systems".to_string())?;
        let report = diagnose::diagnose(system, bootstrap.unwrap_or(0))?;
        return Ok(format!(
            "{{\"omega_range_orders\":{},\"degeneracy\":{},\"lambda_identifiable\":{},\"K_identifiable\":{},\"alpha_h_identifiable\":{},\"recommendation\":{},\"bootstrap_ci\":null}}",
            json_number(report.omega_range_orders),
            json_string(&report.degeneracy),
            report.lambda_identifiable,
            report.k_identifiable,
            report.alpha_h_identifiable,
            json_string(&report.recommendation),
        ));
    }

    if command == "check" {
        for system in &chosen {
            solver::solve(system, delta.unwrap_or(system.params.coexistence_delta))?;
        }
        return Ok(format!("OK: {} system(s) validated", chosen.len()));
    }

    let mut entries = Vec::new();
    for system in chosen {

        let result = solver::solve(system, delta.unwrap_or(system.params.coexistence_delta))?;
        let entry = format!(
            "{}:{{\"allocation\":{},\"fitness\":{},\"coexistence\":{},\"k_min\":{},\"model_used\":{},\"lambda_used\":{},\"K_used\":{},\"alpha_h_used\":{},\"omega_range\":{},\"degeneracy\":{}}}",
            json_string(&system.name),
            json_numbers(&result.allocation),
            json_numbers(&result.fitness),
            json_option_bool(result.coexistence),
            json_option_number(result.k_min),
            json_string(&result.model_used),
            json_number(result.lambda_used),
            json_number(result.k_used),
            json_number(result.alpha_h_used),
            json_number(result.omega_range_orders),
            json_string(&result.degeneracy),
        );
        entries.push(entry);
    }
    Ok(format!("{{{}}}", entries.join(",")))
}

fn main() {
    let args: Vec<String> = env::args().skip(1).collect();
    match execute(&args) {
        Ok(output) if !output.is_empty() => println!("{}", output),
        Ok(_) => {}
        Err(error) => {
            eprintln!("ronin-core: {}", error);
            std::process::exit(1);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::execute;
    use std::fs;
    use std::path::PathBuf;

    fn fixture() -> String {
        PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .join("../examples/maquinas.ronin")
            .to_string_lossy()
            .into_owned()
    }

    #[test]
    fn list_command_prints_every_system_name() {
        let args = vec!["list".into(), fixture()];
        assert_eq!(execute(&args).unwrap(), "Maquinas");
    }

    #[test]
    fn check_command_validates_project() {
        let args = vec!["check".into(), fixture()];
        assert_eq!(execute(&args).unwrap(), "OK: 1 system(s) validated");
    }

    #[test]
    fn solve_command_emits_json_results() {
        let args = vec!["solve".into(), fixture()];
        let output = execute(&args).unwrap();
        assert!(output.starts_with("{\"Maquinas\":{"));
        assert!(output.contains("\"allocation\":["));
        assert!(output.contains("\"fitness\":["));
    }

    #[test]
    fn compile_command_emits_versioned_ir() {
        let args = vec!["compile".into(), fixture()];
        let output = execute(&args).unwrap();
        assert!(output.starts_with("{\"format\":\"ronin-ir\",\"ir_version\":1"));
        assert!(output.contains("\"name\":\"Maquinas\""));
        assert!(output.contains("\"K\":\"inf\""));
    }

    #[test]
    fn compile_command_writes_ir_to_requested_file() {
        let path = std::env::temp_dir()
            .join(format!("ronin-ir-{}.json", std::process::id()));
        let args = vec![
            "compile".into(),
            fixture(),
            "--output".into(),
            path.to_string_lossy().into_owned(),
        ];
        assert_eq!(execute(&args).unwrap(), "");
        let output = fs::read_to_string(&path).unwrap();
        assert!(output.contains("\"format\":\"ronin-ir\""));
        fs::remove_file(path).unwrap();
    }

    #[test]
    fn compile_rejects_invalid_project() {
        let path = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .join("../tests/fixtures/conformance/invalid_frequency_sum.ronin")
            .to_string_lossy()
            .into_owned();
        let args = vec!["compile".into(), path];
        assert!(execute(&args).unwrap_err().contains("frequencies must sum to 1"));
    }

    #[test]
    fn compile_rejects_system_filter() {
        let args = vec!["compile".into(), fixture(), "--system".into(), "Maquinas".into()];
        assert!(execute(&args).unwrap_err().contains("--system is not supported"));
    }

    #[test]
    fn system_filter_rejects_unknown_names() {
        let args = vec!["solve".into(), fixture(), "--system".into(), "Missing".into()];
        assert!(execute(&args).unwrap_err().contains("unknown system: Missing"));
    }
}
