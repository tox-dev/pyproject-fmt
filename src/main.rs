use std::io::{Read, Write};
use std::string::String;

use clap::Parser;
use clio::{Input, OutputPath};

use crate::format::format_toml;

mod format;
mod table_ordering;

#[derive(Parser)]
#[clap(version, long_about = None)]
/// Format your pyproject.toml files
struct Cli {
    /// TOML file to format, '-' for stdout
    #[clap(value_parser, default_value = "-")]
    source: Input,

    /// Output file, '-' for stdout
    #[clap(long, short, value_parser, default_value = "-")]
    destination: OutputPath,

    /// number of spaces to indent by
    #[arg(short, long, default_value_t = 2)]
    indent: usize,

    /// number of spaces to indent by
    #[arg(short, long, default_value_t = 120)]
    width: usize,
}

fn main() {
    let mut cli = Cli::parse();

    let mut content = String::new();
    cli.source.read_to_string(&mut content).unwrap();

    let result = format_toml(content, cli.width, cli.indent);

    let mut output = cli.destination.create_with_len(result.len() as u64).unwrap();
    output.write_all(result.as_ref()).unwrap();
}
