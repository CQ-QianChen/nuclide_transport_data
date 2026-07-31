import pandas as pd
from nuctransportdb import merge_method as mm


def base_row(**overrides):
    # Build one row with all merge-relevant columns defaulted to None.
    row = {
        "nuclide": "I",
        "nuclide_property": "sorption_coefficient",
        "rock_type": "Sandstone",
        "source": "measured",
        "type": "scalar",
        "value": None,
        "value_min": None,
        "value_max": None,
        "value_std": None,
        "sample_size": None,
        "sampled_data": None,
        "unit_str": None,
        "unit_base": None,
        "variable_name": None,
        "variable_unit_str": None,
        "variable_unit_base": None,
        "description": None,
        "agency": None,
        "location": None,
        "simplified_lithology": None,
        "ID": "5133cfd0-3684-5785-ad1c-47383cca3521",
    }
    row.update(overrides)
    return row


class TestMasks:
    # test Mask helper functions
    def test_value_empty_mask(self):
        df = pd.DataFrame([base_row(), base_row(value=1.0, ID="95fa1828-6701-5022-970e-b30b43ba898c")])
        mask = mm.value_empty_mask(df)
        assert list(mask) == [True, False]

    def test_value_invalid_mask_min_greater_than_max(self):
        df = pd.DataFrame([base_row(value=5.0, value_min=10.0, value_max=1.0)])
        assert mm.value_invalid_mask(df).iloc[0]

    def test_value_invalid_mask_only_std_given(self):
        df = pd.DataFrame([base_row(value_std=0.1)])
        assert mm.value_invalid_mask(df).iloc[0]

    def test_value_uniform_mask(self):
        df = pd.DataFrame([base_row(value_min=1.0, value_max=2.0)])
        assert mm.value_uniform_mask(df).iloc[0]

    def test_value_truncnorm_mask(self):
        df = pd.DataFrame(
            [base_row(value=1.5, value_min=1.0, value_max=2.0, value_std=0.2)],
        )
        assert mm.value_truncnorm_mask(df).iloc[0]

    def test_value_pdf_mask(self):
        df = pd.DataFrame([base_row(sampled_data="np.array([1,2,3])")])
        assert mm.value_pdf_mask(df).iloc[0]

class TestMergePropertyValue:
    def test_single_row_with_pdf_is_passed_through(self):
        df = pd.DataFrame(
            [base_row(nuclide_property="sorption_coefficient",
                       sampled_data="np.array([1.0, 2.0, 3.0])")],
        )
        result = mm.merge_property_value(df, source_type="merged")
        assert len(result) == 1
        assert result.iloc[0]["nuclide"] == "I"

    def test_multiple_rows_are_merged_into_one(self):
        df = pd.DataFrame(
            [
                base_row(value=1.0, value_min=0.5, value_max=1.5, value_std=0.1, ID="5133cfd0-3684-5785-ad1c-47383cca3521"),
                base_row(value=1.2, value_min=0.6, value_max=1.8, value_std=0.15, ID="95fa1828-6701-5022-970e-b30b43ba898c"),
            ],
        )
        result = mm.merge_property_value(df, sample_size=1000, source_type="merged")
        assert len(result) == 1
        assert result.iloc[0]["source"] == "merged"
        assert result.iloc[0]["value"] is not None

    def test_identical_values_produce_zero_std(self):
        df = pd.DataFrame(
            [
                base_row(value=0.0, value_std=0.0, ID="5133cfd0-3684-5785-ad1c-47383cca3521"),
                base_row(value=0.0, value_std=0.0, ID="95fa1828-6701-5022-970e-b30b43ba898c"),
            ],
        )
        result = mm.merge_property_value(df, sample_size=1000, source_type="merged")
        assert result.iloc[0]["value_std"] == 0.0
        assert result.iloc[0]["value_min"] is None
        assert result.iloc[0]["value_max"] is None


    def test_custom_sampling_function_is_used(self):
        df = pd.DataFrame(
            [
                base_row(value=1.0, value_min=0.5, value_max=1.5, value_std=0.1, ID="5133cfd0-3684-5785-ad1c-47383cca3521"),
                base_row(value=1.2, value_min=0.6, value_max=1.8, value_std=0.15, ID="95fa1828-6701-5022-970e-b30b43ba898c"),
            ],
        )
        result = mm.merge_property_value(
            df,
            sample_size=1000,
            source_type="merged",
            sampling_functions_by_property={"I": mm.generate_uniform},
        )
        assert "scipy.stats.uniform" in result.iloc[0]["sampled_data"]

    def test_nonscalar_rows_kept_for_merged_source(self):
        df = pd.DataFrame(
            [
                base_row(type="expression", value="x+1", ID="5133cfd0-3684-5785-ad1c-47383cca3521"),
                base_row(sampled_data="np.array([1.0, 2.0])", ID="95fa1828-6701-5022-970e-b30b43ba898c"),
            ],
        )
        result = mm.merge_property_value(df, source_type="merged")
        assert "expression" in list(result["type"])

    def test_nonscalar_rows_dropped_for_default_source(self):
        df = pd.DataFrame(
            [
                base_row(type="expression", value="x+1", ID="5133cfd0-3684-5785-ad1c-47383cca3521"),
                base_row(sampled_data="np.array([1.0, 2.0])", ID="95fa1828-6701-5022-970e-b30b43ba898c"),
            ],
        )
        result = mm.merge_property_value(df, source_type="default")
        assert "expression" not in list(result["type"])

    def test_empty_columns_dropped_except_required(self):
        df = pd.DataFrame(
            [base_row(sampled_data="np.array([1.0, 2.0, 3.0])", ID="5133cfd0-3684-5785-ad1c-47383cca3521")],
        )
        result = mm.merge_property_value(df, source_type="merged")
        assert "agency" not in result.columns
        assert "value" in result.columns
