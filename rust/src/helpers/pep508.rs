use pyo3::prelude::*;
use pyo3::prepare_freethreaded_python;
use pyo3::types::IntoPyDict;

pub fn normalize_req_str(value: &str, keep_full_version: bool) -> String {
    prepare_freethreaded_python();
    Python::with_gil(|py| {
        let norm: String = PyModule::import_bound(py, "pyproject_fmt._pep508")?
            .getattr("normalize_req")?
            .call(
                (value,),
                Some(&[("keep_full_version", keep_full_version)].into_py_dict_bound(py)),
            )?
            .extract()?;
        Ok::<String, PyErr>(norm)
    })
    .unwrap()
}
