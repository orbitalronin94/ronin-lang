use ronin_core::{diagnose, ir, parser, simulator, solver};
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

fn csv_field(value: &str) -> String {
    if value.contains(',') || value.contains('"') || value.contains('\n') || value.contains('\r') {
        format!("\"{}\"", value.replace('"', "\"\""))
    } else {
        value.to_string()
    }
}

fn parse_args(
    args: &[String],
) -> Result<(String, String, Option<String>, Option<f64>, Option<String>, Option<usize>, Option<usize>, Option<u64>, Option<String>), String> {
    if args.len() < 2 {
        return Err(
            "usage: ronin-core <list|check|solve|run|compile|diagnose|simulate> FILE [--system NAME] [--delta VALUE] [--steps N] [--seed N] [--bootstrap N] [-o PATH]".into()
        );
    }
    let command = args[0].clone();
    if !["list", "check", "solve", "run", "compile", "diagnose", "simulate"].contains(&command.as_str()) {
        return Err(format!("unknown command: {}", command));
    }
    let file = args[1].clone();
    let mut system = None;
    let mut delta = None;
    let mut output = None;
    let mut bootstrap = None;
    let mut steps = None;
    let mut seed = None;
    let mut output_format = None;
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
            "--steps" => {
                index += 1;
                if index >= args.len() {
                    return Err("--steps requires an integer".into());
                }
                steps = Some(args[index].parse::<usize>()
                    .map_err(|_| "--steps must be a positive integer".to_string())?);
            }
            "--seed" => {
                index += 1;
                if index >= args.len() {
                    return Err("--seed requires an unsigned integer".into());
                }
                seed = Some(args[index].parse::<u64>()
                    .map_err(|_| "--seed must be an unsigned integer".to_string())?);
            }
            "--format" => {
                index += 1;
                if index >= args.len() {
                    return Err("--format requires json or csv".into());
                }
                output_format = Some(args[index].clone());
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
    if (steps.is_some() || seed.is_some()) && command != "simulate" {
        return Err("--steps and --seed are only supported by simulate".into());
    }
    if steps == Some(0) {
        return Err("--steps must be >= 1".into());
    }
    if let Some(ref value) = output_format {
        if !["json", "csv"].contains(&value.as_str()) {
            return Err("--format must be json or csv".into());
        }
        if command != "run" {
            return Err("--format is only supported by run".into());
        }
    }
    if bootstrap.is_some() && command != "diagnose" {
        return Err("--bootstrap is only supported by diagnose".into());
    }
    if system.is_some() && command == "compile" {
        return Err("--system is not supported by compile; all systems are compiled".into());
    }
    Ok((command, file, system, delta, output, bootstrap, steps, seed, output_format))
}

pub fn execute(args: &[String]) -> Result<String, String> {
    let (command, file, selected, delta, output_path, bootstrap, steps, seed, output_format) = parse_args(args)?;
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

    let mut chosen: Vec<_> = systems.iter().filter(|system| {
        selected.as_ref().map_or(true, |name| &system.name == name)
    }).collect();
    if let Some(name) = selected.as_ref() {
        if chosen.is_empty() {
            return Err(format!("unknown system: {}", name));
        }
    }

    if command == "solve" && selected.is_none() {
        chosen.truncate(1);
    }

    if command == "list" {
        return Ok(chosen.iter().map(|system| system.name.as_str()).collect::<Vec<_>>().join("\n"));
    }

    if command == "simulate" {
        let system = chosen.first().ok_or_else(|| "project contains no systems".to_string())?;
        let result = simulator::simulate(system, steps.unwrap_or(100), seed)?;
        let history: Vec<String> = result.history.iter().map(|state| json_numbers(state)).collect();
        let extinctions = result.extinction_events.iter().map(|index| index.to_string()).collect::<Vec<_>>().join(",");
        let seed_json = result.seed.map(|value| value.to_string()).unwrap_or_else(|| "null".into());
        return Ok(format!(
            "{{\"history\":[{}],\"final_state\":{},\"steps\":{},\"seed\":{},\"extinction_events\":[{}],\"survivability\":{}}}",
            history.join(","),
            json_numbers(&result.final_state),
            result.steps,
            seed_json,
            extinctions,
            json_number(result.survivability),
        ));
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
            solver::validate_system(system)?;
        }
        return Ok(format!("OK: {} system(s) validated", chosen.len()));
    }

    let mut entries = Vec::new();
    let mut csv_rows = Vec::new();
    for system in chosen {

        let result = solver::solve(system, delta.unwrap_or(system.params.coexistence_delta))?;
        for (index, (fitness, allocation)) in result.fitness.iter().zip(result.allocation.iter()).enumerate() {
            csv_rows.push(format!(
                "{},{},{},{:.17},{:.17}",
                csv_field(&system.name),
                index + 1,
                csv_field(&system.params.model),
                fitness,
                allocation,
            ));
        }
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
    if command == "run" && output_format.as_deref() == Some("csv") {
        let mut csv = String::from("system,agent_index,model,fitness,allocation\n");
        csv.push_str(&csv_rows.join("\n"));
        csv.push('\n');
        return Ok(csv);
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
    use super::{csv_field, execute};
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
    fn check_command_validates_without_running_solver() {
        let path = std::env::temp_dir()
            .join(format!("ronin-zero-fitness-{}.ronin", std::process::id()));
        let source = r#"
            system ZeroFitness = {
                parts: 2, resource: 10,
                agents: [
                    { phi: 0.0, psi: 0.0, frequency: 0.5 },
                    { phi: 0.0, psi: 0.0, frequency: 0.5 }
                ]
            }
        "#;
        fs::write(&path, source).unwrap();
        let args = vec!["check".into(), path.to_string_lossy().into_owned()];
        let result = execute(&args).unwrap();
        assert_eq!(result, "OK: 1 system(s) validated");
        fs::remove_file(path).unwrap();
    }

    #[test]
    fn check_command_validates_project() {
        let args = vec!["check".into(), fixture()];
        assert_eq!(execute(&args).unwrap(), "OK: 1 system(s) validated");
    }

    #[test]
    fn run_command_exports_csv_with_one_row_per_agent() {
        let args = vec!["run".into(), fixture(), "--format".into(), "csv".into()];
        let output = execute(&args).unwrap();
        let lines: Vec<&str> = output.lines().collect();
        assert_eq!(lines[0], "system,agent_index,model,fitness,allocation");
        assert_eq!(lines.len(), 3);
        assert!(lines[1].starts_with("Maquinas,1,pusfre,"));
        assert!(lines[2].starts_with("Maquinas,2,pusfre,"));
    }

    #[test]
    fn run_command_keeps_json_as_default_format() {
        let args = vec!["run".into(), fixture()];
        let output = execute(&args).unwrap();
        assert!(output.starts_with("{\"Maquinas\":{"));
    }

    #[test]
    fn format_option_is_restricted_to_run_and_known_values() {
        let args = vec!["solve".into(), fixture(), "--format".into(), "csv".into()];
        assert!(execute(&args).unwrap_err().contains("--format is only supported by run"));
        let args = vec!["run".into(), fixture(), "--format".into(), "xml".into()];
        assert!(execute(&args).unwrap_err().contains("--format must be json or csv"));
    }

    #[test]
    fn csv_field_quotes_commas_quotes_and_newlines() {
        assert_eq!(csv_field("a,b"), "\"a,b\"");
        assert_eq!(csv_field("say \"hi\""), "\"say \"\"hi\"\"\"");
    }

    #[test]
    fn solve_defaults_to_first_system_while_run_executes_all() {
        let path = std::env::temp_dir()
            .join(format!("ronin-multi-solve-{}.ronin", std::process::id()));
        let source = r#"
            system First = {
                parts: 2, resource: 10,
                agents: [
                    { phi: 0.5, psi: 0.5, frequency: 0.5 },
                    { phi: 0.5, psi: 0.5, frequency: 0.5 }
                ]
            }
            system Second = {
                parts: 2, resource: 20,
                agents: [
                    { phi: 0.6, psi: 0.5, frequency: 0.5 },
                    { phi: 0.5, psi: 0.6, frequency: 0.5 }
                ]
            }
        "#;
        fs::write(&path, source).unwrap();
        let file = path.to_string_lossy().into_owned();

        let solve = execute(&vec!["solve".into(), file.clone()]).unwrap();
        assert!(solve.contains("\"First\""));
        assert!(!solve.contains("\"Second\""));

        let run = execute(&vec!["run".into(), file.clone()]).unwrap();
        assert!(run.contains("\"First\""));
        assert!(run.contains("\"Second\""));

        let selected = execute(&vec!["solve".into(), file, "--system".into(), "Second".into()]).unwrap();
        assert!(selected.contains("\"Second\""));
        assert!(!selected.contains("\"First\""));
        fs::remove_file(path).unwrap();
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
    fn simulate_command_emits_reproducible_json_for_explicit_seed() {
        let args = vec!["simulate".into(), fixture(), "--steps".into(), "8".into(), "--seed".into(), "42".into()];
        let first = execute(&args).unwrap();
        let second = execute(&args).unwrap();
        assert_eq!(first, second);
        assert!(first.contains("\"steps\":8"));
        assert!(first.contains("\"seed\":42"));
        assert!(first.contains("\"history\":["));
        assert!(first.contains("\"final_state\":["));
    }

    #[test]
    fn simulate_command_rejects_zero_steps() {
        let args = vec!["simulate".into(), fixture(), "--steps".into(), "0".into()];
        assert!(execute(&args).unwrap_err().contains("--steps must be >= 1"));
    }

    #[test]
    fn simulate_flags_are_rejected_for_other_commands() {
        let args = vec!["solve".into(), fixture(), "--seed".into(), "42".into()];
        assert!(execute(&args).unwrap_err().contains("only supported by simulate"));
    }

    #[test]
    fn diagnose_command_emits_python_compatible_report() {
        let path = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .join("../tests/fixtures/conformance/degeneracy_active.ronin")
            .to_string_lossy()
            .into_owned();
        let args = vec!["diagnose".into(), path];
        let output = execute(&args).unwrap();
        assert!(output.contains("\"degeneracy\":\"active\""));
        assert!(output.contains("\"bootstrap_ci\":null"));
        assert!(output.contains("\"K_identifiable\":false"));
    }

    #[test]
    fn diagnose_accepts_bootstrap_flag_without_fabricating_interval() {
        let path = PathBuf::from(env!("CARGO_MANIFEST_DIR"))
            .join("../tests/fixtures/conformance/degeneracy_active.ronin")
            .to_string_lossy()
            .into_owned();
        let args = vec!["diagnose".into(), path, "--bootstrap".into(), "100".into()];
        let output = execute(&args).unwrap();
        assert!(output.contains("\"bootstrap_ci\":null"));
    }

    #[test]
    fn diagnose_rejects_negative_bootstrap_count() {
        let args = vec!["diagnose".into(), fixture(), "--bootstrap".into(), "-1".into()];
        assert!(execute(&args).unwrap_err().contains("--bootstrap must be a non-negative integer"));
    }

    #[test]
    fn diagnose_rejects_bootstrap_flag_on_other_commands() {
        let args = vec!["solve".into(), fixture(), "--bootstrap".into(), "100".into()];
        assert!(execute(&args).unwrap_err().contains("--bootstrap is only supported by diagnose"));
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
