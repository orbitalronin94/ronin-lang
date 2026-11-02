use ronin_core::diagnose_sir_early_phase;
use std::env;

fn json_number(value: f64) -> String {
    if value.is_finite() { format!("{:.17e}", value) } else { "null".into() }
}

fn main() {
    let args: Vec<String> = env::args().skip(1).collect();
    if args.len() < 7 {
        eprintln!("usage: sir_design_probe beta gamma rho I0 sigma time...");
        std::process::exit(2);
    }
    let parse = |index: usize| -> f64 {
        args[index].parse::<f64>().unwrap_or_else(|_| {
            eprintln!("invalid numeric argument: {}", args[index]);
            std::process::exit(2);
        })
    };
    let beta = parse(0);
    let gamma = parse(1);
    let rho = parse(2);
    let i0 = parse(3);
    let sigma = parse(4);
    let times: Vec<f64> = args[5..]
        .iter()
        .map(|value| value.parse::<f64>().unwrap_or(f64::NAN))
        .collect();
    let report = diagnose_sir_early_phase(&times, beta, gamma, rho, i0, sigma)
        .unwrap_or_else(|error| {
            eprintln!("{error}");
            std::process::exit(1);
        });
    let info = report.local_information;
    println!(
        "{{\"growth_rate\":{},\"observed_amplitude\":{},\"local_rank\":{},\"singular_values\":[{}],\"fim_condition_number\":{}}}",
        json_number(report.growth_rate),
        json_number(report.observed_amplitude),
        info.local_rank,
        info.singular_values.iter().map(|value| json_number(*value)).collect::<Vec<_>>().join(","),
        json_number(info.fim_condition_number),
    );
}
