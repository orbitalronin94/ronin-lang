use crate::ast::{Agent, Params, System};

#[derive(Clone, Debug, PartialEq)]
struct Token {
    value: String,
    line: usize,
    column: usize,
}

fn lex(source: &str) -> Result<Vec<Token>, String> {
    let chars: Vec<char> = source.chars().collect();
    let mut tokens = Vec::new();
    let (mut i, mut line, mut column) = (0, 1, 1);

    while i < chars.len() {
        let ch = chars[i];
        if ch.is_whitespace() {
            if ch == '\n' {
                line += 1;
                column = 1;
            } else {
                column += 1;
            }
            i += 1;
            continue;
        }
        if ch == '/' && chars.get(i + 1) == Some(&'/') {
            while i < chars.len() && chars[i] != '\n' {
                i += 1;
                column += 1;
            }
            continue;
        }

        let start_line = line;
        let start_column = column;
        let start = i;

        if ch.is_ascii_alphabetic() || ch == '_' {
            i += 1;
            while i < chars.len()
                && (chars[i].is_ascii_alphanumeric() || chars[i] == '_')
            {
                i += 1;
            }
        } else if ch.is_ascii_digit()
            || (ch == '.' && chars.get(i + 1).map_or(false, |c| c.is_ascii_digit()))
            || ((ch == '+' || ch == '-')
                && chars.get(i + 1).map_or(false, |c| c.is_ascii_digit() || *c == '.'))
        {
            i += 1;
            while i < chars.len()
                && (chars[i].is_ascii_digit() || chars[i] == '.' || chars[i] == 'e'
                    || chars[i] == 'E' || chars[i] == '+' || chars[i] == '-')
            {
                i += 1;
            }
        } else if ch == '"' {
            i += 1;
            let mut escaped = false;
            while i < chars.len() {
                let current = chars[i];
                i += 1;
                if escaped {
                    escaped = false;
                } else if current == '\\' {
                    escaped = true;
                } else if current == '"' {
                    break;
                }
            }
            if chars.get(i.saturating_sub(1)) != Some(&'"') {
                return Err(format!("Unterminated string at {}:{}", start_line, start_column));
            }
        } else if "{}[](),:=".contains(ch) || ch == '∞' {
            i += 1;
        } else {
            return Err(format!("Unexpected character {:?} at {}:{}", ch, line, column));
        }

        let value: String = chars[start..i].iter().collect();
        column += i - start;
        tokens.push(Token { value, line: start_line, column: start_column });
    }
    tokens.push(Token { value: String::new(), line, column });
    Ok(tokens)
}

struct Parser {
    tokens: Vec<Token>,
    index: usize,
}

impl Parser {
    fn current(&self) -> &Token {
        &self.tokens[self.index]
    }

    fn take(&mut self) -> Token {
        let token = self.current().clone();
        self.index += 1;
        token
    }

    fn expect(&mut self, expected: &str) -> Result<(), String> {
        let token = self.take();
        if token.value != expected {
            return Err(format!(
                "Expected {:?} at {}:{}, got {:?}",
                expected, token.line, token.column, token.value
            ));
        }
        Ok(())
    }

    fn identifier(&mut self) -> Result<String, String> {
        let token = self.take();
        let valid = token.value.chars().next().map_or(false, |c| c.is_ascii_alphabetic() || c == '_')
            && token.value.chars().all(|c| c.is_ascii_alphanumeric() || c == '_');
        if !valid {
            return Err(format!("Expected identifier at {}:{}", token.line, token.column));
        }
        Ok(token.value)
    }

    fn number(&mut self) -> Result<f64, String> {
        let token = self.take();
        match token.value.to_lowercase().as_str() {
            "inf" | "infinity" | "∞" => Ok(f64::INFINITY),
            _ => token.value.parse::<f64>().map_err(|_| {
                format!("Expected number at {}:{}", token.line, token.column)
            }),
        }
    }

    fn scalar(&mut self) -> Result<String, String> {
        let token = self.take();
        if token.value.starts_with('"') && token.value.ends_with('"') {
            Ok(token.value[1..token.value.len() - 1].to_string())
        } else {
            Ok(token.value)
        }
    }

    fn optional_comma(&mut self) {
        if self.current().value == "," {
            self.take();
        }
    }

    fn agent(&mut self) -> Result<Agent, String> {
        self.expect("{")?;
        let mut fields = std::collections::HashMap::new();
        while self.current().value != "}" {
            if self.current().value.is_empty() {
                return Err("Unterminated agent block".into());
            }
            let key = self.identifier()?;
            self.expect(":")?;
            let value = self.number()?;
            if fields.insert(key.clone(), value).is_some() {
                return Err(format!("Duplicate agent field: {}", key));
            }
            self.optional_comma();
        }
        self.expect("}")?;
        let phi = fields.remove("phi").ok_or("Missing agent field: phi")?;
        let psi = fields.remove("psi").ok_or("Missing agent field: psi")?;
        let frequency = fields.remove("frequency").ok_or("Missing agent field: frequency")?;
        if !fields.is_empty() {
            return Err(format!("Unknown agent field: {}", fields.keys().next().unwrap()));
        }
        Ok(Agent { phi, psi, frequency })
    }

    fn agents(&mut self) -> Result<Vec<Agent>, String> {
        self.expect("[")?;
        let mut agents = Vec::new();
        while self.current().value != "]" {
            if self.current().value.is_empty() {
                return Err("Unterminated agents list".into());
            }
            agents.push(self.agent()?);
            self.optional_comma();
        }
        self.expect("]")?;
        self.optional_comma();
        Ok(agents)
    }

