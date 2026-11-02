use ronin_core::sobol_first_order;
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
    if args.len() != 3 {
        eprintln!("usage: sobol_probe f_a f_b f_ab_rows");
        std::process::exit(2);
    }
    let f_a = parse_vector(&args[0]).unwrap_or_else(|error| {
        eprintln!("{error}");
        std::process::exit(2);
    });
    let f_b = parse_vector(&args[1]).unwrap_or_else(|error| {
        eprintln!("{error}");
        std::process::exit(2);
    });
    let f_ab: Vec<Vec<f64>> = args[2].split(';')
        .map(|row| parse_vector(row).unwrap_or_else(|error| {
            eprintln!("{error}");
            std::process::exit(2);
        }))
        .collect();
    let report = sobol_first_order(&f_a, &f_b, &f_ab).unwrap_or_else(|error| {
        eprintln!("{error}");
        std::process::exit(1);
    });
    println!(
        "{{\"sample_count\":{},\"parameter_count\":{},\"first_order_indices\":[{}],\"output_scale\":{},\"output_variance_normalized\":{}}}",
        report.sample_count,
        report.parameter_count,
        report.first_order_indices.iter().map(|value| json_number(*value)).collect::<Vec<_>>().join(","),
        json_number(report.output_scale),
        json_number(report.output_variance_normalized),
    );
}
