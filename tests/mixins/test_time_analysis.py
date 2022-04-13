from typing import Tuple
from numbers import Number

from _utils import TestSolverOutput
import pandas as pd
import pytest

import numpy as np

from anndata import AnnData

from moscot.problems.time._lineage import TemporalProblem


class TestTemporalAnalysisMixin:
    @pytest.mark.parametrize("forward", [True, False])
    def test_cell_transition_full_pipeline(self, gt_temporal_adata: AnnData, forward: bool):
        cell_types = set(np.unique(gt_temporal_adata.obs["cell_type"]))
        problem = TemporalProblem(gt_temporal_adata)
        problem = problem.prepare("day", subset=[(10, 10.5), (10.5, 11), (10, 11)], policy="explicit")
        assert set(problem.problems.keys()) == {(10, 10.5), (10, 11), (10.5, 11)}
        problem[10, 10.5]._solution = TestSolverOutput(gt_temporal_adata.uns["tmap_10_105"])
        problem[10.5, 11]._solution = TestSolverOutput(gt_temporal_adata.uns["tmap_105_11"])
        problem[10, 11]._solution = TestSolverOutput(gt_temporal_adata.uns["tmap_10_11"])

        result = problem.cell_transition(10, 10.5, "cell_type", "cell_type", forward=forward)

        assert isinstance(result, pd.DataFrame)
        assert result.shape == (len(cell_types), len(cell_types))
        assert set(result.index) == set(cell_types)
        assert set(result.columns) == set(cell_types)
        marginal = result.sum(axis=forward == 1).values
        present_cell_type_marginal = marginal[marginal > 0]
        np.testing.assert_almost_equal(present_cell_type_marginal, np.ones(len(present_cell_type_marginal)), decimal=5)

    @pytest.mark.parametrize("forward", [True, False])
    def test_cell_transition_subset_pipeline(self, gt_temporal_adata: AnnData, forward: bool):
        problem = TemporalProblem(gt_temporal_adata)
        problem = problem.prepare("day", subset=[(10, 10.5), (10.5, 11), (10, 11)], policy="explicit")
        assert set(problem.problems.keys()) == {(10, 10.5), (10, 11), (10.5, 11)}
        problem[10, 10.5]._solution = TestSolverOutput(gt_temporal_adata.uns["tmap_10_105"])
        problem[10.5, 11]._solution = TestSolverOutput(gt_temporal_adata.uns["tmap_105_11"])
        problem[10, 11]._solution = TestSolverOutput(gt_temporal_adata.uns["tmap_10_11"])

        early_cells = ["Stromal", "unknown"]
        late_cells = ["Stromal", "Epithelial"]
        result = problem.cell_transition(
            10, 10.5, {"cell_type": early_cells}, {"cell_type": late_cells}, forward=forward
        )
        assert isinstance(result, pd.DataFrame)
        assert result.shape == (2, 2)
        assert set(result.index) == set(early_cells)
        assert set(result.columns) == set(late_cells)
        marginal = result.sum(axis=forward == 1).values
        present_cell_type_marginal = marginal[marginal > 0]
        np.testing.assert_almost_equal(present_cell_type_marginal, np.ones(len(present_cell_type_marginal)), decimal=5)

    @pytest.mark.parametrize("forward", [True, False])
    def test_cell_transition_regression(self, gt_temporal_adata: AnnData, forward: bool):
        problem = TemporalProblem(gt_temporal_adata)
        problem = problem.prepare("day", subset=[(10, 10.5), (10.5, 11), (10, 11)], policy="explicit")
        assert set(problem.problems.keys()) == {(10, 10.5), (10, 11), (10.5, 11)}
        problem[10, 10.5]._solution = TestSolverOutput(gt_temporal_adata.uns["tmap_10_105"])
        problem[10.5, 11]._solution = TestSolverOutput(gt_temporal_adata.uns["tmap_105_11"])
        problem[10, 11]._solution = TestSolverOutput(gt_temporal_adata.uns["tmap_10_11"])

        result = problem.cell_transition(10, 10.5, early_cells="cell_type", late_cells="cell_type", forward=forward)
        assert result.shape == (6, 6)
        marginal = result.sum(axis=forward == 1).values
        present_cell_type_marginal = marginal[marginal > 0]
        np.testing.assert_almost_equal(present_cell_type_marginal, np.ones(len(present_cell_type_marginal)), decimal=5)

        direction = "forward" if forward else "backward"
        gt = gt_temporal_adata.uns[f"cell_transition_10_105_{direction}"]
        np.testing.assert_almost_equal(result.values, gt.values, decimal=4)

    def test_compute_time_point_distances_pipeline(self, adata_time: AnnData):
        problem = TemporalProblem(adata_time)
        problem.prepare("time")
        distance_source_intermediate, distance_intermediate_target = problem.compute_time_point_distances(
            start=0, intermediate=1, end=2
        )
        assert isinstance(distance_source_intermediate, float)
        assert isinstance(distance_intermediate_target, float)
        assert distance_source_intermediate > 0
        assert distance_intermediate_target > 0

    def test_batch_distances_pipeline(self, adata_time: AnnData):
        problem = TemporalProblem(adata_time)
        problem.prepare("time")

        batch_distance = problem.compute_batch_distances(time=1, batch_key="batch")
        assert isinstance(batch_distance, float)
        assert batch_distance > 0

    def test_compute_interpolated_distance_regression(self, gt_temporal_adata: AnnData):
        problem = TemporalProblem(gt_temporal_adata)
        problem = problem.prepare("day", subset=[(10, 10.5), (10.5, 11), (10, 11)], policy="explicit")
        assert set(problem.problems.keys()) == {(10, 10.5), (10, 11), (10.5, 11)}
        problem[10, 10.5]._solution = TestSolverOutput(gt_temporal_adata.uns["tmap_10_105"])
        problem[10.5, 11]._solution = TestSolverOutput(gt_temporal_adata.uns["tmap_105_11"])
        problem[10, 11]._solution = TestSolverOutput(gt_temporal_adata.uns["tmap_10_11"])

        interpolation_result = problem.compute_interpolated_distance(10, 10.5, 11, seed=42)
        isinstance(interpolation_result, float)
        assert interpolation_result > 0
        np.testing.assert_almost_equal(interpolation_result, 20.629795, decimal=4)  # pre-computed

    def test_compute_time_point_distances_regression(self, gt_temporal_adata: AnnData):
        problem = TemporalProblem(gt_temporal_adata)
        problem = problem.prepare("day", subset=[(10, 10.5), (10.5, 11), (10, 11)], policy="explicit")
        assert set(problem.problems.keys()) == {(10, 10.5), (10, 11), (10.5, 11)}

        result = problem.compute_time_point_distances(10, 10.5, 11)
        assert isinstance(result, tuple)
        assert result[0] > 0 and result[1] > 0
        np.testing.assert_almost_equal(result[0], 23.9996, decimal=4)  # pre-computed
        np.testing.assert_almost_equal(result[1], 22.7514, decimal=4)  # pre-computed

    def test_compute_batch_distances_regression(self, gt_temporal_adata: AnnData):
        problem = TemporalProblem(gt_temporal_adata)
        problem = problem.prepare("day", subset=[(10, 10.5), (10.5, 11), (10, 11)], policy="explicit")
        assert set(problem.problems.keys()) == {(10, 10.5), (10, 11), (10.5, 11)}

        result = problem.compute_batch_distances(10, "batch")
        assert isinstance(result, float)
        np.testing.assert_almost_equal(result, 22.9107, decimal=4)  # pre-computed

    def test_compute_random_distance_regression(self, gt_temporal_adata: AnnData):
        problem = TemporalProblem(gt_temporal_adata)
        problem = problem.prepare("day", subset=[(10, 10.5), (10.5, 11), (10, 11)], policy="explicit")
        assert set(problem.problems.keys()) == {(10, 10.5), (10, 11), (10.5, 11)}

        result = problem.compute_random_distance(10, 10.5, 11, seed=42)
        assert isinstance(result, float)
        np.testing.assert_almost_equal(result, 21.1825, decimal=4)  # pre-computed

    @pytest.mark.parametrize("only_start", [True, False])
    def test_get_data_pipeline(self, adata_time: AnnData, only_start: bool):
        problem = TemporalProblem(adata_time)
        problem.prepare("time")

        result = problem._get_data(0, only_start=only_start) if only_start else problem._get_data(0, 1, 2)

        assert isinstance(result, Tuple)
        assert len(result) == 2 if only_start else len(result) == 5
        if only_start:
            assert isinstance(result[0], np.ndarray)
            assert isinstance(result[1], AnnData)
        else:
            assert isinstance(result[0], np.ndarray)
            assert isinstance(result[1], np.ndarray)
            assert isinstance(result[2], np.ndarray)
            assert isinstance(result[3], AnnData)
            assert isinstance(result[4], np.ndarray)

    @pytest.mark.parametrize("time_points", [(0, 1, 2), (0, 2, 1), ()])
    def test_get_interp_param_pipeline(self, adata_time: AnnData, time_points: Tuple[Number]):
        start, intermediate, end = time_points if len(time_points) else (42, 43, 44)
        interpolation_parameter = None if len(time_points) == 3 else 0.5
        problem = TemporalProblem(adata_time)
        problem.prepare("time")
        problem.solve()

        if intermediate <= start or end <= intermediate:
            with np.testing.assert_raises(ValueError):
                problem._get_interp_param(interpolation_parameter, start, intermediate, end)
        else:
            inter_param = problem._get_interp_param(interpolation_parameter, start, intermediate, end)
            assert inter_param == 0.5