    fn params(&mut self) -> Result<Params, String> {
        self.expect("{")?;
        let mut params = Params {
            alpha: 1.0, gamma: 0.4, sigma: 0.0, model: "pusfre".into(),
            lambda: 0.0, k: f64::INFINITY, alpha_h: 1.0,
            memory_order: 1, coexistence_delta: 0.05,
        };
        let mut seen = std::collections::HashSet::new();
        while self.current().value != "}" {
            if self.current().value.is_empty() {
                return Err("Unterminated params block".into());
            }
            let key = self.identifier()?;
            self.expect(":")?;
            if !seen.insert(key.clone()) {
                return Err(format!("Duplicate params field: {}", key));
            }
            match key.as_str() {
                "model" => params.model = self.scalar()?,
                "alpha" => params.alpha = self.number()?,
                "gamma" => params.gamma = self.number()?,
                "sigma" => params.sigma = self.number()?,
                "coexistence_delta" => params.coexistence_delta = self.number()?,
                "lambda" => params.lambda = self.number()?,
                "K" | "k" => params.k = self.number()?,
                "alpha_h" => params.alpha_h = self.number()?,
                "memory_order" => {
                    let value = self.number()?;
                    if !value.is_finite() || value < 0.0 || value.fract() != 0.0 {
                        return Err("memory_order must be a non-negative integer".into());
                    }
                    params.memory_order = value as usize;
                }
                _ => return Err(format!("Unknown params field: {}", key)),
            }
            self.optional_comma();
        }
        self.expect("}")?;
        self.optional_comma();
        Ok(params)
    }

    fn system(&mut self) -> Result<System, String> {
        self.expect("system")?;
        let name = self.identifier()?;
        self.expect("=")?;
        self.expect("{")?;
        let mut parts = None;
        let mut resource = None;
        let mut agents = None;
        let mut params = Params {
            alpha: 1.0, gamma: 0.4, sigma: 0.0, model: "pusfre".into(),
            lambda: 0.0, k: f64::INFINITY, alpha_h: 1.0,
            memory_order: 1, coexistence_delta: 0.05,
        };
        let mut seen = std::collections::HashSet::new();
        while self.current().value != "}" {
            if self.current().value.is_empty() {
                return Err(format!("Unterminated system {}", name));
            }
            let key = self.identifier()?;
            self.expect(":")?;
            if !seen.insert(key.clone()) {
                return Err(format!("Duplicate system {} field: {}", name, key));
            }
            match key.as_str() {
                "parts" => {
                    let value = self.number()?;
                    if !value.is_finite() || value <= 0.0 || value.fract() != 0.0 {
                        return Err("parts must be a positive integer".into());
                    }
                    parts = Some(value as usize);
                }
                "resource" => resource = Some(self.number()?),
                "agents" => agents = Some(self.agents()?),
                "params" => params = self.params()?,
                _ => return Err(format!("Unknown system field: {}", key)),
            }
            self.optional_comma();
        }
        self.expect("}")?;
        Ok(System {
            name,
            parts: parts.ok_or("Missing system field: parts")?,
            resource: resource.ok_or("Missing system field: resource")?,
            agents: agents.ok_or("Missing system field: agents")?,
            params,
        })
    }
}

pub fn parse(source: &str) -> Result<Vec<System>, String> {
    let tokens = lex(source)?;
    let mut parser = Parser { tokens, index: 0 };
    let mut systems = Vec::new();
    let mut names = std::collections::HashSet::new();
    while !parser.current().value.is_empty() {
        let system = parser.system()?;
        if !names.insert(system.name.clone()) {
            return Err(format!("Duplicate system {}", system.name));
        }
        systems.push(system);
    }
    Ok(systems)
}

#[cfg(test)]
mod tests {
    use super::parse;

    #[test]
    fn parses_maquinas_fixture() {
        let systems = parse(include_str!("../../examples/maquinas.ronin")).unwrap();
        assert_eq!(systems.len(), 1);
        assert_eq!(systems[0].name, "Maquinas");
        assert_eq!(systems[0].parts, 2);
        assert_eq!(systems[0].agents.len(), 2);
        assert_eq!(systems[0].params.model, "pusfre");
    }

    #[test]
    fn parses_extended_params_and_comments() {
        let source = r#"
            // parser supports comments
            system Coastal = {
              parts: 2, resource: 10,
              agents: [
                { phi: 0.6, psi: 0.7, frequency: 0.5 },
                { phi: 0.5, psi: 0.8, frequency: 0.5 }
              ],
              params: { model: "ces", lambda: -0.25, K: inf, memory_order: 2 }
            }
        "#;
        let parsed = parse(source).unwrap();
        assert_eq!(parsed[0].params.model, "ces");
        assert_eq!(parsed[0].params.lambda, -0.25);
        assert!(parsed[0].params.k.is_infinite());
        assert_eq!(parsed[0].params.memory_order, 2);
    }

    #[test]
    fn rejects_duplicate_and_unknown_fields() {
        let duplicate = "system S = { parts: 2, parts: 3, resource: 1, agents: [{phi: 1, psi: 1, frequency: 1}] }";
        assert!(parse(duplicate).unwrap_err().contains("Duplicate system S field: parts"));
        let unknown = "system S = { parts: 2, resource: 1, agents: [{phi: 1, psi: 1, frequency: 1}], params: { typo: 1 } }";
        assert!(parse(unknown).unwrap_err().contains("Unknown params field: typo"));
    }
}
