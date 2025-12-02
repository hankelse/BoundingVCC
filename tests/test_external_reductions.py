import unittest
from unittest.mock import patch, MagicMock

import os
import tempfile

from src.structures.graph import Graph
from src.solvers.tools.reductions import apply_reductions_external
from src.solvers.tools.reductions import remove_masked_nodes


class TestApplyReductionsExternal(unittest.TestCase):

    # ----------------------------------------------------------------------
    # Utility graph builders
    # ----------------------------------------------------------------------

    def make_triangle(self):
        """3-clique: nodes {0,1,2}"""
        return Graph(edge_list=[(0,1), (1,2), (0,2)], name="tri")

    def make_path4(self):
        """Path graph of length 3: 0-1-2-3"""
        return Graph(edge_list=[(0,1), (1,2), (2,3)], name="path4")

    # ----------------------------------------------------------------------
    # Tests
    # ----------------------------------------------------------------------

    @patch("src.solvers.tools.reductions.reduvcc_reductions")
    @patch("src.solvers.tools.reductions.read_clique_cover")
    def test_empty_graph(self, mock_read_cover, mock_reduvcc):
        g = Graph(edge_list=[])

        removed_nodes, cliques = apply_reductions_external(g)

        self.assertEqual(removed_nodes, [])
        self.assertEqual(cliques, [])
        mock_reduvcc.assert_not_called()
        mock_read_cover.assert_not_called()

    @patch("src.solvers.tools.reductions.reduvcc_reductions")
    @patch("src.solvers.tools.reductions.read_clique_cover")
    def test_external_failure(self, mock_read_cover, mock_reduvcc):
        g = self.make_triangle()

        mock_reduvcc.return_value = {
            "returncode": 1,
            "stderr": "Some failure message",
            "summary": None,
            "reduced_graph_nodes": None,
            "removed_cliques": 0
        }

        removed_nodes, cliques = apply_reductions_external(g)

        self.assertIsNone(removed_nodes)
        self.assertIsNone(cliques)
        mock_read_cover.assert_not_called()

    @patch("src.solvers.tools.reductions.reduvcc_reductions")
    @patch("src.solvers.tools.reductions.read_clique_cover")
    def test_no_reductions(self, mock_read_cover, mock_reduvcc):
        g = self.make_triangle()

        mock_reduvcc.return_value = {
            "returncode": 0,
            "summary": {"vertices": 3},
            "reduced_graph_nodes": 3,
            "removed_cliques": 0
        }
        mock_read_cover.return_value = []

        removed_nodes, cliques = apply_reductions_external(g)

        self.assertEqual(removed_nodes, [False, False, False])
        self.assertEqual(cliques, [])

    @patch("src.solvers.tools.reductions.reduvcc_reductions")
    @patch("src.solvers.tools.reductions.read_clique_cover")
    def test_partial_reduction(self, mock_read_cover, mock_reduvcc):
        g = self.make_path4()  # 4 nodes

        mock_reduvcc.return_value = {
            "returncode": 0,
            "summary": {"vertices": 4},
            "reduced_graph_nodes": 2,
            "removed_cliques": 1
        }
        mock_read_cover.return_value = [["dummy_clique"]]

        removed_nodes, cliques = apply_reductions_external(g)

        # Expect 2 nodes removed, approximated as first two nodes
        self.assertEqual(removed_nodes.count(True), 2)
        self.assertEqual(removed_nodes.count(False), 2)

        # And cliques returned
        self.assertEqual(len(cliques), 1)

    @patch("src.solvers.tools.reductions.reduvcc_reductions")
    @patch("src.solvers.tools.reductions.read_clique_cover")
    def test_full_reduction(self, mock_read_cover, mock_reduvcc):
        g = self.make_path4()

        mock_reduvcc.return_value = {
            "returncode": 0,
            "summary": {"vertices": 4},
            "reduced_graph_nodes": 0,
            "removed_cliques": 2
        }
        mock_read_cover.return_value = [["c1"], ["c2"]]

        removed_nodes, cliques = apply_reductions_external(g)

        self.assertEqual(removed_nodes, [True, True, True, True])
        self.assertEqual(len(cliques), 2)

    # ----------------------------------------------------------------------
    # Tests involving remove_masked_nodes
    # ----------------------------------------------------------------------

    @patch("src.solvers.tools.reductions.reduvcc_reductions")
    @patch("src.solvers.tools.reductions.read_clique_cover")
    def test_reduce_then_remove_masked_nodes_valid_graph(self, mock_read_cover, mock_reduvcc):
        """
        Ensures that remove_masked_nodes produces a graph whose edges & nodes
        are a valid induced subgraph of the original graph.
        """
        g = self.make_path4()  # 0-1-2-3

        mock_reduvcc.return_value = {
            "returncode": 0,
            "summary": {"vertices": 4},
            "reduced_graph_nodes": 3,   # Remove 1 node
            "removed_cliques": 0
        }
        mock_read_cover.return_value = []

        removed_nodes, cliques = apply_reductions_external(g)
        reduced = remove_masked_nodes(g, removed_nodes)

        # The reduced graph should have 3 nodes
        self.assertEqual(reduced.number_of_nodes(), 3)

        # All edges in reduced must exist in original
        for (u, v) in reduced.edges():
            self.assertTrue(g.has_edge(g.remapped_label(u), g.remapped_label(v)) or
                            g.has_edge(g.remapped_label(v), g.remapped_label(u)))

    # ----------------------------------------------------------------------
    # I/O and behavior tests
    # ----------------------------------------------------------------------

    @patch("src.solvers.tools.reductions.reduvcc_reductions")
    @patch("src.solvers.tools.reductions.read_clique_cover")
    def test_graph_write_called(self, mock_read_cover, mock_reduvcc):
        g = self.make_triangle()

        with patch.object(g, "write", wraps=g.write) as mock_write:

            mock_reduvcc.return_value = {
                "returncode": 0,
                "summary": {"vertices": 3},
                "reduced_graph_nodes": 3,
                "removed_cliques": 0
            }
            mock_read_cover.return_value = []

            apply_reductions_external(g)

            mock_write.assert_called_once()

    # ----------------------------------------------------------------------
    # Edge cases using summary=None
    # ----------------------------------------------------------------------

    @patch("src.solvers.tools.reductions.reduvcc_reductions")
    @patch("src.solvers.tools.reductions.read_clique_cover")
    def test_summary_none(self, mock_read_cover, mock_reduvcc):
        g = self.make_triangle()

        mock_reduvcc.return_value = {
            "returncode": 0,
            "summary": None,
            "reduced_graph_nodes": 1,
            "removed_cliques": 0
        }
        mock_read_cover.return_value = []

        removed_nodes, cliques = apply_reductions_external(g)

        # n_original should fallback to graph.number_of_nodes()
        self.assertEqual(removed_nodes.count(True), 2)
        self.assertEqual(removed_nodes.count(False), 1)


if __name__ == "__main__":
    unittest.main()
