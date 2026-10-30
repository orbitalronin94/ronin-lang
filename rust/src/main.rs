use ronin_core::{parser, solver};
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

fn json_numbers(values: &[f64]) -> String {
    let items: Vec<String> = values.iter().map(|value| {
        if value.is_finite() { format!("{:.17}", value) } else if value.is_sign_positive() { "\"inf\"".into() } else { "\"-inf\"".into() }
    }).collect();
    format!("[{}]", items.join(","))
}

fn parse_args(args: &[String]) -> Result<(String, String, Option<String>, f64), String> {
    if args.len() < 2 {
        return Err("usage: ronin-rust <list|check|solve|run> FILE [--system NAME] [--delta VALUE]".into());
    }
    let command = args[0].clone();
    if !["list", "check", "solve", "run"].contains(&command.as_str()) {
        return Err(format!("unknown command: {}", command));
    }
    let file = args[1].clone();
    let mut system = None;
    let mut delta = 0.05;
    let mut index = 2;
    while index < args.len() {
        match args[index].as_str() {
            "--system" => {
                index += 1;
                if index >= args.len() { return Err("--system requires a name".into()); }
                system = Some(args[index].clone());
            }
            "--delta" => {
                index += 1;
                if index >= args.len() { return Err("--delta requires a number".into()); }
                delta = args[index].parse::<f64>().map_err(|_| "--delta must be numeric".to_string())?;
            }
            option => return Err(format!("unknown option: {}", option)),
        }
        index += 1;
    }
    Ok((command, file, system, delta))
}

pub fn execute(args: &[String]) -> Result<String, String> {
    let (command, file, selected, delta) = parse_args(args)?;
    let source = fs::read_to_string(&file)
        .map_err(|error| format!("cannot read {}: {}", file, error))?;
    let systems = parser::parse(&source)?;
    if systems.is_empty() { return Err("project contains no systems".into()); }

    let chosen: Vec<_> = systems.iter().filter(|system| {
        selected.as_ref().map_or(true, |name| &system.name == name)
    }).collect();
    if let Some(name) = selected.as_ref() {
        if chosen.is_empty() { return Err(format!("unknown system: {}", name)); }
    }

    if command == "list" {
        return Ok(chosen.iter().map(|system| system.name.as_str()).collect::<Vec<_>>().join("\n"));
    }

    if command == "check" {
        for system in &chosen { solver::solve(system, delta)?; }
        return Ok(format!("OK: {} system(s) validated", chosen.len()));
    }

    let mut entries = Vec::new();
    for system in chosen {
        let result = solver::solve(system, delta)?;
        let entry = format!(
            "{}:{{\"allocation\":{},\"fitness\":{},\"model_used\":{},\"lambda_used\":{:.17},\"K_used\":{},\"alpha_h_used\":{:.17}}}",
            json_string(&system.name),
            json_numbers(&result.allocation),
            json_numbers(&result.fitness),
            json_string(&result.model_used),
            result.lambda_used,
            if result.k_used.is_finite() { format!("{:.17}", result.k_used) } else { json_string("inf") },
            result.alpha_h_used,
        );
        entries.push(entry);
    }
    Ok(format!("{{{}}}", entries.join(",")))
}

fn main() {
    let args: Vec<String> = env::args().skip(1).collect();
    match execute(&args) {
        Ok(output) => println!("{}", output),
        Err(error) => {
            eprintln!("ronin-rust: {}", error);
            std::process::exit(1);
        }
    }
}

#[cfg(test)]
mod tests {
    use super::execute;
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
    fn system_filter_rejects_unknown_names() {
        let args = vec!["solve".into(), fixture(), "--system".into(), "Missing".into()];
        assert!(execute(&args).unwrap_err().contains("unknown system: Missing"));
    }
}
