use ronin_core::d_optimal_hill_design;
use std::env;

fn json_number(value: f64) -> String {
    if value.is_finite() { format!("{:.17e}", value) } else { "null".into() }
}

fn main() {
    let args: Vec<String> = env::args().skip(1).collect();
    if args.len() != 6 {
        eprintln!("usage: hill_d_optimal_probe n_samples K alpha_h sigma ridge omega_csv");
        std::process::exit(2);
    }
    let n_samples = args[0].parse::<usize>().unwrap_or_else(|_| {
        eprintln!("n_samples must be an integer");
        std::process::exit(2);
    });
    let parse = |index: usize, name: &str| args[index].parse::<f64>().unwrap_or_else(|_| {
        eprintln!("{name} must be numeric");
        std::process::exit(2);
    });
    let k = parse(1, "K");
    let alpha_h = parse(2, "alpha_h");
    let sigma = parse(3, "sigma");
    let ridge = parse(4, "ridge");
    let omega: Vec<f64> = args[5].split(',').map(|part| {
        part.parse::<f64>().unwrap_or_else(|_| {
            eprintln!("invalid omega value: {part}");
            std::process::exit(2);
        })
    }).collect();
    let report = d_optimal_hill_design(
        &omega, n_samples, k, alpha_h, sigma, 1e-12, ridge,
    ).unwrap_or_else(|error| {
        eprintln!("{error}");
        std::process::exit(1);
    });
    let indices = report.selected_indices.iter().map(usize::to_string).collect::<Vec<_>>().join(",");
    let selected_omega = report.selected_omega.iter().map(|value| json_number(*value)).collect::<Vec<_>>().join(",");
    println!(
        "{{\"selected_indices\":[{}],\"selected_omega\":[{}],\"log_determinant\":{},\"local_rank\":{},\"condition\":{},\"warnings\":{}}}",
        indices,
        selected_omega,
        json_number(report.design.log_determinant),
        report.design.local_information.local_rank,
        json_number(report.design.local_information.fim_condition_number),
        report.warnings.len(),
    );
}
