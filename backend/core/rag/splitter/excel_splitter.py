import pandas as pd
from langchain_core.documents import Document as LangChainDocument
from core.rag.splitter.structured_file import TextSplitter
from config.config_info import settings
from config.splitter_model import SplitterModel
from typing import List

class ExcelSplitter(TextSplitter):
    def __init__(self, file_path: str, splitter_args=None, splitter_model: SplitterModel = settings.SPPLITTER_MODEL, *args, **kwargs):
        super().__init__(splitter_args=splitter_args, SPPLITTER_MODEL=splitter_model, *args, **kwargs)
        self.file_path = file_path
        self.splitter_model = splitter_model

    def load(self):
        # Read all sheets from the Excel file
        excel_data = pd.read_excel(self.file_path, sheet_name=None)
        full_text = ""

        for sheet_name, sheet_data in excel_data.items():
            full_text += f"Sheet: {sheet_name}\n"
            full_text += "|" + " | ".join(sheet_data.columns) + "|\n"  # Add column headers
            full_text += "|" + " | ".join(["---"] * len(sheet_data.columns)) + "|\n"  # Add separator line

            for _, row in sheet_data.iterrows():
                row_text = "| " + " | ".join(str(cell) if pd.notna(cell) else "" for cell in row) + " |\n"
                full_text += row_text

            full_text += "\n\n"  # Separate sheets

        print(full_text)
        return full_text

    def split(self) -> List[LangChainDocument]:
        full_text = self.load()
        return super().split(full_text)

if __name__ == "__main__":
    excel_splitter = ExcelSplitter("/Users/markyangkp/Downloads/test.xls")
    excel_splitter.load()