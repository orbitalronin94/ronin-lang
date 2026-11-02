use ronin_core::diagnose_hill_design;
use std::env;

fn json_number(value: f64) -> String {
    if value.is_finite() {
        format!("{:.17e}", value)
    } else {
        "null".into()
    }
}

fn main() {
    let args: Vec<String> = env::args().skip(1).collect();
    if args.len() < 6 {
        eprintln!("usage: hill_design_probe K alpha_h sigma relative_tolerance saturation_ratio omega...");
        std::process::exit(2);
    }
    let parse = |index: usize| -> f64 {
        args[index].parse::<f64>().unwrap_or_else(|_| {
            eprintln!("invalid numeric argument: {}", args[index]);
            std::process::exit(2);
        })
    };
    let k = parse(0);
    let alpha_h = parse(1);
    let sigma = parse(2);
    let tolerance = parse(3);
    let saturation_ratio = parse(4);
    let omega: Vec<f64> = args[5..]
        .iter()
        .map(|value| value.parse::<f64>().unwrap_or(f64::NAN))
        .collect();

    let report = diagnose_hill_design(
        &omega, k, alpha_h, sigma, tolerance, saturation_ratio,
    )
    .unwrap_or_else(|error| {
        eprintln!("{error}");
        std::process::exit(1);
    });

    println!(
        "{{\"observations\":{},\"omega_range_orders\":{},\"saturation_fraction\":{},\"max_omega_over_k\":{},\"singular_values\":[{},{}],\"fim_condition_number\":{},\"local_rank\":{},\"weak_direction\":[{},{}]}}",
        report.observations,
        json_number(report.omega_range_orders),
        json_number(report.saturation_fraction),
        json_number(report.max_omega_over_k),
        json_number(report.singular_values[0]),
        json_number(report.singular_values[1]),
        json_number(report.fim_condition_number),
        report.local_rank,
        json_number(report.weak_direction[0]),
        json_number(report.weak_direction[1]),
    );
}
