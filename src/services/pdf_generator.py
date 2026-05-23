"""
Генератор PDF для коммерческих предложений.
Использует WeasyPrint для конвертации HTML -> PDF.
"""
import os
from pathlib import Path

from weasyprint import HTML


class PDFGenerator:
    """Генерирует PDF-файл из HTML-контента коммерческого предложения"""

    def generate_pdf(
        self, proposal_id: int, content_html: str, output_dir: str
    ) -> str:
        """
        Конвертирует HTML в PDF и сохраняет файл.

        :param proposal_id: ID предложения (используется в имени файла)
        :param content_html: HTML-строка для конвертации
        :param output_dir: Директория для сохранения PDF
        :return: Путь к сохранённому PDF-файлу
        """
        # Создаём директорию если она не существует
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        file_name = f"proposal_{proposal_id}.pdf"
        file_path = os.path.join(output_dir, file_name)

        HTML(string=content_html).write_pdf(file_path)

        return file_path
