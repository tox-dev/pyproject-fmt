use std::string::String;

use taplo::formatter::{format_syntax, Options};
use taplo::parser::parse;

use crate::table_ordering::reorder_table;

pub fn format_toml(content: String, width: usize, indent: usize) -> String {
    let mut root_ast = parse(&content).into_syntax().clone_for_update();
    reorder_table(&mut root_ast);
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
        column_width: width,
        indent_tables: false,
        indent_entries: false,
        inline_table_expand: true,
        trailing_newline: true,
        allowed_blank_lines: 1, // one blank line to separate
        indent_string: " ".repeat(indent),
        reorder_keys: false,  // respect custom order
        reorder_arrays: true, // stable order in arrays
        crlf: false,
    };
    format_syntax(root_ast, options)
}
