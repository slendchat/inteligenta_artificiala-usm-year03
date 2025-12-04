import unittest

from planner import heuristics, search, state


class PlannerTests(unittest.TestCase):
    def test_forward_finds_goal(self) -> None:
        result = search.forward_search(heuristics.zero)
        self.assertTrue(result.found)
        self.assertTrue(result.path[-1].is_goal())

    def test_backward_hits_start(self) -> None:
        start = state.initial_state()
        result = search.backward_search(heuristics.start_distance)
        self.assertTrue(result.found)
        self.assertEqual(result.path[0], start)


if __name__ == "__main__":
    unittest.main()
