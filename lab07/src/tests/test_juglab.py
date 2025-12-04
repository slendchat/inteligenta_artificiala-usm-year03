import unittest

from juglab import analysis, heuristics, search, state


class JugLabTests(unittest.TestCase):
    def test_successor_generation(self) -> None:
        start = state.INITIAL_STATE
        moves = state.successors(start)
        actions = {tr.action for tr in moves}
        self.assertEqual(len(moves), 2)
        self.assertIn("Fill 4L jug", actions)
        self.assertIn("Fill 3L jug", actions)

    def test_bfs_finds_goal(self) -> None:
        result = search.breadth_first_search(goals=list(state.goal_states()))
        self.assertTrue(result.found)
        self.assertEqual(result.path[-1].big, state.GOAL_VOLUME)
        self.assertEqual(result.cost, 6)

    def test_heuristic_is_admissible(self) -> None:
        report = analysis.evaluate_heuristic(heuristics.difference_to_target)
        self.assertTrue(report["admissible"])
        self.assertTrue(report["consistent"])


if __name__ == "__main__":
    unittest.main()
