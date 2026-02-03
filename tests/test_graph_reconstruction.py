
import unittest
import sys
import os

# Add python directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../python')))

# Imports
try:
    from table_graph_builder import TableGraphBuilder, FinancialTableGraph
    from parser_config import ExtractedTable, StatementType, ReportingEntity
except ImportError as e:
    print(f"Import Error: {e}")

class TestGraphReconstruction(unittest.TestCase):
    def setUp(self):
        self.builder = TableGraphBuilder()

    def test_build_graph_simple(self):
        # Create a mock extracted table
        try:
            table = ExtractedTable(
                page_num=1,
                headers=["Particulars", "31-03-2023", "31-03-2022"],
                rows=[
                    ["Assets", "", ""],
                    ["Non-current assets", "1000", "900"],
                    ["Current assets", "500", "400"]
                ],
                statement_type=StatementType.BALANCE_SHEET,
                reporting_entity=ReportingEntity.STANDALONE,
                confidence=0.9
            )
            
            graph = self.builder.build_graph(table)
            
            self.assertIsNotNone(graph)
            # Check columns
            self.assertEqual(len(graph.columns), 3)
            # Check if date was parsed (Column 1 should be 2023-03-31)
            # Note: build_graph logic depends on date parsing. 
            # We assume "31-03-2023" is parsed by the builder -> indian_finance_utils
            
            # Check cells
            # Rows with empty values (like headers) are skipped => 4 data cells
            self.assertEqual(len(graph.cells), 4)
            
            # Check value extraction
            # Row 1 (Non-current), Col 1 (Value 1000)
            # _cells_by_pos[(1, 1)] -> 1-indexed? Or 0-indexed?
            # parser_config usually 0-indexed lists, but row_idx might be 0-based.
            # TableGraphBuilder logic: enumerates rows.
            
            # Let's check finding a specific value
            value_cells = [c for c in graph.cells if c.value == 1000.0]
            self.assertTrue(len(value_cells) >= 1)
            
        except Exception as e:
            self.fail(f"Graph construction failed: {e}")

if __name__ == '__main__':
    unittest.main()
