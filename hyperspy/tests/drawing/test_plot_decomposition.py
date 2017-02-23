# -*- coding: utf-8 -*-
# Copyright 2007-2015 The HyperSpy developers
#
# This file is part of  HyperSpy.
#
#  HyperSpy is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
#  HyperSpy is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with  HyperSpy.  If not, see <http://www.gnu.org/licenses/>.

import numpy as np
import pytest

from hyperspy import signals


baseline_dir = 'plot_explained_variance_ratio'
default_tol = 2.0


@pytest.mark.skipif("sys.platform == 'darwin'")
class TestPlotExplainedVarianceRatio:

    def setup_method(self, method):
        np.random.seed(1)
        sources = np.random.random(size=(5, 100))
        np.random.seed(1)
        mixmat = np.random.random((100, 5))
        self.s = signals.Signal1D(np.dot(mixmat, sources))
        np.random.seed(1)
        self.s.add_gaussian_noise(.1)
        self.s.decomposition()

    def _generate_parameters():
        parameters = []
        for n in [10, 50]:
            for xaxis_type in ['index', 'number']:
                for threshold in [0, 0.001]:
                    for xaxis_labeling in ['ordinal', 'cardinal']:
                        parameters.append([n, threshold, xaxis_type,
                                           xaxis_labeling])
        return parameters

    @pytest.mark.skipif("sys.platform == 'darwin'")
    @pytest.mark.parametrize(("n", "threshold", "xaxis_type", "xaxis_labeling"),
                             _generate_parameters())
    @pytest.mark.mpl_image_compare(
        baseline_dir=baseline_dir, tolerance=default_tol)
    def test_plot_explained_variance_ratio(self, n, threshold, xaxis_type,
                                           xaxis_labeling):
        ax = self.s.plot_explained_variance_ratio(n, threshold=threshold,
                                                  xaxis_type=xaxis_type,
                                                  xaxis_labeling=xaxis_labeling)
        return ax.get_figure()
