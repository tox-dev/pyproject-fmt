use std::io::{Read, Write};
use std::string::String;

use clap::Parser;
use clio::{Input, OutputPath};
use taplo::formatter::{format_syntax, Options};
use taplo::parser::parse;
use taplo::syntax::SyntaxNode;

use crate::table_ordering::reorder_table;

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

    let mut root_ast = parse(&content).into_syntax().clone_for_update();
    reorder_table(&mut root_ast);

    let result = format(&mut cli, root_ast);

    let mut output = cli.destination.create_with_len(result.len() as u64).unwrap();
    output.write_all(result.as_ref()).unwrap();
}

fn format(cli: &mut Cli, ast: SyntaxNode) -> String {
    let options = Options {
        align_entries: false,         // do not align by =
        align_comments: true,         // align inline comments
        align_single_comments: true,  // align comments after entries
        array_trailing_comma: true,   // ensure arrays finish with trailing comma
        array_auto_expand: true,      // arrays go to multi line for easier diffs
        array_auto_collapse: false,   // do not collapse for easier diffs
        compact_arrays: false,        // do not compact for easier diffs
        compact_inline_tables: false, // do not compact for easier diffs
        compact_entries: false,       // do not compact for easier diffs
        column_width: cli.width,
        indent_tables: false,
        indent_entries: false,
        inline_table_expand: true,
        trailing_newline: true,
        allowed_blank_lines: 1, // one blank line to separate
        indent_string: " ".repeat(cli.indent),
        reorder_keys: false,  // respect custom order
        reorder_arrays: true, // stable order in arrays
        crlf: false,
    };
    format_syntax(ast, options)
}
