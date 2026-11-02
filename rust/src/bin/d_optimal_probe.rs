use ronin_core::d_optimal_design;
use std::env;

fn parse_vector(value: &str) -> Result<Vec<f64>, String> {
    value.split(',')
        .map(|part| part.parse::<f64>().map_err(|_| format!("invalid number: {part}")))
        .collect()
}

fn json_number(value: f64) -> String {
    if value.is_finite() { format!("{:.17e}", value) } else { "null".into() }
}

fn main() {
    let args: Vec<String> = env::args().skip(1).collect();
    if args.len() != 5 {
        eprintln!("usage: d_optimal_probe n_samples ridge matrix_rows weights scales");
        std::process::exit(2);
    }
    let n_samples = args[0].parse::<usize>().unwrap_or_else(|_| {
        eprintln!("n_samples must be an integer");
        std::process::exit(2);
    });
    let ridge = args[1].parse::<f64>().unwrap_or_else(|_| {
        eprintln!("ridge must be numeric");
        std::process::exit(2);
    });
    let matrix: Vec<Vec<f64>> = args[2].split(';')
        .map(|row| parse_vector(row).unwrap_or_else(|error| {
            eprintln!("{error}");
            std::process::exit(2);
        }))
        .collect();
    let weights = if args[3] == "-" { None } else {
        Some(parse_vector(&args[3]).unwrap_or_else(|error| {
            eprintln!("{error}");
            std::process::exit(2);
        }))
    };
    let scales = if args[4] == "-" { None } else {
        Some(parse_vector(&args[4]).unwrap_or_else(|error| {
            eprintln!("{error}");
            std::process::exit(2);
        }))
    };

    let report = d_optimal_design(
        &matrix, n_samples, weights.as_deref(), None, scales.as_deref(), 1e-12, ridge,
    ).unwrap_or_else(|error| {
        eprintln!("{error}");
        std::process::exit(1);
    });
    let indices = report.selected_indices.iter().map(usize::to_string).collect::<Vec<_>>().join(",");
    let information = report.normalized_information_matrix.iter().map(|row| {
        format!("[{}]", row.iter().map(|value| json_number(*value)).collect::<Vec<_>>().join(","))
    }).collect::<Vec<_>>().join(",");
    println!(
        "{{\"selected_indices\":[{}],\"log_determinant\":{},\"jacobian_scale\":{},\"local_rank\":{},\"fim_condition_number\":{},\"normalized_information_matrix\":[{}]}}",
        indices,
        json_number(report.log_determinant),
        json_number(report.jacobian_scale),
        report.local_information.local_rank,
        json_number(report.local_information.fim_condition_number),
        information,
    );
}
