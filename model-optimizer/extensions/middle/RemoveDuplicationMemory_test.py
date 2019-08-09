"""
 Copyright (c) 2019 Intel Corporation

 Licensed under the Apache License, Version 2.0 (the "License");
 you may not use this file except in compliance with the License.
 You may obtain a copy of the License at

      http://www.apache.org/licenses/LICENSE-2.0

 Unless required by applicable law or agreed to in writing, software
 distributed under the License is distributed on an "AS IS" BASIS,
 WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 See the License for the specific language governing permissions and
 limitations under the License.
"""
import unittest

from extensions.middle.RemoveDuplicationMemory import RemoveMemoryDuplicationPattern
from mo.utils.unittest.graph import build_graph, compare_graphs


class RemoveMemoryDuplicationPatternTests(unittest.TestCase):

    def test_remove_duplication(self):
        graph = build_graph({'in_node': {'kind': 'data', 'shape': [1, 13]},
                             'splice_1': {'kind': 'op', 'op': 'Splice', 'context': range(-5, 6)},
                             'splice_data_1': {'kind': 'data', 'shape': [1, 143]},
                             'placeholder_1': {'kind': 'op', 'op': None},
                             'splice_2': {'kind': 'op', 'op': 'Splice', 'context': range(-1, 2)},
                             'splice_data_2': {'kind': 'data', 'shape': [1, 39]},
                             'placeholder_2': {'kind': 'op', 'op': None},
                             },
                            [('in_node', 'splice_1'), ('splice_1', 'splice_data_1'), ('splice_data_1', 'placeholder_1'),
                             ('in_node', 'splice_2'), ('splice_2', 'splice_data_2'), ('splice_data_2', 'placeholder_2'),
                             ],
                            nodes_with_edges_only=True)
        RemoveMemoryDuplicationPattern().find_and_replace_pattern(graph)
        ref_graph = build_graph({'in_node': {'kind': 'data', 'shape': [1, 13]},
                                 'splice_1': {'kind': 'op', 'op': 'Splice', 'context': range(-5, 6)},
                                 'splice_data_1': {'kind': 'data', 'shape': [1, 143]},
                                 'placeholder_1': {'kind': 'op'},
                                 'crop_2': {'kind': 'op', 'op': 'Crop', 'offset': 52, 'dim': 39, 'axis': -1},
                                 'splice_data_2': {'kind': 'data', 'shape': [1, 39]},
                                 'placeholder_2': {'kind': 'op'},
                                 },
                                [
                                    ('in_node', 'splice_1'), ('splice_1', 'splice_data_1'),
                                    ('splice_data_1', 'placeholder_1'),
                                    ('splice_data_1', 'crop_2'), ('crop_2', 'splice_data_2'),
                                    ('splice_data_2', 'placeholder_2'),
                                ],
                                nodes_with_edges_only=True
                                )

        (flag, resp) = compare_graphs(graph, ref_graph, 'placeholder_2')
        self.assertTrue(flag, resp)

    def test_remove_duplication_with_crops(self):
        graph = build_graph({'in_node': {'kind': 'data', 'shape': [1, 13]},
                             'splice_1': {'kind': 'op', 'op': 'Splice', 'context': range(-5, 6)},
                             'splice_data_1': {'kind': 'data', 'shape': [1, 143]},
                             'crop_1': {'kind': 'op', 'op': 'Crop', 'offset': 13, 'dim': 13, 'axis': -1},
                             'splice_2': {'kind': 'op', 'op': 'Splice', 'context': range(-1, 2)},
                             'splice_data_2': {'kind': 'data', 'shape': [1, 39]},
                             'crop_2': {'kind': 'op', 'op': 'Crop', 'offset': 13, 'dim': 13, 'axis': -1},
                             },
                            [('in_node', 'splice_1'), ('splice_1', 'splice_data_1'), ('splice_data_1', 'crop_1'),
                             ('in_node', 'splice_2'), ('splice_2', 'splice_data_2'), ('splice_data_2', 'crop_2'),
                             ],
                            nodes_with_edges_only=True)
        RemoveMemoryDuplicationPattern().find_and_replace_pattern(graph)
        ref_graph = build_graph({'in_node': {'kind': 'data', 'shape': [1, 13]},
                                 'splice_1': {'kind': 'op', 'op': 'Splice', 'context': range(-5, 6)},
                                 'splice_data_1': {'kind': 'data', 'shape': [1, 143]},
                                 'crop_1': {'kind': 'op', 'op': 'Crop', 'offset': 13, 'dim': 13},
                                 'crop_2': {'kind': 'op', 'op': 'Crop', 'offset': 65, 'dim': 13, 'axis': -1},
                                 },
                                [
                                    ('in_node', 'splice_1'), ('splice_1', 'splice_data_1'),
                                    ('splice_data_1', 'crop_1'),
                                    ('splice_data_1', 'crop_2'),
                                ],
                                nodes_with_edges_only=True
                                )

        (flag, resp) = compare_graphs(graph, ref_graph, 'crop_2')
        self.assertTrue(flag, resp)